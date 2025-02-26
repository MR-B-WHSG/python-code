#!/usr/bin/env python3
"""
Chess Game using Pygame
------------------------
This is a complete, single–file chess game.
Features:
 • Standard chess rules (including castling, en passant, and pawn promotion)
 • Two modes: Two–player and Single–player (with a simple heuristic AI for black)
 • Top–down view with a 512x512 board and 45x45 piece images centered in each square
 • A simple, modern splash screen for mode selection

Note: The piece images are assumed to be in PNG format.
"""

import pygame
import sys

# Global constants for board and piece sizes
BOARD_SIZE = 512          # Board image is 512x512 pixels
SQUARE_SIZE = BOARD_SIZE // 8  # Each square is 64x64 pixels (512/8)
PIECE_SIZE = 45           # Piece icons are 45x45 pixels

# ------------------------------
# Chess piece class definition
# ------------------------------
class Piece:
    def __init__(self, color, ptype):
        """
        Initialize a chess piece.
        :param color: 'white' or 'black'
        :param ptype: type of piece: 'king', 'queen', 'rook', 'bishop', 'knight', or 'pawn'
        """
        self.color = color
        self.type = ptype
        self.has_moved = False  # Used for castling and pawn's first move

# ------------------------------
# Main Chess Game Class
# ------------------------------
class ChessGame:
    def __init__(self, mode):
        """
        Initialize the chess game.
        :param mode: 1 for single–player (human = white, AI = black), 2 for two–player.
        """
        self.mode = mode
        # Create an 8x8 board (list of lists). Each cell is either None or a Piece.
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.turn = 'white'  # White starts
        self.selected_piece = None    # Currently selected piece (if any)
        self.selected_pos = None      # (col, row) of the selected piece
        self.valid_moves = []         # List of valid moves for the selected piece
        self.en_passant_target = None # Square available for en passant capture (if any)
        self.move_history = []        # History of moves made (for potential further expansion)
        self.load_assets()            # Load board and piece images
        self.initialize_board()       # Set up initial board state

    def load_assets(self):
        """
        Load images for the board and all pieces.
        """
        # Load and scale the board image
        self.board_img = pygame.image.load("assets/board.png")
        self.board_img = pygame.transform.scale(self.board_img, (BOARD_SIZE, BOARD_SIZE))
        # Dictionary to store piece images with keys: (color, piece_type)
        self.images = {}
        pieces = ['king', 'queen', 'rook', 'bishop', 'knight', 'pawn']
        for color in ['white', 'black']:
            for piece in pieces:
                key = (color, piece)
                # Build the file path; note: using 'w' for white and 'b' for black
                path = f"assets/{color}/{'w' if color=='white' else 'b'}{piece}.png"
                img = pygame.image.load(path)
                # Scale the image to PIECE_SIZE x PIECE_SIZE
                self.images[key] = pygame.transform.scale(img, (PIECE_SIZE, PIECE_SIZE))

    def initialize_board(self):
        """
        Set up the board with pieces in their standard starting positions.
        White pieces are on rows 7 and 6; Black pieces on rows 0 and 1.
        """
        # White pieces (back rank on row 7)
        self.board[7][0] = Piece('white', 'rook')
        self.board[7][1] = Piece('white', 'knight')
        self.board[7][2] = Piece('white', 'bishop')
        self.board[7][3] = Piece('white', 'queen')
        self.board[7][4] = Piece('white', 'king')
        self.board[7][5] = Piece('white', 'bishop')
        self.board[7][6] = Piece('white', 'knight')
        self.board[7][7] = Piece('white', 'rook')
        # White pawns on row 6
        for col in range(8):
            self.board[6][col] = Piece('white', 'pawn')
        # Black pieces (back rank on row 0)
        self.board[0][0] = Piece('black', 'rook')
        self.board[0][1] = Piece('black', 'knight')
        self.board[0][2] = Piece('black', 'bishop')
        self.board[0][3] = Piece('black', 'queen')
        self.board[0][4] = Piece('black', 'king')
        self.board[0][5] = Piece('black', 'bishop')
        self.board[0][6] = Piece('black', 'knight')
        self.board[0][7] = Piece('black', 'rook')
        # Black pawns on row 1
        for col in range(8):
            self.board[1][col] = Piece('black', 'pawn')

    def draw(self, screen):
        """
        Draw the board and all pieces onto the screen.
        Highlights the selected piece and its valid moves.
        """
        # Draw board background
        screen.blit(self.board_img, (0, 0))
        # Draw each piece on the board
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece is not None:
                    img = self.images[(piece.color, piece.type)]
                    # Center the piece image within the square
                    x = col * SQUARE_SIZE + (SQUARE_SIZE - PIECE_SIZE) // 2
                    y = row * SQUARE_SIZE + (SQUARE_SIZE - PIECE_SIZE) // 2
                    screen.blit(img, (x, y))
        # If a piece is selected, highlight its square and valid moves
        if self.selected_piece is not None:
            highlight = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
            highlight.set_alpha(100)
            highlight.fill((0, 255, 0))
            # Highlight the selected piece's square
            sel_col, sel_row = self.selected_pos
            screen.blit(highlight, (sel_col * SQUARE_SIZE, sel_row * SQUARE_SIZE))
            # Highlight each valid destination square
            for move in self.valid_moves:
                # move is a tuple: (start_col, start_row, end_col, end_row, special)
                end_col, end_row = move[2], move[3]
                screen.blit(highlight, (end_col * SQUARE_SIZE, end_row * SQUARE_SIZE))

    def handle_click(self, pos):
        """
        Process a mouse click at position pos.
        Select a piece if none is selected, or if a valid move is clicked, perform the move.
        """
        col = pos[0] // SQUARE_SIZE
        row = pos[1] // SQUARE_SIZE
        # If no piece is selected yet, try to select one that belongs to the current turn.
        if self.selected_piece is None:
            piece = self.board[row][col]
            if piece is not None and piece.color == self.turn:
                self.selected_piece = piece
                self.selected_pos = (col, row)
                self.valid_moves = self.get_valid_moves(col, row)
        else:
            # If a piece is already selected, check if the click is on a valid destination.
            for move in self.valid_moves:
                if move[2] == col and move[3] == row:
                    self.make_move(move)
                    self.selected_piece = None
                    self.valid_moves = []
                    self.selected_pos = None
                    return
            # If a different piece (of the same color) is clicked, reselect.
            piece = self.board[row][col]
            if piece is not None and piece.color == self.turn:
                self.selected_piece = piece
                self.selected_pos = (col, row)
                self.valid_moves = self.get_valid_moves(col, row)
            else:
                # Click on an invalid square deselects.
                self.selected_piece = None
                self.valid_moves = []
                self.selected_pos = None

    def in_bounds(self, col, row):
        """
        Check if a board coordinate (col, row) is within bounds.
        """
        return 0 <= col < 8 and 0 <= row < 8

    def get_valid_moves(self, col, row):
        """
        Return a list of legal moves for the piece at the given position.
        Each move is represented as a tuple:
          (start_col, start_row, end_col, end_row, special)
        where special is a string that may be:
          'normal', 'promotion', 'en_passant', 'castling_kingside', or 'castling_queenside'
        """
        piece = self.board[row][col]
        if piece is None:
            return []
        moves = []
        # Delegate to the appropriate move generator based on piece type.
        if piece.type == 'pawn':
            moves = self.get_pawn_moves(col, row, piece)
        elif piece.type == 'knight':
            moves = self.get_knight_moves(col, row, piece)
        elif piece.type == 'bishop':
            moves = self.get_bishop_moves(col, row, piece)
        elif piece.type == 'rook':
            moves = self.get_rook_moves(col, row, piece)
        elif piece.type == 'queen':
            moves = self.get_queen_moves(col, row, piece)
        elif piece.type == 'king':
            moves = self.get_king_moves(col, row, piece)
        # Filter out moves that would leave the king in check.
        legal_moves = []
        for move in moves:
            if self.is_move_legal(move):
                legal_moves.append(move)
        return legal_moves

    def get_pawn_moves(self, col, row, piece):
        """
        Generate pawn moves (including captures, two–step move, promotion, and en passant).
        """
        moves = []
        direction = -1 if piece.color == 'white' else 1
        start_row = 6 if piece.color == 'white' else 1
        new_row = row + direction
        # Forward move if square is empty
        if self.in_bounds(col, new_row) and self.board[new_row][col] is None:
            if (piece.color == 'white' and new_row == 0) or (piece.color == 'black' and new_row == 7):
                moves.append((col, row, col, new_row, 'promotion'))
            else:
                moves.append((col, row, col, new_row, 'normal'))
            # Two–step move from starting position if both squares are empty.
            if row == start_row:
                new_row2 = row + 2 * direction
                if self.board[row + direction][col] is None and self.board[new_row2][col] is None:
                    moves.append((col, row, col, new_row2, 'normal'))
        # Captures (diagonally)
        for dc in [-1, 1]:
            new_col = col + dc
            new_row = row + direction
            if self.in_bounds(new_col, new_row):
                target = self.board[new_row][new_col]
                if target is not None and target.color != piece.color:
                    if (piece.color == 'white' and new_row == 0) or (piece.color == 'black' and new_row == 7):
                        moves.append((col, row, new_col, new_row, 'promotion'))
                    else:
                        moves.append((col, row, new_col, new_row, 'normal'))
        # En passant capture
        if self.en_passant_target is not None:
            ep_col, ep_row = self.en_passant_target
            if abs(ep_col - col) == 1 and ep_row == row + direction:
                moves.append((col, row, ep_col, ep_row, 'en_passant'))
        return moves

    def get_knight_moves(self, col, row, piece):
        """
        Generate knight moves in L–shape.
        """
        moves = []
        knight_moves = [(2, 1), (1, 2), (-1, 2), (-2, 1),
                        (-2, -1), (-1, -2), (1, -2), (2, -1)]
        for dc, dr in knight_moves:
            new_col = col + dc
            new_row = row + dr
            if self.in_bounds(new_col, new_row):
                target = self.board[new_row][new_col]
                if target is None or target.color != piece.color:
                    moves.append((col, row, new_col, new_row, 'normal'))
        return moves

    def get_bishop_moves(self, col, row, piece):
        """
        Generate bishop moves (diagonal moves until blocked).
        """
        moves = []
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        for dc, dr in directions:
            new_col, new_row = col, row
            while True:
                new_col += dc
                new_row += dr
                if not self.in_bounds(new_col, new_row):
                    break
                target = self.board[new_row][new_col]
                if target is None:
                    moves.append((col, row, new_col, new_row, 'normal'))
                else:
                    if target.color != piece.color:
                        moves.append((col, row, new_col, new_row, 'normal'))
                    break
        return moves

    def get_rook_moves(self, col, row, piece):
        """
        Generate rook moves (horizontal and vertical until blocked).
        """
        moves = []
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for dc, dr in directions:
            new_col, new_row = col, row
            while True:
                new_col += dc
                new_row += dr
                if not self.in_bounds(new_col, new_row):
                    break
                target = self.board[new_row][new_col]
                if target is None:
                    moves.append((col, row, new_col, new_row, 'normal'))
                else:
                    if target.color != piece.color:
                        moves.append((col, row, new_col, new_row, 'normal'))
                    break
        return moves

    def get_queen_moves(self, col, row, piece):
        """
        Generate queen moves (combining rook and bishop moves).
        """
        return self.get_bishop_moves(col, row, piece) + self.get_rookMoves(col, row, piece)

    def get_rookMoves(self, col, row, piece):
        """
        Helper method for queen moves: same as rook moves.
        """
        return self.get_rook_moves(col, row, piece)

    def get_queen_moves(self, col, row, piece):
        """
        Generate queen moves (combining bishop and rook moves).
        """
        return self.get_bishop_moves(col, row, piece) + self.get_rook_moves(col, row, piece)

    def get_king_moves(self, col, row, piece):
        """
        Generate king moves (one square in any direction plus castling).
        """
        moves = []
        king_moves = [(1, 0), (-1, 0), (0, 1), (0, -1),
                      (1, 1), (1, -1), (-1, 1), (-1, -1)]
        for dc, dr in king_moves:
            new_col = col + dc
            new_row = row + dr
            if self.in_bounds(new_col, new_row):
                target = self.board[new_row][new_col]
                if target is None or target.color != piece.color:
                    moves.append((col, row, new_col, new_row, 'normal'))
        # Castling (only if king has not moved and is not in check)
        if not piece.has_moved and not self.is_in_check(self.board, piece.color):
            # Determine back–rank row based on color.
            row_castle = 7 if piece.color == 'white' else 0
            # Kingside castling: check that squares between king and rook are empty
            rook = self.board[row_castle][7]
            if rook is not None and rook.type == 'rook' and rook.color == piece.color and not rook.has_moved:
                if self.board[row_castle][5] is None and self.board[row_castle][6] is None:
                    # Also check that the squares the king passes through are not attacked.
                    if not self.square_attacked(5, row_castle, piece.color) and not self.square_attacked(6, row_castle, piece.color):
                        moves.append((col, row, 6, row_castle, 'castling_kingside'))
            # Queenside castling
            rook = self.board[row_castle][0]
            if rook is not None and rook.type == 'rook' and rook.color == piece.color and not rook.has_moved:
                if (self.board[row_castle][1] is None and self.board[row_castle][2] is None and
                    self.board[row_castle][3] is None):
                    if not self.square_attacked(2, row_castle, piece.color) and not self.square_attacked(3, row_castle, piece.color):
                        moves.append((col, row, 2, row_castle, 'castling_queenside'))
        return moves

    def square_attacked(self, col, row, color):
        """
        Determine if a square (col, row) is attacked by any enemy piece.
        :param color: Color of the side that is defending.
        :return: True if attacked, else False.
        """
        enemy_color = 'black' if color == 'white' else 'white'
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece is not None and piece.color == enemy_color:
                    # For pawns, only consider diagonal capture moves.
                    if piece.type == 'pawn':
                        direction = 1 if enemy_color == 'black' else -1
                        for dc in [-1, 1]:
                            if (c + dc, r + direction) == (col, row):
                                return True
                    elif piece.type == 'knight':
                        knight_moves = [(2, 1), (1, 2), (-1, 2), (-2, 1),
                                        (-2, -1), (-1, -2), (1, -2), (2, -1)]
                        for dc, dr in knight_moves:
                            if (c + dc, r + dr) == (col, row):
                                return True
                    elif piece.type in ['bishop', 'queen']:
                        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
                        for dc, dr in directions:
                            new_c, new_r = c, r
                            while True:
                                new_c += dc
                                new_r += dr
                                if not self.in_bounds(new_c, new_r):
                                    break
                                if (new_c, new_r) == (col, row):
                                    return True
                                if self.board[new_r][new_c] is not None:
                                    break
                    if piece.type in ['rook', 'queen']:
                        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
                        for dc, dr in directions:
                            new_c, new_r = c, r
                            while True:
                                new_c += dc
                                new_r += dr
                                if not self.in_bounds(new_c, new_r):
                                    break
                                if (new_c, new_r) == (col, row):
                                    return True
                                if self.board[new_r][new_c] is not None:
                                    break
                    elif piece.type == 'king':
                        king_moves = [(1, 0), (-1, 0), (0, 1), (0, -1),
                                      (1, 1), (1, -1), (-1, 1), (-1, -1)]
                        for dc, dr in king_moves:
                            if (c + dc, r + dr) == (col, row):
                                return True
        return False

    def is_in_check(self, board, color):
        """
        Check if the king of the given color is in check on the given board.
        :param board: 2D list representing the board.
        :param color: 'white' or 'black'
        :return: True if in check, else False.
        """
        king_pos = None
        for r in range(8):
            for c in range(8):
                piece = board[r][c]
                if piece is not None and piece.type == 'king' and piece.color == color:
                    king_pos = (c, r)
                    break
            if king_pos is not None:
                break
        # If king not found (should not happen), consider it in check.
        if king_pos is None:
            return True
        enemy_color = 'black' if color == 'white' else 'white'
        # Check enemy moves against king's position
        for r in range(8):
            for c in range(8):
                piece = board[r][c]
                if piece is not None and piece.color == enemy_color:
                    # For pawns, consider only diagonal capture.
                    if piece.type == 'pawn':
                        direction = 1 if enemy_color == 'black' else -1
                        for dc in [-1, 1]:
                            if (c + dc, r + direction) == king_pos:
                                return True
                    elif piece.type == 'knight':
                        knight_moves = [(2, 1), (1, 2), (-1, 2), (-2, 1),
                                        (-2, -1), (-1, -2), (1, -2), (2, -1)]
                        for dc, dr in knight_moves:
                            if (c + dc, r + dr) == king_pos:
                                return True
                    elif piece.type in ['bishop', 'queen']:
                        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
                        for dc, dr in directions:
                            new_c, new_r = c, r
                            while True:
                                new_c += dc
                                new_r += dr
                                if not self.in_bounds(new_c, new_r):
                                    break
                                if (new_c, new_r) == king_pos:
                                    return True
                                if board[new_r][new_c] is not None:
                                    break
                    if piece.type in ['rook', 'queen']:
                        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
                        for dc, dr in directions:
                            new_c, new_r = c, r
                            while True:
                                new_c += dc
                                new_r += dr
                                if not self.in_bounds(new_c, new_r):
                                    break
                                if (new_c, new_r) == king_pos:
                                    return True
                                if board[new_r][new_c] is not None:
                                    break
                    elif piece.type == 'king':
                        king_moves = [(1, 0), (-1, 0), (0, 1), (0, -1),
                                      (1, 1), (1, -1), (-1, 1), (-1, -1)]
                        for dc, dr in king_moves:
                            if (c + dc, r + dr) == king_pos:
                                return True
        return False

    def copy_board(self):
        """
        Create a deep copy of the current board (pieces and their state).
        """
        new_board = [[None for _ in range(8)] for _ in range(8)]
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece is not None:
                    new_piece = Piece(piece.color, piece.type)
                    new_piece.has_moved = piece.has_moved
                    new_board[r][c] = new_piece
        return new_board

    def is_move_legal(self, move):
        """
        Check whether a move is legal by simulating it and ensuring the king is not left in check.
        """
        board_copy = self.copy_board()
        self.make_move_on_board(board_copy, move)
        # If after the move the current side's king is in check, the move is illegal.
        if self.is_in_check(board_copy, self.turn):
            return False
        return True

    def make_move(self, move):
        """
        Execute a move on the actual game board and update game state.
        :param move: A tuple (start_col, start_row, end_col, end_row, special)
        """
        start_col, start_row, end_col, end_row, special = move
        piece = self.board[start_row][start_col]
        # Handle castling moves
        if special.startswith('castling'):
            # Move king to destination square.
            self.board[end_row][end_col] = piece
            self.board[start_row][start_col] = None
            piece.has_moved = True
            if special == 'castling_kingside':
                # Move the rook from the corner to next to the king.
                rook = self.board[end_row][7]
                self.board[end_row][end_col - 1] = rook
                self.board[end_row][7] = None
                rook.has_moved = True
            elif special == 'castling_queenside':
                rook = self.board[end_row][0]
                self.board[end_row][end_col + 1] = rook
                self.board[end_row][0] = None
                rook.has_moved = True
            self.en_passant_target = None
        # Handle en passant capture
        elif special == 'en_passant':
            self.board[end_row][end_col] = piece
            self.board[start_row][start_col] = None
            piece.has_moved = True
            # Remove the captured pawn (which is on the same column as the destination but on the starting row)
            self.board[start_row][end_col] = None
            self.en_passant_target = None
        # Handle pawn promotion (auto-promote to queen)
        elif special == 'promotion':
            self.board[end_row][end_col] = piece
            self.board[start_row][start_col] = None
            piece.has_moved = True
            piece.type = 'queen'
            self.en_passant_target = None
        else:
            # Normal move
            self.board[end_row][end_col] = piece
            self.board[start_row][start_col] = None
            piece.has_moved = True
            # If a pawn moves two squares, set en passant target.
            if piece.type == 'pawn' and abs(end_row - start_row) == 2:
                self.en_passant_target = (start_col, (start_row + end_row) // 2)
            else:
                self.en_passant_target = None
        # Add the move to the history and switch turn.
        self.move_history.append(move)
        self.turn = 'black' if self.turn == 'white' else 'white'

    def get_all_moves(self, color):
        """
        Generate all legal moves for the given color.
        """
        moves = []
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece is not None and piece.color == color:
                    moves.extend(self.get_valid_moves(col, row))
        return moves

    def make_move_on_board(self, board, move):
        """
        Simulate a move on a given board copy.
        Used for move–validation and AI evaluation.
        This function handles special moves similarly to make_move().
        """
        start_col, start_row, end_col, end_row, special = move
        piece = board[start_row][start_col]
        if special.startswith('castling'):
            board[end_row][end_col] = piece
            board[start_row][start_col] = None
            piece.has_moved = True
            if special == 'castling_kingside':
                rook = board[end_row][7]
                board[end_row][end_col - 1] = rook
                board[end_row][7] = None
                rook.has_moved = True
            elif special == 'castling_queenside':
                rook = board[end_row][0]
                board[end_row][end_col + 1] = rook
                board[end_row][0] = None
                rook.has_moved = True
        elif special == 'en_passant':
            board[end_row][end_col] = piece
            board[start_row][start_col] = None
            piece.has_moved = True
            board[start_row][end_col] = None
        elif special == 'promotion':
            board[end_row][end_col] = piece
            board[start_row][start_col] = None
            piece.has_moved = True
            piece.type = 'queen'
        else:
            board[end_row][end_col] = piece
            board[start_row][start_col] = None
            piece.has_moved = True
        return board

    def evaluate_board(self, board):
        """
        Evaluate the board using a simple heuristic based on piece values.
        Positive score favors white; negative favors black.
        """
        values = {'pawn': 10, 'knight': 30, 'bishop': 30,
                  'rook': 50, 'queen': 90, 'king': 900}
        score = 0
        for r in range(8):
            for c in range(8):
                piece = board[r][c]
                if piece is not None:
                    if piece.color == 'white':
                        score += values[piece.type]
                    else:
                        score -= values[piece.type]
        return score

    def ai_move(self):
        """
        AI move for single–player mode.
        Uses a simple greedy evaluation: tries each legal move and chooses the one that yields the best immediate evaluation.
        (AI plays as black.)
        """
        best_move = None
        best_score = float('-inf')
        moves = self.get_all_moves('black')
        for move in moves:
            board_copy = self.copy_board()
            self.make_move_on_board(board_copy, move)
            score = self.evaluate_board(board_copy)
            if score > best_score:
                best_score = score
                best_move = move
        if best_move is not None:
            self.make_move(best_move)

# ------------------------------
# Splash Screen Function
# ------------------------------
def splash_screen(screen, clock):
    """
    Display a simple splash screen with options for 1 Player and 2 Player.
    Returns 1 or 2 based on user selection.
    """
    font = pygame.font.SysFont(None, 40)
    # Define buttons (positioned roughly in the middle of the window)
    one_player_rect = pygame.Rect(156, 200, 200, 50)
    two_player_rect = pygame.Rect(156, 300, 200, 50)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if one_player_rect.collidepoint(pos):
                    return 1
                elif two_player_rect.collidepoint(pos):
                    return 2
        # Fill background with colour
        screen.fill((30, 30, 30))
        # Draw title text
        title_text = font.render("Chess Game", True, (255, 255, 255))
        screen.blit(title_text, (BOARD_SIZE // 2 - title_text.get_width() // 2, 100))
        # Draw buttons
        pygame.draw.rect(screen, (70, 130, 180), one_player_rect)
        pygame.draw.rect(screen, (70, 130, 180), two_player_rect)
        one_text = font.render("1 Player", True, (255, 255, 255))
        two_text = font.render("2 Player", True, (255, 255, 255))
        screen.blit(one_text, (one_player_rect.centerx - one_text.get_width() // 2,
                               one_player_rect.centery - one_text.get_height() // 2))
        screen.blit(two_text, (two_player_rect.centerx - two_text.get_width() // 2,
                               two_player_rect.centery - two_text.get_height() // 2))
        pygame.display.flip()
        clock.tick(60)

# ------------------------------
# Main Game Loop
# ------------------------------
def main():
    pygame.init()
    screen = pygame.display.set_mode((BOARD_SIZE, BOARD_SIZE))
    pygame.display.set_caption("Chess Game")
    clock = pygame.time.Clock()
    # Show splash screen and get selected mode (1 or 2 player)
    mode = splash_screen(screen, clock)
    game = ChessGame(mode)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Allow human move input only if it's the human's turn.
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # In two-player mode, both colors are human.
                # In single-player mode, only white is controlled by human.
                if game.turn == 'white' or game.mode == 2:
                    game.handle_click(pygame.mouse.get_pos())
        # In single-player mode, let the AI play as black.
        if game.mode == 1 and game.turn == 'black':
            # Delay a bit so the AI move isn’t instantaneous.
            pygame.time.delay(500)
            game.ai_move()
        game.draw(screen)
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
