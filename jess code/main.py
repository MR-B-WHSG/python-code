import pygame
from sys import exit
import random

pygame.init()

# Cell size and screen size
cell_size = 20
screen_width = 1200
screen_height = 600

# Colours
white = (255,255,255)
black = (0,0,0)
blue = (0,0,255)
green = (0,255,0)

# Number of rows and columns
columns = screen_width // cell_size
rows = screen_height // cell_size

# (width, height)
screen = pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption("TBD")

# Set clock time
clock = pygame.time.Clock()

# Directions for movements?????????
directions = [(1,0),(-1,0),(0,1),(0,-1)]

# Maze grid: 1 = wall and 0 = path
maze = [[1 for _ in range(columns)] for _ in range(rows)]

visited = [[False for _ in range(columns)] for _ in range(rows)]


def is_valid_move(x,y):
    return 0 <= x < columns and 0 <= y < rows and not visited[y][x] == 1

def carve_path(x,y):
    print("hi carve path")
    stack = [(x,y)]

    while stack:
        cx, cy = stack[-1]
        visited[cy][cx] = True
        maze[cy][cx] = 0
        neighbours = []
        #random.shuffle(directions)

        for dx, dy in directions:
            nx , ny = cx + dx * 2, cy + dy * 2
            if is_valid_move(nx,ny):
                neighbours.append((nx,ny,cx + dx,cy+ dy))
                # maze[y+dy][x+dx] = 0
                #carve_path(nx,ny)

        if neighbours :
            ny, ny, wall_x, wall_y = random.choice(neighbours)
            maze[wall_y][wall_x] = 0
            stack.append((nx,ny))
        else:
           stack.pop()

carve_path(0,0)

# Exit to maze
maze[rows-1][columns-1] = 0


def draw_maze():
     for y in range(rows):
         for x in range(columns):
            if y == rows -  1 and x == columns - 1:
                 colour = green
            else:
                colour = white if maze[y][x] == 0 else black

            pygame.draw.rect(screen, colour,(x* cell_size, y * cell_size,cell_size,cell_size))



# Player stats
player_surface = pygame.image.load("players/spearknight.png")
player_size = (cell_size,cell_size)
player_surface = pygame.transform.scale(player_surface,player_size)
player_position_x = 0
player_position_y = 400
movement = 1
# Background information
#background_surface = pygame.image.load("backgrounds/temple.png")
#background_size = (900,500)
#background_surface = pygame.transform.scale(background_surface,background_size)


while True:
    print("hi!")
    screen.fill(black)
    draw_maze()

    for event in pygame.event.get():#
        # When you click the x button the code will stop running
        if event. type == pygame.QUIT:
            pygame.quit()
            exit()


    #screen.blit(background_surface,(0,0))
    screen.blit(player_surface,(player_position_x,player_position_y))
    keys = pygame.key.get_pressed()
    # player moves right
    if keys[pygame.K_RIGHT]:
      player_position_x += movement
    # player moves left
    if keys[pygame.K_LEFT]:
        player_position_x -= movement
    # player moves up
    if keys[pygame.K_UP]:
        player_position_y += movement
    # player moves down
    if keys[pygame.K_DOWN]:
        player_position_y += movement

    pygame.display.update()

    # The game will have a max of 60 frames per second
    clock.tick(20)

