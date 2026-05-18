# Algorytm Dijkstry w Pythonie z wizualizacją grafu

Projekt implementuje algorytm Dijkstry w języku Python. Program:

- oblicza najkrótsze ścieżki od wybranego wierzchołka startowego,
- odtwarza minimalną drogę do wskazanego wierzchołka,
- wypisuje pełny przebieg algorytmu w formie tabeli (`Nr etapu | Zbiór L | ...`),
- rysuje skierowany graf z wagami,
- zaznacza najkrótszą ścieżkę kolorem czerwonym.

---

## Funkcjonalności

### Algorytm Dijkstry

Program oblicza:

- minimalny koszt dotarcia do każdego wierzchołka,
- poprzednika każdego wierzchołka,
- najkrótszą ścieżkę pomiędzy dwoma wskazanymi wierzchołkami.

### Tabela przebiegu algorytmu

Podczas działania program generuje tabelę zgodną z wymaganiami typowych zadań akademickich.

Przykład:

```c++
Nr etapu | Zbiór L             | B      | C      | D      | E      | F      | G      | H
------------------------------------------------------------------------------------------------
0        | {}                  | ∞      | ∞      | ∞      | ∞      | ∞      | ∞      | ∞
1        | {A}                 | 9(A)   | 3(A)   | ∞      | ∞      | ∞      | ∞      | ∞
2        | {A,C}               | 9(A)   | 3(A)   | 4(C)   | 10(C)  | ∞      | ∞      | 23(C)
3        | {A,C,D}             | 8(D)   | 3(A)   | 4(C)   | 9(D)   | 13(D)  | ∞      | 23(C)
```
## Wizualizacja grafu

Program wyświetla skierowany graf, w którym:

- strzałki pokazują kierunek krawędzi,
- liczby przy krawędziach oznaczają wagi,
- najkrótsza ścieżka jest podświetlona na czerwono.

---
### Wymagania
Python 3.8 lub nowszy

### Biblioteki:

- networkx
- matplotlib
  
### Instalacja
```
pip install networkx matplotlib
```
### Uruchomienie
python main.py


## Konfiguracja grafu

Graf definiowany jest jako słownik słowników:
```c++
graph = {
    'A': {'B': 9, 'C': 3},
    'B': {'E': 7, 'C': 2},
    'C': {'D': 1, 'E': 7, 'H': 20},
    'D': {'B': 4, 'F': 9, 'E': 5},
    'E': {'G': 8, 'F': 2, 'H': 9},
    'F': {'G': 4},
    'G': {'H': 2},
    'H': {'A': 4}
}
```
### Ustawienie wierzchołków
```py
start = 'A'   # wierzchołek początkowy
end = 'G'     # wierzchołek docelowy
```

### Przykładowy wynik
```
Najkrótsza ścieżka z A do G:
A -> C -> D -> E -> F -> G
Koszt: 15
```

## Główne funkcje
```py
dijkstra(graph, start)
```

### Uruchamia algorytm Dijkstry i zwraca:

```
distances – najkrótsze odległości,
previous – poprzedników w ścieżkach.
get_path(previous, start, end)
```

Odtwarza najkrótszą ścieżkę od `start` do `end`.

### `draw_graph(graph, shortest_path=None)`

Rysuje graf oraz opcjonalnie podświetla najkrótszą ścieżkę.

### `print_dijkstra_table(...)`

Wypisuje tabelę przebiegu algorytmu.

---

## Zastosowanie

Projekt jest szczególnie przydatny do:

- nauki algorytmu Dijkstry,
- rozwiązywania zadań na studiach,
- przygotowania do kolokwiów i egzaminów,
- wizualizacji grafów skierowanych.

---

## Autor

- [@Narothe](https://github.com/Narothe)

Projekt przygotowany w Pythonie jako pomoc edukacyjna do analizy najkrótszych ścieżek w grafach.
