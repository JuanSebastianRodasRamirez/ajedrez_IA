import tkinter as tk
from tkinter import messagebox, ttk
import time
from typing import Optional
import threading

from game import create_random_game, Game, Board, AIPlayer


class GameGUI:
    def __init__(self, root: tk.Tk, game: Game, difficulty: str = "amateur"):
        self.root = root
        self.game = game
        self.board: Board = game.board
        self.selected_horse_id: Optional[str] = None
        self.difficulty = difficulty
        self.ai_thinking = False
        
        # Configurar IA según dificultad
        depth_map = {"principiante": 2, "amateur": 4, "experto": 6}
        self.ai_player = AIPlayer("P1", depth_map.get(difficulty, 4))  # IA siempre es P1 (blanco)

        # Configurar ventana principal con estilo de ajedrez
        root.title('♞ Smart Horses - Jugador vs IA ♞')
        root.configure(bg='#2C1810')  # Fondo marrón oscuro tipo madera
        
        # Panel de control superior con estilo elegante
        ctrl = tk.Frame(root, bg='#8B4513', relief=tk.RAISED, bd=3)
        ctrl.pack(side=tk.TOP, fill=tk.X, padx=8, pady=8)
        
        self.info_label = tk.Label(ctrl, text='', bg='#D2B48C', fg='#2C1810', 
                                   font=('Georgia', 10, 'bold'), relief=tk.SUNKEN, bd=2, padx=10, pady=5)
        self.info_label.pack(side=tk.LEFT, padx=5)
        
        new_btn = tk.Button(ctrl, text='⟳ Nuevo Juego', command=self.new_game,
                           bg='#D4AF37', fg='#2C1810', font=('Georgia', 10, 'bold'),
                           relief=tk.RAISED, bd=3, padx=15, pady=5,
                           activebackground='#FFD700', cursor='hand2')
        new_btn.pack(side=tk.RIGHT, padx=5)

        # Tablero con marco de madera
        board_container = tk.Frame(root, bg='#8B4513', relief=tk.RAISED, bd=8)
        board_container.pack(padx=10, pady=10)
        
        self.board_frame = tk.Frame(board_container, bg='#4A2511', relief=tk.SUNKEN, bd=4)
        self.board_frame.pack(padx=4, pady=4)

    # no image for horses; show horse id text on the buttons

        self.cell_buttons = {}
        self._build_board_ui()
        self.refresh()

    def _build_board_ui(self):
        # Crear botones para el tablero con estilo de ajedrez
        for y in range(self.board.height):
            for x in range(self.board.width):
                # Determinar color de casilla base (patrón de ajedrez)
                is_light = (x + y) % 2 == 0
                
                btn = tk.Button(self.board_frame, width=8, height=4,
                                command=lambda p=(x, y): self.on_cell_click(p),
                                relief=tk.RAISED, bd=2,
                                font=('Arial', 11, 'bold'),
                                cursor='hand2')
                btn.grid(row=y, column=x, padx=0, pady=0)
                self.cell_buttons[(x, y)] = btn

    def refresh(self):
        occ = self.game.occupied_positions()
        # compute legal destinations for selected horse
        moves_set = set()
        if self.selected_horse_id is not None:
            moves = self.game.generate_moves_for_player(self.game.turn)
            moves_set = {dst for hid, dst in moves if hid == self.selected_horse_id}

        for pos, btn in self.cell_buttons.items():
            # Determinar color base de la casilla (patrón de ajedrez)
            x, y = pos
            is_light = (x + y) % 2 == 0
            base_light = '#F0D9B5'  # Beige claro
            base_dark = '#B58863'   # Marrón
            
            bg = base_light if is_light else base_dark
            text = ''
            fg = '#2C1810'  # Color de texto oscuro
            
            blocked = self.board.is_blocked(pos)
            
            # highlight move destinations first (even if they have points)
            if pos in moves_set:
                bg = '#FFD700'  # Dorado para movimientos válidos
                # if there are points, show them but keep highlight
                if pos in self.board.points:
                    text = str(self.board.points[pos])
                else:
                    text = ''
                btn.config(text=text, bg=bg, fg='#2C1810', font=('Arial', 11, 'bold'))
                continue
            if pos in occ:
                hid = occ[pos]
                h = self.game.horses[hid]
                # Mantener color base de ajedrez cuando hay caballo
                if h.owner == 'P1':  # IA (Blanco)
                    text = f"♞"  # Caballo blanco
                    fg = '#FFFFFF'  # Blanco
                else:  # Jugador humano (Negro)
                    text = f"♞"  # Caballo negro
                    fg = '#000000'  # Negro
                
                if self.selected_horse_id == hid:
                    bg = '#90EE90'  # Verde claro para selección
                    fg = '#2C1810'
                elif blocked:
                    bg = '#3D3D3D'  # Negro para casillas bloqueadas
                # Si no está seleccionado ni bloqueado, mantiene bg del patrón de ajedrez
            elif pos in self.board.points:
                val = self.board.points[pos]
                text = str(val)
                # Tonos verdes para positivos, rojos para negativos, sobre base de ajedrez
                if val > 0:
                    bg = '#90EE90' if is_light else '#7FD67F'  # Verde
                else:
                    bg = '#FFB6B6' if is_light else '#FF9999'  # Rojo
                if blocked:
                    bg = '#3D3D3D'  # Negro para casillas bloqueadas
            elif pos in moves_set:
                bg = '#FFD700'  # Dorado
            else:
                bg = base_light if is_light else base_dark
                if blocked:
                    bg = '#3D3D3D'  # Negro para casillas bloqueadas

            btn.config(text=text, bg=bg, fg=fg, font=('Arial', 11, 'bold'))

        # update info label
        turn_text = "IA (Blanco)" if self.game.turn == "P1" else "Jugador (Negro)"
        difficulty_text = f"Dificultad: {self.difficulty.capitalize()}"
        scores_text = f"Puntos - IA: {self.game.scores.get('P1', 0)} | Jugador: {self.game.scores.get('P2', 0)}"
        self.info_label.config(text=f"Turno: {turn_text}  |  {difficulty_text}  |  {scores_text}")
        
        # Verificar si el juego terminó antes de procesar turnos
        if self.is_game_over()[0]:
            return
            
        # Verificar si el jugador actual tiene movimientos disponibles
        current_moves = self.game.generate_moves_for_player(self.game.turn)
        if not current_moves:
            # El jugador actual no tiene movimientos - aplicar penalización y cambiar turno
            self.game.scores[self.game.turn] = self.game.scores.get(self.game.turn, 0) - 4
            self.game._switch_turn()
            # Actualizar la visualización después del cambio de turno
            self.root.after(100, self.refresh)
            return
        
        # Si es turno de la IA y no está pensando, hacer movimiento
        if self.game.turn == "P1" and not self.ai_thinking:
            self.make_ai_move()

    def on_cell_click(self, pos):
        # Solo permitir interacción si es turno del jugador humano (P2) y la IA no está pensando
        if self.game.turn != "P2" or self.ai_thinking:
            return
        
        occ = self.game.occupied_positions()
        # select own horse
        if self.selected_horse_id is None:
            if pos in occ:
                hid = occ[pos]
                if self.game.horses[hid].owner == "P2":  # Solo caballo del jugador humano
                    self.selected_horse_id = hid
                    self.refresh()
                else:
                    return
            else:
                return
            return

        # have a selection, try move
        hid = self.selected_horse_id
        # check legal
        legal = {dst for _hid, dst in self.game.generate_moves_for_player("P2") if _hid == hid}
        if pos not in legal:
            # deselect silently
            self.selected_horse_id = None
            self.refresh()
            return
        # apply move
        try:
            pts = self.game.apply_move(hid, pos)
        except Exception:
            # invalid move, deselect silently
            self.selected_horse_id = None
            self.refresh()
            return
        # deselect
        self.selected_horse_id = None
        self.refresh()
        self.check_game_over()

    def make_ai_move(self):
        """Hace que la IA realice su movimiento en un hilo separado."""
        def ai_move_thread():
            self.ai_thinking = True
            self.root.after(0, lambda: self.info_label.config(text="IA está pensando..."))
            
            # Pequeña pausa para mostrar que la IA está pensando
            time.sleep(0.5)
            
            best_move = self.ai_player.get_best_move(self.game)
            
            if best_move:
                try:
                    self.game.apply_move(best_move[0], best_move[1])
                except Exception:
                    pass
            
            self.ai_thinking = False
            self.root.after(0, self.refresh)
            self.root.after(0, self.check_game_over)
        
        thread = threading.Thread(target=ai_move_thread)
        thread.daemon = True
        thread.start()
    
    def check_game_over(self):
        """Verifica si el juego ha terminado y muestra el resultado."""
        over, reason, winner = self.game.is_game_over()
        if over:
            # Asegurar que se muestren las puntuaciones actualizadas
            final_scores = dict(self.game.scores)  # Hacer una copia de los scores actuales
            
            if winner == "P1":
                winner_text = "¡La IA (Caballo Blanco) ha ganado!"
            elif winner == "P2":
                winner_text = "¡Has ganado! (Caballo Negro)"
            else:
                winner_text = "¡Empate!"
            
            scores_p1 = final_scores.get('P1', 0)
            scores_p2 = final_scores.get('P2', 0)
            
            # Mostrar diálogo personalizado con estilo de ajedrez
            show_game_over_dialog(self.root, winner_text, scores_p1, scores_p2, self.new_game)
    
    def is_game_over(self):
        """Wrapper para acceder al método is_game_over del juego."""
        return self.game.is_game_over()
    
    def new_game(self):
        # Mostrar selector de dificultad
        new_difficulty = select_difficulty(self.root)
        
        # Si el usuario canceló (cerró la ventana), no hacer nada
        if new_difficulty is None:
            return
        
        # Actualizar dificultad y IA
        self.difficulty = new_difficulty
        depth_map = {"principiante": 2, "amateur": 4, "experto": 6}
        self.ai_player = AIPlayer("P1", depth_map.get(new_difficulty, 4))
        
        # Reinicializar juego
        seed = int(time.time()) % 100000
        self.game.initialize(width=self.board.width, height=self.board.height, seed=seed)
        self.board = self.game.board
        
        # Reconstruir UI si cambió el tamaño
        for b in self.cell_buttons.values():
            b.destroy()
        self.cell_buttons.clear()
        self._build_board_ui()
        self.selected_horse_id = None
        self.ai_thinking = False
        self.refresh()


