"""
Ritual of the Spiral - a Razor Enhanced Python Script for Ultima Online

Places a black pearl spiral pattern using ritual framework.
Generates an spiral with configurable parameters.

Current Items = Black pearl (0x0F7A)

VERSION = 20250907
"""

import math
import time
import random

DEBUG_MODE = False # default = false , set to true for debug messages
SAFE_MODE = False  # extra slow pacing and movement

# Preview mode: when True, does not move or place real items. Instead, render client-side
# fake items at the target coordinates using PacketLogger.SendToClient
PREVIEW_MODE = False
PREVIEW_DEFAULT_HUE = 0x0000  # 0 means no hue

# Item Configuration
# Default spiral: Black Pearl (0x0F7A)
# Antispiral: Arcane Dust (0x5745)
BLACK_PEARL_ITEM_IDS = {
    "Black Pearl": [0x0F7A],
}
ARCANE_DUST_ITEM_IDS = {
    "Arcane Dust": [0x5745],
}
ITEM_NAME_LOOKUP = {}
ITEM_NAME_LOOKUP.update(BLACK_PEARL_ITEM_IDS)
ITEM_NAME_LOOKUP.update(ARCANE_DUST_ITEM_IDS)

# Spiral generation parameters
SPIRAL_RADIUS = 7  # Maximum radius of spiral (increased for larger scale)
SPIRAL_SPACING = 4   # Distance between spiral arms (tiles) - wider for thicker appearance
SPIRAL_TURNS = 4.0  # Number of full turns the spiral makes (extended for longer spiral)

# Thickness and stacking parameters
SPIRAL_THICKNESS = 2  # Number of parallel lines to create thickness
RANDOM_STACKING_ENABLED = True  # Enable random stacking towards center
MAX_STACK_HEIGHT = 1  # Maximum items to stack at one location
CENTER_STACK_BIAS = 0.7  # Higher values = more stacking towards center (0.0-1.0)

# Global stacking control parameters
MAX_STACKS_PER_LOCATION = 3  # Maximum number of items to place at any single coordinate
ENFORCE_STACK_LIMIT = True   # If True, strictly enforce the stack limit per location

# Item management
SKIP_ITEM_COUNT_CHECK = True  # If True, place whatever items available without checking total needed

# Phase toggles for spiral components
# Enable exactly one (or both if desired) to place default spiral and/or antispiral.
PLACE_COMPONENTS = {
    "spiral_pattern": True,       # Default spiral with Black Pearl
    "antispiral_pattern": True,  # Antispiral with Arcane Dust
}

# Component Configuration: spiral patterns
# Both use the same algorithm; antispiral uses an angle_offset to interleave points without overlap.
RITUAL_CONFIG = {
    "spiral_pattern": {
        "label": "Black Pearl spiral",
        "item_ids": BLACK_PEARL_ITEM_IDS["Black Pearl"],
        "pattern": "spiral",
        "angle_offset": 0.0,  # radians
        "max_radius": SPIRAL_RADIUS,
        "spacing": SPIRAL_SPACING,
        "turns": SPIRAL_TURNS,
        "thickness": SPIRAL_THICKNESS,
        "radius_offset": 0.0,           # additional radial shift
        "theta_phase": 0.0,             # phase of theta sampling in [0,1) of one increment
        "random_stacking": RANDOM_STACKING_ENABLED,
        "max_stack_height": MAX_STACK_HEIGHT,
        "center_stack_bias": CENTER_STACK_BIAS,
        "skip_count_check": SKIP_ITEM_COUNT_CHECK,
        "max_stacks_per_location": MAX_STACKS_PER_LOCATION,
        "enforce_stack_limit": ENFORCE_STACK_LIMIT,
    },
    "antispiral_pattern": {
        "label": "Arcane Dust antispiral",
        "item_ids": ARCANE_DUST_ITEM_IDS["Arcane Dust"],
        "pattern": "spiral",
        "angle_offset": 1.57079632679,  # ~pi/2 radians (90 degrees)
        "max_radius": SPIRAL_RADIUS,
        "spacing": SPIRAL_SPACING,
        "turns": SPIRAL_TURNS,
        "thickness": SPIRAL_THICKNESS,
        "radius_offset": SPIRAL_SPACING / 2.0,  # shift half the inter-arm spacing to sit between arms
        "theta_phase": 0.5,                     # sample halfway between base points to avoid rounding overlaps
        "random_stacking": RANDOM_STACKING_ENABLED,
        "max_stack_height": MAX_STACK_HEIGHT,
        "center_stack_bias": CENTER_STACK_BIAS,
        "skip_count_check": SKIP_ITEM_COUNT_CHECK,
        "max_stacks_per_location": MAX_STACKS_PER_LOCATION,
        "enforce_stack_limit": ENFORCE_STACK_LIMIT,
    },
}

