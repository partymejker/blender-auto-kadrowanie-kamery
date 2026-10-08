# Historia zmian

Wszystkie istotne zmiany w dodatku „Auto kadrowanie kamery” są opisane w tym pliku.

Format jest oparty na [Keep a Changelog](https://keepachangelog.com/pl/1.1.0/), a numeracja wersji na [wersjonowaniu semantycznym](https://semver.org/lang/pl/).

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

[2.0.0]: https://github.com/partymejker/blender-auto-kadrowanie-kamery/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/partymejker/blender-auto-kadrowanie-kamery/releases/tag/v1.0.0
