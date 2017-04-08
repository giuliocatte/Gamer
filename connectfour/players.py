
from core.players import RandomPlayer, IOPlayer, Player, MiniMaxingPlayer
from core.lib import shuffling_negamax
from core.main import player_logger
from .referee import check_victory
from .nn import get_callable_from_saved_network, DEFAULT_PATH


inf = float('inf')


class CFPlayer(Player):
    turn_lines = 7
    setup_lines = 1


class IOCFPlayer(IOPlayer, CFPlayer):

    loud = False

    def setup(self, player_id, inp):
        print('player', player_id, 'your color is', inp)
        return super().setup(player_id, inp)


class RandomCFPlayer(RandomPlayer, CFPlayer):

    def process_turn_input(self, inp):
        a = self.available_moves = []
        for i, col in enumerate(inp):
            if col[-1] == '0':
                a.append(str(i + 1))
        player_logger.debug('available_moves: %s', self.available_moves)

    def compute_available_moves(self):
        return self.available_moves


class MiniMaxingCFPlayer(MiniMaxingPlayer, CFPlayer):

    search_depth = 2
    evaluation_level = 1
    value_functions = ['dumb_value_function', 'some_heuristics']
    fixed_id = 1

    @staticmethod
    def dumb_value_function(node):
        board = node['board']
        move = node['move']
        value = -node['to_move'] * inf if check_victory(board, move - 1) else 0
        player_logger.debug('evaluated move %s on board %s: value %s', move, board, value)
        return value

    @staticmethod
    def some_heuristics(node):
        board = node['board']
        x = node['move'] - 1
        if check_victory(board, x):
            return -node['to_move'] * inf
        col = board[x]
        if col[-1]:
            y = 5
        else:
            y = col.index(0) - 1
        move_value = col[y]
        pieces = 0
        for dx, dy in ((1, 0), (0, 1), (-1, 1), (1, 1)):
            p = 1
            l = 1
            for side in (-1, 1):
                if (dx, dy) == (0, 1) and side == 1:
                    continue  # dont count lines directed up
                for dist in range(1, 4):
                    cx = x + dist * dx * side
                    cy = y + dist * dy * side
                    if 0 <= cx <= 6 and 0 <= cy <= 5:
                        if board[cx][cy] == move_value:
                            p += 1
                        elif board[cx][cy] == 0:
                            l += 1
                        else:
                            break
                    else:
                        break
            if l >= 4:
                pieces += p ** 2
        return -node['to_move'] * pieces

    @staticmethod
    def child_function(node):
        board, to_move = node['board'], node['to_move']
        for x, col in enumerate(board):
            if col[-1] == 0:
                c = list(col)
                c[c.index(0)] = to_move
                b = list(board)
                b[x] = c
                yield {
                    'board': b,
                    'to_move': -to_move,
                    'move': x + 1
                }

    @staticmethod
    def terminal_function(node):
        board = node['board']
        move = node['move']
        if move is None:
            # state of the board BEFORE the move
            return False
        if check_victory(board, move - 1):
            return True
        if all(c[-1] != 0 for c in board):
            return True
        return False

    def process_turn_input(self, inp):
        b = self.board = []
        for col in inp:
            b.append([int(v) for v in col.split()])


class TensorFlowCFPlayer(CFPlayer):
    '''
        uses a trained neural network with 42 neurons input (representing spaces in the grid)
        and 7 neurons output (representing chance that the move in that position is the best move)

        since this appears to be some sort of a standard, in the grid 1 represents my pieces, -1 opponent pieces,
        and 0 empty cells
    '''
    saved_nn_path = DEFAULT_PATH

    def setup(self, player_id, inp):
        super().setup(player_id, inp)
        self.nn = get_callable_from_saved_network(self.saved_nn_path)

    def process_turn_input(self, inp):
        a = self.available_moves = []
        n = self.network_input = []
        for i, col in enumerate(inp):
            vals = [int(v) for v in col.split()]
            if vals[-1] == 0:
                a.append(i)
            n.extend(vals)

    def compute_move(self):
        outp = self.nn(self.network_input)
        player_logger.info('nn output: %s', outp)
        move = max((el, i) for i, el in enumerate(outp) if i in self.available_moves)[1]
        return str(move + 1)
