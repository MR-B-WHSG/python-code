import random

#############################
#       GLOBAL STATE       #
#############################

# For one-turn overrides from rank 9 or special rank 2 reset
# Format: (direction, (rank, suit)) => e.g. ("higher", (5, "Hearts"))
special_card_next_turn_override = (None, None)

#############################
#       BUILD THE DECK     #
#############################

SUITS = ["Clubs", "Diamonds", "Hearts", "Spades"]
RANKS = list(range(2, 15))  # 2..14 (2=2, ..., 11=J,12=Q,13=K,14=A)

def build_full_deck():
    """Return a standard 52-card deck, shuffled."""
    deck = [(rank, suit) for suit in SUITS for rank in RANKS]
    random.shuffle(deck)
    return deck

def card_name(card):
    """Convert (rank, suit) => a readable string, e.g. (11, 'Hearts') => 'Jack of Hearts'."""
    rank, suit = card
    rank_str = {
        11: "Jack",
        12: "Queen",
        13: "King",
        14: "Ace"
    }.get(rank, str(rank))
    return f"{rank_str} of {suit}"

#############################
#       PLAYER CLASSES     #
#############################

class Player:
    """
    Human with 3 face-down, 3 face-up, 3 in-hand.
    Does not draw unless forced to pick up the discard.
    """
    def __init__(self, name="You"):
        self.name = name
        self.hand = []
        self.face_up = []
        self.face_down = []

    def total_cards_left(self):
        return len(self.hand) + len(self.face_up) + len(self.face_down)

    def __str__(self):
        return self.name

class AIPlayer:
    """
    AI with a single 'hand'.
    After each turn, draws to 5 (unless chaining 10s in one turn).
    """
    def __init__(self, name="Computer"):
        self.name = name
        self.hand = []

    def total_cards_left(self):
        return len(self.hand)

    def __str__(self):
        return self.name

#############################
#          DEALING         #
#############################

def deal_to_player(deck, player):
    """Give the human player 3 face-down, 3 face-up, 3 in-hand."""
    for _ in range(3):
        player.face_down.append(deck.pop())
    for _ in range(3):
        player.face_up.append(deck.pop())
    for _ in range(3):
        player.hand.append(deck.pop())

def deal_to_ai(deck, ai, initial_hand_size=5):
    """Deal 'initial_hand_size' cards to the AI's hand."""
    for _ in range(initial_hand_size):
        ai.hand.append(deck.pop())

#############################
#     DISCARD + SPECIAL    #
#############################

def get_effective_top(discard_pile):
    """
    Return the top non-8 card from discard, or None if none exist.
    8 is "invisible," so we skip it. If only 8s, effectively empty.
    """
    for card in reversed(discard_pile):
        if card[0] != 8:
            return card
    return None

def burn_pile(discard_pile):
    """Clear the discard pile entirely."""
    discard_pile.clear()

#############################
#     RULES & CONDITIONS   #
#############################

def can_play(card, base_card, direction="higher"):
    """
    Return True if 'card' can be played on top of 'base_card'.

    We have 4 "magic" cards that are always playable: 2, 8, 9, 10.
    If the card is not one of these, then:
      - If base_card is None, anything is playable
      - Otherwise, rank >= base_rank (if direction='higher') or <= base_rank (if direction='lower')
    """
    rank, suit = card

    # Magic ranks => always playable
    if rank in (2, 8, 9, 10):
        return True

    # If the pile is empty (or effectively empty due to only 8s)
    if base_card is None:
        return True

    # Normal rank comparison
    base_rank, _ = base_card
    if direction == "higher":
        return rank >= base_rank
    else:
        return rank <= base_rank

