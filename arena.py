
import logging
from collections import defaultdict

import fire
import sys

logging.basicConfig(format='%(asctime)s:%(name)s:%(levelname)s %(message)s', level=logging.WARN)
from core.main import match_logger, player_logger, ref_logger, Match, DRAW

from connectfour.referee import ConnectFour
from connectfour.players import MiniMaxingCFPlayer, TensorFlowCFPlayer, RandomCFPlayer
from tictactoe.referee import TicTacToe
from tictactoe.players import MiniMaxingTTTPlayer, TensorFlowTTTPlayer


GAMES = {
    'c4': ConnectFour,
    'ttt': TicTacToe,
}

PLAYERS = {
    'c4': {
        'mini2': MiniMaxingCFPlayer(search_depth=2),
        'mini3': MiniMaxingCFPlayer(search_depth=3),
        'mini4': MiniMaxingCFPlayer(search_depth=4),
        'mini5': MiniMaxingCFPlayer(search_depth=5),
        'neural': TensorFlowCFPlayer(),
        'random': RandomCFPlayer()
    },
    'ttt': {
        'mini': MiniMaxingTTTPlayer(),
        'neural': TensorFlowTTTPlayer()
    }
}



class Arena:

    def __init__(self, game, *players):
        self.game_class = GAMES[game]
        self.players = [PLAYERS[game][p] for p in players]

    def challenge(self, games=100):
        '''
            plays several games between given players, reporting results
        '''
        outcomes = defaultdict(int)
        print('running: {:>3}%'.format(0), end='')
        phase = None
        for i in range(1, games + 1):
            match = Match(game=self.game_class(), players=self.players)
            outcome = match.run()
            if outcome == DRAW:
                outcomes['draws'] += 1
            else:
                outcomes[str(match.players[outcome - 1]) + ' victories'] += 1
            for p in self.players:
                p.reset()
            p = int(i / games * 100)
            if p != phase:
                phase = p
                print('\b\b\b\b{:>3}%'.format(phase), end='')
                sys.stdout.flush()
        print()
        print(games, 'games played:')
        for outcome, n in sorted(outcomes.items()):
            print('{:>6.1%}'.format(n / games), outcome)

    def explain(self):
        '''
            play a single game between players,
            logging estensively to understand player choices
        '''
        match_logger.setLevel(logging.INFO)
        player_logger.setLevel(logging.DEBUG)
        ref_logger.setLevel(logging.DEBUG)
        match = Match(game=self.game_class(), players=self.players, interactive=True, clear_board=False)
        outcome = match.run()
        print(str(match.players[outcome - 1]) + ' wins')


if __name__ == '__main__':
    fire.Fire(Arena)

