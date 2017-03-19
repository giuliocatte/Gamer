import logging
from random import shuffle

match_logger = logging.getLogger('gamer.match')
ref_logger = logging.getLogger('gamer.referee')
player_logger = logging.getLogger('gamer.player')
# loggo a livello info lo sviluppo della partita

# TODO: valutare se non usare numeri negativi per far partire player_id da 0
RUNNING = 0
DRAW = -1


class InvalidMove(Exception):
    pass


class Game:

    def __init__(self, referee_class):
        self.referee_class = referee_class


class SimultanousGame(Game):

    def turn(self, referee, players):
        boards = referee.get_boards()
        moves = []
        for p, b in zip(players, boards):
            for r in b:
                m = p.listener.send(r)  # se l'input ha valori multipli mi interessa solo l'ultimo output
            moves.append(m)
        # TODO: gestire simultaneita' di esecuzione e valutare timeout
        return referee.execute_turn(moves)


class SequentialGame(Game):

    def turn(self, referee, players):
        for i, p in enumerate(players):
            i = i + 1
            board = referee.get_board(i)
            match_logger.debug('player %s to move', i)
            for b in board:
                m = p.listener.send(b)  # se l'input ha valori multipli mi interessa solo l'ultimo output
            # TODO: valutare timeout
            try:
                state = referee.execute_turn(i, m)
            except InvalidMove as e:
                match_logger.warn('player %s lost due to invalid move:\n%s', i, e)
                # TODO: questo funziona solo per due giocatori
                state = (i % 2) + 1
            if state != RUNNING:
                # TODO: eventualmente gestire sequential pero' con parita' di turni per la vittoria
                return state
        return state


class Referee:

    def __init__(self, players=2, random_seed=None):
        self.players_number = players
        self.random_seed = random_seed
        self.round_number = 0

    def setup(self):
        '''
            generates the starting game data for each player as a list
        '''
        return self.get_boards()

    def get_board(self, player_id):
        '''
            returns the current board info for player "player_id"
        '''
        return NotImplemented

    def get_boards(self):
        '''
            commodity: returns the current boards for each player, as a list
        '''
        return [self.get_board(i + 1) for i in range(self.players_number)]


class SequentialGameReferee(Referee):

    def execute_turn(self, player_id, move):
        '''
            move is a single move for player "player_id"
            returns a exit code:
            0 game still running
            n > 0 id of the winner
            -1 game draw
        '''
        return NotImplemented


class SimultanousGameReferee(Referee):

    def execute_turn(self, moves):
        '''
            moves is a list of moves for each player
            returns a exit code:
            0 game still running
            n > 0 id of the winner
            -1 game draw
        '''
        return NotImplemented


class Match:

    def __init__(self, game, players, random_order=True):
        self.turn_number = 0
        self.sub_turn_number = 0
        self.game = game
        pl = self.players = list(players)
        if random_order:
            shuffle(pl)
        self.referee = game.referee_class(pl)

    def run(self):
        boards = self.referee.setup()
        match_logger.info('starting data for player 1:\n%s', '\n'.join(boards[0]))
        for i in range(1, len(self.players)):
            match_logger.debug('starting data for player %s:\n%s', i + 1, '\n'.join(boards[i]))
        for (i, p), b in zip(enumerate(self.players), boards):
            p.setup(i + 1, b)  # TODO: valutare timeout ed eventualmente gestire simultaneita'

        state = RUNNING
        while state == RUNNING:
            state = self.game.turn(self.referee, self.players)
            match_logger.debug('state after turn %s: %s', self.referee.round_number, state)
        match_logger.info('game ending with state: %s', state)
        return state

