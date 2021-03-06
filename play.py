
import logging
import fire

logging.basicConfig(format='%(asctime)s:%(name)s:%(levelname)s %(message)s', level=logging.WARN)
from core.main import match_logger, player_logger, ref_logger, Match, DRAW

match_logger.setLevel(logging.WARN)
player_logger.setLevel(logging.WARN)
ref_logger.setLevel(logging.INFO)


def test_game(mod, ai_number=1, **kwargs):
    ais = []
    for n in range(ai_number):
        print('choose AI for player {}:'.format(n+2))
        for i, ai in enumerate(mod.AIS):
            print('{}. {}{}'.format(i, ai['caption'], ' (default)' if not i else ''))
        ai = mod.AIS[int(input() or 0)]
        kw = {}
        for opt in ai['options']:
            print('enter {}:'.format(opt['caption']))
            for i, ov in enumerate(opt['values']):
                if ov:
                    print('{}. {}{}'.format(i, ov, ' (default)' if i == opt['default'] else ''))
            v = input()
            kw[opt['name']] = int(v or opt['default'])
        ais.append((ai, kw))
    if ai_number == 1:    
        print('pick player order?')
        print('0. random (default)')
        print('1. go first')
        print('2. go second')
        ord = int(input() or 0)
    else:
        ord = 0
    players = [
        mod.IOPLAYER_CLASS(),
        *(ai['class'](**kw) for ai, kw in ais)
    ]
    if ord:
        rand = False
        if ord == 2:
            players.reverse()
    else:
        rand = True

    g = mod.REFEREE_CLASS(players_number=ai_number + 1)
    match = Match(game=g, players=players, random_order=rand, **kwargs)
    outcome = match.run()
    if outcome == DRAW:
        print('Draw!')
    else:
        print('player {} wins!'.format(outcome))


class Play:

    def __init__(self, p_log='WARN', r_log='WARN', m_log='WARN'):
        match_logger.setLevel(getattr(logging, m_log))
        player_logger.setLevel(getattr(logging, p_log))
        ref_logger.setLevel(getattr(logging, r_log))

    def chess(self, **kwargs):
        import chess.test as mod
        test_game(mod, **kwargs)

    def ttt(self, **kwargs):
        ''' plays a game of tic tac toe
        '''
        import tictactoe.test as mod
        test_game(mod, **kwargs)

    def c4(self, **kwargs):
        ''' plays a game of connect4
        '''
        import connectfour.test as mod
        test_game(mod, **kwargs)
    
    def brasserie(self, **kwargs):
        ''' plays a game of Brasserie
        '''
        print('choose verbosity level: 1 minimum, 2 verbose (default), 3 every log possible')
        verb = int(input() or 2)
        if verb >= 2:
            kwargs['clear_board'] = False
            ref_logger.setLevel(logging.DEBUG)
            if verb == 3:
                player_logger.setLevel(logging.DEBUG)
                match_logger.setLevel(logging.DEBUG)

        import brasserie.test as mod
        print('choose number of opponents: (default 2)')
        ais = int(input() or 2)
        test_game(mod, ais, **kwargs)


if __name__ == '__main__':
    fire.Fire(Play)

