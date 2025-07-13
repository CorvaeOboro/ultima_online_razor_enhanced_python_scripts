"""
Ritual of the Circle - A Razor Enhanced Python script for Ultima Online

Places an expanded ritual pattern with multiple circles and shapes forming mandala like patterns:

1. Main Circle Pattern:
   - Circle 1: 4 points (radius 1)
   - Circle 2: 12 points (radius 2)
   - Circle 3: 16 points (radius 3)
   - Circle 4: 24 points (radius 4)

2. Additional Components:
   - Overlay Items: Secondary items placed on circle points
   - Amethyst Circle: 4 points in cardinal directions radius 3
   - Sapphire Circle: 4 points in diagonal directions radius 3
   - Candle Circle: 4 points in a circle larger than circle 4
   - Middle Circle: Large diamond pattern
   - Middle Lantern Circle: 4 lanterns in diamond corner

3. Outer Components:
    - 8 circles of radius 4 offset from the center , at their centers another lantern , around them is a radius 6 circle 
    - the outermost circle around the the whole ritual is a 2 layer round circle of blackpearl and eye of newt

3. Phase Control:
   - Each component can be toggled independently
   - Failures in one component do not stop the ritual

Current Items 
Lettuce , Cabbage 
Eye of newt 
Black pearl , nightshade

for UOR Britain location , a large open area with the moongate at center , 

VERSION = 20250621
"""

import math
from System.Collections.Generic import List
import datetime

# Phase toggles 
PLACE_COMPONENTS = {
    "A_gem_4": True,        # Amethyst circle
    "B_gem_4": True,        # Sapphire circle
    "C_base_4": True,       # First base circle
    "D_base_5": True,       # Second base circle
    "E_base_6": True,       # Third base circle
    "F_base_7": True,       # Fourth base circle
    "G_overlay_6": True,    # First overlay circle
    "H_overlay_7": True,    # Second overlay circle
    "I_middle_8": True,     # Middle diamond pattern
    "J_middle_9": True,     # Middle circle pattern
    "K_middle_4": True,     # Middle lantern circle
    "V_outer_4": True,       # Inner circle instances
    "W_outer_6": True,       # Outer circle instances
    "X_outer_0": True,       # Center lantern instances
    "Y_final_12": True,     # Inner final ring
    "Z_final_13": True      # Outer final ring
}
# Component Configuration
RITUAL_CONFIG = {
    # Inner gem circles (4 points each)
    "A_gem_4": {
        "item_id": 0x0F85,  # Amethyst
        "radius": 3,
        "points": 4,
        "pattern": "diagonal"
    },
    "B_gem_4": {
        "item_id": 0x0F86,  # Sapphire
        "radius": 3,
        "points": 4,
        "pattern": "diagonal"
    },
    
    # Base circles (concentric)
    "C_base_4": {
        "item_id": 0x0F7B,  # Lettuce
        "radius": 4,
        "pattern": "circle"
    },
    "D_base_5": {
        "item_id": 0x0F7B,  # Cabbage
        "radius": 5,
        "pattern": "circle"
    },
    "E_base_6": {
        "item_id": 0x0F7B,  # Lettuce
        "radius": 6,
        "pattern": "circle"
    },
    "F_base_7": {
        "item_id": 0x0F7B,  # Cabbage
        "radius": 7,
        "pattern": "circle"
    },
    
    # Overlay circles
    "G_overlay_6": {
        "item_id": 0x0994,  # (UOR) Pear 0x0994  or (AOS)Nox crystal 0x0F8E
        "radius": 6,
        "pattern": "circle"
    },
    "H_overlay_7": {
        "item_id": 0x0F88,  # Nightshade
        "radius": 7,
        "pattern": "circle"
    },
    
    # Middle Circle (diamond pattern)
    "I_middle_8": {
        "item_id": 0x0F7A,  # Black Pearl
        "radius": 8,
        "points": 8,
        "pattern": "diamond"
    },
    "J_middle_9": {
        "item_id": 0x0F7A,  # Black Pearl
        "radius": 9,
        "pattern": "circle"
    },

    # Lanterns
    "K_middle_4": {
        "item_id": 0x0A25,  # Lantern
        "radius": 7,
        "points": 4,
        "pattern": "circle"
    },
    
    # Outer component circles (8 instances)
    "V_outer_4": {
        "item_id": 0x0F87,  # Eye of Newt
        "radius": 2,
        "center_radius": 11,  # Distance of instances from main center
        "instances": 8,      # Number of instances around the center
        "pattern": "instanced_circles",
        "rotation": 22.5     # (360/8)/2 degrees rotation for offset
    },
    "W_outer_6": {
        "item_id": 0x0F88,  # Nightshade
        "radius": 3,
        "center_radius": 11,  # Distance of instances from main center
        "instances": 8,      # Number of instances around the center
        "pattern": "instanced_circles",
        "rotation": 22.5     # (360/8)/2 degrees rotation for offset
    },
    "X_outer_0": {
        "item_id": 0x0A25,  # Lantern
        "radius": 0,        # Single point at each instance center
        "center_radius": 11, # Distance of instances from main center
        "instances": 8,     # Number of instances around the center
        "pattern": "instanced_points",
        "rotation": 22.5     # (360/8)/2 degrees rotation for offset
    },
    
    # Final outer rings
    "Y_final_12": {
        "item_id": 0x0F7A,  # Black Pearl
        "radius": 16,
        "pattern": "circle"
    },
    "Z_final_13": {
        "item_id": 0x0F88,  # Nightshade
        "radius": 17,
        "pattern": "circle"
    }
}

# Constants (simplified, since most are now in config)
CIRCLE_SPACING = 1  # Tiles between each circle
PAUSE_DURATION = 600  # Pause between actions
PAUSE_DURATION_SHORT = 400
PAUSE_DURATION_PLACE = 700

# Item IDs
# Main circle items
ITEM_CIRCLE_A_ID = 0x0C70  # Lettuce
ITEM_CIRCLE_B_ID = 0x0C7B  # Cabbage
BLACKPEARL_ID = 0x0F7A  # Black Pearl
EYE_OF_NEWT_ID = 0x0F87  # Eye of Newt for outer ring

