import random

# ======================================
# CONSTANTS & HELPERS
# ======================================
RANK_ORDER = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
RANK_VALUE = {rank: i for i, rank in enumerate(RANK_ORDER)}


def get_rank(card: str) -> str:
    if card.startswith('10'):
        return '10'
    return card[:-1]


def top_effective_rank(discard_pile):
    """
    Return the rank we compare against, ignoring '8' on top.
    If pile empty, treat as '2'.
    """
    if not discard_pile:
        return '2'
    for card in reversed(discard_pile):
        if get_rank(card) != '8':
            return get_rank(card)
    return '2'  # if all 8's


def check_four_in_a_row(discard_pile):
    """
    If top 4 cards share rank => True => burn the pile.
    """
    if len(discard_pile) < 4:
        return False
    last_four = discard_pile[-4:]
    ranks = [get_rank(c) for c in last_four]
    return len(set(ranks)) == 1


# ======================================
# BUILD & DEAL
# ======================================
def build_deck():
    suits = ['H', 'D', 'S', 'C']
    deck = [rank + suit for rank in RANK_ORDER for suit in suits]
    random.shuffle(deck)
    return deck


def deal_cards(deck, num_players):
    """
    3 face-down, 3 face-up, 3 in-hand per player.
    """
    players = {}
    needed_per_player = 9
    total_needed = needed_per_player * num_players
    if total_needed > len(deck):
        raise ValueError("Not enough cards to deal!")

    for i in range(num_players):
        pname = f"Player {i + 1}"
        face_down = deck[:3]
        deck = deck[3:]
        face_up = deck[:3]
        deck = deck[3:]
        hand = deck[:3]
        deck = deck[3:]

        players[pname] = {
            "face_down": face_down,
            "face_up": face_up,
            "hand": hand
        }
    return players, deck


# ======================================
# GAMEPLAY LOGIC
# ======================================
def get_current_zone(players, pname):
    """
    Must empty 'hand' first, then 'face_up', then 'face_down'.
    """
    if players[pname]["hand"]:
        return "hand"
    elif players[pname]["face_up"]:
        return "face_up"
    else:
        return "face_down"


def is_player_done(players, pname):
    """
    Done if all zones are empty.
    """
    return (not players[pname]['hand']
            and not players[pname]['face_up']
            and not players[pname]['face_down'])


def can_play(current_rank, test_rank, ascending=True):
    """
    Magic cards => always playable: 2,8,9,10.
    Otherwise:
      if ascending => test_rank >= current_rank
      if descending => test_rank <= current_rank
    """
    if test_rank in ['2', '8', '9', '10']:
        return True
    if ascending:
        return RANK_VALUE[test_rank] >= RANK_VALUE[current_rank]
    else:
        return RANK_VALUE[test_rank] <= RANK_VALUE[current_rank]


def post_play_effects(discard_pile, just_played):
    """
    Check 10 => burn, or 4-of-a-kind => burn
    Return (burned, same_player_goes_again).
    """
    ranks_played = [get_rank(c) for c in just_played]
    if '10' in ranks_played:
        print(">>> '10' => burn the pile! <<<")
        discard_pile.clear()
        return True, True

    if check_four_in_a_row(discard_pile):
        print(">>> Four-of-a-kind => burn the pile! <<<")
        discard_pile.clear()
        return True, True

    return False, False


