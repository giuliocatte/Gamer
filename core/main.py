import logging
import os
from random import shuffle

from .players import IOPlayer

match_logger = logging.getLogger('gamer.match')
ref_logger = logging.getLogger('gamer.referee')
player_logger = logging.getLogger('gamer.player')
# loggo a livello info lo sviluppo della partita

# TODO: valutare se non usare numeri negativi per far partire player_id da 0
RUNNING = 0
DRAW = -1

SIMULTANEOUS = 1
SEQUENTIAL = 2


class InvalidMove(Exception):
    pass


class Game:
    '''
        abstract base class for games
    '''
    players_number = 2

    def __init__(self, random_seed=None):
        self.random_seed = random_seed
        self.round_number = 0

    def setup(self):
        '''
            generates the starting game data for each player as a list
            probably you would overwrite this
        '''
        return self.get_boards()

    def get_board(self, player_id):
        '''
            returns the current board info for player "player_id"
            as a sequence of strings
        '''
        raise NotImplementedError

    def get_boards(self):
        '''
            commodity: returns the current boards for each player, as a list
        '''
        return [self.get_board(i + 1) for i in range(self.players_number)]

    def interactive_board(self):
        '''
            prints an on screen representation of current board
        '''
        raise NotImplementedError


class SequentialGame(Game):
    '''
        abstract base class for sequential games
    '''
    turn_type = SEQUENTIAL

    def __init__(self, random_seed=None):
        super().__init__(random_seed)
        self.turn_number = 0

    def execute_turn(self, player_id, move):
        '''
            move is a single move for player "player_id"
            returns a exit code:
            0 game still running
            n > 0 id of the winner
            -1 game draw
        '''
        raise NotImplementedError


class SimultanousGame(Game):
    '''
        abstract base class for simultaneous games
    '''
    turn_type = SIMULTANEOUS

    def execute_turn(self, moves):
        '''
            moves is a list of moves for each player
            returns a exit code:
            0 game still running
            n > 0 id of the winner
            -1 game draw
        '''
        raise NotImplementedError


class Match:
    '''
        structure class to manage comunication between a game "referee" and 2 or more player agents
        ideally (but this is not implemented yet) these agents could be run asinchronically
    '''

    def __init__(self, game, players, random_order=True, interactive=None, clear_board=True):
        pl = self.players = list(players)
        self.interactive = any(isinstance(p, IOPlayer) for p in players) if interactive is None else interactive
        self.clear_board = clear_board
        if random_order:
            shuffle(pl)
        self.referee = game

    def simultaneous_turn(self):
        boards = self.referee.get_boards()
        moves = []
        for p, b in zip(self.players, boards):
            for r in b:
                m = p.listener.send(r)  # if input has multiple lines, only the last output is of interest
            moves.append(m)
        # TODO: gestire simultaneita' di esecuzione e valutare timeout
        return self.referee.execute_turn(moves)

    def sequential_turn(self):
        for i, p in enumerate(self.players):
            self.referee.turn_number += 1
            i = i + 1
            board = self.referee.get_board(i)
            match_logger.debug('player %s to move', i)
            if self.interactive:
                if self.clear_board:
                    os.system('clear')
                self.referee.interactive_board()
            for b in board:
                m = p.listener.send(b)  # if input has multiple lines, only the last output is of interest
            # TODO: valutare timeout
            try:
                state = self.referee.execute_turn(i, m)
            except InvalidMove as e:
                match_logger.warn('player %s lost due to invalid move:\n%s', i, e)
                # TODO: questo funziona solo per due giocatori
                state = (i % 2) + 1
            if state != RUNNING:
                # TODO: eventualmente gestire sequential pero' con parita' di turni per la vittoria
                return state
        return state

    def run(self):
        if self.referee.turn_type == SIMULTANEOUS:
            turn = self.simultaneous_turn
        elif self.referee.turn_type == SEQUENTIAL:
            turn = self.sequential_turn
        else:
            raise ValueError('unknown turn type of referee {}: {}', self.referee, self.referee.turn_type)
        boards = self.referee.setup()
        match_logger.info('starting data for player 1:\n%s', '\n'.join(boards[0]))
        for i in range(1, len(self.players)):
            match_logger.debug('starting data for player %s:\n%s', i + 1, '\n'.join(boards[i]))
        for (i, p), b in zip(enumerate(self.players), boards):
            p.setup(i + 1, b)  # TODO: valutare timeout ed eventualmente gestire simultaneita'

        state = RUNNING
        while state == RUNNING:
            self.referee.round_number += 1
            state = turn()
            match_logger.debug('state after turn %s: %s', self.referee.round_number, state)
        match_logger.info('game ending with state: %s', state)
        if self.interactive:
            if self.clear_board:
                os.system('clear')
            self.referee.interactive_board()
        return state