# Overlay items
ITEM_OVERLAY_A_ID = 0x0994  # (UOR) Pear 0x0994  or (AOS)Nox crystal 0x0F8E
ITEM_OVERLAY_B_ID = 0x0F88  # Nightshade

# Filler item
ITEM_FILLER_ID = 0x0994  # (UOR) Pear 0x0994  or (AOS)Nox crystal 0x0F8E

# Additional component items
AMETHYST_ID = 0x0F16  # Amethyst
SAPPHIRE_ID = 0x0F11  # Sapphire
CANDLE_ID = 0x0A25  # Candle =  0x0A28 , Lantern = 0x0A25

# Timing constants
MAX_DISTANCE = 1  # Maximum distance for placement - must be close to place items
PATHFINDING_RETRY = 3  # Number of retries for movement
MOVE_RETRY_PAUSE = 500  # Shorter pause for retrying movement

#//==================================================================

class ItemCache:
    """Cache for item information to reduce client load."""
    def __init__(self):
        self.item_counts = {}  # item_id -> count
        self.item_serials = {}  # item_id -> list of serials
        self.last_update = None
        self.update_interval = 5000  # 5 seconds between full updates
    
    def update_if_needed(self):
        """Update cache if interval has passed."""
        current_time = datetime.datetime.now()
        if (self.last_update is None or 
            (current_time - self.last_update).total_seconds() * 1000 >= self.update_interval):
            self.full_update()
    
    def full_update(self):
        """Do a full cache update."""
        self.item_counts.clear()
        self.item_serials.clear()
        
        # Scan backpack once
        items = Items.FindBySerial(Player.Backpack.Serial).Contains
        if items:
            for item in items:
                item_id = item.ItemID
                # Update counts
                self.item_counts[item_id] = self.item_counts.get(item_id, 0) + 1
                # Update serials
                if item_id not in self.item_serials:
                    self.item_serials[item_id] = []
                self.item_serials[item_id].append(item.Serial)
        
        self.last_update = datetime.datetime.now()
    
    def get_count(self, item_id):
        """Get cached count for item_id."""
        self.update_if_needed()
        return self.item_counts.get(item_id, 0)
    
    def get_next_serial(self, item_id):
        """Get next available serial for item_id."""
        self.update_if_needed()
        serials = self.item_serials.get(item_id, [])
        if not serials:
            return None
        return serials.pop(0)  # Remove and return first serial
    
    def decrement_count(self, item_id):
        """Decrement count for item_id after successful placement."""
        if item_id in self.item_counts:
            self.item_counts[item_id] = max(0, self.item_counts[item_id] - 1)

# Global item cache
ITEM_CACHE = ItemCache()

def is_valid_position(x, y, z=None):
    """Check if a position is valid for item placement."""
    try:
        # Check if tile is walkable (not water/blocked)
        land_id = Statics.GetLandID(x, y, Player.Map)
        if land_id >= 0x00A8 and land_id <= 0x00AB:  # Water tiles
            return False
            
        # Check for static tiles that might block
        statics = Statics.GetStaticsTileInfo(x, y, Player.Map)
        if statics and any(s.StaticID >= 0x4000 for s in statics):  # Unwalkable statics
            return False
            
        return True
    except:
        return False

def place_item(point_x, point_y, item_id, z=None):
    """Place a single item at the specified coordinates with verification.
    Returns True if placement was successful."""
    max_retries = 3
    base_delay = PAUSE_DURATION  # 600ms base delay
    move_attempts = 0
    max_move_attempts = 3  # Maximum attempts to reach position
    
    if z is None:
        z = Player.Position.Z
    
    # First check if position is valid
    if not is_valid_position(point_x, point_y):
        Misc.SendMessage(f"Warning: Invalid position at ({point_x}, {point_y}), skipping...", 33)
        return False
    
    # Check cached item count first, retry if empty
    cache_retry_attempts = 3
    for cache_try in range(cache_retry_attempts):
        if ITEM_CACHE.get_count(item_id) > 0:
            break
        Misc.SendMessage(f"Warning: No items of type {hex(item_id)} found in cache (attempt {cache_try+1}/{cache_retry_attempts})", 33)
        ITEM_CACHE.full_update()
        Misc.Pause(PAUSE_DURATION * 2)  # Wait longer to allow for restock or pickup
    else:
        Misc.SendMessage(f"Error: Still no items of type {hex(item_id)} after {cache_retry_attempts} cache updates. Skipping point.", 33)
        return False
    
    for attempt in range(max_retries):
        try:
            # Check if we're close enough - must be within 1 tile
            while abs(Player.Position.X - point_x) > 1 or abs(Player.Position.Y - point_y) > 1:
                if move_attempts >= max_move_attempts:
                    Misc.SendMessage(f"Warning: Failed to reach position ({point_x}, {point_y}) after {max_move_attempts} attempts", 33)
                    return False
                    
                if not gotoLocation(point_x, point_y):
                    Misc.SendMessage(f"Movement failed, attempt {move_attempts + 1}/{max_move_attempts}", 33)
                    move_attempts += 1
                    Misc.Pause(MOVE_RETRY_PAUSE)
                    continue
                
                # Extra pause after movement to ensure server sync
                Misc.Pause(300)
            
            # Get item serial from cache
            item_serial = ITEM_CACHE.get_next_serial(item_id)
            if not item_serial:
                if attempt == max_retries - 1:
                    Misc.SendMessage(f"Warning: No more items of type {hex(item_id)} available", 33)
                ITEM_CACHE.full_update()  # Force cache update on failure
                Misc.Pause(base_delay)
                continue
            
            # Attempt placement with timeout
            placement_start = datetime.datetime.now()
            Items.MoveOnGround(item_serial, 1, point_x, point_y, z)
            Misc.Pause(PAUSE_DURATION_PLACE)
            
            # Check if placement took too long
            placement_time = (datetime.datetime.now() - placement_start).total_seconds()
            if placement_time > 2.0:  # If placement takes more than 2 seconds
                Misc.SendMessage(f"Warning: Placement timed out at ({point_x}, {point_y})", 33)
                return False
            
            # Update cache after successful placement
            ITEM_CACHE.decrement_count(item_id)
            return True
            
        except Exception as e:
            Misc.SendMessage(f"Warning: Error placing item: {str(e)}", 33)
            Misc.Pause(base_delay)
            continue
    
    return False

