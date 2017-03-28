import os

from core.main import SequentialGame, InvalidMove, DRAW, RUNNING, ref_logger

EMPTY = '.'
SYMBOLS = [EMPTY, 'X', 'O']  # player_id parte da 1

LINES = [['A1', 'A2', 'A3'], ['B1', 'B2', 'B3'], ['C1', 'C2', 'C3'],
        ['A1', 'B1', 'C1'], ['A2', 'B2', 'C2'], ['A3', 'B3', 'C3'],
         ['A1', 'B2', 'C3'], ['A3', 'B2', 'C1']]


class TicTacToe(SequentialGame):

    def __init__(self, players):
        super().__init__(players)
        self.board = dict.fromkeys((x + y for x in 'ABC' for y in '123'), EMPTY)

    def setup(self):
        ref_logger.info('starting game; board:\n%s', self.draw_board())
        return [[s] for s in SYMBOLS[1:]]

    def get_board(self, player_id):
        b = self.board
        return [' '.join(b[r + str(c)] for c in range(1, 4)) for r in 'ABC']

    def execute_turn(self, player_id, move):
        b = self.board
        move = move.upper()
        try:
            occ = b[move]
        except KeyError:
            raise InvalidMove('moves should be of type "XY" with X in "ABC" and Y in "123", received: "{}"'.format(move))
        if occ != EMPTY:
            raise InvalidMove('received move {}, tile already occupied'.format(move))
        v = b[move] = SYMBOLS[player_id]
        ref_logger.info('turn %s; board:\n%s', self.turn_number, self.draw_board())
        if player_id == self.players_number:
            self.round_number += 1
        if any(all(b[li] == v for li in line) for line in LINES):
            return player_id
        if all(v != EMPTY for v in b.values()):
            return DRAW
        return RUNNING

    def draw_board(self):
        return '    1   2   3\n\n' \
            'A   {b[A1]} | {b[A2]} | {b[A3]}\n' \
            '   ---+---+---\n' \
            'B   {b[B1]} | {b[B2]} | {b[B3]}\n' \
            '   ---+---+---\n' \
            'C   {b[C1]} | {b[C2]} | {b[C3]}\n'.format(b=self.board).replace(EMPTY, ' ')

    def interactive_board(self):
        os.system('clear')
        print(self.draw_board())

