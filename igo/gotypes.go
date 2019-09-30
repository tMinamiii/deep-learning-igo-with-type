package igo

type Player int

const (
	Black Player = iota
	White Player
)

type Player(enum.IntEnum):
    black = 1
    white = 2

    @property
    def other(self) -> Player:
        return Player.black if self == Player.white else Player.white


class Point(namedtuple('Point', 'row col')):
    row: int
    col: int

    def neighbors(self) -> List[Point]:
        return [
            Point(self.row - 1, self.col),
            Point(self.row + 1, self.col),
            Point(self.row, self.col - 1),
            Point(self.row, self.col + 1),
        ]
