import pygame
import math
import random

class Enemy:
    """
    Enemy spaceship entity for Asteroids Reborn
    AI-controlled adversary that hunts the player with enhanced intelligence
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vel_x = 0
        self.vel_y = 0
        self.rotation = 0  # Angle in degrees
        self.radius = 20  # For collision detection
        
        # Enemy state
        self.health = 4  # Increased health from 3 to 4 to make it tougher
        self.shoot_cooldown = 0
        self.acceleration = 0
        self.active = True
        self.respawn_timer = 0
        
        # AI behavior variables
        self.target_x = 0
        self.target_y = 0
        self.behavior_timer = 0
        self.behavior_state = "seek"  # States: seek, attack, evade, ambush, flank
        self.last_player_pos = None  # Last known position of player
        self.last_detection_time = 0
        self.avoiding_asteroid = False
        self.avoidance_direction = 0
        self.avoidance_timer = 0
        self.prediction_factor = 0.8  # How much to predict player movement (0-1)
        self.flanking_direction = random.choice([-1, 1])  # Direction to flank player
        self.burst_fire_count = 0  # For burst fire mode
        self.burst_fire_cooldown = 0  # Cooldown between bursts
        self.burst_fire_delay = 0  # Delay between shots in a burst
        self.shot_accuracy = random.uniform(0.85, 0.97)  # Accuracy of shots (85-97%)
        
        # Enemy characteristics
        self.rotation_speed = 160  # degrees per second (increased from 130)
        self.thrust_strength = 180  # acceleration (increased from 150)
        self.max_velocity = 280  # Max speed (increased from 250)
        self.shoot_rate = 0.9  # Seconds between shots (reduced from 1.2)
        self.detection_range = 500  # How far the enemy can "see" the player (increased from 400)
        self.asteroid_detection_range = 180  # How far the enemy can detect asteroids (increased from 150)
        self.friction = 0.9999  # velocity damping
        self.burst_mode = False  # Whether enemy is in burst fire mode
        
        # Strategy variables
        self.strategy_change_timer = random.uniform(8.0, 15.0)  # Time until strategy change
        self.aim_predict_time = 0.5  # How far ahead to aim (in seconds)
    
    def update(self, dt, player_x, player_y, screen_width, screen_height, sound_manager=None, asteroids=None):
        """Update enemy state and AI behavior"""
        if not self.active:
            # If inactive, update respawn timer
            self.respawn_timer -= dt
            if self.respawn_timer <= 0:
                self.respawn(screen_width, screen_height, player_x, player_y)
            return False
        
        # Track previous acceleration state for sound effects
        previous_acceleration = self.acceleration > 0.3
        
        # Update strategy timer
        self.strategy_change_timer -= dt
        if self.strategy_change_timer <= 0:
            # Change firing mode and other strategies periodically
            self.burst_mode = not self.burst_mode
            self.flanking_direction = random.choice([-1, 1])
            self.prediction_factor = random.uniform(0.6, 1.0)
            self.aim_predict_time = random.uniform(0.3, 0.8)
            self.strategy_change_timer = random.uniform(8.0, 15.0)
        
        # Update avoidance timer
        if self.avoiding_asteroid:
            self.avoidance_timer -= dt
            if self.avoidance_timer <= 0:
                self.avoiding_asteroid = False
        
        # Update burst fire cooldowns
        if self.burst_fire_delay > 0:
            self.burst_fire_delay -= dt
        if self.burst_fire_cooldown > 0:
            self.burst_fire_cooldown -= dt
        
        # Check for nearby asteroids and try to avoid them
        if asteroids and not self.avoiding_asteroid:
            closest_asteroid = None
            closest_distance = self.asteroid_detection_range
            
            for asteroid in asteroids:
                dx = asteroid.x - self.x
                dy = asteroid.y - self.y
                distance = math.sqrt(dx * dx + dy * dy)
                
                # Consider asteroids on collision course
                if distance < closest_distance:
                    # Calculate if asteroid is moving towards the enemy
                    # (rough approximation by checking if distance will decrease)
                    next_dx = asteroid.x + asteroid.vel_x * dt - self.x - self.vel_x * dt
                    next_dy = asteroid.y + asteroid.vel_y * dt - self.y - self.vel_y * dt
                    next_distance = math.sqrt(next_dx * next_dx + next_dy * next_dy)
                    
                    if next_distance < distance:
                        closest_asteroid = asteroid
                        closest_distance = distance
            
            # If there's a dangerous asteroid nearby, avoid it
            if closest_asteroid:
                self.start_asteroid_avoidance(closest_asteroid)
        
        # Update AI behavior timer
        self.behavior_timer -= dt
        if self.behavior_timer <= 0 and not self.avoiding_asteroid:
            self.update_behavior_state(player_x, player_y)
            self.behavior_timer = random.uniform(1.0, 2.5)  # Shorter timer for quicker reactions
        
        # Calculate distance to player
        dx = player_x - self.x
        dy = player_y - self.y
        distance_to_player = math.sqrt(dx * dx + dy * dy)
        
        # Update the AI behavior based on current state
        if self.avoiding_asteroid:
            # When avoiding an asteroid, rotate in the avoidance direction and apply thrust
            self.rotation += self.avoidance_direction * self.rotation_speed * dt
            self.acceleration = 1.0  # Full thrust to avoid
        elif distance_to_player < self.detection_range:
            # Player is in detection range, update last known position
            self.last_player_pos = (player_x, player_y)
            self.last_detection_time = 0
            
            # Execute behavior based on current state
            if self.behavior_state in ["seek", "attack", "ambush", "flank"]:
                # Target position with prediction based on player velocity and distance
                target_x = player_x
                target_y = player_y
                
                # Try to predict player movement based on their current position
                # This is a simple prediction; we'll use estimated velocity instead of actual player velocity
                if self.behavior_state != "ambush" and self.last_player_pos is not None:
                    # Estimate player velocity from last known position
                    time_since_last_pos = self.behavior_timer  # Use behavior timer as time estimate
                    if time_since_last_pos > 0:
                        last_x, last_y = self.last_player_pos
                        est_vel_x = (player_x - last_x) / time_since_last_pos
                        est_vel_y = (player_y - last_y) / time_since_last_pos
                        
                        # Predict where the player will be
                        prediction_time = self.aim_predict_time * self.prediction_factor
                        target_x += est_vel_x * prediction_time
                        target_y += est_vel_y * prediction_time
                
                # For flanking, offset the target position perpendicular to estimated player direction
                if self.behavior_state == "flank":
                    # Calculate perpendicular vector to player's estimated direction
                    if self.last_player_pos is not None:
                        last_x, last_y = self.last_player_pos
                        # Get direction vector
                        dir_x = player_x - last_x
                        dir_y = player_y - last_y
                        
                        # Calculate perpendicular vector (normalize first)
                        length = math.sqrt(dir_x**2 + dir_y**2)
                        if length > 0:  # Avoid division by zero
                            dir_x /= length
                            dir_y /= length
                            
                            # Get perpendicular vector (rotate 90 degrees)
                            perp_x = -dir_y * self.flanking_direction
                            perp_y = dir_x * self.flanking_direction
                            
                            # Offset the target position
                            flank_distance = 150
                            target_x += perp_x * flank_distance
                            target_y += perp_y * flank_distance
                
                # For ambush, try to get ahead of player's path
                if self.behavior_state == "ambush" and self.last_player_pos is not None:
                    last_x, last_y = self.last_player_pos
                    # Calculate player direction
                    dir_x = player_x - last_x
                    dir_y = player_y - last_y
                    
                    # Only ambush if player is moving significantly
                    dir_length = math.sqrt(dir_x**2 + dir_y**2)
                    if dir_length > 5:
                        dir_x /= dir_length
                        dir_y /= dir_length
                        ambush_distance = 200
                        target_x = player_x + dir_x * ambush_distance
                        target_y = player_y + dir_y * ambush_distance
                
                # Calculate angle to target position
                dx = target_x - self.x
                dy = target_y - self.y
                target_angle = math.degrees(math.atan2(dy, dx))
                
                # Calculate shortest rotation to target
                angle_diff = (target_angle - self.rotation) % 360
                if angle_diff > 180:
                    angle_diff -= 360
                
                # Rotate towards target with some randomness for more natural movement
                rotation_speed = self.rotation_speed
                if self.behavior_state == "attack":
                    rotation_speed *= 1.2  # Faster rotation during attack
                
                if abs(angle_diff) > 5:  # Only rotate if difference is significant
                    if angle_diff > 0:
                        self.rotation += min(rotation_speed * dt, abs(angle_diff))
                    else:
                        self.rotation -= min(rotation_speed * dt, abs(angle_diff))
                
                # Apply thrust based on behavior
                if self.behavior_state == "seek":
                    # Move towards player at medium speed
                    self.acceleration = 0.7  # Slightly faster than before
                elif self.behavior_state == "attack":
                    # Move towards player more aggressively
                    self.acceleration = 1.0  # Full thrust during attack
                elif self.behavior_state == "ambush":
                    # Move to ambush position quickly
                    self.acceleration = 0.9
                elif self.behavior_state == "flank":
                    # Move to flanking position
                    self.acceleration = 0.8
                    
                # Shooting logic based on behavior state and distance to player
                should_fire = False
                firing_accuracy = self.shot_accuracy
                
                # Only shoot if angle to player is reasonably aligned
                aim_angle_diff = abs(angle_diff)
                if aim_angle_diff < 20:  # Narrower firing arc than before
                    # Scale accuracy based on angle - more accurate when directly aligned
                    accuracy_scale = 1.0 - (aim_angle_diff / 20) * 0.3
                    firing_accuracy *= accuracy_scale
                    
                    # Different shooting patterns based on behavior
                    if self.burst_mode and self.burst_fire_cooldown <= 0:
                        # Burst fire mode - 3 quick shots
                        if self.burst_fire_count > 0 and self.burst_fire_delay <= 0:
                            should_fire = True
                            self.burst_fire_count -= 1
                            self.burst_fire_delay = 0.15  # Delay between burst shots
                        elif self.burst_fire_count == 0:
                            # Start a new burst
                            self.burst_fire_count = 3  # 3 shots per burst
                            self.burst_fire_cooldown = self.shoot_rate * 1.5  # Longer cooldown after burst
                            should_fire = True
                            self.burst_fire_count -= 1 
                            self.burst_fire_delay = 0.15
                    else:
                        # Normal fire mode
                        if self.shoot_cooldown <= 0:
                            should_fire = True
                            self.shoot_cooldown = self.shoot_rate
                    
                    # Apply accuracy randomization to firing decision
                    if should_fire and random.random() > firing_accuracy:
                        # "Miss" the shot intentionally
                        should_fire = False
                        # We still used our shot though, don't want to fire immediately again
                    
                    if should_fire and sound_manager:
                        sound_manager.play("enemy_shoot")
                    
                    if should_fire:
                        return True  # Signal to gameplay state to create a projectile
            
            elif self.behavior_state == "evade":
                # Move away from player
                target_angle = (math.degrees(math.atan2(dy, dx)) + 180) % 360  # Opposite direction
                
                # Calculate shortest rotation to target
                angle_diff = (target_angle - self.rotation) % 360
                if angle_diff > 180:
                    angle_diff -= 360
                
                # Rotate away from player
                if abs(angle_diff) > 5:
                    if angle_diff > 0:
                        self.rotation += min(self.rotation_speed * dt, abs(angle_diff))
                    else:
                        self.rotation -= min(self.rotation_speed * dt, abs(angle_diff))
                
                # Apply thrust to move away
                self.acceleration = 1.0  # Full thrust when evading (increased from 0.8)
                
                # Occasionally fire backward while evading if health is not too low
                if self.health > 1 and self.shoot_cooldown <= 0 and random.random() < 0.3:
                    if sound_manager:
                        sound_manager.play("enemy_shoot")
                    self.shoot_cooldown = self.shoot_rate * 1.5  # Longer cooldown for rear shots
                    return True  # Signal to gameplay state to create a projectile
        else:
            # Player is out of detection range
            self.last_detection_time += dt
            
            # If we have a last known position and haven't detected player recently
            if self.last_player_pos and self.last_detection_time < 7.0:  # Remember player for longer (up from 5s)
                # Move toward last known position
                last_x, last_y = self.last_player_pos
                dx = last_x - self.x
                dy = last_y - self.y
                
                # Calculate target angle to last known position
                target_angle = math.degrees(math.atan2(dy, dx))
                
                # Calculate shortest rotation to target
                angle_diff = (target_angle - self.rotation) % 360
                if angle_diff > 180:
                    angle_diff -= 360
                
                # Rotate towards last known position
                if abs(angle_diff) > 5:
                    if angle_diff > 0:
                        self.rotation += min(self.rotation_speed * dt, abs(angle_diff))
                    else:
                        self.rotation -= min(self.rotation_speed * dt, abs(angle_diff))
                
                # Apply thrust
                self.acceleration = 0.6  # Slightly higher thrust when searching (up from 0.5)
                
                # Occasionally fire shots in the direction of last known position
                if self.shoot_cooldown <= 0 and random.random() < 0.1 and abs(angle_diff) < 30:
                    if sound_manager:
                        sound_manager.play("enemy_shoot")
                    self.shoot_cooldown = self.shoot_rate * 1.3
                    return True
            else:
                # Smarter random wandering behavior when player is out of range for a while
                if random.random() < 0.03:  # Random direction change (slightly higher chance)
                    self.rotation += random.uniform(-40, 40)  # More varied rotation
                    
                # Apply random thrust
                if random.random() < 0.08:  # Slightly higher chance to change acceleration
                    self.acceleration = random.uniform(0.4, 0.7)  # Higher acceleration range
                else:
                    self.acceleration = max(0, self.acceleration - 0.1 * dt)  # Gradual deceleration
                
                # Occasionally fire shots when wandering
                if self.shoot_cooldown <= 0 and random.random() < 0.02:
                    if sound_manager:
                        sound_manager.play("enemy_shoot")
                    self.shoot_cooldown = self.shoot_rate * 1.5
                    return True
        
        # Apply acceleration based on rotation
        if self.acceleration > 0:
            angle_rad = math.radians(self.rotation)
            accel_x = math.cos(angle_rad) * self.thrust_strength * self.acceleration * dt
            accel_y = math.sin(angle_rad) * self.thrust_strength * self.acceleration * dt
            
            # Apply acceleration to velocity
            self.vel_x += accel_x
            self.vel_y += accel_y
            
            # Limit velocity to max speed
            velocity = math.sqrt(self.vel_x * self.vel_x + self.vel_y * self.vel_y)
            if velocity > self.max_velocity:
                scale = self.max_velocity / velocity
                self.vel_x *= scale
                self.vel_y *= scale
            
            # Play looping thrust sound if acceleration is significant
            # if sound_manager and self.acceleration > 0.3:
            #     sound_manager.loop("enemy_thrust")
        
        # Check if acceleration state changed (for sound effects)
        # current_acceleration = self.acceleration > 0.3
        # if not current_acceleration and previous_acceleration and sound_manager:
        #     sound_manager.stop("enemy_thrust")
        
        # Apply friction/damping
        self.vel_x *= self.friction
        self.vel_y *= self.friction
        
        # Update position based on velocity
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
        
        # Update timers
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt
        
        # Wrap position around screen edges
        if self.x < 0:
            self.x = screen_width
        elif self.x > screen_width:
            self.x = 0
        if self.y < 0:
            self.y = screen_height
        elif self.y > screen_height:
            self.y = 0
            
        return False  # Signal that no projectile was fired this update
    
    def start_asteroid_avoidance(self, asteroid):
        """Calculate avoidance maneuver for an incoming asteroid"""
        # Calculate vector from asteroid to enemy
        dx = self.x - asteroid.x
        dy = self.y - asteroid.y
        
        # Calculate perpendicular direction to avoid (either left or right)
        # We'll use the cross product to determine which direction is better
        asteroid_vel_x = asteroid.vel_x if hasattr(asteroid, 'vel_x') else 0
        asteroid_vel_y = asteroid.vel_y if hasattr(asteroid, 'vel_y') else 0
        
        # Cross product to determine which side to turn
        cross_product = dx * asteroid_vel_y - dy * asteroid_vel_x
        
        # If cross product is positive, turn right; if negative, turn left
        self.avoidance_direction = 1 if cross_product > 0 else -1
        
        # Set avoidance state
        self.avoiding_asteroid = True
        self.avoidance_timer = 1.0  # Avoid for 1 second
        
        # Set behavior state to evade
        self.behavior_state = "evade"
    
    def update_behavior_state(self, player_x, player_y):
        """Update the AI behavior state based on situation"""
        # Don't change behavior if currently avoiding asteroid
        if self.avoiding_asteroid:
            return
            
        # Calculate distance to player
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Determine behavior based on distance, health, and randomness for unpredictability
        if distance < 120:  # Very close
            if self.health > 2:
                # If healthy enough, choose between attack and evade
                self.behavior_state = "attack" if random.random() < 0.7 else "evade"
            else:
                # If damaged, primarily evade when close but still may attack occasionally
                self.behavior_state = "evade" if random.random() < 0.85 else "attack"
        elif distance < 300:  # Medium distance
            random_val = random.random()
            if self.health > 2:
                # Aggressive when healthy at medium range
                if random_val < 0.6:
                    self.behavior_state = "attack"
                elif random_val < 0.8:
                    self.behavior_state = "flank"
                else:
                    self.behavior_state = "seek"
            else:
                # Mix of behaviors when damaged
                if random_val < 0.4:
                    self.behavior_state = "attack"
                elif random_val < 0.7:
                    self.behavior_state = "flank"
                elif random_val < 0.9:
                    self.behavior_state = "seek"
                else:
                    self.behavior_state = "evade"
        else:  # Far away
            random_val = random.random()
            # More strategic at range
            if random_val < 0.4:
                self.behavior_state = "seek"
            elif random_val < 0.7:
                self.behavior_state = "ambush"
            else:
                self.behavior_state = "flank"
    
    def take_damage(self):
        """Handle enemy taking damage"""
        self.health -= 1
        if self.health <= 0:
            self.active = False
            self.respawn_timer = 8.0  # Respawn slightly faster (from 10 seconds)
            return True  # Signal that enemy was destroyed
        
        # When damaged, change behavior and possibly increase aggression
        if random.random() < 0.5:
            self.behavior_state = "attack"  # Become aggressive when hit
            self.shot_accuracy = min(0.99, self.shot_accuracy + 0.05)  # Become more accurate
        else:
            self.behavior_state = "evade"  # Or retreat to recover
        
        return False  # Enemy damaged but not destroyed
    
    def respawn(self, screen_width, screen_height, player_x, player_y):
        """Respawn the enemy ship away from the player"""
        # Find a position away from the player
        while True:
            x = random.randint(0, screen_width)
            y = random.randint(0, screen_height)
            
            # Make sure it's not too close to the player
            dx = x - player_x
            dy = y - player_y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance > 350:  # Increased safe distance (from 300)
                break
        
        # Reset enemy state
        self.x = x
        self.y = y
        self.vel_x = 0
        self.vel_y = 0
        self.rotation = random.uniform(0, 360)
        self.health = 4  # Increased health (from 3)
        self.active = True
        self.behavior_state = "seek"
        self.last_player_pos = None
        self.avoiding_asteroid = False
        self.avoidance_timer = 0
        self.burst_fire_count = 0
        self.burst_fire_cooldown = 0
        self.burst_fire_delay = 0
        self.flanking_direction = random.choice([-1, 1])
        self.prediction_factor = random.uniform(0.6, 1.0)
        self.strategy_change_timer = random.uniform(8.0, 15.0)
        self.shot_accuracy = random.uniform(0.85, 0.97)  # Reset accuracy for the new ship
    
    def render(self, surface):
        """Render the enemy ship"""
        # Don't render if inactive or off screen
        if not self.active or (self.x < -50 or self.x > surface.get_width() + 50 or
                               self.y < -50 or self.y > surface.get_height() + 50):
            return
        
        # Calculate ship vertices based on current rotation
        angle_rad = math.radians(self.rotation)
        
        # Enhanced enemy ship design: more angular, aggressive, and detailed
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
        
        # Secondary hull details for more depth
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
        
        # Improved enemy ship colors based on health with metallic shading
        if self.health >= 4:
            base_color = (200, 30, 30)  # Deep red at full health
            highlight_color = (255, 80, 80)  # Red highlight
            glow_color = (255, 50, 50, 100)  # Red glow
        elif self.health == 3:
            base_color = (220, 50, 20)  # Red-orange at high health
            highlight_color = (255, 100, 50)  # Orange-red highlight
            glow_color = (255, 70, 20, 100)  # Orange-red glow
        elif self.health == 2:
            base_color = (230, 100, 20)  # Orange at medium health
            highlight_color = (255, 140, 40)  # Brighter orange highlight
            glow_color = (255, 120, 30, 100)  # Orange glow
        else:
            base_color = (230, 150, 20)  # Yellow-orange at low health
            highlight_color = (255, 180, 30)  # Yellow highlight
            glow_color = (255, 170, 30, 100)  # Yellow-orange glow
            
        # Add menacing red engine glow
        engine_glow_radius = 8 + (pygame.time.get_ticks() % 6) / 3.0  # Pulsating effect
        engine_glow_color = (255, 60, 50, 130)  # Red engine glow
        
        # Engine position
        back_angle = angle_rad + math.pi
        engine_x = self.x + math.cos(back_angle) * 12
        engine_y = self.y + math.sin(back_angle) * 12
        
        # Create a surface for the glow with alpha
        glow_surface = pygame.Surface((int(engine_glow_radius*2), int(engine_glow_radius*2)), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, engine_glow_color, 
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
        
        # Draw engine thrust if accelerating with enhanced visual effect
        if self.acceleration > 0.3:
            # Engine position (behind the ship)
            engine_angle = angle_rad + math.pi  # Opposite direction of ship heading
            
            # Create flame effect with random length and layered appearance
            flame_length = 12 + (pygame.time.get_ticks() % 8)  # Enhanced fluctuating flame
            flame_width = 7 + random.uniform(-1, 1)
            
            # Outer flame layer (reddish)
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
            
            # Draw the flame with a vibrant red-orange color
            flame_color = (255, 80, 30)
            pygame.draw.polygon(surface, flame_color, flame_points)
            
            # Middle flame layer (orange)
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
            
            mid_flame_color = (255, 140, 20)
            pygame.draw.polygon(surface, mid_flame_color, mid_flame_points)
            
            # Inner flame layer (yellow-white core)
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
            
            inner_flame_color = (255, 220, 100)
            pygame.draw.polygon(surface, inner_flame_color, inner_flame_points)
            
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
                
                # Draw side thrusters with orange-red colors
                pygame.draw.polygon(surface, (255, 120, 30), right_flame_points)
                pygame.draw.polygon(surface, (255, 120, 30), left_flame_points)
        
        # Health indicator using pulsating energy lines along the hull
        if self.health > 0:
            # Pulse based on health level (faster pulse when lower health)
            pulse_speed = 1500 - (self.health * 300)  # 300, 600, 900, 1200 ms
            pulse_phase = (pygame.time.get_ticks() % pulse_speed) / pulse_speed
            
            # Draw energy lines along hull based on health
            for i in range(self.health):
                line_intensity = int(100 + 155 * pulse_phase)
                line_color = (255, line_intensity, line_intensity)
                
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