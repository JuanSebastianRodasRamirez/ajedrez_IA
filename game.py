from typing import List, Tuple, Dict, Optional, Set
import random

Position = Tuple[int, int]

KNIGHT_DELTAS = [
    (2, 1), (2, -1), (-2, 1), (-2, -1),
    (1, 2), (1, -2), (-1, 2), (-1, -2),
]


class Horse:
    """Represents a horse piece. Has an id, owner and current position.

    The horse exposes a method `move_and_collect` that moves the horse to a
    destination on a given board, collects any points on that cell, destroys
    the points on the board and marks the cell blocked (unavailable forever).
    """

    def __init__(self, horse_id: str, owner: str, pos: Position):
        self.id = horse_id
        self.owner = owner
        self.pos = pos

    def __repr__(self) -> str:
        return f"Horse(id={self.id!r}, owner={self.owner!r}, pos={self.pos!r})"

    def possible_moves(self, board: 'Board', occupied: Set[Position]) -> List[Position]:
        """Return a list of positions this horse can legally move to.

        Rules applied here:
        - must be in bounds
        - cannot land on an occupied cell (no captures)
        - cannot land on a blocked cell
        """
        moves: List[Position] = []
        x0, y0 = self.pos
        for dx, dy in KNIGHT_DELTAS:
            to = (x0 + dx, y0 + dy)
            if not board.in_bounds(to):
                continue
            if to in occupied:
                continue
            if board.is_blocked(to):
                continue
            moves.append(to)
        return moves

    def move_and_collect(self, to: Position, board: 'Board') -> int:
        """Move this horse to `to` on `board`, collect points and mark the cell blocked.

        Returns the number of points collected (can be negative).
        Raises ValueError if the destination is invalid (out of bounds or blocked).
        Note: callers are expected to ensure the destination is not occupied.
        """
        if not board.in_bounds(to):
            raise ValueError("Destination out of bounds")
        if board.is_blocked(to):
            raise ValueError("Destination is blocked")
        pts = board.get_points(to)
        # collect and destroy
        board.destroy_points(to)
        # permanently block the cell so it can't be used again
        board.block_position(to)
        # perform move
        self.pos = to
        return pts


class Board:
    """Represents the game board.

    The board stores point values per cell and a set of permanently blocked
    positions. It offers helper methods to query and mutate cell state.
    """

    def __init__(self, width: int, height: int, points: Optional[Dict[Position, int]] = None):
        self.width = width
        self.height = height
        # points map: position -> value
        self.points: Dict[Position, int] = points.copy() if points else {}
        # permanently blocked positions (after a horse visits)
        self.blocked: Set[Position] = set()

    def in_bounds(self, pos: Position) -> bool:
        x, y = pos
        return 0 <= x < self.width and 0 <= y < self.height

    def get_points(self, pos: Position) -> int:
        return self.points.get(pos, 0)

    def destroy_points(self, pos: Position) -> None:
        if pos in self.points:
            del self.points[pos]

    def block_position(self, pos: Position) -> None:
        self.blocked.add(pos)

    def is_blocked(self, pos: Position) -> bool:
        return pos in self.blocked

    def remaining_points_total(self) -> int:
        return sum(self.points.values())

    def set_cell_state(self, pos: Position, value: Optional[int]) -> None:
        """Set the state of a cell.

        If value is None the cell has no points. If value is int the cell gets that
        point value. This is useful to change or populate cells.
        """
        if not self.in_bounds(pos):
            raise ValueError("Position out of bounds")
        if value is None:
            if pos in self.points:
                del self.points[pos]
        else:
            self.points[pos] = value


