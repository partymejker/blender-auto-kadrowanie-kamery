bl_info = {
    "name": "Auto kadrowanie kamery",
    "author": "partymejkerr",
    "version": (1, 0, 0),
    "blender": (4, 4, 0),
    "location": "Widok 3D > panel boczny (N) > zakładka Kadrowanie",
    "description": "Utrzymuje wybrane obiekty na środku kadru i w ramie: animuje cel kamery "
                   "i (opcjonalnie) ogniskową. Położenie i obrót kamery zostają bez zmian.",
    "category": "Camera",
}

import bpy
import numpy as np
from mathutils import Vector
from bpy.props import (BoolProperty, EnumProperty, FloatProperty, IntProperty,
                       PointerProperty, StringProperty)

try:
    from bpy_extras import anim_utils
except ImportError:  # starsze wersje Blendera
    anim_utils = None

TRACK_TYPES = {'DAMPED_TRACK', 'TRACK_TO', 'LOCKED_TRACK'}
GEOMETRY_TYPES = {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'CURVES',
                  'POINTCLOUD', 'VOLUME', 'GREASEPENCIL', 'GPENCIL'}
TARGET_PREFIX = "AF_Cel_"
MAX_VERTS = 5000      # większe siatki liczone po bounding boxie (szybciej, z zapasem)
MAX_KEYS = 60
CAM_KEYS = ("af_constraint", "af_added", "af_orig_target", "af_orig_subtarget", "af_objects")
ZOOM_KEYS = ("af_zoom_param", "af_zoom_value", "af_zoom_keys")


# ---------------------------------------------------------------- animacja

def _fcurve_collection(id_data):
    ad = id_data.animation_data
    if ad is None or ad.action is None:
        return None
    act = ad.action
    if hasattr(act, "fcurves"):
        return act.fcurves
    if anim_utils is None:
        return None
    cb = anim_utils.action_get_channelbag_for_slot(act, ad.action_slot)
    return cb.fcurves if cb else None


def _fcurves(id_data, data_path):
    coll = _fcurve_collection(id_data)
    if coll is None:
        return {}
    return {fc.array_index: fc for fc in coll if fc.data_path == data_path}


def _remove_fcurves(id_data, data_path):
    coll = _fcurve_collection(id_data)
    if coll is None:
        return
    for fc in [fc for fc in coll if fc.data_path == data_path]:
        coll.remove(fc)


def _write_keys(fcs, keys):
    frames = sorted(keys)
    for ch, fc in enumerate(fcs):
        kps = fc.keyframe_points
        try:
            kps.clear()
        except AttributeError:
            while len(kps):
                kps.remove(kps[0], fast=True)
        kps.add(len(frames))
        for kp, f in zip(kps, frames):
            kp.co = (f, keys[f][ch])
            kp.interpolation = 'BEZIER'
            kp.handle_left_type = 'AUTO_CLAMPED'
            kp.handle_right_type = 'AUTO_CLAMPED'
        fc.update()


def _fit_keys(fcs, frames, values, err_fn, tol):
    """Dokłada klucze tylko tam, gdzie krzywa najbardziej odbiega od ideału."""
    keys = {frames[0]: values[0], frames[-1]: values[-1]}
    while True:
        _write_keys(fcs, keys)
        worst, wi = 0.0, None
        for i, f in enumerate(frames):
            e = err_fn(i, [fc.evaluate(f) for fc in fcs])
            if e > worst:
                worst, wi = e, i
        if worst <= tol or wi is None or frames[wi] in keys or len(keys) >= MAX_KEYS:
            return len(keys)
        keys[frames[wi]] = values[wi]


# ---------------------------------------------------------------- ogniskowa: kopia / przywracanie

def _backup_zoom(cd, param):
    if "af_zoom_param" in cd:
        return
    cd["af_zoom_param"] = param
    cd["af_zoom_value"] = getattr(cd, param)
    fc = _fcurves(cd, param).get(0)
    if fc and len(fc.keyframe_points):
        cd["af_zoom_keys"] = [c for kp in fc.keyframe_points for c in (kp.co[0], kp.co[1])]


