"""
Ritual Feast of Cake - a Razor Enhanced Python script for Ultima Online

Cakes, Water Pitchers, Apples, Nightshade
Creates a multi-ring pattern using the deserts 
Pattern focuses on interleaved rings and symmetry, staying within item limits:
- Cakes: < 15 (uses 12)
- Water Pitchers: < 20 (uses 16)
- Apples: < 40 (uses 36)
- Nightshade: < 70 (uses 64)

TODO:
elixir of rebirth in the center 0x4516
black pearl in the open grid cells of the circle , filling in the gaps of all layers combined

VERSION = 20250818
"""
import math
import time
import random

DEBUG_MODE = True
SAFE_MODE = True  # extra-conservative pacing and movement

# Phase toggles for each component
PLACE_COMPONENTS = {
    "A_cake_rosette": True,      # Inner rosette of cakes
    "B_pitcher_star": True,      # Star ring of water pitchers
    "C_apple_ring_1": True,      # Inner apple ring
    "D_apple_ring_2": True,      # Middle apple ring
    "E_nightshade_ring_1": True, # Outer nightshade ring
    "F_nightshade_ring_2": True  # Outermost nightshade ring
}

FEAST_ITEM_IDS = {
    "Cake": 0x09E9,
    "Water Pitcher": 0x1F9D,
    "Apple": 0x09D0,
    "Nightshade": 0x0F88
}

# Component Configuration
FEAST_CONFIG = {
    # 12-point inner rosette of cakes
    "A_cake_rosette": {
        "item_ids": [FEAST_ITEM_IDS["Cake"]],
        "radius": 2,
        "points": 12,       # < 15
        "pattern": "circle",
        "rotation": 15      # slight rotation for rosette feel
    },
    # 16-point pitcher star just outside cakes
    "B_pitcher_star": {
        "item_ids": [FEAST_ITEM_IDS["Water Pitcher"]],
        "radius": 3,
        "points": 16,       # < 20
        "pattern": "circle",
        "rotation": 11.25   # between cardinals/diagonals
    },
    # Apples: 24 points inner ring
    "C_apple_ring_1": {
        "item_ids": [FEAST_ITEM_IDS["Apple"]],
        "radius": 4,
        "points": 24,       # part of total 36
        "pattern": "circle",
        "rotation": 0
    },
    # Apples: 12 points middle ring (interleaved)
    "D_apple_ring_2": {
        "item_ids": [FEAST_ITEM_IDS["Apple"]],
        "radius": 5,
        "points": 12,       # 24 + 12 = 36 (< 40)
        "pattern": "circle",
        "rotation": 15
    },
    # Nightshade: 32 points outer ring
    "E_nightshade_ring_1": {
        "item_ids": [FEAST_ITEM_IDS["Nightshade"]],
        "radius": 6,
        "points": 32,       # part of total 64
        "pattern": "circle",
        "rotation": 0
    },
    # Nightshade: 32 points outermost ring (offset)
    "F_nightshade_ring_2": {
        "item_ids": [FEAST_ITEM_IDS["Nightshade"]],
        "radius": 7,
        "points": 32,       # 32 + 32 = 64 (< 70)
        "pattern": "circle",
        "rotation": 5
    }
}

# Constants
PAUSE_DURATION = 350        # General pause between actions (ms)
PAUSE_DURATION_PLACE = 550  # Pause after placing item (ms)
MAX_DISTANCE = 2

# Movement tuning (graceful handling)
GOTO_BASE_DELAY = 250       # base delay between movement attempts (ms)
GOTO_MAX_RETRIES = 1        # minimal retries
WIGGLE_RADII = [0]          # in SAFE_MODE we only try exact tile
WIGGLE_ANGLES = [0, 45, 90, 135, 180, 225, 270, 315]
WALK_REPEATS_PER_DIR = 2    # how many times to attempt walking in one direction before switching

# Center bias tuning (keep minimal to avoid backtracking)
CENTER_BIAS_ENABLED = True
CENTER_NUDGE_DISTANCE = 3   # only nudge toward center if farther than this many tiles from center
CENTER_NUDGE_STEPS = 2      # max steps to take toward center when nudging

# Placement tuning
PLACE_MAX_RETRIES = 1        # minimal placement attempts
PLACE_BACKOFF_BASE = 250     # ms
POINT_TIMEOUT_MS = 1500      # per-point cap
POINT_BREATHER_MS = 250      # larger breather between points

