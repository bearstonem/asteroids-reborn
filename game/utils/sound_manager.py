import pygame
import os
import random

class SoundManager:
    """
    Manages all sound effects for Asteroids Reborn
    """
    def __init__(self):
        # Dictionary to store loaded sounds
        self.sounds = {}
        
        # Dictionary to store loaded music
        self.music_tracks = {}
        self.current_music = None
        
        # Sound settings
        self.enabled = True
        self.volume = 0.7  # Default volume level (0.0 to 1.0)
        self.music_volume = 0.5  # Default music volume level
        
        # Track currently looping sounds
        self.looping_sounds = {}
        
        # Try to load sounds if pygame mixer is initialized
        if pygame.mixer.get_init():
            self.load_sounds()
            self.load_music()
        else:
            print("Warning: pygame mixer not initialized, sounds disabled")
            self.enabled = False
    
    def load_sounds(self):
        """Load all sound effects into memory"""
        sounds_dir = os.path.join("game", "assets", "sounds")
        
        # Define sound effects to load
        sound_files = {
            "player_shoot": "player_shoot.mp3",
            "explosion": "explosion.mp3",
            "thrust": "thrust.mp3",
            "enemy_thrust": "enemy_thrust.mp3",  # Reuse player thrust for enemy thrust            
            "powerup": "powerup.mp3",
            "game_over": "game_over.mp3",
            "level_up": "level_up.mp3",
            "hit": "hit.mp3",  # Added hit sound for enemy being hit
            "enemy_shoot": "enemy_shoot.mp3",  # Enemy shoot sound
            "powerup_spawn": "powerup_spawn.mp3"
        }
        
        # Load each sound
        for name, file in sound_files.items():
            sound_path = os.path.join(sounds_dir, file)
            try:
                if os.path.isfile(sound_path) and os.path.getsize(sound_path) > 0:
                    self.sounds[name] = pygame.mixer.Sound(sound_path)
                    self.sounds[name].set_volume(self.volume)
                else:
                    print(f"Warning: Sound file '{sound_path}' not found or empty")
            except pygame.error as e:
                print(f"Error loading sound '{sound_path}': {e}")
    
    def load_music(self):
        """Load all music tracks into memory"""
        music_dir = os.path.join("game", "assets", "sounds", "music")
        
        try:
            # Check if music directory exists
            if os.path.isdir(music_dir):
                # Find all music files in directory
                for file in os.listdir(music_dir):
                    if file.endswith(".mp3") or file.endswith(".ogg") or file.endswith(".wav"):
                        track_name = os.path.splitext(file)[0]  # Get name without extension
                        self.music_tracks[track_name] = os.path.join(music_dir, file)
                print(f"Loaded {len(self.music_tracks)} music tracks")
            else:
                print(f"Warning: Music directory '{music_dir}' not found")
        except Exception as e:
            print(f"Error loading music: {e}")
    
    def play(self, sound_name):
        """Play a sound by name"""
        if not self.enabled:
            return
            
        if sound_name in self.sounds:
            self.sounds[sound_name].play()
        else:
            print(f"Warning: Attempted to play unknown sound '{sound_name}'")
    
    def loop(self, sound_name):
        """Loop a sound continuously"""
        if not self.enabled:
            return
            
        if sound_name in self.sounds:
            # Don't start the sound again if it's already looping
            if sound_name not in self.looping_sounds or not self.looping_sounds[sound_name]:
                # Use the built-in loop parameter (-1 for infinite loop)
                channel = self.sounds[sound_name].play(-1)
                self.looping_sounds[sound_name] = True
        else:
            print(f"Warning: Attempted to loop unknown sound '{sound_name}'")
    
    def stop(self, sound_name):
        """Stop a specific sound"""
        if not self.enabled:
            return
            
        if sound_name in self.sounds:
            self.sounds[sound_name].stop()
            # Update looping status
            if sound_name in self.looping_sounds:
                self.looping_sounds[sound_name] = False
        else:
            print(f"Warning: Attempted to stop unknown sound '{sound_name}'")
    
    def set_volume(self, volume):
        """Set the volume for all sounds (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, volume))  # Clamp between 0 and 1
        
        # Update volume for all loaded sounds
        for sound in self.sounds.values():
            sound.set_volume(self.volume)
    
    def set_music_volume(self, volume):
        """Set the volume for music (0.0 to 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))  # Clamp between 0 and 1
        pygame.mixer.music.set_volume(self.music_volume)
    
    def play_random_music(self):
        """Play a random music track"""
        if not self.enabled or not self.music_tracks:
            return None
        
        # Choose a random track
        track_name = random.choice(list(self.music_tracks.keys()))
        return self.play_music(track_name)
    
    def play_music(self, track_name):
        """Play a specific music track by name"""
        if not self.enabled:
            return None
        
        if track_name in self.music_tracks:
            try:
                # Stop any currently playing music
                pygame.mixer.music.stop()
                
                # Load and play the selected track
                pygame.mixer.music.load(self.music_tracks[track_name])
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(-1)  # Loop indefinitely
                
                self.current_music = track_name
                return track_name
            except pygame.error as e:
                print(f"Error playing music '{track_name}': {e}")
                return None
        else:
            print(f"Warning: Attempted to play unknown music track '{track_name}'")
            return None
    
    def stop_music(self):
        """Stop the currently playing music"""
        if self.enabled:
            pygame.mixer.music.stop()
            self.current_music = None
    
    def toggle_sounds(self):
        """Toggle sounds on/off"""
        self.enabled = not self.enabled
        
        # If disabling sounds, stop all currently looping sounds and music
        if not self.enabled:
            for sound_name in list(self.looping_sounds.keys()):
                if self.looping_sounds[sound_name]:
                    self.sounds[sound_name].stop()
                    self.looping_sounds[sound_name] = False
            
            # Stop music
            pygame.mixer.music.stop()
                    
        return self.enabled 