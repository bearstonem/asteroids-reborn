import pygame
from game.utils.sound_manager import SoundManager

class GameState:
    """
    Main game state manager for Asteroids Reborn
    Handles state transitions and common game resources
    """
    def __init__(self):
        self.current_state = None
        self.states_stack = []
        # Initialize sound manager
        self.sound_manager = SoundManager()
        
    def change_state(self, new_state):
        """
        Change to a completely new state, clearing the state stack
        """
        self.states_stack.clear()
        self.push_state(new_state)
    
    def push_state(self, new_state):
        """
        Push a new state onto the stack (e.g., pause menu over gameplay)
        """
        self.states_stack.append(new_state)
        self.current_state = new_state
    
    def pop_state(self):
        """
        Remove the top state and go back to the previous one
        """
        if len(self.states_stack) > 1:
            self.states_stack.pop()
            self.current_state = self.states_stack[-1]
            return True
        return False
    
    def handle_event(self, event):
        """
        Pass events to the current state
        """
        if self.current_state:
            self.current_state.handle_event(event)
    
    def update(self, dt):
        """
        Update the current state
        """
        if self.current_state:
            self.current_state.update(dt)
    
    def render(self, surface):
        """
        Render the current state
        """
        if self.current_state:
            self.current_state.render(surface) 