class Game:
    """Encapsulates the game: board, horses, turn and scores.

    Responsibilities:
    - initialize the board and horses (randomly placing the 10 point cells and the horses)
    - generate and apply moves
    - check end condition
    - run a simple play loop (start)
    """

    POINT_VALUES = [-10, -5, -4, -3, -1, 1, 3, 4, 5, 10]

    def __init__(self):
        self.board: Optional[Board] = None
        self.horses: Dict[str, Horse] = {}
        self.turn: Optional[str] = None
        self.scores: Dict[str, int] = {}

    def initialize(self, width: int = 8, height: int = 8, player_ids: Optional[List[str]] = None, seed: Optional[int] = None) -> None:
        """Initialize a new game: create an 8x8 board (by default), place 10 point cells and two horses.

        Horses are placed on random cells that do not contain the point cells. Seed can be provided for reproducibility.
        """
        if player_ids is None:
            player_ids = ["P1", "P2"]
        rnd = random.Random(seed)
        # generate point cells
        points = create_random_point_cells(width, height, Game.POINT_VALUES, seed)
        board = Board(width, height, points)
        # choose free cells for horses
        all_cells = [(x, y) for y in range(height) for x in range(width)]
        free_cells = [c for c in all_cells if c not in points]
        if len(free_cells) < len(player_ids):
            raise ValueError("Not enough free cells to place horses")
        chosen = rnd.sample(free_cells, len(player_ids))
        horses: Dict[str, Horse] = {}
        for i, pid in enumerate(player_ids):
            hid = f"H{i+1}"
            horses[hid] = Horse(hid, pid, chosen[i])
        # set state
        self.board = board
        self.horses = horses
        self.turn = player_ids[0]
        self.scores = {pid: 0 for pid in player_ids}

    def occupied_positions(self) -> Dict[Position, str]:
        return {h.pos: hid for hid, h in self.horses.items()}

    def generate_moves_for_player(self, player: str) -> List[Tuple[str, Position]]:
        """Return a list of (horse_id, destination) legal moves for `player`."""
        occ = set(self.occupied_positions().keys())
        moves: List[Tuple[str, Position]] = []
        for hid, h in self.horses.items():
            if h.owner != player:
                continue
            for to in h.possible_moves(self.board, occ):
                moves.append((hid, to))
        return moves

    def apply_move(self, horse_id: str, to: Position) -> int:
        """Apply a move for horse `horse_id` to position `to`.

        Returns collected points. Raises ValueError for invalid moves.
        """
        if horse_id not in self.horses:
            raise ValueError("Invalid horse id")
        horse = self.horses[horse_id]
        occ = set(self.occupied_positions().keys())
        if to in occ:
            raise ValueError("Destination occupied")
        if self.board.is_blocked(to):
            raise ValueError("Destination blocked")
        # perform move via horse
        pts = horse.move_and_collect(to, self.board)
        # add to score
        self.scores[horse.owner] = self.scores.get(horse.owner, 0) + pts
        # switch turn
        self._switch_turn()
        return pts

    def _switch_turn(self) -> None:
        players = sorted(list({h.owner for h in self.horses.values()}))
        if not players:
            self.turn = None
            return
        if self.turn not in players:
            self.turn = players[0]
            return
        if len(players) == 1:
            self.turn = players[0]
            return
        next_idx = (players.index(self.turn) + 1) % len(players)
        self.turn = players[next_idx]

    def is_game_over(self) -> Tuple[bool, str, Optional[str]]:
        """Return (over, reason, winner)

        End conditions implemented:
        - if only one player remains (winner)
        - if no point cells remain (winner by score or draw)
        - if none of the players has any legal move (winner by score or draw)
        """
        players = sorted(list({h.owner for h in self.horses.values()}))
        if len(players) == 0:
            return True, "no_horses_left", None
        if len(players) == 1:
            return True, "one_player_remaining", players[0]
        if self.board.remaining_points_total() == 0:
            p_sorted = sorted(self.scores.items(), key=lambda kv: kv[1], reverse=True)
            if len(p_sorted) >= 2 and p_sorted[0][1] == p_sorted[1][1]:
                return True, "no_points_left_draw", None
            return True, "no_points_left", p_sorted[0][0]
        player_moves = {p: len(self.generate_moves_for_player(p)) for p in players}
        if all(v == 0 for v in player_moves.values()):
            p_sorted = sorted(self.scores.items(), key=lambda kv: kv[1], reverse=True)
            if len(p_sorted) >= 2 and p_sorted[0][1] == p_sorted[1][1]:
                return True, "no_moves_draw", None
            return True, "no_moves", p_sorted[0][0]
        return False, "ongoing", None

    def start(self, seed: Optional[int] = None, max_steps: int = 1000) -> Tuple[Dict[str, int], str]:
        """Start a simple automatic play loop until the game ends or max_steps reached.

        At each turn the current player's first available move is played (deterministic
        order but random seed can be provided if desired to shuffle move ordering).

        Returns final scores and reason for game end.
        """
        if self.board is None:
            raise RuntimeError("Game not initialized")
        rnd = random.Random(seed)
        steps = 0
        while steps < max_steps:
            over, reason, winner = self.is_game_over()
            if over:
                return self.scores, reason
            cur = self.turn
            moves = self.generate_moves_for_player(cur)
            if not moves:
                # no moves for current player -> switch turn
                self._switch_turn()
                steps += 1
                continue
            # pick a move; for some variation shuffle available moves
            rnd.shuffle(moves)
            hid, to = moves[0]
            try:
                pts = self.apply_move(hid, to)
            except ValueError:
                # if move invalid for any reason, skip it and continue
                steps += 1
                continue
            steps += 1
        # reached max steps
        return self.scores, "max_steps_reached"


# Helper functions kept for convenience
def create_random_point_cells(width: int, height: int, values: List[int], seed: Optional[int] = None) -> Dict[Position, int]:
    cells: List[Position] = [(x, y) for y in range(height) for x in range(width)]
    if len(cells) < len(values):
        raise ValueError("Board too small to place required point cells")
    rnd = random.Random(seed)
    chosen = rnd.sample(cells, len(values))
    return {pos: val for pos, val in zip(chosen, values)}


def create_random_game(width: int = 8, height: int = 8, player_ids: Optional[List[str]] = None, seed: Optional[int] = None) -> Game:
    g = Game()
    g.initialize(width=width, height=height, player_ids=player_ids, seed=seed)
    return g
