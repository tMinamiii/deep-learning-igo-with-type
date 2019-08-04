import enum
from collections import namedtuple


class Player(enum.Enum):
    d_black = 1
    d_white = 2

    @property
    def other(self):
        return Player.d_black if self == Player.d_white else Player.d_white


class Point(namedtuple('Point', 'row col')):
    def neighbors(self):
        return [
            Point(self.row - 1, self.col),
            Point(self.row + 1, self.col),
            Point(self.row, self.col - 1),
            Point(self.row, self.col + 1),
        ]
