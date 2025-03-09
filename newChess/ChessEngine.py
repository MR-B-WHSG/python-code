"""
This file is responsible for storing all the information about the
state of the Chess Game. It is also responsible for validating moves
made by the user. It will also keep a move log.
"""
import pygame


class GameState:
    def __init__(self):

        # Chess board is a 8x8 2D list, each element represents a chess piece and is 2 characters

        # The first character is the colour, 'b' or 'w'
        # Second Character is the piece name, 'K', 'N', 'R', B', 'P', 'Q'
        # "--" represents an empty space on the chess board that has no piece
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]

        self.moveMapping = {
            'p': self.get_pawn_moves,
            'R': self.get_rook_moves,
            'N': self.get_knight_moves,
            'B': self.get_bishop_moves,
            'Q': self.get_queen_moves,
            'K': self.get_king_moves
        }

        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)  # Exact location of white king
        self.blackKingLocation = (0, 4)

        self.inCheck = False
        self.pins = []  # list of pinned pieces
        self.checks = []
        self.checkmate = False
        self.stalemate = False
        self.enpassantPossible = ()  # These are the coordinates for the square where it is possible to do en passant
        self.enpassantPossibleLog = [self.enpassantPossible]

        # Castle Rights
        self.whiteCastleKing_side = True
        self.whiteCastleQueen_side = True
        self.blackCastleKing_side = True
        self.blackCastleQueen_side = True
        self.castleRightsLog = [CastleRights(self.whiteCastleKing_side, self.blackCastleKing_side,
                                             self.whiteCastleQueen_side,
                                             self.blackCastleQueen_side)]  # Keeps track of the castles available

    def make_move(self, move):
        self.board[move.endRow][move.endCol] = move.pieceMoved  # new position of the piece on the board
        self.board[move.startRow][move.startCol] = '--'  # Replaces the initial position of the piece with a blank space
        self.moveLog.append(move)  # Keeps track of the move in order to undo
        self.whiteToMove = not self.whiteToMove  # Switches turns

        # Updating the location of the king once moved
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)

        # Pawn Promotion
        running = True
        if move.isPawnPromotion:
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_q:
                            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'
                            running = False
                        if event.key == pygame.K_r:
                            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'R'
                            running = False
                        if event.key == pygame.K_b:
                            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'B'
                            running = False
                        if event.key == pygame.K_k:
                            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'N'
                            running = False

        # En Passant Move
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = '--'  # Captures the pawn

        # Updating the enpassant possible variable
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
            # Should only update the variable when a pawn has moved two squares
            self.enpassantPossible = ((move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.enpassantPossible = ()

        self.enpassantPossibleLog.append(self.enpassantPossible)

        # Updating the rights to castle - Only when the rook or the king moves
        self.update_castle_rights(move)
        self.castleRightsLog.append(CastleRights(self.whiteCastleKing_side, self.blackCastleKing_side,
                                                 self.whiteCastleQueen_side, self.blackCastleQueen_side))

        # Castling Moves
        if move.castle:
            if move.endCol - move.startCol == 2:  # King_side castle
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]  # Moves the rook
                self.board[move.endRow][move.endCol + 1] = '--'  # Empty space where the Rook was
            else:  # Queen_side Castling
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]  # Moves the rook
                self.board[move.endRow][move.endCol - 2] = '--'  # Empty space where the Rook was

    def get_valid_moves(self):
        pass

    def get_pawn_moves(self):
        pass

    def get_rook_moves(self):
        pass

    def get_knight_moves(self):
        pass

    def get_bishop_moves(self):
        pass

    def get_queen_moves(self):
        pass

    def get_king_moves(self):
        pass

    def update_castle_rights(self, move):
        pass

class CastleRights:
    def __init__(self, white_king_side, black_king_side, white_queen_side, black_queen_side):
        self.whiteKingSide = white_king_side
        self.blackKingSide = black_king_side
        self.whiteQueenSide = white_queen_side
        self.blackQueenSide = black_queen_side


