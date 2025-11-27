import tkinter as tk
from tkinter import messagebox
import time
from typing import Optional

from game import create_random_game, Game, Board


class GameGUI:
    def __init__(self, root: tk.Tk, game: Game):
        self.root = root
        self.game = game
        self.board: Board = game.board
        self.selected_horse_id: Optional[str] = None

        root.title('Smart Horses')

        ctrl = tk.Frame(root)
        ctrl.pack(side=tk.TOP, fill=tk.X, padx=4, pady=4)
        self.info_label = tk.Label(ctrl, text='')
        self.info_label.pack(side=tk.LEFT)
        new_btn = tk.Button(ctrl, text='New Random Game', command=self.new_game)
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
                text = hid
                # coloring by owner
                if h.owner == 'P1':
                    bg = 'lightblue'
                else:
                    bg = 'lightgreen'
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
        self.info_label.config(text=f"Turn: {self.game.turn}    Scores: {self.game.scores}")

    def on_cell_click(self, pos):
        occ = self.game.occupied_positions()
        # select own horse
        if self.selected_horse_id is None:
            if pos in occ:
                hid = occ[pos]
                if self.game.horses[hid].owner == self.game.turn:
                    self.selected_horse_id = hid
                    self.refresh()
                else:
                    # silently ignore selecting opponent horse
                    return
            else:
                # silent ignore
                return
            return

        # have a selection, try move
        hid = self.selected_horse_id
        # check legal
        legal = {dst for _hid, dst in self.game.generate_moves_for_player(self.game.turn) if _hid == hid}
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
        over, reason, winner = self.game.is_game_over()
        if over:
            if winner:
                messagebox.showinfo('Game over', f'Winner: {winner} (reason: {reason})')
            else:
                messagebox.showinfo('Game over', f'Draw or no winner (reason: {reason})')

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
        self.refresh()


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', type=int, help='seed for random init')
    parser.add_argument('--size', type=int, default=8, help='board size')
    args = parser.parse_args()

    g = create_random_game(width=args.size, height=args.size, seed=args.seed)
    root = tk.Tk()
    app = GameGUI(root, g)
    root.mainloop()


if __name__ == '__main__':
    main()
