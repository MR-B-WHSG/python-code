import pygame
import random

WIN_WIDTH = 990
WIN_HEIGHT = 990
TILE_SIZE = 18
FPS = 60

PLAYER_LAYER = 1

# Creating a display
RES = (WIN_WIDTH, WIN_HEIGHT)
tiles = 55
cols = WIN_WIDTH // tiles
rows = WIN_HEIGHT // tiles

# Implementing pygame
pygame.init()
screen = pygame.display.set_mode(RES)
pygame.display.set_caption("Playing")
clock = pygame.time.Clock()

class Game:
    #creating a function that will make sprites easy to use
    def __init__(self):
        self.running = True
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.enemies = pygame.sprite.LayeredUpdates()
        #self.gems = pygame.sprite.LayeredUpdates()
        #self.collect = pygame.sprite.LayeredUpdates()

        self.player = Player(self, 1, 1)

    def new(self):
        self.playing = True
        self.all_sprites.add(self.player)
    def events(self):
        #game loop events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False

    def update(self):
        self.all_sprites.update()

    def draw(self):
        screen.fill("black")
        draw_grid()
        self.all_sprites.draw(screen)
        pygame.display.update()
        clock.tick(FPS)

    def run(self):
        self.new()
        while self.playing:
            self.events()
            self.update()
            self.draw()

    #def game_over(self):
        #pass
class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game

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
        #self.x = max(0, min(cols-1, self.x))
        #self.y = max(0, min(rows-1, self.y))

        #updating position
        self.rect.topleft = (self.x * TILE_SIZE, self.y * TILE_SIZE)

class Cell:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.walls = {'top': True, 'right': True, 'bottom': True, 'left': True}
        self.visited = False

#using two dimensional arrays to draw different lines of the tiles
    def draw(self):
        x, y = self.x * tiles, self.y * tiles
        if self.visited:
            pygame.draw.rect(screen, pygame.Color("#76AA79"), (x, y, tiles, tiles))

        if self.walls['top']:
            pygame.draw.line(screen, pygame.Color("#B0CCB1"), (x, y), (x + tiles, y), 3)
        if self.walls['right']:
            pygame.draw.line(screen, pygame.Color("#B0CCB1"), (x + tiles, y), (x + tiles, y + tiles), 3)
        if self.walls['bottom']:
            pygame.draw.line(screen, pygame.Color("#B0CCB1"), (x + tiles, y + tiles), (x, y + tiles), 3)
        if self.walls['left']:
            pygame.draw.line(screen, pygame.Color("#B0CCB1"), (x, y + tiles), (x, y), 3)

    def draw_current_cell(self):
        x, y = self.x * tiles, self.y * tiles
        pygame.draw.rect(screen, pygame.Color("#E91E63"),
                         (x + 2, y + 2, tiles - 4, tiles - 4))

    def check_cell(self, x, y):
        find_index = lambda x, y: x + y * cols
        if x < 0 or x >= cols or y < 0 or y >= rows:
            return False
        return grid_cells[find_index(x, y)]

#creating a function to check neighbouring cells (whether visited or not)
    def check_other_cells(self):
        oc = []
        top = self.check_cell(self.x, self.y - 1)
        right = self.check_cell(self.x + 1, self.y)
        bottom = self.check_cell(self.x, self.y + 1)
        left = self.check_cell(self.x - 1, self.y)
        if top and not top.visited:
            oc.append(top)
        if right and not right.visited:
            oc.append(right)
        if bottom and not bottom.visited:
            oc.append(bottom)
        if left and not left.visited:
            oc.append(left)
        return random.choice(oc) if oc else False

#function to remove walls
def remove_walls(current, next):
    dx = current.x - next.x
    dy = current.y - next.y

    if dx == 1:
        current.walls["left"] = False
        next.walls["right"] = False

    elif dx == -1:
        current.walls["right"] = False
        next.walls["left"] = False

    if dy == 1:
        current.walls["top"] = False
        next.walls["bottom"] = False

    elif dy == -1:
        current.walls["bottom"] = False
        next.walls["top"] = False

# Creating a list of cell objects using the Cell class
grid_cells = [Cell(col, row) for row in range(rows) for col in range(cols)]
current_cell = grid_cells[0]
stack = []

def draw_grid():
    for cell in grid_cells:
        cell.draw()

def generate_maze():
    global current_cell
    running = True
    while running:
        screen.fill(pygame.Color("#B46F6F"))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        current_cell.visited = True
        next_cell = current_cell.check_other_cells()

        if next_cell:
            next_cell.visited = True
            remove_walls(current_cell, next_cell)
            stack.append(current_cell)
            current_cell = next_cell
        elif stack:
            current_cell = stack.pop()

        draw_grid()
        pygame.display.flip()
        clock.tick(30)

        if not any(cell.visited == False for cell in grid_cells):
            running = False
def main():
   generate_maze()
   game = Game()
   game.run()

if __name__ == "__main__":
    main()