''''
Will undo the last move made
'''
def undo_move(self):

    if len(self.moveLog) != 0: #Makes sure that the user has made a move previously

        move = self.moveLog.pop() #returns and deletes the last move

        self.board[move.startRow][move.startCol] = move.pieceMoved

        self.board[move.endRow][move.endCol] = move.pieceCaptured

        self.whiteToMove = not self.whiteToMove #Switches turns back to original user

        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.startRow,
            move.startCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.startRow,
            move.startCol)

        #Undoing enpassant move
        if move.isEnpassantMove:

            self.board[move.endRow][move.endCol] = '--'
            #Removes the pawn that was moved

            self.board[move.startRow][move.endCol] = move.pieceCaptured #Puts the opponent's pawn back onto the correct square

            self.enpassantPossibleLog.pop() #Gets rid of the last item

            self.enpassantPossible = self.enpassantPossibleLog[-1]
            #sets the new items to the value of the last item in the log

        #Undoing Castling Rights
        self.castleRightsLog.pop() #Getting rid of the new castle rights from the move that is being undone
        castle_rights = self.castleRightsLog[-1] #sets the current castle rights to the last one in the list
        self.whiteCastleKing_side = castle_rights.wks
        self.blackCastleKing_side = castle_rights.bks
        self.whiteCastleQueen_side = castle_rights.wqs
        self.blackCastleQueen_side = castle_rights.bqs

        #Undoing a Castle
        if move.castle:

            if move.endCol - move.startCol == 2: # King_side castle

                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1] # Moves the rook

                self.board[move.endRow][move.endCol - 1] = '--'
                # Empty space where the Rook was

            else: # Queen_side Castling
                self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][ move.endCol + 1] # Moves the rook
                self.board[move.endRow][move.endCol + 1] = '--'

                # Empty space where the Rook was

        self.checkmate = False
        self.stalemate = False

'''
Will update the rights to castle based on the move
'''
def update_castle_rights(self, move):

    if move.pieceMoved == 'wK':
        self.whiteCastleQueen_side = False
        self.whiteCastleKing_side = False

    elif move.pieceMoved == 'bk':
        self.blackCastleQueen_side = False
        self.blackCastleKing_side = False

    elif move.pieceMoved == 'wR':
        if move.startRow == 7:

            if move.startCol == 0: #left Rook
                self.whiteCastleQueen_side = False

            elif move.startCol == 7: #Right Rook
                self.whiteCastleKing_side = False

    elif move.pieceMoved == 'bR':
        if move.startRow == 0:

            if move.startCol == 0: #left Rook
                self.blackCastleQueen_side = False

            elif move.startCol == 7: #Right Rook
                self.blackCastleKing_side = False

'''
function for valid moves
'''
def get_valid_moves(self):

    moves = []
    self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
    if self.whiteToMove:
        king_row = self.whiteKingLocation[0]
        king_col = self.whiteKingLocation[1]
    else:
        king_row = self.blackKingLocation[0]
        king_col = self.blackKingLocation[1]

    if self.inCheck:
        if len(self.checks) == 1:  # Single Check
            moves = self.getAllPossibleMoves()
            # Blocking a check means you have to move a piece
            # between the enemy piece and the king
            check = self.checks[0]  # Checks the information about
            # the check
            check_row = check[0]
            check_col = check[1]
            piece_causing_check = self.board[check_row][check_col]

            # Gets the piece that is causing the check
            valid_squares = []  # Squares that can be moved to
            # if the piece causing the check is a knight, the king
            # must be moved or the knight must be captured
            if piece_causing_check[1] == 'N':
                valid_squares = [(check_row, check_col)]  # The only piece you can capture is the knight
            else:
                for i in range(1, 8):
                    valid_square = (king_row + check[2] * i,
                                   king_col + check[3] * i)  # check[2] and check[3] are the directions of the check

                    valid_squares.append(valid_square)
                    if valid_square[0] == check_row and valid_square[1] == check_col:  # Once you get to the piece the check must end

                        break
                # Need to get rid of any moves that do not block the
                # check or move the king
                for i in range(len(moves) - 1, -1, -1):
                    if moves[i].pieceMoved[1] != 'K':  # If the move
                        # doesn't move the king then it must block or capture
                        if not (moves[i].endRow, moves[i].endCol) in valid_squares:  # move doesn't block the check or capture the piece
                            moves.remove(moves[i])
                    else:  # the check is a double check so the king must move
                        self.getKingMoves(king_row, king_col, moves)
    else:  # King is not in check
        moves = self.getAllPossibleMoves()

    if len(moves) == 0:
        if self.inCheck:
            self.checkmate = True
        else:
            self.stalemate = True
    else:
        self.checkmate = False
        self.stalemate = False

    return moves
