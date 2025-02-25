import pygame
import sys
from game.game_state import GameState
from game.states.menu_state import MenuState

# Initialize pygame
pygame.init()
pygame.display.set_caption("Asteroids Reborn")

# Constants
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Create the main screen - default to windowed mode initially
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

# Initialize game state with screen dimensions
game_state = GameState()
game_state.screen_width = SCREEN_WIDTH
game_state.screen_height = SCREEN_HEIGHT
game_state.is_fullscreen = False

# Function to toggle fullscreen mode
def toggle_fullscreen(enable_fullscreen):
    global screen
    if enable_fullscreen:
        # Get the desktop size for fullscreen mode
        info = pygame.display.Info()
        fullscreen_width = info.current_w
        fullscreen_height = info.current_h
        screen = pygame.display.set_mode((fullscreen_width, fullscreen_height), pygame.FULLSCREEN)
        game_state.screen_width = fullscreen_width
        game_state.screen_height = fullscreen_height
        game_state.is_fullscreen = True
    else:
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        game_state.screen_width = SCREEN_WIDTH
        game_state.screen_height = SCREEN_HEIGHT
        game_state.is_fullscreen = False

# Store the toggle function in game_state for access from menu
game_state.toggle_fullscreen = toggle_fullscreen

# Initialize default state
game_state.change_state(MenuState(game_state))

# Main game loop
while True:
    # Calculate delta time
    dt = clock.tick(FPS) / 1000.0  # Convert to seconds
    
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        game_state.handle_event(event)
    
    # Update game state
    game_state.update(dt)
    
    # Render
    screen.fill((0, 0, 0))  # Clear screen with black
    game_state.render(screen)
    pygame.display.flip()  # Update the display 