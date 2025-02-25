import pygame
import random
import math
from game.states.base_state import BaseState
from game.entities.player import Player
from game.entities.asteroid import Asteroid
from game.entities.projectile import Projectile
from game.entities.particle import Particle
from game.entities.powerup import Powerup
from game.entities.enemy import Enemy
from game.utils.collision import check_collision

class GameplayState(BaseState):
    """
    Main gameplay state for Asteroids Reborn
    """
    def __init__(self, game_state):
        super().__init__(game_state)
        self.ui_font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Initialize star field
        self.stars = []
        self.initialize_stars(300)  # Increased number of stars
        
        self.initialize_game()
    
    def initialize_game(self):
        """Initialize or reset the game to starting state"""
        # Get screen dimensions
        self.screen_width = pygame.display.get_surface().get_width()
        self.screen_height = pygame.display.get_surface().get_height()
        
        # Initialize game entities
        self.player = Player(self.screen_width // 2, self.screen_height // 2)
        self.asteroids = []
        self.projectiles = []
        self.particles = []
        self.powerups = []
        self.enemy = Enemy(100, 100)  # Initialize enemy at a different position than player
        
        # Game state variables
        self.score = 0
        self.level = 1
        self.game_over = False
        self.level_cleared = False
        self.level_start_timer = 2.0  # Give player some time before asteroids appear
        
        # Reinitialize star field with new random stars
        self.initialize_stars(300)
        
        # Powerup spawn timer
        self.powerup_spawn_timer = random.uniform(5.0, 10.0)  # First random powerup in 5-10 seconds
        
        # UI elements
        self.game_over_font = pygame.font.Font(None, 72)
        
        # Initialize the first level
        self.start_new_level()
    
    def initialize_stars(self, num_stars):
        """Create a starfield of persistent stars with varied properties"""
        self.stars = []
        screen_width = pygame.display.get_surface().get_width()
        screen_height = pygame.display.get_surface().get_height()
        
        for _ in range(num_stars):
            # Create stars with varying properties
            star = {
                'x': random.randint(0, screen_width),
                'y': random.randint(0, screen_height),
                'size': random.randint(1, 3),  # Varying star sizes (1-3 pixels)
                'brightness': random.randint(150, 255),  # Varying brightness
                'flicker_speed': random.uniform(0.5, 2.0),  # How fast it flickers
                'flicker_offset': random.uniform(0, 6.28),  # Random phase offset
                'flicker_amount': random.uniform(0.0, 0.5)  # How much it flickers (0-0.5)
            }
            self.stars.append(star)
    
    def start_new_level(self):
        """Set up the next level"""
        self.level_cleared = False
        self.level_start_timer = 2.0
        
        # Reinitialize star field with new random stars
        self.initialize_stars(300)
        
        # Play random background music for this level
        self.game_state.sound_manager.play_random_music()
        
        # Generate asteroids for this level
        num_asteroids = 3 + (self.level // 2)  # Increasing difficulty
        
        # Avoid spawning asteroids too close to the player
        for _ in range(num_asteroids):
            while True:
                # Get a random position
                x = random.randint(0, self.screen_width)
                y = random.randint(0, self.screen_height)
                
                # Make sure it's not too close to the player
                player_pos = pygame.math.Vector2(self.player.x, self.player.y)
                asteroid_pos = pygame.math.Vector2(x, y)
                if (asteroid_pos - player_pos).length() > 200:  # Safe distance
                    break
            
            size = random.choice(["large", "medium"])
            asteroid_type = random.choice(["normal", "ice", "mineral", "unstable"])
            
            # Calculate velocity based on level (higher levels = faster asteroids)
            speed_factor = 1.0 + (self.level * 0.1)
            vel_x = random.uniform(-1, 1) * speed_factor
            vel_y = random.uniform(-1, 1) * speed_factor
            
            self.asteroids.append(
                Asteroid(x, y, vel_x, vel_y, size, asteroid_type)
            )
    
    def handle_event(self, event):
        """Handle input events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Return to main menu/title screen when ESC is pressed
                # Fade out any game music that might be playing
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.fadeout(1000)
                # Change to menu state using runtime import to avoid circular dependency
                from game.states.menu_state import MenuState
                # Save the current gameplay state in the game_state for potential resume
                self.game_state.paused_gameplay_state = self
                # Create a new menu state with resume_available=True
                self.game_state.change_state(MenuState(self.game_state, resume_available=True))
            elif event.key == pygame.K_r and self.game_over:
                self.initialize_game()  # Restart the game
        
        # Pass events to player if game is active
        if not self.game_over:
            self.player.handle_event(event)
    
    def update(self, dt):
        """Update game state"""
        # Apply time slow effect if active
        effective_dt = dt
        if self.player and self.player.time_slow:
            effective_dt = dt * 0.167  # Slowed to 1/6 speed (3x more powerful than before) when time slow is active
        else:
            effective_dt = dt
        
        if self.game_over:
            # Only update particles when game over
            for particle in self.particles[:]:
                particle.update(dt)
                if particle.life <= 0:
                    self.particles.remove(particle)
            return
        
        # Update level start timer
        if self.level_start_timer > 0:
            self.level_start_timer -= dt
            if self.level_start_timer <= 0:
                # Level has officially started, play level sound
                self.game_state.sound_manager.play("level_up")
        
        # Update random powerup spawning timer
        if self.level_start_timer <= 0:  # Only spawn after level start
            self.powerup_spawn_timer -= dt
            if self.powerup_spawn_timer <= 0:
                # Reset timer with random interval based on level (more frequent in higher levels)
                base_time = max(15.0 - (self.level * 0.5), 5.0)  # Starts at ~15s in level 1, decreases to minimum of 5s
                self.powerup_spawn_timer = random.uniform(base_time * 0.7, base_time * 1.3)  # Some randomness
                
                # Spawn a random powerup at a random location away from the player
                self.spawn_random_powerup()
        
        # Update player
        self.player.update(dt, self.game_state.sound_manager)
        
        # Update power-up timers
        if self.player.invulnerable and self.player.invulnerable_timer > 0:
            self.player.invulnerable_timer -= dt
            if self.player.invulnerable_timer <= 0:
                self.player.invulnerable = False
        
        if self.player.rapid_fire and self.player.rapid_fire_timer > 0:
            self.player.rapid_fire_timer -= dt
            if self.player.rapid_fire_timer <= 0:
                self.player.rapid_fire = False
                
        if self.player.time_slow and self.player.time_slow_timer > 0:
            self.player.time_slow_timer -= dt
            if self.player.time_slow_timer <= 0:
                self.player.time_slow = False
                
        if self.player.triple_shot and self.player.triple_shot_timer > 0:
            self.player.triple_shot_timer -= dt
            if self.player.triple_shot_timer <= 0:
                self.player.triple_shot = False
                
        if self.player.magnet and self.player.magnet_timer > 0:
            self.player.magnet_timer -= dt
            if self.player.magnet_timer <= 0:
                self.player.magnet = False
        
        # Wrap player position around screen edges
        if self.player.x < 0:
            self.player.x = self.screen_width
        elif self.player.x > self.screen_width:
            self.player.x = 0
        if self.player.y < 0:
            self.player.y = self.screen_height
        elif self.player.y > self.screen_height:
            self.player.y = 0
        
        # Handle player shooting
        if self.player.is_shooting and self.player.shoot_cooldown <= 0:
            # Reset cooldown based on rapid fire status
            if self.player.rapid_fire:
                self.player.shoot_cooldown = 0.1  # Faster fire rate with powerup
            else:
                self.player.shoot_cooldown = 0.2  # Normal fire rate
            
            # Spawn projectile
            angle_rad = math.radians(self.player.rotation)
            
            # Create projectile velocity based on ship direction
            proj_speed = 400  # Projectile speed
            vel_x = math.cos(angle_rad) * proj_speed
            vel_y = math.sin(angle_rad) * proj_speed
            
            # Add some of the ship velocity to the projectile
            vel_x += self.player.vel_x * 0.5
            vel_y += self.player.vel_y * 0.5
            
            # Calculate projectile spawn position (in front of the ship)
            spawn_distance = self.player.radius + 5
            spawn_x = self.player.x + math.cos(angle_rad) * spawn_distance
            spawn_y = self.player.y + math.sin(angle_rad) * spawn_distance
            
            # Create and add the projectile
            self.projectiles.append(
                Projectile(spawn_x, spawn_y, vel_x, vel_y)
            )
            
            # Create additional projectiles if triple shot is active
            if self.player.triple_shot:
                # Left projectile (20 degrees offset)
                left_angle = angle_rad - math.radians(20)
                left_vel_x = math.cos(left_angle) * proj_speed + self.player.vel_x * 0.5
                left_vel_y = math.sin(left_angle) * proj_speed + self.player.vel_y * 0.5
                self.projectiles.append(
                    Projectile(spawn_x, spawn_y, left_vel_x, left_vel_y)
                )
                
                # Right projectile (20 degrees offset)
                right_angle = angle_rad + math.radians(20)
                right_vel_x = math.cos(right_angle) * proj_speed + self.player.vel_x * 0.5
                right_vel_y = math.sin(right_angle) * proj_speed + self.player.vel_y * 0.5
                self.projectiles.append(
                    Projectile(spawn_x, spawn_y, right_vel_x, right_vel_y)
                )
            
            # Play shooting sound
            self.game_state.sound_manager.play("player_shoot")
        
        # Update enemy
        if self.enemy.active:
            should_fire = self.enemy.update(effective_dt, self.player.x, self.player.y, 
                                            self.screen_width, self.screen_height,
                                            self.game_state.sound_manager,
                                            self.asteroids)
            
            # Handle enemy shooting
            if should_fire:
                # Calculate projectile position based on enemy position and rotation
                angle_rad = math.radians(self.enemy.rotation)
                start_distance = self.enemy.radius + 5
                
                start_x = self.enemy.x + math.cos(angle_rad) * start_distance
                start_y = self.enemy.y + math.sin(angle_rad) * start_distance
                
                # Create the projectile - slightly slower than player projectiles
                projectile = Projectile(
                    start_x, start_y,
                    math.cos(angle_rad) * 300,  # X velocity
                    math.sin(angle_rad) * 300   # Y velocity
                )
                self.projectiles.append(projectile)
            
            # Check collision between player and enemy
            if not self.player.invulnerable and check_collision(self.player, self.enemy):
                self.player_destroyed()
        else:
            # Update respawn timer when inactive
            self.enemy.update(effective_dt, self.player.x, self.player.y, 
                              self.screen_width, self.screen_height)
        
        # Update asteroids with potential time slow effect
        for asteroid in self.asteroids[:]:
            asteroid.update(effective_dt)
            
            # Wrap asteroid position around screen edges
            if asteroid.x < -50:
                asteroid.x = self.screen_width + 50
            elif asteroid.x > self.screen_width + 50:
                asteroid.x = -50
            if asteroid.y < -50:
                asteroid.y = self.screen_height + 50
            elif asteroid.y > self.screen_height + 50:
                asteroid.y = -50
            
            # Check collision with player
            if not self.player.invulnerable and check_collision(self.player, asteroid):
                self.player_destroyed()
                break
            
            # Check collision with enemy ship
            if self.enemy.active and check_collision(self.enemy, asteroid):
                enemy_destroyed = self.enemy.take_damage()
                
                # Create hit particles
                for _ in range(8):
                    vel_x = random.uniform(-50, 50)
                    vel_y = random.uniform(-50, 50)
                    self.particles.append(
                        Particle(
                            self.enemy.x, self.enemy.y,
                            vel_x, vel_y,
                            random.uniform(0.3, 0.8),
                            (255, 100, 50)
                        )
                    )
                
                # If enemy was destroyed, create more particles for explosion
                if enemy_destroyed:
                    self.game_state.sound_manager.play("explosion")
                    self.score += 250  # Slightly less score than when player destroys enemy
                    
                    # Create explosion effect
                    for _ in range(20):
                        vel_x = random.uniform(-100, 100)
                        vel_y = random.uniform(-100, 100)
                        self.particles.append(
                            Particle(
                                self.enemy.x, self.enemy.y,
                                vel_x, vel_y,
                                random.uniform(0.5, 1.5),
                                (255, 50, 50)
                            )
                        )
                else:
                    # Just play a hit sound if not destroyed
                    self.game_state.sound_manager.play("hit")
                
                # Don't destroy the asteroid when it hits the enemy
                # This makes the game more challenging and realistic
                # If you want to destroy the asteroid too, you could add code here to do that
                
                break  # Break out of asteroid loop after collision
        
        # Update projectiles
        for projectile in self.projectiles[:]:
            projectile.update(effective_dt)
            
            # Wrap projectiles around screen edges instead of removing them
            if projectile.x < 0:
                projectile.x = self.screen_width
            elif projectile.x > self.screen_width:
                projectile.x = 0
            if projectile.y < 0:
                projectile.y = self.screen_height
            elif projectile.y > self.screen_height:
                projectile.y = 0
            
            # Remove projectile if its lifetime is over
            if projectile.life <= 0:
                self.projectiles.remove(projectile)
                continue
            
            # Check collision with player (so player can take damage from projectiles)
            if not self.player.invulnerable and check_collision(projectile, self.player):
                self.player_destroyed()
                if projectile in self.projectiles:
                    self.projectiles.remove(projectile)
                break
            
            # Check collision with enemy
            if self.enemy.active and check_collision(projectile, self.enemy):
                # Check if the projectile originated from the player
                # For simplicity, we'll just check if the projectile is moving in roughly 
                # the same direction as the player's rotation
                player_angle_rad = math.radians(self.player.rotation)
                projectile_angle_rad = math.atan2(projectile.vel_y, projectile.vel_x)
                angle_diff = abs(player_angle_rad - projectile_angle_rad)
                
                # If angle difference is small, consider it a player projectile
                if angle_diff < 0.5 or angle_diff > math.pi * 2 - 0.5:
                    enemy_destroyed = self.enemy.take_damage()
                    
                    # Create hit particles
                    for _ in range(5):
                        vel_x = random.uniform(-50, 50)
                        vel_y = random.uniform(-50, 50)
                        self.particles.append(
                            Particle(
                                self.enemy.x, self.enemy.y,
                                vel_x, vel_y,
                                random.uniform(0.3, 0.8),
                                (255, 100, 50)
                            )
                        )
                    
                    # If enemy was destroyed, create more particles for explosion
                    if enemy_destroyed:
                        self.game_state.sound_manager.play("explosion")
                        self.score += 500  # Score for destroying enemy
                        
                        # Create explosion effect
                        for _ in range(20):
                            vel_x = random.uniform(-100, 100)
                            vel_y = random.uniform(-100, 100)
                            self.particles.append(
                                Particle(
                                    self.enemy.x, self.enemy.y,
                                    vel_x, vel_y,
                                    random.uniform(0.5, 1.5),
                                    (255, 50, 50)
                                )
                            )
                    else:
                        # Just play a hit sound if not destroyed
                        self.game_state.sound_manager.play("hit")
                
                # Remove the projectile regardless
                if projectile in self.projectiles:
                    self.projectiles.remove(projectile)
                break
            
            # Check collision with asteroids
            for asteroid in self.asteroids[:]:
                if check_collision(projectile, asteroid):
                    self.handle_asteroid_hit(asteroid, projectile)
                    if projectile in self.projectiles:  # It might have been removed already
                        self.projectiles.remove(projectile)
                    break
        
        # Update particles
        for particle in self.particles[:]:
            particle.update(dt)
            if particle.life <= 0:
                self.particles.remove(particle)
        
        # Update powerups
        for powerup in self.powerups[:]:
            powerup.update(dt)
            
            # Wrap powerup around screen edges
            if powerup.x < -20:
                powerup.x = self.screen_width + 20
            elif powerup.x > self.screen_width + 20:
                powerup.x = -20
            if powerup.y < -20:
                powerup.y = self.screen_height + 20
            elif powerup.y > self.screen_height + 20:
                powerup.y = -20
            
            # Check collision with player
            if check_collision(self.player, powerup):
                self.handle_powerup_collected(powerup)
                self.powerups.remove(powerup)
                continue
            
            # Remove if expired
            if powerup.life <= 0:
                self.powerups.remove(powerup)
        
        # Check if level cleared
        if len(self.asteroids) == 0 and not self.level_cleared:
            self.level_cleared = True
            self.level += 1
            self.start_new_level()
            
        # Apply magnet effect to powerups
        if self.player and self.player.magnet:
            for powerup in self.powerups[:]:
                # Calculate distance to player
                dx = self.player.x - powerup.x
                dy = self.player.y - powerup.y
                distance = math.sqrt(dx * dx + dy * dy)
                
                # If within magnet radius, pull toward player
                if distance < self.player.magnet_radius:
                    # Calculate attraction force (stronger when closer)
                    force = (1.0 - distance / self.player.magnet_radius) * 12.0  # Increased from 5.0 to 12.0 for stronger attraction
                    # Apply force to powerup velocity
                    powerup.vel_x += (dx / distance) * force
                    powerup.vel_y += (dy / distance) * force
    
    def handle_asteroid_hit(self, asteroid, projectile):
        """Handle an asteroid being hit by a projectile"""
        # Remove the asteroid
        self.asteroids.remove(asteroid)
        
        # Play explosion sound
        self.game_state.sound_manager.play("explosion")
        
        # Add score based on size and type
        if asteroid.size == "large":
            self.score += 100
        elif asteroid.size == "medium":
            self.score += 150
        else:  # small
            self.score += 200
        
        # Extra score for special asteroid types
        if asteroid.type == "mineral":
            self.score += 50
        elif asteroid.type == "unstable":
            self.score += 75
        
        # Create particles for explosion effect with enhanced visuals
        # More particles for larger asteroids
        if asteroid.size == "large":
            num_particles = 40  # Increased from 15
        elif asteroid.size == "medium":
            num_particles = 30  # Increased from 10
        else:  # small
            num_particles = 20
            
        # Create primary explosion particles
        for _ in range(num_particles):
            # Create more dynamic velocities for particles
            speed = random.uniform(50, 200)  # Higher speed range
            angle = random.uniform(0, 2 * math.pi)
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed
            
            # Different colors based on asteroid type with more variation
            if asteroid.type == "normal":
                base_color = (150, 150, 150)
                # Add some variation to the colors
                color_variation = random.randint(-30, 30)
                color = (
                    max(0, min(255, base_color[0] + color_variation)),
                    max(0, min(255, base_color[1] + color_variation)),
                    max(0, min(255, base_color[2] + color_variation))
                )
            elif asteroid.type == "ice":
                # More vibrant ice colors
                blue = random.randint(200, 255)
                color = (random.randint(200, 240), random.randint(200, 240), blue)
            elif asteroid.type == "mineral":
                # More vibrant mineral colors
                red = random.randint(180, 255)
                green = random.randint(120, 180)
                blue = random.randint(50, 100)
                color = (red, green, blue)
            else:  # unstable
                # More vibrant unstable colors with reds and oranges
                red = random.randint(220, 255)
                green = random.randint(50, 150)
                blue = random.randint(20, 50)
                color = (red, green, blue)
            
            # Create the particle with varied parameters
            # Determine if this particle has special effects
            has_glow = random.random() < 0.3  # 30% chance for glow
            has_trail = random.random() < 0.2  # 20% chance for trail
            
            # Pick a random shape with weights (circle most common)
            shapes = ["circle", "square", "triangle", "star"]
            shape_weights = [0.7, 0.1, 0.1, 0.1]
            shape = random.choices(shapes, weights=shape_weights)[0]
            
            # Pick a random fade mode
            fade_modes = ["normal", "pulse", "flicker"]
            fade_weights = [0.6, 0.2, 0.2]
            fade_mode = random.choices(fade_modes, weights=fade_weights)[0]
            
            # Determine if particle spins
            spins = random.random() < 0.4  # 40% chance to spin
            
            # Create particle with various visual effects
            self.particles.append(
                Particle(
                    asteroid.x, asteroid.y,
                    vel_x, vel_y,
                    random.uniform(0.7, 2.0),  # Longer lifetime
                    color,
                    size=random.uniform(2.0, 5.0),  # Larger particles
                    shape=shape,
                    trail=has_trail,
                    glow=has_glow,
                    fade_mode=fade_mode,
                    spin=spins
                )
            )
            
        # Add central explosion flash for larger asteroids
        if asteroid.size in ["large", "medium"]:
            # Central bright flash
            flash_color = (255, 255, 200) if asteroid.type != "unstable" else (255, 200, 100)
            self.particles.append(
                Particle(
                    asteroid.x, asteroid.y,
                    0, 0,  # No velocity
                    0.3,  # Short life
                    flash_color,
                    size=12.0 if asteroid.size == "large" else 8.0,
                    glow=True,
                    fade_mode="normal"
                )
            )
            
            # Shock wave particle (expanding ring)
            shock_size = 6.0 if asteroid.size == "large" else 4.0
            for _ in range(3):  # Create multiple rings with offsets
                self.particles.append(
                    Particle(
                        asteroid.x + random.uniform(-3, 3), 
                        asteroid.y + random.uniform(-3, 3),
                        0, 0,  # No velocity
                        0.6,   # Medium life
                        flash_color,
                        size=shock_size + random.uniform(-1, 1),
                        shape="circle",
                        glow=True,
                        fade_mode="pulse"
                    )
                )
        
        # Break larger asteroids into smaller ones
        if asteroid.size == "large":
            for _ in range(2):
                vel_x = random.uniform(-50, 50)
                vel_y = random.uniform(-50, 50)
                new_asteroid = Asteroid(
                    asteroid.x, asteroid.y,
                    vel_x, vel_y,
                    "medium", asteroid.type
                )
                self.asteroids.append(new_asteroid)
        elif asteroid.size == "medium":
            for _ in range(2):
                vel_x = random.uniform(-75, 75)
                vel_y = random.uniform(-75, 75)
                new_asteroid = Asteroid(
                    asteroid.x, asteroid.y,
                    vel_x, vel_y,
                    "small", asteroid.type
                )
                self.asteroids.append(new_asteroid)
        
        # Special effects based on asteroid type
        if asteroid.type == "unstable":
            # Create a larger explosion that damages nearby asteroids
            for nearby_asteroid in self.asteroids[:]:
                dx = nearby_asteroid.x - asteroid.x
                dy = nearby_asteroid.y - asteroid.y
                distance = math.sqrt(dx * dx + dy * dy)
                if distance < 100:  # Explosion radius
                    # Damage or destroy the nearby asteroid
                    self.asteroids.remove(nearby_asteroid)
                    
                    # Add more particles for chain reaction with intense effects
                    for _ in range(15):  # Increased from 5
                        speed = random.uniform(50, 200)
                        angle = random.uniform(0, 2 * math.pi)
                        vel_x = math.cos(angle) * speed
                        vel_y = math.sin(angle) * speed
                        
                        # Create spectacular chain reaction particles
                        self.particles.append(
                            Particle(
                                nearby_asteroid.x, nearby_asteroid.y,
                                vel_x, vel_y,
                                random.uniform(0.7, 1.5),
                                (255, random.randint(100, 200), random.randint(20, 80)),
                                size=random.uniform(2.0, 5.0),
                                shape=random.choice(["circle", "star"]),
                                trail=True,
                                glow=random.random() < 0.6,
                                fade_mode=random.choice(["normal", "flicker"]),
                                spin=random.random() < 0.5
                            )
                        )
                    
                    # Add a shockwave effect at each chain explosion
                    shock_color = (255, 180, 50)
                    self.particles.append(
                        Particle(
                            nearby_asteroid.x, nearby_asteroid.y,
                            0, 0,
                            0.5,
                            shock_color,
                            size=8.0,
                            shape="circle",
                            glow=True,
                            fade_mode="pulse"
                        )
                    )
            
            # Add an extra central explosion for unstable asteroids
            # This creates a more dramatic effect for the chain reaction
            for _ in range(5):
                pulse_size = random.uniform(8.0, 15.0)
                self.particles.append(
                    Particle(
                        asteroid.x, asteroid.y,
                        0, 0,
                        random.uniform(0.4, 0.8),
                        (255, random.randint(100, 200), random.randint(20, 80)),
                        size=pulse_size,
                        shape="circle",
                        glow=True,
                        fade_mode="pulse"
                    )
                )
        
        # Chance to spawn a powerup
        if random.random() < 0.2:  # 20% chance (increased from 10%)
            # Select a random powerup type with weights
            powerup_types = [
                "shield", 
                "rapidfire", 
                "extralife", 
                "timeslow", 
                "tripleshot", 
                "magnet"
            ]
            
            # Different weights for different powerups (rarer ones have lower chance)
            weights = [0.2, 0.2, 0.1, 0.2, 0.15, 0.15]
            
            powerup_type = random.choices(powerup_types, weights=weights)[0]
            
            # Create a powerup at the asteroid's position with some velocity
            self.powerups.append(
                Powerup(
                    asteroid.x, asteroid.y,
                    random.uniform(-50, 50), random.uniform(-50, 50),
                    powerup_type
                )
            )
            
            # Add a special effect for powerup spawning
            powerup_colors = {
                "shield": (100, 200, 255),
                "rapidfire": (255, 200, 100),
                "extralife": (100, 255, 100),
                "timeslow": (200, 100, 255),
                "tripleshot": (255, 100, 100),
                "magnet": (255, 255, 100)
            }
            
            color = powerup_colors.get(powerup_type, (255, 255, 255))
            
            # Create a burst of particles around the powerup
            for _ in range(15):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(20, 80)
                self.particles.append(
                    Particle(
                        asteroid.x, asteroid.y,
                        math.cos(angle) * speed,
                        math.sin(angle) * speed,
                        random.uniform(0.5, 1.2),
                        color,
                        size=random.uniform(1.5, 3.0),
                        shape="star" if random.random() < 0.3 else "circle",
                        glow=True,
                        fade_mode="pulse"
                    )
                )
    
    def handle_powerup_collected(self, powerup):
        """Handle player collecting a powerup"""
        # Play powerup sound
        self.game_state.sound_manager.play("powerup")
        
        # Create special particle effects when collecting a powerup
        powerup_colors = {
            "shield": (100, 200, 255),
            "rapidfire": (255, 200, 100),
            "extralife": (100, 255, 100),
            "timeslow": (200, 100, 255),
            "tripleshot": (255, 100, 100),
            "magnet": (255, 255, 100)
        }
        
        color = powerup_colors.get(powerup.powerup_type, (255, 255, 255))
        
        # Create particles spiraling outward from the player
        for i in range(40):  # Create 40 particles in a spiral pattern
            angle = i * (2 * math.pi / 20)  # Distribute around a circle
            distance = 5 + i * 0.5  # Increasing distance creates spiral
            
            start_x = self.player.x + math.cos(angle) * distance
            start_y = self.player.y + math.sin(angle) * distance
            
            speed = random.uniform(30, 100)
            
            self.particles.append(
                Particle(
                    start_x, start_y,
                    math.cos(angle) * speed,
                    math.sin(angle) * speed,
                    random.uniform(0.5, 1.5),
                    color,
                    size=random.uniform(2.0, 4.0),
                    shape=random.choice(["circle", "star"]) if random.random() < 0.7 else random.choice(["triangle", "square"]),
                    trail=random.random() < 0.3,
                    glow=True,
                    fade_mode="pulse" if random.random() < 0.7 else "flicker",
                    spin=random.random() < 0.5
                )
            )
        
        # Create a shockwave effect centered on the player
        for _ in range(3):
            ring_size = random.uniform(8, 12)
            self.particles.append(
                Particle(
                    self.player.x, self.player.y,
                    0, 0,
                    random.uniform(0.4, 0.8),
                    color,
                    size=ring_size,
                    shape="circle",
                    glow=True,
                    fade_mode="pulse"
                )
            )
        
        # Apply the powerup effect
        if powerup.powerup_type == "shield":
            self.player.invulnerable = True
            self.player.invulnerable_timer = 15.0  # 15 seconds of shield
        elif powerup.powerup_type == "rapidfire":
            self.player.rapid_fire = True
            self.player.rapid_fire_timer = 15.0  # 15 seconds of rapid fire
        elif powerup.powerup_type == "extralife":
            self.player.lives += 1
        elif powerup.powerup_type == "timeslow":
            self.player.time_slow = True
            self.player.time_slow_timer = 10.0  # 10 seconds of time slow
        elif powerup.powerup_type == "tripleshot":
            self.player.triple_shot = True
            self.player.triple_shot_timer = 15.0  # 15 seconds of triple shot
        elif powerup.powerup_type == "magnet":
            self.player.magnet = True
            self.player.magnet_timer = 18.0  # 18 seconds of magnet effect
    
    def player_destroyed(self):
        """Handle player being destroyed"""
        # Play explosion sound
        self.game_state.sound_manager.play("explosion")
        
        # Create enhanced explosion effect for player destruction
        # Main explosion flash
        self.particles.append(
            Particle(
                self.player.x, self.player.y,
                0, 0,
                0.5,
                (255, 255, 200),
                size=15.0,
                shape="circle",
                glow=True,
                fade_mode="normal"
            )
        )
        
        # Multiple shockwave rings
        for i in range(3):
            delay = i * 0.1  # Stagger the rings
            size = 10.0 + i * 4.0  # Increasing sizes
            self.particles.append(
                Particle(
                    self.player.x, self.player.y,
                    0, 0,
                    0.6 + delay,
                    (255, 200 - i * 30, 50),
                    size=size,
                    shape="circle",
                    glow=True,
                    fade_mode="pulse"
                )
            )
        
        # Main debris particles
        for _ in range(60):  # Increased from 20
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 250)
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed
            
            # Random colors for explosion - yellows, oranges, and reds
            r = random.randint(200, 255)
            g = random.randint(50, 200)
            b = random.randint(0, 50)
            
            # Create particle with varied parameters
            self.particles.append(
                Particle(
                    self.player.x, self.player.y,
                    vel_x, vel_y,
                    random.uniform(0.8, 2.0),
                    (r, g, b),
                    size=random.uniform(2.0, 5.0),
                    shape=random.choice(["circle", "triangle", "square", "star"]),
                    trail=random.random() < 0.4,
                    glow=random.random() < 0.6,
                    fade_mode=random.choice(["normal", "pulse", "flicker"]),
                    spin=random.random() < 0.7
                )
            )
        
        # Additional sparks that live longer
        for _ in range(30):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(20, 100)
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed
            
            self.particles.append(
                Particle(
                    self.player.x, self.player.y,
                    vel_x, vel_y,
                    random.uniform(1.5, 3.0),
                    (255, 255, random.randint(100, 200)),
                    size=random.uniform(1.0, 2.5),
                    shape="circle",
                    trail=True,
                    glow=True,
                    fade_mode="flicker",
                    spin=False
                )
            )
        
        # Reduce player lives
        self.player.lives -= 1
        
        if self.player.lives <= 0:
            self.game_over = True
            # Stop any background music
            self.game_state.sound_manager.stop_music()
            # Play game over sound
            self.game_state.sound_manager.play("game_over")
            
            # Add extra "game over" particle effects
            for _ in range(100):
                # Particles spread across the screen
                x = random.randint(0, self.screen_width)
                y = random.randint(0, self.screen_height)
                
                # Particles move toward center
                dx = self.screen_width // 2 - x
                dy = self.screen_height // 2 - y
                dist = math.sqrt(dx * dx + dy * dy)
                
                if dist > 0:
                    vel_x = dx / dist * random.uniform(20, 50)
                    vel_y = dy / dist * random.uniform(20, 50)
                else:
                    vel_x = random.uniform(-20, 20)
                    vel_y = random.uniform(-20, 20)
                
                # Red colors for game over
                r = random.randint(200, 255)
                g = random.randint(0, 100)
                b = random.randint(0, 50)
                
                self.particles.append(
                    Particle(
                        x, y,
                        vel_x, vel_y,
                        random.uniform(1.0, 5.0),
                        (r, g, b),
                        size=random.uniform(1.5, 4.0),
                        shape=random.choice(["circle", "square", "triangle", "star"]),
                        trail=random.random() < 0.3,
                        glow=random.random() < 0.5,
                        fade_mode=random.choice(["normal", "flicker"]),
                        spin=random.random() < 0.5
                    )
                )
        else:
            # Reset player position
            self.player.x = self.screen_width // 2
            self.player.y = self.screen_height // 2
            self.player.vel_x = 0
            self.player.vel_y = 0
            self.player.rotation = 0
            
            # Make player temporarily invulnerable
            self.player.invulnerable = True
            self.player.invulnerable_timer = 3.0
            
            # Add respawn effect
            for i in range(30):
                angle = i * (2 * math.pi / 30)  # Distribute in a circle
                speed = random.uniform(30, 80)
                
                self.particles.append(
                    Particle(
                        self.player.x, self.player.y,
                        math.cos(angle) * speed,
                        math.sin(angle) * speed,
                        random.uniform(0.5, 1.5),
                        (100, 200, 255),  # Blue for respawn
                        size=random.uniform(1.5, 3.5),
                        shape="circle",
                        trail=random.random() < 0.3,
                        glow=True,
                        fade_mode="pulse",
                        spin=False
                    )
                )
    
    def render(self, surface):
        """Render the game state"""
        # Clear the screen
        surface.fill((0, 0, 20))  # Dark blue background
        
        # Draw stars with varying brightness and subtle flicker effect
        current_time = pygame.time.get_ticks() / 1000  # Current time in seconds
        for star in self.stars:
            # Create subtle flicker effect using sine wave
            flicker = math.sin(current_time * star['flicker_speed'] + star['flicker_offset'])
            flicker_factor = 1.0 - (star['flicker_amount'] * flicker)
            
            # Calculate brightness with flicker effect
            brightness = int(star['brightness'] * flicker_factor)
            brightness = max(100, min(255, brightness))  # Clamp between 100-255 to avoid disappearing
            
            color = (brightness, brightness, min(255, brightness + 30))  # Slight blue tint
            
            # Draw larger stars as circles, tiny ones as pixels
            if star['size'] == 1:
                surface.set_at((star['x'], star['y']), color)
            else:
                pygame.draw.circle(surface, color, (star['x'], star['y']), star['size'] // 2)
        
        # Draw game entities
        for asteroid in self.asteroids:
            asteroid.render(surface)
        
        for projectile in self.projectiles:
            projectile.render(surface)
        
        for particle in self.particles:
            particle.render(surface)
        
        for powerup in self.powerups:
            powerup.render(surface)
        
        # Draw enemy
        self.enemy.render(surface)
        
        # Draw player if still alive
        if not self.game_over:
            self.player.render(surface)
        
        # Draw UI
        self.render_ui(surface)
    
    def render_ui(self, surface):
        """Render the user interface"""
        # Display score
        score_text = self.ui_font.render(f"Score: {self.score}", True, (255, 255, 255))
        surface.blit(score_text, (20, 20))
        
        # Display level
        level_text = self.ui_font.render(f"Level: {self.level}", True, (255, 255, 255))
        level_rect = level_text.get_rect()
        level_rect.midtop = (surface.get_width() // 2, 20)
        surface.blit(level_text, level_rect)
        
        # Display lives
        lives_text = self.ui_font.render(f"Lives: {self.player.lives}", True, (255, 255, 255))
        lives_rect = lives_text.get_rect()
        lives_rect.topright = (surface.get_width() - 20, 20)
        surface.blit(lives_text, lives_rect)
        
        # Display active power-ups
        y_offset = 60
        if self.player.invulnerable and self.player.invulnerable_timer > 0:
            shield_text = self.small_font.render(f"Shield: {self.player.invulnerable_timer:.1f}s", True, (100, 200, 255))
            surface.blit(shield_text, (20, y_offset))
            y_offset += 25
            
        if self.player.rapid_fire and self.player.rapid_fire_timer > 0:
            rapid_text = self.small_font.render(f"Rapid Fire: {self.player.rapid_fire_timer:.1f}s", True, (255, 200, 100))
            surface.blit(rapid_text, (20, y_offset))
            y_offset += 25
            
        if self.player.triple_shot and self.player.triple_shot_timer > 0:
            triple_text = self.small_font.render(f"Triple Shot: {self.player.triple_shot_timer:.1f}s", True, (255, 100, 100))
            surface.blit(triple_text, (20, y_offset))
            y_offset += 25
            
        if self.player.time_slow and self.player.time_slow_timer > 0:
            time_text = self.small_font.render(f"Time Slow: {self.player.time_slow_timer:.1f}s", True, (200, 100, 255))
            surface.blit(time_text, (20, y_offset))
            y_offset += 25
            
        if self.player.magnet and self.player.magnet_timer > 0:
            magnet_text = self.small_font.render(f"Magnet: {self.player.magnet_timer:.1f}s", True, (255, 255, 100))
            surface.blit(magnet_text, (20, y_offset))
        
        # Display level start message if needed
        if self.level_start_timer > 0:
            level_msg = self.ui_font.render(f"Level {self.level}", True, (255, 255, 0))
            level_msg_rect = level_msg.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2))
            surface.blit(level_msg, level_msg_rect)
        
        # Display game over message if needed
        if self.game_over:
            game_over_text = self.game_over_font.render("GAME OVER", True, (255, 50, 50))
            game_over_rect = game_over_text.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2))
            surface.blit(game_over_text, game_over_rect)
            
            restart_text = self.ui_font.render("Press R to Restart", True, (255, 255, 255))
            restart_rect = restart_text.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2 + 60))
            surface.blit(restart_text, restart_rect)
    
    def spawn_random_powerup(self):
        """Spawn a random powerup at a random location away from the player"""
        # Find a suitable random position (not too close to the player)
        while True:
            x = random.randint(50, self.screen_width - 50)
            y = random.randint(50, self.screen_height - 50)
            
            # Calculate distance to player
            dx = x - self.player.x
            dy = y - self.player.y
            distance = math.sqrt(dx * dx + dy * dy)
            
            # Make sure it's not too close to the player
            if distance > 150:  # Minimum safe distance
                break
        
        # Select a random powerup type with weights
        powerup_types = [
            "shield", 
            "rapidfire", 
            "extralife", 
            "timeslow", 
            "tripleshot", 
            "magnet"
        ]
        
        # Different weights for different powerups (rarer ones have lower chance)
        weights = [0.2, 0.2, 0.1, 0.2, 0.15, 0.15]
        
        powerup_type = random.choices(powerup_types, weights=weights)[0]
        
        # Random velocity for interesting movement
        # Higher speed for more challenging collection
        speed = random.uniform(30, 80)
        angle = random.uniform(0, 2 * math.pi)  # Random direction
        vel_x = math.cos(angle) * speed
        vel_y = math.sin(angle) * speed
        
        # Create and add the powerup
        self.powerups.append(
            Powerup(x, y, vel_x, vel_y, powerup_type)
        )
        
        # Optional: Play a subtle sound to indicate a powerup has spawned
        if hasattr(self.game_state, 'sound_manager'):
            self.game_state.sound_manager.play("powerup_spawn") 