def square_under_attack(self, r, c, friendly):
    enemy_colour = 'w' if friendly == 'b' else 'b'
    directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
    for j in range(len(directions)):

        d = directions[j]
        possible_pin = ()
        for i in range(1, 8):

            end_row = r + d[0] * i
            end_col = c + d[1] * i
            if 0 <= end_row < 8 and 0 <= end_col < 8:

                end_piece = self.board[end_row][end_col]
                if end_piece[0] == friendly: # there is no attack in that direction
                    break

                elif end_piece[0] == enemy_colour:
                    move_type = end_piece[1]
                    if (0 <= j <= 3 and move_type == 'R') or \
                            (4 <= j <= 7 and move_type == 'B') or \
                            (i == 1 and move_type == 'p' and
                             ((enemy_colour == 'w' and 6 <= j <= 7) or (enemy_colour == 'b' and 4 <= j <= 5))) or \
                            (move_type == 'Q') or (i == 1 and move_type == 'K'):
                        return True
                    else: # There are no impending checks by the enemy piece
                        break

                else:
                    break
    # Check for Knight Checks
    directions = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2),
                  (1, 2), (2, -1), (2, 1))
    for m in directions:

        end_row = r + m[0]
        end_col = c + m[1]
        if 0 <= end_row < 8 and 0 <= end_col < 8:

            end_piece = self.board[end_row][end_col]
            if end_piece[0] == enemy_colour and end_piece[1] == 'N':
                # Checks if the enemy Knight is attacking the king
                return True

    return False
def check_for_pins_and_checks(self):
    pins = []
    checks = []
    in_check = False
    if self.whiteToMove:
        enemy_colour = 'b'
        friendly = 'w'
        start_row = self.whiteKingLocation[0]
        start_col = self.whiteKingLocation[1]
    else:
        enemy_colour = 'w'
        friendly = 'b'
        start_row = self.blackKingLocation[0]
        start_col = self.blackKingLocation[1]

    # Checking from the king's location outwards for pins and checks - keeping track of them
    directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))

    for j in range(len(directions)):
        d = directions[j]
        possible_pin = ()
        for i in range(1, 8):
            end_row = start_row + d[0] * i
            end_col = start_col + d[1] * i
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == friendly and end_piece[1] != 'K':
                    # removes the possibility of the king being able to move in the same direction away from enemy piece whilst still being in check.
                    if possible_pin == ():  # the first friendly piece could be pinned
                        possible_pin = (end_row, end_col, d[0], d[1])
                    else:  # no pin or check possible in this direction as it is the second friendly piece
                        break
                elif end_piece[0] == enemy_colour:
                    move_type = end_piece[1]
                    '''
                    There are 5 possibilities for a piece to be pinned/checked:
                    1 - The piece is in front/behind or to the left/right of the king and is a Rook
                    2 - The piece is diagonally away from the King and is Bishop
                    3 - the piece is 1 square away diagonally from the King and is a pawn
                    4 - The piece is in any direction and is a Queen
                    5 - The piece is 1 square away in any direction and is a King (Kings cannot be next to each other)
                    '''
                    if (0 <= j <= 3 and move_type == 'R') or \
                            (4 <= j <= 7 and move_type == 'B') or \
                            (i == 1 and move_type == 'p' and
                             ((enemy_colour == 'w' and 6 <= j <= 7) or (enemy_colour == 'b' and 4 <= j <= 5))) or \
                            (move_type == 'Q') or (i == 1 and move_type == 'K'):
                        if possible_pin == ():  # if there are no pins, there must be a check
                            in_check = True
                            checks.append((end_row, end_col, d[0], d[1]))
                        break
                    else:  # There is a piece blocking so there must be a pin
                        pins.append(possible_pin)
                        break
                else:  # There are no impending checks by the enemy piece
                    break
            else:
                break
    # Check for Knight Checks
    directions = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2),
                  (1, 2), (2, -1), (2, 1))
    for m in directions:
        end_row = start_row + m[0]
        end_col = start_col + m[1]
        if 0 <= end_row < 8 and 0 <= end_col < 8:
            end_piece = self.board[end_row][end_col]
            if end_piece[0] == enemy_colour and end_piece[1] == 'N':
                # Checks if the enemy Knight is attacking the king
                in_check = True
                checks.append((end_row, end_col, m[0], m[1]))

    return in_check, pins, checks