# Constants 
PAUSE_DURATION = 350        # General pause between actions (ms)
PAUSE_DURATION_PLACE = 550  # Pause after placing item (ms)
PREVIEW_PAUSE_DURATION = 25 # Fast pause for preview mode (ms)
PREVIEW_PAUSE_PLACE = 35    # Fast pause after preview placement (ms)
MAX_DISTANCE = 2

# Movement tuning 
GOTO_BASE_DELAY = 250       # base delay between movement attempts (ms)
GOTO_MAX_RETRIES = 1        # minimal retries
WIGGLE_RADII = [0]          # in SAFE_MODE we only try exact tile
WIGGLE_ANGLES = [0, 45, 90, 135, 180, 225, 270, 315]
WALK_REPEATS_PER_DIR = 2    # attempts per direction

# Center bias tuning 
CENTER_BIAS_ENABLED = True
CENTER_NUDGE_DISTANCE = 3
CENTER_NUDGE_STEPS = 2

# Placement tuning
PLACE_MAX_RETRIES = 1
PLACE_BACKOFF_BASE = 250
POINT_TIMEOUT_MS = 1500
POINT_BREATHER_MS = 250
PREVIEW_BREATHER_MS = 15    # Fast when using preview mode

# Global throttling / jitter 
RATE_MIN_GAP_MS = 350
LOOP_YIELD_MS = 40
JITTER_MS = 50
PREVIEW_MIN_GAP_MS = 10     # Minimal gap for preview mode
PREVIEW_JITTER_MS = 5       # Minimal jitter for preview
LAST_ACTION_MS = 0

# Phase fail-safe and dedupe
MAX_PHASE_FAILURES = 6
PLACED_COORDS_BY_ITEM = {}
ALL_PLACED_COORDS = set()  # legacy/global view (kept for debugging)
ALL_PLACED_COORDS_BY_COMPONENT = {}  # dict[str -> set[(x,y)]]
BAD_COORDS = set()

#//========================================================

def debug_message(msg, color=0):
    if DEBUG_MODE:
        try:
            Misc.SendMessage(msg, color)
        except Exception:
            print(msg)

def _convert_packet_to_bytes(packet_list):
    byte_list = []
    for value in packet_list:
        if value:
            byte_list.append(int(value, 16))
        else:
            byte_list.append(0)
    return byte_list

def _send_fake_item(item_x, item_y, item_z, item_id_4hex_with_space, hue_4hex_with_space):
    """Send a client-only item render at location without server state change."""
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
    s = f"{int(value) & 0xFFFF:04X}"
    return s[:2] + " " + s[2:]

def preview_item_at(x, y, z, item_id, hue=PREVIEW_DEFAULT_HUE):
    item_hex = _format_hex_4_with_space(item_id)
    hue_hex = _format_hex_4_with_space(hue)
    _send_fake_item(x, y, z, item_hex, hue_hex)

