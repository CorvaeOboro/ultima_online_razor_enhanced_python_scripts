"""
RITUAL of DEATH - a Razor Enhanced Python Script for Ultima Online

places a death ritual pattern , darkened floor crack , circles of bones , 4 pillars of death orbs

dark cloth, black pearl, eye of newt ,
bones, bone piles, rib cages
stacked plant bowls , lantern , death orb 

VERSION::20250917
"""
import math
import time
import random

DEBUG_MODE = False            # debug messages in journal
SAFE_MODE = False             # extra delays slowmode
PREVIEW_MODE = True           # If True, render client-side only
USE_AUTO_Z_STACKING = True    # If True, use Z=-1 for all item placements
MOVE_MATERIALS_TO_TARGET_CONTAINER = False  # If True, move required materials to target container before ritual

# ===== Seed Control =====
USE_RANDOM_SEED = False         # If False, use FIXED_SEED for reproducible patterns
FIXED_SEED = 999            # Seed to use when USE_RANDOM_SEED is False
PREFERRED_SEEDS = [12345, 4444]  # Collection of good seeds to randomly choose from

# ===== Layer toggles =====
ENABLE_CENTER_CRACKS = True           # cloth cracks made from Cloth
ENABLE_CENTER_CRACKS_CLOTH = True     # cloth crack arms (main layer)
ENABLE_CENTER_CRACKS_EYE_NEWT = True  # eye of newt crack arms 
ENABLE_CENTER_CRACKS_PEARL = False    # black pearl crack arms # FALSE
ENABLE_CENTER_PEARL = True            # black pearl rings (concentric circles)
ENABLE_CENTER_ORB = False              # center death orb on pillar # FALSE
ENABLE_DEATH_PILLARS = True           # 4 surrounding death pillars
ENABLE_PILLAR_DECORATIONS = True      # death decorations around pillars

# ===== Global Exclusion Zone =====
ENABLE_EXCLUSION_ZONE = False          # If True, skip placement attempts on excluded coordinates
EXCLUSION_ZONE_RADIUS = 1             # Radius around center to exclude

# ===== Material Movement =====
TARGET_CONTAINER_SERIAL = 0x4012CE48   # Serial of container to move materials to (change this to your container)

# ===== SHAPES =====
DEATH_CIRCLE = {
    "radius": 2,        # distance from center for the 4 death pillar positions
    "rotation": 0,     # base rotation (45 degrees for diagonal placement) 45 default
    "count": 4,         # 4 death pillars
}

# Center orb pillar
CENTER_PILLAR_RADIUS = 0  # At center position

# Pillar construction
PILLAR_BOWL_STACK_COUNT = 5
STACK_Z_STEP = 1          # Z increment per stacked item
STACK_TOP_EXTRA = 1       # Extra Z for items that sit on top of a layer

# Center-layer visuals (cloth cracks, black pearl rings)
CENTER_CRACK_ARMS = 8
CENTER_CRACK_MIN_LEN = 2
CENTER_CRACK_MAX_LEN = 5
CENTER_PEARL_RING_RADII = [2, 3, 5]
CENTER_PEARL_RING_POINTS = [8, 12, 24]

# Current seed being used (set at runtime)
CURRENT_SEED = None

# Crack branching
CENTER_CRACK_BRANCH_CHANCE = 0.3            # chance per segment to start a branch
CENTER_CRACK_MAX_BRANCHES_PER_ARM = 2       # cap branches per main arm
CENTER_CRACK_BRANCH_ANGLE_OFFSET_MIN = 25   # degrees away from main direction (min)
CENTER_CRACK_BRANCH_ANGLE_OFFSET_MAX = 60   # degrees away from main direction (max)
CENTER_CRACK_BRANCH_MIN_LEN = 2
CENTER_CRACK_BRANCH_MAX_LEN = 4

# Black pearl crack tuning
PEARL_CRACK_MIN_LEN = CENTER_CRACK_MIN_LEN + 1
PEARL_CRACK_MAX_LEN = CENTER_CRACK_MAX_LEN + 2
PEARL_CRACK_ARMS = CENTER_CRACK_ARMS
PEARL_STACK_MAX = 1               # maximum items stacked at center
PEARL_STACK_FALLOFF = 1.5         # tiles per -1 stack as distance increases
PEARL_STACK_SIGMA = 1.0           # smooth falloff shaping for center stacking
PEARL_STACK_PREVIEW_DELAY_MS = 100  # pause between stacked preview placements

# Decoration settings
DECORATION_RING_RADIUS = 3
DECORATION_RING_POINTS = 8
DECORATION_LINE_LENGTH = 4
DECORATION_LINE_SPACING = 1

# ===== TIMING =====
PAUSE_DURATION = 350
PAUSE_DURATION_PLACE = 550
MAX_DISTANCE = 2

GOTO_BASE_DELAY = 250
GOTO_MAX_RETRIES = 1
WIGGLE_RADII = [0]
WIGGLE_ANGLES = [0, 45, 90, 135, 180, 225, 270, 315]
WALK_REPEATS_PER_DIR = 2

CENTER_BIAS_ENABLED = True
CENTER_NUDGE_DISTANCE = 3
CENTER_NUDGE_STEPS = 2

PLACE_MAX_RETRIES = 2
PLACE_BACKOFF_BASE = 250
POINT_TIMEOUT_MS = 1500
POINT_BREATHER_MS = 250

RATE_MIN_GAP_MS = 350
LOOP_YIELD_MS = 40
JITTER_MS = 50
LAST_ACTION_MS = 0

# In preview mode, use snappier timings
PREVIEW_DELAY_SCALE = 0.3   # 30% of normal delays
PREVIEW_JITTER_MS = 10      # smaller random jitter window
PREVIEW_DEFAULT_HUE = 0x0000   # 0 means no hue
PREVIEW_Z_OFFSET = 3 # avoiding clipping with ground
PREVIEW_RANDOM_POOL_DELAY_MS = 400  # extra delay per preview random-pool item

MAX_PHASE_FAILURES = 6
PLACED_COORDS_BY_ITEM = {}
BAD_COORDS = set()
EXCLUDED_COORDS = set()  # Global exclusion zone coordinates
ENABLE_STACK_TRACKING = True
# Tracks the next available Z at a given (x,y) after successful placements.
PLACED_TOP_Z = {}

# ===== ITEM IDS =====
ORB_ITEM_ID = 0x573E  # Death orbs share the same base item ID
DEFAULT_CLOTH_HUE = 0x025A  # Default dark cloth hue
DEATH_ORB_HUE = 0x0b3a  # Death orb hue (black)

MATERIAL_ITEM_IDS = {
    # Base items
    "Cloth": [0x1766],
    "Plant Bowl": [0x15FD],
    "Lantern": [0x0A25],
    # Death items
    "Black Pearl": [0x0F7A],
    "Eye of Newt": [0x0F87],
    "Bones": [0x0F7E],
    "Bone Piles": [0x1B0E, 0x1B0B, 0x1B0C, 0x1B0F, 0x1B09],
    "Rib Cage": [0x1B17],
    # Additional death-themed items
    "Night Sight Potion": [0x0F06],
    "Spider Carapace": [0x5720],
}

# Death item dictionary for readable configuration - references MATERIAL_ITEM_IDS
DEATH_ITEMS = {
    "cloth": MATERIAL_ITEM_IDS["Cloth"][0],
    "bones": MATERIAL_ITEM_IDS["Bones"][0],
    "bone_pile_1": MATERIAL_ITEM_IDS["Bone Piles"][0],
    "bone_pile_2": MATERIAL_ITEM_IDS["Bone Piles"][1], 
    "bone_pile_3": MATERIAL_ITEM_IDS["Bone Piles"][2],
    "rib_cage": MATERIAL_ITEM_IDS["Rib Cage"][0],
    "black_pearl": MATERIAL_ITEM_IDS["Black Pearl"][0],
    "eye_of_newt": MATERIAL_ITEM_IDS["Eye of Newt"][0],
    "night_sight_potion": MATERIAL_ITEM_IDS["Night Sight Potion"][0],
    "spider_carapace": MATERIAL_ITEM_IDS["Spider Carapace"][0],
    "lantern": MATERIAL_ITEM_IDS["Lantern"][0],
    "plant_bowl": MATERIAL_ITEM_IDS["Plant Bowl"][0],
    "death_orb": ORB_ITEM_ID,
}