'''
function for all the moves
'''
def get_all_possible_moves(self):

    moves = [] #Starting with an empty list
    for r in range(len(self.board)): #Will go through the board 8 times for each row
        for c in range(len(self.board[r])): #Goes through the columns in each row
            turn = self.board[r][c][0] #Gives the first character of each piece
            if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                piece = self.board[r][c][1]
                self.moveMapping[piece](r, c, moves) #Calls the appropriate function based on the piece selected
    return moves
'''
Gets all the move for pawns and adds these moves to the list
'''
def get_pawn_moves(self, r, c, moves):

    piece_pinned = False
    pin_direction = ()
    for i in range(len(self.pins)-1, -1, -1):

        if self.pins[i][0] == r and self.pins [i][1] == c:
            piece_pinned = True
            pin_direction = (self.pins[i][2], self.pins[i][3])
            self.pins.remove(self.pins[i])
            break

    if self.whiteToMove:
        move_amount = -1
        start_row = 6
        king_row, king_col = self.whiteKingLocation
        enemy_colour = 'b'

    else:
        move_amount = 1
        start_row = 1
        king_row, king_col = self.blackKingLocation
        enemy_colour = 'w'

    # Moving
    if self.board[r + move_amount][c] == '--': # 1 square pawn move
        if not piece_pinned or pin_direction == (move_amount, 0):
            moves.append(Move((r, c), (r + move_amount, c), self.board))

    if r == start_row and self.board[r + 2 * move_amount][c] == '--': # 2 square pawn move
        moves.append(Move((r, c), (r + 2 * move_amount, c), self.board))

    # Capturing
    if c - 1 >= 0:
        if not piece_pinned or pin_direction == (move_amount, -1):
            if self.board[r + move_amount][c - 1][0] == enemy_colour:
                # Diagonal Left Capture
                moves.append(Move((r, c), (r + move_amount, c - 1), self.board))

        if (r + move_amount, c - 1) == self.enpassantPossible:
            is_attacking_piece = is_blocking_piece = False
            if king_row == r:
                if king_col < c: # Checks if the king is left of the pawn
                    inside_range = range(king_col + 1, c - 1)
                    outside_range = range(c + 1, 8) # gives the list of values between pawn and end of the board
                else: # King is to the right of the pawn
                    inside_range = range(king_col - 1, c + 1, -1)
                    outside_range = range(c - 1, -1, -1)

                for i in inside_range:
                    if self.board[r][i] != '--':  # There is a piece blocking
                        is_blocking_piece = True

                for i in outside_range:
                    square = self.board[r][i]
                    if square[0] == enemy_colour and (
                            square[1] == 'R' or square[1] == 'Q'):  # There is an attacking piece
                        is_attacking_piece = True
                    elif square != '--':
                        is_blocking_piece = True
                if not is_attacking_piece or is_blocking_piece:
                    moves.append(Move((r, c), (r + move_amount, c - 1), self.board))

                if c + 1 <= 7:
                    if not piece_pinned or pin_direction == (move_amount, 1):
                        if self.board[r + move_amount][c + 1][0] == enemy_colour:
                            # Diagonal Right Capture
                            moves.append(Move((r, c), (r + move_amount, c + 1), self.board))

                        if (r + move_amount, c + 1) == self.enpassantPossible:
                            is_attacking_piece = is_blocking_piece = False
                if king_row == r:
                    if king_col < c:  # Checks if the king is left of the pawn
                        # inside range is between the king and pawn, outside range is between the pawn and the end of the board
                        inside_range = range(king_col + 1, c)  # gives the list of values between king and pawn
                        outside_range = range(c + 2, 8)  # give list of values between pawn and end of the board
                    else:  # King is to the right of the pawn
                        inside_range = range(king_col - 1, c + 1, -1)
                        outside_range = range(c - 1, -1, -1)

                for i in inside_range:
                    if self.board[r][i] != '--':  # There is a piece blocking
                        is_blocking_piece = True

                for i in outside_range:
                    square = self.board[r][i]
                    if square[0] == enemy_colour and (
                            square[1] == 'R' or square[1] == 'Q'):  # There is an attacking piece
                        is_attacking_piece = True
                    elif square != '--':
                        is_blocking_piece = True
                if not is_attacking_piece or is_blocking_piece:
                    moves.append(Move((r, c), (r + move_amount, c + 1), self.board, is_enpassant_move=True))
