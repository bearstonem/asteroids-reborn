import pygame
import sys

class WebAudioHelper:
    """
    Helper class for managing audio in web environments
    where audio autoplay is restricted by browsers
    """
    
    def __init__(self):
        self.audio_initialized = False
        self.audio_queued = []  # Queue for sound objects to play after initialization
        self.is_web = self._check_if_web()
    
    def _check_if_web(self):
        """Check if running in a web environment (pygbag)"""
        return hasattr(sys, 'platform') and sys.platform.startswith('emscripten')
    
    def initialize_audio(self):
        """Initialize pygame audio system"""
        if not self.audio_initialized:
            try:
                pygame.mixer.init()
                self.audio_initialized = True
                # Play any queued sounds
                for sound, kwargs in self.audio_queued:
                    sound.play(**kwargs)
                self.audio_queued = []  # Clear the queue
                return True
            except Exception as e:
                print(f"Failed to initialize audio: {e}")
                return False
        return True  # Already initialized
    
    def safe_play(self, sound, **kwargs):
        """
        Safely play a sound, handling browser restrictions
        
        Args:
            sound: pygame.mixer.Sound object
            **kwargs: Additional arguments to pass to sound.play()
        """
        # If not in web environment, play normally
        if not self.is_web:
            sound.play(**kwargs)
            return True
            
        # If in web but audio not initialized, queue it
        if not self.audio_initialized:
            self.audio_queued.append((sound, kwargs))
            return False
            
        # Audio is initialized and we're good to play
        sound.play(**kwargs)
        return True
    
    def safe_load_sound(self, path):
        """
        Safely load a sound file, handling potential errors
        
        Args:
            path: Path to the sound file
            
        Returns:
            pygame.mixer.Sound object or None if loading failed
        """
        try:
            return pygame.mixer.Sound(path)
        except Exception as e:
            print(f"Error loading sound {path}: {e}")
            return None


# Create a singleton instance for global use
audio_helper = WebAudioHelper() 