import chess

# From AlphaZero
PAWN_VALUE = 100
KNIGHT_VALUE = 305
BISHOP_VALUE = 333
ROOK_VALUE = 563
QUEEN_VALUE = 950

# Used for alpha, beta, and mates:
MATE_VALUE = 100000
POS_MAX = 1000000
NEG_MAX = -1000000

#Tables used to estimate positional value of pieces based on square
pawntable = [
 0,  0,  0,  0,  0,  0,  0,  0,
 5, 10, 10,-20,-20, 10, 10,  5,
 5, -5,-10,  0,  0,-10, -5,  5,
 0,  0,  0, 20, 20,  0,  0,  0,
 5,  5, 10, 25, 25, 10,  5,  5,
10, 10, 20, 30, 30, 20, 10, 10,
50, 50, 50, 50, 50, 50, 50, 50,
 100,  100,  100,  100,  100,  100,  100,  100]
knightstable = [
-50,-40,-30,-30,-30,-30,-40,-50,
-40,-20,  0,  5,  5,  0,-20,-40,
-30,  5, 10, 15, 15, 10,  5,-30,
-30,  0, 15, 20, 20, 15,  0,-30,
-30,  5, 15, 20, 20, 15,  5,-30,
-30,  0, 10, 15, 15, 10,  0,-30,
-40,-20,  0,  0,  0,  0,-20,-40,
-50,-40,-30,-30,-30,-30,-40,-50]
bishopstable = [
-20,-10,-10,-10,-10,-10,-10,-20,
-10,  5,  0,  0,  0,  0,  5,-10,
-10, 10, 10, 10, 10, 10, 10,-10,
-10,  0, 10, 10, 10, 10,  0,-10,
-10,  5,  5, 10, 10,  5,  5,-10,
-10,  0,  5, 10, 10,  5,  0,-10,
-10,  0,  0,  0,  0,  0,  0,-10,
-20,-10,-10,-10,-10,-10,-10,-20]
rookstable = [
  0,  0,  0,  5,  5,  0,  0,  0,
 -5,  0,  0,  0,  0,  0,  0, -5,
 -5,  0,  0,  0,  0,  0,  0, -5,
 -5,  0,  0,  0,  0,  0,  0, -5,
 -5,  0,  0,  0,  0,  0,  0, -5,
 -5,  0,  0,  0,  0,  0,  0, -5,
  5, 10, 10, 10, 10, 10, 10,  5,
 0,  0,  0,  0,  0,  0,  0,  0]
queenstable = [
-20,-10,-10, -5, -5,-10,-10,-20,
-10,  0,  0,  0,  0,  0,  0,-10,
-10,  5,  5,  5,  5,  5,  0,-10,
  0,  0,  5,  5,  5,  5,  0, -5,
 -5,  0,  5,  5,  5,  5,  0, -5,
-10,  0,  5,  5,  5,  5,  0,-10,
-10,  0,  0,  0,  0,  0,  0,-10,
-20,-10,-10, -5, -5,-10,-10,-20]
kingstable = [
 20, 30, 10,  0,  0, 10, 30, 20,
 20, 20,  0,  0,  0,  0, 20, 20,
-10,-20,-20,-20,-20,-20,-20,-10,
-20,-30,-30,-40,-40,-30,-30,-20,
-30,-40,-40,-50,-50,-40,-40,-30,
-30,-40,-40,-50,-50,-40,-40,-30,
-30,-40,-40,-50,-50,-40,-40,-30,
-30,-40,-40,-50,-50,-40,-40,-30]

#Function that uses the above tables, accounting for color  
def positionalValue(square, piece, color):
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
        return kingtable[square]

#Class that runs the bot
class Bot:

    #Initializes relevant values, including start position
    def __init__(self, depth, pos = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'):
        self._board = chess.Board(fen = pos)
        self._leaves = 0
        self._maxdepth = depth
    
    # Generate all legal moves and sort according to heuristic
    def gen_moves(self):
        movelist = list(self._board.legal_moves)
        #Heuristic that defines move ordering
        def heuristic(move):
            #Fixed value for castling, as it's very unique 
            if b.is_castling(move):
                return 200
            score = 0
            #Determine which piece is moving
            piece = self._board.piece_at(move.from_square).piece_type
            #Look at all checks first
            if self._board.gives_check(move):
                score += 1000
            #Look at captures next, prioritizing capturing valuable pieces 
            if self._board.is_capture(move):
                #See if it's en passant (causes error with oppiece otherwise)
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
                        #should not get here, king cannot be captured
                        pass
            #See which moves improve positioning of pieces
            to_pos = positionalValue(move.to_square,piece,self._board.turn)
            from_pos = positionalValue(move.from_square,piece,self._board.turn)
            score += (to_pos - from_pos)
            return score
        #Sort list according to heuristic
        return sorted(movelist, key = heuristic, reverse = True)
    
    #Evaluate a position.  Currently, we just use material difference.
    def eval(self):
        self._leaves += 1
        pawndiff = len(self._board.pieces(chess.PAWN, chess.WHITE)) - \
            len(self._board.pieces(chess.PAWN, chess.BLACK))
        knightdiff = len(self._board.pieces(chess.KNIGHT, chess.WHITE)) - \
            len(self._board.pieces(chess.KNIGHT, chess.BLACK))
        bishopdiff = len(self._board.pieces(chess.BISHOP, chess.WHITE)) - \
            len(self._board.pieces(chess.BISHOP, chess.BLACK))
        rookdiff = len(self._board.pieces(chess.ROOK, chess.WHITE)) - \
            len(self._board.pieces(chess.ROOK, chess.BLACK))
        queendiff = len(self._board.pieces(chess.QUEEN, chess.WHITE)) - \
            len(self._board.pieces(chess.QUEEN, chess.BLACK))
        material = pawndiff * PAWN_VALUE + knightdiff * KNIGHT_VALUE + bishopdiff * \
            BISHOP_VALUE + rookdiff * ROOK_VALUE + queendiff * QUEEN_VALUE
        return material if self._board.turn else -material

    #If no moves left, determine if checkmate or stalemate
    def scoreEnd(self,depth):
        if self._board.is_check():
            #Prioritize faster mates
            return - MATE_VALUE + depth
        else:
            return 0 
    
    #Start the search
    def start_search(self, depth=None):
        best_eval = 0
        best_move = chess.Move.null()
        self._leaves = 0
        if depth == None:
            depth = self._maxdepth

        #Recursive function performing search
        def search(d, md, alpha, beta):
            nonlocal best_move
            nonlocal best_eval
            #If we hit depth, return eval
            if d == md:
                return self.eval()
            #Generate moves
            moves = self.gen_moves()
            if len(moves) == 0:
                return self.scoreEnd(d)
            for mv in moves:
                self._board.push(mv)
                #Search further down game tree
                val = -search(d+1, md, - beta, -alpha)
                self._board.pop()
                #Prune these nodes, as opponent can avoid
                if val >= beta:
                    return beta
                #New best move 
                if val > alpha:
                    alpha = val
                    if d == 0:
                        best_move = mv
                        best_eval = val
            return alpha
        #Call search with initial alpha and beta 
        search(0,depth,NEG_MAX, POS_MAX)
        #For testing purposes, return best evaluation along with the move 
        return (best_eval,best_move)
