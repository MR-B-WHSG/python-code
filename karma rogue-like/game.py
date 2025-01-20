# game.py

import random
import rules
from cards import build_full_deck, card_name
from rules import (
    get_effective_top,
    handle_special_card,
    recheck_special_overrides
)
from player import HumanPlayer, AIPlayer, LowestFirstAI, HighestFirstAI, RandomAI
from scoring import compute_card_score

def deal_to_player_shead_style(deck, player, allow_faceup_choice=False):
    """
    Give each player 3 face-down, 3 face-up, 3 in-hand.
    If allow_faceup_choice=True (for human), do "pick 3 out of 6" for face-up.
    Else just top 3 => face_up, next 3 => hand.
    """
    # 3 face-down
    for _ in range(3):
        player.face_down.append(deck.pop())

    if allow_faceup_choice:
        temp_hand = [deck.pop() for _ in range(6)]
        print("\nYou have these 6 cards to place face-up:")
        for i, c in enumerate(temp_hand):
            print(f"  {i}. {card_name(c)}")

        chosen_indices = []
        while len(chosen_indices) < 3:
            try:
                idx = int(input("Choose an index for face-up: "))
                if 0 <= idx < 6 and idx not in chosen_indices:
                    chosen_indices.append(idx)
                else:
                    print("Invalid choice.")
            except ValueError:
                print("Invalid input.")

        # The chosen 3 => face_up, the rest => hand
        player.face_up = [temp_hand[i] for i in chosen_indices]
        player.hand   = [temp_hand[i] for i in range(6) if i not in chosen_indices]
    else:
        # AI or no choice
        for _ in range(3):
            player.face_up.append(deck.pop())
        for _ in range(3):
            player.hand.append(deck.pop())

def take_turn(player, discard_pile, leftover_deck, ref_card, direction, scores, round_count):
    """
    Single turn for a player. Return True if the same player goes again (10 chaining),
    else False. Each time a card is played, if player is human => accumulate score.

    MULTI-CARD logic:
      - If flipping face-down (human or AI), we pick exactly 1 card index to flip.
      - If playing from hand/face-up, we gather all chosen cards (must share rank).
      - Only the LAST card triggers the special card effect (2,8,9,10).
      - Score is computed for each card played if human, then added.
    """
    from rules import can_play

    # 1) Decide which zone to play from
    if player.hand:
        zone = player.hand
        zone_name = "hand"
    elif player.face_up:
        zone = player.face_up
        zone_name = "face-up"
    else:
        zone = player.face_down
        zone_name = "face-down"

    # 2) Face-down logic => human chooses which index to flip, AI picks random
    if zone_name == "face-down":
        if not zone:
            print(f"{player.name} has no face-down cards left!")
            input("Press Enter to continue...")
            return False

        if player.is_human:
            print("\nChoose which face-down card to flip:")
            for i in range(len(zone)):
                print(f"  {i}. [Hidden]")
            flip_idx = None
            while flip_idx not in range(len(zone)):
                try:
                    flip_idx = int(input("Enter the index of the face-down card: "))
                except ValueError:
                    pass
        else:
            flip_idx = random.randrange(len(zone))

        flipped_card = zone.pop(flip_idx)
        print(f"{player.name} flips a face-down card... {card_name(flipped_card)}")

        if not can_play(flipped_card, ref_card, direction):
            print(f"{player.name} cannot play the flipped card. They pick up the discard pile.")
            player.hand.append(flipped_card)
            player.hand.extend(discard_pile)
            discard_pile.clear()
            input("Press Enter to continue...")
            return False
        else:
            print(f"{player.name} plays the flipped card.")
            discard_pile.append(flipped_card)

            # If human, compute score
            if player.is_human:
                pts = compute_card_score(flipped_card, ref_card, round_count)
                scores["You"] = scores.get("You", 0) + pts
                print(f"You earned {pts} points! (total {scores['You']})")

            same_player = handle_special_card(flipped_card, discard_pile, player, ref_card)
            input("Press Enter to continue...")
            return same_player

    # 3) Hand/Face-up => multi-card logic
    valid_indices = [i for i, c in enumerate(zone) if can_play(c, ref_card, direction)]
    if not valid_indices:
        print(f"{player.name} cannot play from {zone_name}. Picks up discard.")
        zone.extend(discard_pile)
        discard_pile.clear()
        input("Press Enter to continue...")
        return False

    chosen_indices = player.pick_cards_from_zone(zone, valid_indices, direction, ref_card, discard_pile)
    if not chosen_indices:
        # means pass => pick up
        print(f"{player.name} picks up the discard pile.")
        zone.extend(discard_pile)
        discard_pile.clear()
        input("Press Enter to continue...")
        return False

    # Now we have a set of cards with the same rank
    chosen_indices.sort(reverse=True)  # remove higher indices first so we don't mess up lower indices
    played_cards = []
    for idx in chosen_indices:
        card_chosen = zone.pop(idx)
        played_cards.append(card_chosen)

    # The last card triggers the special effect
    for c in played_cards:
        print(f"{player.name} plays {card_name(c)} from their {zone_name}.")

    discard_pile.extend(played_cards)

    # SCORING for each card if human
    if player.is_human:
        total_pts = 0
        for c in played_cards:
            pts = compute_card_score(c, ref_card, round_count)
            total_pts += pts
        scores["You"] = scores.get("You", 0) + total_pts
        print(f"You earned {total_pts} points this move! (total {scores['You']})")

    # Check special effect from the LAST card
    last_card = played_cards[-1]
    same_player = handle_special_card(last_card, discard_pile, player, ref_card)
    input("Press Enter to continue...")
    return same_player