'''
Gets all the Rooks moves and adds these moves to the list
'''
def get_rook_moves(self, r, c, moves):

    piece_pinned = False
    pin_direction = ()
    for i in range(len(self.pins) - 1, -1, -1):

        if self.pins[i][0] == r and self.pins[i][1] == c:
            piece_pinned = True
            pin_direction = (self.pins[i][2], self.pins[i][3])
            if self.board[r][c][1] != 'Q': # we cannot get rid of the queen from a pin on the rook moves, we will only remove it on a bishop

             self.pins.remove(self.pins[i])
            break

    #Rooks move--> up, left, down, right
    directions = ((-1,0), (1,0), (0,-1), (0, 1)) #list of
    # tuples of all the possible directions for Rooks
    if self.whiteToMove:

        enemy_colour = 'b'
    else:

        enemy_colour = 'w'
    for d in directions:

        for i in range(1,8):
            end_row = r + d[0] * i #gets all the rows in the given direction
            end_col = c +d[1] * i #Gets all the columns in the given direction
            if 0 <= end_row < 8 and 0 <= end_col < 8: #Checks if the piece is on the board
                if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]): #Checks if the pin is in the direction or the opposite direction as well

                    end_square = self.board[end_row][end_col]
                    if end_square == '--': #checks if the squares in the given direction is empty
                        moves.append(Move((r,c), (end_row, end_col), self.board))
                    elif end_square[0] == enemy_colour: #Checks if the first index of the piece in the underlying text based game is the enemy colour
                        moves.append(Move((r,c), (end_row, end_col), self.board))

                        break
                    else: #when the endSquare is off the board

                        break
                else:

                    break
def get_knight_moves(self, r, c, moves):
    piece_pinned = False
    for i in range(len(self.pins) - 1, -1, -1):

        if self.pins[i][0] == r and self.pins[i][1] == c:
            piece_pinned = True
            self.pins.remove(self.pins[i])
            break

    directions = ((1,-2), (2,-1), (2, 1), (1, 2), (-1, 2), (-2, 1),
                  (-2, -1), (-1, -2))

    if self.whiteToMove:
        friendly = 'w'
    else:
        friendly = 'b'

    for i in directions:
        end_row = r + i[0]
        end_col = c + i[1]
        if 0 <= end_row < 8 and 0 <= end_col < 8:

            if not piece_pinned:
                end_square = self.board[end_row][end_col]
                if end_square[0] != friendly:  # Only have to mention friendly piece
                    moves.append(Move((r, c), (end_row, end_col), self.board))
def get_bishop_moves(self, r, c, moves):
    piece_pinned = False
    pin_direction = ()
    for i in range(len(self.pins) - 1, -1, -1):

        if self.pins[i][0] == r and self.pins[i][1] == c:
            piece_pinned = True
            pin_direction = (self.pins[i][2], self.pins[i][3])
            self.pins.remove(self.pins[i])
            break

    directions = ((-1, -1), (1,-1), (-1, 1), (1, 1))
    if self.whiteToMove:
        enemy_colour = 'b'
    else:
        enemy_colour = 'w'
    for d in directions:

        for i in range(1, 8):
            end_row = r + d[0] * i # gets all the rows in the given direction
            end_col = c + d[1] * i # Gets all the columns in the given direction
            if 0 <= end_row < 8 and 0 <= end_col < 8: # Checks if the piece is on the board
                if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):

                    end_square = self.board[end_row][end_col]
                    if end_square == '--': # checks if the squares in the given direction is empty
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    elif end_square[0] == enemy_colour: # Checks if the first index of the piece in the underlying text based game is the enemy colour
                        moves.append(Move((r, c), (end_row, end_col), self.board))

                        break
                    else: # when the end_square is off the board
                        break
                else:
                    break
def get_queen_moves(self, r, c, moves):
    self.getBishopMoves(r, c, moves)
    self.getRookMoves(r, c, moves)
