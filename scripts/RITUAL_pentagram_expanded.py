"""
RITUAL of the Pentagram - A Razor Enhanced Python Script for Ultima Online

Creates a pentagram ritual pattern with multiple layers:

1. Main Components:
   - Star Pattern: 5-point pentagram 
   - Main Circle: Large central circle surrounding the pentagram
   - Secondary Circles: Small circles at each pentagram point
   - Candle Circle: Outer circle of candles

2. Additional Features:
   - pathfinding retries
   - Error handling and recovery
   - Progress messages
   - Layer toggles

Current Items 
Black pearl , bloodmoss 

VERSION::20250621
"""

import sys
import math
import time
from System.Collections.Generic import List

# Phase toggles
PLACE_STAR = True          # Place the pentagram star
PLACE_CIRCLE = True        # Place the main circle
PLACE_SECONDARY = True     # Place circles at star points
PLACE_CANDLES = True       # Place the outer candle circle
PLACE_OVERLAY = False      # Place overlay items on the pattern

# Constants for ritual patterns
MAIN_RADIUS = 10          # Main circle radius
SECONDARY_RADIUS = 1      # Secondary circle radius
NUM_POINTS = 5            # Five points for pentagram
SECONDARY_RESOLUTION = 32 # Points in secondary circles
ROTATION_ANGLE = 0        # Starting angle (0 = east)

# Golden ratio for perfect pentagram proportions
GOLDEN_RATIO = 1.618033988749895

# Item IDs
STAR_ITEM_ID = 0x0F7B     # Main pentagram lines (Black Pearl)
CIRCLE_ITEM_ID = 0x0F7A   # Main circle (Bloodmoss)
SECONDARY_ITEM_ID = 0x0F7B # Secondary circles (Black Pearl)
CANDLE_ID = 0x0A28        # Candles for outer circle
OVERLAY_ITEM_ID = 0x0F8E  # Nox crystal for overlay

# Timing constants
MAX_DISTANCE = 1          # Maximum distance for placement
PATHFINDING_RETRY = 3     # Number of retries for movement
PAUSE_DURATION = 800      # Standard pause between actions
MOVE_RETRY_PAUSE = 200    # Shorter pause for retrying movement

def find_item_with_retry(item_id, max_retries=3, retry_delay=500):
    """Find an item in backpack with retries and delay."""
    for _ in range(max_retries):
        item = Items.FindByID(item_id, -1, Player.Backpack.Serial)
        if item:
            return item
        Misc.Pause(retry_delay)
    return None

