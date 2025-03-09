import pygame
import heapq
import random  # For generating random obstacles

# Grid and window dimensions
CELL_SIZE = 40  # Size of each cell in pixels
GRID_WIDTH, GRID_HEIGHT = 10, 10  # You can adjust the grid size here
LOG_PANEL_HEIGHT = 150  # Height of the log panel (in pixels)
WINDOW_WIDTH = GRID_WIDTH * CELL_SIZE
WINDOW_HEIGHT = GRID_HEIGHT * CELL_SIZE + LOG_PANEL_HEIGHT

# Animation speed (frames per second) when not in stepwise mode
ANIMATION_SPEED = 0.5  # Adjust this value to change the speed of the visualization

# Colors (RGB tuples)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)  # Final path
RED = (255, 0, 0)  # Evaluated nodes (closed set)
BLUE = (0, 0, 255)  # Start node
DARK_BROWN = (101, 67, 33)  # Dark brown walls (obstacles)
ORANGE = (255, 165, 0)  # Goal node
LIGHT_BLUE = (173, 216, 230)  # Open set (nodes to be evaluated)
YELLOW = (255, 255, 0)  # Current node being processed

# Global list to store decision logs
log_messages = []
stepwise_mode = False  # Flag to control stepwise execution


def log_decision(message):
    """Append a log message to the log_messages list and print it."""
    log_messages.append(message)
    print(message)


# Define the Node class for pathfinding
class Node:
    def __init__(self, position, parent=None):
        self.position = position  # (x, y) coordinate on the grid
        self.parent = parent  # Reference to parent Node for path reconstruction
        self.g = 0  # Cost from start node to current node
        self.h = 0  # Heuristic cost from current node to goal
        self.f = 0  # Total cost (g + h)

    def __lt__(self, other):
        # Allows Node objects to be compared based on f cost (needed for the priority queue)
        return self.f < other.f


# Heuristic function using Manhattan distance
def heuristic(current, goal):
    """Calculate the Manhattan distance between current and goal positions."""
    return abs(current[0] - goal[0]) + abs(current[1] - goal[1])


# Generator-based A* algorithm that yields state after each decision step.
def astar_steps(grid, start, goal):
    """
    Perform the A* pathfinding algorithm as a generator.
    Yields a tuple (current_node, open_list, closed_list) after processing each node.
    When the goal is reached, yields a tuple ("path", final_path) and returns.
    If no path is found, yields ("no_path", None) at the end.
    """
    open_list = []  # Priority queue for nodes to be evaluated
    closed_list = set()  # Set for nodes that have already been evaluated

    start_node = Node(start)
    heapq.heappush(open_list, (start_node.f, start_node))
    log_decision(f"Starting A* from {start} to {goal}")

    while open_list:
        # Pop the node with the lowest f cost
        current_node = heapq.heappop(open_list)[1]
        log_decision(
            f"Processing node {current_node.position} (f={current_node.f}, g={current_node.g}, h={current_node.h})")

        # Yield the current state for visualization
        yield (current_node, list(open_list), closed_list)

        # Check if the goal is reached
        if current_node.position == goal:
            log_decision(f"Goal reached at {current_node.position}. Reconstructing path...")
            path = []
            while current_node:
                path.append(current_node.position)
                current_node = current_node.parent
            yield ("path", path[::-1])  # Yield final path (from start to goal)
            return

        closed_list.add(current_node.position)

        # Explore neighbors (up, down, left, right)
        for move in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            neighbor_pos = (current_node.position[0] + move[0],
                            current_node.position[1] + move[1])

            # Check if the neighbor is within grid boundaries
            if neighbor_pos[0] < 0 or neighbor_pos[0] >= GRID_WIDTH or \
                    neighbor_pos[1] < 0 or neighbor_pos[1] >= GRID_HEIGHT:
                log_decision(f"Skipping neighbor {neighbor_pos}: out of bounds")
                continue

            # Skip if the neighbor is an obstacle
            if grid[neighbor_pos[1]][neighbor_pos[0]] == 1:
                log_decision(f"Skipping neighbor {neighbor_pos}: obstacle")
                continue

            # Skip if the neighbor has already been evaluated
            if neighbor_pos in closed_list:
                log_decision(f"Skipping neighbor {neighbor_pos}: already evaluated")
                continue

            neighbor_node = Node(neighbor_pos, current_node)
            neighbor_node.g = current_node.g + 1  # Assuming each move costs 1
            neighbor_node.h = heuristic(neighbor_pos, goal)
            neighbor_node.f = neighbor_node.g + neighbor_node.h

            # If a node with the same position and a lower g-cost is already in open_list, skip it
            if any(node.position == neighbor_pos and node.g <= neighbor_node.g for _, node in open_list):
                log_decision(f"Skipping neighbor {neighbor_pos}: already in open list with lower cost")
                continue

            heapq.heappush(open_list, (neighbor_node.f, neighbor_node))
            log_decision(
                f"Adding neighbor {neighbor_pos} to open list (f={neighbor_node.f}, g={neighbor_node.g}, h={neighbor_node.h})")

    log_decision("No path found")
    yield ("no_path", None)


