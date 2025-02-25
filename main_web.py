import pygame
import asyncio
import sys
from game.game_state import GameState
from game.states.menu_state import MenuState
from game.utils.web_audio_helper import audio_helper

# Define the main coroutine for web compatibility
async def main():
    # Initialize pygame but don't initialize audio yet
    pygame.init()
    # Disable audio initially to prevent autoplay issues
    pygame.mixer.quit()
    
    pygame.display.set_caption("Asteroids Reborn")

    # Constants
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    FPS = 60

    # Create the main screen - use flags for web compatibility
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    clock = pygame.time.Clock()

    # Create a "Click to Start" screen
    start_font = pygame.font.SysFont("Arial", 40)
    start_text = start_font.render("Click to Start Game (with Audio)", True, (255, 255, 255))
    start_rect = start_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    
    # Add subtitle text
    subtitle_font = pygame.font.SysFont("Arial", 20)
    subtitle_text = subtitle_font.render("Browser requires user interaction before playing audio", True, (200, 200, 200))
    subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
    
    # Wait for user interaction before continuing
    waiting_for_click = True
    while waiting_for_click:
        screen.fill((0, 0, 0))
        screen.blit(start_text, start_rect)
        screen.blit(subtitle_text, subtitle_rect)
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.FINGERDOWN or event.type == pygame.KEYDOWN:
                waiting_for_click = False
                # Now initialize audio after user interaction
                audio_helper.initialize_audio()
                print("Audio initialized successfully after user interaction")
        
        await asyncio.sleep(0)  # Yield control back to browser

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