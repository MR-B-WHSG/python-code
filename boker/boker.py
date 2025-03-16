#!/usr/bin/env python3
"""
Updated boker.py

A simplified Texas Hold'em Poker game using pygame.
Modifications:
 - Card face images are loaded from files following the pattern:
   "card_{suit_full}_{rank}.png" where suit_full is one of "clubs", "diamonds", "hearts", "spades"
   and rank is padded with a zero if needed (e.g. "09" for 9, "05" for 5). Face cards (J, Q, K, A)
   are used as-is.
 - The card backing image is loaded from "card_backing.png" and used for the computer's hidden cards.
 - Stage advancement: after each betting round, press N to continue to the next stage.
 - Adjusted event loop to prevent automatic progression that caused repeated ties.

To run:
  • Ensure pygame is installed (pip install pygame).
  • Place the card images in a folder named "cards" in the same directory as this script.
    For example:
      - card_backing.png
      - card_clubs_09.png (for 9 of Clubs)
      - card_diamonds_Q.png (for Queen of Diamonds)
      - card_hearts_05.png (for 5 of Hearts)
      - etc.
  • Run this script.
"""

import pygame
import sys
import os
import random
import itertools

# ---------------------------
# Global Constants and Configurations
# ---------------------------
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 30

# Card display dimensions (adjust if needed)
CARD_WIDTH = 71   # typical card image width
CARD_HEIGHT = 96  # typical card image height

# Colors (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Mapping card ranks to integer values
RANK_VALUES = {
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "10": 10,
    "J": 11,
    "Q": 12,
    "K": 13,
    "A": 14
}

# Hand ranking categories with numerical values for comparisons
HAND_RANKS = {
    "High Card": 1,
    "One Pair": 2,
    "Two Pair": 3,
    "Three of a Kind": 4,
    "Straight": 5,
    "Flush": 6,
    "Full House": 7,
    "Four of a Kind": 8,
    "Straight Flush": 9
}

# Define possible ranks and suits used for cards
RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
SUITS = ["C", "D", "H", "S"]

# Mapping from suit letter to full suit name in file names.
SUIT_NAMES = {
    "C": "clubs",
    "D": "diamonds",
    "H": "hearts",
    "S": "spades"
}

# ---------------------------
# Card Class
# ---------------------------
class Card:
    def __init__(self, rank, suit, image):
        """
        Initialize a Card with a rank, suit, and associated image.
        :param rank: Card rank as a string (e.g., "A", "10", "K")
        :param suit: Card suit as a string (e.g., "H", "D")
        :param image: pygame Surface loaded from the card image file (or None if not available).
        """
        self.rank = rank
        self.suit = suit
        self.image = image

    def __repr__(self):
        """
        Return a string representation of the card.
        """
        return f"{self.rank}{self.suit}"

# ---------------------------
# Deck Class
# ---------------------------
class Deck:
    def __init__(self, card_images):
        """
        Initialize a deck of 52 cards.
        :param card_images: Dictionary mapping card IDs (e.g., "9C", "QD") to pygame Surfaces.
        """
        self.cards = []
        # For each suit and rank, create a card with the corresponding image.
        for suit in SUITS:
            for rank in RANKS:
                card_id = rank + suit
                image = card_images.get(card_id)  # may be None if image not found
                self.cards.append(Card(rank, suit, image))
        self.shuffle()

    def shuffle(self):
        """
        Shuffle the deck.
        """
        random.shuffle(self.cards)

    def deal_card(self):
        """
        Deal one card from the deck.
        :return: Card object or None if deck is empty.
        """
        if self.cards:
            return self.cards.pop()
        else:
            return None

# ---------------------------
# Player Class
# ---------------------------
class Player:
    def __init__(self, name, chips=100):
        """
        Initialize a player.
        :param name: Player's name.
        :param chips: Starting chip count.
        """
        self.name = name
        self.chips = chips
        self.hole_cards = []  # list to store the player's two hole cards
        self.current_bet = 0
        self.folded = False

    def reset_hand(self):
        """
        Reset the player's hand status for a new round.
        """
        self.hole_cards = []
        self.current_bet = 0
        self.folded = False

