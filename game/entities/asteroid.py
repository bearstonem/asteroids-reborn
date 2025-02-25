import pygame
import random
import math

class Asteroid:
    """
    Asteroid entity for Asteroids Reborn
    """
    def __init__(self, x, y, vel_x, vel_y, size, asteroid_type):
        self.x = x
        self.y = y
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.size = size
        self.type = asteroid_type
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-20, 20)  # degrees per second
        
        # Set radius and health based on size
        if size == "large":
            self.radius = 40
            self.health = 3
        elif size == "medium":
            self.radius = 25
            self.health = 2
        else:  # small
            self.radius = 15
            self.health = 1
        
        # Modify attributes based on asteroid type
        if self.type == "ice":
            self.radius *= 0.9  # Ice asteroids are a bit smaller
        elif self.type == "mineral":
            self.health += 1  # Mineral asteroids are tougher
        elif self.type == "unstable":
            self.health -= 1  # Unstable asteroids are more fragile
            if self.health < 1:
                self.health = 1
        
        # Create vertices for the asteroid (for a more irregular shape)
        self.vertices = []
        num_vertices = random.randint(7, 12)
        for i in range(num_vertices):
            angle = i * (2 * math.pi / num_vertices)
            # Randomize the radius a bit for irregular shape
            distance = self.radius * random.uniform(0.8, 1.2)
            self.vertices.append((math.cos(angle) * distance, math.sin(angle) * distance))
    
    def update(self, dt):
        """Update asteroid position and rotation"""
        # Update position
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
        
        # Update rotation
        self.rotation += self.rotation_speed * dt
        self.rotation = self.rotation % 360  # Keep rotation between 0-360
        
        # Get screen dimensions for wrapping
        screen_width = pygame.display.get_surface().get_width()
        screen_height = pygame.display.get_surface().get_height()
        
        # Screen wrapping
        if self.x < -self.radius:
            self.x = screen_width + self.radius
        elif self.x > screen_width + self.radius:
            self.x = -self.radius
            
        if self.y < -self.radius:
            self.y = screen_height + self.radius
        elif self.y > screen_height + self.radius:
            self.y = -self.radius
    
    def render(self, surface):
        """Render the asteroid"""
        # Don't render if off screen (with buffer)
        if (self.x < -self.radius * 2 or self.x > surface.get_width() + self.radius * 2 or
            self.y < -self.radius * 2 or self.y > surface.get_height() + self.radius * 2):
            return
        
        # Determine color based on asteroid type
        if self.type == "normal":
            color = (150, 150, 150)  # Gray
        elif self.type == "ice":
            color = (200, 200, 255)  # Light blue
        elif self.type == "mineral":
            color = (200, 150, 100)  # Copper/gold
        elif self.type == "unstable":
            color = (200, 100, 100)  # Reddish
        
        # Transform vertices based on asteroid position and rotation
        transformed_vertices = []
        angle_rad = math.radians(self.rotation)
        
        for vx, vy in self.vertices:
            # Rotate the vertex
            rotated_x = vx * math.cos(angle_rad) - vy * math.sin(angle_rad)
            rotated_y = vx * math.sin(angle_rad) + vy * math.cos(angle_rad)
            
            # Translate to asteroid position
            transformed_vertices.append((self.x + rotated_x, self.y + rotated_y))
        
        # Draw the asteroid
        pygame.draw.polygon(surface, color, transformed_vertices)
        
        # For unstable asteroids, add a pulsing glow effect
        if self.type == "unstable":
            # Pulsing effect based on time
            pulse = (math.sin(pygame.time.get_ticks() * 0.005) + 1) * 0.5  # 0 to 1
            glow_radius = self.radius * (1 + pulse * 0.2)
            
            # Draw semi-transparent circle for glow
            glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (255, 100, 100, 50), (glow_radius, glow_radius), glow_radius)
            surface.blit(glow_surface, (self.x - glow_radius, self.y - glow_radius))
        
        # For mineral asteroids, add sparkling effect
        elif self.type == "mineral" and random.random() < 0.2:  # Only some frames
            for _ in range(2):
                # Random position within asteroid
                angle = random.uniform(0, 2 * math.pi)
                distance = random.uniform(0, self.radius * 0.8)
                sparkle_x = self.x + math.cos(angle) * distance
                sparkle_y = self.y + math.sin(angle) * distance
                
                # Draw sparkle
                sparkle_color = (255, 255, 200)  # Yellow/gold
                pygame.draw.circle(surface, sparkle_color, (int(sparkle_x), int(sparkle_y)), 1)
        
        # Debug: draw collision radius
        # pygame.draw.circle(surface, (255, 0, 0), (int(self.x), int(self.y)), int(self.radius), 1) 