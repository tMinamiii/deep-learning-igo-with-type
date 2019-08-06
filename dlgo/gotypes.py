from __future__ import annotations

from collections import namedtuple
from enum import IntEnum
from typing import List


class Player(IntEnum):
    d_black = 1
    d_white = 2

    @property
    def other(self) -> Player:
        return Player.d_black if self == Player.d_white else Player.d_white


class Point(namedtuple('Point', 'row col')):
    def neighbors(self) -> List[Point]:
        return [
            Point(self.row - 1, self.col),
            Point(self.row + 1, self.col),
            Point(self.row, self.col - 1),
            Point(self.row, self.col + 1),
        ]
