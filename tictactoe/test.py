
from core.main import Match, SequentialGame, DRAW
from .referee import TicTacToe
from .players import RandomTTTPlayer, IOTTTPlayer, MiniMaxingTTTPlayer, TensorFlowTTTPlayer


# TODO: unire referee a game? gestire tutto in una sottoclasse di match?


AIS = [{
    'caption': 'neural network',
    'class': TensorFlowTTTPlayer,
    'options': []
}, {
    'caption': 'minimax',
    'class': MiniMaxingTTTPlayer,
    'options': [{
        'name': 'search_depth',
        'caption': 'search depth',
        'default': 2,
        'values': [
            '',
            'picks immediate best move',
            'considers also your next move',
            'plans two moves ahead',
            '...'
        ]}, {
        'name': 'evaluation_level',
        'caption': 'evaluation level',
        'default': 2,
        'values': [
            'only considers winning moves',
            'will try to get center',
            'will try to build partial lines'
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
#            TensorFlowTTTPlayer(),
            IOTTTPlayer(),
            ai['class'](**kw)
    ]
    if ord:
        rand = False
        if ord == 2:
            players.reverse()
    else:
        rand = True

    match = Match(SequentialGame(referee_class=TicTacToe), players=players, random_order=rand)
    outcome = match.run()
    if outcome == DRAW:
        print('Draw!')
    else:
        print('player {} wins!'.format(outcome))
