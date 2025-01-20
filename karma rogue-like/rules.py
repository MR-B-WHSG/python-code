# rules.py

# We store any "special next turn override" (2 or 9 effect) here.
# (direction, (rank, suit)) => e.g. ("higher", (5, "Hearts"))
special_card_next_turn_override = (None, None)

def get_effective_top(discard_pile):
    """
    Return the top non-8 card from discard, or None if none exist.
    8 is "invisible," so skip it. If only 8s => effectively empty.
    """
    for card in reversed(discard_pile):
        if card[0] != 8:
            return card
    return None

def burn_pile(discard_pile):
    """Clear the discard pile entirely."""
    discard_pile.clear()

def can_play(card, base_card, direction="higher"):
    """
    Return True if `card` can be played on `base_card`.
    Magic ranks (2,8,9,10) are always playable.
    Otherwise, must meet rank >= base_rank (if direction='higher')
    or rank <= base_rank (if direction='lower').
    If base_card is None => anything is playable.
    """
    rank, suit = card
    if rank in (2, 8, 9, 10):
        return True

    if base_card is None:
        return True

    base_rank, _ = base_card
    if direction == "higher":
        return rank >= base_rank
    else:
        return rank <= base_rank

def handle_special_card(card_played, discard_pile, current_player, ref_card):
    """
    Process 2,8,9,10. Return True if the same player goes again (10 chaining).
    Possibly sets special_card_next_turn_override for 2 or 9.
    """
    global special_card_next_turn_override
    special_card_next_turn_override = (None, None)  # reset unless changed

    rank, suit = card_played
    if rank == 2:
        # Next turn sees top rank as 2
        special_card_next_turn_override = ("higher", (2, "Reset"))

    elif rank == 9:
        # Next turn must be 'higher' or 'lower' referencing ref_card
        if ref_card is None:
            base_rank = 2
        else:
            base_rank = ref_card[0]

        if current_player.is_human:
            choice = None
            while choice not in ["higher", "lower"]:
                choice = input(f"You played a 9 on {base_rank}. Next turn 'higher' or 'lower'? ").lower()
            chosen_direction = choice
        else:
            import random
            chosen_direction = random.choice(["higher", "lower"])
            print(f"{current_player.name} played a 9 on {base_rank} => chooses '{chosen_direction}'.")
        special_card_next_turn_override = (chosen_direction, (base_rank, "NineRef"))

    elif rank == 10:
        # Burn the discard, same player continues
        print(f"{current_player.name} played a 10! Burning the pile...")
        burn_pile(discard_pile)
        return True

    # 8 => "invisible," no override needed
    return False

def recheck_special_overrides(discard_pile):
    """
    After a 10 chain or new override, re-check top & override.
    Possibly changes direction to "higher" or "lower" from 2 or 9.
    """
    from rules import get_effective_top, special_card_next_turn_override
    base_card = get_effective_top(discard_pile)
    next_dir, next_ref = special_card_next_turn_override
    if next_dir and next_ref:
        direction = next_dir
        ref_card = next_ref
    else:
        direction = "higher"
        ref_card = base_card
    return (ref_card, direction)