def try_random_position(x, y, radius=2):
    """Try to find a valid position near the target."""
    import random
    
    # Get current position
    current_x = Player.Position.X
    current_y = Player.Position.Y
    
    # Try cardinal directions first
    for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
        coords = PathFinding.Route()
        coords.X = current_x + dx
        coords.Y = current_y + dy
        coords.MaxRetry = 2
        PathFinding.Go(coords)
        Misc.Pause(PAUSE_DURATION // 2)
        
        if abs(Player.Position.X - x) <= MAX_DISTANCE and abs(Player.Position.Y - y) <= MAX_DISTANCE:
            return True
    
    return False

def gotoLocation(x, y, max_retries=5):
    """Attempt to move to location with retries."""
    attempts = 0
    while attempts < max_retries:
        # Try direct path first
        coords = PathFinding.Route()
        coords.X = x
        coords.Y = y
        coords.MaxRetry = 3
        PathFinding.Go(coords)
        Misc.Pause(PAUSE_DURATION)
        
        # Check if we reached the target
        if abs(Player.Position.X - x) <= MAX_DISTANCE and abs(Player.Position.Y - y) <= MAX_DISTANCE:
            return True
        
        # If direct path failed, try moving to adjacent positions
        if attempts < max_retries - 1:
            if try_random_position(x, y):
                return True
        
        attempts += 1
        if attempts < max_retries:
            Misc.Pause(PAUSE_DURATION // 2)
    
    return False

def place_items_at_points(points, center_x, center_y, placed_positions, item_id, max_failures=3):
    """Place items at the specified points."""
    failures = 0
    
    for x, y in points:
        # Skip if position is already occupied
        if (x, y) in placed_positions:
            continue
            
        # Find item with retry
        if not find_item_with_retry(item_id):
            failures += 1
            if failures >= max_failures:
                Misc.SendMessage(f"Failed to find item {item_id} too many times, skipping remaining placements", 33)
                return False
            continue
        
        # Try to move to position
        if not gotoLocation(x, y):
            failures += 1
            if failures >= max_failures:
                Misc.SendMessage(f"Failed to reach positions too many times, skipping remaining placements", 33)
                return False
            continue
        
        # Place item
        item = Items.FindByID(item_id, -1, Player.Backpack.Serial)
        if item:
            Items.MoveOnGround(item.Serial, 1, x, y, Player.Position.Z)
            Misc.Pause(PAUSE_DURATION)
            placed_positions.add((x, y))
    
    return True

def place_secondary_circles(center_x, center_y, max_failures=3):
    """Place secondary circles at star points, allowing overlap."""
    points = generate_secondary_points(center_x, center_y)
    failures = 0
    
    for x, y in points:
        # Find item with retry
        if not find_item_with_retry(SECONDARY_ITEM_ID):
            failures += 1
            if failures >= max_failures:
                Misc.SendMessage(f"Failed to find item {SECONDARY_ITEM_ID} too many times, skipping remaining placements", 33)
                return False
            continue
        
        # Try to move to position
        if not gotoLocation(x, y):
            failures += 1
            if failures >= max_failures:
                Misc.SendMessage(f"Failed to reach positions too many times, skipping remaining placements", 33)
                return False
            continue
        
        # Place item
        item = Items.FindByID(SECONDARY_ITEM_ID, -1, Player.Backpack.Serial)
        if item:
            Items.MoveOnGround(item.Serial, 1, x, y, Player.Position.Z)
            Misc.Pause(PAUSE_DURATION)
    
    return True

def place_and_light_candle(x, y, max_retries=3):
    """Place and immediately light a candle at the specified position."""
    # Try to move to position
    if not gotoLocation(x, y):
        return False
        
    # Find and place candle
    if not find_item_with_retry(CANDLE_ID):
        return False
        
    item = Items.FindByID(CANDLE_ID, -1, Player.Backpack.Serial)
    if not item:
        return False
        
    Items.MoveOnGround(item.Serial, 1, x, y, Player.Position.Z)
    Misc.Pause(PAUSE_DURATION // 2)
    
    # Light the candle immediately
    candle = Items.FindByID(CANDLE_ID, -1, -1, x, y)
    if candle:
        Items.UseItem(candle)
        Misc.Pause(PAUSE_DURATION // 2)
        return True
    
    return False

def place_and_light_candles(center_x, center_y, placed_positions, max_failures=3):
    """Place and light candles in a circle."""
    Misc.SendMessage("Creating and lighting candle circle...", 65)
    
    # Get candle points - centered on pentagram
    candle_points = generate_candle_points(center_x, center_y)
    failures = 0
    
    for x, y in candle_points:
        if not place_and_light_candle(x, y):
            failures += 1
            if failures >= max_failures:
                Misc.SendMessage("Failed to place/light too many candles, skipping remaining", 33)
                return False
    
    return True

def generate_star_points(center_x, center_y):
    """Generate points for pentagram star."""
    points = []
    angle_step = 2 * math.pi / NUM_POINTS
    
    # Calculate vertex points
    vertices = []
    for i in range(NUM_POINTS):
        angle = i * angle_step + math.radians(ROTATION_ANGLE)
        x = center_x + int(MAIN_RADIUS * math.cos(angle))
        y = center_y + int(MAIN_RADIUS * math.sin(angle))
        vertices.append((x, y))
    
    # Generate star pattern
    for i in range(NUM_POINTS):
        start = vertices[i]
        end = vertices[(i + 2) % NUM_POINTS]  # Connect to point 2 steps ahead
        
        # Generate points along the line
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        steps = max(abs(dx), abs(dy))
        
        if steps > 0:
            for step in range(steps + 1):
                x = start[0] + dx * step // steps
                y = start[1] + dy * step // steps
                points.append((x, y))
    
    return points

def generate_circle_points(center_x, center_y, radius):
    """Generate points for a circle."""
    points = []
    steps = int(radius * 8)  # More steps for smoother circle
    
    for i in range(steps):
        angle = 2 * math.pi * i / steps
        x = center_x + int(radius * math.cos(angle))
        y = center_y + int(radius * math.sin(angle))
        points.append((x, y))
    
    return points

def generate_secondary_points(center_x, center_y):
    """Generate points for secondary circles at star points."""
    points = []
    angle_step = 2 * math.pi / NUM_POINTS
    
    # For each star point
    for i in range(NUM_POINTS):
        angle = i * angle_step + math.radians(ROTATION_ANGLE)
        point_x = center_x + int(MAIN_RADIUS * math.cos(angle))
        point_y = center_y + int(MAIN_RADIUS * math.sin(angle))
        
        # Add circle points around this point
        circle_points = generate_circle_points(point_x, point_y, SECONDARY_RADIUS)
        points.extend(circle_points)
    
    return points

def generate_candle_points(center_x, center_y):
    """Generate points for candle circle."""
    candle_radius = MAIN_RADIUS + 1  # Closer to the pentagram
    points = []
    
    # Place candles at points of larger circle
    for i in range(NUM_POINTS):
        angle = i * (2 * math.pi / NUM_POINTS) + math.radians(ROTATION_ANGLE)
        x = center_x + int(candle_radius * math.cos(angle))
        y = center_y + int(candle_radius * math.sin(angle))
        points.append((x, y))
    
    return points

def complete_ritual(center_x, center_y):
    """Complete the ritual by returning to center."""
    Misc.SendMessage("Completing ritual...", 65)
    gotoLocation(center_x, center_y)
    Misc.SendMessage("Ritual complete!", 65)

def main():
    """Main ritual function."""
    try:
        # Get player position for center
        center_x = Player.Position.X
        center_y = Player.Position.Y
        
        # Track all placed positions (except for secondary circles which can overlap)
        placed_positions = set()
        
        # Place pentagram star
        if PLACE_STAR:
            Misc.SendMessage("Creating pentagram star...", 65)
            star_points = generate_star_points(center_x, center_y)
            place_items_at_points(star_points, center_x, center_y, placed_positions, STAR_ITEM_ID)
            Misc.Pause(PAUSE_DURATION)
        
        # Place main circle
        if PLACE_CIRCLE:
            Misc.SendMessage("Creating main circle...", 65)
            circle_points = generate_circle_points(center_x, center_y, MAIN_RADIUS)
            place_items_at_points(circle_points, center_x, center_y, placed_positions, CIRCLE_ITEM_ID)
            Misc.Pause(PAUSE_DURATION)
        
        # Place secondary circles (allowing overlap)
        if PLACE_SECONDARY:
            Misc.SendMessage("Creating secondary circles...", 65)
            place_secondary_circles(center_x, center_y)
            Misc.Pause(PAUSE_DURATION)
        
        # Place overlay items
        if PLACE_OVERLAY:
            Misc.SendMessage("Adding overlay items...", 65)
            if PLACE_STAR:
                place_items_at_points(star_points, center_x, center_y, placed_positions, OVERLAY_ITEM_ID)
            if PLACE_CIRCLE:
                place_items_at_points(circle_points, center_x, center_y, placed_positions, OVERLAY_ITEM_ID)
            Misc.Pause(PAUSE_DURATION)
        
        # Place and light candles
        if PLACE_CANDLES:
            place_and_light_candles(center_x, center_y, placed_positions)
        
        # Complete ritual by returning to center
        complete_ritual(center_x, center_y)
        return True
        
    except Exception as e:
        Misc.SendMessage(f"Error in ritual: {str(e)}", 33)
        return False

if __name__ == '__main__':
    main()
