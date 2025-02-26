import pygame
import math
import random
from game.entities.particle import Particle

class Player:
    """
    Player spaceship entity for Asteroids Reborn
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vel_x = 0
        self.vel_y = 0
        self.rotation = 0  # Angle in degrees
        self.thrust_power = 0
        self.radius = 20  # For collision detection
        
        # Player state
        self.lives = 3
        self.health = 3  # New health property, player can take 3 hits before losing a life
        self.is_thrusting = False
        self.was_thrusting = False  # Track previous thrust state for sound
        self.is_turning_left = False
        self.is_turning_right = False
        self.is_shooting = False
        self.invulnerable = False
        self.invulnerable_timer = 0
        self.rapid_fire = False
        self.rapid_fire_timer = 0
        self.shoot_cooldown = 0
        
        # New powerups
        self.time_slow = False
        self.time_slow_timer = 0
        self.triple_shot = False
        self.triple_shot_timer = 0
        self.magnet = False
        self.magnet_timer = 0
        self.magnet_radius = 250  # Increased from 150 to 250 for larger attraction range
        
        # Particle system for thruster effect
        self.thruster_particles = []
        self.thruster_timer = 0  # Timer for creating new particles
        
        # Player characteristics
        self.rotation_speed = 180  # degrees per second
        self.thrust_strength = 200  # acceleration
        self.max_velocity = 300
        self.friction = 0.9999  # velocity damping (reduced from 0.98 for less friction in space)
    
    def take_damage(self):
        """Handle player taking damage"""
        self.health -= 1
        
        if self.health <= 0:
            # Reset health for next life
            self.health = 3
            return True  # Signal that player lost a life
        
        # Make player temporarily invulnerable after being hit
        self.invulnerable = True
        self.invulnerable_timer = 2.0  # 2 seconds of invulnerability
        
        return False  # Player damaged but still alive
    
    def handle_event(self, event):
        """Handle input events for player control"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                self.is_turning_left = True
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                self.is_turning_right = True
            elif event.key == pygame.K_UP or event.key == pygame.K_w:
                self.is_thrusting = True
            elif event.key == pygame.K_SPACE:
                self.is_shooting = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                self.is_turning_left = False
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                self.is_turning_right = False
            elif event.key == pygame.K_UP or event.key == pygame.K_w:
                self.is_thrusting = False
            elif event.key == pygame.K_SPACE:
                self.is_shooting = False
    
    def update(self, dt, sound_manager=None):
        """Update player state"""
        # Handle rotation
        if self.is_turning_left:
            self.rotation -= self.rotation_speed * dt
        if self.is_turning_right:
            self.rotation += self.rotation_speed * dt
        
        # Normalize rotation to 0-360 degrees
        self.rotation %= 360
        
        # Handle thrust
        if self.is_thrusting:
            # Calculate acceleration vector from ship rotation
            angle_rad = math.radians(self.rotation)
            accel_x = math.cos(angle_rad) * self.thrust_strength * dt
            accel_y = math.sin(angle_rad) * self.thrust_strength * dt
            
            # Apply acceleration to velocity
            self.vel_x += accel_x
            self.vel_y += accel_y
            
            # Limit velocity to max speed
            velocity = math.sqrt(self.vel_x * self.vel_x + self.vel_y * self.vel_y)
            if velocity > self.max_velocity:
                scale = self.max_velocity / velocity
                self.vel_x *= scale
                self.vel_y *= scale
            
            # Generate thruster particles
            self.thruster_timer -= dt
            if self.thruster_timer <= 0:
                self.thruster_timer = 0.01  # Create new particles every 0.01 seconds
                self.create_thruster_particles()
            
            # Loop thrust sound while thrusting
            if sound_manager:
                sound_manager.loop("thrust")
        else:
            # Stop thrust sound when not thrusting
            if sound_manager and self.was_thrusting:
                sound_manager.stop("thrust")
        
        # Track thrust state for sound
        self.was_thrusting = self.is_thrusting
        
        # Apply friction/damping
        self.vel_x *= self.friction
        self.vel_y *= self.friction
        
        # Update position based on velocity
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
        
        # Update thruster particles
        for particle in self.thruster_particles[:]:
            particle.update(dt)
            if particle.life <= 0:
                self.thruster_particles.remove(particle)
        
        # Update timers
        if self.invulnerable:
            self.invulnerable_timer -= dt
            if self.invulnerable_timer <= 0:
                self.invulnerable = False
        
        if self.rapid_fire:
            self.rapid_fire_timer -= dt
            if self.rapid_fire_timer <= 0:
                self.rapid_fire = False
        
        # Update new powerup timers
        if self.time_slow:
            self.time_slow_timer -= dt
            if self.time_slow_timer <= 0:
                self.time_slow = False
        
        if self.triple_shot:
            self.triple_shot_timer -= dt
            if self.triple_shot_timer <= 0:
                self.triple_shot = False
        
        if self.magnet:
            self.magnet_timer -= dt
            if self.magnet_timer <= 0:
                self.magnet = False
        
        # Update shoot cooldown
        if self.shoot_cooldown > 0:
            if self.rapid_fire:
                self.shoot_cooldown -= dt * 2  # Rapid fire is twice as fast
            else:
                self.shoot_cooldown -= dt
    
    def create_thruster_particles(self):
        """Create thruster particles when ship is accelerating"""
        # Calculate thruster position at the back of the ship
        angle_rad = math.radians(self.rotation)
        back_angle = angle_rad + math.pi  # Opposite direction of ship heading
        
        # Create particles at the back of the ship with an offset
        back_offset = 15  # Distance from ship center to thruster
        thruster_x = self.x + math.cos(back_angle) * back_offset
        thruster_y = self.y + math.sin(back_angle) * back_offset
        
        # Create multiple particles for a more dynamic effect
        num_particles = random.randint(2, 5)
        for _ in range(num_particles):
            # Randomize particle direction slightly
            spread = 0.3  # Angle spread in radians
            particle_angle = back_angle + random.uniform(-spread, spread)
            
            # Calculate initial particle velocity (opposite direction of ship movement)
            particle_speed = random.uniform(20, 100)
            vel_x = math.cos(particle_angle) * particle_speed
            vel_y = math.sin(particle_angle) * particle_speed
            
            # Create different colors for thruster based on ship velocity
            velocity = math.sqrt(self.vel_x * self.vel_x + self.vel_y * self.vel_y)
            intensity = min(1.0, velocity / self.max_velocity)
            
            # Color ranges based on ship's health and velocity
            if self.health == 3:  # Blue theme
                if random.random() < 0.7:  # 70% are main flame color
                    r = int(100 + 50 * intensity)
                    g = int(150 + 50 * intensity)
                    b = int(200 + 55 * intensity)
                    color = (r, g, b)
                else:  # 30% are brighter core
                    color = (180, 220, random.randint(230, 255))
            elif self.health == 2:  # Purple theme
                if random.random() < 0.7:  # 70% are main flame color
                    r = int(120 + 60 * intensity)
                    g = int(60 + 40 * intensity)
                    b = int(180 + 75 * intensity)
                    color = (r, g, b)
                else:  # 30% are brighter core
                    color = (180, 140, random.randint(230, 255))
            else:  # Teal theme
                if random.random() < 0.7:  # 70% are main flame color
                    r = int(20 + 30 * intensity)
                    g = int(150 + 80 * intensity)
                    b = int(100 + 50 * intensity)
                    color = (r, g, b)
                else:  # 30% are brighter core
                    color = (100, random.randint(220, 255), 200)
            
            # Add slight randomization to particle position
            offset_x = random.uniform(-3, 3)
            offset_y = random.uniform(-3, 3)
            
            # Add particle effects
            has_glow = random.random() < 0.4
            has_trail = random.random() < 0.3
            
            # Determine particle shape and fade behavior
            if random.random() < 0.8:
                shape = "circle"  # Most thruster particles are circles
                fade = "normal" if random.random() < 0.7 else "pulse"
            else:
                shape = random.choice(["triangle", "square"])
                fade = "flicker"
            
            # Create the particle with enhanced visual effects
            self.thruster_particles.append(
                Particle(
                    thruster_x + offset_x, thruster_y + offset_y,
                    vel_x, vel_y,
                    random.uniform(0.2, 0.6),  # Lifetime
                    color,
                    size=random.uniform(1.5, 4.0),
                    shape=shape,
                    trail=has_trail,
                    glow=has_glow,
                    fade_mode=fade,
                    spin=random.random() < 0.3
                )
            )
    
    def render(self, surface):
        """Render the player ship"""
        # Update particle effects
        self.update_particles()
        
        # Render thruster particles
        for particle in self.thruster_particles:
            particle.render(surface)
        
        # Skip rendering the ship if invulnerable and should be invisible
        if self.invulnerable and pygame.time.get_ticks() % 200 < 100:
            return
        
        # Calculate ship vertices based on current rotation
        angle_rad = math.radians(self.rotation)
        
        # Ship design - identical to enemy ship structure
        main_points = [
            # Sharp pointed nose
            (self.x + math.cos(angle_rad) * 28, 
             self.y + math.sin(angle_rad) * 28),
            
            # Front armor plates
            (self.x + math.cos(angle_rad + 0.4) * 20, 
             self.y + math.sin(angle_rad + 0.4) * 20),
            
            (self.x + math.cos(angle_rad - 0.4) * 20, 
             self.y + math.sin(angle_rad - 0.4) * 20),
            
            # Forward wing struts
            (self.x + math.cos(angle_rad + 0.8) * 15, 
             self.y + math.sin(angle_rad + 0.8) * 15),
            
            (self.x + math.cos(angle_rad - 0.8) * 15, 
             self.y + math.sin(angle_rad - 0.8) * 15),
            
            # Right wing tip (extended and sharper)
            (self.x + math.cos(angle_rad + 2.0) * 24, 
             self.y + math.sin(angle_rad + 2.0) * 24),
            
            # Right wing back (aggressive angle)
            (self.x + math.cos(angle_rad + 2.6) * 20, 
             self.y + math.sin(angle_rad + 2.6) * 20),
            
            # Right inner wing detail
            (self.x + math.cos(angle_rad + 2.9) * 12, 
             self.y + math.sin(angle_rad + 2.9) * 12),
            
            # Tail structure (deeper, more defined)
            (self.x + math.cos(angle_rad + math.pi - 0.3) * 10, 
             self.y + math.sin(angle_rad + math.pi - 0.3) * 10),
            
            (self.x + math.cos(angle_rad + math.pi) * 12, 
             self.y + math.sin(angle_rad + math.pi) * 12),
            
            (self.x + math.cos(angle_rad + math.pi + 0.3) * 10, 
             self.y + math.sin(angle_rad + math.pi + 0.3) * 10),
            
            # Left inner wing detail
            (self.x + math.cos(angle_rad - 2.9) * 12, 
             self.y + math.sin(angle_rad - 2.9) * 12),
            
            # Left wing back (aggressive angle)
            (self.x + math.cos(angle_rad - 2.6) * 20, 
             self.y + math.sin(angle_rad - 2.6) * 20),
            
            # Left wing tip (extended and sharper)
            (self.x + math.cos(angle_rad - 2.0) * 24, 
             self.y + math.sin(angle_rad - 2.0) * 24),
        ]
        
        # Secondary hull details for more depth - identical to enemy ship
        secondary_points = [
            # Front section
            (self.x + math.cos(angle_rad) * 18, 
             self.y + math.sin(angle_rad) * 18),
            
            (self.x + math.cos(angle_rad + 1.0) * 10, 
             self.y + math.sin(angle_rad + 1.0) * 10),
            
            # Cockpit
            (self.x + math.cos(angle_rad + 2.0) * 5, 
             self.y + math.sin(angle_rad + 2.0) * 5),
            
            (self.x + math.cos(angle_rad + math.pi) * 8, 
             self.y + math.sin(angle_rad + math.pi) * 8),
            
            (self.x + math.cos(angle_rad - 2.0) * 5, 
             self.y + math.sin(angle_rad - 2.0) * 5),
            
            (self.x + math.cos(angle_rad - 1.0) * 10, 
             self.y + math.sin(angle_rad - 1.0) * 10),
        ]
        
        # Player ship colors based on health
        if self.health == 3:
            # Full health - vibrant blue/teal with bright highlights
            base_color = (30, 150, 255)  # Bright blue
            highlight_color = (100, 220, 255)  # Cyan highlight
            glow_color = (50, 200, 255, 100)  # Blue-cyan glow
        elif self.health == 2:
            # Medium health - purple/violet
            base_color = (120, 60, 220)  # Purple
            highlight_color = (180, 100, 255)  # Bright violet highlight
            glow_color = (160, 80, 255, 100)  # Purple glow
        else:
            # Low health - teal/green
            base_color = (20, 180, 130)  # Teal green
            highlight_color = (40, 255, 170)  # Bright teal highlight
            glow_color = (30, 220, 150, 100)  # Teal glow
            
        # Add engine glow - identical to enemy but with player colors
        engine_glow_radius = 8 + (pygame.time.get_ticks() % 6) / 3.0  # Pulsating effect
        
        # Engine position
        back_angle = angle_rad + math.pi
        engine_x = self.x + math.cos(back_angle) * 12
        engine_y = self.y + math.sin(back_angle) * 12
        
        # Create a surface for the glow with alpha
        glow_surface = pygame.Surface((int(engine_glow_radius*2), int(engine_glow_radius*2)), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, glow_color, 
                          (int(engine_glow_radius), int(engine_glow_radius)), 
                          int(engine_glow_radius))
        
        # Apply the glow
        surface.blit(glow_surface, 
                    (int(engine_x - engine_glow_radius), 
                     int(engine_y - engine_glow_radius)))
        
        # Draw the ship hull
        pygame.draw.polygon(surface, base_color, main_points)
        
        # Draw inner hull details
        pygame.draw.polygon(surface, highlight_color, secondary_points)
        
        # Add edge highlights
        pygame.draw.polygon(surface, highlight_color, main_points, 1)
        
        # Add glowing energy effects on the wings
        wing_glow_size = 4 + (pygame.time.get_ticks() % 1000) / 500.0  # Pulsating
        
        # Right wing energy point
        right_wing_x = self.x + math.cos(angle_rad + 2.0) * 22
        right_wing_y = self.y + math.sin(angle_rad + 2.0) * 22
        
        # Left wing energy point
        left_wing_x = self.x + math.cos(angle_rad - 2.0) * 22
        left_wing_y = self.y + math.sin(angle_rad - 2.0) * 22
        
        # Create wing glow surfaces
        wing_glow = pygame.Surface((int(wing_glow_size*2), int(wing_glow_size*2)), pygame.SRCALPHA)
        pygame.draw.circle(wing_glow, glow_color, 
                          (int(wing_glow_size), int(wing_glow_size)), 
                          int(wing_glow_size))
        
        # Apply wing glows
        surface.blit(wing_glow, (int(right_wing_x - wing_glow_size), int(right_wing_y - wing_glow_size)))
        surface.blit(wing_glow, (int(left_wing_x - wing_glow_size), int(left_wing_y - wing_glow_size)))
        
        # Draw engine thrust if thrusting with enhanced visual effect
        if self.is_thrusting:
            # Engine position (behind the ship)
            engine_angle = angle_rad + math.pi  # Opposite direction of ship heading
            
            # Create flame effect with random length and layered appearance
            flame_length = 12 + (pygame.time.get_ticks() % 8)  # Enhanced fluctuating flame
            flame_width = 7 + random.uniform(-1, 1)
            
            # Flame colors based on player health
            if self.health == 3:
                outer_flame = (40, 100, 255)  # Deep blue flame
                mid_flame = (80, 160, 255)    # Medium blue
                inner_flame = (160, 230, 255) # White-blue core
            elif self.health == 2:
                outer_flame = (100, 50, 200)  # Purple flame
                mid_flame = (150, 100, 220)   # Lighter purple
                inner_flame = (200, 180, 255) # White-purple core 
            else:
                outer_flame = (30, 150, 100)  # Teal flame
                mid_flame = (50, 200, 150)    # Brighter teal
                inner_flame = (180, 255, 220) # White-teal core
            
            # Outer flame layer
            flame_points = [
                # Center of back
                (self.x + math.cos(angle_rad + math.pi) * 12, 
                 self.y + math.sin(angle_rad + math.pi) * 12),
                
                # Right edge of flame
                (self.x + math.cos(engine_angle + 0.4) * flame_width, 
                 self.y + math.sin(engine_angle + 0.4) * flame_width),
                
                # Tip of flame
                (self.x + math.cos(engine_angle) * (flame_length + 5), 
                 self.y + math.sin(engine_angle) * (flame_length + 5)),
                
                # Left edge of flame
                (self.x + math.cos(engine_angle - 0.4) * flame_width, 
                 self.y + math.sin(engine_angle - 0.4) * flame_width),
            ]
            
            # Draw the flame
            pygame.draw.polygon(surface, outer_flame, flame_points)
            
            # Middle flame layer
            mid_flame_length = flame_length * 0.8
            mid_flame_width = flame_width * 0.7
            
            mid_flame_points = [
                (self.x + math.cos(angle_rad + math.pi) * 12, 
                 self.y + math.sin(angle_rad + math.pi) * 12),
                (self.x + math.cos(engine_angle + 0.3) * mid_flame_width, 
                 self.y + math.sin(engine_angle + 0.3) * mid_flame_width),
                (self.x + math.cos(engine_angle) * (mid_flame_length + 3), 
                 self.y + math.sin(engine_angle) * (mid_flame_length + 3)),
                (self.x + math.cos(engine_angle - 0.3) * mid_flame_width, 
                 self.y + math.sin(engine_angle - 0.3) * mid_flame_width),
            ]
            
            pygame.draw.polygon(surface, mid_flame, mid_flame_points)
            
            # Inner flame layer
            inner_flame_length = flame_length * 0.5
            inner_flame_width = flame_width * 0.4
            
            inner_flame_points = [
                (self.x + math.cos(angle_rad + math.pi) * 12, 
                 self.y + math.sin(angle_rad + math.pi) * 12),
                (self.x + math.cos(engine_angle + 0.2) * inner_flame_width, 
                 self.y + math.sin(engine_angle + 0.2) * inner_flame_width),
                (self.x + math.cos(engine_angle) * (inner_flame_length + 2), 
                 self.y + math.sin(engine_angle) * (inner_flame_length + 2)),
                (self.x + math.cos(engine_angle - 0.2) * inner_flame_width, 
                 self.y + math.sin(engine_angle - 0.2) * inner_flame_width),
            ]
            
            pygame.draw.polygon(surface, inner_flame, inner_flame_points)
            
            # Add secondary thruster effects on the wings
            if random.random() < 0.6:  # Occasional random bursts
                side_flame_size = 4 + random.uniform(-1, 1)
                
                # Right thruster position
                right_thruster_x = self.x + math.cos(angle_rad + 2.6) * 18
                right_thruster_y = self.y + math.sin(angle_rad + 2.6) * 18
                
                right_flame_points = [
                    (right_thruster_x, right_thruster_y),
                    (right_thruster_x + math.cos(engine_angle + 0.3) * side_flame_size/2, 
                     right_thruster_y + math.sin(engine_angle + 0.3) * side_flame_size/2),
                    (right_thruster_x + math.cos(engine_angle) * side_flame_size, 
                     right_thruster_y + math.sin(engine_angle) * side_flame_size),
                    (right_thruster_x + math.cos(engine_angle - 0.3) * side_flame_size/2, 
                     right_thruster_y + math.sin(engine_angle - 0.3) * side_flame_size/2),
                ]
                
                # Left thruster position
                left_thruster_x = self.x + math.cos(angle_rad - 2.6) * 18
                left_thruster_y = self.y + math.sin(angle_rad - 2.6) * 18
                
                left_flame_points = [
                    (left_thruster_x, left_thruster_y),
                    (left_thruster_x + math.cos(engine_angle + 0.3) * side_flame_size/2, 
                     left_thruster_y + math.sin(engine_angle + 0.3) * side_flame_size/2),
                    (left_thruster_x + math.cos(engine_angle) * side_flame_size, 
                     left_thruster_y + math.sin(engine_angle) * side_flame_size),
                    (left_thruster_x + math.cos(engine_angle - 0.3) * side_flame_size/2, 
                     left_thruster_y + math.sin(engine_angle - 0.3) * side_flame_size/2),
                ]
                
                # Draw side thrusters with flame colors
                pygame.draw.polygon(surface, outer_flame, right_flame_points)
                pygame.draw.polygon(surface, outer_flame, left_flame_points)
        
        # Health indicator using pulsating energy lines along the hull
        if self.health > 0:
            # Pulse based on health level (faster pulse when lower health)
            pulse_speed = 1500 - (self.health * 300)  # 300, 600, 900, 1200 ms
            pulse_phase = (pygame.time.get_ticks() % pulse_speed) / pulse_speed
            
            # Color based on player's health
            if self.health == 3:
                line_base_color = (0, 100, 255)  # Blue energy
            elif self.health == 2:
                line_base_color = (120, 60, 220)  # Purple energy
            else:
                line_base_color = (20, 180, 130)  # Teal energy
            
            # Draw energy lines along hull based on health
            for i in range(self.health):
                line_intensity = int(100 + 155 * pulse_phase)
                
                # Pulse effect based on health
                if self.health == 3:
                    line_color = (line_intensity, line_intensity, 255)  # Blue pulsing
                elif self.health == 2:
                    line_color = (line_intensity, line_intensity//2, 255)  # Purple pulsing
                else:
                    line_color = (line_intensity//2, 255, line_intensity)  # Teal pulsing
                
                # Position based on health index
                line_angle = angle_rad + 0.5 + (i * 0.4)
                line_start_x = self.x + math.cos(line_angle) * 5
                line_start_y = self.y + math.sin(line_angle) * 5
                line_end_x = self.x + math.cos(line_angle) * 18
                line_end_y = self.y + math.sin(line_angle) * 18
                
                # Draw the energy line
                pygame.draw.line(surface, line_color, 
                                (int(line_start_x), int(line_start_y)),
                                (int(line_end_x), int(line_end_y)), 2)
                
                # Mirror on other side
                line_angle = angle_rad - 0.5 - (i * 0.4)
                line_start_x = self.x + math.cos(line_angle) * 5
                line_start_y = self.y + math.sin(line_angle) * 5
                line_end_x = self.x + math.cos(line_angle) * 18
                line_end_y = self.y + math.sin(line_angle) * 18
                
                # Draw the mirrored energy line
                pygame.draw.line(surface, line_color, 
                                (int(line_start_x), int(line_start_y)),
                                (int(line_end_x), int(line_end_y)), 2)
                
        # Draw shield if invulnerable with a more impressive appearance than before
        if self.invulnerable:
            # Pulsating shield effect
            shield_pulse = (pygame.time.get_ticks() % 1000) / 1000.0
            shield_radius = self.radius + 8 + 4 * shield_pulse  # Larger, more visible
            
            # Create shield colors to match the ship's color theme
            if self.health == 3:
                shield_color_outer = (100, 200, 255, 100)  # Blue shield
                shield_color_inner = (150, 220, 255, 60)   # Inner blue
            elif self.health == 2:
                shield_color_outer = (140, 100, 255, 100)  # Purple shield
                shield_color_inner = (180, 150, 255, 60)   # Inner purple
            else:
                shield_color_outer = (50, 220, 150, 100)   # Teal shield
                shield_color_inner = (100, 255, 180, 60)   # Inner teal
            
            # Create surface for shield with alpha
            shield_surface = pygame.Surface((int(shield_radius*2 + 4), int(shield_radius*2 + 4)), pygame.SRCALPHA)
            
            # Draw outer shield
            pygame.draw.circle(
                shield_surface, 
                shield_color_outer, 
                (int(shield_radius + 2), int(shield_radius + 2)), 
                int(shield_radius),
                3  # Thicker shield border for more visibility
            )
            
            # Draw inner shield
            pygame.draw.circle(
                shield_surface, 
                shield_color_inner, 
                (int(shield_radius + 2), int(shield_radius + 2)), 
                int(shield_radius * 0.8),
                2  # Thicker inner shield for more visibility
            )
            
            # Draw advanced shield hexagon pattern
            for i in range(6):
                angle = i * (math.pi/3) + (pygame.time.get_ticks() % 6000) / 3000 * math.pi  # Rotating hexagon
                start_x = int(shield_radius + 2 + math.cos(angle) * shield_radius * 0.9)
                start_y = int(shield_radius + 2 + math.sin(angle) * shield_radius * 0.9)
                end_x = int(shield_radius + 2 + math.cos(angle + math.pi/3) * shield_radius * 0.9)
                end_y = int(shield_radius + 2 + math.sin(angle + math.pi/3) * shield_radius * 0.9)
                pygame.draw.line(shield_surface, shield_color_outer, (start_x, start_y), (end_x, end_y), 2)
            
            # Apply the shield
            surface.blit(
                shield_surface,
                (int(self.x - shield_radius - 2), int(self.y - shield_radius - 2))
            )
        
        # Draw magnet field if active with improved appearance
        if self.magnet:
            # More dramatic color that matches the ship's color scheme
            if self.health == 3:
                magnet_color = (100, 150, 255, 20)  # Blue magnet field
                pulse_color = (150, 200, 255, 30)   # Blue pulse
            elif self.health == 2:
                magnet_color = (120, 80, 220, 20)   # Purple magnet field
                pulse_color = (160, 120, 255, 30)   # Purple pulse
            else:
                magnet_color = (40, 180, 130, 20)   # Teal magnet field
                pulse_color = (80, 220, 150, 30)    # Teal pulse
            
            magnet_surface = pygame.Surface((self.magnet_radius * 2, self.magnet_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                magnet_surface,
                magnet_color,
                (int(self.magnet_radius), int(self.magnet_radius)),
                int(self.magnet_radius)
            )
            
            # Add pulsing effects
            pulse = (pygame.time.get_ticks() % 1000) / 1000.0
            pulse_radius = int(self.magnet_radius * (0.7 + 0.3 * pulse))
            pygame.draw.circle(
                magnet_surface,
                pulse_color,
                (int(self.magnet_radius), int(self.magnet_radius)),
                pulse_radius,
                4
            )
            
            surface.blit(
                magnet_surface,
                (int(self.x - self.magnet_radius), int(self.y - self.magnet_radius))
            )
        
        # Draw time slow effect if active
        if self.time_slow:
            # Match color to ship's current color scheme
            if self.health == 3:
                time_color = (120, 180, 255, 120)  # Blue time effect
            elif self.health == 2:
                time_color = (140, 100, 220, 120)  # Purple time effect
            else:
                time_color = (60, 200, 150, 120)   # Teal time effect
            
            # Create time distortion waves
            time_surface = pygame.Surface((100, 100), pygame.SRCALPHA)
            wave_count = 3
            
            for i in range(wave_count):
                progress = (pygame.time.get_ticks() / (2000 + i * 500)) % 1.0
                radius = 10 + progress * 40
                width = max(1, int(3 * (1.0 - progress)))
                alpha = int(150 * (1.0 - progress))
                wave_color = (time_color[0], time_color[1], time_color[2], alpha)
                
                pygame.draw.circle(
                    time_surface,
                    wave_color,
                    (50, 50),
                    int(radius),
                    width
                )
            
            # Add a clock hand effect in the center
            angle = (pygame.time.get_ticks() / 4000.0) % (2 * math.pi)
            # Hour hand
            hour_length = 15
            hour_x = 50 + math.cos(angle) * hour_length
            hour_y = 50 + math.sin(angle) * hour_length
            pygame.draw.line(
                time_surface,
                time_color,
                (50, 50),
                (int(hour_x), int(hour_y)),
                2
            )
            
            # Minute hand
            minute_length = 20
            minute_x = 50 + math.cos(angle * 12) * minute_length
            minute_y = 50 + math.sin(angle * 12) * minute_length
            pygame.draw.line(
                time_surface,
                time_color,
                (50, 50),
                (int(minute_x), int(minute_y)),
                1
            )
            
            # Apply time effect
            surface.blit(
                time_surface,
                (int(self.x - 50), int(self.y - 50))
            )
    
    def update_particles(self):
        """Update thruster particles"""
        # Remove expired particles
        self.thruster_particles = [p for p in self.thruster_particles if p.life > 0]
        
        # Create new thruster particles if thrusting
        if self.is_thrusting and pygame.time.get_ticks() - self.thruster_timer > 30:  # Throttle particle creation
            self.thruster_timer = pygame.time.get_ticks()
            self.create_thruster_particles() 