# Global throttling / jitter to protect client and server
RATE_MIN_GAP_MS = 350        # ensure at least this much time between heavy actions
LOOP_YIELD_MS = 40           # small yield inside loops
JITTER_MS = 50               # random jitter applied to pauses
LAST_ACTION_MS = 0

# Phase fail-safe
MAX_PHASE_FAILURES = 6

# Deduplication: per-item coordinates placed during this run
PLACED_COORDS_BY_ITEM = {}

# Per-run blacklist of coordinates that proved impossible to place on
BAD_COORDS = set()

# Center coordinates (set at runtime in create_arrangement)
CENTER_X = None
CENTER_Y = None


def debug_message(msg, color=0):
    if DEBUG_MODE:
        try:
            Misc.SendMessage(msg, color)
        except Exception:
            print(msg)


def generate_circle_points(center_x, center_y, radius, points, rotation=0):
    """Generate points in a circle with optional rotation"""
    result = []
    for i in range(points):
        angle = math.radians(rotation + (360.0 * i / points))
        x = center_x + int(radius * math.cos(angle))
        y = center_y + int(radius * math.sin(angle))
        result.append((x, y))
    return result


def now_ms():
    return int(time.time() * 1000)


def pause_ms(ms):
    # Adds a small jitter to avoid synchronized spikes
    Misc.Pause(int(ms + random.randint(0, JITTER_MS)))


def throttle(min_gap_ms=RATE_MIN_GAP_MS):
    global LAST_ACTION_MS
    t = now_ms()
    if LAST_ACTION_MS == 0:
        LAST_ACTION_MS = t
        return
    elapsed = t - LAST_ACTION_MS
    if elapsed < min_gap_ms:
        Misc.Pause(min_gap_ms - elapsed)
    LAST_ACTION_MS = now_ms()


def is_safe_ground(x, y, game_map=None):
    """Conservatively determine if a tile is safe to interact with.
    Avoids known-bad coords and simple land ID blacklist. Extendable.
    """
    if game_map is None:
        game_map = Player.Map
    # Skip coordinates previously marked as problematic
    if (x, y) in BAD_COORDS:
        return False
    try:
        land_id = Statics.GetLandID(x, y, game_map)
    except Exception:
        return False
    # Minimal blacklist of bad land IDs (user can extend as needed)
    BAD_LAND_IDS = {0x0001}
    if land_id in BAD_LAND_IDS:
        return False
    return True


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
    if item_id is None:
        return None
    for _ in range(max_retries):
        found = Items.FindByID(item_id, -1, Player.Backpack.Serial)
        if found:
            return found
        pause_ms(retry_delay)
    return None


