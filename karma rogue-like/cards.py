# cards.py

import random

SUITS = ["Clubs", "Diamonds", "Hearts", "Spades"]
RANKS = list(range(2, 15))  # 2..14 => (2=2,3=3,...,11=J,12=Q,13=K,14=A)

def build_full_deck():
    """Return a standard 52-card deck, shuffled."""
    deck = [(rank, suit) for suit in SUITS for rank in RANKS]
    random.shuffle(deck)
    return deck

def card_name(card):
    """
    Convert (rank, suit) => a readable string,
    e.g. (11, 'Hearts') => 'Jack of Hearts'.
    """
    rank, suit = card
    rank_str = {
        11: "Jack",
        12: "Queen",
        13: "King",
        14: "Ace"
    }.get(rank, str(rank))
    return f"{rank_str} of {suit}"
