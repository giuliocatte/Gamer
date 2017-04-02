import os

from core.main import SequentialGame, InvalidMove, DRAW, RUNNING, ref_logger
import colorama
colorama.init()  # this should be mandatory for windows

COLORS = ['YELLOW', 'RED']
PIECE = "◉"


def check_victory(board, x):
    '''
        check if move x has been victorious
    '''
    col = board[x]
    if col[-1]:
        y = 5
    else:
        y = col.index(0) - 1
    move_value = col[y]
    for dx, dy in ((1, 0), (0, 1), (-1, 1), (1, 1)):
        pieces = 1
        for side in (-1, 1):
            for dist in range(1, 4):
                cx = x + dist * dx * side
                cy = y + dist * dy * side
                if 0 <= cx <= 6 and 0 <= cy <= 5 and board[cx][cy] == move_value:
                    pieces += 1
                else:
                    break
        if pieces >= 4:
            return True
    return False


class ConnectFour(SequentialGame):
    '''
        board is a list of 7 columns; each column is a list of 7 cells, where position 0 is bottom

        internally, players are 1 and 2, and board is converted when outputting to players
        to 1 for "you" and -1 for "opponent". 0 is empty, both internally and in the output

        moves are numbers from 1 to 7, so internally there's always a -1 shift
    '''
    def __init__(self, players):
        super().__init__(players)
        self.board = [[0] * 6 for i in range(7)]

    def setup(self):
        ref_logger.info('starting game')
        return [[c] for c in COLORS]

    def get_board(self, player_id):
        b = self.board
        outmap = {player_id: '1', (player_id % 2) + 1: '-1', 0: '0'}
        return [' '.join(outmap[b[c][r]] for r in range(6)) for c in range(7)]

    def execute_turn(self, player_id, strmove):
        b = self.board
        try:
            move = int(strmove) - 1
            if not (0 <= move <= 6):
                raise ValueError('move out of range')
        except (TypeError, ValueError):
            raise InvalidMove('moves should an integer in range 1-7, received: "{}"'.format(strmove))
        col = b[move]
        try:
            row_ind = col.index(0)
        except ValueError:
            raise InvalidMove('received move {}, column already full'.format(move))
        # updating board
        col[row_ind] = player_id

        # searching for victory
        if check_victory(b, move):
            return player_id

        if all(c[-1] for c in b):
            return DRAW
        return RUNNING

    def interactive_board(self, lattice=True):
        print()
        b = self.board
        for row in range(5, -1, -1):
            print(colorama.Fore.BLACK + ' |', end='')
            for i, col in enumerate(b):
                if col[row] == 0:
                    print(' ', end='')
                else:
                    print(getattr(colorama.Fore, COLORS[col[row] - 1]) + PIECE, end='')
                if lattice and i != 6:
                    print(colorama.Fore.BLACK + '|', end='')
            print(colorama.Fore.BLACK + '|')
            if lattice:
                 print(colorama.Fore.BLACK + ' +-+-+-+-+-+-+-+')
        if lattice:
            print(colorama.Fore.BLACK + '  1 2 3 4 5 6 7')
        else:
            print(colorama.Fore.BLACK + ' +-------+')
            print(colorama.Fore.BLACK + '  1234567')
