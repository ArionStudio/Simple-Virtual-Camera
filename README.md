# Implementacja Kamery 3D z Nawigacją Sceny

## Przegląd

Implementacja w Pythonie systemu wirtualnej kamery, umożliwiającego użytkownikom nawigację i obserwację sceny 3D złożonej z czterech sześcianów. Projekt demonstruje zasady grafiki 3D, układów współrzędnych i transformacji kamery poprzez renderowanie w trybie wireframe i z użyciem algorytmu malarskiego (Painter's Algorithm) wspomaganego drzewem BSP (Binary Space Partitioning).

## Funkcjonalności

- Interaktywne sterowanie kamerą 3D z 6 stopniami swobody
- Implementacja podwójnego układu współrzędnych (Światowego i Kamery)
- Renderowanie w czasie rzeczywistym obiektów 3D w trybie wireframe
- Implementacja algorytmu malarskiego (Painter's Algorithm) z BSP
  - Poprawne dzielenie wielokątów przecinających płaszczyzny BSP
  - Obsługa widoku z wewnątrz obiektów
  - Culling tylnych ścian dla lepszej wydajności
- Projekcja perspektywiczna dla realistycznej wizualizacji 3D
- Sterowanie kamerą za pomocą klawiatury i myszy
- Scena złożona z czterech sześcianów ułożonych w prostym wzorze
- Informacje debugowania dostępne w czasie rzeczywistym
- Dynamiczne kolorowanie obiektów w zależności od odległości od kamery
  - Tryb odległościowy: Obiekty jaśniejsze gdy bliżej kamery
  - Tryb skali szarości: Intensywność szarości bazująca na odległości
  - Tryb oryginalny: Podstawowe kolory niezależne od odległości

## Stack Technologiczny

- **Język**: Python
- **Główne Biblioteki**:
  - NumPy: Operacje na macierzach i obliczenia wektorowe
  - Pygame: Zarządzanie oknem i renderowanie 3D
- **Kluczowe Komponenty**:
  - Własne macierze transformacji kamery
  - System rotacji oparty na kątach Eulera
  - Implementacja projekcji perspektywicznej
  - Silnik renderowania wireframe
  - Implementacja algorytmu malarskiego (Painter's Algorithm)
  - Drzewo BSP (Binary Space Partitioning) do określania kolejności renderowania

## Wymagania Systemowe

- Python 3.x
- NumPy
- pygame
- System Operacyjny: Windows/Linux/MacOS

## Instalacja

1. Sklonuj repozytorium
2. Zainstaluj wymagane zależności:
   ```bash
   pip install numpy pygame
   ```
3. Skonfiguruj zmienne środowiskowe jeśli potrzebne

## Uruchomienie

1. Przejdź do katalogu projektu
2. Uruchom główny skrypt dla podstawowego renderera:
   ```bash
   python src/main.py
   ```
3. Lub uruchom renderer z algorytmem malarskim i BSP:
   ```bash
   python src/painter_main.py
   ```

## Sterowanie Kamerą

- **Translacja** (klawiatura):

  - W/S: Ruch w przód/tył (oś Z)
  - A/D: Ruch w lewo/prawo (oś X)
  - Shift/Ctrl: Ruch w górę/dół (oś Y)

- **Rotacja** (mysz):

  - Lewy przycisk myszy + ruch: Obrót wokół osi X (pitch) i Y (yaw)
  - Środkowy przycisk myszy + ruch: Obrót wokół osi Z (roll)
  - Strzałki: Alternatywne sterowanie rotacją (góra/dół: pitch, lewo/prawo: yaw)
  - Alt + strzałki lewo/prawo: Roll

- **Widok**:
  - Kółko myszy: Zoom in/out (zmiana pola widzenia)
  - +/-: Zoom in/out z klawiatury
  - R: Reset kamery do pozycji początkowej
  - Spacja: Stabilizacja kamery (wyprostowanie)
  - F1: Włączenie/wyłączenie informacji debugowania
  - C: Przełączenie trybu kolorowania (odległościowy/skala szarości/oryginalny)
  - ESC: Wyjście z aplikacji

## Struktura Projektu

```
project/
├── src/
│   ├── camera/
│   │   └── camera.py         # Implementacja kamery
│   ├── scene/
│   │   ├── Cuboid.py         # Definicje obiektów 3D
│   │   └── scene.py          # Zarządzanie sceną
│   ├── render/
│   │   ├── renderer.py       # Podstawowy silnik renderowania
│   │   ├── painter_renderer.py # Renderer z algorytmem malarskim
│   │   ├── painter_bsp.py    # Implementacja BSP dla algorytmu malarskiego
│   │   └── projection.py     # Projekcja perspektywiczna
│   ├── transformation.py     # Macierze transformacji
│   ├── main.py               # Główny punkt wejścia dla podstawowego renderera
│   └── painter_main.py       # Główny punkt wejścia dla renderera z algorytmem malarskim
├── requirements.txt
└── README.md
```

## Szczegóły Implementacji

- **Model Kamery**:

  - Pozycja we współrzędnych światowych (x, y, z)
  - Orientacja wykorzystująca kąty Eulera
  - Macierz transformacji kamery
  - Parametry pola widzenia/zoom

- **Reprezentacja Sceny**:

  - Zestaw sześcianów ułożonych w prostym wzorze
  - Definicje wierzchołków i krawędzi we współrzędnych światowych
  - Tablice NumPy do efektywnego przechowywania współrzędnych

- **Pipeline Renderowania**:

  - Transformacja ze współrzędnych światowych do współrzędnych kamery
  - Projekcja perspektywiczna
  - Renderowanie wireframe lub z wypełnionymi ścianami (w zależności od wybranego renderera)
  - Aktualizacje wyświetlania w czasie rzeczywistym

- **Algorytm Malarski (Painter's Algorithm) z BSP**:

  - Wykorzystanie drzewa BSP (Binary Space Partitioning) do określenia poprawnej kolejności renderowania obiektów
  - Podział przestrzeni na regiony przed/za płaszczyznami w celu określenia widoczności
  - Renderowanie obiektów od najdalszych do najbliższych (back-to-front)
  - Wsparcie dla wypełnionych ścian z odpowiednim rozwiązaniem problemu widoczności
  - Dokładne dzielenie wielokątów przecinających płaszczyzny podziału w drzewie BSP
  - Culling tylnych ścian dla poprawy wydajności
  - Optymalizacja przetwarzania węzłów w drzewie BSP

- **System Kolorowania Bazujący na Odległości**:

  - Dynamiczna zmiana intensywności kolorów w zależności od odległości od kamery
  - Trzy tryby kolorowania: odległościowy, skala szarości i oryginalny
  - Płynne przejścia intensywności kolorów dla lepszej percepcji głębi
  - Konfigurowalny zakres min/max odległości dla efektu kolorowania

- **Debugowanie**:
  - Wyświetlanie informacji o pozycji i rotacji kamery
  - Statystyki wydajności (FPS)
  - Liczba twarzy w drzewie BSP
  - Liczba renderowanych ścian
  - Aktualny tryb kolorowania
