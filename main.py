import chess

# Estimates of the value of a piece, taken from AlphaZero
PAWN_VALUE = 100
KNIGHT_VALUE = 305
BISHOP_VALUE = 333
ROOK_VALUE = 563
QUEEN_VALUE = 950

# Used for alpha, beta, and mates:
MATE_VALUE = 100000
POS_MAX = 1000000
NEG_MAX = -1000000

# Tables that hold positional values for each piece.  Positive values mean a given
# square on the board is good for that piece.  The king was two tables, one for
# the endgame (when it is better to be active) and one for before (when it is better
# to be safe).
pawntable = [
    0,  0,  0,  0,  0,  0,  0,  0,
    5, 10, 10, -20, -20, 10, 10,  5,
    5, -5, -10,  0,  0, -10, -5,  5,
    0,  0,  0, 20, 20,  0,  0,  0,
    5,  5, 10, 25, 25, 10,  5,  5,
    10, 10, 20, 30, 30, 20, 10, 10,
    50, 50, 50, 50, 50, 50, 50, 50,
    100,  100,  100,  100,  100,  100,  100,  100]

knighttable = [
    -50, -40, -30, -30, -30, -30, -40, -50,
    -40, -20,  0,  5,  5,  0, -20, -40,
    -30,  5, 10, 15, 15, 10,  5, -30,
    -30,  0, 15, 20, 20, 15,  0, -30,
    -30,  5, 15, 20, 20, 15,  5, -30,
    -30,  0, 10, 15, 15, 10,  0, -30,
    -40, -20,  0,  0,  0,  0, -20, -40,
    -50, -40, -30, -30, -30, -30, -40, -50]

bishoptable = [
    -20, -10, -10, -10, -10, -10, -10, -20,
    -10,  5,  0,  0,  0,  0,  5, -10,
    -10, 10, 10, 10, 10, 10, 10, -10,
    -10,  0, 10, 10, 10, 10,  0, -10,
    -10,  5,  5, 10, 10,  5,  5, -10,
    -10,  0,  5, 10, 10,  5,  0, -10,
    -10,  0,  0,  0,  0,  0,  0, -10,
    -20, -10, -10, -10, -10, -10, -10, -20]

rooktable = [
    0,  0,  0,  5,  5,  0,  0,  0,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    5, 10, 10, 10, 10, 10, 10,  5,
    0,  0,  0,  0,  0,  0,  0,  0]

queentable = [
    -20, -10, -10, -5, -5, -10, -10, -20,
    -10,  0,  0,  0,  0,  0,  0, -10,
    -10,  5,  5,  5,  5,  5,  0, -10,
    0,  0,  5,  5,  5,  5,  0, -5,
    -5,  0,  5,  5,  5,  5,  0, -5,
    -10,  0,  5,  5,  5,  5,  0, -10,
    -10,  0,  0,  0,  0,  0,  0, -10,
    -20, -10, -10, -5, -5, -10, -10, -20]

kingtable = [
    20, 30, 10,  0,  0, 10, 30, 20,
    20, 20,  0,  0,  0,  0, 20, 20,
    -10, -20, -20, -20, -20, -20, -20, -10,
    -20, -30, -30, -40, -40, -30, -30, -20,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30]

kingtableend = [
    -50, -30, -30, -30, -30, -30, -30, -50,
    -30, -30,  0,  0,  0,  0, -30, -30,
    -30, -10, 20, 30, 30, 20, -10, -30,
    -30, -10, 30, 40, 40, 30, -10, -30,
    -30, -10, 30, 40, 40, 30, -10, -30,
    -30, -10, 20, 30, 30, 20, -10, -30,
    -30, -20, -10,  0,  0, -10, -20, -30,
    -50, -40, -30, -20, -20, -30, -40, -50]

# Function that uses the above tables, accounting for color and endgame


def positionalValue(square, piece, color, endgame):
    square = square if color else 63 - square
    if piece == chess.PAWN:
        return pawntable[square]
    if piece == chess.KNIGHT:
        return knighttable[square]
    if piece == chess.BISHOP:
        return bishoptable[square]
    if piece == chess.ROOK:
        return rooktable[square]
    if piece == chess.QUEEN:
        return queentable[square]
    if piece == chess.KING:
        return kingtableend[square] if endgame else kingtable[square]

# Class that runs the bot


