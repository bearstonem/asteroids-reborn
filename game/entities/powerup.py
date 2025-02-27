import pygame
import math
import random

class Powerup:
    """
    Powerup entity for player upgrades in Asteroids Reborn
    """
    def __init__(self, x, y, vel_x, vel_y, powerup_type):
        self.x = x
        self.y = y
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.powerup_type = powerup_type
        self.radius = 25  # For collision detection
        self.life = 13.0  # Powerup despawns after 13 seconds
        self.pulse = 1  # For visual pulsing effect
        self.rotation = random.uniform(0, 360)  # Initial random rotation
        self.rotation_speed = random.uniform(-20, 20)  # Random rotation speed (degrees per second)
        
        # Set color based on powerup type
        if powerup_type == "shield":
            self.color = (100, 200, 255)  # Blue
        elif powerup_type == "rapidfire":
            self.color = (255, 200, 100)  # Orange
        elif powerup_type == "extralife":
            self.color = (100, 255, 100)  # Green
        elif powerup_type == "timeslow":
            self.color = (200, 100, 255)  # Purple
        elif powerup_type == "tripleshot":
            self.color = (255, 100, 100)  # Red
        elif powerup_type == "magnet":
            self.color = (255, 255, 100)  # Yellow
        elif powerup_type == "health":
            self.color = (255, 80, 80)  # Bright red for health
        else:
            self.color = (200, 200, 200)  # Gray (default)
    
    def update(self, dt, screen_width=800, screen_height=600):
        """Update powerup position and lifetime"""
        # Update position
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
        
        # Apply drag (reduced to allow more drifting like asteroids)
        self.vel_x *= 0.995
        self.vel_y *= 0.995
        
        # Update rotation
        self.rotation += self.rotation_speed * dt
        self.rotation %= 360
        
        # Wrap position around screen edges
        if self.x < -self.radius:
            self.x = screen_width + self.radius
        elif self.x > screen_width + self.radius:
            self.x = -self.radius
        if self.y < -self.radius:
            self.y = screen_height + self.radius
        elif self.y > screen_height + self.radius:
            self.y = -self.radius
        
        # Update lifetime
        self.life -= dt
        
        # Update visual pulse effect
        self.pulse = (self.pulse + dt * 5) % (2 * math.pi)
    
    def render(self, surface):
        """Render the powerup"""
        # Skip rendering if off screen (this check is no longer needed due to screen wrapping)
        # but keeping a simplified version for extreme cases
        if (self.x < -self.radius*2 or self.x > surface.get_width() + self.radius*2 or
            self.y < -self.radius*2 or self.y > surface.get_height() + self.radius*2):
            return
        
        # Make it blink faster when close to expiring
        if self.life < 3.0 and int(self.life * 5) % 2 == 0:
            return
        
        # Calculate pulse amount (0.0 to 1.0)
        pulse_amount = (math.sin(self.pulse) + 1) * 0.5
        
        # Draw the powerup with rotation
        if self.powerup_type == "shield":
            # Shield powerup (blue orb with shield symbol)
            # Draw outer orb
            pygame.draw.circle(
                surface,
                self.color,
                (int(self.x), int(self.y)),
                int(self.radius)
            )
            
            # Draw inner shield symbol with rotation
            shield_radius = self.radius * 0.7
            rotation_rad = math.radians(self.rotation)
            start_angle = rotation_rad + math.pi * 0.75
            end_angle = rotation_rad + math.pi * 2.25
            
            pygame.draw.arc(
                surface,
                (255, 255, 255),
                (int(self.x - shield_radius), int(self.y - shield_radius), 
                 int(shield_radius * 2), int(shield_radius * 2)),
                start_angle, end_angle,
                2
            )
            
        elif self.powerup_type == "rapidfire":
            # Rapid fire powerup (orange orb with lightning bolt)
            # Draw outer orb
            pygame.draw.circle(
                surface,
                self.color,
                (int(self.x), int(self.y)),
                int(self.radius)
            )
            
            # Draw lightning bolt symbol with rotation
            rotation_rad = math.radians(self.rotation)
            cos_rot = math.cos(rotation_rad)
            sin_rot = math.sin(rotation_rad)
            
            # Define bolt points relative to center
            rel_points = [
                (-5, -8),
                (2, -2),
                (-2, 0),
                (5, 8),
                (0, 2),
                (2, 0),
                (-2, -4)
            ]
            
            # Rotate and translate points
            bolt_points = []
            for rel_x, rel_y in rel_points:
                # Rotate point
                rot_x = rel_x * cos_rot - rel_y * sin_rot
                rot_y = rel_x * sin_rot + rel_y * cos_rot
                # Translate to powerup position
                bolt_points.append((self.x + rot_x, self.y + rot_y))
            
            pygame.draw.polygon(surface, (255, 255, 255), bolt_points)
            
        elif self.powerup_type == "extralife":
            # Extra life powerup (green orb with heart symbol)
            # Draw outer orb
            pygame.draw.circle(
                surface,
                self.color,
                (int(self.x), int(self.y)),
                int(self.radius)
            )
            
            # Calculate heart position with rotation
            heart_size = self.radius * 0.6
            rotation_rad = math.radians(self.rotation)
            
            # Translate heart top position based on rotation
            heart_offset_y = heart_size * 0.3
            heart_top_x = self.x - math.sin(rotation_rad) * heart_offset_y
            heart_top_y = self.y - math.cos(rotation_rad) * heart_offset_y
            
            # Calculate rotated heart halves
            left_half_x = heart_top_x - math.cos(rotation_rad) * heart_size * 0.35
            left_half_y = heart_top_y + math.sin(rotation_rad) * heart_size * 0.35
            
            right_half_x = heart_top_x + math.cos(rotation_rad) * heart_size * 0.35
            right_half_y = heart_top_y - math.sin(rotation_rad) * heart_size * 0.35
            
            # Left half of heart
            pygame.draw.circle(
                surface,
                (255, 255, 255),
                (int(left_half_x), int(left_half_y)),
                int(heart_size * 0.35)
            )
            
            # Right half of heart
            pygame.draw.circle(
                surface,
                (255, 255, 255),
                (int(right_half_x), int(right_half_y)),
                int(heart_size * 0.35)
            )
            
            # Bottom point of heart
            bottom_x = self.x + math.sin(rotation_rad) * heart_size * 0.5
            bottom_y = self.y + math.cos(rotation_rad) * heart_size * 0.5
            
            # Bottom triangle of heart
            heart_points = [
                (left_half_x, left_half_y),
                (right_half_x, right_half_y),
                (bottom_x, bottom_y)
            ]
            pygame.draw.polygon(surface, (255, 255, 255), heart_points)
        
        elif self.powerup_type == "timeslow":
            # Time slow powerup (purple orb with hourglass symbol)
            # Draw outer orb
            pygame.draw.circle(
                surface,
                self.color,
                (int(self.x), int(self.y)),
                int(self.radius)
            )
            
            # Draw hourglass symbol with rotation
            symbol_size = self.radius * 0.7
            rotation_rad = math.radians(self.rotation)
            cos_rot = math.cos(rotation_rad)
            sin_rot = math.sin(rotation_rad)
            
            # Define hourglass points relative to center
            rel_points = [
                (-symbol_size * 0.5, -symbol_size * 0.6),  # Top-left
                (symbol_size * 0.5, -symbol_size * 0.6),   # Top-right
                (0, 0),                                    # Middle
                (symbol_size * 0.5, symbol_size * 0.6),    # Bottom-right
                (-symbol_size * 0.5, symbol_size * 0.6),   # Bottom-left
                (0, 0)                                     # Middle (connect back)
            ]
            
            # Rotate and translate points
            hourglass_points = []
            for rel_x, rel_y in rel_points:
                # Rotate point
                rot_x = rel_x * cos_rot - rel_y * sin_rot
                rot_y = rel_x * sin_rot + rel_y * cos_rot
                # Translate to powerup position
                hourglass_points.append((self.x + rot_x, self.y + rot_y))
            
            pygame.draw.lines(surface, (255, 255, 255), False, hourglass_points, 2)
        
        elif self.powerup_type == "tripleshot":
            # Triple shot powerup (red orb with three bullet symbols)
            # Draw outer orb
            pygame.draw.circle(
                surface,
                self.color,
                (int(self.x), int(self.y)),
                int(self.radius)
            )
            
            # Draw triple shot symbol with rotation
            symbol_size = self.radius * 0.5
            rotation_rad = math.radians(self.rotation)
            cos_rot = math.cos(rotation_rad)
            sin_rot = math.sin(rotation_rad)
            
            # Draw three small circles representing bullets
            for i in range(3):
                angle = rotation_rad + i * (2 * math.pi / 3)
                bullet_x = self.x + math.cos(angle) * symbol_size * 0.6
                bullet_y = self.y + math.sin(angle) * symbol_size * 0.6
                
                pygame.draw.circle(
                    surface,
                    (255, 255, 255),
                    (int(bullet_x), int(bullet_y)),
                    int(symbol_size * 0.25)
                )
            
            # Draw center connection
            pygame.draw.circle(
                surface,
                (255, 255, 255),
                (int(self.x), int(self.y)),
                int(symbol_size * 0.15)
            )
        
        elif self.powerup_type == "magnet":
            # Magnet powerup (yellow orb with magnet symbol)
            # Draw outer orb
            pygame.draw.circle(
                surface,
                self.color,
                (int(self.x), int(self.y)),
                int(self.radius)
            )
            
            # Draw magnet symbol with rotation
            symbol_size = self.radius * 0.7
            rotation_rad = math.radians(self.rotation)
            cos_rot = math.cos(rotation_rad)
            sin_rot = math.sin(rotation_rad)
            
            # Draw horseshoe magnet symbol
            magnet_width = symbol_size * 0.7
            magnet_height = symbol_size
            
            # U shape points
            rel_points = [
                (-magnet_width/2, -magnet_height/2),  # Left top
                (-magnet_width/2, magnet_height/2),   # Left bottom
                (0, magnet_height/2),                # Bottom middle
                (magnet_width/2, magnet_height/2),   # Right bottom
                (magnet_width/2, -magnet_height/2)   # Right top
            ]
            
            # Rotate and translate points
            magnet_points = []
            for rel_x, rel_y in rel_points:
                # Rotate point
                rot_x = rel_x * cos_rot - rel_y * sin_rot
                rot_y = rel_x * sin_rot + rel_y * cos_rot
                # Translate to powerup position
                magnet_points.append((self.x + rot_x, self.y + rot_y))
            
            pygame.draw.lines(surface, (255, 255, 255), False, magnet_points, 2)
            
            # Draw N/S poles
            pole_size = symbol_size * 0.25
            
            # North pole
            n_pole_x = self.x - (magnet_width/2) * cos_rot
            n_pole_y = self.y - (magnet_width/2) * sin_rot
            pygame.draw.line(
                surface,
                (255, 0, 0),  # Red for North
                (int(n_pole_x), int(n_pole_y)),
                (int(n_pole_x - pole_size * sin_rot), int(n_pole_y + pole_size * cos_rot)),
                3
            )
            
            # South pole
            s_pole_x = self.x + (magnet_width/2) * cos_rot
            s_pole_y = self.y + (magnet_width/2) * sin_rot
            pygame.draw.line(
                surface,
                (0, 0, 255),  # Blue for South
                (int(s_pole_x), int(s_pole_y)),
                (int(s_pole_x - pole_size * sin_rot), int(s_pole_y + pole_size * cos_rot)),
                3
            )
        
        elif self.powerup_type == "health":
            # Health powerup (red orb with medical cross)
            # Draw outer orb
            pygame.draw.circle(
                surface,
                self.color,
                (int(self.x), int(self.y)),
                int(self.radius)
            )
            
            # Draw medical cross symbol with rotation and pulsing effect
            cross_size = self.radius * (0.6 + 0.1 * pulse_amount)  # Pulsing size
            rotation_rad = math.radians(self.rotation)
            cos_rot = math.cos(rotation_rad)
            sin_rot = math.sin(rotation_rad)
            
            # Cross thickness varies with pulse
            cross_thickness = int(2 + pulse_amount * 1)
            
            # Vertical line of cross
            v_start_x = self.x - sin_rot * cross_size
            v_start_y = self.y - cos_rot * cross_size
            v_end_x = self.x + sin_rot * cross_size
            v_end_y = self.y + cos_rot * cross_size
            
            # Horizontal line of cross
            h_start_x = self.x - cos_rot * cross_size
            h_start_y = self.y + sin_rot * cross_size
            h_end_x = self.x + cos_rot * cross_size
            h_end_y = self.y - sin_rot * cross_size
            
            # Draw both lines of the cross
            pygame.draw.line(
                surface,
                (255, 255, 255),
                (int(v_start_x), int(v_start_y)),
                (int(v_end_x), int(v_end_y)),
                cross_thickness
            )
            
            pygame.draw.line(
                surface,
                (255, 255, 255),
                (int(h_start_x), int(h_start_y)),
                (int(h_end_x), int(h_end_y)),
                cross_thickness
            )
            
            # Add a subtle glow effect around the cross
            if pulse_amount > 0.7:  # Only show glow at peak of pulse
                glow_surface = pygame.Surface((int(cross_size*3), int(cross_size*3)), pygame.SRCALPHA)
                glow_color = (255, 150, 150, int(70 * (pulse_amount - 0.7) / 0.3))
                pygame.draw.circle(
                    glow_surface,
                    glow_color,
                    (int(cross_size*1.5), int(cross_size*1.5)),
                    int(cross_size * 1.2)
                )
                surface.blit(
                    glow_surface,
                    (int(self.x - cross_size*1.5), int(self.y - cross_size*1.5))
                )
        
        # Add glow effect based on pulse
        glow_radius = self.radius * (1 + pulse_amount * 0.3)
        glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        glow_alpha = int(100 * pulse_amount)
        glow_color = (*self.color, glow_alpha)
        pygame.draw.circle(
            glow_surface,
            glow_color,
            (int(glow_radius), int(glow_radius)),
            int(glow_radius)
        )
        surface.blit(
            glow_surface,
            (int(self.x - glow_radius), int(self.y - glow_radius))
        ) 