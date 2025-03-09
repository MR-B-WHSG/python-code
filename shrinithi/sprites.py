import pygame
import math
import random
from config import *

class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):

        self.game = game
        self.layer = PLAYER_LAYER
        self.groups = self.game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.image = pygame.Surface([TILE_SIZE, TILE_SIZE])
        self.image.fill("red")

        self.rect = self.image.get_rect()
        self.x, self.y = x, y
        self.rect.topleft = (self.x * TILE_SIZE, self.y * TILE_SIZE)

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.x -= 1
        if keys[pygame.K_RIGHT]:
            self.x += 1
        if keys[pygame.K_UP]:
            self.y -= 1
        if keys[pygame.K_DOWN]:
            self.y += 1

        #boundary conditions
        self.x = max(0, min(-990, self.x))
        self.y = max(0, min(-990, self.y))

        #updating position
        self.rect.topleft = (self.x * TILE_SIZE, self.y * TILE_SIZE)


