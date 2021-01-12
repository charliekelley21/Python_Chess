"""
This class is responsible for storing all the information about the current state of a chess game.
It will aslo be responsible for determining the valid moves at the current state. It will also keep a move log
"""
class GameState():
    def __init__(self):
        #possible improvment - using numPy arrays
        #using 8x8 2-D list, each element has two characters
        #   1st char - color of piece: "b" or "w"
        #   2nd char - type of piece: "R", "N", "B", "Q", "K", or "P"
        # "--" respresents an empty space
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"], # from white's perspective
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.moveFunctions = {'P': self.get_pawn_moves, 'R': self.get_rook_moves, 'N': self.get_knight_moves,
                                'B': self.get_bishop_moves, 'Q': self.get_queen_moves, 'K': self.get_king_moves}
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.inCheck = False
        self.staleMate = False
        self.enpassantPossible = () #coordinates for the square where en passant capture is possible
        self.pins = []
        self.checks = []

    '''
    Takes a move as a parameter and exectues it ( will not work with castling, pawn promotion, en-passant)
    '''
    def make_move(self, move):
        self.board[move.end[0]][move.end[1]] = move.pieceMoved
        self.board[move.start[0]][move.start[1]] = "--"
        self.moveLog.append(move) #log to undo later or print moveLog
        self.whiteToMove = not self.whiteToMove #swap players
        if move.pieceMoved == "wK":
            self.whiteKingLocation = move.end
        elif move.pieceMoved == "bK":
            self.blackKingLocation = move.end
        #pawn promotion
        if move.isPawnPromotion:
            self.board[move.end[0]][move.end[1]] = move.pieceMoved[0] + "Q"
    '''
    Undo the last move made
    '''
    def undo_move(self):
        if len(self.moveLog) != 0: #there is a move to undo
            move = self.moveLog.pop()
            self.board[move.start[0]][move.start[1]] = move.pieceMoved
            self.board[move.end[0]][move.end[1]] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            if move.pieceMoved == "wK":
                self.whiteKingLocation = move.start
            elif move.pieceMoved == "bK":
                self.blackKingLocation = move.start

    '''
    All moves considering checks
    '''
    def get_valid_moves(self):
        moves = []
        self.inCheck, self.pins, self.checks = self.check_pins_checks()
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        if self.inCheck:
            if len(self.checks) == 1: #only checked by one piece
                moves = self.get_all_possible_moves()
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol]
                validSquares = []
                if pieceChecking[1] == 'N':
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i)
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:
                            break
                #get rid of any moves that dont block check or move kig
                for i in range(len(moves) - 1, -1, -1):
                    if moves[i].pieceMoved[1] != 'K': #move doesnt block king
                        if not (moves[i].end[0], moves[i].end[1]) in validSquares:
                            moves.remove(moves[i])
            else:#double check, ust move king
                self.get_king_moves(kingRow, kingCol, moves)
        else:#not in check
            moves = self.get_all_possible_moves()

        return moves

    '''
    All moves without considering checks
    '''
    def get_all_possible_moves(self):
        moves = []
        for r in range(len(self.board)): #number of rows
            for c in range(len(self.board[r])): #number of collumns in given row
                turn = self.board[r][c][0] #color of piece ar (r, c)
                if ((turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove)):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves)
        return moves
    '''
    Get all possible moves for a given pawn
    '''
    def get_pawn_moves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        #black pawns move down board, white up the board
        #pawn has two avaiable moves on first move
        if self.whiteToMove: #white's turn
            if self.board[r-1][c] == "--": #one square pawn advance
                if not piecePinned or pinDirection == (-1, 0):
                    moves.append(Move((r, c), (r-1, c), self.board))
                    if r == 6 and self.board[r-2][c] == "--": #two square pawn advance
                        moves.append(Move((r, c), (r-2, c), self.board))
            if c-1 >= 0 and self.board[r-1][c-1][0] == "b":
                if not piecePinned or pinDirection == (-1, -1):
                    moves.append(Move((r, c), (r-1, c-1), self.board))
            if c+1 <= 7 and self.board[r-1][c+1][0] == "b":
                if not piecePinned or pinDirection == (-1, 1):
                    moves.append(Move((r, c), (r-1, c+1), self.board))
        else:#black pawn moves
            if self.board[r+1][c] == "--": #one square pawn advance
                if not piecePinned or pinDirection == (1, 0):
                    moves.append(Move((r, c), (r+1, c), self.board))
                    if r == 1 and self.board[r+2][c] == "--": #two square pawn advance
                        moves.append(Move((r, c), (r+2, c), self.board))
            if c-1 >= 0 and self.board[r+1][c-1][0] == "w":
                if not piecePinned or pinDirection == (1, -1):
                    moves.append(Move((r, c), (r+1, c-1), self.board))
            if c+1 <= 7 and self.board[r+1][c+1][0] == "w":
                if not piecePinned or pinDirection == (1, 1):
                    moves.append(Move((r, c), (r+1, c+1), self.board))

    '''
    Get all possible moves for a given rook
    '''
    def get_rook_moves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q':
                    self.pins.remove(self.pins[i])
                break
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8: #onboard
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else: #friendly piece
                            break
                else:
                    break

    '''
    Get all possible moves for a given bishop
    '''
    def get_bishop_moves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q':
                    self.pins.remove(self.pins[i])
                break
        directions = ((-1, -1), (1, 1), (1, -1), (-1, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
                for i in range(1, 8):
                    endRow = r + d[0] * i
                    endCol = c + d[1] * i
                    if 0 <= endRow < 8 and 0 <= endCol < 8: #onboard
                        if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                            endPiece = self.board[endRow][endCol]
                            if endPiece == "--":
                                moves.append(Move((r, c), (endRow, endCol), self.board))
                            elif endPiece[0] == enemyColor:
                                moves.append(Move((r, c), (endRow, endCol), self.board))
                                break
                            else: #friendly piece
                                break
                    else:
                        break

    '''
    Get all possible moves for a given knight
    '''
    def get_knight_moves(self, r, c, moves):
        piecePinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                if self.board[r][c][1] != 'Q':
                    self.pins.remove(self.pins[i])
                break
        shifts = [-2, -1, 1, 2]
        for x in shifts:
            for y in shifts:
                if (0 <= r+y < 8 and 0 <= c+x < 8) and not piecePinned:
                    if (self.board[r+y][c+x] == "--" or self.board[r+y][c+x][0] != self.board[r][c][0]):
                        moves.append(Move((r, c), (r+y, c+x), self.board))
        pass

    '''
    Get all possible moves for a given queen
    '''
    def get_queen_moves(self, r, c, moves):
        self.get_rook_moves(r, c, moves)
        self.get_bishop_moves(r, c, moves)

    '''
    Get all possible moves for a given king
    '''
    def get_king_moves(self, r, c, moves):
        allyColor = "w" if self.whiteToMove else "b"
        for x in range(-1, 2):
            for y in range(-1, 2):
                if (0 <= r+y < 8 and 0 <= c+x < 8):
                    endRow = r + y
                    endCol = c + x
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != allyColor:
                        #place king and check for checks
                        if allyColor == "w":
                            self.whiteKingLocation = (endRow, endCol)
                        else:
                            self.blackKingLocation = (endRow, endCol)
                        inCheck, pins, checks = self.check_pins_checks()
                        if not inCheck:
                            moves.append(Move((r,c), (endRow, endCol), self.board))
                        if allyColor == "w":
                            self.whiteKingLocation = (r, c)
                        else:
                            self.blackKingLocation = (r, c)

                        moves.append(Move((r, c), (r+y, c+x), self.board))

    def check_pins_checks(self):
        pins = []
        checks = []
        inCheck = False
        if self.whiteToMove:
            enemyColor = "b"
            allyColor = "w"
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = "w"
            allyColor = "b"
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
        directions = ((-1, 0), (0, 1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = ()
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != 'K':
                        if possiblePin == ():
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else:
                            break
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]
                        if (0 <= j <= 3 and type == 'R') or \
                                (4 <= j <= 7 and type == 'B') or \
                                (i == 1 and type == 'P' and ((enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5))) or \
                                (type == 'Q') or (i == 1 and type == 'K'):
                            if possiblePin == (): #no piece blocking so check
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else: #piece blocking so pin
                                pins.append(possiblePin)
                else:
                        break #offboard
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == 'N': #enemy knight
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))
        return inCheck, pins, checks


class Move():
    # map keys to values
    # key : value
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v:k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v:k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnpassantMove=False):
        self.start = startSq
        self.end = endSq
        self.pieceMoved = board[self.start[0]][self.start[1]]
        self.pieceCaptured = board[self.end[0]][self.end[1]]
        self.moveID = 1000*self.start[0] + 100*self.start[1] + 10*self.end[0] + self.end[1]
        #pawn promotion
        self.isPawnPromotion = ((self.pieceMoved == "wP" and self.end[0] == 0) or (self.pieceMoved == "bP" and self.end[0] == 7))
        #en passant
        self.isEnpassantMove = isEnpassantMove

    '''
    Overriding the equals method
    '''
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID

    def get_chess_notation(self): #modify to include full chess notation
        return self.get_rank_file(self.start[0], self.start[1]) + self.get_rank_file(self.end[0], self.end[1])

    def get_rank_file(self, row, col):
        return self.colsToFiles[col] + self.rowsToRanks[row]
