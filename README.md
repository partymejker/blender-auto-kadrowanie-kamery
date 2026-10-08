# Auto kadrowanie kamery

Dodatek do Blendera, który utrzymuje wybrane obiekty na środku kadru aktywnej kamery i pilnuje, żeby nie wychodziły poza ramę. Rozwiązuje problem obiektu, który ucieka z kadru albo nie jest na środku, gdy kamera się porusza, a obiekty się animują.

Położenie i obrót kamery oraz animacja obiektów zostają bez zmian. Dodatek animuje tylko cel, na który patrzy kamera, i opcjonalnie ogniskową.

## Najważniejsze cechy

- Automatyczny cel kamery (pusty obiekt `AF_Cel_<nazwa kamery>`) z kluczami tylko tam, gdzie są potrzebne.
- Wygładzanie ruchu kamery, żeby kamera nie szarpała.
- Ogniskowa w trzech trybach: *Animowana*, *Stała* albo *Bez zmian*; opcja „Bez pompowania ogniskowej”.
- Obsługa kamer perspektywicznych i ortograficznych.
- Kadrowanie kilku zakresów klatek po kolei, każdy z innymi ustawieniami.
- Raport po każdym uruchomieniu: najmniejszy margines i największe odchylenie od środka.
- Przycisk „Przywróć oryginał”, który cofa wszystkie zmiany dodatku.

Aktualna wersja: 2.0.2.

## Wymagania

- Blender 4.4 lub nowszy.
- Testowano na Blenderze 5.2.2 LTS, Windows 11.

## Instalacja w skrócie

1. Pobierz plik `auto_kadrowanie_kamery.py` z [najnowszego wydania](https://github.com/partymejker/blender-auto-kadrowanie-kamery/releases/latest). Nie zmieniaj nazwy pliku.
2. W Blenderze otwórz *Edit → Preferences → Add-ons*, kliknij strzałkę w prawym górnym rogu i wybierz *Install from Disk…*.
3. Wskaż pobrany plik i zaznacz pole przy „Auto kadrowanie kamery”.

Szczegóły, aktualizacja i odinstalowanie: [docs/instalacja.md](docs/instalacja.md).

## Szybki start

1. Upewnij się, że scena ma aktywną kamerę.
2. W widoku 3D zaznacz obiekty, które mają być w kadrze.
3. Naciśnij **N** i otwórz zakładkę **Kadrowanie**.
4. Kliknij **Wycentruj w kamerze**.
5. Przeczytaj raport pod przyciskami i odtwórz animację. Jeśli wynik się nie podoba, kliknij **Przywróć oryginał** albo naciśnij Ctrl+Z.

## Dokumentacja

- [Instalacja](docs/instalacja.md): pobranie, instalacja, aktualizacja, odinstalowanie.
- [Instrukcja](docs/instrukcja.md): jak działa dodatek, opis wszystkich opcji, raport, kadrowanie kilku zakresów, cofanie zmian.
- [Rozwiązywanie problemów](docs/rozwiazywanie-problemow.md): komunikaty, ostrzeżenia i typowe kłopoty.
- [Historia zmian](CHANGELOG.md)

## Licencja

GNU General Public License w wersji 3 lub dowolnej późniejszej (GPL-3.0-or-later). Pełny tekst: [LICENSE](LICENSE).

## Testy

Dla osób rozwijających dodatek: w folderze `tests/` jest skrypt, który sam buduje scenę testową i sprawdza działanie dodatku w Blenderze uruchomionym w tle. Dodatek jest wczytywany prosto z repozytorium, bez instalowania. W katalogu głównym repozytorium uruchom:

```
"<ścieżka do blender.exe>" -b --factory-startup --python tests/test_dodatek.py
```

Skrypt wypisuje wynik każdego testu i kończy się kodem wyjścia 1, jeśli któryś test nie przejdzie.

## Autor

partymejker
