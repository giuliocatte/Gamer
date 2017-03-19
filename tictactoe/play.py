
from core.main import Match, SequentialGame, DRAW
from .referee import TicTacToe
from .players import RandomTTTPlayer, IOTTTPlayer, MiniMaxingTTTPlayer


# TODO: unire referee a game? gestire tutto in una sottoclasse di match?


AIS = [{
    'caption': 'minimax',
    'class': MiniMaxingTTTPlayer,
    'options': [{
        'name': 'search_depth',
        'caption': 'search depth',
        'default': 2,
        'values': [
            'dumb',
            'picks immediate best move',
            'considers also your next move',
            'plans two moves ahead',
            '...'
        ]}, {
        'name': 'evaluation_level',
        'caption': 'evaluation level',
        'default': 0,
        'values': [
            'only considers winning moves',
            'considers center occupation',
            'some overkill heuristics'
        ]}]
}, {
    'caption': 'random',
    'class': RandomTTTPlayer,
    'options': []
}]


def test_game():
    print('choose AI:')
    for i, ai in enumerate(AIS):
        print('{}. {}'.format(i, ai['caption']))
    ai = AIS[int(input() or 0)]
    kw = {}
    for opt in ai['options']:
        print('enter {}:'.format(opt['caption']))
        for i, ov in enumerate(opt['values']):
            print('{}. {}{}'.format(i, ov, ' (default)' if i == opt['default'] else ''))
        v = input()
        kw[opt['name']] = int(v or opt['default'])

    match = Match(SequentialGame(referee_class=TicTacToe), players=[
            IOTTTPlayer(),
            ai['class'](**kw)
    ])
    outcome = match.run()
    if outcome == DRAW:
        print('Draw!')
    else:
        print('player {} wins!'.format(outcome))
