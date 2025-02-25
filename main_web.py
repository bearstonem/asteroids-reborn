import pygame
import asyncio
import sys
from game.game_state import GameState
from game.states.menu_state import MenuState

# Define the main coroutine for web compatibility
async def main():
    # Initialize pygame
    pygame.init()
    pygame.display.set_caption("Asteroids Reborn")

    # Constants
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    FPS = 60

    # Create the main screen - use flags for web compatibility
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    clock = pygame.time.Clock()

    # Initialize game state
    game_state = GameState()
    game_state.change_state(MenuState(game_state))

    # Main game loop
    running = True
    while running:
        # Calculate delta time
        dt = clock.tick(FPS) / 1000.0  # Convert to seconds
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            game_state.handle_event(event)
        
        # Update game state
        game_state.update(dt)
        
        # Render
        screen.fill((0, 0, 0))  # Clear screen with black
        game_state.render(screen)
        pygame.display.flip()  # Update the display

        # Add this to yield control back to browser
        await asyncio.sleep(0)
    
    pygame.quit()
    sys.exit()

# Web-compatible entry point
if __name__ == "__main__":
    asyncio.run(main()) 