'''
    chess rules are such a mess
'''
from itertools import product

from core.main import SequentialGame, InvalidMove, DRAW, RUNNING, ref_logger
import colorama
colorama.init(autoreset=True)


# PIECES = {
#     'K': ('♔', '♚'),
#     'Q': ('♕', '♛'),
#     'R': ('♖', '♜'),
#     'N': ('♘', '♞'),
#     'B': ('♗', '♝'),
#     'P': ('♙', '♟')
# }  # using colorama, it is better to always use the filled ones

PIECES = {
    'K': '♚',
    'Q': '♛',
    'R': '♜',
    'N': '♞',
    'B': '♝',
    'P': '♟'
}

COLORS = ('W', 'B')
EMPTY = '.'
XCOORD = 'abcdefgh'
YCOORD = '87654321'


# MOVES = {  # dx, dy
#     'K': [(dx, dy) for dx, dy in product(range(-1, 2), repeat=2) if dx or dy],
#     'Q': [(x * d, y * d) for d in range(-8, -9) for (x, y) in ((0, 1), (1, 0), (1, 1), (1, -1)) if d],
#     'R': [(x * d, y * d) for d in range(-8, -9) for (x, y) in ((0, 1), (1, 0)) if d],
#     'B': [(x * d, y * d) for d in range(-8, -9) for (x, y) in ((1, 1), (1, -1)) if d],
#     'N': [(1, 2), (1, -2), (2, 1), (2, -1), (-1, 2), (-1, -2), (-2, -1), (-2, 1)]
# }

MOVES = {
    'K': ((1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)),
    'N': ((1, 2), (1, -2), (2, 1), (2, -1), (-1, 2), (-1, -2), (-2, -1), (-2, 1))
}

DIRECTIONS = {
    'Q': ((0, 1), (1, 0), (1, 1), (1, -1)),
    'R': ((0, 1), (1, 0)),
    'B': ((1, 1), (1, -1))
}


ROOK_CASTLE = {
    (0, 0): (2, 0),
    (7, 0): (6, 0),
    (0, 7): (2, 7),
    (7, 7): (6, 7)
}

KING_HOUSES = [None, (4, 7), (4, 0)]

NULLMOVE = '0000'


def available_piece_moves(board, tile, free_cell=None, block_cell=None):
    '''
        yields all the valid moves for a piece (not pawn), including captures
        do not take into account check constraints
        assumes that board[tile] is a piece

        if skip_cell is passed, that cell is considered empty
    '''
    t0, t1 = tile
    col, piece = board[tile]
    if piece in ('K', 'N'):
        for m0, m1 in MOVES[piece]:
            d0 = t0 + m0
            d1 = t1 + m1
            k = d0, d1
            if k == free_cell or 0 <= d0 <= 7 and 0 <= d1 <= 7 and board[k][0] != col or k == block_cell:
                yield k
    else:
        for dx, dy in DIRECTIONS[piece]:
            for v in (-1, 1):
                for l in range(1, 8):
                    d0 = t0 + dx * v * l
                    d1 = t1 + dy * v * l
                    k = d0, d1
                    if 0 <= d0 <= 7 and 0 <= d1 <= 7:  # in board
                        c = board[k][0]
                        if k == free_cell or c == EMPTY and k != block_cell:  # empty cell
                            yield k
                            continue
                        elif k == block_cell or c != col:  # opponent piece
                            yield k
                    break