def place_item(x, y, item_id, z=None):
    """Place a single item with verification"""
    if item_id is None:
        return False
    # Try a few nearby offsets to avoid impossible exact tiles
    offsets = [(0, 0)] if SAFE_MODE else [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
    if z is None:
        z = Player.Position.Z

    for dx_off, dy_off in offsets:
        tx = x + dx_off
        ty = y + dy_off
        if not is_valid_position(tx, ty, z):
            continue
        if not is_safe_ground(tx, ty):
            BAD_COORDS.add((tx, ty))
            continue
        for attempt in range(1, PLACE_MAX_RETRIES + 1):
        # Re-locate an item each attempt (inventory changes frequently)
            item = Items.FindByID(item_id, -1, Player.Backpack.Serial)
            if not item:
                debug_message(f"Could not find item 0x{item_id:X}", 33)
                return False

        # Snapshot count
            try:
                initial_count = Items.BackpackCount(item_id, -1)
            except Exception as e:
                debug_message(f"BackpackCount error for 0x{item_id:X}: {e}", 33)
                return False
            if initial_count <= 0:
                return False

        # Try to place item
            try:
                Items.MoveOnGround(item, 1, tx, ty, z)
            except Exception as e:
                debug_message(f"MoveOnGround failed at ({tx},{ty}): {e}", 33)
                # mark original coord as bad and back off to avoid loops
                BAD_COORDS.add((x, y))
                pause_ms(PAUSE_DURATION + 150)
                return False
            else:
                throttle()
                pause_ms(PAUSE_DURATION_PLACE)

            # Verify placement with multiple checks
                for _ in range(2):
                    try:
                        new_count = Items.BackpackCount(item_id, -1)
                    except Exception as e:
                        debug_message(f"BackpackCount verify error: {e}", 33)
                        break
                    if new_count < initial_count:
                        return True
                    pause_ms(PAUSE_DURATION)

        # Backoff before next attempt
            pause_ms(PLACE_BACKOFF_BASE * attempt)

    return False


def place_items_at_points(points, item_id, z=None, progress_msg="Placing items"):
    """Place items at points with progress tracking"""
    if not points or item_id is None:
        return set()

    total = len(points)
    placed = set()
    failures = 0
    if item_id not in PLACED_COORDS_BY_ITEM:
        PLACED_COORDS_BY_ITEM[item_id] = set()

    for i, (x, y) in enumerate(points, 1):
        debug_message(f"{progress_msg}: {i} out of {total}", 67)

        start_ms = int(time.time() * 1000)

        # Skip coordinates previously marked as bad
        if (x, y) in BAD_COORDS:
            debug_message(f"Skipping known-bad coord ({x},{y})", 33)
            continue

        # Per-item dedup: skip if this item already placed at these coords
        if (x, y) in PLACED_COORDS_BY_ITEM[item_id]:
            debug_message(f"Duplicate coords for {get_item_name(item_id)} at ({x},{y}), skipping.", 68)
            continue

        # Try to get in range (with per-point timeout)
        if not goto_location_with_wiggle(x, y):
            debug_message(f"Could not reach position ({x}, {y})", 33)
            failures += 1
            if failures >= MAX_PHASE_FAILURES:
                debug_message("Too many failures in this phase; aborting phase early.", 33)
                break
            continue

        # Try placement up to 1 time (reduced); we already retried movement
        for attempt in range(1):
            if place_item(x, y, item_id, z):
                placed.add((x, y))
                PLACED_COORDS_BY_ITEM[item_id].add((x, y))
                break
            # No extra placement retry, just small pause before skip
            pause_ms(PAUSE_DURATION)

            # Timeout guard per point
            if int(time.time() * 1000) - start_ms > POINT_TIMEOUT_MS:
                debug_message(f"Timeout at point ({x},{y}), skipping.", 33)
                BAD_COORDS.add((x, y))
                failures += 1
                break

        # Small breather between points to avoid client overload
        pause_ms(POINT_BREATHER_MS)

    return placed


def get_direction(from_x, from_y, to_x, to_y):
    """Calculate direction from one point to another"""
    dx = to_x - from_x
    dy = to_y - from_y

    # N=0, NE=1, E=2, SE=3, S=4, SW=5, W=6, NW=7
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
    """Convert 0-7 direction index to Razor Enhanced walk string."""
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


def goto_location_with_wiggle(x, y, max_retries=GOTO_MAX_RETRIES):
    """Conservative walking-only approach.
    1) Bias toward center (if set) with a few steps.
    2) Walk toward target with verification and backoff.
    No pathfinding is used to avoid client crashes.
    """
    target_x = int(float(x))
    target_y = int(float(y))

    # Pre-check: avoid unsafe tiles
    if not is_safe_ground(target_x, target_y):
        return False

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

            # try base direction then slight variations
            dirs = [base_dir, (base_dir+1)%8, (base_dir+7)%8]
            moved = False
            for d in dirs:
                # attempt multiple steps in the same direction
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
                # back off and try again more slowly
                step_delay = int(step_delay * 1.3) + 50
                pause_ms(step_delay)
        return (abs(Player.Position.X - tx) <= MAX_DISTANCE and
                abs(Player.Position.Y - ty) <= MAX_DISTANCE)

    # 1) Try to move directly toward the target first
    if attempt_walk_toward(target_x, target_y, max_steps=8):
        return True

    # 2) Optional minimal nudge toward center, then retry target
    if CENTER_BIAS_ENABLED and CENTER_X is not None and CENTER_Y is not None:
        dxc = abs(Player.Position.X - CENTER_X)
        dyc = abs(Player.Position.Y - CENTER_Y)
        if dxc > CENTER_NUDGE_DISTANCE or dyc > CENTER_NUDGE_DISTANCE:
            attempt_walk_toward(CENTER_X, CENTER_Y, max_steps=CENTER_NUDGE_STEPS)
            # retry target after nudge
            if attempt_walk_toward(target_x, target_y, max_steps=6):
                return True

    return (abs(Player.Position.X - target_x) <= MAX_DISTANCE and
            abs(Player.Position.Y - target_y) <= MAX_DISTANCE)


def get_first_available_item_id(item_ids, required_count):
    """Return the first item_id with at least required_count in backpack.
    Skips None entries gracefully.
    """
    if isinstance(item_ids, int) or item_ids is None:
        item_ids = [item_ids]
    for item_id in item_ids:
        if item_id is None:
            continue
        if Items.BackpackCount(item_id, -1) >= required_count:
            return item_id
    # Fallback to the first valid ID if present
    for item_id in item_ids:
        if item_id is not None:
            return item_id
    return None


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
    elif config["pattern"] == "center":
        points = [(center_x, center_y)]

    required = 1 if config["pattern"] == "center" else config["points"]
    item_id = get_first_available_item_id(config["item_ids"], required)
    if item_id is None:
        debug_message("Skipping component: item ID not set or not available.", 33)
        return set()
    return place_items_at_points(
        points,
        item_id,
        z,
        f"Placing {get_item_name(item_id)}"
    )


def get_item_name(item_id):
    """Get readable name for item ID"""
    for name, id_val in FEAST_ITEM_IDS.items():
        if id_val == item_id:
            return name
    return f"Item 0x{item_id:X}" if item_id is not None else "Unknown Item"


def display_configuration():
    """Display active arrangement configuration"""
    debug_message("Current Arrangement Configuration:", 67)
    for phase, active in PLACE_COMPONENTS.items():
        if phase in FEAST_CONFIG:
            config = FEAST_CONFIG[phase]
            item_ids = config["item_ids"] if isinstance(config["item_ids"], list) else [config["item_ids"]]
            names = ", ".join([get_item_name(i) for i in item_ids])
            status = "ACTIVE" if active else "DISABLED"
            debug_message(
                f"{phase}: {names} - {status}",
                68 if active else 33
            )


def calculate_item_totals():
    """Calculate and display required items"""
    totals = {}
    for phase, config in FEAST_CONFIG.items():
        if not PLACE_COMPONENTS[phase]:
            continue
        item_ids = config["item_ids"] if isinstance(config["item_ids"], list) else [config["item_ids"]]
        key = tuple([i for i in item_ids if i is not None])
        if not key:
            # No valid IDs configured yet
            debug_message(f"{phase}: No valid item ID configured.", 33)
            continue
        if key not in totals:
            totals[key] = 0
        totals[key] += config["points"] if config["pattern"] != "center" else 1
    debug_message("\nRequired Items:", 67)
    for item_ids, count in totals.items():
        names = ", ".join([get_item_name(i) for i in item_ids])
        have = sum([Items.BackpackCount(i, -1) for i in item_ids])
        status = "OK" if have >= count else "MISSING"
        color = 68 if have >= count else 33
        debug_message(f"{names}: Need {count}, Have {have} - {status}", color)


def create_arrangement(center_x, center_y):
    """Create the arrangement pattern"""
    debug_message("Beginning arrangement...", 67)

    center_z = Player.Position.Z

    # First try to reach the center
    global CENTER_X, CENTER_Y
    CENTER_X, CENTER_Y = center_x, center_y
    if not goto_location_with_wiggle(center_x, center_y):
        debug_message("Could not reach center position!", 33)
        return

    # Place each component if enabled
    for phase, config in FEAST_CONFIG.items():
        if not PLACE_COMPONENTS[phase]:
            continue
        item_ids = config["item_ids"] if isinstance(config["item_ids"], list) else [config["item_ids"]]
        required = 1 if config["pattern"] == "center" else config["points"]
        item_id = get_first_available_item_id(item_ids, required)
        if item_id is None:
            debug_message(f"Skipping {phase}: item ID not set or item missing.", 33)
            continue
        have = Items.BackpackCount(item_id, -1)
        if have < required:
            debug_message(f"Skipping {phase}: missing {get_item_name(item_id)} (need {required}, have {have})", 33)
            continue
        temp_config = dict(config)
        temp_config["item_ids"] = [item_id]
        placed = place_pattern_component(center_x, center_y, temp_config, center_z)
        debug_message(
            f"Placed {len(placed)} items for {phase}",
            68 if placed else 33
        )

    debug_message("Arrangement complete!", 67)


def main():
    """Main function"""
    display_configuration()
    calculate_item_totals()

    # Use player's current position as center
    center_x = Player.Position.X
    center_y = Player.Position.Y

    create_arrangement(center_x, center_y)


if __name__ == "__main__":
    main()
