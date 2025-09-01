"""
Ritual of Gems - a Razor Enhanced Python script for Ultima Online

Places a multi-ring of color-ordered gems centered on the player.

Color order (inner to outer):
- Diamond (White/Clear)     0x0F26
- Ruby (Red)                0x0F13
- Amber (Orange)            0x0F25
- Citrine (Yellow)          0x0F15
- Tourmaline (Green/Pink)   0x0F18
- Emerald (Green)           0x0F10
- Sapphire (Teal)           0x0F11
- Star Sapphire (Blue)      0x0F0F
- Amethyst (Violet)         0x0F16

VERSION = 20250828
"""

import math
import time
import random

DEBUG_MODE = False
SAFE_MODE = False  # extra-conservative pacing and movement

# Preview mode: when True, do not move or place real items. Instead, render client-side
# fake items at the target coordinates using PacketLogger.SendToClient
PREVIEW_MODE = False
PREVIEW_DEFAULT_HUE = 0x0000  # 0 means no hue

# Phase toggles for each component (one ring per gem color)
PLACE_COMPONENTS = {
    "A_diamond_inner": True,
    "B_ruby": True,
    "C_amber": True,
    "D_citrine": True,
    "E_tourmaline": True,
    "F_emerald": True,
    "G_sapphire": True,
    "H_star_sapphire": True,
    "I_amethyst_outer": True,
}

# Placement order control: smallest radius first (True) or largest first (False)
ORDER_SMALLEST_FIRST = True

# Gem Item IDs (primary + alternates where applicable)
GEM_ITEM_IDS = {
    "Ruby": [0x0F13],
    "Amber": [0x0F25],
    "Citrine": [0x0F15],
    "Tourmaline": [0x0F18, 0x0F2D],  # include TourmalineB as fallback
    "Diamond": [0x0F26],
    "Emerald": [0x0F10],
    "Sapphire": [0x0F11, 0x0F19, 0x0F21],  # include alternates
    "Star Sapphire": [0x0F0F],
    "Amethyst": [0x0F16],
}

# Component Configuration: circles expanding outward by color order
RITUAL_CONFIG = {
    "A_diamond_inner": {
        "item_ids": GEM_ITEM_IDS["Diamond"],
        "radius": 2,
        "points": 10,
        "pattern": "circle",
        "rotation": 0,
    },
    "B_ruby": {
        "item_ids": GEM_ITEM_IDS["Ruby"],
        "radius": 3,
        "points": 12,
        "pattern": "circle",
        "rotation": 15,
    },
    "C_amber": {
        "item_ids": GEM_ITEM_IDS["Amber"],
        "radius": 4,
        "points": 14,
        "pattern": "circle",
        "rotation": 0,
    },
    "D_citrine": {
        "item_ids": GEM_ITEM_IDS["Citrine"],
        "radius": 5,
        "points": 16,
        "pattern": "circle",
        "rotation": 11.25,
    },
    "E_tourmaline": {
        "item_ids": GEM_ITEM_IDS["Tourmaline"],
        "radius": 6,
        "points": 18,
        "pattern": "circle",
        "rotation": 0,
    },
    "F_emerald": {
        "item_ids": GEM_ITEM_IDS["Emerald"],
        "radius": 7,
        "points": 20,
        "pattern": "circle",
        "rotation": 9,
    },
    "G_sapphire": {
        "item_ids": GEM_ITEM_IDS["Sapphire"],
        "radius": 8,
        "points": 20,
        "pattern": "circle",
        "rotation": 0,
    },
    "H_star_sapphire": {
        "item_ids": GEM_ITEM_IDS["Star Sapphire"],
        "radius": 9,
        "points": 22,
        "pattern": "circle",
        "rotation": 8,
    },
    "I_amethyst_outer": {
        "item_ids": GEM_ITEM_IDS["Amethyst"],
        "radius": 10,
        "points": 24,
        "pattern": "circle",
        "rotation": 0,
    },
}

# Constants (copied/tuned from feast base)
PAUSE_DURATION = 350        # General pause between actions (ms)
PAUSE_DURATION_PLACE = 550  # Pause after placing item (ms)
MAX_DISTANCE = 2

# Movement tuning (graceful handling)
GOTO_BASE_DELAY = 250       # base delay between movement attempts (ms)
GOTO_MAX_RETRIES = 1        # minimal retries
WIGGLE_RADII = [0]          # in SAFE_MODE we only try exact tile
WIGGLE_ANGLES = [0, 45, 90, 135, 180, 225, 270, 315]
WALK_REPEATS_PER_DIR = 2    # attempts per direction

# Center bias tuning (keep minimal to avoid backtracking)
CENTER_BIAS_ENABLED = True
CENTER_NUDGE_DISTANCE = 3
CENTER_NUDGE_STEPS = 2

# Placement tuning
PLACE_MAX_RETRIES = 1
PLACE_BACKOFF_BASE = 250
POINT_TIMEOUT_MS = 1500
POINT_BREATHER_MS = 250

# Global throttling / jitter to protect client and server
RATE_MIN_GAP_MS = 350
LOOP_YIELD_MS = 40
JITTER_MS = 50
LAST_ACTION_MS = 0

# Phase fail-safe and dedupe
MAX_PHASE_FAILURES = 6
PLACED_COORDS_BY_ITEM = {}
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
    """Send a client-only item render at location without server state change.

    item_id_4hex_with_space example: "0F 13" for 0x0F13
    hue_4hex_with_space example: "00 00" for no hue
    """
    try:
        # Packet template from (F3 -> draw static item to client)
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

