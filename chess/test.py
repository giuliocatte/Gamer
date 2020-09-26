
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
        'values': []
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
