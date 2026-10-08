"""Testy dodatku „Auto kadrowanie kamery” uruchamiane w Blenderze w tle.

Uruchomienie (z katalogu głównego repozytorium):

    blender -b --factory-startup --python tests/test_dodatek.py

Skrypt sam buduje scenę testową i importuje dodatek prosto z repozytorium,
bez instalowania go w Blenderze. Kończy się kodem wyjścia 1, jeśli któryś test
nie przejdzie.
"""

import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tempfile
import traceback

sys.dont_write_bytecode = True      # nie zapisuj __pycache__ w repozytorium

import bpy

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
import auto_kadrowanie_kamery as af  # noqa: E402

TMP = tempfile.mkdtemp(prefix="af_testy_")


# ---------------------------------------------------------------- scena testowa

def reset_scene():
    for coll in (bpy.data.objects, bpy.data.meshes, bpy.data.cameras, bpy.data.lights,
                 bpy.data.actions):
        for item in list(coll):
            coll.remove(item)
    sc = bpy.context.scene
    s = sc.af_settings
    for p in s.bl_rna.properties:
        if not p.is_readonly:
            s.property_unset(p.identifier)
    sc.frame_start, sc.frame_end = 1, 60
    sc.frame_set(1)
    return sc


def add_cube(name="Cube", size=1.0, keys=((1, (0, 0, 0)), (60, (3, 0, 1)))):
    sc = bpy.context.scene
    bpy.ops.mesh.primitive_cube_add(size=size)
    cube = bpy.context.active_object
    cube.name = name
    for f, loc in keys:
        cube.location = loc
        cube.keyframe_insert("location", frame=f)
    return cube


def build(ortho=False, lens=50.0):
    """Animowany sześcian, kamera z animowanym położeniem i constraintem Damped Track."""
    sc = reset_scene()
    cube = add_cube()
    orig = bpy.data.objects.new("Cel_oryginalny", None)
    sc.collection.objects.link(orig)
    cd = bpy.data.cameras.new("Camera")
    cd.lens = lens
    if ortho:
        cd.type = 'ORTHO'
        cd.ortho_scale = 2.0
    cam = bpy.data.objects.new("Camera", cd)
    sc.collection.objects.link(cam)
    for f, loc in ((1, (0, -10, 2)), (60, (4, -9, 3))):
        cam.location = loc
        cam.keyframe_insert("location", frame=f)
    con = cam.constraints.new('DAMPED_TRACK')
    con.track_axis = 'TRACK_NEGATIVE_Z'
    con.target = orig
    sc.camera = cam
    select(cube)
    return sc, cam, cube, orig


def select(*objs):
    vl = bpy.context.view_layer
    for o in vl.objects:
        o.select_set(False)
    for o in objs:
        o.select_set(True)
    vl.objects.active = objs[0] if objs else None


def frame(**opts):
    s = bpy.context.scene.af_settings
    for k, v in opts.items():
        setattr(s, k, v)
    bpy.ops.camera.af_auto_frame()
    return s.last_report


def targets():
    return [o for o in bpy.data.objects if o.name.startswith(af.TARGET_PREFIX)]


def margin(report):
    m = re.search(r"Najmniejszy margines: (-?[\d.]+)%", report)
    assert m, f"brak linii marginesu w raporcie:\n{report}"
    return float(m.group(1))


def keys_of(id_data, path):
    fcs = af._fcurves(id_data, path)
    return {i: [tuple(kp.co) for kp in fc.keyframe_points] for i, fc in fcs.items()}


def check(cond, msg):
    if not cond:
        raise AssertionError(msg)


# ---------------------------------------------------------------- testy

def test_01_podstawowe():
    sc, cam, cube, orig = build()
    rep = frame()
    check(margin(rep) >= 0, f"margines ujemny:\n{rep}")
    check(bpy.data.objects.get("AF_Cel_Camera") is not None, "nie powstał cel AF_Cel_Camera")
    check(cam.constraints[0].target.name == "AF_Cel_Camera", "constraint nie wskazuje celu")


