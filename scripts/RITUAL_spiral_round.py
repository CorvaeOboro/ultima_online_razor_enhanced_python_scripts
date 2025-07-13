"""
Ritual of the Spiral - a Razor Enhanced Python Script for Ultima Online

Places a 45-degree rotated spiral pattern with smooth corners ..
2 tiles spacing between rings

Current Items = Black pearl (0x0F7A)

VERSION::20250621
"""

# Item IDs
PLACE_ITEM_ID = 0x0F7A  # Black pearl for spiral pattern

"""
# Toggle to select spiral generation method
USE_ARCHIMEDES_SPIRAL = True  # True = use Archimedean spiral, False = use manual SPIRAL_POINTS

EXAMPLE_MANUAL_SPIRAL_POINTS = [  # Pre-calculated spiral points relative to center
    (0, 0),     # Center
    (1, -1),    # First diagonal step
    (2, -2),    # Northeast corner
    (2, -1),    # Move southeast
    (2, 0),     
    (2, 1),
    (2, 2),     # Southeast corner
    (1, 2),     # Move southwest
    (0, 2),     
    (-1, 2),
    (-2, 2),    # Southwest corner
    (-2, 1),    # Move northwest
    (-2, 0),    
    (-2, -1),
    (-2, -2),   # Northwest corner
    (-1, -2),   # Move northeast
    (0, -2),    
    (1, -2),    # Complete first ring
    (4, -4),    # Start second ring
    (4, -3),    # Move southeast
    (4, -2),
    (4, -1),
    (4, 0),
    (4, 1),
    (4, 2),     # Southeast section
    (3, 3),     # Move southwest
    (2, 4),
    (1, 4),
    (0, 4),
    (-1, 4),
    (-2, 4),    # Southwest section
    (-3, 3),    # Move northwest
    (-4, 2),
    (-4, 1),
    (-4, 0),
    (-4, -1),
    (-4, -2),   # Northwest section
    (-3, -3),   # Move northeast
    (-2, -4),
    (-1, -4),
    (0, -4),
    (1, -4),
    (2, -4),    # Northeast section
    (3, -3),    # Return to start of ring
    (4, -4)     # Complete second ring
]
"""

# Constants for ritual patterns
SPIRAL_RADIUS = 8  # Maximum radius of spiral (increased for larger spiral)
# Spiral generation parameters
SPIRAL_SPACING = 2  # Distance between spiral arms (tiles)
SPIRAL_TURNS = 2    # Number of full turns the spiral makes (increased for more coils)

# Generate a smooth, rounded spiral using the Archimedean spiral formula
import math

def generate_spiral_points(center_x, center_y, max_radius, spacing=SPIRAL_SPACING, turns=SPIRAL_TURNS):
    """Generate spiral points using the selected method."""
    if USE_ARCHIMEDES_SPIRAL:
        points = []
        a = 0  # Start at center
        b = spacing / (2 * math.pi)  # Controls the distance between spiral arms
        theta = 0
        theta_max = turns * 2 * math.pi
        last_point = None
        while True:
            r = a + b * theta
            if r > max_radius:
                break
            x = int(round(center_x + r * math.cos(theta)))
            y = int(round(center_y + r * math.sin(theta)))
            if last_point != (x, y):
                points.append((x, y))
                last_point = (x, y)
            theta += 0.25  # Smaller values = smoother spiral
        return points
    else:
        # Manual points, shifted to center
        return [(center_x + dx, center_y + dy) for (dx, dy) in EXAMPLE_MANUAL_SPIRAL_POINTS]

# Movement and timing constants
MAX_DISTANCE = 2  # Maximum distance for placement
PATHFINDING_RETRY = 3  # Number of retries for movement
PAUSE_DURATION = 800  # Standard pause between actions

# Feature flags
PLACE_SPIRAL = True
COMPLETE_RITUAL = True