# Function to draw the grid and visualize algorithm elements
def draw_grid(screen, grid, path, start, goal, open_list=[], closed_list=set(), current_node=None):
    """Draw the grid, obstacles, and algorithm visualization elements."""
    for y in range(len(grid)):
        for x in range(len(grid[0])):
            # Create a rectangle for each cell
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)

            # Determine the cell color based on its state
            if (x, y) == start:
                color = BLUE  # Start node
            elif (x, y) == goal:
                color = ORANGE  # Goal node
            elif grid[y][x] == 1:
                color = DARK_BROWN  # Wall
            elif (x, y) in path:
                color = GREEN  # Final path
            elif (x, y) in closed_list:
                color = RED  # Evaluated nodes (closed set)
            elif any(node.position == (x, y) for _, node in open_list):
                color = LIGHT_BLUE  # Nodes in the open set
            else:
                color = WHITE  # Unvisited cell

            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, BLACK, rect, 1)  # Draw cell borders

    # Optionally highlight the current node being processed
    if current_node:
        cx, cy = current_node.position
        pygame.draw.rect(screen, YELLOW, (cx * CELL_SIZE, cy * CELL_SIZE, CELL_SIZE, CELL_SIZE))


# Function to draw the log panel below the grid
def draw_logs(screen, log_messages, font):
    """Draw the log panel displaying decision logs."""
    log_y_start = GRID_HEIGHT * CELL_SIZE  # Starting y coordinate for log panel
    log_panel_rect = pygame.Rect(0, log_y_start, WINDOW_WIDTH, LOG_PANEL_HEIGHT)
    pygame.draw.rect(screen, WHITE, log_panel_rect)
    pygame.draw.rect(screen, BLACK, log_panel_rect, 2)

    line_height = font.get_linesize()
    max_lines = LOG_PANEL_HEIGHT // line_height
    messages_to_draw = log_messages[-max_lines:]

    for i, message in enumerate(messages_to_draw):
        text_surface = font.render(message, True, BLACK)
        screen.blit(text_surface, (5, log_y_start + i * line_height))


# Main function to run the visualization
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("A* Algorithm Visualization with Logs")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 20)  # Default font, size 20 for logs

    # Generate a random grid with obstacles
    grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    obstacle_probability = 0.2  # 20% chance for each cell to be an obstacle
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if random.random() < obstacle_probability:
                grid[y][x] = 1

    # Ensure the start and goal positions are not obstacles
    start = (0, 0)
    goal = (GRID_WIDTH - 1, GRID_HEIGHT - 1)
    grid[start[1]][start[0]] = 0
    grid[goal[1]][goal[0]] = 0

    # Variable to hold the final path (if found)
    final_path = []
    running = True

    # Create the A* generator
    astar_gen = astar_steps(grid, start, goal)

    # Main loop to run the A* algorithm step by step
    while running:
        try:
            result = next(astar_gen)
        except StopIteration:
            break

        # Check the result from the generator
        if isinstance(result, tuple) and result[0] == "path":
            final_path = result[1]
            break
        elif isinstance(result, tuple) and result[0] == "no_path":
            final_path = []
            break
        else:
            # Unpack current state: current_node, open_list, and closed_list
            current_node, open_list, closed_list = result

            # Process events (to allow toggling stepwise mode)
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        stepwise_mode = not stepwise_mode

            # Clear screen and draw current state
            screen.fill(WHITE)
            # During the search, we don't have a final path yet so pass an empty list for path
            draw_grid(screen, grid, [], start, goal, open_list, closed_list, current_node)
            draw_logs(screen, log_messages, font)

            # If stepwise mode is active, wait for ENTER to advance; otherwise, auto-advance
            if stepwise_mode:
                step_msg = "Stepwise Mode: Press ENTER to advance, 's' to toggle off"
                text_surface = font.render(step_msg, True, BLACK)
                screen.blit(text_surface, (5, WINDOW_HEIGHT - LOG_PANEL_HEIGHT - 30))
                pygame.display.flip()
                waiting = True
                while waiting:
                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_RETURN:
                                waiting = False
                            elif event.key == pygame.K_s:
                                stepwise_mode = False
                                waiting = False
            else:
                pygame.display.flip()
                pygame.event.pump()
                clock.tick(ANIMATION_SPEED)

    # After the search finishes, display the final result (grid + log panel) until the window is closed
    while running:
        screen.fill(WHITE)
        draw_grid(screen, grid, final_path, start, goal)
        draw_logs(screen, log_messages, font)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    pygame.quit()