def generate_circle_points(center_x, center_y, radius, points, rotation=0):
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

def place_item(x, y, item_id, z=None):
    if PREVIEW_MODE:
        if z is None:
            z = Player.Position.Z
        preview_item_at(x, y, z, item_id, PREVIEW_DEFAULT_HUE)
        return True
    if item_id is None:
        return False
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
                Items.MoveOnGround(item, 1, tx, ty, z)
            except Exception as e:
                debug_message(f"MoveOnGround failed at ({tx},{ty}): {e}", 33)
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

def place_items_at_points(points, item_id, z=None, progress_msg="Placing items", center=None):
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

        if (x, y) in BAD_COORDS:
            debug_message(f"Skipping known-bad coord ({x},{y})", 33)
            continue

        if (x, y) in PLACED_COORDS_BY_ITEM[item_id]:
            debug_message(f"Duplicate coords for {get_item_name(item_id)} at ({x},{y}), skipping.", 68)
            continue

        if not PREVIEW_MODE:
            if not goto_location_with_wiggle(x, y, center=center):
                debug_message(f"Could not reach position ({x}, {y})", 33)
                failures += 1
                if failures >= MAX_PHASE_FAILURES:
                    debug_message("Too many failures in this phase; aborting phase early.", 33)
                    break
                continue

        for attempt in range(1):
            if place_item(x, y, item_id, z):
                placed.add((x, y))
                PLACED_COORDS_BY_ITEM[item_id].add((x, y))
                break
            if PREVIEW_MODE:
                # In preview, a single send is enough; no retry/backpack logic
                break
            pause_ms(PAUSE_DURATION)

            if int(time.time() * 1000) - start_ms > POINT_TIMEOUT_MS:
                debug_message(f"Timeout at point ({x},{y}), skipping.", 33)
                BAD_COORDS.add((x, y))
                failures += 1
                break

        pause_ms(POINT_BREATHER_MS)

    return placed

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

def get_ordered_phases():
    items = []
    for phase, config in RITUAL_CONFIG.items():
        radius = config.get("radius", 0)
        items.append((phase, config, radius))
    items.sort(key=lambda t: t[2], reverse=not ORDER_SMALLEST_FIRST)
    return [(phase, config) for (phase, config, _) in items]

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

def place_pattern_component(center_x, center_y, config, z=None):
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
    if PREVIEW_MODE:
        # In preview: use first configured ID even if not present in backpack
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
        f"{verb} {get_item_name(item_id)}",
        center=(center_x, center_y)
    )

def get_item_name(item_id):
    for name, ids in GEM_ITEM_IDS.items():
        if isinstance(ids, list) and item_id in ids:
            return name
        if ids == item_id:
            return name
    return f"Item 0x{item_id:X}" if item_id is not None else "Unknown Item"

def display_configuration():
    debug_message("Current Gem Arrangement Configuration:", 67)
    for phase, config in get_ordered_phases():
        active = PLACE_COMPONENTS.get(phase, False)
        item_ids = config["item_ids"] if isinstance(config["item_ids"], list) else [config["item_ids"]]
        names = ", ".join([get_item_name(i) for i in item_ids if i is not None])
        status = "ACTIVE" if active else "DISABLED"
        debug_message(f"{phase}: {names} - {status}", 68 if active else 33)

def calculate_item_totals():
    totals = {}
    for phase, config in get_ordered_phases():
        if not PLACE_COMPONENTS[phase]:
            continue
        item_ids = config["item_ids"] if isinstance(config["item_ids"], list) else [config["item_ids"]]
        key = tuple([i for i in item_ids if i is not None])
        if not key:
            debug_message(f"{phase}: No valid item ID configured.", 33)
            continue
        if key not in totals:
            totals[key] = 0
        totals[key] += config["points"] if config["pattern"] != "center" else 1
    debug_message("\nRequired Gems:", 67)
    for item_ids, count in totals.items():
        names = ", ".join([get_item_name(i) for i in item_ids])
        have = sum([Items.BackpackCount(i, -1) for i in item_ids])
        status = "OK" if have >= count else "MISSING"
        color = 68 if have >= count else 33
        debug_message(f"{names}: Need {count}, Have {have} - {status}", color)

def create_arrangement(center_x, center_y):
    debug_message("Beginning gem arrangement...", 67)

    center_z = Player.Position.Z

    if not PREVIEW_MODE:
        if not goto_location_with_wiggle(center_x, center_y, center=(center_x, center_y)):
            debug_message("Could not reach center position!", 33)
            return

    for phase, config in get_ordered_phases():
        if not PLACE_COMPONENTS[phase]:
            continue
        item_ids = config["item_ids"] if isinstance(config["item_ids"], list) else [config["item_ids"]]
        required = 1 if config["pattern"] == "center" else config["points"]
        if PREVIEW_MODE:
            # Choose first available ID for visual
            item_id = next((i for i in item_ids if i is not None), None)
        else:
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
            (f"Previewed {len(placed)} items for {phase}" if PREVIEW_MODE else f"Placed {len(placed)} items for {phase}"),
            68 if placed else 33
        )

    debug_message("Gem arrangement complete!", 67)

def main():
    display_configuration()
    calculate_item_totals()

    center_x = Player.Position.X
    center_y = Player.Position.Y

    create_arrangement(center_x, center_y)

if __name__ == "__main__":
    main()