# Death pillar configuration - references MATERIAL_ITEM_IDS
DEATH_PILLAR_CONFIG = {
    "decorations": [
        {"type": "ring", "item_ids": MATERIAL_ITEM_IDS["Bone Piles"] + MATERIAL_ITEM_IDS["Rib Cage"], "radius": 2, "points": 8, "rotation": 0},  # All bone items
        {"type": "ring", "item_ids": MATERIAL_ITEM_IDS["Eye of Newt"], "radius": 3, "points": 12, "rotation": 0},  # Eye of Newt
        #{"type": "ring", "item_ids": MATERIAL_ITEM_IDS["Black Pearl"], "radius": 4, "points": 16, "rotation": 0},  # Black Pearl
        {"type": "ring", "item_ids": MATERIAL_ITEM_IDS["Bones"], "radius": 4, "points": 8, "rotation": 0},  # Bones
        #{"type": "line", "item_ids": MATERIAL_ITEM_IDS["Bone Piles"], "length": 3, "spacing": 1, "direction": "outward", "start_offset": 2},  # Bone Piles
    ]
}

#//==========================================================================
# UTILITY FUNCTIONS

def initialize_exclusion_zone(center_x, center_y):
    """Initialize the global exclusion zone around center coordinates"""
    global EXCLUDED_COORDS
    EXCLUDED_COORDS.clear()
    
    if not ENABLE_EXCLUSION_ZONE:
        return
    
    # Add center and surrounding grid cells based on radius
    for dx in range(-EXCLUSION_ZONE_RADIUS, EXCLUSION_ZONE_RADIUS + 1):
        for dy in range(-EXCLUSION_ZONE_RADIUS, EXCLUSION_ZONE_RADIUS + 1):
            x = center_x + dx
            y = center_y + dy
            EXCLUDED_COORDS.add((x, y))
    
    debug_message(f"Exclusion zone initialized: {len(EXCLUDED_COORDS)} coordinates around ({center_x},{center_y}) radius {EXCLUSION_ZONE_RADIUS}", 68)

def is_coordinate_excluded(x, y):
    """Check if coordinate is in the global exclusion zone"""
    return ENABLE_EXCLUSION_ZONE and (x, y) in EXCLUDED_COORDS

def debug_message(msg, color=0):
    if DEBUG_MODE:
        try:
            Misc.SendMessage(msg, color)
        except Exception:
            print(msg)

def now_ms():
    return int(time.time() * 1000)

def pause_ms(ms):
    if PREVIEW_MODE:
        scaled = int(ms * PREVIEW_DELAY_SCALE)
        jitter = random.randint(0, PREVIEW_JITTER_MS)
        Misc.Pause(max(0, scaled + jitter))
    else:
        Misc.Pause(int(ms + random.randint(0, JITTER_MS)))

def throttle(min_gap_ms=RATE_MIN_GAP_MS):
    global LAST_ACTION_MS
    t = now_ms()
    if LAST_ACTION_MS == 0:
        LAST_ACTION_MS = t
        return
    elapsed = t - LAST_ACTION_MS
    eff_gap = int(min_gap_ms * PREVIEW_DELAY_SCALE) if PREVIEW_MODE else min_gap_ms
    if elapsed < eff_gap:
        Misc.Pause(eff_gap - elapsed)
    LAST_ACTION_MS = now_ms()

def get_ground_z(x, y):
    """Get the actual ground Z coordinate at the specified tile."""
    try:
        # Get static tiles at this position
        tiles = Statics.GetStaticsTileInfo(x, y, Player.Map)
        if tiles and len(tiles) > 0:
            # Use the Z of the highest walkable tile
            walkable_tiles = [t for t in tiles]
            if walkable_tiles:
                ground_z = max(t.StaticZ for t in walkable_tiles)
                debug_message(f"get_ground_z({x},{y}): found static tiles, using Z={ground_z}", 68)
                return ground_z
        # Fallback to land tile Z
        land_z = Statics.GetLandZ(x, y, Player.Map)
        debug_message(f"get_ground_z({x},{y}): using land Z={land_z}", 68)
        return land_z
    except Exception as e:
        debug_message(f"get_ground_z({x},{y}): error {e}, using player Z={Player.Position.Z}", 68)
        return Player.Position.Z

def compute_target_z(x, y, proposed_z):
    """Return the Z to use for placement, stacking above prior placements at (x,y)."""
    # Get the actual ground Z at this location
    ground_z = get_ground_z(x, y)
    
    if ENABLE_STACK_TRACKING:
        prev = PLACED_TOP_Z.get((x, y))
        if prev is not None:
            try:
                # Always stack on top of previous items
                return int(prev) + STACK_Z_STEP
            except Exception:
                return prev + STACK_Z_STEP
    
    # Use ground Z as base instead of proposed Z
    return ground_z

def is_safe_ground(x, y, game_map=None):
    if game_map is None:
        game_map = Player.Map
    if (x, y) in BAD_COORDS:
        return False
    try:
        land_id = Statics.GetLandID(x, y, game_map)
    except Exception:
        return False
    BAD_LAND_IDS = {0x0001}
    if land_id in BAD_LAND_IDS:
        return False
    return True

# ===== PREVIEW FUNCTIONS =====
def _convert_packet_to_bytes(packet_list):
    byte_list = []
    for value in packet_list:
        if value:
            byte_list.append(int(value, 16))
        else:
            byte_list.append(0)
    return byte_list

def _send_fake_item(item_x, item_y, item_z, item_id_4hex_with_space, hue_4hex_with_space):
    try:
        packet = (
            "F3 00 01 00 48 FC BB 12 "
            + item_id_4hex_with_space
            + " 00 00 01 00 01 05 88 06 88 0A 00 04 15 20 00 00"
        )
        packet_list = packet.split(" ")

        serial_hex = hex(random.randrange(0, 0xFFFFFF))[2:].zfill(6)

        i_loc_x = hex(int(item_x))[2:].zfill(4)
        i_loc_y = hex(int(item_y))[2:].zfill(4)
        i_loc_z = hex(int(item_z))[2:].zfill(2)

        x1, x2 = i_loc_x[:2], i_loc_x[2:]
        y1, y2 = i_loc_y[:2], i_loc_y[2:]

        hues = hue_4hex_with_space.split(" ")

        packet_list[5] = serial_hex[0:2]
        packet_list[6] = serial_hex[2:4]
        packet_list[7] = serial_hex[4:6]
        packet_list[15] = x1
        packet_list[16] = x2
        packet_list[17] = y1
        packet_list[18] = y2
        packet_list[19] = i_loc_z
        packet_list[21] = hues[0]
        packet_list[22] = hues[1]

        byte_list = _convert_packet_to_bytes(packet_list)
        PacketLogger.SendToClient(byte_list)
    except Exception as e:
        debug_message(f"Preview send failed: {e}", 33)

def _format_hex_4_with_space(value):
    """Convert a value to a 4-digit hex string with space in the middle.
    Handles both integer and string inputs, including '0x' prefixed strings.
    """
    try:
        # If value is a string with '0x' prefix, convert it to int first
        if isinstance(value, str) and value.lower().startswith('0x'):
            value = int(value, 16)
        # Convert to integer and ensure it's 16-bit
        value_int = int(value) & 0xFFFF
        # Format as 4-digit hex, uppercase, zero-padded
        hex_str = f"{value_int:04X}"
        # Insert space in the middle (e.g., '0010' -> '00 10')
        return f"{hex_str[:2]} {hex_str[2:]}"
    except (ValueError, TypeError) as e:
        debug_message(f"ERROR: Could not format value '{value}' as hex: {e}", 33)
        return "00 00"  # Return a safe default

