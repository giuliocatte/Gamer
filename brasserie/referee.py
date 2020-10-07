from random import shuffle
from core.main import SimultanousGame, InvalidMove, DRAW, RUNNING, ref_logger
from core.lib import maximizer
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
from math import floor

RED = 'RED'
YELLOW = 'YELLOW'
PLAYER = 3
COMMON = 4
ALIVE = 'ALIVE'
DEAD = 'DEAD'

PLAYER_TRACKS_NAMES = ('social', 'liquid', 'heart')
PLAYER_TRACKS_LENGTH = (7, 7, 7)
PLAYER_TRACKS_EFFECT = (
    # (kind of track, index of track, {position: (dot color, modifier)})
    (COMMON, 1, {0: (RED, 2), 1: (YELLOW, 1), 2: (YELLOW, 1), 6: (RED, 2)}),
    (COMMON, 0, {0: (RED, 2), 4: (YELLOW, 1), 5: (YELLOW, 1), 6: (RED, 2)}),
    (PLAYER, 0, {0: (RED, -2), 1: (RED, -2), 2: (YELLOW, -1), 5: (YELLOW, -1), 6: (RED, -2)}),
)
STARTING_TRACKS_POSITION = (4, 2, 3)
COMMON_TRACKS_NAMES = ('noise', 'cash')
COMMON_TRACKS_EFFECT = (
    # (kind of track, index of track, {position: (dot color, modifier)})
    (PLAYER, 2, {3: (YELLOW, 1), 4: (YELLOW, 1), 5: (YELLOW, 1), 6: (RED, 2)}),
    (PLAYER, 2, {1: (YELLOW, 1), 2: (YELLOW, 1), 5: (YELLOW, 1), 6: (RED, 2)}),
)
COMMON_TRACKS_LENGTH = (7, 7)
DECK = [  # type, name, points, tracks modifiers
    ("Bibite", "Cola", 0, (0, 2, -3)),
    ("Bibite", "Acqua", 0, (0, 1, -2)),
    ("Bibite", "La Bionda", 2, (0, 2, -2)),
    ("Bibite", "La Rossa", 2, (0, 2, -1)),
    ("Bibite", "La Scura", 3, (0, 3, -1)),
    ("Main", "Galletto arrosto", 2, (1, 0, 1)),
    ("Main", "Crocchette di pollo", 3, (1, 0, 3)),
    ("Main", "La Salsiccia", 5, (-2, 0, 2)),
    ("Main", "Filetto", 5, (-1, 0, 2)),
    ("Main", "Hamburgherino", 6, (-2, 0, 3)),
    ("Contorni", "Insalatina", 1, (-2, 0, -2)),
    ("Contorni", "Le Patas", 1, (2, 0, 1)),
    ("Contorni", "Le Sfiziose", 1, (3, 0, 2)),
    ("Contorni", "Olive all'ascolana", 2, (2, 0, 1)),
    ("Contorni", "Anelli di cipolla", 3, (-2, 0, 1)),
    ("Main", "Crudo e mozzarella", 1, (1, 0, 1)),
    ("Main", "Vegetariano", 4, (-2, 0, 1)),
    ("Main", "Cotto e funghi", 4, (-1, 0, 2)),
    ("Main", "Speck e brie", 5, (-1, 0, 3)),
    ("Main", "Porchetta", 7, (-2, 0, 4)),
    ("Bibite",	"La Belga",	2, (	0,	1,	-1)),
    ("Bibite",	"La Bianca",	1, (	0,	1,	-2)),
    ("Bibite",	"Gazosa",	1, (	1,	2,	-2)),
    ("Bibite",	"Acqua gasata",	0, (	0,	1,	-3)),
    ("Dolce",	"Palline di crema",	1, (	1,	0,	1)),
    ("Dolce",	"Salame dolce",	1, (	2,	0,	2)),
    ("Dolce",	"Profitterol",	3, (	1,	0,	2)),
    ("Dolce",	"Sacher torta",	4, (	2,	0,	4)),
    ("Dolce",	"Tiramisu",	4, (	2,	0,	3)),
    ("Dolce",	"Limone transgenico",	2, (	2,	1,	0)),
    ("Main",	"Tagliere di salumi",	1, (	0,	-2,	1)),
    ("Contorni",	"Verdure grigliate",	3, (	-2,	0,	0))
]
CARDS_PER_TURN = {2: 4, 3: 5, 4: 6}
POINTS_FOR_CARD_SET = {2: 3, 3: 6, 4: 10}
AVAILABLE_WCS = (1, 3, 6)
WC_WAIT = {1: 1, 3: 2, 6: 3}
LIQUID_TRACK_NAME = 'liquid'
NOISE_TRACK_NAME = 'noise'
SOCIAL_TRACK_NAME = 'social'
CASH_TRACK_NAME = 'cash'
REDS_TO_DIE = 3