def run_one_round(scores, round_count):
    """
    Run a single round of Shead with multiple players.
    - We only track the human player's score (scores["You"]).
    - The last player left is the Shead.
    - We'll pick random AI names from male/female lists.
    """
    # Two huge name lists (for brevity, we'll do small lists)
    male_names = ["John", "Michael", "David", "Chris", "James"]
    female_names = ["Sarah", "Emily", "Laura", "Kate", "Linda"]

    try:
        num_ais = int(input("How many AI opponents? (0..3 recommended) "))
    except ValueError:
        num_ais = 1

    # Available AI personalities
    ai_personalities = [AIPlayer, LowestFirstAI, HighestFirstAI, RandomAI]

    deck = build_full_deck()

    # Create the human
    human = HumanPlayer("You")
    players = [human]

    import random
    for i in range(num_ais):
        # Pick male or female 50/50
        if random.random() < 0.5:
            ai_name = random.choice(male_names)
        else:
            ai_name = random.choice(female_names)

        # Add a random surname or letter to differentiate
        ai_name += f"#{i+1}"

        AICLASS = random.choice(ai_personalities)
        ai_player = AICLASS(name=ai_name)
        players.append(ai_player)

    # Deal
    for p in players:
        if p.is_human:
            deal_to_player_shead_style(deck, p, allow_faceup_choice=True)
        else:
            deal_to_player_shead_style(deck, p, allow_faceup_choice=False)

    discard_pile = []
    leftover_deck = deck
    current_index = 0

    finish_order = []

    while len(players) > 1:
        player = players[current_index]
        print("\n" + "-"*50)
        for pl in players:
            print(f"{pl.name} has {pl.total_cards_left()} cards left.")
        print()

        if player.total_cards_left() == 0:
            # They finished earlier, remove them
            finish_order.append(player)
            players.remove(player)
            if current_index >= len(players):
                current_index = 0
            continue

        # Determine top & override
        base_card = get_effective_top(discard_pile)
        next_dir, next_ref = rules.special_card_next_turn_override
        if next_dir and next_ref:
            direction = next_dir
            ref_card = next_ref
        else:
            direction = "higher"
            ref_card = base_card

        if ref_card is None:
            print("Discard is empty (or only 8s). Any card can be played.")
        else:
            from cards import card_name
            comp = ">=" if direction == "higher" else "<="
            print(f"The card to beat is {card_name(ref_card)} ({comp}).")

        # Clear override
        rules.special_card_next_turn_override = (None, None)

        same_player = take_turn(player, discard_pile, leftover_deck, ref_card, direction, scores, round_count)

        # If they finished mid-turn => remove them
        if player.total_cards_left() == 0:
            finish_order.append(player)
            players.remove(player)
            if len(players) == 1:
                break
            # If same_player was True, it doesn't matter, they're out
            if current_index >= len(players):
                current_index = 0
            continue

        if same_player:
            new_ref, new_dir = recheck_special_overrides(discard_pile)
            continue

        # next player
        current_index = (current_index + 1) % len(players)

    # Only 1 left => Shead
    if len(players) == 1:
        finish_order.append(players[0])
        print(f"\n{players[0].name} is the last one with cards... the maroon!\n")

    print("Round results / finishing order:")
    for i, p in enumerate(finish_order, start=1):
        if i == len(finish_order):
            print(f"  {i}. {p.name} (maroon)")
        else:
            print(f"  {i}. {p.name} (Safe)")

    return finish_order