# ---------------------------
# PokerHandEvaluator Class
# ---------------------------
class PokerHandEvaluator:
    @staticmethod
    def evaluate_hand(cards):
        """
        Evaluate the best 5-card poker hand from a list of cards (up to 7 cards).
        :param cards: List of Card objects.
        :return: Tuple representing the hand's rank.
        """
        best_rank = (0,)  # Initialize with a very low rank
        # Check all possible 5-card combinations
        for combo in itertools.combinations(cards, 5):
            rank = PokerHandEvaluator.evaluate_five_card_hand(list(combo))
            if rank > best_rank:
                best_rank = rank
        return best_rank

    @staticmethod
    def evaluate_five_card_hand(hand):
        """
        Evaluate a 5-card hand.
        :param hand: List of 5 Card objects.
        :return: Tuple structured as (hand category, tie-breakers...) for comparison.
        """
        # Get numeric values for each card and sort them in descending order
        values = sorted([RANK_VALUES[card.rank] for card in hand], reverse=True)
        # Count how many times each rank appears
        rank_counts = {value: values.count(value) for value in values}
        # Determine if the hand is a flush (all cards same suit)
        is_flush = len(set(card.suit for card in hand)) == 1
        # Check if the hand forms a straight (5 consecutive values)
        is_straight = PokerHandEvaluator.check_straight(values)

        # Evaluate hand categories in order of strength
        if is_flush and is_straight:
            return (HAND_RANKS["Straight Flush"], max(values))
        if 4 in rank_counts.values():
            # Four of a Kind
            four_val = max([val for val, count in rank_counts.items() if count == 4])
            kicker = max([val for val in values if val != four_val])
            return (HAND_RANKS["Four of a Kind"], four_val, kicker)
        if 3 in rank_counts.values() and 2 in rank_counts.values():
            # Full House
            three_val = max([val for val, count in rank_counts.items() if count == 3])
            pair_val = max([val for val, count in rank_counts.items() if count == 2])
            return (HAND_RANKS["Full House"], three_val, pair_val)
        if is_flush:
            return (HAND_RANKS["Flush"],) + tuple(values)
        if is_straight:
            return (HAND_RANKS["Straight"], max(values))
        if 3 in rank_counts.values():
            # Three of a Kind
            three_val = max([val for val, count in rank_counts.items() if count == 3])
            kickers = sorted([val for val in values if val != three_val], reverse=True)
            return (HAND_RANKS["Three of a Kind"], three_val) + tuple(kickers)
        pairs = [val for val, count in rank_counts.items() if count == 2]
        if len(pairs) >= 2:
            # Two Pair
            high_pair = max(pairs)
            low_pair = min(pairs)
            kicker = max([val for val in values if val not in pairs])
            return (HAND_RANKS["Two Pair"], high_pair, low_pair, kicker)
        if len(pairs) == 1:
            # One Pair
            pair_val = pairs[0]
            kickers = sorted([val for val in values if val != pair_val], reverse=True)
            return (HAND_RANKS["One Pair"], pair_val) + tuple(kickers)
        # High Card
        return (HAND_RANKS["High Card"],) + tuple(values)

    @staticmethod
    def check_straight(values):
        """
        Check if the provided sorted (descending) list of values contains a straight.
        Special handling is included for the Ace-low straight.
        :param values: List of integer card values.
        :return: True if a straight is found, False otherwise.
        """
        unique_values = sorted(set(values), reverse=True)
        if len(unique_values) < 5:
            return False
        # Check for 5 consecutive numbers
        for i in range(len(unique_values) - 4):
            window = unique_values[i:i+5]
            if window[0] - window[4] == 4:
                return True
        # Special case for Ace-low straight (A, 5, 4, 3, 2)
        if set([14, 5, 4, 3, 2]).issubset(set(values)):
            return True
        return False