def _restore_zoom(cd):
    if "af_zoom_param" not in cd:
        return
    param = cd["af_zoom_param"]
    value = cd["af_zoom_value"]
    _remove_fcurves(cd, param)
    keys = list(cd.get("af_zoom_keys", []))
    for i in range(0, len(keys), 2):
        setattr(cd, param, keys[i + 1])
        cd.keyframe_insert(param, frame=keys[i])
    setattr(cd, param, value)
    for k in ZOOM_KEYS:
        if k in cd:
            del cd[k]


# ---------------------------------------------------------------- cel kamery

def _setup_target(context, cam):
    name = TARGET_PREFIX + cam.name
    emp = bpy.data.objects.get(name)
    if emp is None:
        emp = bpy.data.objects.new(name, None)
        emp.empty_display_type = 'SPHERE'
        emp.empty_display_size = 0.25
        context.scene.collection.objects.link(emp)
    emp.hide_render = True
    emp.parent = None
    emp.animation_data_clear()

    con = cam.constraints.get(cam.get("af_constraint", ""))
    if con is None:
        con = next((c for c in cam.constraints if c.type in TRACK_TYPES and not c.mute), None)
        if con is None:
            con = cam.constraints.new('DAMPED_TRACK')
            con.name = "AF Damped Track"
            con.track_axis = 'TRACK_NEGATIVE_Z'
            cam["af_added"] = 1
        else:
            cam["af_added"] = 0
        cam["af_constraint"] = con.name
        cam["af_orig_target"] = con.target.name if con.target and con.target != emp else ""
        cam["af_orig_subtarget"] = getattr(con, "subtarget", "")
    con.target = emp
    if hasattr(con, "subtarget"):
        con.subtarget = ""
    return emp


def _restore_all(cam):
    con = cam.constraints.get(cam.get("af_constraint", ""))
    if con is not None:
        if cam.get("af_added"):
            cam.constraints.remove(con)
        else:
            con.target = bpy.data.objects.get(cam.get("af_orig_target", ""))
            if hasattr(con, "subtarget"):
                con.subtarget = cam.get("af_orig_subtarget", "")
    _restore_zoom(cam.data)
    emp = bpy.data.objects.get(TARGET_PREFIX + cam.name)
    if emp is not None:
        bpy.data.objects.remove(emp, do_unlink=True)
    for k in CAM_KEYS:
        if k in cam:
            del cam[k]


# ---------------------------------------------------------------- geometria i rzutowanie

def _collect_objects(context, cam, include_children):
    base = [o for o in context.selected_objects
            if o != cam and not o.name.startswith(TARGET_PREFIX)]
    if not base and cam.get("af_objects"):
        base = [bpy.data.objects[n] for n in cam["af_objects"].split("\n") if n in bpy.data.objects]
    res, seen = [], set()
    for o in base:
        for x in [o] + (list(o.children_recursive) if include_children else []):
            if x.name in seen or x == cam or x.type not in GEOMETRY_TYPES:
                continue
            seen.add(x.name)
            res.append(x)
    return res


def _gather_points(depsgraph, objs):
    chunks = []
    for o in objs:
        oe = o.evaluated_get(depsgraph)
        mw = np.array(oe.matrix_world)
        co = None
        if oe.type == 'MESH':
            n = len(oe.data.vertices)
            if 0 < n <= MAX_VERTS:
                buf = np.empty(n * 3, dtype=np.float32)
                oe.data.vertices.foreach_get("co", buf)
                co = buf.reshape(-1, 3).astype(np.float64)
        if co is None:
            co = np.array([tuple(c) for c in oe.bound_box], dtype=np.float64)
        chunks.append(co @ mw[:3, :3].T + mw[:3, 3])
    return np.concatenate(chunks) if chunks else np.zeros((0, 3))


def _cam_frame(cam_eval, scene):
    vf = cam_eval.data.view_frame(scene=scene)
    return vf[2].x, vf[1].x, vf[1].y, vf[0].y, -vf[0].z