class Bot:

    def __init__(self, depth, pos='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'):
        self._board = chess.Board(fen=pos)
        self._leaves = 0
        self._maxdepth = depth

    # Generate all legal moves and sort according to heuristic
    def gen_moves(self):
        movelist = list(self._board.legal_moves)

        def heuristic(move):
            # Castling is special, so fix value
            if b.is_castling(move):
                return 200
            score = 0
            piece = self._board.piece_at(move.from_square).piece_type
            # Look at checks first
            if self._board.gives_check(move):
                score += 1000
            # Prioritize captures by the piece captured
            if self._board.is_capture(move):
                if piece == chess.PAWN and self._board.is_en_passant(move):
                    score += PAWN_VALUE
                else:
                    oppiece = self._board.piece_at(move.to_square).piece_type
                    if oppiece == chess.PAWN:
                        score += PAWN_VALUE
                    elif oppiece == chess.KNIGHT:
                        score += KNIGHT_VALUE
                    elif oppiece == chess.BISHOP:
                        score += BISHOP_VALUE
                    elif oppiece == chess.ROOK:
                        score += ROOK_VALUE
                    elif oppiece == chess.QUEEN:
                        score += QUEEN_VALUE
                    else:
                        # should not get here
                        pass
            # Ignore king moves to make this faster to avoid checking endgame
            if not (piece == chess.KING):
                to_pos = positionalValue(
                    move.to_square, piece, self._board.turn, False)
                from_pos = positionalValue(
                    move.from_square, piece, self._board.turn, False)
                score += (to_pos - from_pos)
            return score

        return sorted(movelist, key=heuristic, reverse=True)

    # Generate moves for quiesence search (don't worry about ordering, just get captures)
    def gen_moves_q(self):
        movelist = list(self._board.legal_moves)
        out = []
        for mv in movelist:
            if self._board.is_capture(mv):
                out.append(mv)
        return out

    # Evaluate the position
    def eval(self):
        self._leaves += 1
        # Get all the pieces
        wps = self._board.pieces(chess.PAWN, chess.WHITE)
        bps = self._board.pieces(chess.PAWN, chess.BLACK)
        wns = self._board.pieces(chess.KNIGHT, chess.WHITE)
        bns = self._board.pieces(chess.KNIGHT, chess.BLACK)
        wbs = self._board.pieces(chess.BISHOP, chess.WHITE)
        bbs = self._board.pieces(chess.BISHOP, chess.BLACK)
        wrs = self._board.pieces(chess.ROOK, chess.WHITE)
        brs = self._board.pieces(chess.ROOK, chess.BLACK)
        wqs = self._board.pieces(chess.QUEEN, chess.WHITE)
        bqs = self._board.pieces(chess.QUEEN, chess.BLACK)
        wks = self._board.pieces(chess.KING, chess.WHITE)
        bks = self._board.pieces(chess.KING, chess.BLACK)
        # Calculate material for both sides
        whitematerial = len(wns) * KNIGHT_VALUE + len(wbs) * \
            BISHOP_VALUE + len(wrs) * ROOK_VALUE + len(wqs) * QUEEN_VALUE
        blackmaterial = len(bns) * KNIGHT_VALUE + len(bbs) * \
            BISHOP_VALUE + len(brs) * ROOK_VALUE + len(bqs) * QUEEN_VALUE
        whitepawns = len(wps) * PAWN_VALUE
        blackpawns = len(wps) * PAWN_VALUE
        # Determine if we are in an endgame (useful for king tables, as well as pawn values)
        endgamew = len(wqs) == 0 or whitematerial < 1300
        endgameb = len(bqs) == 0 or blackmaterial < 1300
        endgame = endgamew and endgameb

        # Update material eval with positional eval
        whiteeval = whitematerial + whitepawns
        whiteeval += (1.5 if endgame else 1) * \
            sum([positionalValue(i, chess.PAWN, chess.WHITE, endgame)
                for i in wps])
        whiteeval += sum([positionalValue(i, chess.KNIGHT,
                         chess.WHITE, endgame) for i in wns])
        whiteeval += sum([positionalValue(i, chess.BISHOP,
                         chess.WHITE, endgame) for i in wbs])
        whiteeval += sum([positionalValue(i, chess.ROOK,
                         chess.WHITE, endgame) for i in wrs])
        whiteeval += sum([positionalValue(i, chess.QUEEN,
                         chess.WHITE, endgame) for i in wqs])
        whiteeval += sum([positionalValue(i, chess.KING,
                         chess.WHITE, endgame) for i in wks])

        # Update material eval with positional eval
        blackeval = blackmaterial + blackpawns
        blackeval += (1.5 if endgame else 1) * \
            sum([positionalValue(i, chess.PAWN, chess.BLACK, endgame)
                for i in bps])
        blackeval += sum([positionalValue(i, chess.KNIGHT,
                         chess.BLACK, endgame) for i in bns])
        blackeval += sum([positionalValue(i, chess.BISHOP,
                         chess.BLACK, endgame) for i in bbs])
        blackeval += sum([positionalValue(i, chess.ROOK,
                         chess.BLACK, endgame) for i in brs])
        blackeval += sum([positionalValue(i, chess.QUEEN,
                         chess.BLACK, endgame) for i in bqs])
        blackeval += sum([positionalValue(i, chess.KING,
                         chess.BLACK, endgame) for i in bks])

        # Final eval is difference between sides, depending on turn
        return whiteeval - blackeval if self._board.turn else blackeval - whiteeval

    # If one side has no moves, check if it is checkmated (loss) or stalemated (draw)
    def scoreEnd(self, depth):
        if self._board.is_check():
            return - MATE_VALUE + depth
        else:
            return 0

    # Start the search to a given depth
    def start_search(self, depth=None):
        best_eval = 0
        best_move = chess.Move.null()
        self._leaves = 0
        if depth == None:
            depth = self._maxdepth

        # Standard alpha-beta search
        def search(d, md, alpha, beta):
            nonlocal best_move
            nonlocal best_eval
            if d == md:
                return quiescence_search(alpha, beta)
            moves = self.gen_moves()
            if len(moves) == 0:
                return self.scoreEnd(d)
            for mv in moves:
                self._board.push(mv)
                val = -search(d+1, md, - beta, -alpha)
                self._board.pop()
                if val >= beta:
                    return beta
                if val > alpha:
                    alpha = val
                    if d == 0:
                        best_move = mv
                        best_eval = val
            return alpha

        # Quiesence search: check captures until we reach a quiet position
        def quiescence_search(alpha, beta):
            standpat = self.eval()
            if standpat >= beta:
                return beta
            if alpha < standpat:
                alpha = standpat
            for mv in self.gen_moves_q():
                self._board.push(mv)
                val = -quiescence_search(-beta, -alpha)
                self._board.pop()
                if val >= beta:
                    return beta
                if val > alpha:
                    alpha = val
            return alpha
        search(0, depth, NEG_MAX, POS_MAX)
        return (best_eval, best_move)