class Chess(SequentialGame):
    '''
        referee class for chess

        internally board is a dict (x, y) -> CV or '.' (for empty squares)
        where:
            x, y start from 0 at top left
            C is color (W or B)
            V is value (one of R N B Q K and P for pawn)

        output towards player is just the move made from previous player, on first turn is nullmove (see below)

        input move is case insensitive and follows the uci protocol, e.g.:
        E2E4 for king pawn opening
        E4F5 for pawn capture
        E1G1 for castling
        E7E8Q for promotion

        ref http://wbec-ridderkerk.nl/html/UCIProtocol.html
        The move format is in long algebraic notation.
        A nullmove from the Engine to the GUI should be send as 0000.
        Examples:  e2e4, e7e5, e1g1 (white short castling), e7e8q (for promotion)
    '''
    def __init__(self, players_number=2):
        super().__init__(players_number=players_number)
        self.draw_turn_counter = 0
        self.available_ep = None  # "enpassable" piece
        # list variables defined here have None as first element, so that I can access them by player_id
        self.available_castles = [None, {(2, 7), (6, 7)}, {(2, 0), (6, 0)}]
        self.kings = [None, (4, 7), (4, 0)]
        self.player_pieces = [None, {(x, y) for x in range(8) for y in range(6, 8)},
                              {(x, y) for x in range(8) for y in range(2)}]

        self.tomove = COLORS[0]
        self.moves = []
        self.board = b = dict.fromkeys(product(range(8), repeat=2), EMPTY)
        for col, y in zip(COLORS, (7, 0)):
            for i, p in zip(range(8), 'RNBQKBNR'):
                b[i, y] = col + p
        for col, y in zip(COLORS, (6, 1)):
            for i in range(8):
                b[i, y] = col + 'P'

    def copy(self):
        new = Chess()
        new.draw_turn_counter = self.draw_turn_counter
        new.available_ep = self.available_ep
        new.available_castles = [None] + [ac.copy() for ac in self.available_castles[1:]]
        new.kings = list(self.kings)
        new.player_pieces = [None] + [pp.copy() for pp in self.player_pieces[1:]]
        new.tomove = self.tomove
        new.board = self.board.copy()
        # it's ok for new.moves to be empty
        return new

    def setup(self):
        ref_logger.info('starting game')
        return [['WHITE'], ['BLACK']]

    def get_board(self, player_id):
        return [self.moves[-1] if self.moves else NULLMOVE]

    def available_moves(self, player_id, starting_tile=None):
        b = self.board
        tiles = (starting_tile, ) if starting_tile else self.player_pieces[player_id]
        for t in tiles:
            if b[t][1] == 'P':
                for m in self.valid_pawn_moves(player_id, t):
                    if not self.exposes_to_check(player_id, t, m):
                        yield (t, m)
            else:
                for m in available_piece_moves(b, t):
                    if not self.exposes_to_check(player_id, t, m):
                        yield (t, m)
                # castles
                if t == KING_HOUSES[player_id]:
                    for m in self.available_castles[player_id]:
                        c2x, c2y = m
                        for i, tile in enumerate((t, (3, c2y) if c2x == 2 else (5, c2y), m)):
                            # here enumerate is used only to exclude first element from the first check
                            if i and b[tile] != EMPTY or self.check_menace(tile, (player_id % 2) + 1):
                                break
                        else:
                            yield (t, m)

    def check_menace(self, tile, player_id, pieces=None, free_cell=None, block_cell=None):
        '''
            returns a true value if the tile is under menace, false otherwise
            do not take into account en passant
            if a true value is returned, it is the coordinate set of _a_ menacing piece

            player_id is the moving player (the menacing one)

            if pieces is given, those coordinates for starting menaces are checked
            otherwise, the full board is scanned for pieces of player player_id

            free_cell and block_cell are propagated to available_piece_moves
        '''
        board = self.board
        if pieces is None:
            plcol = COLORS[player_id - 1]
            pieces = (coord for coord, col_p in board.items() if plcol == col_p[0])

        for coord in pieces:
            if coord == block_cell:  # this piece has been eaten
                continue
            col, p = board[coord]
            if p == 'P':
                for m in self.valid_pawn_moves(player_id, coord, free_cell=free_cell, block_cell=block_cell):
                    if m == tile:
                        return coord
            else:
                for m in available_piece_moves(board, coord, free_cell=free_cell, block_cell=block_cell):
                    if m == tile:
                        return coord
        return False

    def valid_pawn_moves(self, player_id, starting_tile, free_cell=None, block_cell=None):
        '''
            yields all valid moves for pawn of player {player_id} on {starting_tile}
            of course if it is the last tile there will be a promotion, but it's not handled here
            do not takes into account king check
        '''
        dy = -1 if player_id == 1 else 1
        sx, sy = starting_tile
        b = self.board
        oppo = COLORS[player_id % 2]
        c = sx, sy + dy
        if b[c] == EMPTY and c != block_cell or c == free_cell:
            yield c
            # double movement from starting position
            c = sx, sy + dy * 2
            if (sy - 1 * dy) % 7 == 0 and (b[c] == EMPTY and c != block_cell or c == free_cell):
                yield c
        # capture
        for dx in (-1, 1):
            c = sx + dx, sy + dy
            if 0 <= sx + dx < 8 and (b[c][0] == oppo or c == block_cell or self.available_ep == (sx + dx, sy)):
                yield c

    def exposes_to_check(self, player_id, starting_tile, target_tile):
        '''
            checks if the given move for player player_id exposes the moving player to check (i.e. is invalid)
        '''
        otherpl = (player_id % 2) + 1
        targ = target_tile if self.board[starting_tile][-1] == 'K' else self.kings[player_id]
        mena = self.check_menace(targ,
                                 player_id=otherpl,
                                 pieces=self.player_pieces[otherpl],
                                 free_cell=starting_tile,
                                 block_cell=target_tile)
        if mena:
            ref_logger.debug('move %s exposes to check from %s', (starting_tile, target_tile), mena)
            return mena

    def execute_turn(self, player_id, strmove):
        b = self.board
        pp = self.player_pieces

        ref_logger.debug('received input %s, validating', strmove)
        # input validation
        strmove = strmove.lower()
        if len(strmove) > 5 or len(strmove) < 4:
            raise InvalidMove('starting position invalid (move "{}")'.format(strmove))
        c1, c2, new_piece = strmove[0:2], strmove[2:4], strmove[4:].upper()
        try:
            c1x = XCOORD.index(c1[0])
            c1y = YCOORD.index(c1[1])
        except KeyError:
            raise InvalidMove('starting position invalid (move "{}")'.format(strmove))
        starting_tile = c1x, c1y
        try:
            col, piece = b[starting_tile]
        except ValueError:  # too many values to unpack
            raise InvalidMove('starting position is a empty square (move "{}")'.format(strmove))
        plcol = COLORS[player_id - 1]
        if col != plcol:
            raise InvalidMove('starting position not corresponding to a piece of correct player (move "{}")'.format(
                                                                                                            strmove))
        try:
            c2x = XCOORD.index(c2[0])
            c2y = YCOORD.index(c2[1])
        except KeyError:
            raise InvalidMove('target position invalid (move "{}")'.format(strmove))
        target_tile = c2x, c2y

        # move validation
        if b[target_tile][0] == col:
            raise InvalidMove('target space occupied by friendly piece (move "{}")'.format(strmove))
        if new_piece:  # promotion
            if piece != 'P' or c2[1] not in ('1', '8') or new_piece not in 'QRNB':
                raise InvalidMove('invalid promotion (move "{}")'.format(strmove))
        else:
            new_piece = piece
        ac = self.available_castles[player_id]
        castling_rook = None
        if starting_tile == KING_HOUSES[player_id] and target_tile in ac:  # castle
            castling_rook = [(0, c2y), (2, c2y)] if c2x == 2 else [(7, c2y), (5, c2y)]

        move = (starting_tile, target_tile)
        ref_logger.debug('checking if given move %s is a valid one', move)
        if all(m != move for m in self.available_moves(player_id, starting_tile)):
            raise InvalidMove('invalid move "{}"'.format(strmove))

        self.moves.append(strmove)
        # ladies and gentleman, the move!
        b[starting_tile] = EMPTY
        capture = False
        if b[target_tile] != EMPTY:
            capture = True
            self.draw_turn_counter = 0
            pp[(player_id % 2) + 1].remove(target_tile)
        if piece == 'P' and c2x != c1x and b[target_tile] == EMPTY:
            # en passant
            b[self.available_ep] = EMPTY
            pp[(player_id % 2) + 1].remove(self.available_ep)
        b[target_tile] = col + new_piece
        pp[player_id].remove(starting_tile)
        pp[player_id].add(target_tile)
        if castling_rook:
            b[castling_rook[0]] = EMPTY
            pp[player_id].remove(castling_rook[0])
            b[castling_rook[1]] = col + 'R'
            pp[player_id].add(castling_rook[1])

        if piece == 'P' or capture:
            self.draw_turn_counter = 0
        else:
            self.draw_turn_counter += 1
        if piece == 'P' and abs(c2y - c1y) > 1:
            self.available_ep = target_tile
        else:
            self.available_ep = None
        if piece == 'K':
            self.kings[player_id] = target_tile
        if ac:
            if piece == 'R':
                rc = ROOK_CASTLE.get(starting_tile)
                if rc:
                    ac.discard(rc)
            if piece == 'K':
                ac.clear()

        self.tomove = COLORS[player_id % 2]

        mate = self.check_mate(player_id)
        if mate == 2:
            return player_id
        elif mate == 1 or self.check_draw():
            return DRAW
        return RUNNING

    def check_draw(self):
        # TODO: threefold repetition
        pp = self.player_pieces
        return self.draw_turn_counter == 100 or len(pp[1]) == len(pp[2]) == 1

    def check_mate(self, player_id):
        '''
            returns 2 if player {player_id} made checkmate with last move, 1 if stalemate, 0 if none
        '''
        pp = self.player_pieces
        other_player = (player_id % 2) + 1
        other_king = self.kings[other_player]
        ref_logger.debug('looking available moves of next player to detect mate')
        available_moves = any(self.available_moves(other_player))
        if not available_moves:
            ref_logger.info('no available moves, checking whether is stalemate or checkmate')
            check = self.check_menace(other_king, player_id=player_id, pieces=pp[player_id])
            if check:  # check
                ref_logger.info('opposing king %s under check from %s, mate!', other_king, check)
                return 2
            return 1
        return 0

    def interactive_board(self):
        print()
        b = self.board
        cell_colors = (colorama.Back.GREEN, colorama.Back.YELLOW)
        piece_colors = {'W': colorama.Fore.WHITE, 'B': colorama.Fore.BLACK}

        ranges = range(8) if self.tomove == 'W' else range(7, -1, -1)
        for y in ranges:
            print(str(8 - y) + ' ', end='')
            for x in ranges:
                back = cell_colors[(y + x) % 2]
                piece = b[x, y]
                if piece == EMPTY:
                    print(back + '  ', end='')
                else:
                    print(back + piece_colors[piece[0]] + PIECES[piece[1]] + ' ', end='')
            print()
        if self.tomove == 'W':
            print('  a b c d e f g h')
        else:
            print('  h g f e d c b a')