def _project(cam_eval, scene, P):
    """Pozycje punktów w kadrze (0..1), jak world_to_camera_view, ale wektorowo."""
    minx, maxx, miny, maxy, fz = _cam_frame(cam_eval, scene)
    M = np.array(cam_eval.matrix_world.normalized().inverted())
    L = P @ M[:3, :3].T + M[:3, 3]
    if cam_eval.data.type == 'ORTHO':
        ok = np.ones(len(P), dtype=bool)
        X, Y = L[:, 0], L[:, 1]
    else:
        z = -L[:, 2]
        ok = z > 1e-6
        zz = np.where(ok, z, 1.0)
        X, Y = L[:, 0] * fz / zz, L[:, 1] * fz / zz
    u = (X - minx) / (maxx - minx)
    v = (Y - miny) / (maxy - miny)
    return u[ok], v[ok], bool((~ok).any())


def _frame_size_at(cam_eval, scene, point):
    minx, maxx, miny, maxy, fz = _cam_frame(cam_eval, scene)
    w, h = maxx - minx, maxy - miny
    if cam_eval.data.type != 'ORTHO':
        d = -(cam_eval.matrix_world.normalized().inverted() @ point).z
        if d <= 1e-6:
            return None
        w, h = w * d / fz, h * d / fz
    return w, h


# ---------------------------------------------------------------- ustawienia

class AF_Settings(bpy.types.PropertyGroup):
    margin: FloatProperty(
        name="Margines", default=10.0, min=0.0, max=45.0, subtype='PERCENTAGE',
        description="Minimalny odstęp obiektów od krawędzi kadru")
    zoom_mode: EnumProperty(
        name="Ogniskowa", default='ANIM',
        items=[('ANIM', "Animowana", "Zmienia ogniskową tylko tam, gdzie obiekt by się nie zmieścił"),
               ('CONST', "Stała", "Jedna ogniskowa na całą animację, dobrana do najtrudniejszej klatki"),
               ('NONE', "Bez zmian", "Tylko centrowanie, ogniskowa zostaje")])
    allow_zoom_in: BoolProperty(
        name="Pozwól przybliżać", default=False,
        description="Pozwala zwiększać ogniskową ponad oryginalną, żeby obiekt wypełniał kadr")
    include_children: BoolProperty(
        name="Uwzględnij dzieci", default=True,
        description="Do kadrowania wchodzą też obiekty podpięte (parent) pod zaznaczone")
    use_scene_range: BoolProperty(name="Zakres klatek sceny", default=True)
    frame_start: IntProperty(name="Od", default=1)
    frame_end: IntProperty(name="Do", default=250)
    tolerance: FloatProperty(
        name="Dokładność", default=2.0, min=0.1, max=10.0, subtype='PERCENTAGE',
        description="Dopuszczalne odchylenie od ideału. Mniej = dokładniej, ale więcej kluczy")
    last_report: StringProperty()


# ---------------------------------------------------------------- operatory

