# Rozwiązywanie problemów

[← Powrót do README](../README.md)

Każdy problem jest opisany w układzie: **objaw → przyczyna → co zrobić**. Opis opcji panelu znajdziesz w [instrukcji](instrukcja.md#panel-i-jego-opcje).

Spis treści:

- [Komunikaty błędów](#komunikaty-błędów)
- [Ostrzeżenia w raporcie](#ostrzeżenia-w-raporcie)
- [Ruch kamery i ogniskowej](#ruch-kamery-i-ogniskowej)
- [Kilka zakresów](#kilka-zakresów)
- [Panel i przyciski](#panel-i-przyciski)
- [Wydajność i dokładność](#wydajność-i-dokładność)

## Komunikaty błędów

### Komunikat „Zaznacz obiekty, które mają być w kadrze.”

**Objaw:** po kliknięciu **Wycentruj w kamerze** pojawia się ten komunikat i nic się nie dzieje.

**Przyczyna:** dodatek nie znalazł żadnego obiektu do kadrowania. Dzieje się tak, gdy:

- nic nie jest zaznaczone, a ta kamera nie była wcześniej kadrowana (albo po kliknięciu „Przywróć oryginał” zapamiętana lista obiektów została wyczyszczona);
- zaznaczone są tylko obiekty bez geometrii, np. światła, puste obiekty (Empty) bez podpiętych obiektów z geometrią, szkielety albo sama kamera (panel pokazuje wtedy „Zaznaczone obiekty nie mają geometrii”);
- wszystkie zapamiętane obiekty zostały usunięte z pliku albo ze sceny. Sama zmiana nazw obiektów nie przeszkadza.

**Co zrobić:** zaznacz w widoku 3D obiekty z geometrią (siatki, krzywe, teksty itp.) i kliknij przycisk ponownie. Jeśli chcesz kadrować obiekt bez geometrii, np. Empty, pod który podpięte są siatki, zaznacz go i upewnij się, że opcja „Uwzględnij dzieci” jest włączona. Zanim klikniesz, sprawdź w panelu napis „Obiekty do kadrowania: <liczba>”.

### Napis „Zaznaczone obiekty nie mają geometrii” w panelu

**Objaw:** w górnej części panelu, z ikoną ostrzeżenia, jest napis „Zaznaczone obiekty nie mają geometrii”.

**Przyczyna:** coś jest zaznaczone, ale żaden z zaznaczonych obiektów (ani ich dzieci, jeśli włączone jest „Uwzględnij dzieci”) nie ma geometrii. Tak jest np. przy zaznaczonym samym świetle, pustym obiekcie bez podpiętych siatek albo szkielecie. Kliknięcie **Wycentruj w kamerze** skończy się komunikatem „Zaznacz obiekty, które mają być w kadrze.”. Dodatek nie sięga wtedy po listę z ostatniego razu, bo zaznaczenie ma pierwszeństwo.

**Co zrobić:** zaznacz obiekty z geometrią. Jeśli chcesz użyć obiektów z ostatniego razu, odznacz wszystko. Panel pokaże wtedy „Użyję obiektów z ostatniego razu (<liczba>)”. Jeśli zaznaczony jest pusty obiekt z podpiętymi siatkami, włącz „Uwzględnij dzieci”.

### Komunikat „Nieprawidłowy zakres klatek.”

**Objaw:** po kliknięciu **Wycentruj w kamerze** pojawia się ten komunikat.

**Przyczyna:** koniec zakresu jest mniejszy niż początek. Przy wyłączonym „Zakres klatek sceny” chodzi o pola *Od* i *Do*, przy włączonym o *Start* i *End* sceny. Zakres jednej klatki (np. *Od* = 50, *Do* = 50) jest od wersji 2.0.1 prawidłowy.

**Co zrobić:** ustaw *Do* większe lub równe *Od* (albo *End* większe lub równe *Start*).

### Komunikat „Kamery panoramiczne nie są obsługiwane.”

**Objaw:** po kliknięciu **Wycentruj w kamerze** pojawia się ten komunikat.

**Przyczyna:** aktywna kamera sceny ma typ *Panoramic*. Dodatek obsługuje tylko kamery perspektywiczne (*Perspective*) i ortograficzne (*Orthographic*).

**Co zrobić:** w ustawieniach kamery (*Object Data Properties* kamery, pole *Type*) wybierz *Perspective* albo *Orthographic*, albo ustaw jako aktywną inną kamerę.

## Ostrzeżenia w raporcie

### Ostrzeżenie: obiekt wychodzi poza kadr

**Objaw:** w raporcie jest linia „Uwaga: obiekt wychodzi poza kadr - wybierz ogniskową Animowaną/Stałą” (przy kamerze ortograficznej: „Uwaga: obiekt wychodzi poza kadr - wybierz tryb Animowana/Stała”), a „Najmniejszy margines” ma wartość ujemną.

**Przyczyna:** w co najmniej jednej klatce obiekty nie mieszczą się w kadrze. Najczęściej dzieje się tak w trybie „Bez zmian”, bo dodatek tylko centruje i nie może oddalić kamery.

**Co zrobić:**

1. Ustaw „Ogniskowa” (przy kamerze ortograficznej: „Skala orto”) na *Animowana* albo *Stała* i kliknij **Wycentruj w kamerze** jeszcze raz.
2. Jeśli ostrzeżenie pojawia się mimo to, zmniejsz „Dokładność” (np. do 1%), żeby klucze dokładniej trzymały się wyliczonej ogniskowej, albo zwiększ „Margines”.
3. Sprawdź klatkę podaną w linii „Najmniejszy margines”. Jeśli w raporcie jest też ostrzeżenie o obiektach za kamerą, zacznij od [tego problemu](#ostrzeżenie-część-obiektów-była-za-kamerą).

### Ostrzeżenie: część obiektów była za kamerą

**Objaw:** w raporcie jest linia „Uwaga: część obiektów była za kamerą w niektórych klatkach”.

**Przyczyna:** w niektórych klatkach część punktów kadrowanych obiektów znalazła się za kamerą, np. obiekt przelatuje obok albo przez kamerę albo jest bardzo duży i otacza kamerę. Takie punkty są pomijane w obliczeniach, więc w tych klatkach kadr może być niedokładny, a obiekt może wychodzić poza ramę.

**Co zrobić:**

- Odtwórz animację z widoku kamery (Numpad 0) i znajdź klatki, w których obiekt jest za kamerą lub bardzo blisko niej.
- Wyklucz te klatki: wyłącz „Zakres klatek sceny” i kadruj tylko zakresy, w których obiekty są przed kamerą (patrz [kadrowanie kilku zakresów](instrukcja.md#kadrowanie-kilku-zakresów)).
- Nie zaznaczaj do kadrowania obiektów, które przechodzą za kamerę, jeśli nie muszą być w kadrze.

### Obiekty niewidoczne dla kamery

**Objaw:** w raporcie jest linia „W <n> klatkach obiekty były niewidoczne dla kamery” albo, zamiast liczb, „Najmniejszy margines: brak danych (obiekty niewidoczne w żadnej klatce)” i „Maks. odchylenie od środka: brak danych (obiekty niewidoczne w żadnej klatce)”.

**Przyczyna:** w tych klatkach żaden punkt kadrowanych obiektów nie był przed kamerą. Kamera nie mogła się do nich obrócić albo obiekty są cały czas za nią. Dzieje się tak np. wtedy, gdy constraint śledzący ma *Influence* mniejsze niż 1, gdy po nim działa inny constraint ograniczający obrót albo gdy *Locked Track* nie pozwala obrócić kamery w potrzebną stronę. Dla takich klatek dodatek nie ma czego zmierzyć, więc nie wlicza ich do marginesu i odchylenia.

**Co zrobić:**

- Odtwórz animację z widoku kamery (Numpad 0) i sprawdź, czy kamera w ogóle obraca się w stronę celu `AF_Cel_<nazwa kamery>`.
- Sprawdź constrainty kamery (*Object Constraint Properties*): czy constraint śledzący ma *Influence* = 1 i czy inny constraint nie blokuje obrotu.
- Jeśli obiekty są niewidoczne tylko w części animacji, kadruj tylko zakresy, w których kamera może je zobaczyć (patrz [kadrowanie kilku zakresów](instrukcja.md#kadrowanie-kilku-zakresów)).

### Pominięto obiekty z ostatniego razu

**Objaw:** w raporcie jest linia „Pominięto <n> obiekt(ów) z ostatniego razu, których nie ma już w pliku”.

**Przyczyna:** nic nie było zaznaczone, więc dodatek użył listy obiektów z ostatniego razu. Część z tych obiektów została od tamtej pory usunięta z pliku albo ze sceny. Pozostałe obiekty zostały wykadrowane normalnie. Zmiana nazw obiektów nie powoduje tego komunikatu.

**Co zrobić:** jeśli usunięcie było zamierzone, nic nie musisz robić. Przy następnym kadrowaniu komunikat już się nie pojawi, bo dodatek zapamiętał nową listę. Jeśli w kadrze brakuje jakiegoś obiektu, zaznacz wszystkie obiekty, które mają być w kadrze, i kliknij **Wycentruj w kamerze** jeszcze raz.

### Dane kamery są współdzielone

**Objaw:** w panelu jest napis „Dane kamery współdzielone (<liczba> obiekty)”, a w raporcie linia „Dane kamery „<nazwa danych>” ma <n> obiektów – zmiana ogniskowej dotyczy ich wszystkich” (przy kamerze ortograficznej: „… zmiana skali dotyczy ich wszystkich”).

**Przyczyna:** kilka obiektów-kamer korzysta z tych samych danych kamery (*Object Data*). Tak się dzieje np. po powieleniu kamery przez *Duplicate Linked* (Alt+D). Ogniskowa i skala są zapisane w danych kamery, więc ich zmiana dotyczy wszystkich tych kamer. Napis w panelu pojawia się zawsze przy współdzielonych danych, a linia w raporcie tylko wtedy, gdy dodatek rzeczywiście zmienił ogniskową lub skalę.

**Co zrobić:**

- Jeśli inne kamery mają mieć własną ogniskową, rozdziel dane, zanim zaczniesz kadrować: zaznacz kamerę, przejdź do *Object Data Properties* i kliknij liczbę użytkowników obok nazwy danych (tworzy to osobną kopię). Dodatek sam niczego nie rozdziela.
- Jeśli chcesz tylko centrować, bez zmiany ogniskowej, ustaw „Ogniskowa” na *Bez zmian*.
- Jeśli wspólna ogniskowa jest zamierzona, ostrzeżenie możesz zignorować.

## Ruch kamery i ogniskowej

### Kamera szarpie lub jest nerwowa

**Objaw:** kamera wykonuje małe, nerwowe ruchy albo ogniskowa przybliża i oddala na zmianę.

**Przyczyna:** wygładzanie jest za słabe albo ogniskowa może zmieniać kierunek wiele razy.

**Co zrobić:**

- Zwiększ „Wygładzanie (klatki)”. Poniżej ok. 8 wygładzanie prawie nie działa. Zacznij od wartości domyślnej 24 i zwiększaj (patrz [jak dobrać wartość](instrukcja.md#wygładzanie-jak-dobrać-wartość)).
- Włącz „Bez pompowania ogniskowej” (działa przy ogniskowej *Animowanej*).
- Jeśli włączone jest „Pozwól przybliżać”, wyłącz je. Ogniskowa będzie wtedy tylko oddalać.
- Rozważ ogniskową *Stała*: jedna wartość na cały zakres, bez zoomu.
- Jeśli korzystasz z wersji 1.0.0, zaktualizuj dodatek do 2.0.0, w której dodano wygładzanie ([instalacja](instalacja.md#4-aktualizacja-do-nowszej-wersji)).

### Obiekt za bardzo odjeżdża od środka

**Objaw:** obiekt jest wyraźnie poza środkiem kadru, a „Maks. odchylenie od środka” w raporcie przekracza ok. 5%.

**Przyczyna:** wygładzanie jest za silne w stosunku do długości ruchów w animacji albo „Dokładność” ma dużą wartość.

**Co zrobić:**

- Zmniejsz „Wygładzanie (klatki)”. Praktyczna zasada: od połowy do całej długości najkrótszego ruchu w animacji.
- Zmniejsz „Dokładność” (np. z 2% do 1%).
- Po każdej zmianie kliknij **Wycentruj w kamerze** i porównaj wartość „Maks. odchylenie od środka”.

### Za dużo kluczy

**Objaw:** cel kamery albo ogniskowa ma bardzo dużo kluczy, co utrudnia ręczne poprawki.

**Przyczyna:** mała wartość „Dokładność” (dodatek dokłada klucze, dopóki krzywa nie zmieści się w tej tolerancji) albo słabe wygładzanie, przez które ścieżka celu ma dużo drobnych zmian. Dodatek wstawia najwyżej 60 kluczy na zakres.

**Co zrobić:**

- Zwiększ „Dokładność” (np. do 3–5%).
- Zwiększ „Wygładzanie (klatki)”.
- Sprawdź w raporcie, czy margines i odchylenie od środka są nadal akceptowalne.

## Kilka zakresów

### Skok na styku dwóch zakresów

**Objaw:** w miejscu, gdzie kończy się jeden kadrowany zakres i zaczyna następny (np. 1–130 i 131–200), kamera albo ogniskowa gwałtownie przeskakuje.

**Przyczyna:** każdy zakres jest liczony osobno i kończy się własnym kluczem. Gdy zakresy się stykają, między ostatnim kluczem jednego a pierwszym kluczem drugiego jest tylko jedna klatka.

**Co zrobić:** kadruj taki fragment jednym zakresem (np. 1–200). Jeśli potrzebujesz różnych ustawień, zostaw między zakresami przerwę, w której Blender płynnie przejdzie od jednego stanu do drugiego.

### Stare klucze w przerwie między zakresami

**Objaw:** w przerwie między kadrowanymi zakresami kamera wykonuje dziwne ruchy, których się nie spodziewasz.

**Przyczyna:** wcześniej kadrowany był większy zakres, który obejmował też obecną przerwę. Jego klucze poza nowymi zakresami zostały nietknięte, bo dodatek nie zmienia kluczy poza kadrowanym zakresem.

**Co zrobić:** kliknij **Przywróć oryginał** (usuwa kadrowanie wszystkich zakresów), a potem kadruj zakresy po kolei od nowa.

## Panel i przyciski

### Przycisk „Przywróć oryginał” jest niewidoczny

**Objaw:** w panelu jest tylko przycisk **Wycentruj w kamerze**.

**Przyczyna:** przycisk jest widoczny tylko wtedy, gdy aktywna kamera była już kadrowana. Nie widać go, gdy:

- ta kamera nie była jeszcze kadrowana;
- zmieniła się aktywna kamera sceny (sprawdź napis „Kamera: <nazwa>” w panelu);
- kadrowanie zostało już cofnięte przyciskiem „Przywróć oryginał”.

**Co zrobić:** ustaw jako aktywną kamerę, która była kadrowana. Jeśli kadrowanie zostało już cofnięte, nie ma nic więcej do przywrócenia. Ostatnie operacje możesz też cofnąć przez Ctrl+Z.

### Przycisk „Wycentruj w kamerze” jest nieaktywny

**Objaw:** przycisk jest wyszarzony albo panel pokazuje tylko „Scena nie ma aktywnej kamery”.

**Przyczyna:** scena nie ma aktywnej kamery.

**Co zrobić:** zaznacz kamerę i naciśnij Ctrl+Numpad 0 albo wybierz ją w polu *Camera* w ustawieniach sceny (*Scene Properties*).

### Panel się nie pojawia po instalacji

**Objaw:** po naciśnięciu **N** w widoku 3D nie ma zakładki **Kadrowanie**.

**Przyczyna i co zrobić:**

- **Dodatek nie jest włączony.** Otwórz *Edit → Preferences → Add-ons*, znajdź „Auto kadrowanie kamery” i zaznacz pole przy nazwie.
- **Zmieniona nazwa pliku.** Plik musi nazywać się dokładnie `auto_kadrowanie_kamery.py`. Zmień nazwę i zainstaluj ponownie ([instalacja](instalacja.md#1-pobranie-pliku)).
- **Za stara wersja Blendera.** Dodatek wymaga Blendera 4.4 lub nowszego.
- **Kursor nie jest nad widokiem 3D.** Klawisz **N** otwiera panel boczny tego obszaru, nad którym jest kursor. Najedź na widok 3D i naciśnij **N** ponownie.
- **Zakładka jest schowana.** Gdy w panelu bocznym jest dużo zakładek, część z nich może się nie mieścić. Przewiń pasek zakładek kółkiem myszy albo powiększ okno.
- **Po aktualizacji nadal widać starą wersję.** Zamknij Blendera i uruchom go ponownie.

## Wydajność i dokładność

### Działanie przy bardzo gęstych siatkach

**Objaw:** kadr ma większy zapas wokół obiektu, niż wynika z ustawionego marginesu, albo obiekt wydaje się lekko przesunięty względem środka. Przy długich zakresach i ciężkich scenach obliczenia trwają długo.

**Przyczyna:**

- Siatki powyżej 5000 wierzchołków są liczone po prostopadłościanie otaczającym (bounding box), a nie po każdym wierzchołku. To szybsze, ale pudełko jest zwykle większe niż sam kształt, więc kadr ma lekki zapas, a środek kadru wypada na środku pudełka. Liczy się siatka po działaniu modyfikatorów, więc np. *Subdivision Surface* może przekroczyć próg 5000 wierzchołków.
- Dodatek kilka razy przechodzi przez każdą klatkę zakresu i za każdym razem Blender musi przeliczyć scenę (animacje, modyfikatory, symulacje).

**Co zrobić:**

- Jeśli zapas jest za duży, zmniejsz „Margines”.
- Jeśli chcesz, żeby obiekt mógł wypełnić kadr bardziej niż przy oryginalnej ogniskowej, włącz „Pozwól przybliżać”.
- Przy długich obliczeniach kadruj krótsze zakresy (patrz [kadrowanie kilku zakresów](instrukcja.md#kadrowanie-kilku-zakresów)).
