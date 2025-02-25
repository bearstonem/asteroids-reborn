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
            
            # Color ranges from yellow (slow) to blue/white (fast)
            if random.random() < 0.7:  # 70% are main flame color
                r = int(255 * (1.0 - intensity * 0.5))
                g = int(200 * (1.0 - intensity * 0.2))
                b = int(100 + 155 * intensity)
                color = (r, g, b)
            else:  # 30% are brighter core
                color = (255, 255, random.randint(180, 255))
            
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
        # Don't render if off screen
        if (self.x < -50 or self.x > surface.get_width() + 50 or
            self.y < -50 or self.y > surface.get_height() + 50):
            return
        
        # Draw thruster particles first (behind the ship)
        for particle in self.thruster_particles:
            particle.render(surface)
        
        # Skip some frames if invulnerable to create blinking effect
        if self.invulnerable and pygame.time.get_ticks() % 200 < 100:
            return
        
        # Calculate ship vertices based on current rotation
        angle_rad = math.radians(self.rotation)
        
        # Ship design: triangle with a small tail
        points = [
            # Nose of the ship
            (self.x + math.cos(angle_rad) * 20, 
             self.y + math.sin(angle_rad) * 20),
            
            # Right wing
            (self.x + math.cos(angle_rad + 2.6) * 15, 
             self.y + math.sin(angle_rad + 2.6) * 15),
            
            # Tail indent
            (self.x + math.cos(angle_rad + math.pi) * 5, 
             self.y + math.sin(angle_rad + math.pi) * 5),
            
            # Left wing
            (self.x + math.cos(angle_rad - 2.6) * 15, 
             self.y + math.sin(angle_rad - 2.6) * 15),
        ]
        
        # Draw the ship
        ship_color = (50, 150, 255)  # Blue ship
        
        # Draw active thruster flame if thrusting (visible from the outside)
        if self.is_thrusting:
            # Calculate thruster position
            back_angle = angle_rad + math.pi
            thruster_x = self.x + math.cos(back_angle) * 12
            thruster_y = self.y + math.sin(back_angle) * 12
            
            # Draw flame (triangle shape)
            flame_length = 10 + random.uniform(-2, 2)  # Flickering effect
            flame_width = 6 + random.uniform(-1, 1)
            
            flame_points = [
                (thruster_x, thruster_y),
                (thruster_x + math.cos(back_angle + 0.3) * flame_width, 
                 thruster_y + math.sin(back_angle + 0.3) * flame_width),
                (thruster_x + math.cos(back_angle) * flame_length, 
                 thruster_y + math.sin(back_angle) * flame_length),
                (thruster_x + math.cos(back_angle - 0.3) * flame_width, 
                 thruster_y + math.sin(back_angle - 0.3) * flame_width),
            ]
            
            # Flame color changes over time for flickering effect
            flicker = (pygame.time.get_ticks() % 100) / 100.0
            flame_color = (255, 200 + int(55 * flicker), 0)
            
            pygame.draw.polygon(surface, flame_color, flame_points)
            
            # Inner flame (brighter)
            inner_flame_length = flame_length * 0.7
            inner_flame_width = flame_width * 0.5
            
            inner_flame_points = [
                (thruster_x, thruster_y),
                (thruster_x + math.cos(back_angle + 0.2) * inner_flame_width, 
                 thruster_y + math.sin(back_angle + 0.2) * inner_flame_width),
                (thruster_x + math.cos(back_angle) * inner_flame_length, 
                 thruster_y + math.sin(back_angle) * inner_flame_length),
                (thruster_x + math.cos(back_angle - 0.2) * inner_flame_width, 
                 thruster_y + math.sin(back_angle - 0.2) * inner_flame_width),
            ]
            
            inner_flame_color = (255, 255, 200)
            pygame.draw.polygon(surface, inner_flame_color, inner_flame_points)
        
        # Draw shield if invulnerable
        if self.invulnerable:
            shield_color = (100, 200, 255, 100)  # Light blue, semi-transparent
            pygame.draw.circle(
                surface, 
                shield_color, 
                (int(self.x), int(self.y)), 
                int(self.radius + 5),
                2  # Shield thickness
            )
        
        # Draw magnet field if active
        if self.magnet:
            magnet_color = (255, 255, 100, 30)  # Yellow, very transparent
            magnet_surface = pygame.Surface((self.magnet_radius * 2, self.magnet_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                magnet_surface,
                magnet_color,
                (int(self.magnet_radius), int(self.magnet_radius)),
                int(self.magnet_radius)
            )
            # Add pulsing effect
            pulse = (pygame.time.get_ticks() % 1000) / 1000.0
            pulse_radius = int(self.magnet_radius * (0.8 + 0.2 * pulse))
            pygame.draw.circle(
                magnet_surface,
                (255, 255, 100, 20),
                (int(self.magnet_radius), int(self.magnet_radius)),
                pulse_radius,
                3
            )
            surface.blit(
                magnet_surface,
                (int(self.x - self.magnet_radius), int(self.y - self.magnet_radius))
            )
        
        # Draw time slow effect if active
        if self.time_slow:
            # Add a subtle time slow indicator (clock hands)
            time_color = (200, 100, 255, 150)
            # Draw clock hands that move slowly
            angle = (pygame.time.get_ticks() / 2000.0) % (2 * math.pi)
            # Hour hand
            hour_length = self.radius * 0.6
            hour_x = self.x + math.cos(angle) * hour_length
            hour_y = self.y + math.sin(angle) * hour_length
            pygame.draw.line(
                surface,
                time_color,
                (int(self.x), int(self.y)),
                (int(hour_x), int(hour_y)),
                2
            )
            # Minute hand
            minute_length = self.radius * 0.8
            minute_x = self.x + math.cos(angle * 12) * minute_length
            minute_y = self.y + math.sin(angle * 12) * minute_length
            pygame.draw.line(
                surface,
                time_color,
                (int(self.x), int(self.y)),
                (int(minute_x), int(minute_y)),
                1
            )
        
        # Draw the ship body
        pygame.draw.polygon(surface, ship_color, points)
        
        # Draw a hull glow effect for the ship
        if random.random() < 0.2:  # Occasional subtle glow
            glow_points = []
            for point in points:
                # Add slight randomization to glow points
                glow_points.append((
                    point[0] + random.uniform(-1, 1),
                    point[1] + random.uniform(-1, 1)
                ))
            pygame.draw.polygon(surface, (100, 180, 255, 50), glow_points, 2) 