def show_game_over_dialog(parent, winner_text, score_p1, score_p2, new_game_callback):
    """Muestra un diálogo personalizado de fin de juego con estilo de ajedrez."""
    dialog = tk.Toplevel(parent)
    dialog.title("♔ Fin del Juego")
    dialog.geometry("420x300")
    dialog.resizable(False, False)
    dialog.grab_set()  # Modal
    
    # Estilo de ajedrez
    dialog.configure(bg='#2C1810')  # Fondo marrón oscuro
    
    # Prevenir cierre con X
    dialog.protocol("WM_DELETE_WINDOW", lambda: None)
    
    # Centrar la ventana
    dialog.transient(parent)
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (420 // 2)
    y = (dialog.winfo_screenheight() // 2) - (300 // 2)
    dialog.geometry(f"420x300+{x}+{y}")
    
    # Título del ganador
    title_frame = tk.Frame(dialog, bg='#8B4513', relief=tk.RAISED, bd=3)
    title_frame.pack(pady=15, padx=20, fill=tk.X)
    
    tk.Label(title_frame, text=winner_text, 
            font=("Georgia", 14, "bold"),
            bg='#8B4513', fg='#FFD700',
            pady=10).pack()
    
    # Puntuaciones
    scores_frame = tk.Frame(dialog, bg='#2C1810')
    scores_frame.pack(pady=15)
    
    tk.Label(scores_frame, text="Puntuación Final", 
            font=("Georgia", 12, "bold"),
            bg='#2C1810', fg='#D2B48C').pack()
    
    tk.Label(scores_frame, text="═" * 30, 
            font=("Arial", 10),
            bg='#2C1810', fg='#B58863').pack()
    
    tk.Label(scores_frame, text=f"IA (Blanco): {score_p1} puntos", 
            font=("Georgia", 11),
            bg='#2C1810', fg='#D2B48C').pack(pady=3)
    
    tk.Label(scores_frame, text=f"Jugador (Negro): {score_p2} puntos", 
            font=("Georgia", 11),
            bg='#2C1810', fg='#D2B48C').pack(pady=3)
    
    # Botones
    buttons_frame = tk.Frame(dialog, bg='#2C1810')
    buttons_frame.pack(pady=20)
    
    def on_view_game():
        dialog.destroy()
    
    def on_new_game():
        dialog.destroy()
        new_game_callback()
    
    tk.Button(buttons_frame, text="👁️  Ver Partida", 
              width=18,
              font=("Georgia", 10, "bold"),
              bg='#B58863', fg='#FFFFFF',
              activebackground='#8B4513',
              relief=tk.RAISED, bd=3,
              cursor='hand2',
              command=on_view_game).pack(side=tk.LEFT, padx=10)
    
    tk.Button(buttons_frame, text="⟳  Jugar de Nuevo", 
              width=18,
              font=("Georgia", 10, "bold"),
              bg='#D4AF37', fg='#2C1810',
              activebackground='#FFD700',
              relief=tk.RAISED, bd=3,
              cursor='hand2',
              command=on_new_game).pack(side=tk.LEFT, padx=10)
    
    dialog.wait_window()


def select_difficulty(parent=None):
    """Ventana para seleccionar la dificultad."""
    difficulty = {"value": None}  # None indica que se canceló
    
    def on_select(selected):
        difficulty["value"] = selected
        dialog.destroy()
    
    def on_close():
        # Si es la primera vez (inicio del programa), cerrar todo
        dialog.destroy()
        if parent is None:
            import sys
            sys.exit(0)
    
    dialog = tk.Toplevel(parent) if parent else tk.Tk()
    dialog.title("♞ Seleccionar Dificultad")
    dialog.geometry("350x250")
    dialog.resizable(False, False)
    if parent:
        dialog.grab_set()  # Modal solo si hay ventana padre
    
    # Estilo de ajedrez para el diálogo
    dialog.configure(bg='#2C1810')  # Fondo marrón oscuro
    
    # Manejar el cierre de la ventana
    dialog.protocol("WM_DELETE_WINDOW", on_close)
    
    # Centrar la ventana
    dialog.transient()
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (350 // 2)
    y = (dialog.winfo_screenheight() // 2) - (250 // 2)
    dialog.geometry(f"350x250+{x}+{y}")
    
    # Título con estilo
    title_label = tk.Label(dialog, text="Selecciona el nivel de dificultad:", 
                          font=("Georgia", 12, "bold"), 
                          bg='#2C1810', fg='#D2B48C')
    title_label.pack(pady=20)
    
    # Botones con estilo de ajedrez
    tk.Button(dialog, text="Principiante (Profundidad 2)", 
              width=28, 
              font=("Georgia", 10),
              bg='#F0D9B5', fg='#2C1810',
              activebackground='#D4AF37',
              relief=tk.RAISED, bd=3,
              cursor='hand2',
              command=lambda: on_select("principiante")).pack(pady=8)
    
    tk.Button(dialog, text="Amateur (Profundidad 4)", 
              width=28,
              font=("Georgia", 10),
              bg='#B58863', fg='#FFFFFF',
              activebackground='#D4AF37',
              relief=tk.RAISED, bd=3,
              cursor='hand2',
              command=lambda: on_select("amateur")).pack(pady=8)
    
    tk.Button(dialog, text="Experto (Profundidad 6)", 
              width=28,
              font=("Georgia", 10),
              bg='#8B4513', fg='#FFFFFF',
              activebackground='#D4AF37',
              relief=tk.RAISED, bd=3,
              cursor='hand2',
              command=lambda: on_select("experto")).pack(pady=8)
    
    dialog.wait_window()
    return difficulty["value"]

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', type=int, help='seed for random init')
    parser.add_argument('--size', type=int, default=8, help='board size')
    parser.add_argument('--difficulty', type=str, choices=["principiante", "amateur", "experto"], 
                       help='AI difficulty level')
    args = parser.parse_args()
    
    # Seleccionar dificultad si no se proporcionó
    if args.difficulty:
        difficulty = args.difficulty
    else:
        difficulty_dialog = select_difficulty(parent=None)
        if difficulty_dialog is None:
            # Usuario cerró el diálogo, salir del programa
            import sys
            sys.exit(0)
        difficulty = difficulty_dialog
    
    # Crear el juego
    g = create_random_game(width=args.size, height=args.size, seed=args.seed, player_ids=["P1", "P2"])
    
    # Crear ventana principal
    root = tk.Tk()
    app = GameGUI(root, g, difficulty)
    root.mainloop()


if __name__ == '__main__':
    main()
