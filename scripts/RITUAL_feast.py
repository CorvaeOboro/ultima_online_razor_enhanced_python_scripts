"""
Ritual Feast Generator - A Razor Enhanced Python script for Ultima Online

Creates a Ritual radial pattern using food items, centered around a roast pig.
Placing them in the world from the starting position 
A bountiful feast for all !

Pattern Components:
1. Centerpiece: Roast Pig
2. Inner Circle: Cooked Birds in a  circle
3. Inner Petals: Apples and cabbage alternating
4. Outer Ring: Lettuce forming a natural border
5. Connecting Points: Grapes at key intersections
6. Accent Points: Onions at cardinal directions

VERSION = 20250621
"""

import sys
import math
from System.Collections.Generic import List
import datetime

# Phase toggles for each component
PLACE_COMPONENTS = {
    "A_centerpiece": True,   # Central roast pig
    "B_inner_circle": True,  # Circle of cooked birds
    "C_petals_1": True,     # Apple petals
    "D_petals_2": True,     # Cabbage petals
    "E_outer_ring": True,   # Lettuce border
    "F_intersect": True,    # Grape intersections
    "G_accents": True       # Onion accents
}

# Component Configuration
FEAST_CONFIG = {
    "A_centerpiece": {
        "item_id": 0x09BB,  # Roast Pig
        "radius": 0,
        "points": 1,
        "pattern": "center"
    },
    "B_inner_circle": {
        "item_id": 0x09B7,  # Cooked Bird
        "radius": 2,
        "points": 8,
        "pattern": "circle"
    },
    "C_petals_1": {
        "item_id": 0x09D0,  # Apple
        "radius": 3,
        "points": 16,
        "pattern": "circle"
    },
    "D_petals_2": {
        "item_id": 0x0C7B,  # Cabbage
        "radius": 4,
        "points": 20,
        "pattern": "circle",
        "rotation": 0
    },
    "E_outer_ring": {
        "item_id": 0x0C70,  # Lettuce
        "radius": 5,
        "points": 20,
        "pattern": "circle"
    },
    "F_intersect": {
        "item_id": 0x09D1,  # Grapes
        "radius": 5,
        "points": 4,
        "pattern": "circle",
        "rotation": 45
    },
    "G_accents": {
        "item_id": 0x0C6D,  # Onion
        "radius": 3,
        "points": 4,
        "pattern": "cardinal"
    }
}

# Constants
PAUSE_DURATION = 500       # General pause between actions
PAUSE_DURATION_PLACE = 800  # Pause after placing item
MAX_DISTANCE = 2
PATHFINDING_RETRY = 3

def generate_circle_points(center_x, center_y, radius, points, rotation=0):
    """Generate points in a circle with optional rotation"""
    result = []
    for i in range(points):
        angle = math.radians(rotation + (360.0 * i / points))
        x = center_x + int(radius * math.cos(angle))
        y = center_y + int(radius * math.sin(angle))
        result.append((x, y))
    return result

def generate_cardinal_points(center_x, center_y, radius):
    """Generate points at cardinal directions"""
    return [
        (center_x, center_y - radius),  # North
        (center_x + radius, center_y),  # East
        (center_x, center_y + radius),  # South
        (center_x - radius, center_y)   # West
    ]

def is_valid_position(x, y, z=None):
    """Check if a position is valid for item placement"""
    if z is None:
        z = Player.Position.Z
        
    return (
        Player.Position.X - MAX_DISTANCE <= x <= Player.Position.X + MAX_DISTANCE
        and Player.Position.Y - MAX_DISTANCE <= y <= Player.Position.Y + MAX_DISTANCE
        and Statics.GetLandID(x, y, Player.Map) not in [0x0001]
    )

def find_item_with_retry(item_id, max_retries=3, retry_delay=500):
    """Find an item in backpack with retries"""
    for _ in range(max_retries):
        found = Items.FindByID(item_id, -1, Player.Backpack.Serial)
        if found:
            return found
        Misc.Pause(retry_delay)
    return None

def place_item(x, y, item_id, z=None):
    """Place a single item with verification"""
    if not is_valid_position(x, y, z):
        return False
        
    # Find a new item each time
    item = Items.FindByID(item_id, -1, Player.Backpack.Serial)
    if not item:
        Misc.SendMessage(f"Could not find item 0x{item_id:X}", 33)
        return False
    
    # Get initial count
    initial_count = Items.BackpackCount(item_id, -1)
    if initial_count <= 0:
        return False
        
    # Try to place item
    Items.MoveOnGround(item, 1, x, y, z if z is not None else Player.Position.Z)
    Misc.Pause(PAUSE_DURATION_PLACE)
    
    # Verify placement with multiple checks
    for _ in range(2):
        new_count = Items.BackpackCount(item_id, -1)
        if new_count < initial_count:
            return True
        Misc.Pause(PAUSE_DURATION)
    
    return False

