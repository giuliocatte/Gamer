
import logging
import fire

logging.basicConfig(format='%(asctime)s:%(name)s:%(levelname)s %(message)s', level=logging.WARN)
from core.main import match_logger, player_logger, ref_logger, Match, DRAW

match_logger.setLevel(logging.WARN)
player_logger.setLevel(logging.WARN)
ref_logger.setLevel(logging.WARN)


def test_game(mod):
    print('choose AI:')
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
    print('pick player order?')
    print('0. random (default)')
    print('1. go first')
    print('2. go second')
    ord = int(input() or 0)
    players = [
        mod.IOPLAYER_CLASS(),
        ai['class'](**kw)
    ]
    if ord:
        rand = False
        if ord == 2:
            players.reverse()
    else:
        rand = True

    match = Match(game=mod.REFEREE_CLASS(), players=players, random_order=rand)
    outcome = match.run()
    if outcome == DRAW:
        print('Draw!')
    else:
        print('player {} wins!'.format(outcome))


class Play:

    def ttt(self):
        ''' plays a game of tic tac toe
        '''
        import tictactoe.test as mod
        test_game(mod)

    def c4(self):
        ''' plays a game of connect4
        '''
        import connectfour.test as mod
        test_game(mod)


if __name__ == '__main__':
    fire.Fire(Play)