def generate_circle_concentric_points(center_x, center_y, radius, _, circle_num):
    """Generate points for a circle with given radius.
    Creates thick, diamond-shaped circles rotated 45 degrees."""
    points = []
    
    if radius == 1:
        # First circle: Diamond (4 points at diagonals)
        points = [
            (center_x + 1, center_y - 1),  # NE
            (center_x + 1, center_y + 1),  # SE
            (center_x - 1, center_y + 1),  # SW
            (center_x - 1, center_y - 1),  # NW
        ]
    elif radius == 2:
        # Second circle: Rotated octagon (12 points)
        points = [
            (center_x + 2, center_y - 1),  # ENE
            (center_x + 2, center_y),      # E
            (center_x + 2, center_y + 1),  # ESE
            (center_x + 1, center_y + 2),  # SSE
            (center_x, center_y + 2),      # S
            (center_x - 1, center_y + 2),  # SSW
            (center_x - 2, center_y + 1),  # WSW
            (center_x - 2, center_y),      # W
            (center_x - 2, center_y - 1),  # WNW
            (center_x - 1, center_y - 2),  # NNW
            (center_x, center_y - 2),      # N
            (center_x + 1, center_y - 2),  # NNE
        ]
    elif radius == 3:
        # Third circle: Thicker diamond (16 points)
        points = [
            # East quadrant
            (center_x + 3, center_y - 2),
            (center_x + 3, center_y - 1),
            (center_x + 3, center_y),
            (center_x + 3, center_y + 1),
            (center_x + 3, center_y + 2),
            # Southeast quadrant
            (center_x + 2, center_y + 3),
            (center_x + 1, center_y + 3),
            (center_x, center_y + 3),
            # Southwest quadrant
            (center_x - 1, center_y + 3),
            (center_x - 2, center_y + 3),
            # West quadrant
            (center_x - 3, center_y + 2),
            (center_x - 3, center_y + 1),
            (center_x - 3, center_y),
            (center_x - 3, center_y - 1),
            (center_x - 3, center_y - 2),
            # Northwest quadrant
            (center_x - 2, center_y - 3),
            (center_x - 1, center_y - 3),
            (center_x, center_y - 3),
            # Northeast quadrant
            (center_x + 1, center_y - 3),
            (center_x + 2, center_y - 3),
        ]
    else:
        # Fourth circle: Thick diamond (24 points)
        points = [
            # East quadrant
            (center_x + 4, center_y - 2),
            (center_x + 4, center_y - 1),
            (center_x + 4, center_y),
            (center_x + 4, center_y + 1),
            (center_x + 4, center_y + 2),
            # Southeast quadrant
            (center_x + 3, center_y + 3),
            (center_x + 2, center_y + 4),
            (center_x + 1, center_y + 4),
            (center_x, center_y + 4),
            # Southwest quadrant
            (center_x - 1, center_y + 4),
            (center_x - 2, center_y + 4),
            (center_x - 3, center_y + 3),
            # West quadrant
            (center_x - 4, center_y + 2),
            (center_x - 4, center_y + 1),
            (center_x - 4, center_y),
            (center_x - 4, center_y - 1),
            (center_x - 4, center_y - 2),
            # Northwest quadrant
            (center_x - 3, center_y - 3),
            (center_x - 2, center_y - 4),
            (center_x - 1, center_y - 4),
            (center_x, center_y - 4),
            # Northeast quadrant
            (center_x + 1, center_y - 4),
            (center_x + 2, center_y - 4),
            (center_x + 3, center_y - 3),
        ]
    
    return points

def generate_core_4_points(center_x, center_y):
    """Generate points for amethyst circle (larger than circle 2)."""
    radius = 2.5  # Between circle 2 (r=2) and circle 3 (r=3)
    points = [
        (center_x + 3, center_y),      # East
        (center_x, center_y + 3),      # South
        (center_x - 3, center_y),      # West
        (center_x, center_y - 3),      # North
    ]
    return points

def generate_core_4_points_alt(center_x, center_y):
    """Generate points for sapphire circle (rotated 45 degrees from amethyst)."""
    radius = 3  # Same radius as amethyst circle
    points = [
        (center_x + 2, center_y - 2),  # Northeast
        (center_x + 2, center_y + 2),  # Southeast
        (center_x - 2, center_y + 2),  # Southwest
        (center_x - 2, center_y - 2),  # Northwest
    ]
    return points

def generate_candle_points(center_x, center_y):
    """Generate points for candle circle (larger than circle 4)."""
    points = [
        (center_x + 5, center_y),      # East
        (center_x, center_y + 5),      # South
        (center_x - 5, center_y),      # West
        (center_x, center_y - 5),      # North
    ]
    return points

def generate_blackpearl_points(center_x, center_y):
    """Generate points for black pearl circles (radius 7 and 9)."""
    points_r7 = []
    points_r9 = []
    
    # Helper function to generate points in clockwise order
    def generate_circle_points(radius):
        circle_points = []
        
        # Start from east (0 degrees) and go clockwise
        for angle in range(0, 360, 5):  # 5 degree steps for smooth circle
            # Convert angle to radians
            rad = math.radians(angle)
            # Calculate point on circle_highres circle
            circle_highres_x = radius * math.cos(rad)
            circle_highres_y = radius * math.sin(rad)
            # Round to nearest integer for game grid
            x = int(round(circle_highres_x))
            y = int(round(circle_highres_y))
            # Add point if it's not too close to previous point
            point = (center_x + x, center_y + y)
            if not circle_points or point != circle_points[-1]:
                circle_points.append(point)
        
        return circle_points
    
    # Generate points for both circles in clockwise order
    points_r7 = generate_circle_points(7)
    points_r9 = generate_circle_points(9)
    
    # Return points with inner circle first, then outer circle
    return points_r7 + points_r9

