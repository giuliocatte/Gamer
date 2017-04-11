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

CASTLES = ('0-0', '0-0-0')
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
            if k == free_cell or 0 <= d0 <= 7 and 0 <= d1 <= 7 and board[k][0] != col and k != block_cell:
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
                        if k == free_cell or c == EMPTY:  # empty cell
                            yield k
                            continue
                        elif block_cell or c != col:  # opponent piece
                            yield k
                    break


def check_menace(board, tile, player_id=None, pieces=None, free_cell=None, block_cell=None):
    '''
        returns a true value if the tile is under menace, false otherwise
        do not take into account en passant
        if a true value is returned, it is the coordinate set of _a_ menacing piece

        if pieces is given, those coordinates for starting menaces are checked
        otherwise, the full board is scanned for pieces of player player_id

        skip_cell and block cell are propagated to available_piece_moves
    '''
    if pieces is None:
        plcol = COLORS[player_id - 1]
        pieces = (coord for coord, (col, p) in board.items() if plcol == col)

    for coord in pieces:
        col, p = board[coord]
        # TODO: probably this should be a Chess method, so that I would have better ways to handle pawns
        if p == 'P':
            dy = -1 if col == 'W' else 1
            if tile[1] == coord[1] + dy and abs(tile[0] - coord[0]) == 1:
                return coord
        else:
            for m in available_piece_moves(board, coord, free_cell=free_cell, block_cell=block_cell):
                if m == tile:
                    return coord
    return False


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
    def __init__(self):
        super().__init__()
        self.draw_turn_counter = 0
        self.available_ep = None  # "enpassable" piece
        # list variables defined here have None as first element, so that I can access them by player_id
        self.available_castles = [None, {(2, 7), (6, 7)}, {(2, 0), (6, 0)}]
        self._kings = [None, (4, 7), (4, 0)]
        self._player_pieces = [None, {(x, y) for x in range(8) for y in range(6, 8)},
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
        new._kings = list(self._kings)
        new._player_pieces = [None] + [pp.copy() for pp in self._player_pieces[1:]]
        new.tomove = self.tomove
        new.board = self.board.copy()

    def setup(self):
        ref_logger.info('starting game')
        return [['WHITE'], ['BLACK']]

    def get_board(self, player_id):
        return [self.moves[-1] if self.moves else NULLMOVE]

    def available_moves(self, player_id, starting_tile=None):
        b = self.board
        tiles = (starting_tile, ) if starting_tile else self._player_pieces[player_id]
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
                if starting_tile == KING_HOUSES[player_id]:
                    for m in self.available_castles[player_id]:
                        c2x, c2y = m
                        for i, tile in enumerate((t, (3, c2y) if c2x == 2 else (5, c2y), m)):
                            # here enumerate is used only to exclude first element from the first check
                            if i and b[tile] != EMPTY or check_menace(b, tile, (player_id % 2) + 1):
                                break
                        else:
                            yield (t, m)

    def valid_pawn_moves(self, player_id, starting_tile):
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
        if b[c] == EMPTY:
            yield c
            # double movement from starting position
            c = sx, sy + dy * 2
            if (sy - 1 * dy) % 7 == 0 and b[c] == EMPTY:
                yield c
        # capture
        for dx in (-1, 1):
            c = sx + dx, sy + dy
            if 0 <= sx + dx < 8 and (b[c][0] == oppo or self.available_ep == (sx + dx, sy)):
                yield c

    def exposes_to_check(self, player_id, starting_tile, target_tile):
        b = self.board
        if b[starting_tile][-1] == 'K':
            return check_menace(b, target_tile, pieces=self._player_pieces[(player_id % 2) + 1],
                                free_cell=starting_tile)
        else:
            return check_menace(b, self._kings[player_id], pieces=self._player_pieces[(player_id % 2) + 1],
                                free_cell=starting_tile, block_cell=target_tile)

    def execute_turn(self, player_id, strmove):
        b = self.board
        pp = self._player_pieces

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

        if all(m != (starting_tile, target_tile) for m in self.available_moves(player_id, starting_tile)):
            raise InvalidMove('invalid move "{}"'.format(strmove))

        # ladies and gentleman, the move!
        self.moves.append(strmove)
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
            self._kings[player_id] = target_tile
        if ac:
            if piece == 'R':
                rc = ROOK_CASTLE.get(starting_tile)
                if rc:
                    ac.discard(rc)
            if piece == 'K':
                ac.clear()

        self.tomove = COLORS[player_id % 2]

        if self.check_checkmate(player_id):
            return player_id
        if self.check_draw():
            return DRAW

        return RUNNING

    def check_draw(self):
        pp = self._player_pieces
        return self.draw_turn_counter == 100 or len(pp[1]) == len(pp[2]) == 1

    def check_checkmate(self, player_id):
        '''
            returns True if player {player_id} made checkmate with last move
        '''
        b = self.board
        pp = self._player_pieces
        other_player = (player_id % 2) + 1
        other_king = self._kings[other_player]
        check = check_menace(b, other_king, pieces=pp[player_id])
        if check:  # check
            ref_logger.info('opposing king %s under check from %s, looking for mate', other_king, check)
            if any(self.available_moves(other_player)):
                return False
            return True
        return False

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
