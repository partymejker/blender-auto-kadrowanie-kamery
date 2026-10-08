# Historia zmian

Wszystkie istotne zmiany w dodatku „Auto kadrowanie kamery” są opisane w tym pliku.

Format jest oparty na [Keep a Changelog](https://keepachangelog.com/pl/1.1.0/), a numeracja wersji na [wersjonowaniu semantycznym](https://semver.org/lang/pl/).

## [2.0.2] - 2026-10-08

### Naprawiono

- Gramatyka ostrzeżenia o współdzielonych danych kamery: raport pisze „Dane kamery „<nazwa>” są używane przez 2 obiekty” (zamiast „ma 2 obiektów”), a liczba obiektów w raporcie i w panelu ma poprawną formę (2 obiekty, 5 obiektów).

## [2.0.1] - 2026-10-08

### Naprawiono

- Po zmianie nazwy kamery dodatek używa tego samego celu kamery (zmienia tylko jego nazwę), a „Przywróć oryginał” usuwa go i przywraca poprzedni cel constraintu.
- Lista obiektów z ostatniego razu działa po zmianie nazw obiektów, a gdy któryś obiekt usunięto, raport mówi o tym linią „Pominięto <n> obiekt(ów) z ostatniego razu, których nie ma już w pliku”.
- Panel pokazuje dokładnie tyle obiektów, ile zostanie wykadrowanych („Obiekty do kadrowania: <n>”, „Użyję obiektów z ostatniego razu (<n>)”), i ostrzega napisem „Zaznaczone obiekty nie mają geometrii”.
- Gdy obiekty nie były widoczne w żadnej klatce, raport pokazuje „brak danych” zamiast mylącego „100.0%”, a gdy tylko w części klatek, podaje ich liczbę.
- Przy kamerze ortograficznej raport i panel mówią o skali („skala orto:”, „Skala orto”, „Bez pompowania skali”), a nie o ogniskowej.
- Można kadrować zakres jednej klatki (*Od* = *Do*); błąd „Nieprawidłowy zakres klatek.” pojawia się tylko, gdy *Do* < *Od*.
- Panel i raport ostrzegają, gdy z tych samych danych kamery korzysta kilka obiektów, bo zmiana ogniskowej lub skali dotyczy ich wszystkich.
- Cel kamery, który nie należy do bieżącej sceny, jest przy kadrowaniu dołączany z powrotem do głównej kolekcji sceny.

### Zmieniono

- Autor dodatku: partymejker.
- W ustawieniach dodatku (*Edit → Preferences → Add-ons*) są odnośniki do dokumentacji i do zgłaszania błędów.

### Dodano

- Skrypt testów `tests/test_dodatek.py` uruchamiany w Blenderze w tle.

## [2.0.0] - 2026-10-08

### Dodano

- Opcja „Wygładzanie (klatki)” (domyślnie 24), która wygładza ścieżkę celu kamery w czasie.
- Opcja „Bez pompowania ogniskowej” (domyślnie włączona). Ogniskowa ma kształt jednej doliny i nigdy nie przybliża bardziej, niż pozwala margines.
- Kadrowanie wielu zakresów. Klucze poza wybranym zakresem zostają bez zmian.

### Zmieniono

- Ogniskowa jest liczona dla już wygładzonej ścieżki celu, więc margines jest zachowany.
- Raport podaje zakres klatek, a przycisk „Przywróć oryginał” obejmuje wszystkie zakresy.

### Naprawiono

- Szarpanie kamery i „pompowanie” ogniskowej (naprzemienne oddalanie i przybliżanie). Wersja 1.0.0 śledziła idealny środek klatka po klatce zbyt dokładnie. W teście na projekcie z rozkładaniem siatki sześcianu największe szarpnięcie zoomu spadło ok. 7 razy, a obrotu ok. 2 razy. Liczba zmian kierunku zoomu spadła z 3 do 0, przy odchyleniu od środka maks. ok. 2,3% kadru.

## [1.0.0] - 2026-10-08

### Dodano

- Pierwsze wydanie: automatyczny cel kamery (`AF_Cel_<kamera>`) z kluczami tylko tam, gdzie potrzeba.
- Tryby ogniskowej: Animowana, Stała, Bez zmian. Obsługa kamer perspektywicznych i ortograficznych.
- Opcje: Margines, Dokładność, Pozwól przybliżać, Uwzględnij dzieci, zakres klatek sceny albo własny.
- Raport z najmniejszym marginesem i odchyleniem od środka, przycisk „Przywróć oryginał”.

[2.0.2]: https://github.com/partymejker/blender-auto-kadrowanie-kamery/compare/v2.0.1...v2.0.2
[2.0.1]: https://github.com/partymejker/blender-auto-kadrowanie-kamery/compare/v2.0.0...v2.0.1
[2.0.0]: https://github.com/partymejker/blender-auto-kadrowanie-kamery/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/partymejker/blender-auto-kadrowanie-kamery/releases/tag/v1.0.0
