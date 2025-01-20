# setup.py
"""
Handles:
 - Building the players (human + random-personality AIs)
 - 3 face-down + 6 face-up selection for the human
 - finalize_faceup_selection
 - returning (players, leftover_deck, discard_pile) for main_app
"""

import random
import cards
import game
import player

class GameSetup:
    """
    Utility class for building players, dealing,
    face-up selection, etc.
    """

    def __init__(self):
        # We'll store the face-up selection arrays here
        self.faceup_temp_cards = []
        self.faceup_selected = set()
        self.faceup_player = None

    def create_players(self, num_ais=1):
        """
        Returns a list of players: [human, AI1, AI2, ...]
        with random personalities from AIPlayer, LowestFirstAI, etc.
        """
        from player import HumanPlayer, AIPlayer, LowestFirstAI, HighestFirstAI, RandomAI

        ai_personality_list = [AIPlayer, LowestFirstAI, HighestFirstAI, RandomAI]
        male_names = ["John","Michael","David","Chris","James"]
        female_names= ["Sarah","Emily","Laura","Kate","Linda"]

        players = []
        human = HumanPlayer("You")
        players.append(human)

        for i in range(num_ais):
            if random.random()<0.5:
                nm= random.choice(male_names)
            else:
                nm= random.choice(female_names)
            nm+= f"#{i+1}"
            AIClass= random.choice(ai_personality_list)
            ai_= AIClass(name=nm)
            players.append(ai_)

        return players

    def start_new_game(self, num_ais=1):
        """
        Builds deck, players, leftover_deck, discard_pile,
        does 3 face-down + 6 face-up selection for the human,
        deals AI the standard 3 face-down, 3 face-up, 3 hand
        Returns (players, leftover_deck, discard_pile).
        """
        import cards
        deck = cards.build_full_deck()
        random.shuffle(deck)

        players = self.create_players(num_ais=num_ais)
        leftover_deck = deck
        discard_pile = []

        # The human => 3 face-down, plus 6 "temp" for face-up
        human = players[0]
        for _ in range(3):
            human.face_down.append(leftover_deck.pop())

        self.faceup_temp_cards = [leftover_deck.pop() for _ in range(6)]
        self.faceup_selected = set()
        self.faceup_player = human

        # Deal AI => 3 face-down, 3 face-up, 3 in-hand
        for p in players[1:]:
            game.deal_to_player_shead_style(leftover_deck, p, allow_faceup_choice=False)

        return players, leftover_deck, discard_pile

    def finalize_faceup_selection(self):
        """
        After the user picks 3 out of 6 in faceup_selected,
        lock them as face_up, rest => hand.
        """
        chosen = [self.faceup_temp_cards[i] for i in sorted(self.faceup_selected)]
        leftover = [self.faceup_temp_cards[i] for i in range(len(self.faceup_temp_cards)) if i not in self.faceup_selected]

        self.faceup_player.face_up = chosen
        self.faceup_player.hand    = leftover

        # reset
        self.faceup_temp_cards = []
        self.faceup_selected = set()
        self.faceup_player = None