def get_all_ritual_points(center_x, center_y):
    """Generate all points that will be used in the ritual pattern."""
    used_points = set()
    
    # Get base circle points
    for circle_num in range(4):
        radius = circle_num + 1
        points = generate_circle_concentric_points(center_x, center_y, radius, CIRCLE_SPACING, circle_num)
        used_points.update(points)
    
    # Add amethyst points
    amethyst_points = generate_core_4_points(center_x, center_y)
    used_points.update(amethyst_points)
    
    # Add sapphire points
    sapphire_points = generate_core_4_points_alt(center_x, center_y)
    used_points.update(sapphire_points)
    
    # Add candle points
    candle_points = generate_candle_points(center_x, center_y)
    used_points.update(candle_points)
    
    # Add black pearl points
    blackpearl_points = generate_blackpearl_points(center_x, center_y)
    used_points.update(blackpearl_points)
    
    return used_points

def get_grid_points(center_x, center_y, radius=4):
    """Generate all valid grid points within the ritual area."""
    points = set()
    # Only generate points within the diamond shape of the ritual
    for x in range(center_x - radius, center_x + radius + 1):
        for y in range(center_y - radius, center_y + radius + 1):
            # Check if point is within diamond shape and not too close to center
            manhattan_dist = abs(x - center_x) + abs(y - center_y)
            if manhattan_dist <= radius and manhattan_dist > 1:  # Exclude center and immediate adjacents
                points.add((x, y))
    return points

def find_item_with_retry(item_id, max_retries=3, retry_delay=500):
    """Find an item in backpack with retries and delay."""
    for attempt in range(max_retries):
        item = Items.FindByID(item_id, -1, Player.Backpack.Serial)
        if item and item.Serial:  # Verify we have a valid item with serial
            return item
            
        if attempt < max_retries - 1:
            Misc.SendMessage(f"Item {hex(item_id)} not found, retrying... ({attempt + 1}/{max_retries})", 33)
            Misc.Pause(retry_delay)
    
    Misc.SendMessage(f"Failed to find item {hex(item_id)} after {max_retries} attempts", 33)
    return None

def place_items_at_points(points, item_id, z=None, progress_msg="Placing items"):
    """Place items at the specified points with progress tracking.
    Returns the set of successfully placed positions."""
    placed_positions = set()
    points_placed = 0
    total_points = len(points)
    
    # First check if we have enough items
    available_items = ITEM_CACHE.get_count(item_id)
    if available_items < total_points:
        Misc.SendMessage(f"Warning: Not enough items for this pattern. Have {available_items}, need {total_points}. Skipping this pattern.", 33)
        return set()
    
    Misc.SendMessage(f"{progress_msg}... (0/{total_points})", 68)
    for point_x, point_y in points:
        try:
            if place_item(point_x, point_y, item_id, z):
                placed_positions.add((point_x, point_y))
                points_placed += 1
                if points_placed % 5 == 0 or points_placed == total_points:
                    Misc.SendMessage(f"{progress_msg}... ({points_placed}/{total_points})", 68)
            else:
                Misc.SendMessage(f"Warning: Failed to place item at ({point_x}, {point_y})", 33)
            
            # Throttle between placements to prevent client overload
            Misc.Pause(500)
            
        except Exception as e:
            Misc.SendMessage(f"Warning: Error placing item at ({point_x}, {point_y}): {str(e)}", 33)
            continue
    
    if points_placed < total_points:
        Misc.SendMessage(f"Warning: Only placed {points_placed} out of {total_points} items", 33)
    
    return placed_positions

def place_circle(center_x, center_y, radius, item_id, z=None):
    """Place a circle of items using absolute coordinates."""
    # Generate circle points
    points = []
    seen = set()
    for angle in range(0, 360, 5):  # 5-degree steps for smooth circles
        rad = math.radians(angle)
        x = center_x + int(radius * math.cos(rad))
        y = center_y + int(radius * math.sin(rad))
        pos_key = f"{x},{y}"
        if pos_key not in seen:
            points.append((x, y))
            seen.add(pos_key)
            
    return place_items_at_points(points, item_id, z, f"Placing circle with radius {radius}")

def place_gems(center_x, center_y, gem_type="amethyst"):
    """Place either amethyst or sapphire gems in their pattern."""
    # Get points and item ID based on gem type
    if gem_type == "amethyst":
        points = generate_core_4_points(center_x, center_y)
        item_id = AMETHYST_ID
        msg = "Placing amethyst circle"
    else:
        points = generate_core_4_points_alt(center_x, center_y)
        item_id = SAPPHIRE_ID
        msg = "Placing sapphire circle"
        
    return place_items_at_points(points, item_id, None, msg)

def place_blackpearl_circle(center_x, center_y):
    """Place black pearls in concentric circles."""
    points = generate_blackpearl_points(center_x, center_y)
    return place_items_at_points(points, BLACKPEARL_ID, None, "Placing black pearl circles")

def place_and_light_candles(center_x, center_y):
    """Place and light candles at specific points."""
    points = generate_candle_points(center_x, center_y)
    placed = place_items_at_points(points, CANDLE_ID, None, "Placing candles")
    
    # Light the placed candles
    if placed:
        Misc.SendMessage("Lighting candles...", 68)
        for x, y in placed:
            candle = Items.FindByID(CANDLE_ID, -1, -1, x, y)
            if candle:
                Items.UseItem(candle)
                Misc.Pause(PAUSE_DURATION)
    
    return placed

