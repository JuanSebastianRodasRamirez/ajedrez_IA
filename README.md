# 🐴 Smart Horses - Juego de Estrategia con IA

**Smart Horses** es un juego de estrategia por turnos donde dos jugadores (o un jugador contra la IA) controlan caballos en un tablero tipo ajedrez. El objetivo es acumular la mayor cantidad de puntos recogiendo bonificaciones del tablero mientras se bloquean estratégicamente las casillas.

## 📋 Tabla de Contenidos
- [Características](#características)
- [Reglas del Juego](#reglas-del-juego)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Cómo Jugar](#cómo-jugar)
- [Implementación Técnica](#implementación-técnica)
- [Algoritmo de IA - Minimax](#algoritmo-de-ia---minimax)
- [Función Heurística](#función-heurística)
- [Ejemplos de Uso](#ejemplos-de-uso)
- [Estructura del Proyecto](#estructura-del-proyecto)

---

## ✨ Características

- 🎮 **Interfaz gráfica intuitiva** con Tkinter
- 🤖 **IA con tres niveles de dificultad**:
  - Principiante (profundidad 2)
  - Amateur (profundidad 4)
  - Experto (profundidad 6)
- 🧠 **Algoritmo Minimax con poda alfa-beta**
- 📊 **Sistema de puntuación dinámico**
- 🎯 **10 casillas especiales** con puntos positivos y negativos
- ♟️ **Movimientos tipo caballo de ajedrez**
- 🔒 **Casillas bloqueadas permanentemente** después de visitarlas

---

## 🎯 Reglas del Juego

### Objetivo
Acumular más puntos que tu oponente recogiendo bonificaciones del tablero.

### Mecánica
1. **Tablero**: 8x8 casillas (como un tablero de ajedrez)
2. **Caballos**: Cada jugador controla 1 caballo que se mueve como en ajedrez
3. **Puntos**: Hay 10 casillas con valores especiales:
   - **Positivos**: +1, +3, +4, +5, +10
   - **Negativos**: -1, -3, -4, -5, -10
4. **Turnos**: Los jugadores se alternan para mover su caballo
5. **Casillas bloqueadas**: Después de visitar una casilla, queda bloqueada permanentemente

### Condiciones de Victoria/Derrota

El juego termina cuando:

1. **Ningún jugador puede moverse**: 
   - Se aplica una **penalización de -4 puntos** a cada jugador sin movimientos
   - Gana el jugador con mayor puntuación
   - Si hay empate en puntuación: **EMPATE**

2. **Un jugador se queda sin movimientos** (mientras el otro puede moverse):
   - El jugador sin movimientos recibe **-4 puntos de penalización**
   - El juego continúa hasta que ambos no puedan moverse

### Penalizaciones
- **-4 puntos** cuando un jugador no tiene movimientos legales disponibles

---

## 💻 Requisitos

- Python 3.8 o superior
- Tkinter (incluido con Python en la mayoría de instalaciones)

### Librerías necesarias (estándar de Python)
```python
- typing
- random
- math
- tkinter
- threading
- time
```

---

## 🚀 Instalación

### 1. Clonar el repositorio
```bash
git clone https://github.com/JuanSebastianRodasRamirez/ajedrez_IA.git
cd ajedrez_IA
```

### 2. Verificar instalación de Python
```bash
python --version
# Debe ser Python 3.8 o superior
```

### 3. Ejecutar el juego
```bash
python gui.py
```

O si usas Python 3 específicamente:
```bash
python3 gui.py
```

---

## 🎮 Cómo Jugar

### Inicio del Juego

1. **Ejecuta** `gui.py`
2. **Selecciona la dificultad** de la IA:
   - Principiante (más rápida, menos estratégica)
   - Amateur (balance entre velocidad y estrategia)
   - Experto (más lenta, muy estratégica)
3. El tablero se generará automáticamente con:
   - Tu caballo (Negro) en una posición aleatoria
   - El caballo de la IA (Blanco) en otra posición
   - 10 casillas con puntos distribuidas aleatoriamente

### Durante el Juego

**La IA (Blanco) siempre juega primero**

Cuando sea tu turno (Negro):
1. **Haz clic en tu caballo** para seleccionarlo (se iluminará en amarillo)
2. **Haz clic en una casilla naranja** (movimiento legal) para mover
3. Los puntos se recogerán automáticamente
4. La casilla visitada se bloqueará (aparecerá en gris)

### Indicadores Visuales

| Color | Significado |
|-------|-------------|
| 🟩 Verde | Casilla con puntos positivos |
| 🟥 Rojo | Casilla con puntos negativos |
| 🟧 Naranja | Movimiento legal disponible |
| 🟨 Amarillo | Caballo seleccionado |
| ⬜ Gris claro | Caballo de la IA (Blanco) |
| ⬛ Gris oscuro | Tu caballo (Negro) |
| ⬜ Gris | Casilla bloqueada |

### Interfaz

```
┌─────────────────────────────────────────────────────────┐
│ Turno: Jugador (Negro) | Dificultad: Amateur |         │
│ IA: 15  Jugador: 8                    [Nuevo Juego]    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│              [Tablero 8x8 Interactivo]                 │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 Implementación Técnica

### Arquitectura del Código

El proyecto está dividido en dos módulos principales:

#### 1. `game.py` - Lógica del juego

**Clases principales:**

##### `Horse` (Caballo)
```python
class Horse:
    def __init__(self, horse_id: str, owner: str, pos: Position)
    def possible_moves(self, board: Board, occupied: Set[Position]) -> List[Position]
    def move_and_collect(self, to: Position, board: Board) -> int
```
- Representa un caballo con ID, propietario y posición
- Calcula movimientos legales (tipo ajedrez)
- Mueve y recoge puntos del tablero

##### `Board` (Tablero)
```python
class Board:
    def __init__(self, width: int, height: int, points: Dict[Position, int])
    def in_bounds(self, pos: Position) -> bool
    def get_points(self, pos: Position) -> int
    def block_position(self, pos: Position) -> None
    def is_blocked(self, pos: Position) -> bool
```
- Almacena el estado del tablero (8x8)
- Gestiona puntos por casilla
- Mantiene registro de casillas bloqueadas

##### `Game` (Juego)
```python
class Game:
    def initialize(self, width: int, height: int, player_ids: List[str], seed: int)
    def generate_moves_for_player(self, player: str) -> List[Tuple[str, Position]]
    def apply_move(self, horse_id: str, to: Position) -> int
    def is_game_over(self) -> Tuple[bool, str, Optional[str]]
```
- Coordina toda la mecánica del juego
- Gestiona turnos y puntuaciones
- Verifica condiciones de victoria/derrota

##### `AIPlayer` (Jugador IA)
```python
class AIPlayer:
    def __init__(self, player_id: str, depth: int)
    def get_best_move(self, game: Game) -> Optional[Tuple[str, Position]]
```
- Implementa la inteligencia artificial
- Usa Minimax con poda alfa-beta
- Niveles de dificultad según profundidad

#### 2. `gui.py` - Interfaz gráfica

**Clase principal:**

##### `GameGUI`
```python
class GameGUI:
    def __init__(self, root: tk.Tk, game: Game, difficulty: str)
    def refresh(self) -> None
    def on_cell_click(self, pos: Position) -> None
    def make_ai_move(self) -> None
    def check_game_over(self) -> None
```
- Interfaz Tkinter interactiva
- Visualización del tablero
- Manejo de eventos del usuario
- Ejecución de movimientos de la IA en hilo separado

---

## 🧠 Algoritmo de IA - Minimax

La IA utiliza el **algoritmo Minimax con poda alfa-beta**, un método clásico de búsqueda en árboles de juegos.

### ¿Qué es Minimax?

Minimax es un algoritmo de decisión que:
1. **Explora** posibles secuencias de movimientos futuros
2. **Evalúa** cada posición resultante
3. **Asume** que el oponente jugará óptimamente
4. **Selecciona** el movimiento que maximiza la ventaja

### Implementación

```python
def _minimax(self, game: Game, depth: int, is_maximizing: bool, 
             alpha: float, beta: float) -> float:
    """
    Algoritmo Minimax con poda alfa-beta
    
    Parámetros:
    - game: Estado actual del juego
    - depth: Profundidad de búsqueda restante
    - is_maximizing: True si es turno de la IA, False si es del oponente
    - alpha: Mejor valor para el maximizador
    - beta: Mejor valor para el minimizador
    
    Retorna: Evaluación numérica de la posición
    """
```

### Profundidad de Búsqueda

La profundidad determina cuántos movimientos adelante analiza la IA:

| Nivel | Profundidad | Movimientos Analizados | Velocidad | Dificultad |
|-------|-------------|------------------------|-----------|------------|
| Principiante | 2 | ~100-500 | Rápida | Fácil |
| Amateur | 4 | ~10,000-50,000 | Media | Moderada |
| Experto | 6 | ~1M-5M | Lenta | Difícil |

### Poda Alfa-Beta

La **poda alfa-beta** es una optimización que:
- Elimina ramas del árbol de búsqueda que no pueden afectar la decisión final
- Reduce drásticamente el número de posiciones evaluadas
- Mantiene el resultado idéntico al Minimax puro

**Ejemplo de poda:**
```
Si encontramos un movimiento con valor 10, y una rama alternativa
ya garantiza valor -5 para el oponente, no necesitamos explorar
más esa rama (el oponente nunca la elegiría).
```

### Pseudocódigo Simplificado

```
función minimax(posición, profundidad, es_maximizando):
    si profundidad == 0 o juego_terminado:
        retornar evaluación_heurística(posición)
    
    si es_maximizando:  # Turno de la IA
        mejor_valor = -infinito
        para cada movimiento posible:
            valor = minimax(nueva_posición, profundidad-1, False)
            mejor_valor = max(mejor_valor, valor)
        retornar mejor_valor
    
    sino:  # Turno del oponente
        mejor_valor = +infinito
        para cada movimiento posible:
            valor = minimax(nueva_posición, profundidad-1, True)
            mejor_valor = min(mejor_valor, valor)
        retornar mejor_valor
```

---

## 📊 Función Heurística

La función heurística evalúa qué tan buena es una posición para la IA. Combina **tres factores** principales:

### 1. Diferencia de Puntuación (Peso: 1.0)
```python
score_diff = AI_score - Opponent_score
```
- **Factor más importante**
- Diferencia directa de puntos acumulados
- Refleja quién va ganando

### 2. Movilidad (Peso: 0.5)
```python
mobility_diff = (AI_moves - Opponent_moves) * 0.5
```
- Número de movimientos legales disponibles
- Más movimientos = más opciones estratégicas
- Importante para no quedar bloqueado

### 3. Proximidad a Puntos Valiosos (Peso: 0.3)
```python
proximity_value = sum(points / knight_distance) * 0.3
```
- Distancia a casillas con puntos positivos
- Cuanto más cerca de bonificaciones, mejor
- Usa distancia de movimientos de caballo

### Fórmula Completa

```python
heuristic = score_diff + 0.5 * mobility_diff + 0.3 * proximity_value
```

### Ejemplo de Evaluación

**Posición A:**
- IA: 12 puntos, 5 movimientos, cerca de +10
- Oponente: 8 puntos, 3 movimientos, lejos de bonificaciones

```
score_diff = 12 - 8 = 4
mobility_diff = 5 - 3 = 2
proximity_value ≈ 3 (estimado)

heuristic = 4 + (0.5 × 2) + (0.3 × 3)
          = 4 + 1 + 0.9
          = 5.9  ← Muy buena posición para la IA
```

**Posición B:**
- IA: 5 puntos, 1 movimiento, lejos de bonificaciones
- Oponente: 10 puntos, 6 movimientos, cerca de +5

```
score_diff = 5 - 10 = -5
mobility_diff = 1 - 6 = -5
proximity_value ≈ -2 (estimado)

heuristic = -5 + (0.5 × -5) + (0.3 × -2)
          = -5 - 2.5 - 0.6
          = -8.1  ← Mala posición para la IA
```

### Cálculo de Distancia de Caballo

La distancia entre dos posiciones se aproxima considerando movimientos de caballo:

```python
def _knight_distance(self, pos1: Position, pos2: Position) -> int:
    """Distancia mínima en movimientos de caballo"""
    if pos1 == pos2:
        return 0
    
    dx, dy = abs(x2 - x1), abs(y2 - y1)
    
    # Casos especiales rápidos
    if dx == 1 and dy == 1:
        return 2  # Movimientos en L
    if dx == 2 and dy == 2:
        return 4  # Dos movimientos en L
    
    # Aproximación general
    return max(2, (dx + dy + 1) // 2)
```

---

## 📚 Ejemplos de Uso

### Ejemplo 1: Juego Básico contra IA (Amateur)

```bash
# Ejecutar el juego
python gui.py

# Se abrirá ventana de selección de dificultad
# Seleccionar "Amateur (Profundidad 4)"
# El juego inicia automáticamente
```

**Pantalla inicial:**
```
┌─────────────────────────────────────┐
│ Turno: IA (Blanco)                  │
│ Dificultad: Amateur                 │
│ IA: 0  Jugador: 0                   │
├─────────────────────────────────────┤
│ [  ] [  ] [+5] [  ] [  ] [  ] [  ] │
│ [  ] [♞B] [  ] [-3] [  ] [  ] [+1] │
│ [  ] [  ] [  ] [  ] [+10][  ] [  ] │
│ [-10][  ] [  ] [  ] [  ] [  ] [  ] │
│ [  ] [  ] [+3] [  ] [  ] [-5] [  ] │
│ [  ] [  ] [  ] [+4] [  ] [  ] [  ] │
│ [  ] [-1] [  ] [  ] [  ] [  ] [  ] │
│ [  ] [  ] [  ] [♞N] [  ] [-4] [  ] │
└─────────────────────────────────────┘

La IA piensa su movimiento...
```

### Ejemplo 2: Juego con Semilla Personalizada

```python
# Crear juego con semilla específica (reproducible)
from game import create_random_game, AIPlayer
import tkinter as tk
from gui import GameGUI

# Crear juego con semilla 12345
game = create_random_game(width=8, height=8, seed=12345, player_ids=["P1", "P2"])

# Configurar interfaz
root = tk.Tk()
app = GameGUI(root, game, difficulty="experto")
root.mainloop()
```

### Ejemplo 3: Uso Programático (Sin GUI)

```python
from game import create_random_game

# Crear juego
game = create_random_game(seed=42)

# Juego automático hasta el final
final_scores, reason = game.start(seed=42)

print(f"Razón de finalización: {reason}")
print(f"Puntuaciones finales: {final_scores}")
```

**Salida esperada:**
```
Razón de finalización: no_moves
Puntuaciones finales: {'P1': 18, 'P2': 12}
```

### Ejemplo 4: Iniciar con Argumentos de Línea de Comandos

```bash
# Tablero 6x6 con semilla específica y dificultad experta
python gui.py --size 6 --seed 123 --difficulty experto

# Solo semilla personalizada (8x8 por defecto, selección de dificultad manual)
python gui.py --seed 999

# Tablero grande 10x10
python gui.py --size 10
```

### Ejemplo 5: Análisis de Movimientos de IA

```python
from game import create_random_game, AIPlayer

# Crear juego
game = create_random_game(seed=100)
ai = AIPlayer("P1", depth=4)

# Obtener mejor movimiento
best_move = ai.get_best_move(game)
print(f"IA recomienda: Mover {best_move[0]} a {best_move[1]}")

# Aplicar movimiento
points = game.apply_move(best_move[0], best_move[1])
print(f"Puntos obtenidos: {points}")
print(f"Nueva puntuación: {game.scores}")
```

**Salida:**
```
IA recomienda: Mover H1 a (5, 3)
Puntos obtenidos: 5
Nueva puntuación: {'P1': 5, 'P2': 0}
```

---

## 📁 Estructura del Proyecto

```
ajedrez_IA/
│
├── game.py              # Lógica del juego y IA
│   ├── Horse           # Clase del caballo
│   ├── Board           # Clase del tablero
│   ├── Game            # Clase del juego principal
│   └── AIPlayer        # Clase de la IA (Minimax)
│
├── gui.py              # Interfaz gráfica
│   ├── GameGUI         # Clase principal de la GUI
│   ├── select_difficulty()  # Selector de dificultad
│   └── main()          # Función principal
│
├── README.md           # Este archivo
├── .gitignore          # Archivos ignorados por Git
└── __pycache__/        # Archivos compilados de Python
```

### Descripción de Archivos

#### `game.py` (462 líneas)
Contiene toda la lógica del juego:
- Movimientos de caballos
- Gestión del tablero
- Sistema de puntuación
- Algoritmo Minimax
- Función heurística
- Condiciones de victoria

#### `gui.py` (≈250 líneas)
Interfaz gráfica con Tkinter:
- Renderizado del tablero
- Manejo de clics del usuario
- Visualización de puntuaciones
- Selector de dificultad
- Ejecución de IA en hilos

---

## 🎓 Conceptos de IA Implementados

### 1. **Búsqueda Adversarial**
- Modelado del juego como árbol de decisiones
- Consideración de movimientos del oponente

### 2. **Poda de Búsqueda**
- Alfa-beta para optimizar exploración
- Reducción exponencial de nodos visitados

### 3. **Evaluación Heurística**
- Función multi-criterio (score, mobilidad, proximidad)
- Pesos balanceados empíricamente

### 4. **Profundidad Limitada**
- Búsqueda iterativa con límite de profundidad
- Trade-off entre tiempo y calidad

### 5. **Simulación de Partidas**
- Copia profunda del estado del juego
- Reversibilidad de movimientos

---

## 🎯 Estrategias Ganadoras

### Consejos para Vencer a la IA

1. **Principio del juego:**
   - Busca las casillas con **+10** y **+5** primero
   - Evita las casillas negativas al inicio
   - Mantén movilidad (no te dejes encerrar)

2. **Medio juego:**
   - Bloquea el acceso de la IA a puntos positivos
   - Calcula 2-3 movimientos adelante
   - Observa cuántos movimientos te quedan

3. **Final del juego:**
   - Si vas perdiendo, arriesga por puntos altos
   - Si vas ganando, prioriza mantener movilidad
   - Recuerda la penalización de -4 por no tener movimientos

4. **Contra Experto:**
   - La IA evalúa 6 movimientos adelante
   - Requiere pensamiento estratégico profundo
   - Usa casillas negativas para engañarla (forzar malas posiciones)

---

## 🐛 Solución de Problemas

### El juego no inicia
```bash
# Verificar versión de Python
python --version

# Debe ser 3.8+, si no:
python3 gui.py
```

### Error: "No module named 'tkinter'"
```bash
# En Ubuntu/Debian:
sudo apt-get install python3-tk

# En macOS (con Homebrew):
brew install python-tk

# En Windows: Tkinter viene preinstalado
```

### La IA tarda mucho (Experto)
- Es normal, está evaluando millones de posiciones
- Reduce a "Amateur" para más rapidez
- En tableros grandes, usa "Principiante"

### El juego se congela
- La IA se ejecuta en un hilo separado
- Espera unos segundos (especialmente en Experto)
- Si persiste, reinicia con `Ctrl+C` y usa menor dificultad

---

## 🤝 Contribuir

¿Quieres mejorar el proyecto? ¡Las contribuciones son bienvenidas!

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

### Ideas para Contribuir
- [ ] Modo jugador vs jugador
- [ ] Guardar/cargar partidas
- [ ] Historial de movimientos
- [ ] Replay de partidas
- [ ] Más niveles de dificultad
- [ ] Tableros temáticos
- [ ] Sonidos y animaciones
- [ ] Estadísticas de victorias

---

## 📄 Licencia

Este proyecto fue desarrollado como proyecto académico.

---

## 👥 Autores

- **Juan Sebastian Rodas Ramirez** - Desarrollo principal

---

## 🙏 Agradecimientos

- Algoritmo Minimax: Russell & Norvig - "Artificial Intelligence: A Modern Approach"
- Inspiración: Juegos clásicos de estrategia y ajedrez
- Python Software Foundation por Tkinter

---

## 📞 Contacto

¿Preguntas o sugerencias?
- GitHub: [@JuanSebastianRodasRamirez](https://github.com/JuanSebastianRodasRamirez)
- Repository: [ajedrez_IA](https://github.com/JuanSebastianRodasRamirez/ajedrez_IA)

---

**¡Disfruta jugando Smart Horses! 🐴♟️**