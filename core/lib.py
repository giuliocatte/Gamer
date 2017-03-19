
inf = float('inf')


def minimax(node, value_function, child_function, terminal_function, depth, maximizing=True):
    '''
    01 function minimax(node, depth, maximizingPlayer)
    02     if depth = 0 or node is a terminal node
    03         return the heuristic value of node

    04     if maximizingPlayer
    05         bestValue := −∞
    06         for each child of node
    07             v := minimax(child, depth − 1, FALSE)
    08             bestValue := max(bestValue, v)
    09         return bestValue

    10     else    (* minimizing player *)
    11         bestValue := +∞
    12         for each child of node
    13             v := minimax(child, depth − 1, TRUE)
    14             bestValue := min(bestValue, v)
    15         return bestValue
    '''
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
    '''
    01 function negamax(node, depth, color)
    02     if depth = 0 or node is a terminal node
    03         return color * the heuristic value of node

    04     bestValue := −∞
    05     foreach child of node
    06         v := −negamax(child, depth − 1, −color)
    07         bestValue := max( bestValue, v )
    08     return bestValue
    '''
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