def place_items_at_points(points, item_id, z=None, progress_msg="Placing items"):
    """Place items at points with progress tracking"""
    if not points:
        return set()
        
    total = len(points)
    placed = set()
    
    for i, (x, y) in enumerate(points, 1):
        Misc.SendMessage(f"{progress_msg}: {i}/{total}", 67)
        
        # Try to get in range - convert coordinates to string for goto_location
        if not goto_location_with_wiggle(str(x), str(y)):
            Misc.SendMessage(f"Could not reach position ({x}, {y})", 33)
            continue
        
        # Try placement up to 2 times
        for attempt in range(2):
            if place_item(x, y, item_id, z):
                placed.add((x, y))
                break
            if attempt < 1:  # Only pause between attempts, not after last attempt
                Misc.Pause(PAUSE_DURATION)
                
    return placed

def get_direction(from_x, from_y, to_x, to_y):
    """Calculate direction from one point to another"""
    dx = to_x - from_x
    dy = to_y - from_y
    
    # Convert to direction value (0-7)
    # N=0, NE=1, E=2, SE=3, S=4, SW=5, W=6, NW=7
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
    # Convert to float for calculations
    target_x = float(x)
    target_y = float(y)
    
    for _ in range(max_retries):
        if (abs(Player.Position.X - target_x) <= MAX_DISTANCE and 
            abs(Player.Position.Y - target_y) <= MAX_DISTANCE):
            return True
            
        # Try to move closer - convert to int for PathFindTo
        Player.PathFindTo(int(target_x), int(target_y), Player.Position.Z)
        Misc.Pause(500)
        
        # If still not in range, try to walk directly
        if not (abs(Player.Position.X - target_x) <= MAX_DISTANCE and 
                abs(Player.Position.Y - target_y) <= MAX_DISTANCE):
            direction = get_direction(Player.Position.X, Player.Position.Y, target_x, target_y)
            Player.Walk(direction)
            Misc.Pause(200)
    
    return False

def place_pattern_component(center_x, center_y, config, z=None):
    """Place a single item component"""
    points = []
    if config["pattern"] == "circle":
        points = generate_circle_points(
            center_x, 
            center_y, 
            config["radius"], 
            config["points"],
            config.get("rotation", 0)
        )
    elif config["pattern"] == "cardinal":
        points = generate_cardinal_points(center_x, center_y, config["radius"])
    elif config["pattern"] == "center":
        points = [(center_x, center_y)]
        
    return place_items_at_points(
        points, 
        config["item_id"], 
        z,
        f"Placing {get_item_name(config['item_id'])}"
    )

def get_item_name(item_id):
    """Get readable name for item ID"""
    for component in FEAST_CONFIG.values():
        if component["item_id"] == item_id:
            return component.get("name", f"Item 0x{item_id:X}")
    return f"Item 0x{item_id:X}"

def display_configuration():
    """Display active feast configuration"""
    Misc.SendMessage("Current Feast Configuration:", 67)
    for phase, active in PLACE_COMPONENTS.items():
        if phase in FEAST_CONFIG:
            config = FEAST_CONFIG[phase]
            status = "ACTIVE" if active else "DISABLED"
            Misc.SendMessage(
                f"{phase}: {get_item_name(config['item_id'])} - {status}",
                68 if active else 33
            )

def calculate_item_totals():
    """Calculate and display required items"""
    totals = {}
    
    for phase, config in FEAST_CONFIG.items():
        if not PLACE_COMPONENTS[phase]:
            continue
            
        item_id = config["item_id"]
        if item_id not in totals:
            totals[item_id] = 0
            
        if config["pattern"] == "center":
            totals[item_id] += 1
        elif config["pattern"] == "cardinal":
            totals[item_id] += 4
        else:
            totals[item_id] += config["points"]
            
    Misc.SendMessage("\nRequired Items:", 67)
    for item_id, count in totals.items():
        name = get_item_name(item_id)
        have = Items.BackpackCount(item_id, -1)
        status = "OK" if have >= count else "MISSING"
        color = 68 if have >= count else 33
        Misc.SendMessage(f"{name}: Need {count}, Have {have} - {status}", color)

def create_feast(center_x, center_y):
    """Create the feast pattern"""
    Misc.SendMessage("Beginning feast ritual...", 67)
    
    # Get center Z coordinate once
    center_z = Player.Position.Z
    
    # First try to reach the center
    if not goto_location_with_wiggle(center_x, center_y):
        Misc.SendMessage("Could not reach center position!", 33)
        return
    
    # Place each component if enabled
    for phase, config in FEAST_CONFIG.items():
        if not PLACE_COMPONENTS[phase]:
            continue
            
        placed = place_pattern_component(center_x, center_y, config, center_z)
        Misc.SendMessage(
            f"Placed {len(placed)} items for {phase}",
            68 if placed else 33
        )
        
    Misc.SendMessage("Feast ritual complete!", 67)

def main():
    """Main function"""

    # Display configuration
    display_configuration()
    
    # Calculate and verify items
    calculate_item_totals()
    
    # Use player's current position as center
    center_x = Player.Position.X
    center_y = Player.Position.Y
    
    create_feast(center_x, center_y)

if __name__ == "__main__":
    main()
