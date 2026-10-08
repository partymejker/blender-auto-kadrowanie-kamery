# Instalacja

[← Powrót do README](../README.md)

## Wymagania

- Blender 4.4 lub nowszy (testowano na 5.2.2 LTS, Windows 11).

## 1. Pobranie pliku

1. Wejdź na stronę [najnowszego wydania](https://github.com/partymejker/blender-auto-kadrowanie-kamery/releases/latest). Starsze wersje są na liście [wszystkich wydań](https://github.com/partymejker/blender-auto-kadrowanie-kamery/releases).
2. W sekcji *Assets* kliknij `auto_kadrowanie_kamery.py` i zapisz plik na dysku.

**Nie zmieniaj nazwy pliku.** Blender używa nazwy pliku jako nazwy dodatku w swoim wnętrzu (tzw. nazwy modułu Pythona). Nazwa z kropkami, spacjami albo dopiskiem wersji, np. `auto_kadrowanie_kamery_v2.0.0.py` albo `auto_kadrowanie_kamery (1).py`, nie zadziała albo spowoduje, że Blender potraktuje plik jako inny dodatek. Jeśli przeglądarka dopisała do nazwy numer, usuń go, żeby plik nazywał się dokładnie `auto_kadrowanie_kamery.py`.

## 2. Instalacja w Blenderze

1. Otwórz *Edit → Preferences*.
2. Po lewej wybierz *Add-ons*.
3. Kliknij menu rozwijane (strzałkę) w prawym górnym rogu okna.
4. Wybierz *Install from Disk…*.
5. Wskaż pobrany plik `auto_kadrowanie_kamery.py` i potwierdź.
6. Na liście dodatków znajdź „Auto kadrowanie kamery” (możesz wpisać nazwę w pole wyszukiwania) i zaznacz pole przy jego nazwie, jeśli nie jest zaznaczone.

Po rozwinięciu wpisu dodatku zobaczysz jego wersję, autora i miejsce, w którym znajduje się panel.

## 3. Gdzie jest panel

1. Najedź kursorem na widok 3D.
2. Naciśnij klawisz **N**, żeby otworzyć panel boczny.
3. Kliknij zakładkę **Kadrowanie**.

Panel nazywa się „Auto kadrowanie kamery”. Jeśli scena nie ma aktywnej kamery, zobaczysz w nim tylko napis „Scena nie ma aktywnej kamery”.

Jak korzystać z panelu: [instrukcja.md](instrukcja.md).

## 4. Aktualizacja do nowszej wersji

1. Pobierz nowy plik `auto_kadrowanie_kamery.py` z wydania na GitHubie (bez zmiany nazwy).
2. W *Edit → Preferences → Add-ons* odznacz pole przy „Auto kadrowanie kamery”, żeby wyłączyć dodatek.
3. Zainstaluj nowy plik tak samo jak za pierwszym razem: strzałka w prawym górnym rogu → *Install from Disk…*. Nowy plik zastąpi stary, bo ma tę samą nazwę.
4. Zaznacz pole przy „Auto kadrowanie kamery”, żeby włączyć dodatek ponownie.
5. Rozwiń wpis dodatku i sprawdź numer wersji. Jeśli nadal widzisz starą wersję albo w panelu brakuje nowych opcji (np. „Wygładzanie (klatki)” w wersji 2.0.0), zamknij Blendera i uruchom go ponownie.

Ustawienia panelu są zapisywane w pliku `.blend` razem ze sceną, więc aktualizacja nie zmienia już wykonanego kadrowania.

## 5. Odinstalowanie

1. Jeśli dodatek kadrował kamerę w Twoim projekcie i chcesz wrócić do stanu sprzed kadrowania, najpierw kliknij w panelu **Przywróć oryginał** i zapisz plik `.blend`. Po odinstalowaniu ten przycisk nie będzie dostępny. Klucze i obiekt `AF_Cel_<nazwa kamery>`, które dodatek już utworzył, zostają w scenie i działają dalej także bez dodatku.
2. Otwórz *Edit → Preferences → Add-ons* i znajdź „Auto kadrowanie kamery”.
3. Odznacz pole przy nazwie, żeby wyłączyć dodatek.
4. Rozwiń wpis dodatku (albo jego menu) i wybierz *Uninstall*.

## Gdzie Blender trzyma plik dodatku

Po instalacji Blender kopiuje plik do folderu dodatków użytkownika:

| System | Folder |
|---|---|
| Windows | `%APPDATA%\Blender Foundation\Blender\<wersja>\scripts\addons` |
| macOS | `~/Library/Application Support/Blender/<wersja>/scripts/addons` |
| Linux | `~/.config/blender/<wersja>/scripts/addons` |

`<wersja>` to numer wersji Blendera, np. `5.2`. W Windows możesz wkleić ścieżkę z `%APPDATA%` w pasek adresu Eksploratora plików.

Jeśli instalacja przez *Preferences* sprawia kłopot, możesz przy zamkniętym Blenderze skopiować plik `auto_kadrowanie_kamery.py` do tego folderu (albo go z niego usunąć) i potem włączyć dodatek na liście *Add-ons*.

Problemy z instalacją: [rozwiazywanie-problemow.md](rozwiazywanie-problemow.md#panel-się-nie-pojawia-po-instalacji).
