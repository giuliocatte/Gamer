import collections
import os
import random
from itertools import cycle

import tensorflow as tf
import numpy as np

try:
    from core.nn import load_network, create_network, save_network
    from core.lib import normalize
except ImportError:
    # executing as __main__
    import os
    import sys
    currentdir = os.path.dirname(os.path.abspath(__file__))
    parentdir = os.path.dirname(currentdir)
    print(parentdir)
    sys.path.append(parentdir)

    from core.nn import load_network, create_network, save_network
    from core.lib import normalize

DEFAULT_PATH = 'current_network.p'
HIDDEN_LAYERS = (100, 100, 100)


def get_callable_from_saved_network(file_path=DEFAULT_PATH):
    session = tf.Session()
    session.run(tf.initialize_all_variables())

    input_layer, output_layer, variables = create_network(9, hidden_nodes=HIDDEN_LAYERS)
    load_network(session, variables, file_path)

    def cal(board):
        return session.run(output_layer, feed_dict={input_layer: np.array(board).reshape(1, 9)})[0]

    return cal


def stochastic_move(session, input_layer, output_layer, board, side=1, valid_only=False):
    '''
        returns a move as a vector, comupted with the probabilities of the session's nn
        if I default valid_only=True, suddently the win ratio drops instead of raising.
        boh
        forse e' normalize che fa qualcosa che non va?
        TODO: indagare
    '''
    board_tensor = (np.array(board) * side).reshape(1, 9)
    probabilities = session.run(output_layer, feed_dict={input_layer: board_tensor})[0]

    if valid_only:
        probabilities = normalize([p if not board[i] else 0 for i, p in enumerate(probabilities)], ord=0)  # 1 sum
    try:
        move = np.random.multinomial(1, probabilities)
    except ValueError:
        # se la somma e' maggiore di uno si arrabbia, e (forse) puo' capitare per l'arrotondamento
        # d'altro canto, se e' inferiore di uno, aggiunge all'ultimo elemento quel che manca
        # quindi sarebbe meglio calare solo l'ultimo che tutti, ma non ce l'ho fatta, non so perche'
        # TODO: indagare
        move = np.random.multinomial(1, probabilities / (1. + 1e-6))
    return move


_lines = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 3, 6], [1, 4, 7], [2, 5, 8], [0, 4, 8], [2, 4, 6]]


def play_full_game(mover1, mover2):
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



def train_policy_gradients(opponent_func=None, nn_path=None, nn_write_path=None, number_of_games=10000,
                           print_results_every=1000, learn_rate=1e-4, batch_size=100, randomize_first_player=True):
    '''
        Train a network using policy gradients
    '''
    nn_write_path = nn_write_path or nn_path
    reward_placeholder = tf.placeholder("float", shape=(None,))
    actual_move_placeholder = tf.placeholder("float", shape=(None, 9))

    input_layer, output_layer, variables = create_network(9, hidden_nodes=HIDDEN_LAYERS)

    policy_gradient = tf.log(  # natural logarithm
        tf.reduce_sum(tf.mul(actual_move_placeholder, output_layer), reduction_indices=1)) * reward_placeholder
    train_step = tf.train.AdamOptimizer(learn_rate).minimize(-policy_gradient)

    with tf.Session() as session:
        session.run(tf.initialize_all_variables())

        if nn_path and os.path.isfile(nn_path):
            print("loading pre-existing network")
            load_network(session, variables, nn_path)

        mini_batch_board_states, mini_batch_moves, mini_batch_rewards = [], [], []
        results = collections.deque(maxlen=print_results_every)

        def make_training_move(board_state, side):
            mini_batch_board_states.append(np.array(board_state) * side)
            move = stochastic_move(session, input_layer, output_layer, board_state, side)
            mini_batch_moves.append(move)
            return move.argmax()  # returns move as an index

        opponent_func = opponent_func or random_mover

        for episode_number in range(1, number_of_games):
            # randomize if going first or second
            if (not randomize_first_player) or bool(random.getrandbits(1)):
                reward = play_full_game(make_training_move, opponent_func)
            else:
                reward = -play_full_game(opponent_func, make_training_move)

            results.append(reward)

            # we scale here so winning quickly is better winning slowly and loosing slowly better than loosing quick
            last_game_length = len(mini_batch_board_states) - len(mini_batch_rewards)

            reward /= float(last_game_length)

            mini_batch_rewards += ([reward] * last_game_length)

            if episode_number % batch_size == 0:
                normalized_rewards = mini_batch_rewards - np.mean(mini_batch_rewards)

                rewards_std = np.std(normalized_rewards)
                if rewards_std != 0:
                    normalized_rewards /= rewards_std
                else:
                    print("warning: got mini batch std of 0.")

                np_mini_batch_board_states = np.array(mini_batch_board_states) \
                    .reshape(len(mini_batch_rewards), *input_layer.get_shape().as_list()[1:])

                session.run(train_step, feed_dict={input_layer: np_mini_batch_board_states,
                                                   reward_placeholder: normalized_rewards,
                                                   actual_move_placeholder: mini_batch_moves})

                # print('GAME')
                # print(mini_batch_board_states[-last_game_length:], mini_batch_rewards[-1])

                # clear batches
                del mini_batch_board_states[:]
                del mini_batch_moves[:]
                del mini_batch_rewards[:]

            if episode_number % print_results_every == 0:
                print("episode: %s win_rate: %s" % (episode_number, _win_rate(print_results_every, results)))
                if nn_write_path:
                    save_network(session, variables, nn_write_path)

        if nn_write_path:
            save_network(session, variables, nn_write_path)

    return variables, _win_rate(print_results_every, results)


def _win_rate(print_results_every, results):
    '''
        win ratio = won / (won + lost)
            = (won - lost) / ((won + lost) * 2) + 0.5

        where result = won - lost; print_result_every = won + lost
    '''
    return 0.5 + sum(results) / (print_results_every * 2.)


if __name__ == '__main__':
    train_policy_gradients(number_of_games=1000000, nn_write_path=DEFAULT_PATH)
