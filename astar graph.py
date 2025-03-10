import pygame
import heapq
import sys
import random

pygame.init()

# --------------------------
# Global Configuration
# --------------------------

# Window dimensions
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700

# Define areas:
# Top panel for mode buttons and controls (height: 50 pixels)
TOP_PANEL_HEIGHT = 50
# Bottom log panel (height: 150 pixels)
LOG_PANEL_HEIGHT = 150
# Main drawing area height
DRAWING_AREA_HEIGHT = WINDOW_HEIGHT - TOP_PANEL_HEIGHT - LOG_PANEL_HEIGHT

# Colors (RGB tuples)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GRAY = (200, 200, 200)
RED = (255, 0, 0)           # Closed set in A*
GREEN = (0, 255, 0)         # Final path highlight
BLUE = (0, 0, 255)          # Start node
ORANGE = (255, 165, 0)      # Goal node
LIGHT_BLUE = (173, 216, 230)# Open set in A*
YELLOW = (255, 255, 0)      # Current node
DARK_GRAY = (100, 100, 100)

# Speed of A* visualization (frames per second)
ANIMATION_SPEED = 5

# --------------------------
# Global Variables for Graph and UI
# --------------------------
nodes = []       # List of Node objects
edges = []       # List of Edge objects
buttons = []     # List of UI Button objects
log_messages = []  # Log panel messages

final_path = None  # Will hold the final A* path once computed

# Modes for user interaction
# Modes: "add_node", "add_edge", "select_start", "select_goal", "edit_value", "delete", "drag", "none"
current_mode = "add_node"

# For edge creation: store first selected node
edge_start_node = None

# For dragging: store the node being dragged
dragging_node = None

# Start and goal nodes (None until selected)
start_node = None
goal_node = None

# Font for text rendering
FONT = pygame.font.SysFont(None, 20)

# The main pygame screen
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Interactive A* Teaching Tool")

clock = pygame.time.Clock()


# --------------------------
# Helper Functions
# --------------------------
def log_decision(message):
    """Append a log message to the log_messages list and print it."""
    log_messages.append(message)
    print(message)


def draw_text(surface, text, pos, color=BLACK):
    """Helper function to render text on a surface."""
    text_surface = FONT.render(text, True, color)
    surface.blit(text_surface, pos)


def manhattan(p1, p2):
    """Calculate Manhattan distance between two points."""
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])


def update_all_values():
    """
    Recalculate values for all nodes and default edges.
    For each node, if a goal is set, update its heuristic (h) using Manhattan distance.
    If the node already has a g value, update f = g + h.
    For each edge with default cost, update its cost based on the current positions.
    """
    if goal_node is not None:
        for node in nodes:
            node.h = manhattan(node.pos, goal_node.pos)
            if node.g is not None:
                node.f = node.g + node.h
    for edge in edges:
        if edge.default:
            edge.cost = manhattan(edge.node1.pos, edge.node2.pos)


# --------------------------
# Classes for Graph Elements and UI
# --------------------------
class Node:
    next_id = 1  # For labeling nodes

    def __init__(self, pos):
        self.id = Node.next_id
        Node.next_id += 1
        self.pos = pos  # (x, y) tuple in drawing area coordinates
        self.radius = 15
        self.g = None  # Actual cost (can be manually overridden)
        self.h = None  # Heuristic cost (can be manually overridden)
        self.f = None  # g + h (computed automatically)
        self.drag_offset = (0, 0)  # For dragging
        # For A* algorithm use (not persistent for editing)
        self.parent = None

    def draw(self, surface):
        """Draw the node as a circle with its label and cost values."""
        color = DARK_GRAY
        if self == start_node:
            color = BLUE
        elif self == goal_node:
            color = ORANGE

        # Draw the circle
        pygame.draw.circle(surface, color, self.pos, self.radius)
        pygame.draw.circle(surface, BLACK, self.pos, self.radius, 2)

        # Draw the label in the center
        label = FONT.render(str(self.id), True, WHITE)
        label_rect = label.get_rect(center=self.pos)
        surface.blit(label, label_rect)

        # Draw cost values (g and h) near the node
        if self.g is not None:
            g_text = FONT.render(f"g:{self.g}", True, BLACK)
            surface.blit(g_text, (self.pos[0] - self.radius, self.pos[1] - self.radius - 20))
        if self.h is not None:
            h_text = FONT.render(f"h:{self.h}", True, BLACK)
            surface.blit(h_text, (self.pos[0] - self.radius, self.pos[1] + self.radius + 5))
        if self.g is not None and self.h is not None:
            self.f = self.g + self.h
            f_text = FONT.render(f"f:{self.f}", True, BLACK)
            surface.blit(f_text, (self.pos[0] - self.radius, self.pos[1] - self.radius - 40))

    def is_clicked(self, pos):
        """Return True if a given pos is within the node's circle."""
        dx = self.pos[0] - pos[0]
        dy = self.pos[1] - pos[1]
        return dx * dx + dy * dy <= self.radius * self.radius


