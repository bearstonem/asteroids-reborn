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

# Create the main screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

# Initialize game state
game_state = GameState()
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