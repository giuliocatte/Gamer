from core.main import player_logger
from core.players import RandomPlayer, IOPlayer, Player, MiniMaxingPlayer
from .referee import Chess, XCOORD, YCOORD, NULLMOVE, available_piece_moves, EMPTY

# from .nn import get_callable_from_saved_network, DEFAULT_PATH

inf = float('inf')

PIECES_VALUES = {
    'P': 100,
    'N': 320,
    'B': 330,
    'R': 500,
    'Q': 900,
    'K': 20000
}

POSITIONS_VALUES = [None,
    {'P': (
        (  0,  0,  0,  0,  0,  0,  0,  0),
        ( 50, 50, 50, 50, 50, 50, 50, 50),
        ( 10, 10, 20, 30, 30, 20, 10, 10),
        (  5,  5, 10, 25, 25, 10,  5,  5),
        (  0,  0,  0, 20, 20,  0,  0,  0),
        (  5, -5,-10,  0,  0,-10, -5,  5),
        (  5, 10, 10,-20,-20, 10, 10,  5),
        (  0,  0,  0,  0,  0,  0,  0,  0)
    ),
    'N': (
        (-50,-40,-30,-30,-30,-30,-40,-50),
        (-40,-20,  0,  0,  0,  0,-20,-40),
        (-30,  0, 10, 15, 15, 10,  0,-30),
        (-30,  5, 15, 20, 20, 15,  5,-30),
        (-30,  0, 15, 20, 20, 15,  0,-30),
        (-30,  5, 10, 15, 15, 10,  5,-30),
        (-40,-20,  0,  5,  5,  0,-20,-40),
        (-50,-40,-30,-30,-30,-30,-40,-50)
    ),
    'B': (
        (-20,-10,-10,-10,-10,-10,-10,-20),
        (-10,  0,  0,  0,  0,  0,  0,-10),
        (-10,  0,  5, 10, 10,  5,  0,-10),
        (-10,  5,  5, 10, 10,  5,  5,-10),
        (-10,  0, 10, 10, 10, 10,  0,-10),
        (-10, 10, 10, 10, 10, 10, 10,-10),
        (-10,  5,  0,  0,  0,  0,  5,-10),
        (-20,-10,-10,-10,-10,-10,-10,-20)
    ),
    'R': (
        (  0,  0,  0,  0,  0,  0,  0,  0),
        (  5, 10, 10, 10, 10, 10, 10,  5),
        ( -5,  0,  0,  0,  0,  0,  0, -5),
        ( -5,  0,  0,  0,  0,  0,  0, -5),
        ( -5,  0,  0,  0,  0,  0,  0, -5),
        ( -5,  0,  0,  0,  0,  0,  0, -5),
        ( -5,  0,  0,  0,  0,  0,  0, -5),
        (  0,  0,  0,  5,  5,  0,  0,  0)
    ),
    'Q': (
        (-20,-10,-10, -5, -5,-10,-10,-20),
        (-10,  0,  0,  0,  0,  0,  0,-10),
        (-10,  0,  5,  5,  5,  5,  0,-10),
        ( -5,  0,  5,  5,  5,  5,  0, -5),
        (  0,  0,  5,  5,  5,  5,  0, -5),
        (-10,  5,  5,  5,  5,  5,  0,-10),
        (-10,  0,  5,  0,  0,  0,  0,-10),
        (-20,-10,-10, -5, -5,-10,-10,-20)
    ),
    'K': (
        (-30,-40,-40,-50,-50,-40,-40,-30),
        (-30,-40,-40,-50,-50,-40,-40,-30),
        (-30,-40,-40,-50,-50,-40,-40,-30),
        (-30,-40,-40,-50,-50,-40,-40,-30),
        (-20,-30,-30,-40,-40,-30,-30,-20),
        (-10,-20,-20,-20,-20,-20,-20,-10),
        ( 20, 20,  0,  0,  0,  0, 20, 20),
        ( 20, 30, 10,  0,  0, 10, 30, 20)
    ),
    'L': (  # king late game
        (-50,-40,-30,-20,-20,-30,-40,-50),
        (-30,-20,-10,  0,  0,-10,-20,-30),
        (-30,-10, 20, 30, 30, 20,-10,-30),
        (-30,-10, 30, 40, 40, 30,-10,-30),
        (-30,-10, 30, 40, 40, 30,-10,-30),
        (-30,-10, 20, 30, 30, 20,-10,-30),
        (-30,-30,  0,  0,  0,  0,-30,-30),
        (-50,-30,-30,-30,-30,-30,-30,-50)
    )
}]
POSITIONS_VALUES.append(
    {k: tuple(t[::-1] for t in reversed(v)) for k, v in POSITIONS_VALUES[1].items()}
)


