import copy

from dlgo.gotypes import Player


class Move():
    def __init__(self, point=None, is_pass=False, is_resign=False):
        assert(point is not None) ^ is_pass ^ is_resign
        self.point = point
        self.is_play = (self.point is not None)
        self.is_pass = is_pass
        self.is_resign = is_resign

    @classmethod
    def play(cls, point) -> 'Move':
        return Move(point=point)

    @classmethod
    def pass_turn(cls) -> 'Move':
        return Move(is_pass=True)

    @classmethod
    def resign(cls) -> 'Move':
        return Move(is_resign=True)


class GoString():
    def __init__(self, color, stones, liberties):
        self.color = color
        self.stones = set(stones)
        self.liberties = set(liberties)

    def move_liberty(self, point) -> None:
        self.liberties.remove(point)

    def add_liberty(self, point) -> None:
        self.liberties.add(point)

    def merged_with(self, go_string: 'GoString') -> 'GoString':
        assert go_string.color == self.color
        combined_stones = self.stones | go_string.stones
        return GoString(
            self.color,
            combined_stones,
            (self.liberties | go_string.liberties) - combined_stones
        )






