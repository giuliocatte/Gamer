from itertools import chain

from core.players import RandomPlayer, IOPlayer, Player
from core.main import player_logger

from .referee import CARDS_PER_TURN, AVAILABLE_WCS, ALIVE


class BPlayer(Player):

    def __init__(self):
        super().__init__()
        self.players_number = None
        self.players_alive = None
        self.players = None
        self.turn_lines = None

    @property
    def me(self):
        return self.players[self.id - 1]

    def setup(self, player_id, inp):
        n = int(inp[0])
        self.players_number = n
        self.turn_lines = n + 1
        super().setup(player_id, inp)

    def process_turn_input(self, inp):
        self.players_alive = 0
        pl = self.players = []
        for i, p in zip(range(self.players_number), inp):
            p = p.split(' ')
            pl.append(p)
            if p[0] == ALIVE:
                self.players_alive += 1

    def compute_available_moves(self):
        vals = tuple(chain((str(v) for v in range(1, CARDS_PER_TURN[self.players_alive] + 1)),
                     ('wc{}'.format(w) for w in AVAILABLE_WCS)))
        free_dices = 2 - (len(self.me[4].split(',')) if self.me[4] else 0)
        if free_dices == 2:
            return ['{} {}'.format(v1, v2) for v1 in vals for v2 in vals if v1 != v2 or v1.startswith('wc')]
        elif free_dices == 1:
            return vals
        else:
            return ['']


class IOBPlayer(BPlayer, IOPlayer):
    loud = False

    def compute_move(self):
        moveset = self.compute_available_moves()
        while True:
            mv = super().compute_move()
            if mv in moveset:
                return mv
            print('invalid move, try again:')


class RandomBPlayer(BPlayer, RandomPlayer):
    pass
