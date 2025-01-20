# scoring.py

import random

def compute_card_score(card_played, base_card, round_count):
    """
    Magic multipliers:
      - 2 => x2
      - 8 => x(base_card's rank) or 0 if no base
      - 9 => x(dice roll 1..6)
      - 10 => x10
      - else => rank_of_card_played
    Then multiply by round_count.
    """
    rank_played = card_played[0]

    if rank_played == 2:
        # 2 => (2*2)=4
        base_score = 4
    elif rank_played == 8:
        if base_card is None:
            base_score = 0
        else:
            base_score = 8 * base_card[0]
    elif rank_played == 9:
        dice = random.randint(1, 6)
        base_score = 9 * dice
    elif rank_played == 10:
        base_score = 100  # 10 * 10
    else:
        base_score = rank_played

    return base_score * round_count