def get_direction(from_x, from_y, to_x, to_y):
    """Calculate direction from one point to another"""
    dx = to_x - from_x
    dy = to_y - from_y
    if dx == 0:
        if dy < 0: return 0  # North
        return 4  # South
    elif dy == 0:
        if dx > 0: return 2  # East
        return 6  # West
    elif dx > 0:
        if dy < 0: return 1  # Northeast
        return 3  # Southeast
    else:
        if dy < 0: return 7  # Northwest
        return 5  # Southwest

def goto_location_with_wiggle(x, y, max_retries=3):
    """Move to within placement range"""
    target_x = float(x)
    target_y = float(y)
    for _ in range(max_retries):
        if (abs(Player.Position.X - target_x) <= MAX_DISTANCE and 
            abs(Player.Position.Y - target_y) <= MAX_DISTANCE):
            return True
        Player.PathFindTo(int(target_x), int(target_y), Player.Position.Z)
        Misc.Pause(500)
        if not (abs(Player.Position.X - target_x) <= MAX_DISTANCE and 
                abs(Player.Position.Y - target_y) <= MAX_DISTANCE):
            direction = get_direction(Player.Position.X, Player.Position.Y, target_x, target_y)
            Player.Walk(direction)
            Misc.Pause(200)
    return False

def place_items_at_points(points, center_x, center_y, placed_positions=None, item_id=None):
    """Place items at specified coordinates, avoiding duplicates."""
    if placed_positions is None:
        placed_positions = set()
    
    if item_id is None:
        Misc.SendMessage("No item ID specified!", 33)
        return False
    
    # Ensure we have the item
    item = Items.FindByID(item_id, -1, Player.Backpack.Serial)
    if not item:
        Misc.SendMessage(f"Cannot find required item (0x{item_id:X})!", 33)
        return False
    
    for x, y in points:
        # Skip if already placed
        if (x, y) in placed_positions:
            continue
        
        # Move to position if needed (check player vs. target tile)
        if abs(Player.Position.X - x) > MAX_DISTANCE or abs(Player.Position.Y - y) > MAX_DISTANCE:
            if not goto_location_with_wiggle(float(x), float(y)):
                Misc.SendMessage(f"Failed to reach position ({x}, {y})", 33)
                continue
        # Place item
        Items.MoveOnGround(item.Serial, 1, x, y, Player.Position.Z)
        Misc.Pause(PAUSE_DURATION)
        placed_positions.add((x, y))
    
    return True

def complete_ritual(center_x, center_y):
    """Complete the ritual by returning to center."""
    # Return to center
    if goto_location_with_wiggle(center_x, center_y):
        # Use Spirit Speak at center
        Player.UseSkill("Spirit Speak")
        Misc.Pause(PAUSE_DURATION)
        return True
    
    Misc.SendMessage("Failed to return to ritual center!", 33)
    return False

def main():
    """Main ritual function."""
    # Use player's current position as ritual center
    center_x = Player.Position.X
    center_y = Player.Position.Y
    
    Misc.SendMessage(f"Starting rotated spiral ritual at current position ({center_x}, {center_y})...", 65)
    
    # Track placed positions
    placed_positions = set()
    
    # Generate and place spiral pattern
    if PLACE_SPIRAL:
        Misc.SendMessage("Creating rotated spiral pattern with black pearls...", 65)
        spiral_points = generate_spiral_points(center_x, center_y, SPIRAL_RADIUS)
        
        # Place points in order from outside in
        total_points = len(spiral_points)
        for i, point in enumerate(spiral_points, 1):
            place_items_at_points([point], center_x, center_y, placed_positions, PLACE_ITEM_ID)
            
            # Show progress every 10 points
            if i % 10 == 0 or i == total_points:
                percent = (i / total_points) * 100
                Misc.SendMessage(f"Progress: {i}/{total_points} points placed ({percent:.0f}%)", 65)
        
        Misc.SendMessage(f"Spiral pattern complete! Placed {total_points} points.", 65)
    
    # Complete the ritual
    if COMPLETE_RITUAL:
        complete_ritual(center_x, center_y)
        Misc.SendMessage("Ritual completed successfully!", 65)

if __name__ == '__main__':
    main()
