from __future__ import annotations

import copy
from typing import Dict, List, Optional

from dlgo.gotypes import Player, Point


class Move():
    def __init__(self, point=None, is_pass=False, is_resign=False):
        assert(point is not None) ^ is_pass ^ is_resign
        self.point = point
        self.is_play = (self.point is not None)
        self.is_pass = is_pass
        self.is_resign = is_resign

    @classmethod
    def play(cls, point) -> Move:
        return Move(point=point)

    @classmethod
    def pass_turn(cls) -> Move:
        return Move(is_pass=True)

    @classmethod
    def resign(cls) -> Move:
        return Move(is_resign=True)


class GoString():
    def __init__(self, color: Player, stones, liberties):
        self.color: Player = color
        self.stones = set(stones)
        self.liberties = set(liberties)

    def move_liberty(self, point) -> None:
        self.liberties.remove(point)

    def add_liberty(self, point) -> None:
        self.liberties.add(point)

    def merged_with(self, go_string: GoString) -> GoString:
        assert go_string.color == self.color
        combined_stones = self.stones | go_string.stones
        return GoString(
            self.color,
            combined_stones,
            (self.liberties | go_string.liberties) - combined_stones
        )


class Board():
    def __init__(self, num_rows, num_cols):
        self.num_rows = num_rows
        self.num_cols = num_cols
        self._grid: Dict[Point, GoString] = {}

    def place_stone(self, player: Player, point: Point):
        assert self.is_on_grid(point)
        assert self._grid.get(point) is None
        adjacent_same_color: List[GoString] = []
        adjacent_opposite_color: List[GoString] = []
        liberties: List[Point] = []
        for neighbor in point.neighbors():
            if not self.is_on_grid(neighbor):
                continue
            neighbor_string = self._grid.get(neighbor)
            if neighbor_string is None:
                liberties.append(neighbor)
            elif neighbor_string.color == player:
                if neighbor_string not in adjacent_same_color:
                    adjacent_same_color.append(neighbor_string)
                else:
                    if neighbor_string not in adjacent_opposite_color:
                        adjacent_opposite_color.append(neighbor_string)
            new_string = GoString(player, [point], liberties)

    def is_on_grid(self, point: Point):
        return None

    def get(self, point: Point):
        string = self._grid.get(point)
        if string is None:
            return None
        return string.color

    def get_go_string(self, point: Point) -> Optional[GoString]:
        go_str = self._grid.get(point)
        return go_str