def test_02_zmiana_nazwy_kamery():
    sc, cam, cube, orig = build()
    frame()
    first = bpy.data.objects["AF_Cel_Camera"]
    ptr = first.as_pointer()
    cam.name = "KameraB"
    select()
    frame()
    t = targets()
    check(len(t) == 1, f"po zmianie nazwy kamery są {len(t)} cele: {[o.name for o in t]}")
    check(t[0].as_pointer() == ptr, "powstał nowy obiekt-cel zamiast użyć starego")
    check(t[0].name == "AF_Cel_KameraB", f"cel ma nazwę {t[0].name}, a nie AF_Cel_KameraB")
    bpy.ops.camera.af_reset()
    check(not targets(), "„Przywróć oryginał” nie usunął celu")
    check(cam.constraints[0].target == orig, "nie przywrócono poprzedniego celu constraintu")


def test_03_zmiana_nazwy_obiektu():
    sc, cam, cube, orig = build()
    frame()
    cube.name = "Szescian"
    select()
    rep = frame()
    names = [it.obj.name for it in cam.af_frame_objects if it.obj]
    check(names == ["Szescian"], f"lista obiektów po zmianie nazwy: {names}")
    check("Pominięto" not in rep, f"niepotrzebnie zgłoszono pominięte obiekty:\n{rep}")


def test_04_usuniety_obiekt():
    sc, cam, cube, orig = build()
    kula = add_cube("Kula", keys=((1, (1, 0, 0)),))
    trzeci = add_cube("Trzeci", keys=((1, (-1, 0, 0)),))
    select(cube, kula, trzeci)
    frame()
    bpy.data.objects.remove(kula)                  # usunięty z pliku
    for c in list(trzeci.users_collection):        # usunięty ze sceny (jak klawisz X)
        c.objects.unlink(trzeci)
    bpy.context.view_layer.update()
    select()
    rep = frame()
    check("Pominięto 2 obiekt(ów) z ostatniego razu, których nie ma już w pliku" in rep,
          f"brak linii o pominiętych obiektach:\n{rep}")


def test_05_migracja_200():
    sc, cam, cube, orig = build()
    frame()
    cam.af_frame_objects.clear()
    cam["af_objects"] = "Cube\nNieistniejacy"
    select()
    rep = frame()
    check("af_objects" not in cam, "stary klucz af_objects nie został usunięty")
    names = [it.obj.name for it in cam.af_frame_objects if it.obj]
    check(names == ["Cube"], f"lista po migracji: {names}")
    check("Pominięto 1 obiekt(ów)" in rep, f"brak informacji o brakującym obiekcie:\n{rep}")


def test_06_licznik():
    sc, cam, cube, orig = build()
    ld = bpy.data.lights.new("Swiatlo", 'POINT')
    light = bpy.data.objects.new("Swiatlo", ld)
    sc.collection.objects.link(light)
    select(light)
    n = len(af._collect_objects(bpy.context, cam, True)[0])
    check(n == 0, f"dla samego światła funkcja zwraca {n}")
    select(cube)
    n = len(af._collect_objects(bpy.context, cam, True)[0])
    check(n == 1, f"dla sześcianu funkcja zwraca {n}")


def test_07_brak_widocznych_punktow():
    # Damped Track jest aktywny (niewyciszony), ale ma wpływ 0, więc kamera nie obraca się
    # w stronę celu. Kamera patrzy w dół (-Z), a sześcian jest nad nią, czyli za kamerą.
    sc, cam, cube, orig = build()
    cam.constraints[0].influence = 0.0
    cube.animation_data_clear()
    cube.location = (0, -10, 10)
    cam.animation_data_clear()
    cam.location = (0, -10, 2)
    cam.rotation_euler = (0, 0, 0)
    rep = frame()
    check("100.0%" not in rep, f"raport zawiera 100.0%:\n{rep}")
    check("brak danych" in rep, f"raport nie zawiera „brak danych”:\n{rep}")
    # część klatek: sześcian zjeżdża spod kamery nad nią
    cube.location = (0, -10, -5)
    cube.keyframe_insert("location", frame=1)
    cube.keyframe_insert("location", frame=30)
    cube.location = (0, -10, 10)
    cube.keyframe_insert("location", frame=31)
    cube.keyframe_insert("location", frame=60)
    select(cube)
    rep = frame()
    check(re.search(r"W \d+ klatkach obiekty były niewidoczne dla kamery", rep),
          f"brak linii o klatkach z niewidocznymi obiektami:\n{rep}")