def try_random_position(x, y, radius=2):
    """Try to find a valid position near the target by moving in the general direction of the target."""
    import random
    
    # Get current position
    current_x = Player.Position.X
    current_y = Player.Position.Y
    
    # Calculate direction to target
    dx_to_target = x - current_x
    dy_to_target = y - current_y
    
    # Generate positions prioritizing movement in target direction
    positions = []
    
    # Add primary direction moves (closer to target)
    if abs(dx_to_target) > abs(dy_to_target):
        # Horizontal distance is greater, prioritize x movement
        positions.extend([(1 if dx_to_target > 0 else -1, 0)])
        positions.extend([(1 if dx_to_target > 0 else -1, 1), (1 if dx_to_target > 0 else -1, -1)])
    else:
        # Vertical distance is greater, prioritize y movement
        positions.extend([(0, 1 if dy_to_target > 0 else -1)])
        positions.extend([(1, 1 if dy_to_target > 0 else -1), (-1, 1 if dy_to_target > 0 else -1)])
    
    # Add secondary positions slightly randomized but in general target direction
    secondary_positions = []
    for d in range(1, radius + 1):
        if dx_to_target != 0:
            secondary_positions.append((d if dx_to_target > 0 else -d, random.choice([-1, 0, 1])))
        if dy_to_target != 0:
            secondary_positions.append((random.choice([-1, 0, 1]), d if dy_to_target > 0 else -d))
    
    random.shuffle(secondary_positions)
    positions.extend(secondary_positions)
    
    # Try each position
    for dx, dy in positions:
        # Move to new position
        coords = PathFinding.Route()
        coords.X = current_x + dx
        coords.Y = current_y + dy
        coords.MaxRetry = 2
        PathFinding.Go(coords)
        Misc.Pause(PAUSE_DURATION // 2)
        
        # If we moved and we're close enough to target, success
        if (Player.Position.X != current_x or Player.Position.Y != current_y) and \
           abs(Player.Position.X - x) <= MAX_DISTANCE and abs(Player.Position.Y - y) <= MAX_DISTANCE:
            return True
    
    return False

def gotoLocation(x, y, max_retries=3):
    """Move to within 1 tile of target location."""
    for i in range(max_retries):
        if abs(Player.Position.X - x) <= 1 and abs(Player.Position.Y - y) <= 1:
            return True
            
        Player.PathFindTo(x, y, Player.Position.Z)  # Using correct RE method
        Misc.Pause(MOVE_RETRY_PAUSE)
        
        # Check if we made it within 1 tile
        if abs(Player.Position.X - x) <= 1 and abs(Player.Position.Y - y) <= 1:
            return True
            
        if i < max_retries - 1:
            Misc.SendMessage(f"Movement retry {i + 1}/{max_retries}...", 33)
    
    return False

def complete_ritual(center_x, center_y):
    """Complete the ritual circle placement at the specified center point."""
    center_z = Player.Position.Z
    all_positions = set()
    
    # Place each component independently
    if PLACE_COMPONENTS["A_gem_4"]:
        positions = place_gem_circle(center_x, center_y, RITUAL_CONFIG["A_gem_4"])
        all_positions.update(positions)
    
    if PLACE_COMPONENTS["B_gem_4"]:
        positions = place_gem_circle(center_x, center_y, RITUAL_CONFIG["B_gem_4"])
        all_positions.update(positions)
    
    if PLACE_COMPONENTS["C_base_4"]:
        positions = place_base_circle(center_x, center_y, RITUAL_CONFIG["C_base_4"])
        all_positions.update(positions)
    
    if PLACE_COMPONENTS["D_base_5"]:
        positions = place_base_circle(center_x, center_y, RITUAL_CONFIG["D_base_5"])
        all_positions.update(positions)
    
    if PLACE_COMPONENTS["E_base_6"]:
        positions = place_base_circle(center_x, center_y, RITUAL_CONFIG["E_base_6"])
        all_positions.update(positions)
    
    if PLACE_COMPONENTS["F_base_7"]:
        positions = place_base_circle(center_x, center_y, RITUAL_CONFIG["F_base_7"])
        all_positions.update(positions)
    
    if PLACE_COMPONENTS["G_overlay_6"]:
        positions = place_overlay_circle(center_x, center_y, RITUAL_CONFIG["G_overlay_6"])
        all_positions.update(positions)
    
    if PLACE_COMPONENTS["H_overlay_7"]:
        positions = place_overlay_circle(center_x, center_y, RITUAL_CONFIG["H_overlay_7"])
        all_positions.update(positions)
    
    if PLACE_COMPONENTS["I_middle_8"] or PLACE_COMPONENTS["J_middle_9"] or PLACE_COMPONENTS["K_middle_4"]:
        positions = place_middle_patterns(center_x, center_y)
        all_positions.update(positions)
    
    # Place outer circles (each component handled independently inside)
    positions = place_outer_circles(center_x, center_y, center_z)
    all_positions.update(positions)
    
    # Place final outer rings (both inner and outer) if enabled
    if PLACE_COMPONENTS["Y_final_12"] or PLACE_COMPONENTS["Z_final_13"]:
        place_outer_ring(center_x, center_y, center_z)
    
    Misc.SendMessage(f"Ritual circle placement complete. Total positions: {len(all_positions)}", 68)
    return all_positions

def finalize_ritual(center_x, center_y):
    """Complete the ritual by returning to center and using Spirit Speak."""
    # Return to center
    if gotoLocation(center_x, center_y):
        # Use Spirit Speak at center
        Player.UseSkill("Spirit Speak") # Anh Mi Sah Ko
        Misc.Pause(PAUSE_DURATION)
        return True
    
    Misc.SendMessage("Failed to return to ritual center!", 33)
    return False

def initialize_ritual():
    """Initialize ritual by caching items and validating counts."""
    Misc.SendMessage("=== Initializing Ritual ===", 68)
    
    # Display configuration and calculate totals
    display_configuration()
    calculate_item_totals()
    Misc.Pause(1000)  # Give time to read the totals
    
    # Do initial item cache
    ITEM_CACHE.full_update()
    
    # Report initial counts
    Misc.SendMessage("\n=== Available Items ===", 68)
    for component, config in RITUAL_CONFIG.items():
        if PLACE_COMPONENTS.get(component, False):
            count = ITEM_CACHE.get_count(config['item_id'])
            item_name = get_item_name(config['item_id'])
            Misc.SendMessage(f"{component}: {count} {item_name}", 68)
    
    Misc.SendMessage("=== Initialization Complete ===", 68)

def get_item_name(item_id):
    """Get a readable name for an item ID."""
    # Common item names
    item_names = {
        0x0F7A: "Black Pearl",
        0x0F7B: "Blood Moss",
        0x0F84: "Garlic",
        0x0F85: "Ginseng",
        0x0F86: "Mandrake Root",
        0x0F88: "Nightshade",
        0x0F8D: "Spider's Silk",
        0x0F8C: "Sulfurous Ash",
        0x0F87: "Eye of Newt",
        0x0994: "Pear",
        0x0F8E: "Nox Crystal",
        0x0A25: "Lantern",
        0x0C70: "Lettuce",
        0x0C7B: "Cabbage",
        0x0F16: "Amethyst",
        0x0F11: "Sapphire"
    }
    return item_names.get(item_id, f"Item 0x{item_id:04X}")

def display_configuration():
    """Display the active ritual circle configuration"""
    Misc.SendMessage("=== Ritual Circle Configuration ===", 68)
    Misc.SendMessage("Active Components:", 68)
    
    # Group components by type for cleaner display
    if any(k.startswith("C_base") and v for k, v in PLACE_COMPONENTS.items()):
        Misc.SendMessage("- Base Circles:", 68)
        for k, v in PLACE_COMPONENTS.items():
            if k.startswith("C_base") and v:
                Misc.SendMessage(f"  - {RITUAL_CONFIG[k]['radius']}-tile circle", 68)
    
    if any(k.startswith(("A_gem", "B_gem")) and v for k, v in PLACE_COMPONENTS.items()):
        Misc.SendMessage("- Gem Circles:", 68)
        for k, v in PLACE_COMPONENTS.items():
            if k.startswith(("A_gem", "B_gem")) and v:
                Misc.SendMessage(f"  - {k.replace('_', ' ').title()}", 68)
    
    if any(k.startswith(("G_overlay", "H_overlay")) and v for k, v in PLACE_COMPONENTS.items()):
        Misc.SendMessage("- Overlay Circles:", 68)
        for k, v in PLACE_COMPONENTS.items():
            if k.startswith(("G_overlay", "H_overlay")) and v:
                Misc.SendMessage(f"  - {RITUAL_CONFIG[k]['radius']}-tile overlay", 68)
    
    if PLACE_COMPONENTS["I_middle_8"]:
        Misc.SendMessage("- Middle Circle:", 68)
        Misc.SendMessage(f"  - {RITUAL_CONFIG['I_middle_8']['radius']}-tile diamond pattern", 68)
        Misc.SendMessage(f"  - 8 points", 68)  # Fixed hardcoded value
    
    if PLACE_COMPONENTS["J_middle_9"]:
        Misc.SendMessage("- Middle Lantern Circle:", 68)
        Misc.SendMessage(f"  - {RITUAL_CONFIG['J_middle_9']['radius']}-tile circle", 68)
        Misc.SendMessage(f"  - 9 lanterns", 68)  # Fixed hardcoded value
    
    if PLACE_COMPONENTS["V_outer_4"]:
        Misc.SendMessage("- Outer Circle Sets:", 68)
        Misc.SendMessage(f"  - 8 sets at {RITUAL_CONFIG['V_outer_4']['center_radius']} tiles from center", 68)
        Misc.SendMessage(f"  - Inner circles: {RITUAL_CONFIG['V_outer_4']['radius']} tiles", 68)
        Misc.SendMessage(f"  - Outer circles: {RITUAL_CONFIG['W_outer_6']['radius']} tiles", 68)
        if PLACE_COMPONENTS["X_outer_0"]:
            Misc.SendMessage("  - With center lanterns", 68)
    
    if PLACE_COMPONENTS["Y_final_12"]:
        Misc.SendMessage("- Final Rings:", 68)
        Misc.SendMessage(f"  - Inner ring: {RITUAL_CONFIG['Y_final_12']['radius']} tiles", 68)
        Misc.SendMessage(f"  - Outer ring: {RITUAL_CONFIG['Z_final_13']['radius']} tiles", 68)

def calculate_item_totals():
    """Calculate and display total items needed for the ritual"""
    # Initialize totals dictionary with all unique item IDs from config
    totals = {}
    
    # Helper function to get item name from ID
    def get_item_name(item_id):
        # Map of item IDs to readable names
        item_names = {
            0x0F7B: "Lettuce",
            0x0F85: "Amethyst",
            0x0F86: "Sapphire",
            0x0F7A: "Black Pearl",
            0x0F87: "Eye of Newt",
            0x0F88: "Nightshade",
            0x0994: "Pear",
            0x0A25: "Lantern"
        }
        return item_names.get(item_id, f"Item 0x{item_id:04X}")
    
    # Process each enabled component
    for component_name, enabled in PLACE_COMPONENTS.items():
        if not enabled:
            continue
            
        component = RITUAL_CONFIG[component_name]
        
        if component_name.startswith(("A_", "B_", "C_", "D_", "E_", "F_", "G_", "H_", "I_", "J_")):
            # Simple components with single item type
            item_id = component["item_id"]
            points = component.get("points", 0)
            if component["pattern"] == "circle":
                # For circle patterns, calculate points based on radius
                points = int(2 * math.pi * component["radius"] / 0.5)
            totals[item_id] = totals.get(item_id, 0) + points
            
        elif component_name == "V_outer_4":
            # Outer circle sets (8 sets)
            inner = component
            outer = RITUAL_CONFIG["W_outer_6"]
            
            # Inner circles (8 sets)
            inner_points = int(2 * math.pi * inner["radius"] / 0.5) * 8
            totals[inner["item_id"]] = totals.get(inner["item_id"], 0) + inner_points
            
            # Outer circles (8 sets)
            outer_points = int(2 * math.pi * outer["radius"] / 0.5) * 8
            totals[outer["item_id"]] = totals.get(outer["item_id"], 0) + outer_points
            
            # Center lanterns (if enabled)
            if PLACE_COMPONENTS["X_outer_0"]:
                center = RITUAL_CONFIG["X_outer_0"]
                totals[center["item_id"]] = totals.get(center["item_id"], 0) + 8
                
        elif component_name == "Y_final_12":
            # Final outer rings
            inner = component
            outer = RITUAL_CONFIG["Z_final_13"]
            
            # Inner ring
            inner_points = int(2 * math.pi * inner["radius"] / 0.5)
            totals[inner["item_id"]] = totals.get(inner["item_id"], 0) + inner_points
            
            # Outer ring
            outer_points = int(2 * math.pi * outer["radius"] / 0.5)
            totals[outer["item_id"]] = totals.get(outer["item_id"], 0) + outer_points
    
    # Display item totals
    Misc.SendMessage("\nRequired Items:", 68)
    for item_id, count in totals.items():
        if count > 0:
            item_name = get_item_name(item_id)
            Misc.SendMessage(f"- {item_name}: {count} (0x{item_id:04X})", 68)

def place_outer_circles(center_x, center_y, center_z):
    """Place the 8 outer circles with lanterns. Each component is independent."""
    placed_positions = set()
    
    # Common configuration for outer components
    instances = 8
    center_radius = 11
    rotation = 22.5  # (360/8)/2 degrees rotation for offset
    
    # Pre-calculate instance centers to reuse
    instance_centers = []
    for i in range(instances):
        angle = (2 * math.pi * i) / instances + math.radians(rotation)
        instance_x = center_x + int(center_radius * math.cos(angle))
        instance_y = center_y + int(center_radius * math.sin(angle))
        instance_centers.append((instance_x, instance_y))
    
    # Place inner circles if enabled (Eye of Newt circles)
    if PLACE_COMPONENTS["V_outer_4"]:
        points_placed = 0
        Misc.SendMessage("=== Placing Inner Eye of Newt Circles ===", 68)
        for instance_x, instance_y in instance_centers:
            points, _ = generate_ring_points(instance_x, instance_y, 2)  # 2-tile radius for inner circles
            for point_x, point_y in points:
                if place_item(point_x, point_y, RITUAL_CONFIG['V_outer_4']['item_id']):
                    placed_positions.add((point_x, point_y))
                    points_placed += 1
                    if points_placed % 5 == 0:
                        Misc.SendMessage(f"Placed {points_placed} Eye of Newt points", 68)
    
    # Place center lanterns if enabled (independently)
    if PLACE_COMPONENTS["X_outer_0"]:
        points_placed = 0
        Misc.SendMessage("=== Placing Center Lanterns ===", 68)
        for instance_x, instance_y in instance_centers:
            if place_item(instance_x, instance_y, RITUAL_CONFIG['X_outer_0']['item_id']):
                placed_positions.add((instance_x, instance_y))
                points_placed += 1
                Misc.SendMessage(f"Placed lantern {points_placed}/{instances}", 68)
    
    # Place outer circles if enabled (Nightshade circles)
    if PLACE_COMPONENTS["W_outer_6"]:
        points_placed = 0
        Misc.SendMessage("=== Placing Outer Nightshade Circles ===", 68)
        for instance_x, instance_y in instance_centers:
            points, _ = generate_ring_points(instance_x, instance_y, 3)  # 3-tile radius for outer circles
            for point_x, point_y in points:
                if place_item(point_x, point_y, RITUAL_CONFIG['W_outer_6']['item_id']):
                    placed_positions.add((point_x, point_y))
                    points_placed += 1
                    if points_placed % 5 == 0:
                        Misc.SendMessage(f"Placed {points_placed} Nightshade points", 68)
    
    total_placed = len(placed_positions)
    if total_placed > 0:
        Misc.SendMessage(f"=== Outer Component Placement Complete ===", 68)
        Misc.SendMessage(f"Total positions placed: {total_placed}", 68)
    
    return placed_positions

def generate_ring_points(center_x, center_y, radius, step=5):
    """Generate points for a  circle with specified radius.
    Returns list of points and set of placed positions."""
    points = []
    placed_positions = set()
    
    # Generate points with high resolution
    for angle in range(0, 360, step):
        rad = math.radians(angle)
        point_x = center_x + int(radius * math.cos(rad))
        point_y = center_y + int(radius * math.sin(rad))
        pos_key = f"{point_x},{point_y}"
        if pos_key not in placed_positions:
            points.append((point_x, point_y))
            placed_positions.add(pos_key)
            
    return points, placed_positions

def place_outer_ring(center_x, center_y, center_z):
    """Place the final outer rings of the ritual circle."""
    # Generate points for both rings
    inner_points, _ = generate_ring_points(center_x, center_y, RITUAL_CONFIG['Y_final_12']['radius'])
    outer_points, _ = generate_ring_points(center_x, center_y, RITUAL_CONFIG['Z_final_13']['radius'])
    
    # Place inner ring
    if PLACE_COMPONENTS["Y_final_12"]:
        Misc.SendMessage("Placing inner ring points...", 68)
        place_items_at_points(inner_points, RITUAL_CONFIG['Y_final_12']['item_id'], center_z, "Placing inner ring")
    
    # Place outer ring
    if PLACE_COMPONENTS["Z_final_13"]:
        Misc.SendMessage("Placing outer ring points...", 68)
        place_items_at_points(outer_points, RITUAL_CONFIG['Z_final_13']['item_id'], center_z, "Placing outer ring")
    
    return True

def place_instanced_circles(center_x, center_y, config):
    """Place multiple instances of circles around a center point."""
    placed_positions = set()
    points_placed = 0
    
    # Calculate instance centers
    instances = config.get('instances', 8)
    center_radius = config.get('center_radius', 11)
    rotation = config.get('rotation', 22.5)  # (360/8)/2 degrees rotation for offset
    
    # Check initial item count - just warn if low
    item_count = ITEM_CACHE.get_count(config['item_id'])
    if item_count <= 0:
        Misc.SendMessage(f"Warning: No items of type {hex(config['item_id'])} available for circle placement", 33)
    
    # Place circles
    for i in range(instances):
        # Add rotation offset to base angle
        angle = (2 * math.pi * i) / instances + math.radians(rotation)
        instance_x = center_x + int(center_radius * math.cos(angle))
        instance_y = center_y + int(center_radius * math.sin(angle))
        
        # Generate and place circle points
        points, _ = generate_ring_points(instance_x, instance_y, config.get('radius', 2))
        for point_x, point_y in points:
            if place_item(point_x, point_y, config['item_id']):
                placed_positions.add((point_x, point_y))
                points_placed += 1
                if points_placed % 5 == 0:
                    Misc.SendMessage(f"Placed {points_placed} points", 68)
            else:
                Misc.SendMessage(f"Warning: Failed to place item at ({point_x}, {point_y})", 33)
                continue  # Skip this point but continue with others
    
    return placed_positions

def place_overlay_circle(center_x, center_y, config):
    """Place an overlay circle at the specified center point."""
    placed_positions = set()
    points_placed = 0
    
    Misc.SendMessage(f"=== Placing Overlay Circle (Radius {config['radius']}) ===", 68)
    
    # Generate points for the circle
    points, total_points = generate_ring_points(center_x, center_y, config['radius'])
    
    # Place items at each point
    for point_x, point_y in points:
        if place_item(point_x, point_y, config['item_id']):
            placed_positions.add((point_x, point_y))
            points_placed += 1
            if points_placed % 5 == 0:
                Misc.SendMessage(f"Placed {points_placed}/{total_points} overlay points", 68)
    
    if points_placed > 0:
        Misc.SendMessage(f"Overlay circle complete. Placed {points_placed} points.", 68)
    
    return placed_positions

def place_base_circle(center_x, center_y, config):
    """Place a base circle at the specified center point."""
    placed_positions = set()
    points_placed = 0
    
    Misc.SendMessage(f"=== Placing Base Circle (Radius {config['radius']}) ===", 68)
    
    # Generate points for the circle
    points, total_points = generate_ring_points(center_x, center_y, config['radius'])
    
    # Place items at each point
    for point_x, point_y in points:
        if place_item(point_x, point_y, config['item_id']):
            placed_positions.add((point_x, point_y))
            points_placed += 1
            if points_placed % 5 == 0:
                Misc.SendMessage(f"Placed {points_placed}/{total_points} base points", 68)
    
    if points_placed > 0:
        Misc.SendMessage(f"Base circle complete. Placed {points_placed} points.", 68)
    
    return placed_positions

def place_middle_patterns(center_x, center_y):
    """
    Place the middle ritual patterns (diamond, circle, lanterns) if enabled.
    Returns a set of all placed positions.
    """
    placed_positions = set()
    # Middle diamond pattern (I_middle_8)
    if PLACE_COMPONENTS.get("I_middle_8", False):
        config = RITUAL_CONFIG["I_middle_8"]
        # Diamond: 8 points at 45-degree increments
        points = []
        radius = config.get("radius", 8)
        for i in range(8):
            angle = (2 * math.pi * i) / 8  # 8 points around the circle
            point_x = center_x + int(round(radius * math.cos(angle)))
            point_y = center_y + int(round(radius * math.sin(angle)))
            points.append((point_x, point_y))
        for point_x, point_y in points:
            if place_item(point_x, point_y, config["item_id"]):
                placed_positions.add((point_x, point_y))
        Misc.SendMessage(f"Placed middle diamond (I_middle_8) points: {len(points)}", 68)

    # Middle circle pattern (J_middle_9)
    if PLACE_COMPONENTS.get("J_middle_9", False):
        config = RITUAL_CONFIG["J_middle_9"]
        # Use existing generate_ring_points for a 9-radius circle
        points, _ = generate_ring_points(center_x, center_y, config.get("radius", 9))
        for point_x, point_y in points:
            if place_item(point_x, point_y, config["item_id"]):
                placed_positions.add((point_x, point_y))
        Misc.SendMessage(f"Placed middle circle (J_middle_9) points: {len(points)}", 68)

    # Middle lantern circle (K_middle_4)
    if PLACE_COMPONENTS.get("K_middle_4", False):
        config = RITUAL_CONFIG["K_middle_4"]
        # 4 lanterns in a diamond (cardinal directions)
        points = []
        radius = config.get("radius", 7)
        for i in range(4):
            angle = (2 * math.pi * i) / 4  # 4 points (N, E, S, W)
            point_x = center_x + int(round(radius * math.cos(angle)))
            point_y = center_y + int(round(radius * math.sin(angle)))
            points.append((point_x, point_y))
        for point_x, point_y in points:
            if place_item(point_x, point_y, config["item_id"]):
                placed_positions.add((point_x, point_y))
        Misc.SendMessage(f"Placed middle lanterns (K_middle_4) points: {len(points)}", 68)

    return placed_positions

def place_gem_circle(center_x, center_y, config):
    """Place a gem circle at the specified center point."""
    placed_positions = set()
    points_placed = 0
    
    Misc.SendMessage(f"=== Placing Gem Circle (Radius {config['radius']}) ===", 68)
    
    # For diagonal pattern, generate points at 45-degree angles
    if config['pattern'] == 'diagonal':
        points = []
        radius = config['radius']
        for i in range(4):  # 4 diagonal points
            angle = (2 * math.pi * i) / 4 + math.radians(45)  # 45-degree offset
            point_x = center_x + int(radius * math.cos(angle))
            point_y = center_y + int(radius * math.sin(angle))
            points.append((point_x, point_y))
        total_points = 4
    else:
        # For regular circle pattern
        points, total_points = generate_ring_points(center_x, center_y, config['radius'])
    
    # Place items at each point
    for point_x, point_y in points:
        if place_item(point_x, point_y, config['item_id']):
            placed_positions.add((point_x, point_y))
            points_placed += 1
            if points_placed % 5 == 0:
                Misc.SendMessage(f"Placed {points_placed}/{total_points} gem points", 68)
    
    if points_placed > 0:
        Misc.SendMessage(f"Gem circle complete. Placed {points_placed} points.", 68)
    
    return placed_positions

def main():
    """Main ritual function."""
    try:
        # Initialize and cache items
        initialize_ritual()
        
        # Get current position as center
        center_x = Player.Position.X
        center_y = Player.Position.Y
        
        Misc.SendMessage(f"=== Starting Ritual at ({center_x}, {center_y}) ===", 68)
        
        # Place all ritual components
        complete_ritual(center_x, center_y)
        
        # Complete ritual by returning to center
        finalize_ritual(center_x, center_y)
        
        Misc.SendMessage("=== Ritual Complete ===", 68)
        
    except Exception as e:
        Misc.SendMessage(f"Error in ritual: {str(e)}", 33)
        return False

if __name__ == '__main__':
    main()
