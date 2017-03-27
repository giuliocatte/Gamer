
from .players import IOCFPlayer, RandomCFPlayer, TensorFlowCFPlayer, MiniMaxingCFPlayer
from .referee import ConnectFour

IOPLAYER_CLASS = IOCFPlayer

REFEREE_CLASS = ConnectFour


AIS = [{
    'caption': 'minimax',
    'class': MiniMaxingCFPlayer,
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
        ]
    }, {
        'name': 'evaluation_level',
        'caption': 'evaluation level',
        'default': 1,
        'values': [
            'only considers winning moves',
            'will try to build and block partial lines'
        ]
    }]
}, {
    'caption': 'random',
    'class': RandomCFPlayer,
    'options': []
}, {
    'caption': 'neural network',
    'class': TensorFlowCFPlayer,
    'options': []
}]
