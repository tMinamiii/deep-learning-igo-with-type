"""gotypes."""
from __future__ import annotations

import enum
from collections import namedtuple
from typing import List


class Player(enum.IntEnum):
    """Player.

    Player class

    Attribute:
        black(int): black
        white(int): white
    """

    black = 1
    white = 2

    @property
    def other(self) -> Player:
        """other."""
        return Player.black if self == Player.white else Player.white


class Point(namedtuple('Point', 'row col')):
    """Point.

    Point class

    Attribute:
        row(int): row number.
        col(int): column number.
    """

    row: int
    col: int

    def neighbors(self) -> List[Point]:
        """neighbors."""
        return [
            Point(self.row - 1, self.col),
            Point(self.row + 1, self.col),
            Point(self.row, self.col - 1),
            Point(self.row, self.col + 1),
        ]
