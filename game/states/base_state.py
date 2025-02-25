class BaseState:
    """
    Base class for all game states
    """
    def __init__(self, game_state):
        self.game_state = game_state
    
    def handle_event(self, event):
        """
        Handle input events
        """
        pass
    
    def update(self, dt):
        """
        Update game state
        """
        pass
    
    def render(self, surface):
        """
        Render the state to the screen
        """
        pass
    
    def enter(self):
        """
        Called when state becomes active
        """
        pass
    
    def exit(self):
        """
        Called when state is no longer active
        """
        pass 