class Brasserie(SimultanousGame):
    '''
        board is a composed of two elements:
        1) a list of players, each of them has status, points, track values, cards, wc_dice
            status is ALIVE or DEAD
            points is an integer
            the values are integers from 0 to PLAYER_TRACKS_LENGTH[i] - 1,
            cards is a list of indices in DECK
            wc_dices is a list of (power, wait) each element is a dice;
                power is liquid reduction (int),
                wait is number of turns
        2) the common board status, made of (track_1_value, track_2_value, cards_on_the_table)
        each player is given the same board, since every info is public
        internally, there is also the deck, composed of the cards yet to draw, and the discard pile
    '''
    def __init__(self, players_number: int, random_seed=None):
        super().__init__(players_number=players_number, random_seed=random_seed)
        d = list(range(len(DECK)))
        shuffle(d)
        self.deck = d
        self.discard_pile = []
        self.players = [{
                'status': ALIVE,
                'points': 0,
                'tracks': list(STARTING_TRACKS_POSITION),
                'cards': [],
                'wc_dices': []
        } for _ in range(players_number)]
        self.common_tracks = [0 for _ in COMMON_TRACKS_NAMES]
        self.cards_on_the_table = []
        self._draw()

    @property
    def players_alive(self):
        return sum(1 for p in self.players if p['status'] == 'ALIVE')

    def _draw(self):
        del self.cards_on_the_table[:]
        deck = self.deck
        disc = self.discard_pile
        for c in range(CARDS_PER_TURN[self.players_alive]):
            if not deck:
                if not disc:
                    raise RuntimeError('unprecedented end of the cards in the deck!')
                deck.extend(disc)
                del disc[:]
                shuffle(deck)
            self.cards_on_the_table.append(deck.pop())

    def setup(self):
        ref_logger.info('starting game')
        p = len(self.players)
        return [[str(p)] for _ in range(p)]

    def get_board(self, player_id):
        b = ['{s} {p} {t} {c} {wc}'.format(
                s=p['status'],
                p=p['points'],
                t=','.join(str(t) for t in p['tracks']),
                c=','.join(str(c) for c in p['cards']),
                wc=','.join('{}:{}'.format(*d) for d in p['wc_dices'])
            ) for p in self.players]
        b.append('{t} {c}'.format(
                t=','.join(str(t) for t in self.common_tracks),
                c=','.join(str(c) for c in self.cards_on_the_table)       
        ))
        return b

    @staticmethod
    def _send_to_wc(plid, player, power):
        ref_logger.debug('player %s sent a dice on wc for %s turns', plid, WC_WAIT[power])
        player['wc_dices'].append([power, WC_WAIT[power]])

    def _shift_wc(self):
        '''
            scrolls every waiting player in the wc
        '''
        l_ind = PLAYER_TRACKS_NAMES.index(LIQUID_TRACK_NAME)
        for i, p in enumerate(self.players):
            to_remove = []
            if p['status'] == DEAD:
                continue
            for j, d in enumerate(p['wc_dices']):
                if d[1] == 1:
                    q = min(d[0], p['tracks'][l_ind])
                    p['tracks'][l_ind] -= q
                    to_remove.append(j)
                    ref_logger.info('a dice for player %s reaches wc, %s liquid removed. current liquid: %s',
                                    i + 1, q, p['tracks'][l_ind])
                else:
                    d[1] -= 1
            while to_remove:
                j = to_remove.pop()
                p['wc_dices'].pop(j)

    def _activate_effects(self):
        '''
            activates side effects of each track
        '''
        s_ind = PLAYER_TRACKS_NAMES.index(SOCIAL_TRACK_NAME)
        for i, (tname, (typ, ind, track)) in enumerate(zip(COMMON_TRACKS_NAMES, COMMON_TRACKS_EFFECT)):
            e = track.get(self.common_tracks[i])
            if not e:
                continue
            trackmax = PLAYER_TRACKS_LENGTH[ind] - 1
            alive = [p for p in self.players if p['status'] == ALIVE]
            if tname == CASH_TRACK_NAME:
                affected = maximizer((lambda p: -p['tracks'][s_ind]), alive, multiple=True)
            else:
                affected = alive
            for p in affected:
                # truncating value between 0 and track max
                currval = p['tracks'][ind]
                p['tracks'][ind] += max(min(e[1], trackmax - currval), -currval)

        for i, (typ, ind, track) in enumerate(PLAYER_TRACKS_EFFECT):
            if typ == PLAYER:
                trackmax = PLAYER_TRACKS_LENGTH[ind] - 1
                for pi, p in enumerate(self.players):
                    if p['status'] == DEAD:
                        continue
                    e = track.get(p['tracks'][i])
                    if e:
                        ref_logger.debug('player %s has track %s on color %s: modifier %s %s',
                                         pi + 1, PLAYER_TRACKS_NAMES[i], e[0], PLAYER_TRACKS_NAMES[ind], e[1])
                        currval = p['tracks'][ind]
                        p['tracks'][ind] += max(min(e[1], trackmax - currval), -currval)
            else:
                trackmax = COMMON_TRACKS_LENGTH[ind] - 1
                top_modifier = 0
                for pi, p in enumerate(self.players):
                    if p['status'] == DEAD:
                        continue
                    e = track.get(p['tracks'][i])
                    if e:
                        ref_logger.debug('player %s has track %s on color %s: modifier %s %s',
                                         pi + 1, PLAYER_TRACKS_NAMES[i], e[0], COMMON_TRACKS_NAMES[ind], e[1])
                        if abs(e[1]) > abs(top_modifier):
                            top_modifier = e[1]
                if top_modifier:
                    currval = self.common_tracks[ind]
                    self.common_tracks[ind] += max(min(top_modifier, trackmax - currval), -currval)
                    ref_logger.debug('highest modifier for track %s: %s. modified %s: %s',
                                     PLAYER_TRACKS_NAMES[i], top_modifier, COMMON_TRACKS_NAMES[ind],
                                     self.common_tracks[ind])

    def _check_deaths(self):
        '''
            set players status to DEAD if it is time
        '''
        g_reds = 0
        n_ind = COMMON_TRACKS_NAMES.index(NOISE_TRACK_NAME)
        s_ind = PLAYER_TRACKS_NAMES.index(SOCIAL_TRACK_NAME)
        c_ind = COMMON_TRACKS_NAMES.index(CASH_TRACK_NAME)
        if COMMON_TRACKS_EFFECT[n_ind][2].get(self.common_tracks[n_ind], (None,))[0] == RED:
            g_reds += 1
            ref_logger.debug('a red for everyone, noise is high')
        for i, p in enumerate(self.players):
            if p['status'] == DEAD:
                continue
            p_reds = sum(1 for v, (_, _, e) in zip(p['tracks'], PLAYER_TRACKS_EFFECT) if e.get(v, (None,))[0] == RED)
            ref_logger.debug('player %s has %s red dots', i + 1, p_reds)
            if COMMON_TRACKS_EFFECT[c_ind][2].get(self.common_tracks[c_ind], (None,))[0] == RED:
                social_value = p['tracks'][s_ind]
                for j, p2 in enumerate(self.players):
                    if j != i and p2['status'] == ALIVE and p2['tracks'][s_ind] < social_value:
                        break
                else:
                    ref_logger.debug('plus the cash one, because it\'s the worst')
                    p_reds += 1
            if p_reds >= REDS_TO_DIE:
                ref_logger.info('player %s dies with %s red dots', i + 1, p_reds)
                p['status'] = DEAD

    @staticmethod
    def _compute_cards_points(cards):
        sets = []
        for c in cards:
            t = DECK[c][0]
            for s in sets:
                if t not in s:
                    s.append(t)
                    break
            else:
                sets.append([t])
        return sum(POINTS_FOR_CARD_SET.get(len(s), 0) for s in sets)

    def _compute_winner(self, use_cards=True, player_filter=None):
        maxpoints = 0
        top_players = []
        player_filter = player_filter or set(range(self.players_number))
        for i, p in enumerate(self.players):
            if i not in player_filter:
                continue
            if use_cards:
                c = self._compute_cards_points(p['cards'])
                pt = p['points'] + c
                ref_logger.info('player %s got %s points (%s from cards)', i + 1, pt, c)
            else:
                pt = p['points']
                ref_logger.info('at tie-breaker player %s got %s points', i + 1, pt)
            if pt > maxpoints:
                maxpoints = pt
                top_players = [i]
            elif pt == maxpoints:
                top_players.append(i)
        if len(top_players) == 1:
            return top_players[0] + 1  # winning player count goes from 1: 0 is "no winner"
        if not use_cards:
            ref_logger.error('players %s are tied with and witout cards, returing draw', [pi + 1 for pi in top_players])
            return DRAW
        return self._compute_winner(use_cards=False)

    def execute_turn(self, moves):
        '''
           each move is two values separed by space.
           each of them is either an int between 1 and 6, or wc{n} with n in AVAILABLE_WCS
        '''
        wcs = tuple('wc{}'.format(n) for n in AVAILABLE_WCS)
        cards = [DECK[c] for c in self.cards_on_the_table]
        dices = [[] for _ in cards]
        ref_logger.info('received moves %s', moves)
        for i, (m, p) in enumerate(zip(moves, self.players)):
            pl = i + 1
            if p['status'] == DEAD:
                ref_logger.debug('player %s is DEAD, ignoring input', pl)
            expected_values = 2 - len(p['wc_dices'])
            values = [v for v in m.split(' ') if v]
            if (l := len(values)) != expected_values:
                raise InvalidMove('expected {} values, got {}'.format(expected_values, l))
            modifiers = [0] * len(PLAYER_TRACKS_NAMES)
            for v in values:
                if v in wcs:
                    self._send_to_wc(pl, p, int(v[-1]))
                elif not v.isdigit():
                    raise InvalidMove('unexpected value: {}'.format(v))
                else:
                    v = int(v)
                    if v < 1 or v > 6:
                        raise InvalidMove('numeric value not in range 1-6: {}'.format(v))
                    dices[v - 1].append(i)
                    c = cards[v - 1]
                    p['points'] += c[2]
                    for ind, val in enumerate(c[3]):
                        modifiers[ind] += val
                    ref_logger.debug('player %s puts a dice on card %s, for %s points and modifiers %s',
                                     pl, v, c[2], c[3])
            for tind, mod in enumerate(modifiers):
                trackmax = PLAYER_TRACKS_LENGTH[tind] - 1
                currval = p['tracks'][tind]
                p['tracks'][tind] += max(min(mod, trackmax - currval), -currval)
            ref_logger.debug('player %s modified status: %s', pl, [ti + 1 for ti in p['tracks']])
        for c, d in zip(self.cards_on_the_table, dices):
            if len(d) == 1:
                self.players[d[0]]['cards'].append(c)
                ref_logger.debug('player %s is the only bidder on the card %s, obtains it', d[0] + 1, DECK[c][1])
            else:
                ref_logger.debug('card %s has %s bids, is discarded', DECK[c][1], len(d))
                self.discard_pile.append(c)
        self._shift_wc()
        self._activate_effects()
        self._check_deaths()
        if sum(1 for p in self.players if p['status'] == ALIVE) <= 1:
            return self._compute_winner()
        self._draw()
        return RUNNING

    def interactive_board(self):
        print()
        for i, p in enumerate(self.players):
            print('*** player', i + 1, 'at', p['points'], 'points. Status: ', end='')
            if p['status'] == 'DEAD':
                print('DEAD')
                continue
            print('ALIVE')
            for t, pos in zip(PLAYER_TRACKS_NAMES, p['tracks']):
                print('track', t, 'at position', pos + 1)
            if c := p['cards']:
                print('cards owned:', ', '.join('{d[1]} ({d[0]})'.format(d=DECK[i]) for i in c))
            else:
                print('no cards owned')
            if w := p['wc_dices']:
                for (power, wait) in w:
                    print('a dice with power', power, 'is waiting in wc for', wait, 'turns')
            else:
                print('both dices available')
        print('*** common board status:')
        for t, pos in zip(COMMON_TRACKS_NAMES, self.common_tracks):
            print('track', t, 'at position', pos + 1)
        print('cards on the table:')
        for j, i in enumerate(self.cards_on_the_table):
            d = DECK[i]
            print('{}. {d[1]} ({d[0]}, {d[2]} pts, modifiers: {})'.format(j + 1, ', '.join(
                    '{} {}'.format(v, n) for v, n in zip(d[3], PLAYER_TRACKS_NAMES)), d=d))

        print(len(self.deck), 'cards remaining in deck,', len(self.discard_pile), 'cards in discard pile')


        ## CODICE PER DISPLAY BOARD E PLANCE
        # mancano i dadi al bagno
        
        SIZE = 4.5

        unita_pos_y = np.array([100,200,300,400,500,600,700,800,900,1000]) # cifre da 0 a 9
        decine_pos  = np.array([[0,0],[180,100],[180,200],[180,300],[280,100],[280,200],[280,300]])
        track_pos_y = np.array([530,730,950])
        track_pos_x = np.array([230,350,470,590,710,830,950])
        
        common_track_pos_y = np.array([800,700,590,430,300,190,70])
        common_track_pos_x = np.array([200,900])
        common_track_wc    = np.array([660,410,200])

        # load the image
        b_img = mpimg.imread("./brasserie/BR_board1.jpg")
        p_img = mpimg.imread("./brasserie/BR_plancia1.jpg")

        N_Players = len(self.players)
        plt.close('all')
        fig = plt.figure(num = 1, figsize = [SIZE*N_Players, SIZE])

        for i, p in enumerate(self.players):
            ax = fig.add_subplot(1, N_Players+1, i+1)
            imgplot = plt.imshow(p_img, interpolation="bicubic")
            #plt.xticks([]), plt.yticks([])  # to hide tick values on X and Y axis
            plt.axis("off")
            
            title = 'Player {} - {}'.format(i+1,p['status'])

            if w := p['wc_dices']:
                for (power, wait) in w:
                    #print('a dice with power', power, 'is waiting in wc for', wait, 'turns')
                    title = title + '\nWC {} in {} turns'.format(power,wait)

            ax.set_title(title)

            decine = floor(p['points']/10)
            unita  = p['points'] - decine*10
            plt.scatter(0,unita_pos_y[unita],c='r',s=140,marker='s')
            plt.scatter(decine_pos[decine][0],decine_pos[decine][1],s=140,c='r',marker='s')

            for t, pos in zip(PLAYER_TRACKS_NAMES, p['tracks']):
                #print('track', PLAYER_TRACKS_NAMES.index(t), 'at position', track_pos_x[pos])
                plt.scatter(track_pos_x[pos],track_pos_y[PLAYER_TRACKS_NAMES.index(t)],s=140,c='r')

            

        ax = fig.add_subplot(1, N_Players+1, N_Players+1)
        imgplot = plt.imshow(b_img, interpolation="bicubic")
        #plt.xticks([]), plt.yticks([])  # to hide tick values on X and Y axis
        plt.axis("off")
        ax.set_title('Board')

        for t, pos in zip(COMMON_TRACKS_NAMES, self.common_tracks):
            #print('track', t, 'at position', pos + 1)
            plt.scatter(common_track_pos_x[COMMON_TRACKS_NAMES.index(t)],common_track_pos_y[pos],s=140,c='r')

        fig.tight_layout()
        plt.show(block=False)
        