def generate_spiral_points(center_x, center_y, max_radius, spacing=SPIRAL_SPACING, turns=SPIRAL_TURNS, thickness=1, angle_offset=0.0, radius_offset=0.0, theta_phase=0.0, theta_increment=0.15):
    """Generate Archimedean spiral points with thickness and optional angular offset.

    angle_offset rotates the spiral around the center to create an "antispiral" that interleaves
    with the default spiral without overlapping.
    """
    points = []
    a = 0  # Start at center
    b = spacing / (2 * math.pi)  # Controls the distance between spiral arms
    theta = float(theta_phase) * float(theta_increment)
    max_theta = turns * 2 * math.pi
    added_points = set()  # Track unique points to avoid duplicates
    
    debug_message(f"Generating spiral: center=({center_x},{center_y}), radius={max_radius}, turns={turns}, thickness={thickness}, angle_offset={round(angle_offset,3)}", 67)
    
    # Safety limit to prevent infinite loops
    max_iterations = 10000
    iteration_count = 0
    
    # Generate base spiral
    while theta <= max_theta and iteration_count < max_iterations:
        r = a + b * theta + float(radius_offset)
        if r > max_radius:
            break
        
        # Create thickness by generating parallel spiral lines
        for offset in range(thickness):
            offset_r = r + (offset * 0.8)  # Slight radius offset for thickness
            if offset_r > max_radius:
                continue
                
            x = int(round(center_x + offset_r * math.cos(theta + angle_offset)))
            y = int(round(center_y + offset_r * math.sin(theta + angle_offset)))
            
            if (x, y) not in added_points:
                points.append((x, y))
                added_points.add((x, y))
                # Reduce debug spam - only show every 10th point
                if len(points) % 10 == 0:
                    debug_message(f"Generated {len(points)} spiral points so far...", 68)
        
        theta += float(theta_increment)  # keep consistent spacing
        iteration_count += 1
    
    if iteration_count >= max_iterations:
        debug_message(f"WARNING: Hit safety limit of {max_iterations} iterations", 33)
    
    debug_message(f"Generated {len(points)} total spiral points", 67)
    return points

def generate_stacked_points(points, center_x, center_y, max_stack_height, center_bias, max_stacks_per_location=None, enforce_limit=True):
    """Generate additional stacking points with bias towards center."""
    stacked_points = []
    
    for x, y in points:
        # Calculate distance from center for bias calculation
        distance_from_center = math.sqrt((x - center_x)**2 + (y - center_y)**2)
        max_distance = math.sqrt((SPIRAL_RADIUS)**2 + (SPIRAL_RADIUS)**2)
        
        # Normalize distance (0.0 = center, 1.0 = edge)
        normalized_distance = min(distance_from_center / max_distance, 1.0) if max_distance > 0 else 0
        
        # Calculate stack probability (higher towards center)
        stack_probability = center_bias * (1.0 - normalized_distance)
        
        # Determine number of additional stacks
        additional_stacks = 0
        for _ in range(max_stack_height - 1):
            if random.random() < stack_probability:
                additional_stacks += 1
            else:
                break
        
        # Apply global stack limit if enforced
        total_stacks = additional_stacks + 1
        if enforce_limit and max_stacks_per_location is not None:
            total_stacks = min(total_stacks, max_stacks_per_location)
            # Reduce debug spam for stack limiting
            if DEBUG_MODE and total_stacks != (additional_stacks + 1):
                debug_message(f"Limited stacks at ({x},{y}) to {total_stacks} (was {additional_stacks + 1})", 68)
        
        # Add the original point plus additional stacks
        for stack_level in range(total_stacks):
            stacked_points.append((x, y, stack_level))
    
    return stacked_points

def now_ms():
    return int(time.time() * 1000)

def pause_ms(ms):
    if PREVIEW_MODE:
        jitter = random.randint(0, PREVIEW_JITTER_MS)
    else:
        jitter = random.randint(0, JITTER_MS)
    Misc.Pause(int(ms + jitter))