# ---------------------------
# PokerGame Class
# ---------------------------
class PokerGame:
    def __init__(self):
        """
        Initialize the PokerGame: set up pygame, load card images, create deck and players, and initialize game variables.
        """
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Texas Hold'em Poker")
        self.clock = pygame.time.Clock()

        # Load card images from the 'cards' folder using our modified naming convention.
        self.card_images = self.load_card_images()
        # Load the card backing image (for hidden cards) from "card_backing.png"
        backing_path = os.path.join("cards", "card_backing.png")
        if os.path.exists(backing_path):
            backing_image = pygame.image.load(backing_path).convert_alpha()
            self.card_backing = pygame.transform.scale(backing_image, (CARD_WIDTH, CARD_HEIGHT))
        else:
            self.card_backing = None

        # Create and shuffle the deck
        self.deck = Deck(self.card_images)

        # Create two players: one human and one computer opponent
        self.human = Player("You")
        self.ai = Player("Computer")
        self.players = [self.human, self.ai]

        # List to store community cards (the shared cards)
        self.community_cards = []

        # Initialize the betting pot
        self.pot = 0

        # Game stage can be: "preflop", "flop", "turn", "river", "showdown"
        self.stage = "preflop"

        # Fixed bet amount for each betting action (simplified betting)
        self.bet_amount = 10
        self.message = "Press B to Bet, C to Check, F to Fold."

        # Flag to control progression between stages; after a betting round, wait for 'N' key to proceed
        self.waiting_for_next_stage = False

    def load_card_images(self):
        """
        Load all card face images from the "cards" folder.
        Expected file naming convention:
          "card_{suit_full}_{rank}.png"
        where suit_full is "clubs", "diamonds", "hearts", or "spades", and rank is:
          - For numeric cards: if a single digit, padded with a 0 (e.g. "05" for 5, "09" for 9),
            or "10" for 10.
          - For face cards: "J", "Q", "K", or "A".
        :return: Dictionary mapping card IDs (e.g., "9C", "QD") to pygame Surfaces.
        """
        card_images = {}
        folder = "cards"
        for suit in SUITS:
            for rank in RANKS:
                # Determine rank string: pad numeric ranks with a zero if needed.
                if rank in ["J", "Q", "K", "A"]:
                    rank_str = rank
                else:
                    # If the rank is a single digit (2-9), pad with a 0.
                    rank_str = rank if len(rank) > 1 else "0" + rank
                # Get full suit name from SUIT_NAMES mapping.
                suit_full = SUIT_NAMES[suit]
                # Construct the expected file name.
                file_name = f"card_{suit_full}_{rank_str}.png"
                path = os.path.join(folder, file_name)
                card_id = rank + suit  # e.g., "9C", "QD"
                if os.path.exists(path):
                    image = pygame.image.load(path).convert_alpha()
                    # Scale the card image to defined dimensions
                    image = pygame.transform.scale(image, (CARD_WIDTH, CARD_HEIGHT))
                    card_images[card_id] = image
                else:
                    # If image not found, store None so fallback can be used.
                    card_images[card_id] = None
        return card_images

    def start_new_round(self):
        """
        Reset the game state and start a new round.
        """
        self.deck = Deck(self.card_images)
        self.community_cards = []
        self.pot = 0
        self.stage = "preflop"
        self.waiting_for_next_stage = False
        self.message = "New round! Press B to Bet, C to Check, F to Fold."
        for player in self.players:
            player.reset_hand()
        # Deal two hole cards to each player.
        for _ in range(2):
            for player in self.players:
                card = self.deck.deal_card()
                if card:
                    player.hole_cards.append(card)

    def deal_community_cards(self, number):
        """
        Deal the specified number of community cards.
        :param number: Number of cards to deal.
        """
        for _ in range(number):
            card = self.deck.deal_card()
            if card:
                self.community_cards.append(card)

    def handle_betting_round(self, action):
        """
        Handle a simplified betting round based on the player's action.
        :param action: 'bet', 'check', or 'fold'
        :return: "fold" if someone folds, otherwise "continue".
        """
        if action == 'fold':
            self.human.folded = True
            self.message = "You folded!"
            return "fold"
        elif action in ['bet', 'check']:
            # Process human action.
            if action == 'bet':
                if self.human.chips >= self.bet_amount:
                    self.human.chips -= self.bet_amount
                    self.human.current_bet += self.bet_amount
                    self.pot += self.bet_amount
                    self.message = "You bet."
                else:
                    self.message = "Not enough chips to bet."
                    return "continue"
            else:
                self.message = "You check."
            # Simple AI logic: randomly choose to bet or check.
            if random.random() < 0.5:
                if self.ai.chips >= self.bet_amount:
                    self.ai.chips -= self.bet_amount
                    self.ai.current_bet += self.bet_amount
                    self.pot += self.bet_amount
                    self.message += " Computer bets."
                else:
                    self.message += " Computer checks."
            else:
                self.message += " Computer checks."
            return "continue"

    def evaluate_showdown(self):
        """
        Evaluate both players' hands at showdown to determine the winner.
        :return: Winning Player object or None in case of a tie.
        """
        if self.human.folded:
            winner = self.ai
        elif self.ai.folded:
            winner = self.human
        else:
            # Evaluate best hand using hole cards plus community cards (7 cards total).
            human_best = PokerHandEvaluator.evaluate_hand(self.human.hole_cards + self.community_cards)
            ai_best = PokerHandEvaluator.evaluate_hand(self.ai.hole_cards + self.community_cards)
            if human_best > ai_best:
                winner = self.human
            elif ai_best > human_best:
                winner = self.ai
            else:
                winner = None  # It is a tie.
        return winner

    def render(self):
        """
        Draw the game state to the screen.
        """
        # Fill the background with a green color (poker table).
        self.screen.fill((0, 128, 0))
        font = pygame.font.SysFont(None, 24)
        large_font = pygame.font.SysFont(None, 36)

        # Display pot and chip counts.
        pot_text = font.render(f"Pot: {self.pot}", True, WHITE)
        self.screen.blit(pot_text, (WINDOW_WIDTH // 2 - 50, 20))

        human_chips_text = font.render(f"Your Chips: {self.human.chips}", True, WHITE)
        self.screen.blit(human_chips_text, (20, WINDOW_HEIGHT - 40))

        ai_chips_text = font.render(f"Computer Chips: {self.ai.chips}", True, WHITE)
        self.screen.blit(ai_chips_text, (WINDOW_WIDTH - 200, 20))

        # Display community cards in the center of the screen.
        start_x = WINDOW_WIDTH // 2 - (len(self.community_cards) * (CARD_WIDTH + 10)) // 2
        for idx, card in enumerate(self.community_cards):
            x = start_x + idx * (CARD_WIDTH + 10)
            y = WINDOW_HEIGHT // 2 - CARD_HEIGHT // 2
            if card.image:
                self.screen.blit(card.image, (x, y))
            else:
                # Fallback: draw a white rectangle with card text.
                pygame.draw.rect(self.screen, WHITE, (x, y, CARD_WIDTH, CARD_HEIGHT))
                card_text = font.render(str(card), True, BLACK)
                self.screen.blit(card_text, (x + 5, y + CARD_HEIGHT//2 - 10))

        # Display the human player's hole cards at the bottom.
        for idx, card in enumerate(self.human.hole_cards):
            x = 50 + idx * (CARD_WIDTH + 10)
            y = WINDOW_HEIGHT - CARD_HEIGHT - 20
            if card.image:
                self.screen.blit(card.image, (x, y))
            else:
                pygame.draw.rect(self.screen, WHITE, (x, y, CARD_WIDTH, CARD_HEIGHT))
                card_text = font.render(str(card), True, BLACK)
                self.screen.blit(card_text, (x + 5, y + CARD_HEIGHT//2 - 10))

        # Display the AI player's hole cards at the top.
        # If not in showdown, use the card backing image if available.
        for idx, card in enumerate(self.ai.hole_cards):
            x = 50 + idx * (CARD_WIDTH + 10)
            y = 60
            if self.stage == "showdown":
                if card.image:
                    self.screen.blit(card.image, (x, y))
                else:
                    pygame.draw.rect(self.screen, WHITE, (x, y, CARD_WIDTH, CARD_HEIGHT))
                    card_text = font.render(str(card), True, BLACK)
                    self.screen.blit(card_text, (x + 5, y + CARD_HEIGHT//2 - 10))
            else:
                if self.card_backing:
                    self.screen.blit(self.card_backing, (x, y))
                else:
                    pygame.draw.rect(self.screen, BLACK, (x, y, CARD_WIDTH, CARD_HEIGHT))
                    pygame.draw.rect(self.screen, WHITE, (x, y, CARD_WIDTH, CARD_HEIGHT), 2)

        # Display the current message/instructions.
        message_text = large_font.render(self.message, True, WHITE)
        self.screen.blit(message_text, (50, WINDOW_HEIGHT - CARD_HEIGHT - 70))

        pygame.display.flip()

    def game_loop(self):
        """
        The main game loop handling events, game logic, and rendering.
        """
        self.start_new_round()

        while True:
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    # If we're in showdown, any key resets the round.
                    if self.stage == "showdown":
                        winner = self.evaluate_showdown()
                        if winner is None:
                            self.message = "It's a tie! Press any key for new round."
                        else:
                            self.message = f"{winner.name} wins the round! Press any key for new round."
                        self.render()
                        pygame.time.wait(2000)  # Pause briefly to show result.
                        self.start_new_round()
                        continue

                    # If waiting for the next stage, only respond to 'N' key.
                    if self.waiting_for_next_stage:
                        if event.key == pygame.K_n:
                            if self.stage == "preflop":
                                self.deal_community_cards(3)  # Deal the flop.
                                self.stage = "flop"
                                self.waiting_for_next_stage = False
                                self.message = "Flop dealt. Press B to Bet, C to Check, F to Fold."
                            elif self.stage == "flop":
                                self.deal_community_cards(1)  # Deal the turn.
                                self.stage = "turn"
                                self.waiting_for_next_stage = False
                                self.message = "Turn dealt. Press B to Bet, C to Check, F to Fold."
                            elif self.stage == "turn":
                                self.deal_community_cards(1)  # Deal the river.
                                self.stage = "river"
                                self.waiting_for_next_stage = False
                                self.message = "River dealt. Press B to Bet, C to Check, F to Fold."
                            elif self.stage == "river":
                                self.stage = "showdown"
                                self.waiting_for_next_stage = False
                                self.message = "Showdown! Press any key to see the results."
                        continue

                    # Process betting actions if not waiting for stage advancement.
                    if event.key == pygame.K_b:
                        result = self.handle_betting_round('bet')
                        if result == "fold":
                            self.stage = "showdown"
                        else:
                            self.waiting_for_next_stage = True
                            self.message += " Press N to continue to next stage."
                    elif event.key == pygame.K_c:
                        result = self.handle_betting_round('check')
                        if result == "fold":
                            self.stage = "showdown"
                        else:
                            self.waiting_for_next_stage = True
                            self.message += " Press N to continue to next stage."
                    elif event.key == pygame.K_f:
                        # Player folds; immediately go to showdown.
                        self.human.folded = True
                        self.message = "You folded!"
                        self.stage = "showdown"

            self.render()

    def run(self):
        """
        Run the PokerGame by starting the main game loop.
        """
        self.game_loop()

# ---------------------------
# Main Function
# ---------------------------
def main():
    """
    Main entry point: create a PokerGame instance and run it.
    """
    game = PokerGame()
    game.run()

if __name__ == "__main__":
    main()