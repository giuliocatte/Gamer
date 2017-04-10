
from .players import IOChessPlayer, RandomChessPlayer, MiniMaxingChessPlayer
from .referee import Chess

IOPLAYER_CLASS = IOChessPlayer

REFEREE_CLASS = Chess


AIS = [{
    'caption': 'minimax',
    'class': MiniMaxingChessPlayer,
    'options': [{
        'name': 'search_depth',
        'caption': 'search depth',
        'default': 4,
        'values': [
            '',
            'picks immediate best move',
            'considers also your next move',
            'plans two moves ahead',
            'plans three moves ahead',
            'plans four moves ahead',
            '...'
        ]
    }]
}, {
    'caption': 'random',
    'class': RandomChessPlayer,
    'options': []
# }, {
#     'caption': 'neural network',
#     'class': TensorFlowChessPlayer,
#     'options': []
}]
