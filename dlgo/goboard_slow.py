"""goboard."""
from __future__ import annotations

import copy
from typing import Dict, Iterable, List, Optional, Set, Tuple, Union

from dlgo.gotypes import Player, Point


class Move():
    """アメリカ囲碁協会では打つ,パス,投了の3つのタイプをMoveで表す."""

    def __init__(
            self, point: Optional[Point] = None, is_pass: bool = False, is_resign: bool = False
    ):
        """__init__."""
        assert (point is not None) ^ is_pass ^ is_resign
        self.point: Optional[Point] = point
        self.is_play: bool = (point is not None)
        self.is_pass: bool = is_pass
        self.is_resign: bool = is_resign

    @classmethod
    def play(cls, point: Point) -> Move:
        """盤上に石をおく."""
        return Move(point=point)

    @classmethod
    def pass_turn(cls) -> Move:
        """着手をパスする."""
        return Move(is_pass=True)

    @classmethod
    def resign(cls) -> Move:
        """ゲームを投了する."""
        return Move(is_resign=True)


class GoString():
    """呼吸点を管理するために、石が連なった塊（連）を表現する."""

    def __init__(self, color: Player, stones: Iterable[Point], liberties: Iterable[Point]):
        """__init."""
        self.color: Player = color
        self.stones: Set[Point] = set(stones)
        self.liberties: Set[Point] = set(liberties)

    def remove_liberty(self, point: Optional[Point]):
        """remove_libery."""
        if point is not None:
            self.liberties.remove(point)

    def add_liberty(self, point: Point):
        """add_liberty."""
        self.liberties.add(point)

    def merged_with(self, go_string: GoString) -> GoString:
        """merged_with.

        プレイヤーが石を置いて連と連とマージする
        相手の連を奪うこと？
        assert go_string.colort == self.colorとあるので敵の連を奪う以外で
        このメソッドを呼び出してはいけない
        """
        assert go_string.color == self.color
        combined_stones = self.stones | go_string.stones
        return GoString(
            self.color, combined_stones, (self.liberties | go_string.liberties) - combined_stones
        )

    @property
    def num_liberties(self):
        """num_liberties."""
        return len(self.liberties)

    def __eq__(self, other):
        """__eq__."""
        return isinstance(other, GoString) and \
            self.color == other.color and \
            self.stones == other.stones and \
            self.liberties == other.liberties


class Board():
    """Board.

    盤上に石を置くロジックと、石を取るロジックを担当
    最初のアイデアは、盤上の各点の状態を追跡する 19 x 19 の配列を作成することです。
    """

    def __init__(self, num_rows: int, num_cols: int):
        """__init__."""
        self.num_rows: int = num_rows
        self.num_cols: int = num_cols
        self._grid: Dict[Optional[Point], Optional[GoString]] = {}

    def is_on_grid(self, point: Point) -> bool:
        """is_on_grid."""
        return 1 <= point.row <= self.num_rows and \
            1 <= point.col <= self.num_cols

    def get(self, point: Point) -> Optional[Player]:
        """get."""
        string = self._grid.get(point)
        if string is None:
            return None
        return string.color

    def get_go_string(self, point: Point) -> Optional[GoString]:
        """get_go_string."""
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
        """place_stone."""
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
            elif neighbor_string not in adjacent_opposite_color:
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
    """GameState.

    盤面の全ての石が含むだけでなく、どちらの手番かと、前の状態が何であったを記録します
    """

    def __init__(
            self, board: Board, next_player: Player, previous: Optional[GameState],
            move: Optional[Move]
    ):
        """__init__."""
        self.board = board
        self.next_player = next_player
        self.previous_state = previous
        self.last_move = move

    def apply_move(self, move: Move) -> GameState:
        """apply_move."""
        if move.is_play:
            next_board = copy.deepcopy(self.board)
            if move.point is not None:
                next_board.place_stone(self.next_player, move.point)
        else:
            next_board = self.board
        return GameState(next_board, self.next_player.other, self, move)

    @classmethod
    def new_game(cls, board_size: Union[int, Tuple[int, int]]) -> GameState:
        """new_game."""
        if isinstance(board_size, int):
            board_size = (board_size, board_size)
        board = Board(*board_size)
        return GameState(board, Player.black, None, None)

    def is_over(self) -> bool:
        """is_over."""
        if self.last_move is None:
            return False
        if self.last_move.is_resign:
            return True
        if self.previous_state is not None:
            second_last_move = self.previous_state.last_move
            if second_last_move is None:
                return False
            return self.last_move.is_pass and second_last_move.is_pass
        return False

    def is_move_self_capture(self, player: Player, move: Move) -> bool:
        """is_move_self_capture."""
        if not move.is_play:
            return False
        next_board: Board = copy.deepcopy(self.board)
        if move.point is not None:
            next_board.place_stone(player, move.point)
            new_string = next_board.get_go_string(move.point)
            if new_string is not None:
                return new_string.num_liberties == 0
        return False