def get_available_moves_from_game(game, player_id):
    b = game.board
    for starting_tile, target_tile in game.available_moves(player_id):
        m = ''.join(
            (XCOORD[starting_tile[0]], YCOORD[starting_tile[1]], XCOORD[target_tile[0]], YCOORD[target_tile[1]]))
        if target_tile[1] in (0, 7) and b[starting_tile][-1] == 'P':
            for p in 'RBQN':
                yield m + p
        else:
            yield m


class ChessPlayer(Player):
    '''
        ABC for chess players
        if a subclass wishes to define compute_move, should use _compute_move instead
    '''
    turn_lines = 1
    setup_lines = 1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game = Chess()

    def process_turn_input(self, inp):
        inp = inp[0]
        if inp != NULLMOVE:
            player_logger.debug('updating internal state for opponent move %s', inp)
            self.game.execute_turn((self.id % 2) + 1, inp)

    def _compute_move(self):
        return super().compute_move()

    def compute_move(self):
        move = self._compute_move()
        player_logger.debug('updating internal state for player move %s', move)
        self.game.execute_turn(self.id, move)
        return move


class IOChessPlayer(ChessPlayer, IOPlayer):
    loud = False
    algebraic = True

    def setup(self, player_id, inp):
        print('player', player_id, 'your color is', inp[0])
        return super().setup(player_id, inp)

    def process_turn_input(self, inp):
        if inp[0] != NULLMOVE:
            print('opponent move:', self.to_algebraic(inp[0]))
        return super().process_turn_input(inp)

    def to_algebraic(self, mov):
        '''
            converts a valid move in coordinates notation to algebraic notation
        '''
        g = self.game
        b = g.board
        starting = XCOORD.index(mov[0]), YCOORD.index(mov[1])
        target = XCOORD.index(mov[2]), YCOORD.index(mov[3])
        spiece = b[starting][1]
        if spiece == 'K':
            # check for castle
            d = abs(starting[0] - target[0])
            if d == 2:
                return '0-0'
            elif d == 3:
                return '0-0-0'
            otherpieces = ()
        else:
            otherpieces = [t for t in g.player_pieces[self.id] if t != starting and b[t] == spiece]
            # in case of promotion, can be more than 1
        tpart = mov[2:]  # pawn promotion is managed as well this way
        if b[target] != EMPTY:
            tpart = 'x' + tpart
        elif b[starting] == 'P' and starting[0] != target[0]:
            tpart = 'x' + tpart + 'e.p.'
        if spiece == 'P':
            spart = mov[0] if 'x' in tpart else ''
        else:
            spart = spiece
            player_logger.debug('checking available moves for using proper algebraic notation')
            if any(target in available_piece_moves(b, op) for op in otherpieces):
                # disambiguation needed
                if all(op[0] != starting[0] for op in otherpieces):
                    spart = spart + mov[0]
                elif all(op[1] != starting[1] for op in otherpieces):
                    spart = spart + mov[1]
                else:
                    spart += mov[:2]
        kingpos = g.kings[self.id]
        player_logger.debug('checking if it is a king check to signal it')
        check = g.check_menace(kingpos, (self.id % 2) + 1, free_cell=starting, block_cell=target)
        if check:
            player_logger.debug('king in %s menaced by %s after move %s%s', kingpos, check, spart, tpart)
            tpart += '+'
        return spart + tpart

    def parse_algebraic(self, alg):
        '''
            receives a move in algebraic notation, returns coordinates notation
        '''
        g = self.game
        p = g.player_pieces[self.id]
        np = ''
        b = g.board
        alg = alg.replace('+', '')
        if alg in ('0-0', '0-0-0', 'O-O', 'O-O-O'):
            sx, sy = g.kings[self.id]
            ty = sy
            tx = 6 if len(alg) == 3 else 2
        elif alg[0] in ('K', 'Q', 'R', 'N', 'B'):
            alg = alg.replace('x', '').replace('X', '').replace(':', '')
            piece = alg[0]
            if len(alg) == 5:  # quite rare
                sx = XCOORD.index(alg[1])
                sy = YCOORD.index(alg[2])
                tx = XCOORD.index(alg[3])
                ty = YCOORD.index(alg[4])
            elif len(alg) == 4:
                k = alg[1]
                tx = XCOORD.index(alg[2])
                ty = YCOORD.index(alg[3])
                if k.isdigit():
                    sy = YCOORD.index(k)
                    sx = next(t for t in p if t[1] == sy and piece == b[t][-1] and
                              any((tx, ty) == tt for tt in available_piece_moves(b, t)))[0]
                else:
                    sx = XCOORD.index(k)
                    sy = next(t for t in p if t[0] == sx and piece == b[t][-1] and
                              any((tx, ty) == tt for tt in available_piece_moves(b, t)))[1]
            else:
                tx = XCOORD.index(alg[1])
                ty = YCOORD.index(alg[2])
                sx, sy = next(t for t in p if piece == b[t][-1] and
                              any((tx, ty) == tt for tt in available_piece_moves(b, t)))
        else:
            if alg[-1] in ('Q', 'N', 'B', 'R'):
                np = alg[-1]
                alg = alg.replace('=', '')[:-1]
            dy = -1 if self.id == 1 else 1
            if len(alg) == 2:
                sx = tx = XCOORD.index(alg[0])
                ty = YCOORD.index(alg[1])
                if b[sx, ty - dy][-1] == 'P':
                    sy = ty - dy
                else:
                    sy = ty - 2 * dy
            else:
                alg = alg.replace('x', '').replace(':', '').replace('.', '').replace('ep', '')
                sx = XCOORD.index(alg[0])
                tx = XCOORD.index(alg[1])
                ty = YCOORD.index(alg[2])
                sy = ty - dy

        return ''.join((XCOORD[sx], YCOORD[sy], XCOORD[tx], YCOORD[ty], np))

    def _compute_move(self):
        while True:
            move = IOPlayer.compute_move(self)  # using super here would create a loop
            if self.algebraic:
                try:
                    move = self.parse_algebraic(move)
                except (ValueError, IndexError, StopIteration):
                    print('invalid move!')
                    continue
            player_logger.debug(move)
            if move in get_available_moves_from_game(self.game, self.id):
                break
            print('invalid move!')
        return move


