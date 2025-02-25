import pygame
import random

class Particle:
    """
    Particle entity for visual effects in Asteroids Reborn
    """
    def __init__(self, x, y, vel_x, vel_y, life, color=(255, 255, 255)):
        self.x = x
        self.y = y
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.life = life  # Lifetime in seconds
        self.max_life = life  # Store initial life for fading
        self.color = color
        self.size = random.uniform(1, 3)
    
    def update(self, dt):
        """Update particle position and lifetime"""
        # Update position
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
        
        # Apply a small drag to slow down particles over time
        self.vel_x *= 0.98
        self.vel_y *= 0.98
        
        # Update lifetime
        self.life -= dt
        
        # Optionally, make particles smaller as they age
        self.size = max(0.5, self.size * (self.life / self.max_life))
    
    def render(self, surface):
        """Render the particle"""
        # Skip rendering if off screen
        if (self.x < 0 or self.x > surface.get_width() or
            self.y < 0 or self.y > surface.get_height()):
            return
        
        # Calculate alpha (transparency) based on remaining life
        alpha = int(255 * (self.life / self.max_life))
        
        # Create a color with alpha
        color_with_alpha = (*self.color, alpha)
        
        # Create a small surface for the particle
        size = max(1, int(self.size * 2))
        particle_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Draw the particle
        pygame.draw.circle(
            particle_surface,
            color_with_alpha,
            (size // 2, size // 2),
            max(1, int(self.size))
        )
        
        # Blit the particle onto the main surface
        surface.blit(
            particle_surface,
            (int(self.x - size // 2), int(self.y - size // 2))
        ) 