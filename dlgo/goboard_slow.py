from __future__ import annotations

import copy
from typing import Dict, Iterable, List, Optional, Set

from dlgo.gotypes import Player, Point


'''
アメリカ囲碁協会では打つ,パス,投了の3つのタイプをMoveで表す
'''


class Move():
    def __init__(self, point: Optional[Point] = None, is_pass: bool = False, is_resign: bool = False):
        assert(point is not None) ^ is_pass ^ is_resign
        self.point: Optional[Point] = point
        self.is_play: bool = (point is not None)
        self.is_pass: bool = is_pass
        self.is_resign: bool = is_resign

    # 盤上に石をおく
    @classmethod
    def play(cls, point: Point) -> Move:
        return Move(point=point)

    # 着手をパスする
    @classmethod
    def pass_turn(cls) -> Move:
        return Move(is_pass=True)

    # ゲームを投了する
    @classmethod
    def resign(cls) -> Move:
        return Move(is_resign=True)


class GoString():
    def __init__(self, color: Player, stones: Iterable[Point], liberties: Iterable[Point]):
        self.color: Player = color
        self.stones: Set[Point] = set(stones)
        self.liberties: Set[Point] = set(liberties)

    def remove_liberty(self, point: Optional[Point]):
        if point is not None:
            self.liberties.remove(point)

    def add_liberty(self, point: Point):
        self.liberties.add(point)

    def merged_with(self, go_string: GoString) -> GoString:
        assert go_string.color == self.color
        combined_stones = self.stones | go_string.stones
        return GoString(
            self.color,
            combined_stones,
            (self.liberties | go_string.liberties) - combined_stones
        )

    @property
    def num_liberties(self):
        return len(self.liberties)

    def __eq__(self, other):
        return isinstance(other, GoString) and \
            self.color == other.color and \
            self.stones == other.stones and \
            self.liberties == other.liberties


class Board():
    def __init__(self, num_rows: int, num_cols: int):
        self.num_rows: int = num_rows
        self.num_cols: int = num_cols
        self._grid: Dict[Optional[Point], Optional[GoString]] = {}

    def is_on_grid(self, point: Point) -> bool:
        return 1 <= point.row <= self.num_rows and \
            1 <= point.col <= self.num_cols

    def get(self, point: Point) -> Optional[Player]:
        string = self._grid.get(point)
        if string is None:
            return None
        return string.color

    def set_go_string(self, point: Point) -> Optional[GoString]:
        string = self._grid.get(point)
        if string is None:
            return None
        return string

    def _remove_string(self, string: GoString):
        for point in string.stones:
            for neighbor in point.neighbors():
                neighbor_string = self._grid.get(neighbor)
                if neighbor_string is None:
                    continue
                if neighbor_string is not string:
                    neighbor_string.add_liberty(point)
            self._grid[point] = None

    def place_stone(self, player: Player, point: Point):
        assert self.is_on_grid
        assert self._grid.get(point) is None
        adjacent_same_color: List[GoString] = []
        adjacent_opposite_color: List[GoString] = []
        liberties: List[Point] = []
        for neighbor in point.neighbors():
            if not self.is_on_grid(neighbor):
                continue
            neighbor_string: Optional[GoString] = self._grid.get(neighbor)
            if neighbor_string is None:
                liberties.append(neighbor)
            elif neighbor_string.color == player:
                if neighbor_string not in adjacent_same_color:
                    adjacent_same_color.append(neighbor_string)
                else:
                    if neighbor_string not in adjacent_opposite_color:
                        adjacent_opposite_color.append(neighbor_string)
            new_string = GoString(player, [point], liberties)

            for same_color_string in adjacent_same_color:
                new_string = new_string.merged_with(same_color_string)
            for new_string_point in new_string.stones:
                self._grid[new_string_point] = new_string
            for other_color_string in adjacent_opposite_color:
                other_color_string.remove_liberty(point)
            for other_color_string in adjacent_opposite_color:
                if other_color_string.num_liberties == 0:
                    self._remove_string(other_color_string)


class GameState():
    def __init__(self, board: Board, next_player: Player, previous, move: Move):
        self.board = board
        self.next_player = next_player
        self.previous = previous
        self.last_move = move

    def apply_move(self, move: Move):
        if move.is_play:
            next_board = copy.deepcopy(self.board)
            if move.point is not None:
                next_board.place_stone(self.next_player, move.point)
