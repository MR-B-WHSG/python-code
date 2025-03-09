import random

def roll_dice(sides=6):
    """Roll a single die with the given number of sides."""
    return random.randint(1, sides)

def calculate_points(die1, die2):
    """Calculate points based on the dice rolls and game rules."""
    total = die1 + die2
    if total % 2 == 0:
        return total + 10  # Even total gets +10 points
    else:
        return max(0, total - 5)  # Odd total loses 5 points but can't go below 0

def play_round():
    """Simulate a single round for both players."""
    # Player 1's turn
    p1_die1, p1_die2 = roll_dice(), roll_dice()
    p1_points = calculate_points(p1_die1, p1_die2)

    # Player 2's turn
    p2_die1, p2_die2 = roll_dice(), roll_dice()
    p2_points = calculate_points(p2_die1, p2_die2)

    print(f"Player 1 rolled {p1_die1} and {p1_die2} -> Round points: {p1_points}")
    print(f"Player 2 rolled {p2_die1} and {p2_die2} -> Round points: {p2_points}")

    return p1_points, p2_points

def play_game(rounds=5):
    """Simulate the dice game with a set number of rounds."""
    p1_total_score = 0
    p2_total_score = 0

    for round_num in range(1, rounds + 1):
        print(f"\nRound {round_num}:")
        p1_points, p2_points = play_round()
        p1_total_score += p1_points
        p2_total_score += p2_points

        print(f"Current Scores -> Player 1: {p1_total_score}, Player 2: {p2_total_score}")
        input()

    # Determine the winner or tie-breaker
    if p1_total_score > p2_total_score:
        print(f"\nPlayer 1 wins with {p1_total_score} points!")
    elif p2_total_score > p1_total_score:
        print(f"\nPlayer 2 wins with {p2_total_score} points!")
    else:
        print("\nIt's a tie! Rolling a single die each to determine the winner.")
        tie_breaker(p1_total_score, p2_total_score)

def tie_breaker(p1_score, p2_score):
    """Handle tie-breaking logic until there's a winner."""
    while True:
        p1_roll = roll_dice()
        p2_roll = roll_dice()
        print(f"Player 1 rolls: {p1_roll}, Player 2 rolls: {p2_roll}")

        if p1_roll > p2_roll:
            print(f"Player 1 wins the tie-breaker with a roll of {p1_roll}!")
            break
        elif p2_roll > p1_roll:
            print(f"Player 2 wins the tie-breaker with a roll of {p2_roll}!")
            break
        else:
            print("It's another tie! Rolling again...")

game = True
while game:
    print("Welcome to the Two-Player Dice Game!")
    play_game()
