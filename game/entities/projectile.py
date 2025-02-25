import pygame
import math

class Projectile:
    """
    Projectile entity for player weapons in Asteroids Reborn
    """
    def __init__(self, x, y, vel_x, vel_y):
        self.x = x
        self.y = y
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.radius = 3  # Small collision radius
        self.life = 3.0  # Projectile lifetime in seconds
        
        # Calculate angle for rendering
        self.angle = math.degrees(math.atan2(vel_y, vel_x))
    
    def update(self, dt):
        """Update projectile position and lifetime"""
        # Update position
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
        
        # Update lifetime
        self.life -= dt
    
    def render(self, surface):
        """Render the projectile"""
        # Draw a small elongated rectangle (bullet)
        angle_rad = math.radians(self.angle)
        
        # Bullet length
        length = 10
        width = 2
        
        # Calculate corners of the bullet rectangle
        cos_angle = math.cos(angle_rad)
        sin_angle = math.sin(angle_rad)
        
        # Front and back offsets along bullet direction
        front_x = self.x + cos_angle * (length / 2)
        front_y = self.y + sin_angle * (length / 2)
        back_x = self.x - cos_angle * (length / 2)
        back_y = self.y - sin_angle * (length / 2)
        
        # Perpendicular direction for width
        perp_x = -sin_angle * (width / 2)
        perp_y = cos_angle * (width / 2)
        
        # Four corners of the bullet
        points = [
            (front_x + perp_x, front_y + perp_y),
            (front_x - perp_x, front_y - perp_y),
            (back_x - perp_x, back_y - perp_y),
            (back_x + perp_x, back_y + perp_y)
        ]
        
        # Draw the bullet
        pygame.draw.polygon(surface, (255, 255, 100), points)  # Yellow bullet
        
        # Add a small glow effect
        glow_surface = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (255, 255, 100, 50), (10, 10), 5)
        surface.blit(glow_surface, (int(self.x) - 10, int(self.y) - 10))
        
        # Draw a small trail behind the projectile
        trail_points = [
            (back_x, back_y),
            (back_x - cos_angle * 5 + perp_x * 0.5, back_y - sin_angle * 5 + perp_y * 0.5),
            (back_x - cos_angle * 5 - perp_x * 0.5, back_y - sin_angle * 5 - perp_y * 0.5)
        ]
        pygame.draw.polygon(surface, (255, 200, 50), trail_points)  # Orange trail
        
        # Debug: draw collision radius
        # pygame.draw.circle(surface, (255, 0, 0), (int(self.x), int(self.y)), int(self.radius), 1) 