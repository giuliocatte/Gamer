import logging

from core.players import RandomPlayer, IOPlayer, Player
from core.lib import shuffling_negamax
from .referee import check_victory

logger = logging.getLogger('tictactoe.players')

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
        logger.debug('available_moves: %s', self.available_moves)

    def compute_available_moves(self):
        return self.available_moves


class MiniMaxingCFPlayer(CFPlayer):

    search_depth = 2
    evaluation_level = 0

    def dumb_value_function(self, node):
        board = node['board']
        move = node['move']
        try:
            y = board[move].index(0) - 1
        except IndexError:
            y = 6
        return check_victory(board, move, y, node['to_move'])

    def some_heuristics(self, node):
        raise NotImplementedError

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
                    'move': x
                }

    @staticmethod
    def terminal_function(node):
        board = node['board']
        move = node['move']
        try:
            y = board[move].index(0) - 1
        except IndexError:
            y = 6
        if check_victory(board, move, y, node['to_move']):
            return True
        if all(c[-1] != 0 for c in board):
            return True
        return False

    def process_turn_input(self, inp):
        b = self.board = []
        for col in inp:
            b.append([int(v) for v in col.split()])

    def compute_move(self):
        valf = [self.dumb_value_function, self.some_heuristics][self.evaluation_level]
        bestvalue, bestmove = shuffling_negamax({'board': self.board, 'to_move': 1 if self.id == 1 else -1, 'move': None},
                          value_function=valf, child_function=self.child_function,
                         terminal_function=self.terminal_function, depth=self.search_depth)
        logger.debug('bestmove: %s; bestvalue: %s', bestmove, bestvalue)
        return bestmove['move']


class TensorFlowCFPlayer(CFPlayer):
    '''
        uses a trained neural network with 42 neurons input (representing spaces in the grid)
        and 7 neurons output (representing chance that the move in that position is the best move)

        since this appears to be some sort of a standard, in the grid 1 represents my pieces, -1 opponent pieces,
        and 0 empty cells
    '''
    saved_nn_path = ''

    def setup(self, player_id, inp):
        super().setup(player_id, inp)
        self.nn = get_callable_from_saved_network(self.saved_nn_path)

    def process_turn_input(self, inp):
        a = self.available_moves = []
        n = self.network_input = []
        raise NotImplementedError

    def compute_move(self):
        outp = self.nn(self.network_input)
        logger.debug('nn output: %s', outp)
        move = max((el, i) for i, el in enumerate(outp) if i in self.available_moves)[1]
        return str(move + 1)