class AF_OT_auto_frame(bpy.types.Operator):
    bl_idname = "camera.af_auto_frame"
    bl_label = "Wycentruj w kamerze"
    bl_description = ("Animuje cel kamery (i ogniskową), żeby zaznaczone obiekty były na środku "
                      "kadru i nie wychodziły poza ramę")
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        cam = context.scene.camera
        return cam is not None and cam.type == 'CAMERA'

    def execute(self, context):
        scene = context.scene
        s = scene.af_settings
        cam = scene.camera
        cd = cam.data
        if cd.type == 'PANO':
            self.report({'ERROR'}, "Kamery panoramiczne nie są obsługiwane.")
            return {'CANCELLED'}
        objs = _collect_objects(context, cam, s.include_children)
        if not objs:
            self.report({'ERROR'}, "Zaznacz obiekty, które mają być w kadrze.")
            return {'CANCELLED'}
        f0, f1 = ((scene.frame_start, scene.frame_end) if s.use_scene_range
                  else (s.frame_start, s.frame_end))
        if f1 <= f0:
            self.report({'ERROR'}, "Nieprawidłowy zakres klatek.")
            return {'CANCELLED'}

        param = "ortho_scale" if cd.type == 'ORTHO' else "lens"
        persp = param == "lens"
        margin = s.margin / 100.0
        tol = s.tolerance / 100.0
        frames = list(range(f0, f1 + 1))
        orig_frame = scene.frame_current
        cam["af_objects"] = "\n".join(o.name for o in objs)

        _restore_zoom(cd)          # cofnij ogniskową z poprzedniego uruchomienia
        _backup_zoom(cd, param)    # zapamiętaj oryginał
        emp = _setup_target(context, cam)

        wm = context.window_manager
        wm.progress_begin(0, 2 * len(frames))
        targets, sizes, zoom_req, behind = [], [], [], False
        try:
            # 1) idealny cel i potrzebna ogniskowa w każdej klatce
            for i, f in enumerate(frames):
                scene.frame_set(f)
                dg = context.evaluated_depsgraph_get()
                P = _gather_points(dg, objs)
                T = Vector(((P.min(0) + P.max(0)) / 2).tolist())
                size, u = None, np.zeros(0)
                for _ in range(12):
                    emp.location = T
                    dg.update()
                    ce = cam.evaluated_get(dg)
                    u, v, b = _project(ce, scene, P)
                    behind |= b
                    if not len(u):
                        break
                    cu = (u.min() + u.max()) / 2 - 0.5
                    cv = (v.min() + v.max()) / 2 - 0.5
                    size = _frame_size_at(ce, scene, T)
                    if size is None or (abs(cu) < 1e-4 and abs(cv) < 1e-4):
                        break
                    R = ce.matrix_world.to_3x3().normalized()
                    T = T + R.col[0] * (cu * size[0]) + R.col[1] * (cv * size[1])
                z0 = getattr(ce.data, param)
                h = (max(abs(u.min() - .5), abs(u.max() - .5), abs(v.min() - .5), abs(v.max() - .5))
                     if len(u) else 0.5)
                k = (0.5 - margin) / h if h > 1e-9 else 1.0
                if not s.allow_zoom_in:
                    k = min(k, 1.0)
                targets.append(T.copy())
                sizes.append(min(size) if size else 1.0)
                zoom_req.append(z0 * k if persp else z0 / k)
                wm.progress_update(i)

            # 2) klucze celu kamery (tylko tyle, ile trzeba)
            emp.location = targets[0]
            emp.keyframe_insert("location", frame=f0)
            fcs = _fcurves(emp, "location")
            fcs = [fcs[0], fcs[1], fcs[2]]
            n_t = _fit_keys(fcs, frames, [tuple(t) for t in targets],
                            lambda i, c: (Vector(c) - targets[i]).length / sizes[i], tol)

            # 3) ogniskowa
            n_z = 0
            if s.zoom_mode == 'ANIM':
                fc_orig = _fcurves(cd, param).get(0)
                orig = [fc_orig.evaluate(f) if fc_orig else getattr(cd, param) for f in frames]
                if any(abs(a - b) > 1e-4 * b for a, b in zip(zoom_req, orig)):
                    _remove_fcurves(cd, param)
                    setattr(cd, param, zoom_req[0])
                    cd.keyframe_insert(param, frame=f0)
                    fc = _fcurves(cd, param)[0]

                    def err_zoom(i, c):
                        rel = (c[0] - zoom_req[i]) / zoom_req[i]
                        clip = rel > 0 if persp else rel < 0
                        return abs(rel) * (3.0 if clip else 1.0)
                    n_z = _fit_keys([fc], frames, [(z,) for z in zoom_req], err_zoom, tol)
            elif s.zoom_mode == 'CONST':
                _remove_fcurves(cd, param)
                setattr(cd, param, min(zoom_req) if persp else max(zoom_req))

            # 4) sprawdzenie wyniku
            worst_m, worst_mf, worst_off, worst_of = 1.0, f0, 0.0, f0
            for i, f in enumerate(frames):
                scene.frame_set(f)
                dg = context.evaluated_depsgraph_get()
                u, v, _ = _project(cam.evaluated_get(dg), scene, _gather_points(dg, objs))
                wm.progress_update(len(frames) + i)
                if not len(u):
                    continue
                m = min(u.min(), 1 - u.max(), v.min(), 1 - v.max())
                off = max(abs((u.min() + u.max()) / 2 - .5), abs((v.min() + v.max()) / 2 - .5))
                if m < worst_m:
                    worst_m, worst_mf = m, f
                if off > worst_off:
                    worst_off, worst_of = off, f
        finally:
            wm.progress_end()
            scene.frame_set(orig_frame)

        zoom_txt = {'ANIM': f"{n_z} kluczy" if n_z else "bez zmian (mieści się)",
                    'CONST': f"stała {getattr(cd, param):.1f}" + (" mm" if persp else ""),
                    'NONE': "bez zmian"}[s.zoom_mode]
        lines = [f"Cel kamery: {n_t} kluczy, ogniskowa: {zoom_txt}",
                 f"Najmniejszy margines: {worst_m * 100:.1f}% (klatka {worst_mf})",
                 f"Maks. odchylenie od środka: {worst_off * 100:.1f}% (klatka {worst_of})"]
        if worst_m < 0:
            lines.append("Uwaga: obiekt wychodzi poza kadr - wybierz ogniskową Animowaną/Stałą")
        if behind:
            lines.append("Uwaga: część obiektów była za kamerą w niektórych klatkach")
        s.last_report = "\n".join(lines)
        self.report({'WARNING' if worst_m < 0 or behind else 'INFO'}, " | ".join(lines))
        return {'FINISHED'}