class RandomChessPlayer(ChessPlayer, RandomPlayer):
    def compute_available_moves(self):
        '''
            each pawn to last row movement accounts for 4 different promotions
            if I really cared about the random player, probably I'd rescale the probabilities
        '''
        am = list(get_available_moves_from_game(self.game, self.id))
        player_logger.debug('available moves: %s', am)
        return am


class MiniMaxingChessPlayer(ChessPlayer, MiniMaxingPlayer):
    search_depth = 4
    value_functions = ['simple_board_value', ]
    algorithm = 'shuffling_minimax_alpha_beta'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.board = self.game  # MiniMaxing superclass expects this name
        self.__late = False

    def _is_late_game(self, board, pp):
        # this could be set some moves in advance, because of depth reading
        if self.__late:
            earlyg = [False, False]
            has_q = [False, False]
            has_p = [0, 0]
            for i, t in enumerate(pp[1:]):
                piece = board[t][1]
                if piece == 'Q':
                    has_q[i] = True
                    if has_p[i] >= 2:
                        earlyg[i] = True
                        continue
                elif piece not in ('P', 'K'):
                    has_p[i] += 1
                    if has_p[i] >= 2 and has_q[i]:
                        earlyg[i] = True
                        continue
            if not any(earlyg):
                player_logger.info('late game is started!')
                self.__late = True
        return self.__late

    def simple_board_value(self, node):
        '''
            https://chessprogramming.wikispaces.com/Simplified+evaluation+function
        '''
        game = node['board']
        board = game.board
        pp = game.player_pieces
        to_move = node['to_move']
        res = game.check_mate(player_id=(to_move % 2) + 1)
        # TODO: non sono del tutto sicurissimo che sia corretto guardare l'altro giocatore :/
        if res == 2:
            val = -inf
        elif res == 1 or game.check_draw():
            val = 0
        # TODO: domanda 1: to_move e' il giocatore che sta valutando o e' l'altro?
        # TODO: domanda 2: e' automatico il cambiamento da bianco a nero o devo girare cose?
        else:
            val = 0
            late_game = self._is_late_game(board, pp)
            # assumiamo che la risposta alla domanda 1 sia si'
            color = 1 if to_move == self.id else -1
            for pl, sgn in ((to_move, color), ((to_move % 2) + 1, -color)):
                pieces = pp[pl]
                tables = POSITIONS_VALUES[pl]
                for tile in pieces:
                    piece = board[tile][1]
                    val += sgn * PIECES_VALUES[piece]
                    val += sgn * tables[piece if not late_game or piece != 'K' else 'L'][tile[1]][tile[0]]
        return val

    @staticmethod
    def child_function(node):
        board = node['board']  # board is a referee actually
        to_move = node['to_move']
        for strmove in get_available_moves_from_game(board, to_move):
            new_board = board.copy()
            new_board.execute_turn(to_move, strmove)
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
        return board.check_mate(player_id=(node['to_move'] % 2) + 1) or board.check_draw()


class TensorFlowChessPlayer(ChessPlayer):
    '''
    '''
    saved_nn_path = 'p'  # DEFAULT_PATH

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
