# Instrukcja (wersja 2.0.2)

[← Powrót do README](../README.md)

Spis treści:

- [Jak to działa](#jak-to-działa)
- [Podstawowe użycie](#podstawowe-użycie)
- [Panel i jego opcje](#panel-i-jego-opcje)
- [Wygładzanie: jak dobrać wartość](#wygładzanie-jak-dobrać-wartość)
- [Odczytywanie raportu](#odczytywanie-raportu)
- [Kadrowanie kilku zakresów](#kadrowanie-kilku-zakresów)
- [Co dodatek zmienia w scenie, a czego nie dotyka](#co-dodatek-zmienia-w-scenie-a-czego-nie-dotyka)
- [Cofanie zmian](#cofanie-zmian)
- [Ponowne uruchamianie po zmianie animacji](#ponowne-uruchamianie-po-zmianie-animacji)

## Jak to działa

Dodatek pracuje z **aktywną kamerą sceny** (tą, z której renderujesz). Nie rusza położenia ani obrotu kamery. Zamiast tego steruje punktem, na który kamera patrzy, i w razie potrzeby ogniskową.

Po kliknięciu **Wycentruj w kamerze** dodatek:

1. Tworzy pusty obiekt (Empty w kształcie kuli) o nazwie `AF_Cel_<nazwa kamery>`, czyli cel kamery. Nie jest on widoczny w renderze.
2. Podpina ten cel do pierwszego aktywnego (niewyciszonego) constraintu śledzącego kamery: *Damped Track*, *Track To* albo *Locked Track*. Constraint to w Blenderze reguła, która automatycznie ustawia obiekt, tu: obraca kamerę w stronę celu. Jeśli kamera nie ma takiego constraintu, dodatek dodaje nowy o nazwie „AF Damped Track”. Poprzedni cel constraintu zostaje zapamiętany.
3. Przechodzi przez każdą klatkę zakresu i liczy, gdzie musi być cel, żeby obrys zaznaczonych obiektów wypadał na środku kadru.
4. Wygładza tę ścieżkę w czasie, żeby kamera nie szarpała.
5. Liczy ogniskową potrzebną, żeby obiekty zmieściły się w kadrze z zadanym marginesem. Kamery ortograficzne zamiast ogniskowej dostają animację *Orthographic Scale*.
6. Wstawia klucze animacji tylko tam, gdzie są potrzebne (zwykle kilka do kilkunastu), z płynnym przejściem między nimi (interpolacja Bézier).
7. Na koniec sprawdza wynik w każdej klatce i pokazuje raport.

Przy dłuższych zakresach obliczenia mogą chwilę potrwać, bo dodatek przechodzi przez zakres klatka po klatce kilka razy.

Kilka rzeczy, które warto wiedzieć:

- **Liczą się tylko obiekty z geometrią**: siatki, krzywe, powierzchnie, metaballe, teksty, krzywe włosów, chmury punktów, wolumeny i Grease Pencil. Światła, kamery, puste obiekty (Empty) i szkielety (Armature) same nie są kadrowane, ale jeśli mają podpięte obiekty z geometrią, a opcja „Uwzględnij dzieci” jest włączona, te obiekty wchodzą do kadrowania.
- **Dodatek zapamiętuje listę obiektów.** Jeśli przy kolejnym uruchomieniu nic nie jest zaznaczone, użyje obiektów z ostatniego razu. Jeśli coś zaznaczysz, nowa lista zastąpi starą. Zmiana nazw obiektów nie psuje tej listy. Obiekty usunięte z pliku albo ze sceny są pomijane, a raport o tym informuje.
- **Zmiana nazwy kamery nie przeszkadza.** Dodatek pamięta swój cel kamery, więc po zmianie nazwy kamery użyje tego samego celu i zmieni jego nazwę na `AF_Cel_<nowa nazwa kamery>`. Jeśli cel nie należy do bieżącej sceny, dodatek dołącza go z powrotem do głównej kolekcji sceny.
- **Wielokrotne uruchomienie jest bezpieczne.** Dodatek najpierw cofa własne poprzednie zmiany ogniskowej w zakresie, a potem liczy od nowa.
- **Siatki powyżej 5000 wierzchołków** są liczone po prostopadłościanie otaczającym obiekt (bounding box, czyli najmniejsze pudełko, w którym mieści się obiekt). To szybsze i daje kadr z lekkim zapasem.
- **Kamery panoramiczne nie są obsługiwane.**

## Podstawowe użycie

1. Ustaw kamerę, z której renderujesz, jako aktywną kamerę sceny (np. zaznacz ją i naciśnij Ctrl+Numpad 0).
2. Zaznacz w widoku 3D obiekty, które mają być w kadrze. Samej kamery nie musisz odznaczać, dodatek ją pomija.
3. Najedź kursorem na widok 3D, naciśnij **N** i otwórz zakładkę **Kadrowanie**.
4. Sprawdź górną część panelu: „Kamera: <nazwa>” pokazuje, którą kamerę dodatek ustawi, a „Obiekty do kadrowania: <liczba>” mówi, ile obiektów zostanie wykadrowanych.
5. Na początek zostaw ustawienia domyślne.
6. Kliknij **Wycentruj w kamerze**.
7. Przeczytaj raport pod przyciskami (patrz [Odczytywanie raportu](#odczytywanie-raportu)), a potem odtwórz animację albo obejrzyj ją z widoku kamery (Numpad 0).
8. Jeśli wynik się nie podoba, zmień ustawienia i kliknij **Wycentruj w kamerze** jeszcze raz albo cofnij wszystko przyciskiem **Przywróć oryginał**.

## Panel i jego opcje

Na górze panelu dodatek pokazuje informacje:

| Napis | Znaczenie |
|---|---|
| „Kamera: <nazwa>” | Aktywna kamera sceny, którą dodatek będzie ustawiał. |
| „Dane kamery współdzielone (<liczba> obiekty)” albo „… (<liczba> obiektów)” | Ostrzeżenie: z tych samych danych kamery (*Object Data*) korzysta kilka obiektów. Zmiana ogniskowej lub skali dotknie ich wszystkich. Dodatek niczego sam nie rozdziela. Patrz [rozwiązywanie problemów](rozwiazywanie-problemow.md#dane-kamery-są-współdzielone). |
| „Obiekty do kadrowania: <liczba>” | Ile obiektów zostanie wykadrowanych: zaznaczone obiekty z geometrią, razem z dziećmi, jeśli włączone jest „Uwzględnij dzieci”. Kamera i cel `AF_Cel_…` nie są liczone. |
| „Zaznaczone obiekty nie mają geometrii” | Ostrzeżenie: coś jest zaznaczone, ale nie ma czego kadrować (np. samo światło). Przycisk zgłosi wtedy błąd. |
| „Użyję obiektów z ostatniego razu (<liczba>)” | Nic nie jest zaznaczone, ale ta kamera była już kadrowana. Dodatek użyje zapamiętanej listy, a liczba mówi, ile obiektów z niej zostanie wykadrowanych. |
| „Zaznacz obiekty do kadrowania” | Nic nie jest zaznaczone i nie ma zapamiętanej listy (albo żaden zapamiętany obiekt już nie istnieje). |
| „Scena nie ma aktywnej kamery” | Ustaw aktywną kamerę sceny. Bez niej panel nie pokazuje opcji. |

Opcje:

| Nazwa w panelu | Domyślnie | Co robi |
|---|---|---|
| Margines | 10% | Minimalny odstęp obiektów od każdej krawędzi kadru. Zakres 0–45%. Większy margines = więcej wolnego miejsca wokół obiektów, więc ogniskowa częściej się oddala. |
| Dokładność | 2% | Dopuszczalne odchylenie od ideału (zakres 0,1–10%). Mniej = dokładniej, ale więcej kluczy. Więcej = mniej kluczy i spokojniejsze krzywe, ale obiekt może trochę bardziej odjeżdżać od środka. |
| Wygładzanie (klatki) | 24 | Siła wygładzania ruchu kamery w klatkach (zakres 0–120). 0 = brak wygładzania. Więcej = spokojniejsza kamera, ale obiekt może lekko odjechać od środka. Wygładzanie działa też na ogniskową w trybie *Animowana*. Zobacz [jak dobrać wartość](#wygładzanie-jak-dobrać-wartość). |
| Ogniskowa | Animowana | *Animowana*: zmienia ogniskową tylko tam, gdzie obiekt by się nie zmieścił. *Stała*: jedna ogniskowa na cały zakres, dobrana do najtrudniejszej klatki. *Bez zmian*: tylko centrowanie, ogniskowa zostaje taka, jaka była. Przy kamerze ortograficznej zamiast ogniskowej zmieniany jest *Orthographic Scale*. |
| Bez pompowania ogniskowej | włączone | Działa tylko przy ogniskowej *Animowanej* (przy innych trybach opcja jest wyszarzona). Ogniskowa najpierw tylko się oddala, potem tylko wraca, bez przybliżania i oddalania na zmianę. Po wyłączeniu ogniskowa może oddalać się i wracać kilka razy, ciaśniej trzymając obiekty, ale zoom bywa wtedy nerwowy. |
| Pozwól przybliżać | wyłączone | Pozwala zwiększyć ogniskową ponad oryginalną, żeby obiekt bardziej wypełniał kadr (przy kamerze ortograficznej: zmniejszyć *Orthographic Scale*). Domyślnie dodatek tylko oddala. |
| Uwzględnij dzieci | włączone | Do kadrowania wchodzą też obiekty podpięte (parent) pod zaznaczone, również pośrednio (dzieci dzieci). |
| Zakres klatek sceny | włączone | Kadruje cały zakres sceny (*Start*–*End* na osi czasu). Po wyłączeniu pojawiają się pola *Od* i *Do* (domyślnie 1 i 250) oraz napis „Klucze poza zakresem zostają”. Wartość *Do* nie może być mniejsza niż *Od*. Zakres jednej klatki (*Od* = *Do*) jest dozwolony. |

Przy kamerze ortograficznej dwie opcje mają w panelu inne napisy, bo zamiast ogniskowej zmieniana jest skala (*Orthographic Scale*): „Ogniskowa” nazywa się „Skala orto”, a „Bez pompowania ogniskowej” nazywa się „Bez pompowania skali”. Działają tak samo.

Przyciski:

- **Wycentruj w kamerze**: uruchamia kadrowanie. Jest nieaktywny, gdy scena nie ma aktywnej kamery.
- **Przywróć oryginał**: cofa wszystkie zmiany dodatku dla aktywnej kamery (patrz [Cofanie zmian](#cofanie-zmian)). Jest widoczny tylko wtedy, gdy kamera była już kadrowana.

Pod przyciskami pojawia się raport z ostatniego uruchomienia.

## Wygładzanie: jak dobrać wartość

- Nie ma wartości „magicznych” ani zakazanych. Działa każda liczba całkowita od 0 do 120.
- Wartość to mniej więcej okno czasowe uśredniania ruchu, liczone w klatkach. Przy 24 kl./s 24 klatki to ok. 1 sekunda, przy 60 kl./s ok. 0,4 sekundy.
- Poniżej ok. 8 wygładzanie prawie nie działa.
- Za duża wartość w stosunku do długości ruchów w animacji rozmywa kolejne etapy ruchu. Obiekt bardziej odjeżdża od środka, a zoom oddala się wcześniej i dłużej, niż to konieczne. Margines nadal jest zachowany.
- Praktyczna zasada: od połowy do całej długości najkrótszego ruchu w animacji. Przykład: jeśli najkrótszy ruch trwa 40 klatek, zacznij od wartości między 20 a 40.
- Jeśli w raporcie „Maks. odchylenie od środka” przekracza ok. 5%, zmniejsz wartość. Jeśli kamera jest nerwowa, zwiększ.

## Odczytywanie raportu

Po każdym kliknięciu **Wycentruj w kamerze** pod przyciskami pojawia się ramka z raportem. Ta sama treść pokazuje się na chwilę na pasku stanu Blendera (linie są tam oddzielone znakiem `|`).

**`Zakres <od>–<do>: cel <n> kluczy, ogniskowa: …`** (przy kamerze ortograficznej: **`Zakres <od>–<do>: cel <n> kluczy, skala orto: …`**)

Jaki zakres klatek był kadrowany i ile kluczy dostał cel kamery w tym zakresie. Po słowie „ogniskowa:” albo „skala orto:” jest jedno z:

| Tekst | Znaczenie |
|---|---|
| `<n> kluczy` | Tryb *Animowana*: ogniskowa (lub skala) została zmieniona i dostała tyle kluczy w zakresie. |
| `bez zmian (mieści się)` | Tryb *Animowana*: obiekty mieściły się z marginesem przy oryginalnej ogniskowej, więc nic nie trzeba było zmieniać. |
| `stała <wartość> mm` | Tryb *Stała*: ustawiona ogniskowa. Przy kamerze ortograficznej jest tu wartość *Orthographic Scale* bez „mm”. |
| `bez zmian` | Tryb *Bez zmian*: ogniskowa nie była ruszana. |

**`Najmniejszy margines: <x>% (klatka <k>)`**

Najciaśniejsze miejsce w zakresie: najmniejszy odstęp obiektów od krawędzi kadru i klatka, w której wystąpił. Wartość bliska ustawionemu marginesowi jest w porządku. Wartość ujemna oznacza, że w tej klatce obiekt wychodzi poza kadr.

**`Maks. odchylenie od środka: <x>% (klatka <k>)`**

Jak daleko środek obiektów odjechał od środka kadru (w procentach szerokości lub wysokości kadru) i w której klatce. Kilka procent to normalny skutek wygładzania. Jeśli wartość przekracza ok. 5%, zmniejsz „Wygładzanie (klatki)”.

**`Najmniejszy margines: brak danych (obiekty niewidoczne w żadnej klatce)`** i **`Maks. odchylenie od środka: brak danych (obiekty niewidoczne w żadnej klatce)`**

Te dwie linie zastępują dwie poprzednie, gdy w żadnej klatce zakresu żaden punkt obiektów nie był przed kamerą. Nie było czego zmierzyć, więc raport nie podaje liczb, a komunikat ma poziom ostrzeżenia. Co zrobić: [rozwiązywanie problemów](rozwiazywanie-problemow.md#obiekty-niewidoczne-dla-kamery).

Pod tymi liniami mogą pojawić się dodatkowe linie i ostrzeżenia. Każde z nich zmienia poziom komunikatu na ostrzeżenie.

**`W <n> klatkach obiekty były niewidoczne dla kamery`**

W części klatek zakresu żaden punkt obiektów nie był przed kamerą. Te klatki nie są brane pod uwagę przy liczeniu marginesu i odchylenia. Co zrobić: [rozwiązywanie problemów](rozwiazywanie-problemow.md#obiekty-niewidoczne-dla-kamery).

**Ostrzeżenie: `Uwaga: obiekt wychodzi poza kadr - wybierz ogniskową Animowaną/Stałą`** (przy kamerze ortograficznej: `Uwaga: obiekt wychodzi poza kadr - wybierz tryb Animowana/Stała`)

Pojawia się, gdy najmniejszy margines jest ujemny. Najczęściej przy trybie „Bez zmian”, bo wtedy dodatek nie może oddalić kamery. Co zrobić: [rozwiązywanie problemów](rozwiazywanie-problemow.md#ostrzeżenie-obiekt-wychodzi-poza-kadr).

**Ostrzeżenie: `Uwaga: część obiektów była za kamerą w niektórych klatkach`**

W niektórych klatkach część punktów obiektów znalazła się za kamerą. Takie punkty są pomijane w obliczeniach, więc wynik w tych klatkach może być niedokładny. Co zrobić: [rozwiązywanie problemów](rozwiazywanie-problemow.md#ostrzeżenie-część-obiektów-była-za-kamerą).

**`Pominięto <n> obiekt(ów) z ostatniego razu, których nie ma już w pliku`**

Pojawia się, gdy nic nie było zaznaczone i dodatek użył listy obiektów z ostatniego razu, a część z tych obiektów usunięto z pliku albo ze sceny. Pozostałe obiekty zostały wykadrowane. Co zrobić: [rozwiązywanie problemów](rozwiazywanie-problemow.md#pominięto-obiekty-z-ostatniego-razu).

**`Dane kamery „<nazwa danych>” są używane przez <n> obiekty – zmiana ogniskowej dotyczy ich wszystkich`** (przy 5 i więcej obiektach: „… przez <n> obiektów …”) (przy kamerze ortograficznej: „… zmiana skali dotyczy ich wszystkich”)

Pojawia się, gdy dodatek zmienił ogniskową lub skalę, a z tych samych danych kamery korzysta kilka obiektów. Co zrobić: [rozwiązywanie problemów](rozwiazywanie-problemow.md#dane-kamery-są-współdzielone).

## Kadrowanie kilku zakresów

Od wersji 2.0.0 możesz kadrować różne części animacji osobno, każdą z innymi ustawieniami i innymi obiektami.

Zasady:

- Klucze celu i ogniskowej **poza** wybranym zakresem zostają nietknięte.
- Ponowne uruchomienie dla danego zakresu zmienia tylko ten zakres.
- W przerwie między zakresami Blender płynnie przechodzi od ostatniego klucza jednego zakresu do pierwszego klucza następnego. Dodatek nie pilnuje wtedy centrowania.
- W przerwie mogą zostać stare klucze z wcześniejszego kadrowania większego zakresu. Żeby zacząć od czystej sytuacji, kliknij najpierw **Przywróć oryginał**.
- Nie stykaj zakresów (np. 1–130 i 131–200), bo na styku może pojawić się skok. Lepiej wtedy kadrować jednym zakresem.
- Zakres może wykraczać poza koniec animacji sceny. Do renderu trzeba wtedy wydłużyć zakres sceny (*End* na osi czasu).
- Zakres może mieć jedną klatkę (*Od* = *Do*), np. żeby wykadrować jedno ujęcie stopklatki.

### Przykład: 1–130 z animowaną ogniskową, potem 250–300 z samym centrowaniem

1. Jeśli kamera była już wcześniej kadrowana, kliknij **Przywróć oryginał**, żeby zacząć od czystej sytuacji.
2. Zaznacz obiekty, które mają być w kadrze w klatkach 1–130.
3. Wyłącz „Zakres klatek sceny”. Wpisz *Od* = 1, *Do* = 130.
4. Ustaw „Ogniskowa” na *Animowana*.
5. Kliknij **Wycentruj w kamerze** i sprawdź raport. Pierwsza linia zaczyna się od „Zakres 1–130”.
6. Zaznacz obiekty, które mają być w kadrze w klatkach 250–300 (mogą być inne niż w pierwszym zakresie). Jeśli to te same obiekty, możesz niczego nie zaznaczać, dodatek użyje obiektów z ostatniego razu.
7. Wpisz *Od* = 250, *Do* = 300.
8. Ustaw „Ogniskowa” na *Bez zmian*.
9. Kliknij **Wycentruj w kamerze**. Raport zaczyna się od „Zakres 250–300”, a ogniskowa ma opis „bez zmian”.
10. Jeśli scena kończy się przed klatką 300, wydłuż zakres sceny (*End*) do co najmniej 300, żeby wyrenderować całość.

Efekt: w klatkach 1–130 obiekty są na środku i ogniskowa oddala się tam, gdzie trzeba. W klatkach 131–249 kamera i ogniskowa płynnie przechodzą od stanu z klatki 130 do stanu z klatki 250, bez pilnowania centrowania. W klatkach 250–300 obiekty są na środku, a ogniskowa jest taka jak oryginalnie.

## Co dodatek zmienia w scenie, a czego nie dotyka

Zmienia:

- Tworzy obiekt `AF_Cel_<nazwa kamery>` (Empty w kształcie kuli, ukryty w renderze) i animuje jego położenie.
- Zmienia cel pierwszego aktywnego constraintu śledzącego kamery (*Damped Track*, *Track To* albo *Locked Track*) na ten obiekt albo, jeśli kamera nie ma takiego constraintu, dodaje constraint „AF Damped Track”. Od tej chwili to constraint wyznacza, w którą stronę patrzy kamera.
- W trybie *Animowana* lub *Stała* zmienia ogniskową kamery (przy kamerze ortograficznej: *Orthographic Scale*) i jej klucze w kadrowanym zakresie.
- Zapisuje w kamerze dane potrzebne do cofnięcia zmian: poprzedni cel constraintu, oryginalną ogniskową z kluczami, odwołanie do obiektu-celu i listę kadrowanych obiektów.
- Jeśli kamera była kadrowana wersją 2.0.0, przy pierwszym kadrowaniu w nowej wersji dodatek sam przepisuje zapamiętaną listę obiektów do nowego formatu.

Nie dotyka:

- położenia i obrotu kamery ani ich animacji,
- animacji kadrowanych obiektów ani żadnych innych obiektów w scenie,
- kluczy celu i ogniskowej poza kadrowanym zakresem,
- innych kamer niż aktywna kamera sceny. Wyjątek: jeśli inna kamera korzysta z tych samych danych kamery, zmiana ogniskowej lub skali dotyczy też jej. Panel i raport ostrzegają o tym.

## Cofanie zmian

**Przycisk „Przywróć oryginał”**

- Przywraca poprzedni cel constraintu albo usuwa dodany „AF Damped Track”.
- Przywraca oryginalną ogniskową (lub *Orthographic Scale*) i jej klucze.
- Usuwa obiekt `AF_Cel_<nazwa kamery>`.
- Czyści zapamiętaną listę obiektów, więc przy następnym kadrowaniu trzeba znów zaznaczyć obiekty.
- Dotyczy **wszystkich** zakresów naraz. Nie da się cofnąć tylko jednego zakresu.
- Przywrócone klucze ogniskowej mają oryginalne klatki i wartości, ale domyślną interpolację z ustawień Blendera. Wcześniejsze niestandardowe uchwyty i interpolacja nie są odtwarzane.
- Przycisk jest widoczny tylko wtedy, gdy aktywna kamera była już kadrowana.

**Ctrl+Z**

Kadrowanie i przywracanie można też cofnąć zwykłym Ctrl+Z (*Edit → Undo*). To wygodne, gdy chcesz wrócić tylko o jedno uruchomienie, np. po kadrowaniu drugiego zakresu.

## Ponowne uruchamianie po zmianie animacji

Dodatek liczy klucze na podstawie animacji, jaka jest w chwili kliknięcia. Jeśli potem zmienisz ruch obiektów albo kamery, kadrowanie nie zaktualizuje się samo.

1. Ustaw ten sam zakres i te same opcje co poprzednio.
2. Jeśli kadrujesz te same obiekty, możesz niczego nie zaznaczać (panel pokaże „Użyję obiektów z ostatniego razu (<liczba>)”).
3. Kliknij **Wycentruj w kamerze**.

Dodatek sam cofnie swoje poprzednie zmiany ogniskowej w tym zakresie i policzy wszystko od nowa. Nie musisz wcześniej klikać „Przywróć oryginał”. Zrób to tylko wtedy, gdy chcesz pozbyć się kadrowania wszystkich zakresów, np. przed kadrowaniem jednego dużego zakresu w miejsce kilku mniejszych.
