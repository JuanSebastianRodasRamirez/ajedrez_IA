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

        root.title('Smart Horses - Jugador vs IA')

        ctrl = tk.Frame(root)
        ctrl.pack(side=tk.TOP, fill=tk.X, padx=4, pady=4)
        self.info_label = tk.Label(ctrl, text='')
        self.info_label.pack(side=tk.LEFT)
        new_btn = tk.Button(ctrl, text='Nuevo Juego', command=self.new_game)
        new_btn.pack(side=tk.RIGHT)

        # board UI
        self.board_frame = tk.Frame(root)
        self.board_frame.pack(padx=4, pady=4)

    # no image for horses; show horse id text on the buttons

        self.cell_buttons = {}
        self._build_board_ui()
        self.refresh()

    def _build_board_ui(self):
        # create buttons for current board size
        for y in range(self.board.height):
            for x in range(self.board.width):
                btn = tk.Button(self.board_frame, width=6, height=3,
                                command=lambda p=(x, y): self.on_cell_click(p))
                btn.grid(row=y, column=x, padx=1, pady=1)
                self.cell_buttons[(x, y)] = btn

    def refresh(self):
        occ = self.game.occupied_positions()
        # compute legal destinations for selected horse
        moves_set = set()
        if self.selected_horse_id is not None:
            moves = self.game.generate_moves_for_player(self.game.turn)
            moves_set = {dst for hid, dst in moves if hid == self.selected_horse_id}

        for pos, btn in self.cell_buttons.items():
            bg = 'white'
            text = ''
            blocked = self.board.is_blocked(pos)
            # highlight move destinations first (even if they have points)
            if pos in moves_set:
                bg = 'orange'
                # if there are points, show them but keep highlight
                if pos in self.board.points:
                    text = str(self.board.points[pos])
                else:
                    text = ''
                btn.config(text=text, bg=bg)
                continue
            if pos in occ:
                hid = occ[pos]
                h = self.game.horses[hid]
                # show horse id as text
                if h.owner == 'P1':  # IA (Blanco)
                    bg = 'lightgray'
                    text = f"♞{hid}"  # Caballo blanco
                else:  # Jugador humano (Negro)
                    bg = 'darkgray'
                    text = f"♞{hid}"  # Caballo negro
                
                if self.selected_horse_id == hid:
                    bg = 'yellow'
                elif blocked:
                    bg = 'gray'
            elif pos in self.board.points:
                val = self.board.points[pos]
                text = str(val)
                bg = "#87e694" if val > 0 else "#e25757"
                if blocked:
                    bg = 'gray'
            elif pos in moves_set:
                bg = 'orange'
            else:
                bg = 'white'
                if blocked:
                    bg = 'gray'

            btn.config(text=text, bg=bg)

        # update info label
        turn_text = "IA (Blanco)" if self.game.turn == "P1" else "Jugador (Negro)"
        difficulty_text = f"Dificultad: {self.difficulty.capitalize()}"
        scores_text = f"IA: {self.game.scores.get('P1', 0)}  Jugador: {self.game.scores.get('P2', 0)}"
        self.info_label.config(text=f"Turno: {turn_text}  |  {difficulty_text}  |  {scores_text}")
        
        # Si es turno de la IA y no está pensando, hacer movimiento
        if self.game.turn == "P1" and not self.ai_thinking and not self.is_game_over()[0]:
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
            if winner == "P1":
                winner_text = "IA (Blanco)"
            elif winner == "P2":
                winner_text = "Jugador (Negro)"
            else:
                winner_text = "Empate"
            
            scores = f"\nPuntuación final:\nIA: {self.game.scores.get('P1', 0)}\nJugador: {self.game.scores.get('P2', 0)}"
            
            if winner:
                messagebox.showinfo('Juego Terminado', f'Ganador: {winner_text}\nRazón: {reason}{scores}')
            else:
                messagebox.showinfo('Juego Terminado', f'Empate\nRazón: {reason}{scores}')
    
    def is_game_over(self):
        """Wrapper para acceder al método is_game_over del juego."""
        return self.game.is_game_over()
    
    def new_game(self):
        seed = int(time.time()) % 100000
        # reinitialize
        self.game.initialize(width=self.board.width, height=self.board.height, seed=seed)
        self.board = self.game.board
        # rebuild UI if size changed
        for b in self.cell_buttons.values():
            b.destroy()
        self.cell_buttons.clear()
        self._build_board_ui()
        self.selected_horse_id = None
        self.ai_thinking = False
        self.refresh()


def select_difficulty():
    """Ventana para seleccionar la dificultad."""
    difficulty = {"value": "amateur"}  # Valor por defecto
    
    def on_select(selected):
        difficulty["value"] = selected
        dialog.destroy()
    
    dialog = tk.Toplevel()
    dialog.title("Seleccionar Dificultad")
    dialog.geometry("300x200")
    dialog.resizable(False, False)
    dialog.grab_set()  # Modal
    
    # Centrar la ventana
    dialog.transient()
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (300 // 2)
    y = (dialog.winfo_screenheight() // 2) - (200 // 2)
    dialog.geometry(f"300x200+{x}+{y}")
    
    tk.Label(dialog, text="Selecciona el nivel de dificultad:", font=("Arial", 12)).pack(pady=20)
    
    tk.Button(dialog, text="Principiante (Profundidad 2)", width=25, 
              command=lambda: on_select("principiante")).pack(pady=5)
    tk.Button(dialog, text="Amateur (Profundidad 4)", width=25, 
              command=lambda: on_select("amateur")).pack(pady=5)
    tk.Button(dialog, text="Experto (Profundidad 6)", width=25, 
              command=lambda: on_select("experto")).pack(pady=5)
    
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
    
    # Crear ventana raíz temporalmente oculta para el diálogo
    temp_root = tk.Tk()
    temp_root.withdraw()
    
    # Seleccionar dificultad si no se proporcionó
    difficulty = args.difficulty if args.difficulty else select_difficulty()
    
    temp_root.destroy()
    
    # Crear el juego
    g = create_random_game(width=args.size, height=args.size, seed=args.seed, player_ids=["P1", "P2"])
    
    # Crear ventana principal
    root = tk.Tk()
    app = GameGUI(root, g, difficulty)
    root.mainloop()


if __name__ == '__main__':
    main()