def throttle(min_gap_ms=None):
    global LAST_ACTION_MS
    if min_gap_ms is None:
        min_gap_ms = PREVIEW_MIN_GAP_MS if PREVIEW_MODE else RATE_MIN_GAP_MS
    
    t = now_ms()
    if LAST_ACTION_MS == 0:
        LAST_ACTION_MS = t
        return
    elapsed = t - LAST_ACTION_MS
    if elapsed < min_gap_ms:
        Misc.Pause(min_gap_ms - elapsed)
    LAST_ACTION_MS = now_ms()

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

def is_valid_position(x, y, z=None):
    if z is None:
        z = Player.Position.Z
    return (
        Player.Position.X - MAX_DISTANCE <= x <= Player.Position.X + MAX_DISTANCE
        and Player.Position.Y - MAX_DISTANCE <= y <= Player.Position.Y + MAX_DISTANCE
        and Statics.GetLandID(x, y, Player.Map) not in [0x0001]
    )

def get_direction(from_x, from_y, to_x, to_y):
    dx = to_x - from_x
    dy = to_y - from_y

    if dx == 0:
        if dy < 0:
            return 0  # North
        return 4      # South
    elif dy == 0:
        if dx > 0:
            return 2  # East
        return 6      # West
    elif dx > 0:
        if dy < 0:
            return 1  # Northeast
        return 3      # Southeast
    else:
        if dy < 0:
            return 7  # Northwest
        return 5      # Southwest

def dir_to_str(d):
    mapping = {
        0: "North",
        1: "Northeast",
        2: "East",
        3: "Southeast",
        4: "South",
        5: "Southwest",
        6: "West",
        7: "Northwest",
    }
    return mapping.get(int(d) % 8, "North")

def attempt_walk_toward(tx, ty, max_steps=6):
    last_pos = (Player.Position.X, Player.Position.Y)
    step_delay = GOTO_BASE_DELAY
    for step in range(max_steps):
        if (abs(Player.Position.X - tx) <= MAX_DISTANCE and
            abs(Player.Position.Y - ty) <= MAX_DISTANCE):
            return True
        try:
            base_dir = get_direction(Player.Position.X, Player.Position.Y, tx, ty)
        except Exception:
            base_dir = 0

        dirs = [base_dir, (base_dir+1)%8, (base_dir+7)%8]
        moved = False
        for d in dirs:
            for rep in range(WALK_REPEATS_PER_DIR):
                try:
                    throttle()
                    Player.Walk(dir_to_str(d))
                except Exception as e:
                    debug_message(f"Walk error dir {d}: {e}", 33)
                    break
                pause_ms(step_delay)
                cur_pos = (Player.Position.X, Player.Position.Y)
                if cur_pos != last_pos:
                    moved = True
                    last_pos = cur_pos
                    break
            if moved:
                break
        if not moved:
            step_delay = int(step_delay * 1.3) + 50
            pause_ms(step_delay)
    return (abs(Player.Position.X - tx) <= MAX_DISTANCE and
            abs(Player.Position.Y - ty) <= MAX_DISTANCE)

def goto_location_with_wiggle(x, y, max_retries=GOTO_MAX_RETRIES, center=None):
    target_x = int(float(x))
    target_y = int(float(y))

    if not is_safe_ground(target_x, target_y):
        return False

    if attempt_walk_toward(target_x, target_y, max_steps=8):
        return True

    if CENTER_BIAS_ENABLED and center is not None:
        cx, cy = int(center[0]), int(center[1])
        dxc = abs(Player.Position.X - cx)
        dyc = abs(Player.Position.Y - cy)
        if dxc > CENTER_NUDGE_DISTANCE or dyc > CENTER_NUDGE_DISTANCE:
            attempt_walk_toward(cx, cy, max_steps=CENTER_NUDGE_STEPS)
            if attempt_walk_toward(target_x, target_y, max_steps=6):
                return True

    return (abs(Player.Position.X - target_x) <= MAX_DISTANCE and
            abs(Player.Position.Y - target_y) <= MAX_DISTANCE)