def handle_special_card(card_played, discard_pile, current_player, ref_card):
    """
    Process 2, 8, 9, 10.
      - 2 => next turn sees base=2 (lowest).
      - 8 => "invisible," no immediate effect (already handled in get_effective_top).
      - 9 => next turn is 'higher/lower' referencing ref_card rank.
      - 10 => burn discard, same player continues (return True).

    Return True if the same player gets another turn (due to 10).
    """
    global special_card_next_turn_override
    # Reset override unless we set a new one
    special_card_next_turn_override = (None, None)

    rank, suit = card_played

    if rank == 2:
        # Next turn sees top rank as 2
        special_card_next_turn_override = ("higher", (2, "Reset"))

    elif rank == 9:
        # Next turn must be 'higher' or 'lower' referencing ref_card
        if ref_card is None:
            base_rank = 2  # fallback if no card beneath
        else:
            base_rank = ref_card[0]

        if isinstance(current_player, Player):
            # Human decides
            choice = None
            while choice not in ["higher", "lower"]:
                choice = input(f"You played a 9 on {base_rank}. Next turn 'higher' or 'lower'? ").lower()
            chosen_direction = choice
        else:
            # AI picks randomly
            chosen_direction = random.choice(["higher", "lower"])
            print(f"{current_player.name} played a 9 on {base_rank} and chose '{chosen_direction}'.")

        special_card_next_turn_override = (chosen_direction, (base_rank, "NineRef"))

    elif rank == 10:
        # Burn discard, same player continues
        print(f"{current_player.name} played a 10! Burning the pile and continuing...")
        burn_pile(discard_pile)
        return True

    # 8 => invisible, no override needed

    return False

#############################
#       AI LOGIC           #
#############################

def ai_play_one_card(ai, discard_pile, ref_card, direction):
    """
    AI tries to play exactly one card.
    If no valid card, returns None => pick up.
    Otherwise returns chosen card.
    """
    valid = [c for c in ai.hand if can_play(c, ref_card, direction)]
    if not valid:
        return None
    valid.sort(key=lambda x: x[0])  # pick lowest rank
    return valid[0]

def ai_turn(ai, discard_pile, leftover_deck, ref_card, direction):
    """
    AI turn with a while loop for chaining 10s:
      1) Attempt to play
      2) If none => pick up => end turn
      3) If 10 => burn => keep playing
      4) Else => end turn
    After turn ends, draws up to 5 (unless chaining 10s).
    """
    while True:
        chosen_card = ai_play_one_card(ai, discard_pile, ref_card, direction)

        if chosen_card is None:
            print(f"{ai.name} cannot play. Picks up the discard pile.")
            ai.hand.extend(discard_pile)
            discard_pile.clear()
            draw_up_to_five(ai, leftover_deck)
            return False  # turn done

        ai.hand.remove(chosen_card)
        discard_pile.append(chosen_card)
        print(f"{ai.name} plays {card_name(chosen_card)}.")

        same_player = handle_special_card(chosen_card, discard_pile, ai, ref_card)
        if same_player:
            # It's a 10 => re-check top & override, continue same turn
            base_card = get_effective_top(discard_pile)
            next_dir, next_ref = special_card_next_turn_override
            if next_dir and next_ref:
                direction = next_dir
                ref_card = next_ref
            else:
                direction = "higher"
                ref_card = base_card
            continue
        else:
            # Normal card => end turn
            draw_up_to_five(ai, leftover_deck)
            return False

def draw_up_to_five(ai, leftover_deck):
    while len(ai.hand) < 5 and leftover_deck:
        ai.hand.append(leftover_deck.pop())

#############################
#   HUMAN (PLAYER) LOGIC   #
#############################

