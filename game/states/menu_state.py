import pygame
import random
from game.states.base_state import BaseState
from game.states.gameplay_state import GameplayState

class MenuState(BaseState):
    """
    Main menu state
    """
    def __init__(self, game_state):
        super().__init__(game_state)
        self.title_font = pygame.font.Font(None, 72)
        self.menu_font = pygame.font.Font(None, 36)
        self.info_font = pygame.font.Font(None, 24)
        self.selected_option = 0
        self.menu_options = [
            "New Game",
            "Options",
            "Credits",
            "Quit"
        ]
        
        # Define powerup information for displaying on the start screen
        self.powerup_info = [
            {"type": "shield", "color": (100, 200, 255), "description": "Shield - Temporary invulnerability"},
            {"type": "rapidfire", "color": (255, 200, 100), "description": "Rapid Fire - Increased firing rate"},
            {"type": "extralife", "color": (100, 255, 100), "description": "Extra Life - Gain an additional life"},
            {"type": "timeslow", "color": (200, 100, 255), "description": "Time Slow - Drastically slows down enemies and asteroids"},
            {"type": "tripleshot", "color": (255, 100, 100), "description": "Triple Shot - Fire three projectiles at once"},
            {"type": "magnet", "color": (255, 255, 100), "description": "Magnet - Attracts nearby powerups"},
        ]
        
        # Define control bindings to display
        self.control_bindings = [
            {"key": "WASD / Arrows", "action": "Move ship"},
            {"key": "SPACE", "action": "Fire weapon"},
            {"key": "ESC", "action": "Pause game"},
            {"key": "R", "action": "Restart game (when game over)"}
        ]
        
        # Add some visual flair with stars in the background
        self.stars = []
        screen_width = pygame.display.get_surface().get_width()
        screen_height = pygame.display.get_surface().get_height()
        
        for _ in range(100):
            self.stars.append({
                'pos': pygame.math.Vector2(
                    random.uniform(0, screen_width),
                    random.uniform(0, screen_height)
                ),
                'size': random.uniform(1, 4),
                'speed': random.uniform(0.1, 0.6)
            })
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.menu_options)
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.menu_options)
            elif event.key == pygame.K_RETURN:
                self.select_option()
    
    def select_option(self):
        if self.selected_option == 0:  # New Game
            self.game_state.change_state(GameplayState(self.game_state))
        elif self.selected_option == 1:  # Options
            # Would transition to an options menu in a complete implementation
            pass
        elif self.selected_option == 2:  # Credits
            # Would show credits in a complete implementation
            pass
        elif self.selected_option == 3:  # Quit
            pygame.quit()
            import sys
            sys.exit()
    
    def update(self, dt):
        # Update star positions for background animation
        screen_width = pygame.display.get_surface().get_width()
        
        for star in self.stars:
            star['pos'].y += star['speed'] * dt * 100
            if star['pos'].y > pygame.display.get_surface().get_height():
                star['pos'].y = 0
                star['pos'].x = random.uniform(0, screen_width)
    
    def render(self, surface):
        # Render background
        surface.fill((0, 0, 20))  # Dark blue background
        
        # Draw stars
        for star in self.stars:
            pygame.draw.circle(
                surface, 
                (200, 200, 255), 
                (int(star['pos'].x), int(star['pos'].y)), 
                int(star['size'])
            )
        
        # Draw title
        title_text = self.title_font.render("ASTEROIDS REBORN", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(surface.get_width() // 2, surface.get_height() // 6))
        surface.blit(title_text, title_rect)
        
        # Draw menu options
        menu_y = surface.get_height() // 3
        for i, option in enumerate(self.menu_options):
            color = (255, 255, 0) if i == self.selected_option else (200, 200, 200)
            text = self.menu_font.render(option, True, color)
            rect = text.get_rect(center=(surface.get_width() // 2, menu_y + i * 50))
            surface.blit(text, rect)
            
            # Draw selection indicator
            if i == self.selected_option:
                indicator_points = [
                    (rect.left - 20, rect.centery),
                    (rect.left - 10, rect.centery - 5),
                    (rect.left - 10, rect.centery + 5)
                ]
                pygame.draw.polygon(surface, (255, 255, 0), indicator_points)
        
        # Draw powerup information
        self.render_powerup_info(surface)
        
        # Draw control bindings
        self.render_control_bindings(surface)
    
    def render_powerup_info(self, surface):
        """Render powerup information on the start screen"""
        info_title = self.menu_font.render("POWERUPS", True, (255, 255, 255))
        info_rect = info_title.get_rect(midtop=(surface.get_width() * 0.25, surface.get_height() * 0.55))
        surface.blit(info_title, info_rect)
        
        # Draw each powerup with description
        for i, powerup in enumerate(self.powerup_info):
            y_pos = info_rect.bottom + 30 + i * 25
            
            # Draw powerup circle
            circle_x = info_rect.left + 15
            pygame.draw.circle(
                surface,
                powerup["color"],
                (circle_x, y_pos),
                8
            )
            
            # Draw powerup description
            text = self.info_font.render(powerup["description"], True, (200, 200, 200))
            text_rect = text.get_rect(midleft=(circle_x + 20, y_pos))
            surface.blit(text, text_rect)
    
    def render_control_bindings(self, surface):
        """Render control bindings on the start screen"""
        controls_title = self.menu_font.render("CONTROLS", True, (255, 255, 255))
        controls_rect = controls_title.get_rect(midtop=(surface.get_width() * 0.75, surface.get_height() * 0.55))
        surface.blit(controls_title, controls_rect)
        
        # Draw each control binding
        for i, binding in enumerate(self.control_bindings):
            y_pos = controls_rect.bottom + 30 + i * 25
            
            # Draw key
            key_text = self.info_font.render(binding["key"], True, (255, 255, 0))
            key_rect = key_text.get_rect(midleft=(controls_rect.left, y_pos))
            surface.blit(key_text, key_rect)
            
            # Draw action description
            action_text = self.info_font.render(binding["action"], True, (200, 200, 200))
            action_rect = action_text.get_rect(midleft=(key_rect.right + 20, y_pos))
            surface.blit(action_text, action_rect) 