def preview_item_at(x, y, z, item_id, hue=PREVIEW_DEFAULT_HUE):
    item_hex = _format_hex_4_with_space(item_id)
    hue_hex = _format_hex_4_with_space(hue)
    _send_fake_item(x, y, z, item_hex, hue_hex)

# ===== MOVEMENT FUNCTIONS =====
def dir_to_str(direction):
    """Convert numeric direction to string for debugging"""
    directions = {0: "North", 1: "NorthEast", 2: "East", 3: "SouthEast", 
                  4: "South", 5: "SouthWest", 6: "West", 7: "NorthWest"}
    return directions.get(direction, f"Unknown({direction})")

def attempt_walk_toward(target_x, target_y, max_attempts=3):
    """Attempt to walk toward target coordinates with +2 tile jumps to reduce jitter"""
    for attempt in range(max_attempts):
        dx = target_x - Player.Position.X
        dy = target_y - Player.Position.Y
        
        if dx == 0 and dy == 0:
            return True
        
        # Calculate direction (0-7) and make +2 tile jumps
        if abs(dx) > abs(dy):
            direction = 2 if dx > 0 else 6  # East or West
        elif abs(dy) > abs(dx):
            direction = 4 if dy > 0 else 0  # South or North
        else:
            # Diagonal movement
            if dx > 0 and dy > 0:
                direction = 3  # SouthEast
            elif dx > 0 and dy < 0:
                direction = 1  # NorthEast
            elif dx < 0 and dy > 0:
                direction = 5  # SouthWest
            else:
                direction = 7  # NorthWest
        
        debug_message(f"Walk attempt {attempt + 1}: moving {dir_to_str(direction)} toward ({target_x},{target_y}) with +2 tile jump", 68)
        
        try:
            # Make 2 steps in the same direction to jump +2 tiles
            for step in range(2):
                if Player.Walk(dir_to_str(direction)):
                    pause_ms(GOTO_BASE_DELAY // 2)  # Shorter pause between steps
                else:
                    debug_message(f"Walk step {step + 1} failed in direction {dir_to_str(direction)}", 33)
                    break
            
            # Check if we reached target or got closer
            new_dx = target_x - Player.Position.X
            new_dy = target_y - Player.Position.Y
            if abs(new_dx) < abs(dx) or abs(new_dy) < abs(dy) or (new_dx == 0 and new_dy == 0):
                debug_message(f"Movement progress: was ({dx},{dy}) now ({new_dx},{new_dy})", 68)
            
        except Exception as e:
            debug_message(f"ERROR: Player.Walk failed with direction {dir_to_str(direction)}: {e}", 33)
            pause_ms(GOTO_BASE_DELAY // 2)
    
    return Player.Position.X == target_x and Player.Position.Y == target_y

def attempt_center_bias_movement(target_x, target_y, center_x, center_y):
    """Attempt to move closer to the target using center bias"""
    # Calculate direction from center to target
    dx = target_x - center_x
    dy = target_y - center_y
    
    # Calculate primary direction
    if abs(dx) > abs(dy):
        direction = 2 if dx > 0 else 6  # East or West
    elif abs(dy) > abs(dx):
        direction = 4 if dy > 0 else 0  # South or North
    else:
        # Diagonal movement
        if dx > 0 and dy > 0:
            direction = 3  # SouthEast
        elif dx > 0 and dy < 0:
            direction = 1  # NorthEast
        elif dx < 0 and dy > 0:
            direction = 5  # SouthWest
        else:
            direction = 7  # NorthWest
    
    debug_message(f"Center bias movement: moving {dir_to_str(direction)} toward ({target_x},{target_y}) from center ({center_x},{center_y})", 68)
    
    try:
        if Player.Walk(dir_to_str(direction)):
            pause_ms(GOTO_BASE_DELAY)
            return True
        else:
            debug_message(f"Center bias movement failed in direction {dir_to_str(direction)}", 33)
            pause_ms(GOTO_BASE_DELAY // 2)
            return False
    except Exception as e:
        debug_message(f"ERROR: Center bias Player.Walk failed with direction {dir_to_str(direction)}: {e}", 33)
        pause_ms(GOTO_BASE_DELAY // 2)
        return False

def goto_location_with_wiggle(target_x, target_y, center=None):
    """Enhanced goto with center bias and wiggle patterns"""
    # Type validation and debugging
    debug_message(f"goto_location_with_wiggle called: target_x={target_x} (type: {type(target_x)}), target_y={target_y} (type: {type(target_y)})", 68)
    
    try:
        target_x_int = int(target_x)
        target_y_int = int(target_y)
        debug_message(f"Converted target coordinates: x={target_x_int}, y={target_y_int}", 68)
    except (ValueError, TypeError) as e:
        debug_message(f"ERROR: Cannot convert target coordinates to int: x={target_x}, y={target_y}, error={e}", 33)
        return False
    
    current_x = Player.Position.X
    current_y = Player.Position.Y
    debug_message(f"Current position: ({current_x},{current_y}), Target: ({target_x_int},{target_y_int})", 68)
    
    if current_x == target_x_int and current_y == target_y_int:
        debug_message(f"Already at target position", 68)
        return True
    
    # Center bias: nudge toward center first if enabled
    if CENTER_BIAS_ENABLED and center:
        try:
            cx, cy = center
            cx_int = int(cx)
            cy_int = int(cy)
            debug_message(f"Center bias enabled: center=({cx_int},{cy_int})", 68)
            for _ in range(CENTER_NUDGE_STEPS):
                if abs(Player.Position.X - cx_int) > CENTER_NUDGE_DISTANCE or abs(Player.Position.Y - cy_int) > CENTER_NUDGE_DISTANCE:
                    if attempt_walk_toward(cx_int, cy_int, 1):
                        debug_message(f"Center bias: moved closer to center ({cx_int},{cy_int})", 68)
                    pause_ms(GOTO_BASE_DELAY)
        except Exception as e:
            debug_message(f"ERROR: Center bias failed: {e}", 33)
    
    # Direct approach first
    debug_message(f"Attempting direct walk to ({target_x_int},{target_y_int})", 68)
    try:
        if attempt_walk_toward(target_x_int, target_y_int):
            debug_message(f"Direct walk successful to ({target_x_int},{target_y_int})", 68)
            return True
    except Exception as e:
        debug_message(f"ERROR: Direct walk failed: {e}", 33)
    if attempt_walk_toward(target_x, target_y):
        return True
    
    # Wiggle pattern approach
    for radius in WIGGLE_RADII:
        for angle in WIGGLE_ANGLES:
            wiggle_x = target_x + int(radius * math.cos(math.radians(angle)))
            wiggle_y = target_y + int(radius * math.sin(math.radians(angle)))
            
            debug_message(f"Wiggle: trying ({wiggle_x},{wiggle_y}) radius={radius} angle={angle}", 68)
            
            if attempt_walk_toward(wiggle_x, wiggle_y):
                # Now try to reach the exact target
                if attempt_walk_toward(target_x, target_y):
                    return True
            
            pause_ms(GOTO_BASE_DELAY)
    
    debug_message(f"Failed to reach ({target_x},{target_y}) after all attempts", 33)
    return False

# ===== GEOMETRIC FUNCTIONS =====
def generate_circle_points(center_x, center_y, radius, num_points, rotation_deg=0):
    """Generate points in a circle around center"""
    points = []
    for i in range(num_points):
        angle_deg = (360.0 * i / num_points) + rotation_deg
        angle_rad = math.radians(angle_deg)
        x = center_x + int(round(radius * math.cos(angle_rad)))
        y = center_y + int(round(radius * math.sin(angle_rad)))
        points.append((x, y))
    return points

def generate_line_points(start_x, start_y, angle_deg, length, spacing=1):
    """Generate points along a line from start position"""
    points = []
    angle_rad = math.radians(angle_deg)
    for i in range(0, length, spacing):
        x = start_x + int(round(i * math.cos(angle_rad)))
        y = start_y + int(round(i * math.sin(angle_rad)))
        points.append((x, y))
    return points

def generate_crack_arm(start_x, start_y, angle_deg, min_len, max_len, branch_chance=0.0, max_branches=0):
    """Generate a crack arm with potential branching"""
    points = []
    length = random.randint(min_len, max_len)
    
    # Main arm points
    main_points = generate_line_points(start_x, start_y, angle_deg, length)
    points.extend(main_points)
    
    # Add branches
    branches_created = 0
    for i, (x, y) in enumerate(main_points[1:], 1):  # Skip start point for branching
        if branches_created >= max_branches:
            break
        if random.random() < branch_chance:
            # Create a branch
            branch_angle_offset = random.randint(CENTER_CRACK_BRANCH_ANGLE_OFFSET_MIN, CENTER_CRACK_BRANCH_ANGLE_OFFSET_MAX)
            if random.random() < 0.5:
                branch_angle_offset = -branch_angle_offset
            branch_angle = angle_deg + branch_angle_offset
            branch_length = random.randint(CENTER_CRACK_BRANCH_MIN_LEN, CENTER_CRACK_BRANCH_MAX_LEN)
            
            branch_points = generate_line_points(x, y, branch_angle, branch_length)
            points.extend(branch_points[1:])  # Skip the starting point to avoid duplicates
            branches_created += 1
    
    return points

def get_death_pillar_positions(center_x, center_y):
    """Get positions for the 4 death pillars around the center"""
    positions = []
    radius = DEATH_CIRCLE["radius"]
    rotation = DEATH_CIRCLE["rotation"]
    count = DEATH_CIRCLE["count"]
    
    for i in range(count):
        angle_deg = (360.0 * i / count) + rotation
        angle_rad = math.radians(angle_deg)
        x = center_x + int(round(radius * math.cos(angle_rad)))
        y = center_y + int(round(radius * math.sin(angle_rad)))
        positions.append((x, y))
    
    return positions

def filter_points_outside_radius(points, center, min_radius, forbidden=None):
    """Filter out points too close to center or in forbidden set"""
    if forbidden is None:
        forbidden = set()
    
    cx, cy = center
    filtered = []
    
    debug_message(f"Filtering {len(points)} points: center=({cx},{cy}), min_radius={min_radius}, forbidden={forbidden}", 68)
    
    for x, y in points:
        if (x, y) in forbidden:
            debug_message(f"Point ({x},{y}) filtered out: in forbidden set", 68)
            continue
        
        distance = math.hypot(x - cx, y - cy)
        if distance >= min_radius:
            filtered.append((x, y))
            debug_message(f"Point ({x},{y}) kept: distance={distance:.2f} >= {min_radius}", 68)
        else:
            debug_message(f"Point ({x},{y}) filtered out: distance={distance:.2f} < {min_radius}", 68)
    
    debug_message(f"Filter result: {len(filtered)}/{len(points)} points kept", 67)
    return filtered

# ===== ITEM PLACEMENT FUNCTIONS =====
def get_first_available_item_id(item_ids, min_count=0):
    """Find first available item ID from a list, randomized selection. Uses min_count=0 to place any available items."""
    if not isinstance(item_ids, list):
        item_ids = [item_ids]
    
    # Filter out None values
    valid_ids = [item_id for item_id in item_ids if item_id is not None]
    if not valid_ids:
        return None
    
    # In preview mode, return a random valid item ID
    if PREVIEW_MODE:
        return random.choice(valid_ids)
    
    # In real mode, check backpack availability and randomize among available items
    available_ids = []
    for item_id in valid_ids:
        try:
            count = Items.BackpackCount(item_id, -1)
            if count > min_count:  # Changed from >= to > so min_count=0 finds any items
                available_ids.append(item_id)
        except Exception:
            continue
    
    if available_ids:
        return random.choice(available_ids)
    
    # If no items meet min_count, return first valid ID anyway to attempt placement
    return valid_ids[0] if valid_ids else None

def place_item(x, y, item_id, z=None, hue=None):
    """Place a single item at the specified location"""
    # Type validation and debugging
    # Handle case where item_id might be a list instead of int
    if isinstance(item_id, list):
        if len(item_id) > 0:
            actual_item_id = item_id[0]
        else:
            debug_message(f"ERROR: Empty item_id list provided", 33)
            return False
    else:
        actual_item_id = item_id
    
    # Additional validation
    if actual_item_id is None:
        debug_message(f"ERROR: actual_item_id is None after processing", 33)
        return False
    
    debug_message(f"place_item called: x={x} (type: {type(x)}), y={y} (type: {type(y)}), item_id=0x{actual_item_id:X}, z={z}, hue={hue}", 68)
    
    # Convert to integers with validation
    try:
        x_int = int(x)
        y_int = int(y)
        debug_message(f"Converted coordinates: x={x_int}, y={y_int}", 68)
    except (ValueError, TypeError) as e:
        debug_message(f"ERROR: Cannot convert coordinates to int: x={x}, y={y}, error={e}", 33)
        return False
    
    if actual_item_id is None:
        debug_message(f"ERROR: item_id is None", 33)
        return False
    
    if is_coordinate_excluded(x_int, y_int):
        debug_message(f"Skipping excluded coordinate ({x_int},{y_int})", 68)
        return False
    
    if not is_safe_ground(x_int, y_int):
        debug_message(f"Unsafe ground at ({x_int},{y_int}), skipping", 33)
        BAD_COORDS.add((x_int, y_int))
        return False
    
    base_z = z if z is not None else Player.Position.Z
    debug_message(f"Using base_z: {base_z} (type: {type(base_z)})", 68)
    
    if PREVIEW_MODE:
        z_final = compute_target_z(x_int, y_int, base_z)
        z_show = z_final + PREVIEW_Z_OFFSET
        debug_message(f"PREVIEW: placing at ({x_int},{y_int},{z_show})", 68)
        preview_item_at(x_int, y_int, z_show, actual_item_id, hue if hue is not None else PREVIEW_DEFAULT_HUE)
        if ENABLE_STACK_TRACKING:
            PLACED_TOP_Z[(x_int, y_int)] = z_final
        return True
    
    # Real placement logic
    try:
        debug_message(f"LIVE MODE: Finding item 0x{actual_item_id:X} in backpack", 68)
        item = Items.FindByID(actual_item_id, -1, Player.Backpack.Serial)
        if not item:
            debug_message(f"ERROR: Item 0x{actual_item_id:X} not found in backpack", 33)
            return False
        
        debug_message(f"Found item: Serial={item.Serial}, ItemID=0x{item.ItemID:X}", 68)
        
        z_final = compute_target_z(x_int, y_int, base_z)
        debug_message(f"Computed z_final: {z_final} (type: {type(z_final)})", 68)
        
        # Check if we're close enough to place without moving (within 2 tiles)
        current_x = Player.Position.X
        current_y = Player.Position.Y
        distance = max(abs(current_x - x_int), abs(current_y - y_int))
        debug_message(f"Distance to target: {distance} tiles from ({current_x},{current_y}) to ({x_int},{y_int})", 68)
        
        if distance <= 2:
            debug_message(f"Close enough ({distance} tiles) - placing without moving", 68)
        else:
            # Move to location if needed
            debug_message(f"Too far ({distance} tiles) - moving to location ({x_int},{y_int})", 68)
            if not goto_location_with_wiggle(x_int, y_int):
                debug_message(f"ERROR: Cannot reach ({x_int},{y_int}) for placement", 33)
                return False
            debug_message(f"Successfully moved to ({x_int},{y_int})", 68)
        
        # Place the item at world coordinates using MoveOnGround like RITUAL_orbs.py
        actual_z = -1 if USE_AUTO_Z_STACKING else int(z_final)
        debug_message(f"Calling MoveOnGround: Serial={item.Serial} (type: {type(item.Serial)}), amount=1, x={x_int} (type: {type(x_int)}), y={y_int} (type: {type(y_int)}), z={actual_z} (type: {type(actual_z)})", 68)
        
        Items.MoveOnGround(item.Serial, 1, x_int, y_int, actual_z)
        debug_message(f"MoveOnGround call completed successfully", 68)
        
        throttle()
        pause_ms(PAUSE_DURATION_PLACE)
        
        if hue is not None:
            debug_message(f"Hue specified: {hue} (not implemented)", 68)
            pass
        
        if ENABLE_STACK_TRACKING:
            PLACED_TOP_Z[(x_int, y_int)] = z_final
        
        debug_message(f"Item placement successful at ({x_int},{y_int})", 67)
        return True
        
    except Exception as e:
        debug_message(f"ERROR: Exception in place_item at ({x_int},{y_int}): {type(e).__name__}: {e}", 33)
        import traceback
        debug_message(f"Traceback: {traceback.format_exc()}", 33)
        return False

def place_items_at_points(points, item_id, base_z, progress_msg="Placing items", center=None, hue=None):
    """Place items at multiple points with progress tracking"""
    if not points:
        return
    
    total = len(points)
    failures = 0
    
    for i, (x, y) in enumerate(points, 1):
        debug_message(f"{progress_msg}: {i} out of {total}", 68)
        
        if place_item(int(x), int(y), item_id, base_z, hue):
            # Handle case where item_id might be a list
            display_id = item_id[0] if isinstance(item_id, list) else item_id
            debug_message(f"Placed item 0x{display_id:X} at ({x},{y})", 68)
        else:
            failures += 1
            # Handle case where item_id might be a list
            display_id = item_id[0] if isinstance(item_id, list) else item_id
            debug_message(f"Failed to place item 0x{display_id:X} at ({x},{y})", 33)
        
        if failures >= MAX_PHASE_FAILURES:
            debug_message(f"Too many failures ({failures}), stopping placement", 33)
            break
        
        pause_ms(POINT_BREATHER_MS)
    
    debug_message(f"{progress_msg} complete: {total - failures}/{total} successful", 67)

def place_mixed_items_at_points(points, item_ids, base_z, progress_msg="Placing mixed items", center=None, hue=None):
    """Place items at multiple points, randomly selecting from available item IDs for each point"""
    if not points or not item_ids:
        return
    
    total = len(points)
    failures = 0
    
    for i, (x, y) in enumerate(points, 1):
        debug_message(f"{progress_msg}: {i} out of {total}", 68)
        
        # Randomly select an item ID for this point
        selected_item_id = random.choice(item_ids)
        
        if place_item(int(x), int(y), selected_item_id, base_z, hue):
            debug_message(f"Placed mixed item 0x{selected_item_id:X} at ({x},{y})", 68)
        else:
            failures += 1
            debug_message(f"Failed to place mixed item 0x{selected_item_id:X} at ({x},{y})", 33)
        
        if failures >= MAX_PHASE_FAILURES:
            debug_message(f"Too many failures ({failures}), stopping placement", 33)
            break
        
        pause_ms(POINT_BREATHER_MS)
    
    debug_message(f"{progress_msg} complete: {total - failures}/{total} successful", 67)

def place_stacked_items_at_point(x, y, item_id, stack_count, base_z, hue=None):
    """Place multiple items stacked at a single point"""
    if stack_count <= 0:
        return False
    
    success_count = 0
    for i in range(stack_count):
        if place_item(int(x), int(y), item_id, base_z, hue):
            success_count += 1
            if PREVIEW_MODE:
                pause_ms(PEARL_STACK_PREVIEW_DELAY_MS)
        else:
            break
    
    return success_count > 0

# ===== MATERIAL MOVEMENT FUNCTIONS =====
def move_materials_to_target_container():
    """Move required ritual materials to target container based on current configuration"""
    if not MOVE_MATERIALS_TO_TARGET_CONTAINER:
        debug_message("Material movement disabled, skipping", 67)
        return True
    
    debug_message("Moving required materials to target container...", 67)
    
    # Get current ritual requirements
    requirements = calculate_death_ritual_requirements()
    if not requirements:
        debug_message("No material requirements calculated", 33)
        return False
    
    # Check if target container exists
    target_container = Items.FindBySerial(TARGET_CONTAINER_SERIAL)
    if not target_container:
        debug_message(f"Target container 0x{TARGET_CONTAINER_SERIAL:X} not found", 33)
        return False
    
    debug_message(f"Target container found: 0x{TARGET_CONTAINER_SERIAL:X}", 67)
    
    total_moved = 0
    total_failed = 0
    
    for material_name, required_count in requirements.items():
        if required_count <= 0:
            continue
            
        debug_message(f"Moving {required_count} {material_name}...", 67)
        
        # Get item IDs for this material
        item_ids = MATERIAL_ITEM_IDS.get(material_name, [])
        if not item_ids:
            debug_message(f"No item IDs found for {material_name}", 33)
            total_failed += required_count
            continue
        
        moved_count = 0
        for item_id in item_ids:
            if moved_count >= required_count:
                break
                
            # Find items in backpack
            backpack_items = Items.FindByID(item_id, -1, Player.Backpack.Serial)
            
            # Handle case where FindByID returns a single item instead of a list
            if backpack_items and not hasattr(backpack_items, '__iter__'):
                backpack_items = [backpack_items]
            elif not backpack_items:
                backpack_items = []
            
            for item in backpack_items:
                if moved_count >= required_count:
                    break
                    
                # Calculate how many to move from this stack
                stack_amount = item.Amount if hasattr(item, 'Amount') else 1
                needed = required_count - moved_count
                move_amount = min(stack_amount, needed)
                
                debug_message(f"Moving {move_amount} of item 0x{item_id:X} (stack: {stack_amount})", 68)
                
                try:
                    # Move items to target container
                    if Items.Move(item, TARGET_CONTAINER_SERIAL, move_amount):
                        moved_count += move_amount
                        total_moved += move_amount
                        debug_message(f"Moved {move_amount} {material_name} successfully", 68)
                        Misc.Pause(250)  # Brief pause between moves
                    else:
                        debug_message(f"Failed to move {move_amount} {material_name}", 33)
                        total_failed += move_amount
                except Exception as e:
                    debug_message(f"Error moving {material_name}: {e}", 33)
                    total_failed += move_amount
        
        if moved_count < required_count:
            shortage = required_count - moved_count
            debug_message(f"Shortage: {shortage} {material_name} not found in backpack", 33)
            total_failed += shortage
    
    debug_message(f"Material movement complete: {total_moved} moved, {total_failed} failed/missing", 67)
    return total_failed == 0

# ===== CENTER CRACK FUNCTIONS =====
def build_center_cracks(center_x, center_y, center_z):
    """Build the center crack pattern using cloth and eye of newt"""
    if not ENABLE_CENTER_CRACKS:
        debug_message("Center cracks disabled, skipping", 68)
        return
    
    debug_message("Building center crack pattern...", 67)
    
    # Build cloth cracks (main layer)
    if ENABLE_CENTER_CRACKS_CLOTH:
        cloth_id = MATERIAL_ITEM_IDS.get("Cloth")
        if cloth_id:
            build_crack_layer(center_x, center_y, center_z, cloth_id, 
                            CENTER_CRACK_ARMS, CENTER_CRACK_MIN_LEN, CENTER_CRACK_MAX_LEN,
                            "Cloth cracks", hue=DEFAULT_CLOTH_HUE)
    
    # Build eye of newt cracks (mystical layer)
    if ENABLE_CENTER_CRACKS_EYE_NEWT:
        newt_id = get_first_available_item_id(MATERIAL_ITEM_IDS.get("Eye of Newt", []))
        if newt_id:
            build_crack_layer(center_x, center_y, center_z, newt_id,
                            CENTER_CRACK_ARMS, CENTER_CRACK_MIN_LEN, CENTER_CRACK_MAX_LEN,
                            "Eye of newt cracks")
    
    # Build black pearl cracks (mystical layer)
    if ENABLE_CENTER_CRACKS_PEARL:
        pearl_id = get_first_available_item_id(MATERIAL_ITEM_IDS.get("Black Pearl", []))
        if pearl_id:
            build_crack_layer(center_x, center_y, center_z, pearl_id,
                            PEARL_CRACK_ARMS, PEARL_CRACK_MIN_LEN, PEARL_CRACK_MAX_LEN,
                            "Black pearl cracks")

def build_crack_layer(center_x, center_y, center_z, item_id, num_arms, min_len, max_len, layer_name, hue=None):
    """Build a single crack layer with branching arms"""
    debug_message(f"Building {layer_name} with {num_arms} arms", 67)
    
    all_crack_points = []
    
    for arm_idx in range(num_arms):
        angle_deg = (360.0 * arm_idx / num_arms)
        
        # Generate crack arm with branching
        crack_points = generate_crack_arm(
            center_x, center_y, angle_deg, min_len, max_len,
            CENTER_CRACK_BRANCH_CHANCE, CENTER_CRACK_MAX_BRANCHES_PER_ARM
        )
        
        # Skip the center point to avoid overlap
        crack_points = crack_points[1:] if crack_points else []
        all_crack_points.extend(crack_points)
    
    # Remove duplicates while preserving order
    unique_points = []
    seen = set()
    for point in all_crack_points:
        if point not in seen:
            unique_points.append(point)
            seen.add(point)
    
    debug_message(f"{layer_name}: generated {len(unique_points)} unique points", 67)
    
    if unique_points:
        place_items_at_points(unique_points, item_id, center_z, f"Placing {layer_name}", hue=hue)

def build_center_pearl_rings(center_x, center_y, center_z):
    """Build black pearl rings and stacked cracks around center"""
    if not ENABLE_CENTER_PEARL:
        debug_message("Center pearl rings disabled, skipping", 68)
        return
    
    debug_message("Building center pearl rings...", 67)
    
    pearl_id = get_first_available_item_id(MATERIAL_ITEM_IDS.get("Black Pearl", []))
    if not pearl_id:
        debug_message("No black pearls available for center rings", 33)
        return
    
    # Build concentric pearl rings
    for i, radius in enumerate(CENTER_PEARL_RING_RADII):
        points_count = CENTER_PEARL_RING_POINTS[i] if i < len(CENTER_PEARL_RING_POINTS) else CENTER_PEARL_RING_POINTS[-1]
        ring_points = generate_circle_points(center_x, center_y, radius, points_count)
        
        # Filter out excluded coordinates
        ring_points = [(x, y) for x, y in ring_points if not is_coordinate_excluded(x, y)]
        
        if ring_points:
            place_items_at_points(ring_points, pearl_id, center_z, f"Pearl ring {i+1} (radius {radius})")
    
    # Build pearl crack arms with stacking (only if enabled)
    if ENABLE_CENTER_CRACKS_PEARL:
        build_pearl_crack_arms(center_x, center_y, center_z, pearl_id)

def build_pearl_crack_arms(center_x, center_y, center_z, pearl_id):
    """Build black pearl crack arms with center stacking"""
    debug_message(f"Building pearl crack arms with stacking", 67)
    
    all_crack_points = []
    
    for arm_idx in range(PEARL_CRACK_ARMS):
        angle_deg = (360.0 * arm_idx / PEARL_CRACK_ARMS)
        
        # Generate crack arm
        crack_points = generate_crack_arm(
            center_x, center_y, angle_deg, PEARL_CRACK_MIN_LEN, PEARL_CRACK_MAX_LEN,
            CENTER_CRACK_BRANCH_CHANCE, CENTER_CRACK_MAX_BRANCHES_PER_ARM
        )
        
        all_crack_points.extend(crack_points)
    
    # Calculate stacking amounts based on distance from center
    stacked_placements = {}
    for x, y in all_crack_points:
        if is_coordinate_excluded(x, y):
            continue
        
        distance = math.hypot(x - center_x, y - center_y)
        
        # Calculate stack count with falloff
        if distance == 0:
            stack_count = PEARL_STACK_MAX
        else:
            # Exponential falloff with sigma shaping
            falloff_factor = math.exp(-(distance / PEARL_STACK_SIGMA) ** 2)
            stack_count = max(1, int(PEARL_STACK_MAX * falloff_factor))
        
        stacked_placements[(x, y)] = stack_count
    
    # Place stacked pearls
    total_points = len(stacked_placements)
    for i, ((x, y), stack_count) in enumerate(stacked_placements.items(), 1):
        debug_message(f"Pearl stacking: {i} out of {total_points} (stack: {stack_count})", 68)
        place_stacked_items_at_point(int(x), int(y), pearl_id, stack_count, center_z)
        pause_ms(POINT_BREATHER_MS)

# ===== PILLAR CONSTRUCTION =====
def build_pillar_at(x, y, center_z):
    """Build a death pillar: cloth -> stacked plant bowls -> lantern"""
    cloth_id = MATERIAL_ITEM_IDS.get("Cloth")[0] if MATERIAL_ITEM_IDS.get("Cloth") else None
    bowl_id = MATERIAL_ITEM_IDS.get("Plant Bowl")[0] if MATERIAL_ITEM_IDS.get("Plant Bowl") else None
    lantern_id = MATERIAL_ITEM_IDS.get("Lantern")[0] if MATERIAL_ITEM_IDS.get("Lantern") else None
    
    debug_message(f"Building pillar at ({x},{y}) with cloth_id=0x{cloth_id:X if cloth_id else 0}, bowl_id=0x{bowl_id:X if bowl_id else 0}, lantern_id=0x{lantern_id:X if lantern_id else 0}", 67)
    
    if not is_safe_ground(x, y):
        debug_message(f"Unsafe ground at ({x},{y}), skipping pillar", 33)
        return center_z + 2  # Return a reasonable Z for decorations even if pillar fails
    
    # Move to pillar location
    if not PREVIEW_MODE:
        if not goto_location_with_wiggle(int(x), int(y)):
            debug_message(f"Cannot reach pillar location ({x},{y})", 33)
            return center_z + 2  # Return a reasonable Z for decorations even if pillar fails
    
    # 1) Base cloth - continue even if this fails
    z_cloth = center_z
    cloth_placed = False
    if cloth_id:
        if place_item(x, y, cloth_id, z_cloth, hue=DEFAULT_CLOTH_HUE):
            cloth_placed = True
            debug_message(f"Base cloth placed at ({x},{y})", 67)
        else:
            debug_message(f"Failed to place base cloth at ({x},{y}) - continuing anyway", 33)
    
    # 2) Stack plant bowls
    top_z = z_cloth
    if bowl_id and PILLAR_BOWL_STACK_COUNT > 0:
        debug_message(f"Attempting to stack {PILLAR_BOWL_STACK_COUNT} bowls with item_id=0x{bowl_id:X}", 67)
        for i in range(PILLAR_BOWL_STACK_COUNT):
            bowl_z = z_cloth + (i + 1) * STACK_Z_STEP
            bowl_z_final = compute_target_z(x, y, bowl_z)
            debug_message(f"Pillar: placing bowl {i+1}/{PILLAR_BOWL_STACK_COUNT} id=0x{bowl_id:X} at ({x},{y}) proposed_z={bowl_z} -> final_z={bowl_z_final}", 67)
            
            # Check if we have bowls available
            try:
                bowl_count = Items.BackpackCount(bowl_id, -1)
                debug_message(f"Bowl count in backpack: {bowl_count}", 67)
                if bowl_count <= 0:
                    debug_message(f"No more bowls available, stopping at bowl {i+1}", 33)
                    break
            except Exception as e:
                debug_message(f"Error checking bowl count: {e}", 33)
                break
            
            if place_item(x, y, bowl_id, bowl_z):
                top_z = bowl_z_final
                debug_message(f"Bowl {i+1}/{PILLAR_BOWL_STACK_COUNT} placed successfully", 67)
            else:
                debug_message(f"Bowl {i+1}/{PILLAR_BOWL_STACK_COUNT} failed to place - continuing with remaining bowls", 33)
    
    # 3) Place lantern on top
    lantern_z = top_z + STACK_TOP_EXTRA
    if lantern_id:
        lantern_z_final = compute_target_z(x, y, lantern_z)
        debug_message(f"Pillar: placing lantern 0x{lantern_id:X} at ({x},{y}) proposed_z={lantern_z} -> final_z={lantern_z_final}", 67)
        if place_item(x, y, lantern_id, lantern_z):
            top_z = lantern_z_final
            debug_message(f"Lantern placed successfully at ({x},{y})", 67)
        else:
            debug_message(f"Lantern failed to place at ({x},{y}) - continuing anyway", 33)
    
    # 4) Return orb placement Z
    orb_z = top_z + STACK_TOP_EXTRA
    debug_message(f"Pillar at ({x},{y}) complete, orb Z: {orb_z}", 67)
    return orb_z

def place_death_orb(x, y, orb_z):
    """Place a death orb at the specified location"""
    orb_id = ORB_ITEM_ID
    if not orb_id:
        debug_message("Death orb item ID not configured", 33)
        return False
    
    return place_item(x, y, orb_id, orb_z, hue=DEATH_ORB_HUE)

# ===== DECORATION FUNCTIONS =====
def place_pillar_decorations(pillar_x, pillar_y, center_x, center_y, center_z):
    """Place death-themed decorations around a pillar"""
    if not ENABLE_PILLAR_DECORATIONS:
        return
    
    debug_message(f"Placing decorations around pillar at ({pillar_x},{pillar_y})", 67)
    
    decorations = DEATH_PILLAR_CONFIG.get("decorations", [])
    debug_message(f"Found {len(decorations)} decoration configurations", 67)
    
    for i, decoration in enumerate(decorations):
        dec_type = decoration.get("type")
        item_ids = decoration.get("item_ids", [])
        
        debug_message(f"Decoration {i+1}: type={dec_type}, item_ids={[hex(id) if id else None for id in item_ids]}", 67)
        
        # Get available item IDs for this decoration type
        available_item_ids = []
        for item_id in item_ids:
            if item_id is None:
                debug_message(f"Skipping None item_id", 68)
                continue
            # Check if we have this item available (or in preview mode)
            if not PREVIEW_MODE:
                try:
                    count = Items.BackpackCount(item_id, -1)
                    debug_message(f"Item 0x{item_id:X} count in backpack: {count}", 67)
                    if count > 0:
                        available_item_ids.append(item_id)
                except Exception as e:
                    debug_message(f"Error checking item 0x{item_id:X}: {e}", 33)
                    continue
            else:
                available_item_ids.append(item_id)  # In preview mode, assume all are available
        
        if not available_item_ids:
            debug_message(f"No available items for {dec_type} decoration {i+1}", 33)
            continue
            
        debug_message(f"Placing {dec_type} decoration with {len(available_item_ids)} available item types around pillar", 67)
        
        if dec_type == "ring":
            radius = decoration.get("radius", 2)
            points = decoration.get("points", 8)
            rotation = decoration.get("rotation", 0)
            
            ring_points = generate_circle_points(pillar_x, pillar_y, radius, points, rotation)
            debug_message(f"Generated {len(ring_points)} ring points around pillar at ({pillar_x},{pillar_y})", 67)
            
            # Filter out points too close to center
            ring_points = filter_points_outside_radius(ring_points, (center_x, center_y), 2, forbidden={(pillar_x, pillar_y)})
            debug_message(f"After filtering: {len(ring_points)} ring points remain", 67)
            
            if ring_points:
                debug_message(f"Ring points to place: {ring_points}", 67)
                place_mixed_items_at_points(ring_points, available_item_ids, center_z, f"Decoration ring around pillar")
                # Continue to next decoration type instead of breaking
            else:
                debug_message(f"No valid ring points after filtering for radius {radius}", 33)
        
        elif dec_type == "line":
            length = decoration.get("length", 4)
            spacing = decoration.get("spacing", 1)
            direction = decoration.get("direction", "inward")
            start_offset = decoration.get("start_offset", 1)
            
            # Calculate angle from pillar to center
            angle_to_center = math.degrees(math.atan2(center_y - pillar_y, center_x - pillar_x))
            
            if direction == "inward":
                line_angle = angle_to_center
            else:  # outward
                line_angle = angle_to_center + 180
            
            # Generate line points with offset
            start_x = pillar_x + int(start_offset * math.cos(math.radians(line_angle)))
            start_y = pillar_y + int(start_offset * math.sin(math.radians(line_angle)))
            
            line_points = generate_line_points(start_x, start_y, line_angle, length, spacing)
            debug_message(f"Generated {len(line_points)} line points from pillar", 67)
            
            # Filter out problematic points
            line_points = filter_points_outside_radius(line_points, (center_x, center_y), 2, forbidden={(pillar_x, pillar_y)})
            debug_message(f"After filtering: {len(line_points)} line points remain", 67)
            
            if line_points:
                debug_message(f"Line points to place: {line_points}", 67)
                place_mixed_items_at_points(line_points, available_item_ids, center_z, f"Decoration line from pillar")
                # Continue to next decoration type instead of breaking
            else:
                debug_message(f"No valid line points after filtering", 33)

# ===== MAIN RITUAL FUNCTIONS =====
def display_configuration():
    """Display the current ritual configuration"""
    debug_message("Death Ritual Configuration:", 67)
    debug_message(f"Preview: {'ON' if PREVIEW_MODE else 'OFF'}; Safe mode: {'ON' if SAFE_MODE else 'OFF'}", 67)
    debug_message(f"Death circle radius: {DEATH_CIRCLE['radius']}, rotation: {DEATH_CIRCLE['rotation']}, pillars: {DEATH_CIRCLE['count']}", 67)
    debug_message(f"Center: cracks={'ON' if ENABLE_CENTER_CRACKS else 'OFF'}, pearls={'ON' if ENABLE_CENTER_PEARL else 'OFF'}", 67)
    debug_message(f"Pillars: center_orb={'ON' if ENABLE_CENTER_ORB else 'OFF'}, death_pillars={'ON' if ENABLE_DEATH_PILLARS else 'OFF'}, decorations={'ON' if ENABLE_PILLAR_DECORATIONS else 'OFF'}", 67)
    debug_message(f"Crack arms: {CENTER_CRACK_ARMS}, length: {CENTER_CRACK_MIN_LEN}-{CENTER_CRACK_MAX_LEN}", 67)
    debug_message(f"Pearl rings: {len(CENTER_PEARL_RING_RADII)} rings at radii {CENTER_PEARL_RING_RADII}", 67)

def initialize_seed():
    """Initialize the random seed for reproducible patterns"""
    global CURRENT_SEED
    
    if USE_RANDOM_SEED:
        if PREFERRED_SEEDS:
            CURRENT_SEED = random.choice(PREFERRED_SEEDS)
            debug_message(f"Using preferred seed: {CURRENT_SEED}", 67)
        else:
            CURRENT_SEED = random.randint(1, 99999)
            debug_message(f"Using random seed: {CURRENT_SEED}", 67)
    else:
        CURRENT_SEED = FIXED_SEED
        debug_message(f"Using fixed seed: {CURRENT_SEED}", 67)
    
    random.seed(CURRENT_SEED)
    return CURRENT_SEED

def create_death_ritual(center_x, center_y):
    """Create the complete death ritual arrangement"""
    debug_message("Beginning Death Ritual arrangement...", 67)
    
    # Initialize seed for reproducible patterns
    seed = initialize_seed()
    debug_message(f"Death Ritual Seed: {seed}", 67)
    
    center_z = Player.Position.Z
    
    # Move to center position if not in preview mode
    if not PREVIEW_MODE:
        if not goto_location_with_wiggle(int(center_x), int(center_y), center=(int(center_x), int(center_y))):
            debug_message("Could not reach center position!", 33)
            return
    
    # Phase 0: Place dark cloth at center as foundation
    debug_message("Phase 0: Placing dark cloth at center...", 67)
    cloth_id = DEATH_ITEMS["cloth"]
    if place_item(center_x, center_y, cloth_id, center_z, hue=0x0001):  # Dark hue
        debug_message("Dark cloth placed at center", 67)
    else:
        debug_message("Failed to place center cloth", 33)
    
    # Phase 1: Build center layers (cracks and pearl rings)
    debug_message("Phase 1: Building center layers...", 67)
    build_center_cracks(center_x, center_y, center_z)
    build_center_pearl_rings(center_x, center_y, center_z)
    
    # Phase 2: Build center orb pillar
    if ENABLE_CENTER_ORB:
        debug_message("Phase 2: Building center death orb pillar...", 67)
        center_orb_z = build_pillar_at(center_x, center_y, center_z)
        if center_orb_z:
            if place_death_orb(center_x, center_y, center_orb_z):
                debug_message("Center death orb placed successfully", 67)
            else:
                debug_message("Failed to place center death orb", 33)
        else:
            debug_message("Failed to build center pillar", 33)
    
    # Phase 3: Build surrounding death pillars
    if ENABLE_DEATH_PILLARS:
        debug_message("Phase 3: Building surrounding death pillars...", 67)
        pillar_positions = get_death_pillar_positions(center_x, center_y)
        
        for i, (px, py) in enumerate(pillar_positions, 1):
            debug_message(f"Building death pillar {i}/{len(pillar_positions)} at ({px},{py})", 67)
            
            # Build pillar
            pillar_orb_z = build_pillar_at(px, py, center_z)
            # Always try to place orb and decorations, even if pillar construction was partial
        
            # Place death orb on pillar
            if place_death_orb(px, py, pillar_orb_z):
                debug_message(f"Death pillar {i} orb placed successfully", 67)
            else:
                debug_message(f"Failed to place orb on death pillar {i}", 33)
        
            # Always try decorations regardless of pillar success
            if ENABLE_PILLAR_DECORATIONS:
                place_pillar_decorations(px, py, center_x, center_y, center_z)
    
    debug_message("Death Ritual arrangement complete!", 67)

def calculate_death_ritual_requirements():
    """Calculate and display item requirements for the death ritual"""
    debug_message("Calculating death ritual requirements...", 67)
    
    requirements = {}
    
    def add_requirement(item_name, count):
        if item_name in requirements:
            requirements[item_name] += count
        else:
            requirements[item_name] = count
    
    # Center crack requirements
    if ENABLE_CENTER_CRACKS:
        if ENABLE_CENTER_CRACKS_CLOTH:
            cloth_estimate = CENTER_CRACK_ARMS * ((CENTER_CRACK_MIN_LEN + CENTER_CRACK_MAX_LEN) // 2)
            branch_estimate = int(cloth_estimate * CENTER_CRACK_BRANCH_CHANCE * CENTER_CRACK_MAX_BRANCHES_PER_ARM)
            add_requirement("Cloth", cloth_estimate + branch_estimate)
        
        if ENABLE_CENTER_CRACKS_EYE_NEWT:
            newt_estimate = CENTER_CRACK_ARMS * ((CENTER_CRACK_MIN_LEN + CENTER_CRACK_MAX_LEN) // 2)
            branch_estimate = int(newt_estimate * CENTER_CRACK_BRANCH_CHANCE * CENTER_CRACK_MAX_BRANCHES_PER_ARM)
            add_requirement("Eye of Newt", newt_estimate + branch_estimate)
    
    # Center pearl requirements
    pearl_total = 0
    if ENABLE_CENTER_PEARL:
        pearl_rings_total = sum(CENTER_PEARL_RING_POINTS)
        pearl_total += pearl_rings_total
    
    if ENABLE_CENTER_CRACKS_PEARL:
        pearl_cracks_estimate = PEARL_CRACK_ARMS * ((PEARL_CRACK_MIN_LEN + PEARL_CRACK_MAX_LEN) // 2)
        pearl_stacking_multiplier = (PEARL_STACK_MAX + 1) // 2  # Average stacking
        pearl_total += pearl_cracks_estimate * pearl_stacking_multiplier
    
    if pearl_total > 0:
        add_requirement("Black Pearl", pearl_total)
    
    # Pillar requirements
    total_pillars = 0
    if ENABLE_CENTER_ORB:
        total_pillars += 1
    if ENABLE_DEATH_PILLARS:
        total_pillars += DEATH_CIRCLE["count"]
    
    if total_pillars > 0:
        add_requirement("Cloth", requirements.get("Cloth", 0) + total_pillars)  # Base cloth per pillar
        add_requirement("Plant Bowl", total_pillars * PILLAR_BOWL_STACK_COUNT)  # Stacked bowls
        add_requirement("Lantern", total_pillars)  # Top lantern
        add_requirement("Death Orb", total_pillars)  # Orbs
    
    # Decoration requirements (rough estimates)
    if ENABLE_PILLAR_DECORATIONS and ENABLE_DEATH_PILLARS:
        decorations = DEATH_PILLAR_CONFIG.get("decorations", [])
        pillar_count = DEATH_CIRCLE["count"]
        
        for decoration in decorations:
            if decoration.get("type") == "ring":
                points = decoration.get("points", 8)
                add_requirement("Bones/Bone Items", pillar_count * points)
            elif decoration.get("type") == "line":
                length = decoration.get("length", 4)
                add_requirement("Bones/Bone Items", pillar_count * length)
    
    # Display requirements
    debug_message("=== DEATH RITUAL REQUIREMENTS ===", 67)
    total_items = 0
    for item_name, count in sorted(requirements.items()):
        debug_message(f"{item_name}: {count}", 68)
        total_items += count
    
    debug_message(f"Total items needed: {total_items}", 67)
    debug_message("=== END REQUIREMENTS ===", 67)
    
    return requirements

def main():
    """Main execution function"""
    display_configuration()
    
    # Move materials to target container if enabled
    if MOVE_MATERIALS_TO_TARGET_CONTAINER:
        debug_message("Material movement enabled, attempting to move materials...", 67)
        if not move_materials_to_target_container():
            debug_message("Material movement failed, stopping ritual", 33)
            return
    else:
        debug_message("Material movement disabled, proceeding with ritual", 67)
    
    # Get player position as center
    center_x = Player.Position.X
    center_y = Player.Position.Y
    
    # Initialize exclusion zone around center
    initialize_exclusion_zone(center_x, center_y)
    
    # Show requirements if in debug mode
    if DEBUG_MODE:
        calculate_death_ritual_requirements()
    
    # Create the death ritual
    create_death_ritual(center_x, center_y)

if __name__ == "__main__":
    main()