def test_08_kamera_ortograficzna():
    sc, cam, cube, orig = build(ortho=True)
    rep = frame()
    check("skala orto:" in rep, f"raport nie zawiera „skala orto:”:\n{rep}")
    check("ogniskowa:" not in rep, f"raport mówi o ogniskowej:\n{rep}")
    check(keys_of(cam.data, "ortho_scale"), "ortho_scale nie jest animowana")
    check(not keys_of(cam.data, "lens"), "animowana jest ogniskowa zamiast skali")


def test_09_jedna_klatka():
    sc, cam, cube, orig = build()
    rep = frame(use_scene_range=False, frame_start=10, frame_end=10)
    check(rep.startswith("Zakres 10–10:"), f"nieoczekiwany raport:\n{rep}")
    check(margin(rep) >= 0, f"margines ujemny:\n{rep}")
    try:
        frame(frame_start=10, frame_end=9)
        raise AssertionError("zakres Do < Od nie zgłosił błędu")
    except RuntimeError as e:
        check("Nieprawidłowy zakres klatek." in str(e), f"inny błąd: {e}")


def test_10_wspolne_dane():
    sc, cam, cube, orig = build(lens=150.0)        # długa ogniskowa: trzeba oddalić
    cam2 = bpy.data.objects.new("Camera2", cam.data)
    sc.collection.objects.link(cam2)
    select(cube)
    rep = frame()
    check("Dane kamery „Camera” ma 2 obiektów – zmiana ogniskowej dotyczy ich wszystkich" in rep,
          f"brak ostrzeżenia o wspólnych danych:\n{rep}")


def test_11_cel_poza_scena():
    sc, cam, cube, orig = build()
    frame()
    emp = bpy.data.objects["AF_Cel_Camera"]
    sc.collection.objects.unlink(emp)
    check(sc.objects.get(emp.name) is None, "nie udało się odłączyć celu od sceny")
    select()
    frame()
    check(sc.objects.get("AF_Cel_Camera") is not None, "cel nie wrócił do sceny")
    check(len(targets()) == 1, "powstał drugi cel")


def test_12_kilka_zakresow():
    sc, cam, cube, orig = build(lens=150.0)
    sc.frame_end = 120
    frame(use_scene_range=False, frame_start=1, frame_end=30)
    emp = bpy.data.objects["AF_Cel_Camera"]
    before_t = {i: [k for k in ks if k[0] <= 30] for i, ks in keys_of(emp, "location").items()}
    before_z = [k for k in keys_of(cam.data, "lens").get(0, []) if k[0] <= 30]
    select()
    frame(frame_start=60, frame_end=90)
    after_t = {i: [k for k in ks if k[0] <= 30] for i, ks in keys_of(emp, "location").items()}
    after_z = [k for k in keys_of(cam.data, "lens").get(0, []) if k[0] <= 30]

    def same(a, b):
        return len(a) == len(b) and all(abs(x[0] - y[0]) < 1e-4 and abs(x[1] - y[1]) < 1e-4
                                        for x, y in zip(a, b))
    check(all(same(before_t[i], after_t[i]) for i in range(3)), "zmieniły się klucze celu w 1–30")
    check(before_z and same(before_z, after_z), "zmieniły się klucze ogniskowej w 1–30")
    check(any(k[0] >= 60 for k in keys_of(emp, "location")[0]), "brak kluczy celu w 60–90")