# ======================================
# MAIN GAME
# ======================================
def main_game():
    print("Welcome to the game, with a single-turn 'lower' effect for 9!")
    num_players = int(input("How many players? (2-6) "))

    deck = build_deck()
    try:
        players, leftover = deal_cards(deck, num_players)
    except ValueError as e:
        print(e)
        return

    turn_order = list(players.keys())
    current_idx = 0

    discard_pile = []

    # The game is normally ascending.
    ascending_mode = True

    # We'll store a "forced_descending_for_one_turn" flag.
    forced_descending_for_one_turn = False

    while True:
        current_player = turn_order[current_idx]

        # Check if that player is done => they win
        if is_player_done(players, current_player):
            print(f"\n{current_player} has no cards left! They win!")
            break

        # If forced_descending_for_one_turn is True,
        # we do descending for THIS turn only, then revert.
        if forced_descending_for_one_turn:
            print("\n(Temporary descending this turn only, due to last 9-lower!)")
            current_ascending = False
        else:
            current_ascending = ascending_mode

        print("\n========================================")
        print(f"It's {current_player}'s turn!")

        zone = get_current_zone(players, current_player)
        if zone == 'hand':
            print(f"Your HAND: {players[current_player]['hand']}")
        elif zone == 'face_up':
            print(f"Your FACE-UP: {players[current_player]['face_up']}")
        else:
            # face_down
            fd_count = len(players[current_player]['face_down'])
            print(f"You have {fd_count} FACE-DOWN cards remaining (unknown).")

        # Effective top rank
        eff_rank = top_effective_rank(discard_pile)
        if discard_pile:
            top_card = discard_pile[-1]
            print(f"Discard top: {top_card} (effective rank: {eff_rank})")
        else:
            print("Discard pile empty => treat top as '2'.")

        # Show current mode
        direction_str = "Ascending" if current_ascending else "Descending"
        print(f"Current direction: {direction_str}")

        zone_cards = players[current_player][zone]

        # FACE-DOWN => flip top
        if zone == 'face_down':
            if not zone_cards:
                print("No face-down cards => skip turn.")
                current_idx = (current_idx + 1) % len(turn_order)
                # Revert if forced:
                if forced_descending_for_one_turn:
                    forced_descending_for_one_turn = False
                continue

            flipped = zone_cards.pop(0)
            rank_flipped = get_rank(flipped)
            print(f"You flip: {flipped}")

            # If '9', ask high or low
            if rank_flipped == '9':
                choice = input("[H]igher (asc) or [L]ower (desc for ONE turn)? ").lower()
                if choice.startswith('l'):
                    # For next player's turn after this one, revert to ascending,
                    # but for THIS turn, it's forced descending if it wasn't already.
                    forced_descending_for_one_turn = True
                    print("9-lower => This turn is descending only, then revert to ascending next turn.")
                else:
                    # 9-higher => permanently ascending
                    forced_descending_for_one_turn = False
                    ascending_mode = True
                    print("9-higher => the game remains ascending.")

            # Check if playable
            if can_play(eff_rank, rank_flipped, current_ascending):
                discard_pile.append(flipped)
                print(f"Played {flipped} successfully.")

                burned, go_again = post_play_effects(discard_pile, [flipped])
                if burned:
                    if go_again:
                        print("Pile burned => same player goes again!")
                        # Revert forced descending if we had it
                        if forced_descending_for_one_turn:
                            forced_descending_for_one_turn = False
                        continue
                else:
                    if go_again:
                        print("You go again!")
                        # Revert forced descending if we had it
                        if forced_descending_for_one_turn:
                            forced_descending_for_one_turn = False
                        continue

                # End turn
                current_idx = (current_idx + 1) % len(turn_order)
            else:
                # pick up
                print("Not playable => pick up pile.")
                if discard_pile:
                    players[current_player]['hand'].extend(discard_pile)
                    discard_pile.clear()
                current_idx = (current_idx + 1) % len(turn_order)

            # After the turn ends, revert forced descending if used
            if forced_descending_for_one_turn:
                forced_descending_for_one_turn = False
                ascending_mode = True  # revert back to normal ascending after this turn
            continue

        # HAND / FACE-UP
        if not zone_cards:
            print("No cards => skip turn.")
            current_idx = (current_idx + 1) % len(turn_order)
            # Revert forced descending if used
            if forced_descending_for_one_turn:
                forced_descending_for_one_turn = False
                ascending_mode = True
            continue

        print(f"Cards in {zone}: {zone_cards}")
        inp = input("Enter one+ cards of SAME rank or press ENTER to pass: ").strip()

        if not inp:
            # pass => pick up
            if discard_pile:
                print("You pick up the discard pile.")
                players[current_player]['hand'].extend(discard_pile)
                discard_pile.clear()
            else:
                print("Pile empty => nothing to pick up.")
            current_idx = (current_idx + 1) % len(turn_order)
            if forced_descending_for_one_turn:
                forced_descending_for_one_turn = False
                ascending_mode = True
            continue

        chosen_cards = inp.split()

        # Validate
        if any(c not in zone_cards for c in chosen_cards):
            print("Invalid choice => pick up pile.")
            if discard_pile:
                players[current_player]['hand'].extend(discard_pile)
                discard_pile.clear()
            current_idx = (current_idx + 1) % len(turn_order)
            if forced_descending_for_one_turn:
                forced_descending_for_one_turn = False
                ascending_mode = True
            continue

        chosen_ranks = [get_rank(c) for c in chosen_cards]
        if len(set(chosen_ranks)) != 1:
            print("All chosen cards must share the SAME rank => pick up pile.")
            if discard_pile:
                players[current_player]['hand'].extend(discard_pile)
                discard_pile.clear()
            current_idx = (current_idx + 1) % len(turn_order)
            if forced_descending_for_one_turn:
                forced_descending_for_one_turn = False
                ascending_mode = True
            continue

        rank_chosen = chosen_ranks[0]

        # If '9' => ask higher/lower
        if rank_chosen == '9':
            choice = input("[H]igher => remain ascending, [L]ower => descending FOR ONE TURN? ").lower()
            if choice.startswith('l'):
                forced_descending_for_one_turn = True
                print("9-lower => descending this turn only; then revert to ascending.")
            else:
                forced_descending_for_one_turn = False
                ascending_mode = True
                print("9-higher => remain ascending.")

        if not can_play(eff_rank, rank_chosen, current_ascending):
            print("Not playable => pick up pile.")
            if discard_pile:
                players[current_player]['hand'].extend(discard_pile)
                discard_pile.clear()
            current_idx = (current_idx + 1) % len(turn_order)
            if forced_descending_for_one_turn:
                forced_descending_for_one_turn = False
                ascending_mode = True
            continue

        # valid => remove from zone, place on discard
        for c in chosen_cards:
            zone_cards.remove(c)
        discard_pile.extend(chosen_cards)

        print(f"{current_player} played {chosen_cards}!")

        # post-play
        burned, go_again = post_play_effects(discard_pile, chosen_cards)
        if burned:
            if go_again:
                print("Pile burned => same player goes again!")
                # revert forced desc if used
                if forced_descending_for_one_turn:
                    forced_descending_for_one_turn = False
                    ascending_mode = True
                continue
            else:
                print("Pile burned => next player's turn.")
                current_idx = (current_idx + 1) % len(turn_order)
        else:
            if go_again:
                print("Magic => you go again!")
                # revert forced desc if used
                if forced_descending_for_one_turn:
                    forced_descending_for_one_turn = False
                    ascending_mode = True
                continue
            else:
                current_idx = (current_idx + 1) % len(turn_order)

        # after turn ends, revert forced descending if used
        if forced_descending_for_one_turn:
            forced_descending_for_one_turn = False
            ascending_mode = True

    print("\nGame over. Thanks for playing!")


if __name__ == "__main__":
    main_game()