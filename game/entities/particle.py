import pygame
import random
import math

class Particle:
    """
    Particle entity for visual effects in Asteroids Reborn
    Enhanced with more dynamic visual properties
    """
    def __init__(self, x, y, vel_x, vel_y, life, color=(255, 255, 255), 
                size=None, shape="circle", trail=False, glow=False, 
                fade_mode="normal", spin=False):
        self.x = x
        self.y = y
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.life = life  # Lifetime in seconds
        self.max_life = life  # Store initial life for fading
        self.color = color
        self.size = random.uniform(1.5, 4.5) if size is None else size
        self.original_size = self.size
        self.shape = shape  # "circle", "square", "triangle", "star"
        self.trail = trail  # Whether this particle leaves a trail
        self.trail_positions = []  # Store previous positions for trail effect
        self.glow = glow  # Whether this particle has a glow effect
        self.fade_mode = fade_mode  # "normal", "pulse", "flicker"
        self.flicker_offset = random.uniform(0, 6.28)
        self.spin = spin  # Whether the particle rotates
        self.rotation = random.uniform(0, 360) if spin else 0
        self.spin_speed = random.uniform(-180, 180) if spin else 0
        self.pulse_speed = random.uniform(1.0, 3.0)
        
    def update(self, dt):
        """Update particle position and lifetime"""
        # Store position for trail effect if enabled
        if self.trail:
            self.trail_positions.append((self.x, self.y))
            # Keep only the last 10 positions for efficiency
            if len(self.trail_positions) > 10:
                self.trail_positions.pop(0)
                
        # Update position
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
        
        # Apply a small drag to slow down particles over time
        self.vel_x *= 0.98
        self.vel_y *= 0.98
        
        # Update rotation if spinning
        if self.spin:
            self.rotation += self.spin_speed * dt
            
        # Update lifetime
        self.life -= dt
        
        # Handle different fade behaviors
        if self.fade_mode == "normal":
            # Normal fade - particles get smaller as they age
            self.size = max(0.5, self.original_size * (self.life / self.max_life))
        elif self.fade_mode == "pulse":
            # Pulsing fade - particles oscillate in size
            life_factor = self.life / self.max_life
            pulse = 0.5 + 0.5 * math.sin(self.pulse_speed * pygame.time.get_ticks() / 1000)
            self.size = max(0.5, self.original_size * (0.5 * life_factor + 0.5 * pulse))
        elif self.fade_mode == "flicker":
            # Flickering fade - particles randomly change in opacity
            life_factor = self.life / self.max_life
            flicker = math.sin(pygame.time.get_ticks() / 100 + self.flicker_offset)
            self.size = max(0.5, self.original_size * life_factor * (0.7 + 0.3 * flicker))
    
    def render(self, surface):
        """Render the particle with enhanced visual effects"""
        # Skip rendering if off screen
        if (self.x < -10 or self.x > surface.get_width() + 10 or
            self.y < -10 or self.y > surface.get_height() + 10):
            return
        
        # Calculate alpha (transparency) based on remaining life
        if self.fade_mode == "flicker":
            flicker = 0.5 + 0.5 * math.sin(pygame.time.get_ticks() / 80 + self.flicker_offset)
            alpha = int(255 * (self.life / self.max_life) * flicker)
        else:
            alpha = int(255 * (self.life / self.max_life))
        
        alpha = max(0, min(255, alpha))  # Ensure alpha is in valid range
        
        # Create a color with alpha
        color_with_alpha = (*self.color, alpha)
        
        # Draw trail if enabled
        if self.trail and len(self.trail_positions) > 1:
            for i in range(len(self.trail_positions) - 1):
                # Calculate trail alpha (fades out for older positions)
                trail_alpha = alpha * (i / len(self.trail_positions))
                trail_color = (*self.color, int(trail_alpha))
                
                # Calculate trail size (smaller for older positions)
                trail_size = max(1, self.size * (i / len(self.trail_positions)))
                
                # Draw trail segment
                start_pos = (int(self.trail_positions[i][0]), int(self.trail_positions[i][1]))
                end_pos = (int(self.trail_positions[i+1][0]), int(self.trail_positions[i+1][1]))
                pygame.draw.line(surface, trail_color, start_pos, end_pos, max(1, int(trail_size)))
        
        # Create a surface for the particle (larger if glow is enabled)
        size_multiplier = 3 if self.glow else 2
        render_size = max(2, int(self.size * size_multiplier))
        particle_surface = pygame.Surface((render_size, render_size), pygame.SRCALPHA)
        
        # Draw glow effect if enabled
        if self.glow:
            # Outer glow (larger, more transparent)
            glow_color = (*self.color, alpha // 3)
            pygame.draw.circle(
                particle_surface,
                glow_color,
                (render_size // 2, render_size // 2),
                max(1, int(self.size * 2))
            )
            
            # Inner glow (smaller, less transparent)
            glow_color = (*self.color, alpha // 2)
            pygame.draw.circle(
                particle_surface,
                glow_color,
                (render_size // 2, render_size // 2),
                max(1, int(self.size * 1.5))
            )
        
        # Draw the particle in different shapes
        if self.shape == "circle":
            pygame.draw.circle(
                particle_surface,
                color_with_alpha,
                (render_size // 2, render_size // 2),
                max(1, int(self.size))
            )
        elif self.shape == "square":
            # Create a square and rotate it if spinning
            rect = pygame.Rect(
                render_size // 2 - int(self.size),
                render_size // 2 - int(self.size),
                int(self.size * 2),
                int(self.size * 2)
            )
            
            if self.spin:
                # Create a Surface to draw the rotated square on
                square_surface = pygame.Surface((render_size, render_size), pygame.SRCALPHA)
                pygame.draw.rect(square_surface, color_with_alpha, rect)
                
                # Rotate the surface
                rotated_surface = pygame.transform.rotate(square_surface, self.rotation)
                # Center the rotated surface
                rotated_rect = rotated_surface.get_rect(center=(render_size // 2, render_size // 2))
                # Blit onto the particle surface
                particle_surface.blit(rotated_surface, rotated_rect)
            else:
                pygame.draw.rect(particle_surface, color_with_alpha, rect)
                
        elif self.shape == "triangle":
            # Create an equilateral triangle
            center_x, center_y = render_size // 2, render_size // 2
            radius = max(1, int(self.size))
            
            # Calculate vertices
            angle_offset = math.radians(self.rotation if self.spin else 0)
            points = []
            for i in range(3):
                angle = angle_offset + math.radians(i * 120)
                point_x = center_x + radius * math.cos(angle)
                point_y = center_y + radius * math.sin(angle)
                points.append((point_x, point_y))
                
            pygame.draw.polygon(particle_surface, color_with_alpha, points)
            
        elif self.shape == "star":
            # Create a 5-pointed star
            center_x, center_y = render_size // 2, render_size // 2
            outer_radius = max(1, int(self.size))
            inner_radius = outer_radius * 0.4
            
            # Calculate vertices
            angle_offset = math.radians(self.rotation if self.spin else 0)
            points = []
            for i in range(10):
                angle = angle_offset + math.radians(i * 36)
                radius = outer_radius if i % 2 == 0 else inner_radius
                point_x = center_x + radius * math.cos(angle)
                point_y = center_y + radius * math.sin(angle)
                points.append((point_x, point_y))
                
            pygame.draw.polygon(particle_surface, color_with_alpha, points)
        
        # Blit the particle onto the main surface
        surface.blit(
            particle_surface,
            (int(self.x - render_size // 2), int(self.y - render_size // 2))
        ) 