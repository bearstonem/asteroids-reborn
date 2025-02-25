import pygame
import math

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
        
        # New power-up states
        self.multishot = False
        self.multishot_timer = 0
        self.time_slow = False
        self.time_slow_timer = 0
        self.magnet = False
        self.magnet_timer = 0
        self.explosion_ammo = 0
        
        self.shoot_cooldown = 0
        
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
        # Apply time slow effect
        if self.time_slow:
            dt *= 0.5  # Slow down time by half
        
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
        
        # Update timers
        if self.invulnerable:
            self.invulnerable_timer -= dt
            if self.invulnerable_timer <= 0:
                self.invulnerable = False
        
        if self.rapid_fire:
            self.rapid_fire_timer -= dt
            if self.rapid_fire_timer <= 0:
                self.rapid_fire = False
        
        # Update new power-up timers
        if self.multishot:
            self.multishot_timer -= dt
            if self.multishot_timer <= 0:
                self.multishot = False
        
        if self.time_slow:
            # Use real dt here, not the modified one
            self.time_slow_timer -= dt * 2  # Time passes at normal rate for the timer
            if self.time_slow_timer <= 0:
                self.time_slow = False
        
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
    
    def render(self, surface):
        """Render the player ship"""
        # Don't render if off screen
        if (self.x < -50 or self.x > surface.get_width() + 50 or
            self.y < -50 or self.y > surface.get_height() + 50):
            return
        
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
        
        # Draw time slow effect
        if self.time_slow:
            # Purple time slow aura
            time_slow_color = (180, 100, 255, 60)  # Purple, very transparent
            # Create pulsing effect
            pulse = (pygame.time.get_ticks() % 1000) / 1000.0
            pulse_size = 5 + pulse * 5
            pygame.draw.circle(
                surface, 
                time_slow_color, 
                (int(self.x), int(self.y)), 
                int(self.radius + pulse_size),
                1  # Thin line
            )
        
        # Draw magnet effect
        if self.magnet:
            # Yellow magnet aura
            magnet_color = (255, 255, 100, 80)  # Yellow, transparent
            # Create rippling effect
            ripple = (pygame.time.get_ticks() % 500) / 500.0
            for i in range(3):
                ripple_offset = (ripple + i/3) % 1.0
                ripple_radius = self.radius + 10 + ripple_offset * 20
                pygame.draw.circle(
                    surface, 
                    magnet_color, 
                    (int(self.x), int(self.y)), 
                    int(ripple_radius),
                    1  # Thin line
                )
        
        # Draw multishot indicator
        if self.multishot:
            # Draw small indicators around the ship showing multishot is active
            ms_color = (255, 100, 150)  # Pink
            # Draw three small dots at the front of the ship
            dot_distance = self.radius + 5
            for i in range(3):
                angle_offset = -0.3 + i * 0.3
                dot_x = self.x + math.cos(angle_rad + angle_offset) * dot_distance
                dot_y = self.y + math.sin(angle_rad + angle_offset) * dot_distance
                pygame.draw.circle(
                    surface,
                    ms_color,
                    (int(dot_x), int(dot_y)),
                    2
                )
        
        # Draw the ship body
        pygame.draw.polygon(surface, ship_color, points)
        
        # Draw engine thrust if the ship is thrusting
        if self.is_thrusting:
            # Engine position (behind the ship)
            engine_angle = angle_rad + math.pi  # Opposite direction of ship heading
            
            # Create flame effect with random length
            flame_length = 10 + (pygame.time.get_ticks() % 6)  # Fluctuating flame
            
            flame_points = [
                # Center of back
                (self.x + math.cos(angle_rad + math.pi) * 5, 
                 self.y + math.sin(angle_rad + math.pi) * 5),
                
                # Right edge of flame
                (self.x + math.cos(engine_angle + 0.3) * flame_length, 
                 self.y + math.sin(engine_angle + 0.3) * flame_length),
                
                # Tip of flame
                (self.x + math.cos(engine_angle) * (flame_length + 5), 
                 self.y + math.sin(engine_angle) * (flame_length + 5)),
                
                # Left edge of flame
                (self.x + math.cos(engine_angle - 0.3) * flame_length, 
                 self.y + math.sin(engine_angle - 0.3) * flame_length),
            ]
            
            # Draw the flame with a yellow-orange color
            flame_color = (255, 150, 50)
            pygame.draw.polygon(surface, flame_color, flame_points)
        
        # Draw explosion ammo indicator if player has explosion shots
        if self.explosion_ammo > 0:
            # Draw small explosion indicators at the bottom of the screen
            exp_color = (255, 50, 50)  # Red
            text_surface = pygame.font.Font(None, 24).render(
                f"Bombs: {self.explosion_ammo}", True, exp_color
            )
            surface.blit(
                text_surface, 
                (self.x - text_surface.get_width() // 2, self.y + self.radius + 10)
            ) 