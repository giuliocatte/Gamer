import numpy as np


inf = float('inf')


def normalize(arr, ord=None):
    '''
    incredibile ma numpy non ha un modo per normalizzare un array
    sklearn ne aveva uno, ma mi da' un deprecation warning con array 1-dimensionali
    a quanto pare e' un mestire difficile :/

    raises a ZeroDivisionError if a 0 vector is passed
    '''
    norm = np.linalg.norm(arr, ord=ord)
    return arr / norm


def minimax(node, value_function, child_function, terminal_function, depth, maximizing=True):
    if not depth or terminal_function(node):
        bestvalue = value_function(node)
        bestchild = node
    elif maximizing:
        bestvalue, bestchild = -inf, None
        for child in child_function(node):
            v, _ = minimax(child, value_function, child_function, terminal_function, depth - 1, False)
            if v >= bestvalue:
                bestvalue = v
                bestchild = child
    else:
        bestvalue, bestchild = inf, None
        for child in child_function(node):
            v, _ = minimax(child, value_function, child_function, terminal_function, depth - 1, True)
            if v <= bestvalue:
                bestvalue = v
                bestchild = child
    return bestvalue, bestchild


def negamax(node, value_function, child_function, terminal_function, depth, color=1):
    if not depth or terminal_function(node):
        bestvalue = color * value_function(node)
        bestchild = node
    else:
        bestvalue, bestchild = -inf, None
        for child in child_function(node):
            v, _ = negamax(child, value_function, child_function, terminal_function, depth - 1, -color)
            v = -v
            if v >= bestvalue:
                bestvalue = v
                bestchild = child
            bestvalue = max(bestvalue, v)
    return bestvalue, bestchild


def maximizer(value_function, elements):
    bestvalue, bestel, el = -inf, None, None
    for el in elements:
        v = value_function(el)
        if v > bestvalue:
            bestvalue = v
            bestel = el
    return bestel or el  # nel caso tutte le mosse abbiano -inf come valore, ne ritorno una a caso

