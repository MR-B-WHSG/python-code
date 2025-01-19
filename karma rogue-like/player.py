# player.py

from rules import can_play
from cards import card_name
import random

class PlayerBase:
    """
    Shared base for both Human and AI.
    Each has:
      - face_down
      - face_up
      - hand
    """
    def __init__(self, name, is_human=False):
        self.name = name
        self.is_human = is_human
        self.face_down = []
        self.face_up = []
        self.hand = []

    def total_cards_left(self):
        return len(self.hand) + len(self.face_up) + len(self.face_down)

    def __str__(self):
        return self.name

    def pick_cards_from_zone(self, zone, valid_indices, direction, ref_card, discard_pile):
        """
        For AI or human, returns a list of indices that will be played *together*.
        Must be all the same rank. By default, pick the first valid index only.
        """
        if not valid_indices:
            return []
        # Return just one card by default in this base class
        return [valid_indices[0]]

class HumanPlayer(PlayerBase):
    """
    The human player. We'll override pick_cards_from_zone to let them
    manually pick multiple indices (all same rank).
    """
    def __init__(self, name="You"):
        super().__init__(name, is_human=True)

    def pick_cards_from_zone(self, zone, valid_indices, direction, ref_card, discard_pile):
        if not valid_indices:
            return []

        print("\nYou may play multiple cards of the same rank at once.")
        print("Enter indices separated by spaces (all must be in the valid list).")
        print(f"Valid single-card indices: {valid_indices}\n")

        # Show the zone to help the user see their cards
        if zone is self.hand:
            print("Your hand cards:")
        else:
            print("Your face-up cards:")

        for i, c in enumerate(zone):
            print(f"  {i}. {card_name(c)}")

        while True:
            raw = input("Choose one or more indices separated by spaces (or blank to pass): ").strip()
            if not raw:
                # If user presses Enter with no input => pass => pick up
                return []
            try:
                chosen = [int(x) for x in raw.split()]
            except ValueError:
                print("Invalid input, please enter numbers only.")
                continue

            # Check if all chosen are in valid_indices
            if any(idx not in valid_indices for idx in chosen):
                print(f"You selected invalid indices. Must be within {valid_indices}.\n")
                continue

            # Check all chosen cards have the same rank
            ranks = [zone[idx][0] for idx in chosen]
            if len(set(ranks)) != 1:
                print("All chosen cards must share the same rank!")
                continue

            # If everything is good, return them
            return chosen

class AIPlayer(PlayerBase):
    """
    Default AI that picks a single valid card (no multi-card logic).
    We'll override in children to pick multiple of the same rank if possible.
    """
    def __init__(self, name="AI"):
        super().__init__(name, is_human=False)

class LowestFirstAI(AIPlayer):
    """
    AI that picks the lowest valid rank, and plays all copies of that rank if it has them.
    """
    def pick_cards_from_zone(self, zone, valid_indices, direction, ref_card, discard_pile):
        if not valid_indices:
            return []

        # For each valid index, get the rank
        valid_cards = [(i, zone[i]) for i in valid_indices]
        # Sort by rank ascending
        valid_cards.sort(key=lambda x: x[1][0])
        # pick the lowest rank
        chosen_rank = valid_cards[0][1][0]

        # find all indices in the zone with that rank, which are also valid
        # Actually, if it's a "magic rank," it's always playable, so we can gather all of them
        # but let's be consistent: only gather the ones that pass can_play check
        # In real Shead, if one card of that rank is playable, all same-rank duplicates are playable
        same_rank_indices = [i for i, card in enumerate(zone) if card[0] == chosen_rank]
        # Filter by can_play if you want to be strict
        # but typically if one is playable, they all are.
        return same_rank_indices

class HighestFirstAI(AIPlayer):
    """
    AI that picks the highest valid rank, and plays all copies of that rank if it has them.
    """
    def pick_cards_from_zone(self, zone, valid_indices, direction, ref_card, discard_pile):
        if not valid_indices:
            return []
        valid_cards = [(i, zone[i]) for i in valid_indices]
        # sort by rank descending
        valid_cards.sort(key=lambda x: x[1][0], reverse=True)
        chosen_rank = valid_cards[0][1][0]
        same_rank_indices = [i for i, card in enumerate(zone) if card[0] == chosen_rank]
        return same_rank_indices

class RandomAI(AIPlayer):
    """
    AI that picks a random valid rank from the zone, playing all duplicates of that rank.
    """
    def pick_cards_from_zone(self, zone, valid_indices, direction, ref_card, discard_pile):
        if not valid_indices:
            return []
        import random
        chosen_idx = random.choice(valid_indices)
        chosen_rank = zone[chosen_idx][0]
        same_rank_indices = [i for i, card in enumerate(zone) if card[0] == chosen_rank]
        return same_rank_indices
