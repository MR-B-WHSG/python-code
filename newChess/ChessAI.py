import random

pieceScores = {'K': 0, 'Q': 9, 'R': 5, 'B': 3, 'N': 3, 'p': 1} # Dictionary of the points for each piece

knightScores = [
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 2, 2, 2, 2, 2, 2, 1],
    [1, 2, 3, 3, 3, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 3, 3, 3, 2, 1],
    [1, 2, 2, 2, 2, 2, 2, 1],
    [1, 1, 1, 1, 1, 1, 1, 1]
]  # Allows AI to recognize the positional strength of knights

bishopScores = [
    [4, 3, 2, 1, 1, 2, 3, 4],
    [3, 4, 3, 2, 2, 3, 4, 3],
    [2, 3, 4, 3, 3, 4, 3, 2],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [2, 3, 4, 3, 3, 4, 3, 2],
    [3, 4, 3, 2, 2, 3, 4, 3],
    [4, 3, 2, 1, 1, 2, 3, 4]
]  # Longer diagonals are better to be on

queenScores = [
    [1, 1, 1, 3, 1, 1, 1, 1],
    [1, 2, 3, 3, 3, 1, 1, 1],
    [1, 4, 3, 3, 3, 4, 2, 1],
    [1, 2, 3, 3, 3, 2, 2, 1],
    [1, 2, 3, 3, 3, 2, 2, 1],
    [1, 4, 3, 3, 3, 4, 2, 1],
    [1, 1, 2, 3, 3, 1, 1, 1],
    [1, 1, 1, 3, 1, 1, 1, 1]
]  # Positions that are 4 points attack weak pawns

rookScores = [
    [4, 3, 4, 4, 4, 4, 3, 4],
    [4, 4, 4, 4, 4, 4, 4, 4],
    [1, 1, 2, 3, 3, 2, 1, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 1, 2, 2, 2, 2, 1, 1],
    [4, 4, 4, 4, 4, 4, 4, 4],
    [4, 3, 4, 4, 4, 4, 3, 4]
]  # Second row is usually the best row to be on

whitePawnScores = [
    [8, 8, 8, 8, 8, 8, 8, 8],
    [8, 8, 8, 8, 8, 8, 8, 8],
    [5, 6, 6, 7, 7, 6, 6, 5],
    [2, 3, 3, 5, 5, 3, 3, 2],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 1, 2, 3, 3, 2, 1, 1],
    [1, 1, 1, 0, 0, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0]
]  # Higher score squares are on the further end of the board

blackPawnScores = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 0, 0, 1, 1, 1],
    [1, 1, 2, 3, 3, 2, 1, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [2, 3, 3, 5, 5, 3, 3, 2],
    [5, 6, 6, 7, 7, 6, 6, 5],
    [8, 8, 8, 8, 8, 8, 8, 8],
    [8, 8, 8, 8, 8, 8, 8, 8]
]  # Higher score squares are at the bottom of the board

piecePositionScores = {
    "N": knightScores,
    "Q": queenScores,
    "R": rookScores,
    "B": bishopScores,
    "bp": blackPawnScores,
    "wp": whitePawnScores
}

CHECKMATE = 100000
STALEMATE = 0
DEPTH = 3
'''
Picks and returns a random move
'''


def find_random_move(valid_moves):
    return valid_moves[random.randint(0, len(valid_moves) - 1)]


'''
Method to make the first recursive call
'''


def find_best_move(gs, valid_moves):  # Helper method to call the initial recursive call and return the result at the end
    global next_move
    next_move = None
    random.shuffle(valid_moves)
    nega_max_alpha_beta(gs, valid_moves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.whiteToMove else -1)
    return next_move


def nega_max_alpha_beta(gs, valid_moves, depth, alpha, beta,
                     turn_multiplier):  # Alpha is the upper bound, Beta is the lower bound*
    global nextMove
    if depth == 0:
        return turn_multiplier * score_board(gs)
    # Ordering the moves will implement later
    max_score = -CHECKMATE
    for move in valid_moves:
        gs.makeMove(move)
        next_moves = gs.get_valid_moves()
        score = -nega_max_alpha_beta(gs, next_moves, depth - 1, -beta, -alpha,-turn_multiplier)  # the minimum and maximum get reversed for the opponent
        if score > max_score:
            max_score = score

        if depth == DEPTH:
            nextMove = move
        gs.undoMove()

        if max_score > alpha:  # Pruning happens here
            alpha = max_score
        if alpha >= beta:  # We don't need to look anymore
            break
    return max_score
'''
Positive score is good for white --> negative score is good for black
'''
def score_board(gs):
    if gs.checkmate:
        if gs.whiteToMove:
            return -CHECKMATE  # Black wins
        else:
            return CHECKMATE  # White Wins
    elif gs.stalemate:
        return STALEMATE

    score = 0
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            # Score will be positive if white is winning, negative if black is winning
            square = gs.board[row][col]
            if square != '--':
                # I will score the board positionally
                piece_position_score = 0
                if square[1] != 'K':
                    if square[1] == 'p':  # for pawns
                        piece_position_score = piecePositionScores[square][row][col]
                    else:  # for other pieces
                        piece_position_score = piecePositionScores[square[1]][row][col]  # Gets the correct score of the pieces in the correct position
                if square[0] == 'w':
                    score += pieceScores[square[1]] + piece_position_score
                elif square[0] == 'b':
                    score -= pieceScores[square[1]] + piece_position_score

    return score