import random
from datetime import datetime
from itertools import cycle
from functools import partial

import numpy as np
import tensorflow as tf

try:
    from core.nn_trainer import train_policy_gradients
    from core.nn import load_network, create_network
except ImportError:
    # executing as __main__
    import os
    import sys
    currentdir = os.path.dirname(os.path.abspath(__file__))
    parentdir = os.path.dirname(currentdir)
    sys.path.append(parentdir)
    from core.nn import load_network, create_network
    from core.nn_trainer import train_policy_gradients

from connectfour.referee import check_victory, ConnectFour

DEFAULT_PATH = 'connectfour/current_network.p'
HIDDEN_LAYERS = (100, 100, 100)


def get_callable_from_saved_network(file_path=DEFAULT_PATH):
    session = tf.Session()  # here the session isn't closed. Will it be a problem?
    session.run(tf.initialize_all_variables())

    input_layer, output_layer, variables = create_network(input_nodes=42, hidden_nodes=HIDDEN_LAYERS, output_nodes=7)
    load_network(session, variables, file_path)

    def cal(board):
        return session.run(output_layer, feed_dict={input_layer: np.array(board).reshape(1, 42)})[0]

    return cal


std_ref = ConnectFour()  # just for board printing


def play_c4_game(mover1, mover2, debug=False):
    '''
        i flatten the board in a 42-length array
        each mover assumes to be player 1, so I have to flip board
    '''
    board = np.array([0] * 42)
    for plid, mover in cycle(zip((1, -1), (mover1, mover2))):
        move = mover(board * plid, plid)
        board = board.reshape(7, 6)
        if debug:
            print('player', plid, 'to move; board:')
            std_ref.board = [[(c + 3) % 3 if c else 0 for c in row] for row in board]
            std_ref.interactive_board()
            print('player', plid, 'executed move', move)
        if board[move][-1]:
            if debug:
                print('player', plid, 'failed due to invalid move')
            return -plid  # fail due to invalid move
        rowind = list(board[move]).index(0)

        board[move][rowind] = plid
        if check_victory(board.tolist(), move):
            if debug:
                print('player', plid, 'won')
            return plid  # won
        if board.all():
            if debug:
                print('it\'s a draw')
            return 0  # draw
        board = board.flatten()


def random_mover(board, plid):
    valid = [i for i in range(7) if not board[(i + 1) * 6 - 1]]
    return random.choice(valid)


def train_c4_policy_gradient(opponent_func, number_of_games, trainer, batch_size=100, print_results_every=1000):
    return train_policy_gradients({'input_nodes': 42, 'hidden_nodes': HIDDEN_LAYERS, 'output_nodes': 7},
                                  (None, 7), trainer.game_func, opponent_func=opponent_func, nn_path=trainer.nn_path,
                                  batch_size=batch_size, nn_write_path=trainer.nn_write_path,
                                  number_of_games=number_of_games,
                                  print_results_every=min(print_results_every, number_of_games),
                                  log_games=trainer.debug)


class Trainer:

    game_func = staticmethod(play_c4_game)
    debug = False

    def __init__(self, path=DEFAULT_PATH, mode='a'):
        '''
        :param path: path where to save the neural network
        :param mode: 'a' to append (train further an already existing network) 'w' to overwrite
        :return:
        '''
        if mode == 'a':
            self.nn_path = path
            self.nn_write_path = None
        elif mode == 'w':
            self.nn_path = None
            self.nn_write_path = path
        else:
            raise ValueError('unsupported mode {}'.format(mode))

    def debug_minimax(self, number_of_games=10, **kwargs):
        self.debug = True
        self.game_func = partial(play_c4_game, debug=True)
        self.train_with_minimax(number_of_games=number_of_games, **kwargs)

    def train_with_minimax(self, number_of_games=1000000, search_depth=2, **kwargs):
        from connectfour.players import MiniMaxingCFPlayer

        def oppo(board, pid):
            '''
                converts nn-like I/O in the connectfour.referee.ConnectFour API
            '''
            p.board = board.reshape(7, 6).tolist()
            m = p.compute_move()
            return int(m) - 1

        print('start', datetime.now())
        p = MiniMaxingCFPlayer(search_depth=search_depth)
        p.setup(1, ['YELLOW'])  # that input isn't useful, but calling setup is
        # player id is always 1, because the board is flipped by the referee

        train_c4_policy_gradient(oppo, number_of_games, self, **kwargs)
        print('end', datetime.now())

    def train_with_random(self):
        train_c4_policy_gradient(random_mover, 500000, self)


if __name__ == '__main__':
    import fire
    fire.Fire(Trainer)
