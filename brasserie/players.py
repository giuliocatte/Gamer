from collections import defaultdict
from itertools import chain
from random import randint, choice

from core.players import RandomPlayer, IOPlayer, Player
from core.main import player_logger

from .referee import CARDS_PER_TURN, AVAILABLE_WCS, ALIVE, LIQUID_TRACK_NAME, PLAYER_TRACKS_NAMES, \
    STARTING_TRACKS_POSITION, PLAYER_TRACKS_EFFECT, RED, YELLOW, COMMON_TRACKS_LENGTH, COMMON_TRACKS_EFFECT, COMMON, \
    REDS_TO_DIE


class BPlayer(Player):

    def __init__(self):
        super().__init__()
        self.players_number = None
        self.players_alive = None
        self.players = None
        self.turn_lines = None
        self.common_tracks = None
        self.available_cards = None

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
        self.common_tracks, self.available_cards = inp[-1].split(' ')

    def compute_available_moves(self):
        vals = tuple(chain((str(v) for v in range(1, CARDS_PER_TURN[self.players_alive] + 1)),
                     ('wc{}'.format(w) for w in AVAILABLE_WCS)))
        free_dices = 2 - (len(self.me[4].split(',')) if self.me[4] else 0)
        if free_dices == 2:
            return ['{} {}'.format(v1, v2) for v1 in vals for v2 in vals if v1 < v2 or v1.startswith('wc')]
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


class HeuristicBPlayer(BPlayer):

    logic = 'avoid_death'

    def compute_move(self):
        return getattr(self, '_logic_' + self.logic)()

    def

    def _compute_worst_common(self):
        actual_common = [int(i) for i in self.common_tracks.split(',')]
        worst_common = [None] * len(actual_common)
        n_reds = 0
        alterations = defaultdict(int)
        for i, (act, w) in enumerate(zip(actual_common, worst_common)):
            # suppongo che non ci siano common tracks che influenzano common tracks
            color = None
            worst = None
            for typ, ind, eff in PLAYER_TRACKS_EFFECT:
                if typ == COMMON and ind == i:
                    for _, var in eff.values():
                        _, affected_p, p_effect = COMMON_TRACKS_EFFECT[i]
                        color, alt = p_effect[act + var]
                        # qui suppongo che tutti i rossi abbiano la stessa penalita'
                        if color == RED:
                            n_reds += 1
                            break
                        elif color == YELLOW:
                            worst = (affected_p, alt)
                            worst_common[i] = (YELLOW, alt)
            if color == RED:  # ho breakato il ciclo interno
                alterations[affected_p] += alt
                break
        else:
            # ho al piu' un giallo
            if color == YELLOW:
                alterations[worst[0]] += worst[1]
        return n_reds, alterations

    def _logic_avoid_death(self):
        '''
            removes nocive moves, random among the others
        '''
        _, _, tracks, _, wc = self.players[self.id]
        tracks = [int(i) for i in tracks.split(',')]
        decent = []
        mvs = self.compute_available_moves()
        n_reds, alterations = self._compute_worst_common()
        for mv in mvs:
            ms = mv.split(' ')
            for m in ms:
                next_pos = ...
                if next_pos_reds + n_reds < REDS_TO_DIE:
                    decent.append(mv)
        if not decent:
            decent = mvs
        return choice(decent)

    def _logic_notsorandom(self):
        '''
            with some randomness, but less stupid than pure random
            aimed to be a decent sparring partner for NN
        '''
        raise NotImplementedError
        # _, _, tracks, _, wc = self.players[self.id]
        # l_ind = PLAYER_TRACKS_NAMES.index(LIQUID_TRACK_NAME)
        # tracks = [int(i) for i in tracks.split(',')]
        # if wc:
        #     # i have a single dice
        # else:
        #     # i have two dices, considering wc
        #     # if liquid track on red, go wc1 if in danger to lose, else 20% wc 1 10% wc 6 70 wc 3
        #     # if liquid track on yellow, wc1 at 20% wc3 at 50%
        #     if tracks[l_ind] > STARTING_TRACKS_POSITION[l_ind]:
        #         liquid_dot = PLAYER_TRACKS_EFFECT[l_ind][2].get(tracks[l_ind], (None, ))
        #         if liquid_dot[0] == RED:
        #             risk = 0
        #             for c, tr in zip(self.common_tracks, COMMON_TRACKS_EFFECT):
        #                 if tr[2].get(min(int(c) + 2, COMMON_TRACKS_LENGTH), (None, ))[0] == RED:
        #                     risk += 1
        #             if randint(1, 100)
        #         elif liquid_dot[0] == YELLOW:


    def _logic_conservative(self):
        '''
            tries to minimize red dots, then yellow dots, then maximize score
            when on yellow goes to bathroom with 3?
        '''
        raise NotImplementedError
