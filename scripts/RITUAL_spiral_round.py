"""
Ritual of the Spiral - a Razor Enhanced Python Script for Ultima Online

Places a 45-degree rotated spiral pattern with smooth corners using black pearls.
2 tiles spacing between rings

VERSION::20250621
"""

import sys
import math
import time
from System.Collections.Generic import List

# Constants for ritual patterns
SPIRAL_RADIUS = 7  # Maximum radius of spiral
SPIRAL_POINTS = [  # Pre-calculated spiral points relative to center
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

# Movement and timing constants
MAX_DISTANCE = 2  # Maximum distance for placement
PATHFINDING_RETRY = 3  # Number of retries for movement
PAUSE_DURATION = 800  # Standard pause between actions

# Item IDs
BLACKPEARL_ID = 0x0F7A  # Black pearl for spiral pattern

# Feature flags
PLACE_SPIRAL = True
COMPLETE_RITUAL = True

def gotoLocation(x, y, max_retries=PATHFINDING_RETRY):
    """Attempt to move to location with retries."""
    attempts = 0
    while attempts < max_retries:
        coords = PathFinding.Route()
        coords.X = x
        coords.Y = y
        coords.MaxRetry = 3
        PathFinding.Go(coords)
        Misc.Pause(PAUSE_DURATION)  # Wait for movement
        
        # Check if we're close enough
        if abs(Player.Position.X - x) <= MAX_DISTANCE and abs(Player.Position.Y - y) <= MAX_DISTANCE:
            return True
        
        attempts += 1
        if attempts < max_retries:
            Misc.SendMessage(f"Retrying movement to ({x}, {y}), attempt {attempts + 1}/{max_retries}", 33)
            Misc.Pause(PAUSE_DURATION)  # Wait before retry
    
    return False

def generate_spiral_points(center_x, center_y, max_radius):
    """Generate points for an inward spiral pattern.
    Uses pre-calculated points to create a rotated square spiral with rounded corners."""
    points = []
    
    # Convert relative points to absolute coordinates
    for dx, dy in SPIRAL_POINTS:
        # Skip points outside max radius
        if abs(dx) > max_radius or abs(dy) > max_radius:
            continue
            
        x = center_x + dx
        y = center_y + dy
        points.append((x, y))
    
    return points

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
        
        # Move to position if needed
        if not Player.InRangeItem(item, MAX_DISTANCE):
            if not gotoLocation(x, y):
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
    if gotoLocation(center_x, center_y):
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
            place_items_at_points([point], center_x, center_y, placed_positions, BLACKPEARL_ID)
            
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
