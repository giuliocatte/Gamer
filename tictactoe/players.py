import logging

from core.players import RandomPlayer, IOPlayer, Player
from core.lib import negamax, minimax

from .referee import LINES, SYMBOLS, EMPTY
from .tf_training import get_callable_from_saved_network, DEFAULT_PATH


logger = logging.getLogger('tictactoe.players')

inf = float('inf')


class TTTPlayer(Player):
    turn_lines = 3
    setup_lines = 1



class IOTTTPlayer(IOPlayer, TTTPlayer):

    loud = False

    def setup(self, player_id, inp):
        print('player', player_id, 'your symbol is', inp[0])
        return super().setup(player_id, inp)


class RandomTTTPlayer(RandomPlayer, TTTPlayer):

    def process_turn_input(self, inp):
        a = self.available_moves = []
        for r, row in zip('ABC', inp):
            for c, cell in zip('123', row.split()):
                if cell == EMPTY:
                    a.append(r + c)
        logger.debug('available_moves: %s', self.available_moves)

    def compute_available_moves(self):
        return self.available_moves


class MiniMaxingTTTPlayer(TTTPlayer):

    algorithm = 'negamax'

    search_depth = 0
    evaluation_level = 0

    def dumb_value_function(self, node):
        board = node['board']
        pid = self.id
        me = SYMBOLS[pid]
        opp = SYMBOLS[(pid % 2) + 1]
        val = 0
        if any(all(board[c] == me for c in l) for l in LINES):
            val = inf
        elif any(all(board[c] == opp for c in l) for l in LINES):
            val = -inf
        return val

    def slightly_better_value_function(self, node):
        board = node['board']
        me = SYMBOLS[self.id]
        opp = SYMBOLS[(self.id % 2) + 1]
        val = 0
        if any(all(board[c] == me for c in l) for l in LINES):
            val = inf
        elif any(all(board[c] == opp for c in l) for l in LINES):
            val = -inf
        elif board['B2'] == me:
            val = 1
        return val

    def some_heuristics(self, node):
        board = node['board']
        me = SYMBOLS[self.id]
        opp = SYMBOLS[(self.id % 2) + 1]
        val = 0
        if any(all(board[c] == me for c in l) for l in LINES):
            val = inf
        elif any(all(board[c] == opp for c in l) for l in LINES):
            val = -inf
        else:
            if board['B2'] == me:
                val += 100
            for l in LINES:
                linestr = ''.join(board[c] for c in l)
                if linestr.count(me) == 2 and EMPTY in linestr:
                    val += 1
                elif linestr.count(opp) == 2 and EMPTY in linestr:
                    val -= 1
        return val

    @staticmethod
    def child_function(node):
        board, to_move = node['board'], node['to_move']
        for k, v in board.items():
            if v == EMPTY:
                b = board.copy()
                b[k] = SYMBOLS[to_move]
                yield {
                    'board': b,
                    'to_move': (to_move % 2) + 1,
                    'move': k
                }

    @staticmethod
    def terminal_function(node):
        board = node['board']
        for s in SYMBOLS[1:]:
            if any(all(board[c] == s for c in l) for l in LINES):
                return True
        return all(c != EMPTY for c in board.values())

    def process_turn_input(self, inp):
        b = self.board = {}
        a = self.available_moves = []
        for r, row in zip('ABC', inp):
            for c, cell in zip('123', row.split()):
                k = r + c
                b[k] = cell
                if cell == EMPTY:
                    a.append(k)

    def compute_move(self):
        valf = [
            self.dumb_value_function,
            self.slightly_better_value_function,
            self.some_heuristics
        ][self.evaluation_level]
        algo = {'minimax': minimax,
                'negamax': negamax}[self.algorithm]

        bestvalue, bestmove = algo({'board': self.board, 'to_move': self.id, 'move': None},
                          value_function=valf, child_function=self.child_function,
                         terminal_function=self.terminal_function, depth=self.search_depth)
        return bestmove['move']


class TensorFlowTTTPlayer(TTTPlayer):
    '''
        uses a trained neural network with 9 neurons input (representing spaces in the grid)
        and 9 neurons output (representing chance that the move in that position is the best move)

        since this appears to be some sort of a standard, in the grid 1 represents my pieces, -1 opponent pieces,
        and 0 empty cells
    '''
    saved_nn_path = DEFAULT_PATH

    def setup(self, player_id, inp):
        super().setup(player_id, inp)
        self.nn = get_callable_from_saved_network(self.saved_nn_path)

    def process_turn_input(self, inp):
        symbols = {
            SYMBOLS[self.id]: 1,
            SYMBOLS[(self.id % 2) + 1]: -1,
            SYMBOLS[0]: 0
        }
        self.network_input = [symbols[c] for row in inp for c in row.split()]

    def compute_move(self):
        outp = self.nn(self.network_input)
        print('outp:', outp * 100)
        move = max((el, i) for i, el in enumerate(outp) if self.network_input[i] == 0)[1]
        return 'ABC'[move // 3] + '123'[move % 3]
