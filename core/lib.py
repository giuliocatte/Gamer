import numpy as np
from random import choice
import sys


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
    return bestvalue, bestchild


def shuffling_negamax(node, value_function, child_function, terminal_function, depth, color=1):
    '''
    like negamax, but randomizes move between same value moves
    '''
    if not depth or terminal_function(node):
        bestvalue = color * value_function(node)
        bestchild = node
    else:
        bestvalue, bestchild = -inf, []
        for child in child_function(node):
            v, _ = negamax(child, value_function, child_function, terminal_function, depth - 1, -color)
            v = -v
            if v == bestvalue:
                bestchild.append(child)
            elif v > bestvalue:
                bestvalue = v
                bestchild = [child]
        bestchild = choice(bestchild)
    return bestvalue, bestchild


def minimax_with_alpha_beta_pruning(node, value_function, child_function, terminal_function, depth, maximizing=True,
                                    alpha=-inf, beta=inf):
    if not depth or terminal_function(node):
        bestvalue = value_function(node)
        bestchild = node
    elif maximizing:
        bestvalue, bestchild = -inf, None
        for child in child_function(node):
            v, _ = minimax_with_alpha_beta_pruning(child, value_function, child_function, terminal_function, depth - 1,
                                                   False, alpha, beta)
            if v >= bestvalue:
                alpha = max(alpha, v)
                bestvalue = v
                bestchild = child
                if beta <= alpha:
                    break
    else:
        bestvalue, bestchild = inf, None
        for child in child_function(node):
            v, _ = minimax_with_alpha_beta_pruning(child, value_function, child_function, terminal_function, depth - 1,
                                                   True, alpha, beta)
            if v <= bestvalue:
                beta = min(beta, v)
                bestvalue = v
                bestchild = child
                if beta <= alpha:
                    break
    return bestvalue, bestchild


def shuffling_minimax_alpha_beta(node, value_function, child_function, terminal_function, depth, maximizing=True,
                                    alpha=-inf, beta=inf):
    if not depth or terminal_function(node):
        bestvalue = value_function(node)
        bestchild = node
    elif maximizing:
        bestvalue, bestchild = -inf, []
        for child in child_function(node):
            v, _ = minimax_with_alpha_beta_pruning(child, value_function, child_function, terminal_function, depth - 1,
                                                   False, alpha, beta)
            if v == bestvalue:
                bestchild.append(child)
            elif v >= bestvalue:
                alpha = max(alpha, v)
                bestvalue = v
                bestchild = [child]
                if beta <= alpha:
                    break
        bestchild = choice(bestchild)
    else:
        bestvalue, bestchild = inf, []
        for child in child_function(node):
            v, _ = minimax_with_alpha_beta_pruning(child, value_function, child_function, terminal_function, depth - 1,
                                                   True, alpha, beta)
            if v == bestvalue:
                bestchild.append(child)
            elif v < bestvalue:
                beta = min(beta, v)
                bestvalue = v
                bestchild = [child]
                if beta <= alpha:
                    break
        bestchild = choice(bestchild)
    return bestvalue, bestchild


def maximizer(value_function, elements):
    bestvalue, bestel, el = -inf, None, None
    for el in elements:
        v = value_function(el)
        if v > bestvalue:
            bestvalue = v
            bestel = el
    return bestel or el  # nel caso tutte le mosse abbiano -inf come valore, ne ritorno una a caso


def perc_counted(iterator, length=None):
    if not length:
        if hasattr(iterator, "__len__"):
            length = len(iterator)
        elif hasattr(iterator, "__length_hint__"):
            length = iterator.__length_hint__(iterator)
    print('running: {:>3}%'.format(0), end='')
    phase = None
    for i in range(1, length + 1):
        p = int(i / length * 100)
        if p != phase:
            phase = p
            print('\b\b\b\b{:>3}%'.format(phase), end='')
            sys.stdout.flush()

