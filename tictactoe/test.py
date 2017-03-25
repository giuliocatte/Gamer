
from .players import RandomTTTPlayer, MiniMaxingTTTPlayer, TensorFlowTTTPlayer, IOTTTPlayer
from .referee import TicTacToe


REFEREE_CLASS = TicTacToe

IOPLAYER_CLASS = IOTTTPlayer


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
