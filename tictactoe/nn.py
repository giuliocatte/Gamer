import random
from datetime import datetime
from itertools import cycle

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


DEFAULT_PATH = 'current_network.p'
HIDDEN_LAYERS = (100, 100, 100, 100)


def get_callable_from_saved_network(file_path=DEFAULT_PATH):
    session = tf.Session()  # here the session isn't closed. Will it be a problem?
    session.run(tf.initialize_all_variables())

    input_layer, output_layer, variables = create_network(9, hidden_nodes=HIDDEN_LAYERS)
    load_network(session, variables, file_path)

    def cal(board):
        return session.run(output_layer, feed_dict={input_layer: np.array(board).reshape(1, 9)})[0]

    return cal


_lines = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 3, 6], [1, 4, 7], [2, 5, 8], [0, 4, 8], [2, 4, 6]]


def play_ttt_game(mover1, mover2):
    '''
        gioca un'intera partita fra il mover1 e il mover2
        ritorna 1 se vince mover1, -1 se vince mover2, 0 se e' un pareggio

        NON usa le regole del gioco normale, ma una versione ermetica
        le mosse sono numeri da 0 a 8, il board viene passato ai mover come una lista di 9 elementi
    '''
    board = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    for plid, mover in cycle(zip((1, -1), (mover1, mover2))):
        move = mover(board, plid)
        if board[move]:
            return -plid  # fail due to invalid move
        board[move] = plid
        if any(all(board[l] == plid for l in line) for line in _lines):
            return plid  # won
        if all(board):
            return 0  # draw


def random_mover(board, pid):
    valid = [i for i in range(9) if not board[i]]
    return random.choice(valid)


def train_ttt_policy_gradient(opponent_func, number_of_games, nn_path=None, nn_write_path=None, print_results_every=1000):
    return train_policy_gradients({'input_nodes': 9, 'hidden_nodes': HIDDEN_LAYERS}, (None, 9), play_ttt_game,
                                  opponent_func=opponent_func, nn_path=nn_path,
                                  nn_write_path=nn_write_path, number_of_games=number_of_games,
                                  print_results_every=print_results_every)


def train_with_minimax():
    '''
        trains vs several incresingly strong minimax players
    '''
    from tictactoe.players import MiniMaxingTTTPlayer, SYMBOLS

    def oppo(board, pid):
        '''
            converts nn-like I/O in the tictactoe.referee.TicTacToe API
        '''
        p.id = 2 if pid == -1 else 1
        b = p.board = {}
        slots = ('A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'C1', 'C2', 'C3')

        for k, val in zip(slots, board):
            cell = SYMBOLS[val]  # works because -1 index is actually 2, awesome
            b[k] = cell
        m = p.compute_move()
        return slots.index(m)

    print('start', datetime.now())
    for i in range(2, 7):
        print('search depth', i)
        p = MiniMaxingTTTPlayer(search_depth=i)
        p.setup(1, ['X'])  # that 'X' isn't useful, but calling setup is

        train_ttt_policy_gradient(number_of_games=50000, nn_path=DEFAULT_PATH, opponent_func=oppo)
        print('end', datetime.now())


def manual_training():
    from tictactoe.referee import TicTacToe, SYMBOLS
    r = TicTacToe(players=[])  # just using this for board printing

    slots = ('A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'C1', 'C2', 'C3')
    def oppo(board, pid):
        b = r.board = {}
        for k, val in zip(slots, board):
            cell = SYMBOLS[val]  # works because -1 index is actually 2, awesome
            b[k] = cell
        print(r.draw_board())
        print('enter move: ', end='')
        return slots.index(input())

    train_ttt_policy_gradient(number_of_games=50, nn_path=DEFAULT_PATH, opponent_func=oppo)



def train_with_random():
    train_ttt_policy_gradient(number_of_games=1000000, nn_write_path=DEFAULT_PATH, opponent_func=random_mover)


if __name__ == '__main__':
    train_with_minimax()
    #train_with_random()

