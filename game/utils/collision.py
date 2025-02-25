import math

def check_collision(entity1, entity2):
    """
    Simple circle-based collision detection between two entities.
    Both entities must have x, y, and radius attributes.
    
    Args:
        entity1: First entity to check collision
        entity2: Second entity to check collision
        
    Returns:
        bool: True if entities are colliding, False otherwise
    """
    # Calculate the distance between entity centers
    dx = entity1.x - entity2.x
    dy = entity1.y - entity2.y
    distance = math.sqrt(dx * dx + dy * dy)
    
    # Check if the distance is less than the sum of radii
    return distance < (entity1.radius + entity2.radius) 