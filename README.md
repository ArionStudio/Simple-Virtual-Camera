# Implementacja Kamery 3D z Nawigacją Sceny

## Przegląd

Implementacja w Pythonie systemu wirtualnej kamery, umożliwiającego użytkownikom nawigację i obserwację sceny 3D złożonej z czterech sześcianów. Projekt demonstruje zasady grafiki 3D, układów współrzędnych i transformacji kamery poprzez renderowanie w trybie wireframe.

## Funkcjonalności

- Interaktywne sterowanie kamerą 3D z 6 stopniami swobody
- Implementacja podwójnego układu współrzędnych (Światowego i Kamery)
- Renderowanie w czasie rzeczywistym obiektów 3D w trybie wireframe
- Projekcja perspektywiczna dla realistycznej wizualizacji 3D
- Sterowanie kamerą za pomocą klawiatury i myszy
- Scena złożona z czterech sześcianów ułożonych w prostym wzorze

## Stack Technologiczny

- **Język**: Python
- **Główne Biblioteki**:
  - NumPy: Operacje na macierzach i obliczenia wektorowe
  - PyOpenGL: Zarządzanie oknem i renderowanie 3D
- **Kluczowe Komponenty**:
  - Własne macierze transformacji kamery
  - System rotacji oparty na kątach Eulera/kwaternionach
  - Implementacja projekcji perspektywicznej
  - Silnik renderowania wireframe

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
2. Uruchom główny skrypt:
   ```bash
   python main.py
   ```

## Sterowanie Kamerą

- **Translacja** (klawiatura):
  - W/S: Ruch w przód/tył (oś Z)
  - A/D: Ruch w lewo/prawo (oś X)
  - Shift/Ctrl: Ruch w górę/dół (oś Y)

- **Rotacja** (mysz):
  - Lewy przycisk myszy + ruch: Obrót wokół osi X (pitch) i Y (yaw)
  - Środkowy przycisk myszy + ruch: Obrót wokół osi Z (roll)

- **Widok**:
  - Kółko myszy: Zoom in/out (zmiana pola widzenia)
  - +/-: Zoom in/out (zmiana pola widzenia)
  - R: Reset kamery do pozycji początkowej
  - E: Stabilizacja kamery (wyprostowanie)
  - ESC: Wyjście z aplikacji

## Struktura Projektu

```
project/
├── src/
│   ├── camera/
│   │   ├── camera.py          # Implementacja kamery
│   │   └── transformations.py # Macierze transformacji
│   ├── scene/
│   │   ├── objects.py         # Definicje obiektów 3D
│   │   └── scene.py          # Zarządzanie sceną
│   ├── renderer/
│   │   ├── renderer.py       # Silnik renderowania OpenGL
│   │   └── projection.py     # Projekcja perspektywiczna
│   └── main.py               # Główny punkt wejścia aplikacji
├── requirements.txt
└── README.md
```

## Szczegóły Implementacji

- **Model Kamery**:

  - Pozycja we współrzędnych światowych (x, y, z)
  - Orientacja wykorzystująca kąty Eulera lub kwaterniony
  - Macierz transformacji kamery
  - Parametry pola widzenia/zoom

- **Reprezentacja Sceny**:

  - Cztery sześciany ułożone w prostym wzorze
  - Definicje wierzchołków i krawędzi we współrzędnych światowych
  - Tablice NumPy do efektywnego przechowywania współrzędnych

- **Pipeline Renderowania**:
  - Transformacja ze współrzędnych światowych do współrzędnych kamery
  - Projekcja perspektywiczna
  - Renderowanie wireframe
  - Aktualizacje wyświetlania w czasie rzeczywistym
