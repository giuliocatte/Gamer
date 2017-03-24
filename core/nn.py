'''
    helpers for neural networks

    most of this is copied by https://github.com/DanielSlater/AlphaToe

    TODO: quando salvo e carico suppongo di avere le informazioni di com'e' fatta la nn da fuori,
    ma non e' necessario, potrei inserire anche quelle nel salvataggio...
'''

import numpy as np
import tensorflow as tf
import pickle


def create_network(input_nodes, hidden_nodes, output_nodes=None, output_softmax=True):
    """Create a network with relu activations at each layer

    Args:
        input_nodes (int): The size of the board this network will work on
        output_nodes: (int): Number of output nodes, if None then number of input nodes is used
        hidden_nodes ([int]): The number of hidden nodes in each hidden layer
        output_softmax (bool): If True softmax is used in the final layer, otherwise just use the activation with no
            non-linearity function

    Returns:
        (input_layer, output_layer, [variables]) : The final item in the tuple is a list containing all the parameters,
            wieghts and biases used in this network
    """
    output_nodes = output_nodes or input_nodes

    variables = []

    with tf.name_scope('network'):
        input_layer = tf.placeholder("float", (None, input_nodes))
        current_layer = input_layer

        for hidden_nodes in hidden_nodes:
            last_layer_nodes = int(current_layer.get_shape()[-1])
            # definisco i weight e bias dal layer n-1 al layer n
            hidden_weights = tf.Variable(
                tf.truncated_normal((last_layer_nodes, hidden_nodes), stddev=1. / np.sqrt(last_layer_nodes)),
                name='weights')
            hidden_bias = tf.Variable(tf.constant(0.01, shape=(hidden_nodes,)), name='biases')

            variables.append(hidden_weights)
            variables.append(hidden_bias)

            current_layer = tf.nn.relu(
                tf.matmul(current_layer, hidden_weights) + hidden_bias)

        # for some reason having output std divided by np.sqrt(output_nodes) massively outperforms np.sqrt(hidden_nodes)
        output_weights = tf.Variable(
            tf.truncated_normal((hidden_nodes, output_nodes), stddev=1. / np.sqrt(output_nodes)), name="output_weights")
        output_bias = tf.Variable(tf.constant(0.01, shape=(output_nodes,)), name="output_bias")

        variables.append(output_weights)
        variables.append(output_bias)

        output_layer = tf.matmul(current_layer, output_weights) + output_bias
        if output_softmax:
            output_layer = tf.nn.softmax(output_layer)

    return input_layer, output_layer, variables


def save_network(session, tf_variables, file_path):
    """Save the given set of variables to the given file using the given session

    Args:
        session (tf.Session): session within which the variables has been initialised
        tf_variables (list of tf.Variable): list of variables which will be saved to the file
        file_path (str): path of the file we want to save to.
    """
    variable_values = session.run(tf_variables)
    with open(file_path, mode='wb') as f:
        pickle.dump(variable_values, f)


def load_network(session, tf_variables, file_path):
    """Load the given set of variables from the given file using the given session

    Args:
        session (tf.Session): session within which the variables has been initialised
        tf_variables (list of tf.Variable): list of variables which will set up with the values saved to the file. List
            order matters, in must be the exact same order as was used to save and all of the same shape.
        file_path (str): path of the file we want to load from.
    """
    with open(file_path, mode='rb') as f:
        variable_values = pickle.load(f)

    try:
        if len(variable_values) != len(tf_variables):
            raise ValueError("Network in file had different structure, variables in file: %s variables in memeory: %s"
                             % (len(variable_values), len(tf_variables)))
        for value, tf_variable in zip(variable_values, tf_variables):
            session.run(tf_variable.assign(value))
    except ValueError as ex:
        # TODO: maybe raise custom exception
        raise ValueError("""Tried to load network file %s with different architecture from the in memory network.
Error was %s
Either delete the network file to train a new network from scratch or change the in memory network to match that dimensions of the one in the file""" % (file_path, ex))


def give_saved_network_a_shot(board, file_path, input_nodes, hidden_nodes, output_nodes=None):
    '''
        calls saved network to evaluate a single board
    '''
    output_nodes = output_nodes or input_nodes
    with tf.Session() as session:
        try:
            session.run(tf.initialize_all_variables())
        except AttributeError:
            # la documentazione dice che quello sopra e' deprecato e di usare questo, ma a quanto pare questo non esiste
            # nella mia versione di tf, almeno
            session.run(tf.global_variables_initializer())

        input_layer, output_layer, variables = create_network(input_nodes, hidden_nodes=hidden_nodes,
                                                                output_nodes=output_nodes)
        load_network(session, variables, file_path)