def get_king_moves(self, r, c, moves):
    row_moves = (-1, -1, -1, 0, 0, 1, 1, 1) #Possible row direction for possible moves
    col_moves = (-1, 0, 1, -1, 1, -1, 0, 1) #Possible column direction for possible moves
    if self.whiteToMove:
        friendly = 'w'
    else:
        friendly = 'b'
    for i in range(8):
        end_row = r + row_moves[i]
        end_col = c + col_moves[i]
        if 0 <= end_row < 8 and 0 <= end_col < 8:
            end_square = self.board[end_row][end_col]
            if end_square[0] != friendly:
                # will place the king on the end square and check for checks
                if friendly == 'w':
                    self.whiteKingLocation = (end_row, end_col)  # temporarily moves king
                else:
                    self.blackKingLocation = (end_row, end_col)  # temporarily moves king

                in_check, pins, checks = self.checkForPinsAndChecks()
                if not in_check:
                    moves.append(Move((r, c), (end_row, end_col), self.board))

                # Placing the king back in its original position
                if friendly == 'w':
                    self.whiteKingLocation = (r, c)
                else:
                    self.blackKingLocation = (r, c)

    self.getCastleMoves(r, c, moves, friendly)
'''
Generating all the valid castle moves for the king at the
specific row and column and adding them to the list of moves
'''

def get_castle_moves(self, r, c, moves, friendly):
    in_check = self.squareUnderAttack(r, c, friendly)
    if in_check:
        return #cannot castle if in check
    if (self.whiteToMove and self.whiteCastleKingside) or (not self.whiteToMove and self.blackCastleKingside):
        self.getKingsideCastleMoves(r, c , moves, friendly)

    if (self.whiteToMove and self.whiteCastleQueenside) or (not self.whiteToMove and self.blackCastleQueenside):
        self.getQueensideCastleMoves(r, c , moves, friendly)

'''
Generates King_side castle moves - will only be called if the
player still has the rights to castle
'''
def get_king_side_castle_moves(self, r, c, moves, friendly):

    if self.board[r][c+1] == '--' and self.board[r][c+2] == '--' and \
       not self.squareUnderAttack(r, c+1, friendly) and not self.squareUnderAttack(r, c+2, friendly):
        moves.append(Move((r, c), (r, c+2), self.board, castle=True))

'''
Generates Queen_side castle moves - will only be called if the
player still has the rights to castle
'''

def get_queen_side_castle_moves(self, r, c, moves, friendly):
    # Will check if the squares between the king and the rook are
    # clear and if the two squares to the left of the king is not under attack

    if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][c-3] == '--' and \
       not self.squareUnderAttack(r, c-1, friendly) and not self.squareUnderAttack(r, c-2, friendly):
        moves.append(Move((r, c), (r, c-2), self.board, castle=True))

class CastleRights:
    def __init__(self, wks, bks, wqs, bqs):

        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move:
    # Creating a dictionary that will map the computer notation of the
    # board into algebraic notation
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, start_sq, end_sq, board, is_enpassant_move=False, castle=False):  # Inclusion of an optional parameter
        self.startRow = start_sq[0]  # startSq is a tuple
        self.startCol = start_sq[1]
        self.endRow = end_sq[0]
        self.endCol = end_sq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]


        self.is_capture = (self.pieceCaptured != '--')  # If a piece is captured, it's not an empty square '--'

        # Pawn Promotion
        self.isPawnPromotion = False  # The game starts off with 0 pawn promotions
        if (self.pieceMoved == 'wp' and self.endRow == 0) or (
                self.pieceMoved == 'bp' and self.endRow == 7):  # These are the conditions for pawn promotion
            self.isPawnPromotion = True

        # En passant
        self.isEnpassantMove = is_enpassant_move
        if self.isEnpassantMove:
            self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'

        self.castle = castle

        self.moveId = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol  # Hash Function - Generates a unique id from 0 to 7777 (Each number represents the start/end row or column)

    '''
    Comparing objects
    '''

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveId == other.moveId
        return False

    def get_chess_notation(self):
        return self.get_rank_file(self.startRow, self.startCol) + self.get_rank_file(self.endRow, self.endCol)

    def get_rank_file(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]

    # overriding the str() function
    def __str__(self):
        # Castle Move
        # 'O-O' is King_side Castle, 'O-O-O' is Queen_side Castle
        if self.castle:
            return "O-O" if self.endCol == 6 else "O-O-O"

        end_square = self.get_rank_file(self.endRow, self.endCol)

        # Pawn Moves
        if self.pieceMoved[1] == 'p':
            if self.is_capture:
                return self.colsToFiles[self.startCol] + 'x' + end_square
            else:
                return end_square

        # piece moves
        move_string = self.pieceMoved[1]
        if self.is_capture:
            move_string += 'x'
        return move_string + end_square