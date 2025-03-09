#!/usr/bin/env python3
"""
A complete example of a Pygame main menu system with state management.
This file demonstrates how to structure your code so that each game state
(e.g. title screen, main menu, gameplay, controls, sound settings) is handled
within one central game loop rather than using nested loops.
"""

import pygame
import sys
import button  # Make sure you have your button module with a Button class

# Initialize Pygame
pygame.init()

# Screen settings
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 900
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Title Screen")

# Load and scale the background image
background = pygame.image.load("gamebg.png")
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Load title image and calculate its centered position
title_img = pygame.image.load("gameTitle.png")
title_width, title_height = title_img.get_size()
title_x = (SCREEN_WIDTH - title_width) // 2
title_y = -20

# Load button images for various states
menu_img = pygame.image.load("menu_button.png")
one_p_img = pygame.image.load("one_player.png")
two_p_img = pygame.image.load("two_player.png")
g_controls_img = pygame.image.load("G_controls.png")
sound_img = pygame.image.load("sound.png")

# Define the initial game state
game_state = "title_screen"

# Create an instance of the menu button on the title screen
menu_btn = button.Button(0, 0, menu_img, 0.5)
menu_btn.rect.x = (SCREEN_WIDTH - menu_btn.rect.width) // 2
menu_btn.rect.y = 500

# Define spacing between buttons
button_spacing = 20

# Create buttons for the main menu state
one_p_btn = button.Button(0, 0, one_p_img, 0.3)
one_p_btn.rect.x = (SCREEN_WIDTH - one_p_btn.rect.width) // 2
# Adjust the y position as needed
one_p_btn.rect.y = 300

two_p_btn = button.Button(0, 0, two_p_img, 0.3)
two_p_btn.rect.x = (SCREEN_WIDTH - two_p_btn.rect.width) // 2
two_p_btn.rect.y = one_p_btn.rect.y + one_p_btn.rect.height + button_spacing

g_controls_btn = button.Button(0, 0, g_controls_img, 0.3)
g_controls_btn.rect.x = (SCREEN_WIDTH - g_controls_btn.rect.width) // 2
g_controls_btn.rect.y = two_p_btn.rect.y + two_p_btn.rect.height + button_spacing

sound_btn = button.Button(0, 0, sound_img, 0.3)
sound_btn.rect.x = (SCREEN_WIDTH - sound_btn.rect.width) // 2
sound_btn.rect.y = g_controls_btn.rect.y + g_controls_btn.rect.height + button_spacing

# Define a font and text color for on-screen messages
font = pygame.font.SysFont("arialblack", 40)
TEXT_COL = (255, 255, 255)


def draw_text(text, font, text_col, y_offset=0):
    """
    Helper function to draw centered text on the screen.

    Parameters:
        text (str): The text to display.
        font (pygame.font.Font): The font to render the text.
        text_col (tuple): RGB color for the text.
        y_offset (int): Vertical offset for centering the text.
    """
    img = font.render(text, True, text_col)
    text_rect = img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + y_offset))
    screen.blit(img, text_rect)


def title_screen():
    """
    Handle the title screen. Draw the title and the menu button.
    If the menu button is clicked, return the next state ("main_menu").

    Returns:
        str: The next game state.
    """
    pygame.display.set_caption("Title Screen")
    screen.blit(background, (0, 0))
    screen.blit(title_img, (title_x, title_y))
    # Draw the menu button; if clicked, change state
    if menu_btn.draw(screen):
        return "main_menu"
    return "title_screen"


def main_menu():
    """
    Handle the main menu state. Draw the buttons and check for clicks.
    Returns the next state based on which button was clicked.

    Returns:
        str: The next game state.
    """
    pygame.display.set_caption("Main Menu")
    screen.blit(background, (0, 0))

    # Check each button for clicks and update state accordingly
    if one_p_btn.draw(screen):
        return "playing"
    elif two_p_btn.draw(screen):
        return "playing"  # Update if two-player needs to be a different state
    elif g_controls_btn.draw(screen):
        return "game_controls"
    elif sound_btn.draw(screen):
        return "sound"
    return "main_menu"


def playing():
    """
    Handle the playing state.
    Draw the background and a text message indicating gameplay.

    Returns:
        str: The current game state ("playing").
    """
    pygame.display.set_caption("Playing")
    screen.blit(background, (0, 0))
    draw_text("Playing...", font, TEXT_COL)
    # Add gameplay elements here as needed
    return "playing"


def game_controls():
    """
    Handle the game controls screen.
    Draw a blue background with instructions.

    Returns:
        str: The current game state ("game_controls").
    """
    pygame.display.set_caption("Game Controls")
    screen.fill("blue")
    draw_text("Game Controls", font, TEXT_COL, -50)
    draw_text("Press ESC to return", font, TEXT_COL, 50)
    return "game_controls"


def sound_settings():
    """
    Handle the sound settings screen.
    Draw a red background with instructions.

    Returns:
        str: The current game state ("sound").
    """
    pygame.display.set_caption("Sound Settings")
    screen.fill("red")
    draw_text("Sound Settings", font, TEXT_COL, -50)
    draw_text("Press ESC to return", font, TEXT_COL, 50)
    return "sound"


# Main game loop settings
clock = pygame.time.Clock()
run = True

# Main game loop
while run:
    # Process events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        # Use the ESC key to return to the main menu from sub-screens
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if game_state in ["game_controls", "sound"]:
                    game_state = "main_menu"

    # Update the game state based on the current state
    if game_state == "title_screen":
        game_state = title_screen()
    elif game_state == "main_menu":
        game_state = main_menu()
    elif game_state == "playing":
        game_state = playing()
    elif game_state == "game_controls":
        game_state = game_controls()
    elif game_state == "sound":
        game_state = sound_settings()

    # Update the display and enforce the frame rate
    pygame.display.update()
    clock.tick(60)

# Quit Pygame and exit the program cleanly
pygame.quit()
sys.exit()
