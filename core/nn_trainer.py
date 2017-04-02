'''
    a modified version of some methods of https://github.com/DanielSlater/AlphaToe
    Copyright (c) 2016 Daniel Slater
    under the MIT License
'''

import collections
import os
import random

import numpy as np
import tensorflow as tf

try:
    from core.lib import normalize
    from core.nn import create_network, load_network, save_network
except ImportError:
    # executing as __main__
    import sys
    currentdir = os.path.dirname(os.path.abspath(__file__))
    parentdir = os.path.dirname(currentdir)
    sys.path.append(parentdir)
    from core.lib import normalize
    from core.nn import create_network, load_network, save_network


def train_policy_gradients(nn_parameters, move_shape, match_func, opponent_func,
                           nn_path=None, nn_write_path=None, number_of_games=10000,
                           print_results_every=1000, learn_rate=1e-4, batch_size=100,
                           randomize_first_player=True, log_games=False):
    '''
        Train a network using policy gradients

        nn_parameters dict of arguments for create_network
        move_shape tuple describing the shape of the
        match_func function that streamlines the referee role: takes in input player functions, return as output
            id of the winning player (1 or -1) or 0 in the case of a draw
        opponent_func function that represents the opponent: takes in input board state and player id, returns in output
            a flat move
        batch_size the size of the mini batch (cfr http://sebastianruder.com/optimizing-gradient-descent/#minibatchgradientdescent)

        if just nn_write_path is passed, writes a new net at the given path
        if just nn_path is passed, reads a net in given path, trains it further, and overwrites it
        if both are passed, reads from nn_path, trains and then writes in nn_write_path

        mi chiedo se ci sia modo di fargli mangiare un oggetto di classe Game e uno di classe Player e fargli calcolare
        da quello play_game e opponent_func.... il problema e' che quelli parlano stringhe, c'e' da fare un bello strato
        di interfaccia... ma forse e' possibile.. l'unica cosa e' la lunghezza della mossa che la dovro' mettere
        in un parametro?
    '''
    nn_write_path = nn_write_path or nn_path
    reward_placeholder = tf.placeholder("float", shape=(None,))
    actual_move_placeholder = tf.placeholder("float", shape=move_shape)

    input_layer, output_layer, variables = create_network(**nn_parameters)

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

        for episode_number in range(1, number_of_games + 1):
            # randomize if going first or second
            if (not randomize_first_player) or bool(random.getrandbits(1)):
                if log_games:
                    print('playing game', episode_number, 'nn first')
                reward = match_func(make_training_move, opponent_func)
            else:
                if log_games:
                    print('playing game', episode_number, 'nn second')
                reward = -match_func(opponent_func, make_training_move)
            results.append(reward)

            # we scale here so winning quickly is better winning slowly and loosing slowly better than loosing quick
            last_game_length = len(mini_batch_board_states) - len(mini_batch_rewards)
            if log_games:
                print('reward is', reward, 'game length', last_game_length)

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


def stochastic_move(session, input_layer, output_layer, board, side=1, valid_only=False):
    '''
        returns a move as a vector, computed with the probabilities of the session's nn
        if I default valid_only=True, suddently the win ratio drops instead of raising.
        boh
    '''
    board_tensor = (np.array(board) * side).reshape(1, len(board))
    probabilities = session.run(output_layer, feed_dict={input_layer: board_tensor})[0]

    if valid_only:
        probabilities = normalize([p if not board[i] else 0 for i, p in enumerate(probabilities)], ord=1)
    try:
        move = np.random.multinomial(1, probabilities)
    except ValueError:
        # se la somma e' maggiore di uno si arrabbia, e (forse) puo' capitare per l'arrotondamento
        # d'altro canto, se e' inferiore di uno, aggiunge all'ultimo elemento quel che manca
        # quindi sarebbe meglio calare solo l'ultimo piuttosto che tutti, ma non ce l'ho fatta, non so perche'
        # TODO: indagare
        # probabilities[-1] -= 1e-6
        # move = np.random.multinomial(1, probabilities)
        move = np.random.multinomial(1, probabilities / (1. + 1e-6))
    return move