class AF_OT_reset(bpy.types.Operator):
    bl_idname = "camera.af_reset"
    bl_label = "Przywróć oryginał"
    bl_description = "Usuwa automatyczne kadrowanie i przywraca poprzedni cel kamery oraz ogniskową"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        cam = context.scene.camera
        return cam is not None and "af_constraint" in cam

    def execute(self, context):
        _restore_all(context.scene.camera)
        context.scene.af_settings.last_report = ""
        return {'FINISHED'}


class AF_PT_panel(bpy.types.Panel):
    bl_label = "Auto kadrowanie kamery"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Kadrowanie"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        s = scene.af_settings
        cam = scene.camera
        if cam is None:
            layout.label(text="Scena nie ma aktywnej kamery", icon='ERROR')
            return
        layout.label(text=f"Kamera: {cam.name}", icon='CAMERA_DATA')
        n = len([o for o in context.selected_objects if o != cam])
        if n:
            layout.label(text=f"Zaznaczone obiekty: {n}", icon='RESTRICT_SELECT_OFF')
        elif cam.get("af_objects"):
            layout.label(text="Użyję obiektów z ostatniego razu", icon='INFO')
        else:
            layout.label(text="Zaznacz obiekty do kadrowania", icon='INFO')

        col = layout.column(align=True)
        col.prop(s, "margin")
        col.prop(s, "tolerance")
        layout.prop(s, "zoom_mode")
        layout.prop(s, "allow_zoom_in")
        layout.prop(s, "include_children")
        layout.prop(s, "use_scene_range")
        if not s.use_scene_range:
            row = layout.row(align=True)
            row.prop(s, "frame_start")
            row.prop(s, "frame_end")

        layout.operator(AF_OT_auto_frame.bl_idname, icon='VIEW_CAMERA')
        if "af_constraint" in cam:
            layout.operator(AF_OT_reset.bl_idname, icon='LOOP_BACK')
        if s.last_report:
            box = layout.box()
            for line in s.last_report.split("\n"):
                box.label(text=line)


classes = (AF_Settings, AF_OT_auto_frame, AF_OT_reset, AF_PT_panel)


def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.Scene.af_settings = PointerProperty(type=AF_Settings)


def unregister():
    del bpy.types.Scene.af_settings
    for c in reversed(classes):
        bpy.utils.unregister_class(c)


if __name__ == "__main__":
    register()