def _load_v200():
    """Wersja 2.0.0 z historii Gita (do testu zgodności), zapisana w katalogu tymczasowym."""
    try:
        src = subprocess.check_output(["git", "-C", REPO, "show", "v2.0.0:auto_kadrowanie_kamery.py"])
    except (OSError, subprocess.CalledProcessError):
        return None
    path = os.path.join(TMP, "af_v200.py")
    with open(path, "wb") as f:
        f.write(src)
    spec = importlib.util.spec_from_file_location("af_v200", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_13_zgodnosc_z_200():
    old = _load_v200()
    sc, cam, cube, orig = build(lens=150.0)
    if old is not None:
        # prawdziwe kadrowanie wersją 2.0.0
        af.unregister()
        old.register()
        try:
            bpy.ops.camera.af_auto_frame()
        finally:
            old.unregister()
            af.register()
    else:
        # brak Gita: właściwości w formacie 2.0.0 ustawione ręcznie
        print("  (brak Gita - dane 2.0.0 odtworzone ręcznie)")
        emp = bpy.data.objects.new("AF_Cel_Camera", None)
        sc.collection.objects.link(emp)
        con = cam.constraints[0]
        cam["af_constraint"] = con.name
        cam["af_added"] = 0
        cam["af_orig_target"] = orig.name
        cam["af_orig_subtarget"] = ""
        cam["af_objects"] = "Cube"
        con.target = emp
        cd = cam.data
        cd["af_zoom_param"] = "lens"
        cd["af_zoom_value"] = cd.lens
        cd.lens = 100.0
        cd.keyframe_insert("lens", frame=1)
    check("af_target" not in cam and "af_objects" in cam, "kamera nie jest w formacie 2.0.0")
    select()
    rep = frame()
    check(margin(rep) >= 0, f"ponowne kadrowanie po 2.0.0: margines ujemny:\n{rep}")
    check(len(targets()) == 1, "po ponownym kadrowaniu jest więcej niż jeden cel")
    check("af_objects" not in cam, "nie zmigrowano listy obiektów")
    bpy.ops.camera.af_reset()
    check(not targets(), "„Przywróć oryginał” nie usunął celu")
    check(cam.constraints[0].target == orig, "nie przywrócono poprzedniego celu constraintu")
    check(abs(cam.data.lens - 150.0) < 1e-4, f"nie przywrócono ogniskowej: {cam.data.lens}")
    check(not keys_of(cam.data, "lens"), "zostały klucze ogniskowej")
    left = [k for k in cam.keys() if k.startswith("af_") and k != "af_frame_objects"]
    check(not left, f"zostały klucze: {left}")
    check(len(cam.af_frame_objects) == 0, "nie wyczyszczono listy obiektów")


class _FakeLayout:
    """Atrapa układu panelu: zbiera napisy, żeby sprawdzić panel bez interfejsu."""

    def __init__(self, texts):
        self.texts = texts
        self.active = True

    def label(self, text="", icon='NONE'):
        self.texts.append(text)

    def prop(self, data, name, text=None, **kw):
        self.texts.append(text if text is not None else data.bl_rna.properties[name].name)

    def operator(self, idname, **kw):
        self.texts.append(idname)

    def column(self, **kw):
        return self

    row = box = column


def _panel_texts():
    texts = []
    af.AF_PT_panel.draw(type("P", (), {"layout": _FakeLayout(texts)})(), bpy.context)
    return texts


def test_14_napisy_panelu():
    sc, cam, cube, orig = build()
    check("Obiekty do kadrowania: 1" in _panel_texts(), f"licznik: {_panel_texts()}")
    ld = bpy.data.lights.new("Swiatlo", 'POINT')
    light = bpy.data.objects.new("Swiatlo", ld)
    sc.collection.objects.link(light)
    select(light)
    check("Zaznaczone obiekty nie mają geometrii" in _panel_texts(), f"światło: {_panel_texts()}")
    select()
    check("Zaznacz obiekty do kadrowania" in _panel_texts(), f"brak zaznaczenia: {_panel_texts()}")
    select(cube)
    frame()
    select()
    check("Użyję obiektów z ostatniego razu (1)" in _panel_texts(), f"ostatni raz: {_panel_texts()}")
    texts = _panel_texts()
    check("Ogniskowa" in texts and "Bez pompowania ogniskowej" in texts, f"perspektywa: {texts}")
    cam2 = bpy.data.objects.new("Camera2", cam.data)
    sc.collection.objects.link(cam2)
    cam.data.type = 'ORTHO'
    texts = _panel_texts()
    check("Skala orto" in texts and "Bez pompowania skali" in texts, f"orto: {texts}")
    check("Dane kamery współdzielone (2 obiekty)" in texts, f"wspólne dane: {texts}")


# ---------------------------------------------------------------- uruchomienie

def main():
    af.register()
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    failed = []
    for name, fn in tests:
        try:
            fn()
            print(f"OK    {name}")
        except Exception as e:
            failed.append(name)
            print(f"BŁĄD  {name}: {e}")
            if not isinstance(e, AssertionError):
                traceback.print_exc()
    af.unregister()
    shutil.rmtree(TMP, ignore_errors=True)
    print(f"\nWynik: {len(tests) - len(failed)}/{len(tests)} testów przeszło.")
    if failed:
        print("Nie przeszły: " + ", ".join(failed))
    sys.stdout.flush()
    sys.exit(1 if failed else 0)


main()
