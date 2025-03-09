import pygame, sys
import button
import playing
pygame.init()

#screen settings
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 900
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Title_screen")

#loading background image
background = pygame.image.load("gamebg.png")
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

#load title image
title_img = pygame.image.load("gameTitle.png")
title_width, title_height = title_img.get_size()
title_x = (SCREEN_WIDTH - title_width) // 2
title_y = -20

#load button images
menu_img = pygame.image.load("menu_button.png")
one_p_img = pygame.image.load("one_player.png")
two_p_img = pygame.image.load("two_player.png")
g_controls_img = pygame.image.load("G_controls.png")
sound_img = pygame.image.load("sound.png")

#game state
game_state = "title_screen"

#making an instance of the menu button
menu_btn = button.Button(0, 0, menu_img, 0.5)
menu_btn.rect.x = (SCREEN_WIDTH - menu_btn.rect.width) // 2
menu_btn.rect.y = 500

button_spacing = 20

#one player button
one_p_btn = button.Button(0, 0, one_p_img, 0.3)
one_p_btn.rect.x = (SCREEN_WIDTH - one_p_btn.rect.width) // 2
one_p_btn.rect.y = -9

#two player button
two_p_btn = button.Button(0, 0, two_p_img, 0.3)
two_p_btn.rect.x = (SCREEN_WIDTH - two_p_btn.rect.width) // 2
two_p_btn.rect.y = one_p_btn.rect.y + one_p_btn.rect.height + button_spacing

#game controls button
g_controls_btn = button.Button(0, 0, g_controls_img, 0.3)
g_controls_btn.rect.x = (SCREEN_WIDTH - g_controls_btn.rect.width) // 2
g_controls_btn.rect.y = two_p_btn.rect.y + two_p_btn.rect.height + button_spacing

#sound button
sound_btn = button.Button(0, 0, sound_img, 0.3)
sound_btn.rect.x = (SCREEN_WIDTH - sound_btn.rect.width) // 2
sound_btn.rect.y = g_controls_btn.rect.y + g_controls_btn.rect.height + button_spacing

#define fonts
font = pygame.font.SysFont("arialblack", 40)

#define colours
TEXT_COL = (255, 255, 255)

def draw_text(text,font, text_col, y_offset=0):
    img = font.render(text, True, text_col)
    text_rect = img.get_rect(center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT //2 + y_offset))
    screen.blit(img, text_rect)

def main_menu():
    #print("made it to main menu")
    pygame.display.set_caption("Main Menu")
    screen.fill("white")
    screen.blit(background, (0,0))
    one_p_btn.draw(screen)
    two_p_btn.draw(screen)
    g_controls_btn.draw(screen)
    sound_btn.draw(screen)

def playing():
    print("i'm trying!!!!")
    pygame.display.set_caption("Playing")
    screen.fill("white")
    screen.blit(background, (0,0))

def controls():
    pygame.display.set_caption("Game controls")
    screen.fill("blue")
def sound():
    pygame.display.set_caption("Sound")
    screen.fill("red")

#gameloop
clock = pygame.time.Clock()
run = True

while run:
    if game_state == "title_screen":
        #display images
        screen.blit(background, (0, 0))
        screen.blit(title_img, (title_x, title_y))

        if menu_btn.draw(screen):
            game_state = "main_menu"

    elif game_state == "main_menu":
        #print(game_state)
        main_menu()

    while game_state == "main_menu":
            if one_p_btn.draw(screen) or two_p_btn.draw(screen):
                game_state = "playing"
                playing()
            elif g_controls_btn.draw(screen):
                game_state = "game_controls"
                controls()
            elif sound_btn.draw(screen):
                game_state = "sound"
                sound()

    """elif game_state == "playing":
        playing()
        
    elif game_state == "game_controls":
        controls()"""



#event handler
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                print("Pause")
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()

