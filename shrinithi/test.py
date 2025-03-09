import pygame
import random

# Game settings
WIN_WIDTH = 990
WIN_HEIGHT = 990
TILE_SIZE = 18
FPS = 60

# Creating a display
RES = (WIN_WIDTH, WIN_HEIGHT)
tiles = 55
cols = WIN_WIDTH // tiles
rows = WIN_HEIGHT // tiles

# Implementing pygame
pygame.init()
screen = pygame.display.set_mode(RES)
pygame.display.set_caption("Maze Game")
clock = pygame.time.Clock()

class Game:
    """Game class to handle the player and game logic"""
    def __init__(self):
        self.running = True
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.player = Player(self, 0, 0)  # Player positioned at (0,0)

    def new(self):
        """Start a new game"""
        self.playing = True
        self.all_sprites.add(self.player)  # Add the player sprite

    def events(self):
        """Handle game events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False

    def update(self):
        """Update all sprites"""
        self.all_sprites.update()

    def draw(self):
        """Draw all elements"""
        screen.fill("black")  # Background
        draw_grid()  # Draw maze
        self.all_sprites.draw(screen)  # Draw player sprite
        pygame.display.update()
        clock.tick(FPS)

    def run(self):
        """Game loop"""
        self.new()
        while self.playing:
            self.events()
            self.update()
            self.draw()

class Player(pygame.sprite.Sprite):
    """Red block representing the player"""
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill("red")
        self.rect = self.image.get_rect()
        self.x, self.y = x, y
        self.rect.topleft = (self.x * TILE_SIZE, self.y * TILE_SIZE)

    def update(self):
        """Update player position"""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.x -= 1
        if keys[pygame.K_RIGHT]:
            self.x += 1
        if keys[pygame.K_UP]:
            self.y -= 1
        if keys[pygame.K_DOWN]:
            self.y += 1

        # Update position while allowing full movement to the edges
        self.rect.topleft = (self.x * TILE_SIZE, self.y * TILE_SIZE)

class Cell:
    """Defines a single maze cell"""
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.walls = {'top': True, 'right': True, 'bottom': True, 'left': True}
        self.visited = False

    def draw(self):
        """Draws maze walls"""
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

    def check_cell(self, x, y):
        """Checks if the neighboring cell exists"""
        find_index = lambda x, y: x + y * cols
        if x < 0 or x >= cols or y < 0 or y >= rows:
            return False
        return grid_cells[find_index(x, y)]

    def check_other_cells(self):
        """Checks if the neighboring cells are unvisited"""
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

def remove_walls(current, next):
    """Removes walls between two adjacent cells"""
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

# Create maze grid
grid_cells = [Cell(col, row) for row in range(rows) for col in range(cols)]
current_cell = grid_cells[0]
stack = []

def draw_grid():
    """Draws the maze"""
    for cell in grid_cells:
        cell.draw()

def generate_maze():
    """Generates a random maze using DFS"""
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

        # Exit when maze is fully generated
        if not any(cell.visited == False for cell in grid_cells):
            running = False

def main():
    """Runs the game"""
    generate_maze()  # Generate the maze first
    game = Game()  # Initialize game instance
    game.run()  # Run the game loop

if __name__ == "__main__":
    main()
