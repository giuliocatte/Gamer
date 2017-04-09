
from core.players import RandomPlayer, IOPlayer, Player, MiniMaxingPlayer
from .referee import Chess, XCOORD, YCOORD, NULLMOVE
#from .nn import get_callable_from_saved_network, DEFAULT_PATH

inf = float('inf')


def get_available_moves_from_game(game, player_id):
    b = game.board
    for starting_tile, target_tile in game.available_moves(player_id):
        m = '{}{}{}{}'.format(XCOORD[starting_tile[0]], YCOORD[starting_tile[1]],
                               XCOORD[target_tile[1]], YCOORD[target_tile[1]])
        if target_tile[1] in (0, 7) and b[starting_tile][-1] == 'P':
            for p in 'rbqn':
                yield m + p
        else:
            yield m


class ChessPlayer(Player):
    turn_lines = 1
    setup_lines = 1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game = Chess()

    def process_turn_input(self, inp):
        inp = inp[0]
        if inp:
            self.game.execute_turn((self.id % 2) + 1, inp)


class IOChessPlayer(IOPlayer, ChessPlayer):

    loud = False

    def setup(self, player_id, inp):
        print('player', player_id, 'your color is', inp)
        return super().setup(player_id, inp)

    def process_turn_input(self, inp):
        if inp[0] != NULLMOVE:
            print('opponent move:', inp[0])
        return super().process_turn_input(inp)

    def compute_move(self):
        raw = super().compute_move()
        # parsing algebraic notation


class RandomChessPlayer(RandomPlayer, ChessPlayer):

    def compute_available_moves(self):
        '''
            each pawn to last row movement accounts for 4 different promotions
            if I really cared about the random player, probably I'd rescale the probabilities
        '''
        return list(get_available_moves_from_game(self.game, self.id))


class MiniMaxingChessPlayer(MiniMaxingPlayer, ChessPlayer):

    search_depth = 4
    value_functions = ['get_board_value']

    def get_board_value(self, node):
        raise NotImplementedError

    @staticmethod
    def child_function(node):
        board = node['board']
        to_move = node['to_move']
        for strmove in get_available_moves_from_game(board, to_move):
            # TODO: probably there's a more performant way
            new_board = board.copy()
            new_board.execute_move(strmove)
            yield {
                'board': new_board,
                'move': strmove,
                'to_move': (to_move % 2) + 1
            }

    @staticmethod
    def terminal_function(node):
        board = node['board']
        move = node['move']
        if move is None:
            # state of the board BEFORE the move
            return False
        return board.check_checkmate(player_id=(node['to_move'] % 2) + 1) or board.check_draw()


class TensorFlowChessPlayer(ChessPlayer):
    '''
    '''
    saved_nn_path = 'p'#DEFAULT_PATH

    def setup(self, player_id, inp):
        raise NotImplementedError
        # super().setup(player_id, inp)
        # self.nn = get_callable_from_saved_network(self.saved_nn_path)

    def process_turn_input(self, inp):
        raise NotImplementedError

    def compute_move(self):
        raise NotImplementedError
        # outp = self.nn(self.network_input)
        # player_logger.info('nn output: %s', outp)
        # move = max((el, i) for i, el in enumerate(outp) if i in self.available_moves)[1]
        # return str(move + 1)
