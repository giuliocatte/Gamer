
from core.main import Referee, InvalidMove, DRAW, RUNNING, ref_logger
import colorama
colorama.init()  # this should make it work for windows

COLORS = ['YELLOW', 'RED']
PIECE = "◉"


class ConnectFour(Referee):
    '''
        board is a list of 7 columns; each column is a list of 7 cells, where position 0 is bottom

        internally, players are 1 and -1, 0 are empty spaces
        so a player color is COLORS[(player_value + 2) % 3] or COLORS[player_id - 1]

        moves are numbers from 1 to 7, so internally there's always a -1 shift
    '''
    painting_board = False

    def __init__(self, players):
        super().__init__(players)
        self.board = [[0] * 6 for i in range(7)]
        self.turn_number = 0

    def setup(self):
        ref_logger.info('starting game; board:\n%s', self.draw_board())
        return COLORS

    def get_board(self, player_id):
        b = self.board
        return [' '.join(str(b[c][r]) for r in range(6)) for c in range(7)]

    def execute_turn(self, player_id, move):
        print('execting', move, 'for player', player_id)
        self.turn_number += 1
        b = self.board
        try:
            move = int(move) - 1
            if not (0 <= move <= 6):
                raise ValueError('move out of range')
        except (TypeError, ValueError):
            raise InvalidMove('moves should an integer in range 1-7, received: "{}"'.format(move + 1))
        col = b[move]
        try:
            row_ind = col.index(0)
        except ValueError:
            raise InvalidMove('received move {}, column already full'.format(move))
        player_value = 1 if player_id == 1 else -1
        print('column prima', col)
        col[row_ind] = player_value
        print('column dopo', col)
        if self.painting_board:
            self.draw_board()
        if player_id == self.players_number:
            self.round_number += 1

        # searching for victory
        for dx, dy in ((1, 0), (0, 1), (-1, 1), (1, 1)):
            pieces = 1
            for side in (-1, 1):
                for dist in range(1, 4):
                    cx = move + dist * dx * side
                    cy = row_ind + dist * dy * side
                    if 0 <= cx <= 6 and 0 <= cy <= 5 and b[cx][cy] == player_value:
                        pieces += 1
                    else:
                        break
            if pieces >= 4:
                return player_id

        if all(c[-1] for c in b):
            return DRAW
        return RUNNING

    def draw_board(self):
        b = self.board
        for row in range(6):
            print(' |', end='')
            for col in b:
                if col[row] == 0:
                    print(' ', end='')
                else:
                    print(getattr(colorama.Fore, COLORS[(col[row] + 2) % 3]) + PIECE, end='')
            print('|')
        print(' +-------+')
        print('  1234567')
