from random import choice

from core import lib
from core.main import player_logger


class Player:
    '''
        Abstract base class for AIs
        most of times the only methods needed to extend are:
        - process_turn_input, called each turn with the game state input from the referee
        - compute_move, called each turn to have the AI output move for the referee
    '''

    setup_lines = 1
    turn_lines = 1

    def __init__(self, **kw):
        self.arguments = kw
        self.reset()
        for k, v in kw.items():
            setattr(self, k, v)

    def reset(self):
        '''
            executing this method puts the player at the starting state
        '''
        self.listener = self.coroutine()

    def setup(self, player_id, inp):
        self.id = player_id
        self.listener.send(None)

    def compute_move(self):
        '''
            given the input for a turn as a list of turn_lines string, computes the move and return it as a string
        '''
        raise NotImplementedError

    def coroutine(self):
        outp = None
        while True:
            inp = []
            for i in range(self.turn_lines):
                v = yield outp  # same output is yielded n times, referee will consider only the last one
                inp.append(v)
            self.process_turn_input(inp)
            outp = self.compute_move()

    def process_turn_input(self, inp):
        '''
            updates internal state for a turn input
        '''
        raise NotImplementedError

    def __str__(self):
        return '{}({})'.format(self.__class__.__name__, ', '.join('{}={}'.format(*i) for i in self.arguments.items()))


class IOPlayer(Player):

    loud = True

    def setup(self, player_id, inp):
        if self.loud:
            print('player', player_id, 'received starting configuration:')
            for i in range(self.setup_lines):
                print('{}. {}'.format(i + 1, inp[i]))
        return super().setup(player_id, inp)

    def process_turn_input(self, inp):
        if self.loud:
            print('received input:')
            for i in range(self.turn_lines):
                print('{}. {}'.format(i + 1, inp[i]))

    def compute_move(self):
        print('enter move: ', end='')
        return input()


class RandomPlayer(Player):

    def compute_available_moves(self):
        '''
            returns all available moves for next turn as a list
            using internal state
        '''
        return NotImplemented

    def compute_move(self):
        mv = self.compute_available_moves()
        return choice(mv)


class MiniMaxingPlayer(Player):
    '''
        abstract base class for a player based on a minimax algorithm
        the "node" for the minimax is a dictionary
            {'board': <representation of the board>, 'to_move': <id of the player to move>, 'move': <last move>}

        if the board is "rotated towards the player" (i.e. it should behave like if it was player 1), class attribute
        fixed_id should be set at 1.

        several value functions can be implemented, writing the method name in the class list value_functions
        attribute "evaluation_level" will determine which one is used (index of that list)
    '''

    search_depth = 4  # for some reason, even numbers perform way better
    value_functions = []
    evaluation_level = 0
    algorithm = 'shuffling_negamax'
    fixed_id = None

    @staticmethod
    def child_function(node):
        '''
           yields all the nodes reachable from the one passed
        '''
        raise NotImplementedError

    @staticmethod
    def terminal_function(node):
        '''
            returns True if this nodes has no childs
        '''
        raise NotImplementedError

    def compute_move(self):
        '''
            assumes method process_turn_input have written attribute self.board
        '''
        fid = self.fixed_id or self.id
        valf = self.value_functions[self.evaluation_level]
        bestvalue, bestmove = getattr(lib, self.algorithm)({'board': self.board, 'to_move': fid, 'move': None},
                          value_function=valf, child_function=self.child_function,
                         terminal_function=self.terminal_function, depth=self.search_depth)
        player_logger.debug('bestmove: %s; bestvalue: %s', bestmove, bestvalue)
        return str(bestmove['move'] + 1)