class Edge:
    def __init__(self, node1, node2, cost=None):
        self.node1 = node1
        self.node2 = node2
        # If cost is not provided, use Manhattan distance and mark as default.
        if cost is None:
            self.cost = manhattan(node1.pos, node2.pos)
            self.default = True
        else:
            self.cost = cost
            self.default = False

    def draw(self, surface):
        """Draw the edge as a line between node1 and node2 with cost label at the midpoint."""
        # If this is a default edge, update its cost based on current positions.
        if self.default:
            self.cost = manhattan(self.node1.pos, self.node2.pos)
        pygame.draw.line(surface, BLACK, self.node1.pos, self.node2.pos, 2)
        mid_x = (self.node1.pos[0] + self.node2.pos[0]) // 2
        mid_y = (self.node1.pos[1] + self.node2.pos[1]) // 2
        cost_text = FONT.render(str(self.cost), True, BLACK)
        surface.blit(cost_text, (mid_x, mid_y))

    def is_clicked(self, pos):
        """Return True if the pos is close to the line (edge)."""
        p1 = self.node1.pos
        p2 = self.node2.pos
        line_mag = ((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) ** 0.5
        if line_mag < 0.1:
            return False
        u = ((pos[0] - p1[0]) * (p2[0] - p1[0]) + (pos[1] - p1[1]) * (p2[1] - p1[1])) / (line_mag ** 2)
        if u < 0 or u > 1:
            return False
        ix = p1[0] + u * (p2[0] - p1[0])
        iy = p1[1] + u * (p2[1] - p1[1])
        dist = ((pos[0] - ix) ** 2 + (pos[1] - iy) ** 2) ** 0.5
        return dist < 10


class Button:
    def __init__(self, rect, text, mode):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.mode = mode  # When clicked, sets current_mode to this value

    def draw(self, surface):
        pygame.draw.rect(surface, LIGHT_GRAY, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)
        text_surface = FONT.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


# --------------------------
# In-Game Popup for Editing Values
# --------------------------
def popup_edit_value(initial_value, prompt="Enter new value:"):
    """Display an in-game popup dialog to edit a value. Returns the new value as a float."""
    input_active = True
    user_text = str(initial_value)
    popup_rect = pygame.Rect(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 - 25, 200, 50)
    while input_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    try:
                        return float(user_text)
                    except ValueError:
                        return initial_value
                elif event.key == pygame.K_BACKSPACE:
                    user_text = user_text[:-1]
                else:
                    user_text += event.unicode

        pygame.draw.rect(screen, WHITE, popup_rect)
        pygame.draw.rect(screen, BLACK, popup_rect, 2)
        prompt_surface = FONT.render(prompt, True, BLACK)
        input_surface = FONT.render(user_text, True, BLACK)
        screen.blit(prompt_surface, (popup_rect.x + 5, popup_rect.y + 5))
        screen.blit(input_surface, (popup_rect.x + 5, popup_rect.y + 25))
        pygame.display.flip()
        clock.tick(30)


# --------------------------
# A* Algorithm on Graph (Step-by-Step)
# --------------------------
def get_neighbors(node):
    """Return a list of tuples (neighbor, edge_cost) for the given node using the global edges list."""
    neighbors = []
    for edge in edges:
        if edge.node1 == node:
            neighbors.append((edge.node2, edge.cost))
        elif edge.node2 == node:
            neighbors.append((edge.node1, edge.cost))
    return neighbors


def astar_search(start, goal, update_callback=None):
    """Perform A* search on the graph. Uses the global nodes/edges.
       update_callback is called after each step for visualization."""
    open_list = []
    closed_set = set()

    # Initialize: set all nodes' g to infinity, h to Manhattan distance, and f to infinity.
    for node in nodes:
        node.g = float('inf')
        node.h = manhattan(node.pos, goal.pos)
        node.f = float('inf')
        node.parent = None
    start.g = 0
    start.f = start.h  # f = g + h

    heapq.heappush(open_list, (start.f, start.id, start))
    log_decision(f"Starting A* search from node {start.id} to node {goal.id}. The algorithm will explore nodes to determine the lowest cost path.")

    while open_list:
        current = heapq.heappop(open_list)[2]
        log_decision(f"Processing node {current.id}: f = {current.f} (total estimated cost = g + h), where g = {current.g} and h = {current.h}.")

        if update_callback:
            update_callback(current, open_list, closed_set)

        if current == goal:
            log_decision(f"Goal reached at node {current.id}: reconstructing path.")
            path = []
            while current:
                path.append(current)
                current = current.parent
            return path[::-1]

        closed_set.add(current)

        for neighbor, cost in get_neighbors(current):
            if neighbor in closed_set:
                log_decision(f"Skipping neighbor node {neighbor.id}: already evaluated.")
                continue

            tentative_g = current.g + cost
            if tentative_g < neighbor.g:
                neighbor.parent = current
                neighbor.g = tentative_g
                neighbor.h = manhattan(neighbor.pos, goal.pos)
                neighbor.f = neighbor.g + neighbor.h
                log_decision(f"Updating neighbor node {neighbor.id}: new g = {neighbor.g}, h = {neighbor.h}, f = {neighbor.f}.")
                heapq.heappush(open_list, (neighbor.f, neighbor.id, neighbor))
            else:
                log_decision(f"Skipping neighbor node {neighbor.id}: existing path has lower cost (g = {neighbor.g}) than tentative g = {tentative_g}.")

    log_decision("No path found: the algorithm could not find a viable route.")
    return None


# --------------------------
# UI Buttons Setup
# --------------------------
def setup_buttons():
    """Create buttons for different modes and actions."""
    global buttons
    buttons = []
    margin = 5
    btn_width = 80  # Reduced width to free space for mode label
    btn_height = TOP_PANEL_HEIGHT - 2 * margin
    x = margin
    buttons.append(Button((x, margin, btn_width, btn_height), "Add Node", "add_node"))
    x += btn_width + margin
    buttons.append(Button((x, margin, btn_width, btn_height), "Add Edge", "add_edge"))
    x += btn_width + margin
    buttons.append(Button((x, margin, btn_width, btn_height), "Delete", "delete"))
    x += btn_width + margin
    buttons.append(Button((x, margin, btn_width, btn_height), "Edit Value", "edit_value"))
    x += btn_width + margin
    buttons.append(Button((x, margin, btn_width, btn_height), "Drag", "drag"))
    x += btn_width + margin
    buttons.append(Button((x, margin, btn_width, btn_height), "Set Start", "select_start"))
    x += btn_width + margin
    buttons.append(Button((x, margin, btn_width, btn_height), "Set Goal", "select_goal"))
    x += btn_width + margin
    buttons.append(Button((x, margin, btn_width, btn_height), "Run A*", "run_astar"))
    x += btn_width + margin
    buttons.append(Button((x, margin, btn_width, btn_height), "Reset", "reset"))


setup_buttons()


# --------------------------
# Drawing Functions
# --------------------------
def draw_top_panel():
    """Draw the top panel containing buttons and current mode display."""
    top_rect = pygame.Rect(0, 0, WINDOW_WIDTH, TOP_PANEL_HEIGHT)
    pygame.draw.rect(screen, LIGHT_GRAY, top_rect)
    for btn in buttons:
        btn.draw(screen)
    # Position the mode label to the right of the buttons.
    mode_text = FONT.render(f"Mode: {current_mode}", True, BLACK)
    screen.blit(mode_text, (770, 10))


def draw_drawing_area():
    """Draw the main graph area (below top panel, above log panel)."""
    drawing_rect = pygame.Rect(0, TOP_PANEL_HEIGHT, WINDOW_WIDTH, DRAWING_AREA_HEIGHT)
    pygame.draw.rect(screen, WHITE, drawing_rect)
    grid_spacing = 20
    for x in range(0, WINDOW_WIDTH, grid_spacing):
        pygame.draw.line(screen, LIGHT_GRAY, (x, TOP_PANEL_HEIGHT), (x, TOP_PANEL_HEIGHT + DRAWING_AREA_HEIGHT))
    for y in range(TOP_PANEL_HEIGHT, TOP_PANEL_HEIGHT + DRAWING_AREA_HEIGHT, grid_spacing):
        pygame.draw.line(screen, LIGHT_GRAY, (0, y), (WINDOW_WIDTH, y))

    for edge in edges:
        edge.draw(screen)
    for node in nodes:
        node.draw(screen)

    if final_path is not None and len(final_path) > 1:
        for i in range(len(final_path) - 1):
            start_pos = final_path[i].pos
            end_pos = final_path[i + 1].pos
            pygame.draw.line(screen, GREEN, start_pos, end_pos, 6)


def draw_log_panel():
    """Draw the log panel at the bottom of the window."""
    log_rect = pygame.Rect(0, TOP_PANEL_HEIGHT + DRAWING_AREA_HEIGHT, WINDOW_WIDTH, LOG_PANEL_HEIGHT)
    pygame.draw.rect(screen, WHITE, log_rect)
    pygame.draw.rect(screen, BLACK, log_rect, 2)
    line_height = FONT.get_linesize()
    max_lines = LOG_PANEL_HEIGHT // line_height
    messages = log_messages[-max_lines:]
    for i, msg in enumerate(messages):
        draw_text(screen, msg, (5, TOP_PANEL_HEIGHT + DRAWING_AREA_HEIGHT + i * line_height))


# --------------------------
# Main Event Loop
# --------------------------
def main_loop():
    global current_mode, edge_start_node, dragging_node, start_node, goal_node, nodes, edges, log_messages, final_path
    running = True
    astar_path = None

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                continue

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if pos[1] < TOP_PANEL_HEIGHT:
                    for btn in buttons:
                        if btn.is_clicked(pos):
                            if btn.mode == "reset":
                                nodes.clear()
                                edges.clear()
                                start_node = None
                                goal_node = None
                                final_path = None
                                log_messages.clear()
                                log_decision("Graph reset: all nodes and edges cleared.")
                            elif btn.mode == "run_astar":
                                if start_node is None or goal_node is None:
                                    log_decision("Error: Select both start and goal nodes before running A*.")
                                else:
                                    log_decision("Running A* algorithm...")
                                    astar_path = astar_search(start_node, goal_node, update_callback=astar_update)
                                    final_path = astar_path
                                    if final_path:
                                        log_decision("A* algorithm completed: path found.")
                                    else:
                                        log_decision("A* algorithm completed: no path found.")
                            else:
                                current_mode = btn.mode
                            break
                    continue

                if current_mode == "add_node":
                    new_node = Node((pos[0], pos[1]))
                    nodes.append(new_node)
                    log_decision(f"Added node {new_node.id} at {new_node.pos}.")
                elif current_mode == "add_edge":
                    for node in nodes:
                        if node.is_clicked(pos):
                            if edge_start_node is None:
                                edge_start_node = node
                                log_decision(f"Selected node {node.id} as start for new edge.")
                            else:
                                if node != edge_start_node:
                                    new_edge = Edge(edge_start_node, node)
                                    edges.append(new_edge)
                                    log_decision(f"Created edge between node {edge_start_node.id} and node {node.id} with cost {new_edge.cost}.")
                                    edge_start_node = None
                            break
                elif current_mode == "delete":
                    deleted = False
                    for node in nodes:
                        if node.is_clicked(pos):
                            log_decision(f"Deleted node {node.id}.")
                            edges = [edge for edge in edges if edge.node1 != node and edge.node2 != node]
                            if node == start_node:
                                start_node = None
                            if node == goal_node:
                                goal_node = None
                            nodes.remove(node)
                            deleted = True
                            break
                    if not deleted:
                        for edge in edges:
                            if edge.is_clicked(pos):
                                log_decision(f"Deleted edge between node {edge.node1.id} and node {edge.node2.id}.")
                                edges.remove(edge)
                                break
                elif current_mode == "edit_value":
                    for node in nodes:
                        if node.is_clicked(pos):
                            if pos[1] < node.pos[1]:
                                new_val = popup_edit_value(node.g if node.g is not None else 0, prompt=f"Enter new g for node {node.id}:")
                                node.g = new_val
                                log_decision(f"Updated node {node.id} g value to {node.g}.")
                            else:
                                new_val = popup_edit_value(node.h if node.h is not None else 0, prompt=f"Enter new h for node {node.id}:")
                                node.h = new_val
                                log_decision(f"Updated node {node.id} h value to {node.h}.")
                            break
                    for edge in edges:
                        if edge.is_clicked(pos):
                            new_cost = popup_edit_value(edge.cost, prompt=f"Enter new cost for edge between {edge.node1.id} and {edge.node2.id}:")
                            edge.cost = new_cost
                            edge.default = False
                            log_decision(f"Updated cost for edge between node {edge.node1.id} and node {edge.node2.id} to {edge.cost}.")
                            break
                elif current_mode == "select_start":
                    for node in nodes:
                        if node.is_clicked(pos):
                            start_node = node
                            log_decision(f"Node {node.id} set as START node.")
                            break
                elif current_mode == "select_goal":
                    for node in nodes:
                        if node.is_clicked(pos):
                            goal_node = node
                            log_decision(f"Node {node.id} set as GOAL node.")
                            break
                elif current_mode == "drag":
                    for node in nodes:
                        if node.is_clicked(pos):
                            dragging_node = node
                            dragging_node.drag_offset = (node.pos[0] - pos[0], node.pos[1] - pos[1])
                            break

            elif event.type == pygame.MOUSEBUTTONUP:
                if current_mode == "drag":
                    dragging_node = None
            elif event.type == pygame.MOUSEMOTION:
                if current_mode == "drag" and dragging_node:
                    new_x = event.pos[0] + dragging_node.drag_offset[0]
                    new_y = event.pos[1] + dragging_node.drag_offset[1]
                    new_y = max(TOP_PANEL_HEIGHT + dragging_node.radius, new_y)
                    new_y = min(TOP_PANEL_HEIGHT + DRAWING_AREA_HEIGHT - dragging_node.radius, new_y)
                    new_x = max(dragging_node.radius, new_x)
                    new_x = min(WINDOW_WIDTH - dragging_node.radius, new_x)
                    dragging_node.pos = (new_x, new_y)
                    # Recalculate heuristic and default edge costs for all nodes and edges
                    update_all_values()

        screen.fill(WHITE)
        draw_top_panel()
        draw_drawing_area()
        draw_log_panel()
        pygame.display.flip()
        clock.tick(ANIMATION_SPEED)

    pygame.quit()


def astar_update(current_node, open_list, closed_set):
    """Callback for A* algorithm visualization updates."""
    screen.fill(WHITE)
    draw_top_panel()
    draw_drawing_area()
    for node in closed_set:
        pygame.draw.circle(screen, RED, node.pos, node.radius + 4, 2)
    for _, _, node in open_list:
        pygame.draw.circle(screen, LIGHT_BLUE, node.pos, node.radius + 4, 2)
    pygame.draw.circle(screen, YELLOW, current_node.pos, current_node.radius + 6, 3)
    draw_log_panel()
    pygame.display.flip()
    pygame.event.pump()
    clock.tick(ANIMATION_SPEED)


if __name__ == "__main__":
    main_loop()