def player_turn(player, discard_pile, ref_card, direction):
    """
    Player turn with a while loop for 10 chaining:
      - Determine zone (hand, face-up, face-down)
      - Attempt 1 card
      - If 10 => loop again
      - If pick up => turn ends
    """
    while True:
        # Re-check the zone each iteration in case you pick up more cards
        if player.hand:
            zone = player.hand
            zone_name = "hand"
        elif player.face_up:
            zone = player.face_up
            zone_name = "face-up"
        else:
            zone = player.face_down
            zone_name = "face-down"

        if zone_name == "face-down":
            if not zone:
                print("No face-down cards left! Can't play.")
                return False
            flip_idx = random.randrange(len(zone))
            chosen_card = zone.pop(flip_idx)
            print(f"You flip a {card_name(chosen_card)} from face-down...")

            if can_play(chosen_card, ref_card, direction):
                discard_pile.append(chosen_card)
                print("It's playable!")
                same_player = handle_special_card(chosen_card, discard_pile, player, ref_card)
                if same_player:
                    ref_card, direction = recheck_special_overrides(discard_pile)
                    continue
                else:
                    return False
            else:
                print("Not playable. You pick up the entire discard pile!")
                zone.extend(discard_pile)
                discard_pile.clear()
                return False
        else:
            # Show visible zone
            print(f"Your {zone_name} cards:")
            for i, c in enumerate(zone):
                print(f"  {i}. {card_name(c)}")

            valid_indices = [i for i, c in enumerate(zone) if can_play(c, ref_card, direction)]
            if not valid_indices:
                print("No valid card! You pick up the discard pile.")
                zone.extend(discard_pile)
                discard_pile.clear()
                return False

            choice = None
            while choice not in valid_indices:
                try:
                    raw = input(f"Choose a card index {valid_indices} to play: ")
                    choice = int(raw)
                except ValueError:
                    pass

            chosen_card = zone.pop(choice)
            discard_pile.append(chosen_card)
            print(f"You played {card_name(chosen_card)}!")

            same_player = handle_special_card(chosen_card, discard_pile, player, ref_card)
            if same_player:
                ref_card, direction = recheck_special_overrides(discard_pile)
                continue
            else:
                return False

#############################
#      HELPER FUNCTION     #
#############################

def recheck_special_overrides(discard_pile):
    """
    After a 10 or new override is set, re-check top & override for continuing the same turn.
    """
    base_card = get_effective_top(discard_pile)
    next_dir, next_ref = special_card_next_turn_override
    if next_dir and next_ref:
        direction = next_dir
        ref_card = next_ref
    else:
        direction = "higher"
        ref_card = base_card
    return (ref_card, direction)

#############################
#         MAIN LOOP        #
#############################

def main():
    global special_card_next_turn_override

    deck = build_full_deck()

    # Create players
    player = Player("You")
    ai = AIPlayer("Computer")

    # Deal
    deal_to_player(deck, player)
    deal_to_ai(deck, ai, initial_hand_size=5)

    leftover_deck = deck
    deck = []

    discard_pile = []

    current_player = player

    while True:
        print("\n------------------------------------------")
        print(f"You have {player.total_cards_left()} cards left.")
        print(f"Computer has {ai.total_cards_left()} cards left.\n")

        # Check win
        if player.total_cards_left() == 0:
            print("You have no cards left! You win!")
            break
        if ai.total_cards_left() == 0:
            print("Computer has no cards left! You lose!")
            break

        # Determine effective top
        base_card = get_effective_top(discard_pile)

        # Check one-turn override from 2 or 9
        next_dir, next_ref = special_card_next_turn_override
        if next_dir and next_ref:
            direction = next_dir
            ref_card = next_ref
        else:
            direction = "higher"
            ref_card = base_card

        if ref_card is None:
            print("Discard is empty (or only 8s). You can play any card.")
        else:
            top_str = card_name(ref_card)
            if direction == "higher":
                print(f"The card to beat is {top_str} (>=).")
            else:
                print(f"The card to beat is {top_str} (<=).")

        # Clear the override for after this turn, unless changed again
        special_card_next_turn_override = (None, None)

        # Take the turn
        if current_player == player:
            player_turn(player, discard_pile, ref_card, direction)
        else:
            ai_turn(ai, discard_pile, leftover_deck, ref_card, direction)

        # Check immediate win again
        if player.total_cards_left() == 0:
            print("You have no cards left! You win!")
            break
        if ai.total_cards_left() == 0:
            print("Computer has no cards left! You lose!")
            break

        # Switch players (10 chaining is handled inside the turn function)
        current_player = ai if current_player == player else player

if __name__ == "__main__":
    main()
