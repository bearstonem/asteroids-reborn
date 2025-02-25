import pygame
import math
import random
from game.entities.particle import Particle

class Projectile:
    """
    Projectile entity for player weapons in Asteroids Reborn
    Enhanced with particle effects for more spectacular visuals
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
        
        # Store previous positions for trail effect
        self.trail_positions = []
        self.max_trail_length = 5  # Reduced from 10 to 5
        
        # Particle effect system
        self.particles = []
        self.particle_timer = 0
        
        # Projectile color (can be customized for different weapons)
        self.color = (255, 255, 100)  # Default yellow
        
        # Calculate projectile speed for effects intensity
        self.speed = math.sqrt(vel_x * vel_x + vel_y * vel_y)
        
        # Track last position to detect screen wrapping
        self.prev_x = x
        self.prev_y = y
    
    def update(self, dt):
        """Update projectile position, lifetime, and particle effects"""
        # Save previous position for edge detection
        self.prev_x = self.x
        self.prev_y = self.y
        
        # Update position
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
        
        # Screen wrapping detection
        # Get screen dimensions (assuming the standard screen size or the one used in the game)
        screen_width, screen_height = 800, 600  # Adjust if your game uses different dimensions
        
        # Check if projectile crossed screen edge
        crossed_edge = False
        
        # Handle screen edge crossing
        if (self.prev_x < 0 and self.x > screen_width * 0.9) or (self.prev_x > screen_width and self.x < screen_width * 0.1):
            crossed_edge = True
        if (self.prev_y < 0 and self.y > screen_height * 0.9) or (self.prev_y > screen_height and self.y < screen_height * 0.1):
            crossed_edge = True
            
        # Clear trail positions when crossing edge to avoid the visual bug
        if crossed_edge:
            self.trail_positions = []  # Reset trail when crossing screen edge
            # Also remove any existing particles to avoid visual artifacts
            self.particles = []
        
        # Store current position for trail (after edge check)
        self.trail_positions.append((self.x, self.y))
        if len(self.trail_positions) > self.max_trail_length:
            self.trail_positions.pop(0)
        
        # Update lifetime
        self.life -= dt
        
        # Generate trail particles
        self.particle_timer -= dt
        if self.particle_timer <= 0:
            self.particle_timer = 0.05  # Increased from 0.02 to 0.05 (less frequent particles)
            self.generate_particles()
        
        # Update existing particles
        for particle in self.particles[:]:
            particle.update(dt)
            if particle.life <= 0:
                self.particles.remove(particle)
    
    def generate_particles(self):
        """Generate trailing particles behind the projectile"""
        # Create particles at current position with randomized properties
        num_particles = random.randint(0, 1)  # Reduced from 1-3 to 0-1
        
        for _ in range(num_particles):
            # Opposite direction of projectile movement
            angle_rad = math.radians(self.angle + 180)
            spread = 0.3  # Reduced spread from 0.4 to 0.3
            particle_angle = angle_rad + random.uniform(-spread, spread)
            
            # Randomize particle velocity
            particle_speed = random.uniform(5, 25)  # Reduced from 10-40 to 5-25
            vel_x = math.cos(particle_angle) * particle_speed
            vel_y = math.sin(particle_angle) * particle_speed
            
            # Small position randomization
            offset_x = random.uniform(-1, 1)  # Reduced from -2,2 to -1,1
            offset_y = random.uniform(-1, 1)  # Reduced from -2,2 to -1,1
            
            # Determine particle color based on base projectile color
            r, g, b = self.color
            color_variation = random.randint(-20, 20)  # Reduced variation
            
            # Add slight color variations
            color = (
                max(0, min(255, r + color_variation)),
                max(0, min(255, g + color_variation)),
                max(0, min(255, b + color_variation))
            )
            
            # Add visual effects
            has_glow = random.random() < 0.2  # Reduced from 0.4 to 0.2
            has_trail = random.random() < 0.1  # Reduced from 0.3 to 0.1
            
            # Create particle with visual enhancements
            self.particles.append(
                Particle(
                    self.x + offset_x, self.y + offset_y,
                    vel_x, vel_y,
                    random.uniform(0.05, 0.2),  # Reduced lifetime from 0.1-0.4 to 0.05-0.2
                    color,
                    size=random.uniform(0.8, 1.8),  # Reduced size from 1.0-2.5 to 0.8-1.8
                    shape="circle",  # Most projectile particles are circles
                    trail=has_trail,
                    glow=has_glow,
                    fade_mode="normal",  # Removed randomization to simplify
                    spin=False  # No spin for projectile particles
                )
            )
    
    def render(self, surface):
        """Render the projectile with enhanced visual effects"""
        # Draw particles first (underneath the projectile)
        for particle in self.particles:
            particle.render(surface)
        
        # Skip drawing energy trail if we just crossed a screen edge
        should_draw_trail = len(self.trail_positions) > 2
        
        # Only draw trail if all points are close enough to each other
        if should_draw_trail:
            for i in range(len(self.trail_positions) - 1):
                # Check if any two consecutive points are too far apart (indicates screen wrap)
                x1, y1 = self.trail_positions[i]
                x2, y2 = self.trail_positions[i + 1]
                distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
                
                # If distance is too large, it's likely a screen wrap
                if distance > 100:  # Threshold for detecting a wrap
                    should_draw_trail = False
                    break
        
        # Draw a small elongated rectangle (bullet)
        angle_rad = math.radians(self.angle)
        
        # Bullet length
        length = 12  # Slightly longer than before
        width = 3    # Slightly wider than before
        
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
        
        # Draw the bullet with the core color
        pygame.draw.polygon(surface, self.color, points)
        
        # Add a bright center line for energy effect
        center_line = [
            (front_x, front_y),
            (back_x, back_y)
        ]
        pygame.draw.line(surface, (255, 255, 255), center_line[0], center_line[1], 1)
        
        # Add a small glow effect around the entire projectile
        glow_surface = pygame.Surface((int(length) + 14, int(width) + 14), pygame.SRCALPHA)
        glow_center = (glow_surface.get_width() // 2, glow_surface.get_height() // 2)
        
        # Draw multiple layers of glow with decreasing opacity
        for radius in range(8, 1, -2):
            alpha = 100 - radius * 10
            r, g, b = self.color
            pygame.draw.circle(
                glow_surface, 
                (r, g, b, max(0, alpha)), 
                glow_center, 
                radius
            )
        
        # Rotate the glow surface to match projectile direction
        rotated_glow = pygame.transform.rotate(glow_surface, -self.angle)
        glow_rect = rotated_glow.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(rotated_glow, glow_rect.topleft)
        
        # Draw energy trail using the trail positions
        if should_draw_trail:
            # Use a subset of trail positions for smoother effect
            step = max(1, len(self.trail_positions) // 5)
            selected_points = self.trail_positions[::step]
            
            # Draw connecting lines with fading opacity
            for i in range(len(selected_points) - 1):
                progress = i / (len(selected_points) - 1)  # 0.0 to 1.0
                alpha = int(120 * (1.0 - progress))  # Fade out alpha
                
                r, g, b = self.color
                color = (r, g, b, alpha)
                
                start_pos = selected_points[i]
                end_pos = selected_points[i+1]
                
                # Draw the trail segment with fading width and color
                width = max(1, int(3 * (1.0 - progress)))
                
                # Create a small surface for the semi-transparent trail segment
                dx = end_pos[0] - start_pos[0]
                dy = end_pos[1] - start_pos[1]
                line_length = math.sqrt(dx * dx + dy * dy)
                
                if line_length > 0 and line_length < 100:  # Add additional check here
                    # Draw on the main surface directly with a translucent color
                    pygame.draw.line(
                        surface,
                        color,
                        (int(start_pos[0]), int(start_pos[1])),
                        (int(end_pos[0]), int(end_pos[1])),
                        width
                    )
        
        # Debug: draw collision radius
        # pygame.draw.circle(surface, (255, 0, 0), (int(self.x), int(self.y)), int(self.radius), 1) 