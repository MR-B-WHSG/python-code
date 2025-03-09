
import pygame

class Button():
    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height*scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

#creating a function/attribute which draws the button on screen
    def draw(self, surface):
        action = False
        #finding mouse position
        pos = pygame.mouse.get_pos()
        #checking if mouse has moved onto a button
        if self.rect.collidepoint(pos):
            #loop to see if left mouse button (0) has been clicked
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                print("yes")
                action = True
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False

        surface.blit(self.image, (self.rect.x, self.rect.y))

        return action