def place_item(x, y, item_id, z=None, stack_level=0):
    if PREVIEW_MODE:
        if z is None:
            z = -1 #Player.Position.Z - 1  # Always use z-1 for auto-stacking
        # Adjust z for stacking in preview
        preview_z = z - stack_level
        preview_item_at(x, y, preview_z, item_id, PREVIEW_DEFAULT_HUE)
        return True
    if item_id is None:
        return False
    offsets = [(0, 0)] if SAFE_MODE else [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
    if z is None:
        z = -1 #Player.Position.Z - 1  # Always use z-1 for auto-stacking

    for dx_off, dy_off in offsets:
        tx = x + dx_off
        ty = y + dy_off
        if not is_valid_position(tx, ty, z - stack_level):
            continue
        if not is_safe_ground(tx, ty):
            BAD_COORDS.add((tx, ty))
            continue
        for attempt in range(1, PLACE_MAX_RETRIES + 1):
            item = Items.FindByID(item_id, -1, Player.Backpack.Serial)
            if not item:
                debug_message(f"Could not find item 0x{item_id:X}", 33)
                return False

            try:
                initial_count = Items.BackpackCount(item_id, -1)
            except Exception as e:
                debug_message(f"BackpackCount error for 0x{item_id:X}: {e}", 33)
                return False
            if initial_count <= 0:
                return False

            try:
                # Force all items to be placed at actual -1 , not just Player.Position.Z - 1 for auto-stacking
                force_z = -1 # Player.Position.Z - 1
                Items.MoveOnGround(item, 1, tx, ty, force_z)
            except Exception as e:
                debug_message(f"MoveOnGround failed at ({tx},{ty},{force_z}): {e}", 33)
                BAD_COORDS.add((x, y))
                pause_ms(PAUSE_DURATION + 150)
                return False
            else:
                throttle()
                pause_ms(PAUSE_DURATION_PLACE)

            for _ in range(2):
                try:
                    new_count = Items.BackpackCount(item_id, -1)
                except Exception as e:
                    debug_message(f"BackpackCount verify error: {e}", 33)
                    break
                if new_count < initial_count:
                    return True
                pause_ms(PAUSE_DURATION)

            pause_ms(PLACE_BACKOFF_BASE * attempt)

    return False

def place_items_at_points(points, item_id, z=None, progress_msg="Placing spiral", center=None, component_key=None):
    if not points or item_id is None:
        return set()

    total = len(points)
    placed = set()
    failures = 0
    if item_id not in PLACED_COORDS_BY_ITEM:
        PLACED_COORDS_BY_ITEM[item_id] = set()

    for i, point in enumerate(points, 1):
        # Handle both 2D and 3D points (with stack level)
        if len(point) == 3:
            x, y, stack_level = point
        else:
            x, y = point
            stack_level = 0
        debug_message(f"{progress_msg}: {i} out of {total}", 67)

        start_ms = int(time.time() * 1000)

        if (x, y) in BAD_COORDS:
            debug_message(f"Skipping known-bad coord ({x},{y})", 33)
            continue

        # Cross-component dedupe: never place on a tile used by a different component
        if component_key is not None:
            for comp, coords_set in ALL_PLACED_COORDS_BY_COMPONENT.items():
                if comp == component_key:
                    continue  # allow stacking within same component
                if (x, y) in coords_set:
                    debug_message(f"Skipping coord used by component '{comp}' at ({x},{y})", 68)
                    continue_outer = True
                    break
            else:
                continue_outer = False
            if continue_outer:
                continue

        # Allow multiple items at same location for stacking within a component (handled by stack_level)
        # if (x, y) in PLACED_COORDS_BY_ITEM[item_id]:
        #     debug_message(f"Duplicate coords for Black Pearl at ({x},{y}), skipping.", 68)
        #     continue

        if not PREVIEW_MODE:
            if not goto_location_with_wiggle(x, y, center=center):
                debug_message(f"Could not reach position ({x}, {y})", 33)
                failures += 1
                if failures >= MAX_PHASE_FAILURES:
                    debug_message("Too many failures in this phase; aborting phase early.", 33)
                    break
                continue

        for attempt in range(1):
            if place_item(x, y, item_id, z, stack_level):
                placed.add((x, y, stack_level))
                PLACED_COORDS_BY_ITEM[item_id].add((x, y))
                ALL_PLACED_COORDS.add((x, y))
                if component_key is not None:
                    if component_key not in ALL_PLACED_COORDS_BY_COMPONENT:
                        ALL_PLACED_COORDS_BY_COMPONENT[component_key] = set()
                    ALL_PLACED_COORDS_BY_COMPONENT[component_key].add((x, y))
                break
            if PREVIEW_MODE:
                break
            pause_ms(PAUSE_DURATION)

            if int(time.time() * 1000) - start_ms > POINT_TIMEOUT_MS:
                debug_message(f"Timeout at point ({x},{y}), skipping.", 33)
                BAD_COORDS.add((x, y))
                failures += 1
                break

        if PREVIEW_MODE:
            pause_ms(PREVIEW_BREATHER_MS)
        else:
            pause_ms(POINT_BREATHER_MS)

    return placed

def get_first_available_item_id(item_ids, required_count):
    if isinstance(item_ids, int) or item_ids is None:
        item_ids = [item_ids]
    for item_id in item_ids:
        if item_id is None:
            continue
        if Items.BackpackCount(item_id, -1) >= required_count:
            return item_id
    for item_id in item_ids:
        if item_id is not None:
            return item_id
    return None

def place_pattern_component(center_x, center_y, config, z=None, component_key=None):
    points = []
    if config["pattern"] == "spiral":
        # Generate base spiral points
        base_points = generate_spiral_points(
            center_x,
            center_y,
            config["max_radius"],
            config["spacing"],
            config["turns"],
            config.get("thickness", 1),
            config.get("angle_offset", 0.0),
            config.get("radius_offset", 0.0),
            config.get("theta_phase", 0.0)
        )
        
        # Add random stacking if enabled
        if config.get("random_stacking", False):
            points = generate_stacked_points(
                base_points,
                center_x,
                center_y,
                config.get("max_stack_height", 3),
                config.get("center_stack_bias", 0.5),
                config.get("max_stacks_per_location"),
                config.get("enforce_stack_limit", True)
            )
        else:
            points = [(x, y, 0) for x, y in base_points]

    required = len(points) if points else 1
    if PREVIEW_MODE:
        item_ids = config["item_ids"] if isinstance(config["item_ids"], list) else [config["item_ids"]]
        item_id = next((i for i in item_ids if i is not None), None)
    else:
        item_id = get_first_available_item_id(config["item_ids"], required)
    if item_id is None:
        debug_message("Skipping component: item ID not set or not available.", 33)
        return set()
    verb = "Previewing" if PREVIEW_MODE else "Placing"
    return place_items_at_points(
        points,
        item_id,
        z,
        f"{verb} {config.get('label', 'spiral')}",
        center=(center_x, center_y),
        component_key=component_key
    )

def get_item_name(item_id):
    for name, ids in ITEM_NAME_LOOKUP.items():
        if isinstance(ids, list) and item_id in ids:
            return name
        if ids == item_id:
            return name
    return f"Item 0x{item_id:X}" if item_id is not None else "Unknown Item"

def display_configuration():
    debug_message("Current Spiral Configuration:", 67)
    for phase, config in RITUAL_CONFIG.items():
        active = PLACE_COMPONENTS.get(phase, False)
        item_ids = config["item_ids"] if isinstance(config["item_ids"], list) else [config["item_ids"]]
        names = ", ".join([get_item_name(i) for i in item_ids if i is not None])
        status = "ACTIVE" if active else "DISABLED"
        debug_message(f"{phase}: {names} - {status}", 68 if active else 33)

def calculate_item_totals():
    totals = {}
    for phase, config in RITUAL_CONFIG.items():
        if not PLACE_COMPONENTS[phase]:
            continue
        item_ids = config["item_ids"] if isinstance(config["item_ids"], list) else [config["item_ids"]]
        key = tuple([i for i in item_ids if i is not None])
        if not key:
            debug_message(f"{phase}: No valid item ID configured.", 33)
            continue
        if key not in totals:
            totals[key] = 0
        # Calculate spiral points to get required count
        base_points = generate_spiral_points(0, 0, config["max_radius"], config["spacing"], config["turns"], config.get("thickness", 1), config.get("angle_offset", 0.0), config.get("radius_offset", 0.0), config.get("theta_phase", 0.0))
        if config.get("random_stacking", False):
            stacked_points = generate_stacked_points(
                base_points, 0, 0, 
                config.get("max_stack_height", 3), 
                config.get("center_stack_bias", 0.5),
                config.get("max_stacks_per_location"),
                config.get("enforce_stack_limit", True)
            )
            totals[key] += len(stacked_points)
        else:
            totals[key] += len(base_points)
        
        # Show estimate when skip_count_check is enabled
        if config.get("skip_count_check", False):
            debug_message(f"  (Estimated need - will place available items)", 67)
    debug_message("\nRequired Items:", 67)
    for item_ids, count in totals.items():
        names = ", ".join([get_item_name(i) for i in item_ids])
        have = sum([Items.BackpackCount(i, -1) for i in item_ids])
        status = "OK" if have >= count else "MISSING"
        color = 68 if have >= count else 33
        debug_message(f"{names}: Need {count}, Have {have} - {status}", color)

def create_spiral_arrangement(center_x, center_y):
    debug_message("Beginning spiral arrangement...", 67)

    center_z = -1 # Player.Position.Z  # Always use z-1 for auto-stacking

    if not PREVIEW_MODE:
        if not goto_location_with_wiggle(center_x, center_y, center=(center_x, center_y)):
            debug_message("Could not reach center position!", 33)
            return

    for phase, config in RITUAL_CONFIG.items():
        if not PLACE_COMPONENTS[phase]:
            continue
        item_ids = config["item_ids"] if isinstance(config["item_ids"], list) else [config["item_ids"]]
        base_points = generate_spiral_points(center_x, center_y, config["max_radius"], config["spacing"], config["turns"], config.get("thickness", 1), config.get("angle_offset", 0.0), config.get("radius_offset", 0.0), config.get("theta_phase", 0.0))
        if config.get("random_stacking", False):
            spiral_points = generate_stacked_points(
                base_points, center_x, center_y, 
                config.get("max_stack_height", 3), 
                config.get("center_stack_bias", 0.5),
                config.get("max_stacks_per_location"),
                config.get("enforce_stack_limit", True)
            )
        else:
            spiral_points = [(x, y, 0) for x, y in base_points]
        required = len(spiral_points)
        if PREVIEW_MODE:
            item_id = next((i for i in item_ids if i is not None), None)
        else:
            item_id = get_first_available_item_id(item_ids, required)
            if item_id is None:
                debug_message(f"Skipping {phase}: item ID not set or item missing.", 33)
                continue
            have = Items.BackpackCount(item_id, -1)
            if not config.get("skip_count_check", False) and have < required:
                debug_message(f"Skipping {phase}: missing {get_item_name(item_id)} (need {required}, have {have})", 33)
                continue
            elif config.get("skip_count_check", False) and have > 0:
                debug_message(f"Proceeding with {phase}: have {have} {get_item_name(item_id)} (will place what we can)", 68)
        temp_config = dict(config)
        temp_config["item_ids"] = [item_id]
        placed = place_pattern_component(center_x, center_y, temp_config, center_z, component_key=phase)
        debug_message(
            (f"Previewed {len(placed)} items for {phase}" if PREVIEW_MODE else f"Placed {len(placed)} items for {phase}"),
            68 if placed else 33
        )

    debug_message("Spiral arrangement complete!", 67)

def main():
    display_configuration()
    calculate_item_totals()

    center_x = Player.Position.X
    center_y = Player.Position.Y

    create_spiral_arrangement(center_x, center_y)

if __name__ == "__main__":
    main()
