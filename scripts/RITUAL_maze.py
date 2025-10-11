"""
RITUAL maze - a Razor Enhanced Python script for Ultima Online

Places hay on a square plot of farm land to create a maze.
Includes a preview mode to visualize candidate generations and the solution path.
Favors solutions with long winding distance and long false paths

the Hay Sheaf item is non stackable and 10 stones each so we attempt to restock mid placement 
searching for pack horses and try to resume gracefully . some issues still with placement 

SEEDS =
Chosen seed 733978 with score 5431 # this was preety good , long curling tricky paths , its a little harsh as it immeadiately forks you two long choices 

VERSION = 20250923
"""

import json
import math
import os
import random
import time

DEBUG_MODE = True # debug messages
SAFE_MODE = False # extra slow

PREVIEW_MODE = False # Preview mode: client-side fake items; no server state change
PREVIEW_DEFAULT_HUE = 0x0000
PREVIEW_SOLUTION_HUE = 0x0042  # blue-ish overlay for solution

# Checkpointing / resume
CHECKPOINT_DIR = os.path.join("data", "maze_runs")
CHECKPOINT_EVERY_N = 10  # write checkpoint every N placements

# Placement pacing and limits
PAUSE_DURATION = 350
PAUSE_DURATION_PLACE = 550
PREVIEW_PAUSE_DURATION = 25
PREVIEW_PAUSE_PLACE = 35
MAX_DISTANCE = 2

# Movement tuning (mirrors RITUAL_spiral_round.py)
GOTO_BASE_DELAY = 250
GOTO_MAX_RETRIES = 1
WIGGLE_RADII = [0]
WIGGLE_ANGLES = [0, 45, 90, 135, 180, 225, 270, 315]
WALK_REPEATS_PER_DIR = 2

# Center bias
CENTER_BIAS_ENABLED = True
CENTER_NUDGE_DISTANCE = 3
CENTER_NUDGE_STEPS = 2

# Placement tuning
PLACE_MAX_RETRIES = 1
PLACE_BACKOFF_BASE = 250
POINT_TIMEOUT_MS = 1500
POINT_BREATHER_MS = 250
PREVIEW_BREATHER_MS = 15

# Global throttling / jitter
RATE_MIN_GAP_MS = 350
LOOP_YIELD_MS = 40
JITTER_MS = 50
PREVIEW_MIN_GAP_MS = 10
PREVIEW_JITTER_MS = 5
LAST_ACTION_MS = 0

# Phase fail-safe and dedupe
MAX_PHASE_FAILURES = 6
PLACED_COORDS_BY_ITEM = {}
ALL_PLACED_COORDS = set()
ALL_PLACED_COORDS_BY_COMPONENT = {}
BAD_COORDS = set()
 
# Pack animal state
PACK_ROUND_ROBIN_INDEX = 0
PACK_DEPLETED_SERIALS = set()

# Item configuration
# Default wall item: Hay (example IDs; adjust as needed for shard)
HAY_ITEM_IDS = {
    "Hay": [0x0F36],  # common hay/sheaf item ID; change if shard differs
}

# Solution overlay item (cloth bolt or folded cloth). Hue is applied in preview only.
CLOTH_ITEM_IDS = {
    "Cloth": [0x1766],  # folded cloth stack
}

ITEM_NAME_LOOKUP = {}
ITEM_NAME_LOOKUP.update(HAY_ITEM_IDS)
ITEM_NAME_LOOKUP.update(CLOTH_ITEM_IDS)

MAZE_CONFIG = {
    "label": "Hay Maze",
    "wall_item_ids": HAY_ITEM_IDS["Hay"],
    "solution_item_ids": CLOTH_ITEM_IDS["Cloth"],
    "width": 26,           # tiles; should be odd for perfect maze grid mapping
    "height": 26,          # tiles; should be odd
    "cell_size": 1,        # world tiles per logical cell (1 = tight corridors)
    "seed": 733978,          # if None, random; persisted in checkpoint # 733978 , 666666 was image
    "tries_in_preview": 10, # how many seeds to test in preview scoring mode
    "show_solution": True, # when preview, overlay solution path
    "prefer_winding": True,
}

# Restock behavior for non-stackable hay
RESTOCK_WAIT_ENABLED = True
RESTOCK_WAIT_TIMEOUT_SEC = 900  # 15 minutes max wait
RESTOCK_POLL_MS = 2000

# Auto restock from pack animals
AUTO_RESTOCK_ENABLED = True
RESTOCK_BATCH_COUNT = 20            # how many hay items to pull at a time
PACKHORSE_SERIALS = []              # optional hardcoded list of pack animal serials
# Name patterns to match when searching nearby (case-insensitive substring)
PACK_NAME_FILTERS = ["pack horse", "a pack horse", "pack llama", "a pack llama", "packhorse", "packllama"]
PACK_SEARCH_RANGE = 18              # tiles to search for pack animals
PACK_BODY_IDS = [0x0123]            # optional known body IDs for pack animals (shard-specific)
PROMPT_FOR_PACK_ON_MISS = True      # if none found, prompt once to select a pack animal and cache serial

# ================================== Utilities and ritual framework ==================================

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

def _format_hex_4_with_space(value):
    s = f"{int(value) & 0xFFFF:04X}"
    return s[:2] + " " + s[2:]

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
        # Encode Z as unsigned byte to support negative values like -1 => 0xFF
        i_loc_z = f"{(int(item_z) & 0xFF):02X}"

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

def preview_item_at(x, y, z, item_id, hue=PREVIEW_DEFAULT_HUE):
    item_hex = _format_hex_4_with_space(item_id)
    hue_hex = _format_hex_4_with_space(hue)
    _send_fake_item(x, y, z, item_hex, hue_hex)

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
    for _ in range(max_steps):
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
            for _rep in range(WALK_REPEATS_PER_DIR):
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

def place_item(x, y, item_id, z=None):
    if PREVIEW_MODE:
        if z is None:
            z = -1
        preview_item_at(x, y, z, item_id, PREVIEW_DEFAULT_HUE)
        return True
    if item_id is None:
        return False
    offsets = [(0, 0)] if SAFE_MODE else [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
    if z is None:
        z = -1

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
                force_z = -1
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

def get_item_name(item_id):
    for name, ids in ITEM_NAME_LOOKUP.items():
        if isinstance(ids, list) and item_id in ids:
            return name
        if ids == item_id:
            return name
    return f"Item 0x{item_id:X}" if item_id is not None else "Unknown Item"

# ================================== Maze generation ==================================

def _neighbors(grid_w, grid_h, cx, cy):
    # 4-dir neighbors two steps away (for maze carving)
    for dx, dy in [(2,0), (-2,0), (0,2), (0,-2)]:
        nx, ny = cx + dx, cy + dy
        if 1 <= nx < grid_w-1 and 1 <= ny < grid_h-1:
            yield nx, ny, dx, dy

def generate_maze(width, height, seed=None):
    # Use odd dimensions for proper walls; enforce
    if width % 2 == 0:
        width += 1
    if height % 2 == 0:
        height += 1

    rnd = random.Random(seed)
    grid = [[1 for _ in range(width)] for _ in range(height)]  # 1=wall, 0=path

    # Start at random odd cell
    start_x = rnd.randrange(1, width, 2)
    start_y = rnd.randrange(1, height, 2)
    grid[start_y][start_x] = 0

    stack = [(start_x, start_y)]
    while stack:
        cx, cy = stack[-1]
        nbrs = [(nx, ny, dx, dy) for nx, ny, dx, dy in _neighbors(width, height, cx, cy) if grid[ny][nx] == 1]
        if not nbrs:
            stack.pop()
            continue
        nx, ny, dx, dy = rnd.choice(nbrs)
        # Carve wall between
        grid[cy + dy//2][cx + dx//2] = 0
        grid[ny][nx] = 0
        stack.append((nx, ny))

    # Compute distances from an entrance candidate and choose farthest exit
    # Entrance/exit on outer ring where path cell exists
    entrances = []
    for x in range(1, width, 2):
        if grid[1][x] == 0:
            entrances.append((x, 0, x, 1))  # top
        if grid[height-2][x] == 0:
            entrances.append((x, height-1, x, height-2))  # bottom
    for y in range(1, height, 2):
        if grid[y][1] == 0:
            entrances.append((0, y, 1, y))  # left
        if grid[y][width-2] == 0:
            entrances.append((width-1, y, width-2, y))  # right
    if not entrances:
        entrances.append((start_x, 0, start_x, 1))

    ex, ey, ix, iy = entrances[0]
    # Mark entrance and exit as paths
    grid[iy][ix] = 0
    grid[ey][ex] = 0

    # Choose exit as farthest from entrance interior point (ix, iy)
    dist, parents = _bfs_dist(grid, (ix, iy))
    far_candidates = [(dist.get((x, 1), -1), (x, 0), (x, 1)) for x in range(1, width, 2) if grid[1][x] == 0]
    far_candidates += [(dist.get((x, height-2), -1), (x, height-1), (x, height-2)) for x in range(1, width, 2) if grid[height-2][x] == 0]
    far_candidates += [(dist.get((1, y), -1), (0, y), (1, y)) for y in range(1, height, 2) if grid[y][1] == 0]
    far_candidates += [(dist.get((width-2, y), -1), (width-1, y), (width-2, y)) for y in range(1, height, 2) if grid[y][width-2] == 0]
    if far_candidates:
        far_candidates.sort(key=lambda t: t[0])
        d, (ex, ey), (ix2, iy2) = far_candidates[-1]
        grid[iy2][ix2] = 0
        grid[ey][ex] = 0

    # Build solution path from farthest exit
    dist2, parents2 = _bfs_dist(grid, (ix2, iy2)) if far_candidates else (dist, parents)
    target = (ex, ey)
    sol = _reconstruct_path(parents2, (ix2, iy2), target)
    # Convert entrance cell to interior neighbor for world mapping
    entrance_interior = (ix2, iy2) if far_candidates else (ix, iy)

    return {
        "grid": grid,          # 2D list: 1=wall, 0=path
        "width": width,
        "height": height,
        "entrance": (ex, ey),  # border tile
        "entrance_interior": entrance_interior,
        "exit": (ex, ey),      # same as entrance for wall break; used for path mapping
        "solution": sol,       # list of (x,y) grid coords including border endpoint
        "seed": seed,
        "score": _score_maze(grid, sol),
    }

def _bfs_dist(grid, start):
    width = len(grid[0])
    height = len(grid)
    q = [start]
    dist = {start: 0}
    parents = {start: None}
    head = 0
    while head < len(q):
        x, y = q[head]
        head += 1
        for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < width and 0 <= ny < height and grid[ny][nx] == 0 and (nx, ny) not in dist:
                dist[(nx, ny)] = dist[(x, y)] + 1
                parents[(nx, ny)] = (x, y)
                q.append((nx, ny))
    return dist, parents

def _reconstruct_path(parents, start, end):
    cur = end
    out = []
    while cur is not None:
        out.append(cur)
        cur = parents.get(cur)
    out.reverse()
    # ensure starts with start
    if out and out[0] != start:
        out.insert(0, start)
    return out

def _score_maze(grid, solution_path):
    # Favor long solution and long misleading dead-ends
    path_score = len(solution_path)
    # Dead-end analysis: count lengths of branches ending at degree-1 nodes excluding solution path
    width = len(grid[0])
    height = len(grid)
    sol_set = set(solution_path)

    def neighbors_open(x, y):
        for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < width and 0 <= ny < height and grid[ny][nx] == 0:
                yield nx, ny

    dead_end_lengths = []
    visited = set()
    for y in range(height):
        for x in range(width):
            if grid[y][x] != 0 or (x, y) in visited:
                continue
            deg = sum(1 for _ in neighbors_open(x, y))
            if deg == 1 and (x, y) not in sol_set:
                # Follow branch until junction
                length = 1
                visited.add((x, y))
                px, py = x, y
                # advance to next
                nexts = [n for n in neighbors_open(px, py) if n not in visited]
                while len(nexts) == 1:
                    nx, ny = nexts[0]
                    visited.add((nx, ny))
                    length += 1
                    px, py = nx, ny
                    nexts = [n for n in neighbors_open(px, py) if n not in visited]
                dead_end_lengths.append(length)

    # Reward longer dead-ends more than many short ones
    dead_score = sum(l*l for l in dead_end_lengths)
    return path_score * 2 + dead_score

# ============================= Mapping to world coords and placement =============================

def grid_to_world(center_x, center_y, grid_x, grid_y, cell_size=1, width=None, height=None):
    # Align grid (0..W-1, 0..H-1) so that (1,1) maps near center; upper-left alignment
    # Use the actual maze dimensions when provided to ensure correct centering.
    if width is None:
        width = MAZE_CONFIG.get("width", 21)
    if height is None:
        height = MAZE_CONFIG.get("height", 21)
    half_w = int(width) // 2
    half_h = int(height) // 2
    world_x = center_x + (grid_x - half_w) * cell_size
    world_y = center_y + (grid_y - half_h) * cell_size
    return world_x, world_y

def build_wall_points_from_grid(center_x, center_y, maze, cell_size=1):
    """Build world points for walls in a serpentine (zig-zag) row order.
    This reduces walking backtracking by alternating direction each row.
    """
    points = []
    grid = maze["grid"]
    h = maze["height"]
    w = maze["width"]

    for gy in range(h):
        # Determine traversal order for this row (zig-zag)
        if gy % 2 == 0:
            gx_iter = range(w)  # left to right
        else:
            gx_iter = range(w - 1, -1, -1)  # right to left
        for gx in gx_iter:
            if grid[gy][gx] == 1:  # wall
                wx, wy = grid_to_world(center_x, center_y, gx, gy, cell_size, width=w, height=h)
                points.append((int(wx), int(wy)))
    return points

def build_solution_points_from_grid(center_x, center_y, maze, cell_size=1):
    pts = []
    h = maze["height"]
    w = maze["width"]
    for gx, gy in maze["solution"]:
        wx, wy = grid_to_world(center_x, center_y, gx, gy, cell_size, width=w, height=h)
        pts.append((int(wx), int(wy)))
    return pts

def ensure_checkpoint_dir():
    try:
        if not os.path.isdir(CHECKPOINT_DIR):
            os.makedirs(CHECKPOINT_DIR)
    except Exception:
        pass

def checkpoint_path(center_x, center_y, width, height, seed):
    ensure_checkpoint_dir()
    fname = f"maze_w{width}_h{height}_cx{center_x}_cy{center_y}_seed{seed}.json"
    return os.path.join(CHECKPOINT_DIR, fname)

def save_checkpoint(path, state):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
        debug_message(f"Saved checkpoint: {path}", 68)
    except Exception as e:
        debug_message(f"Failed to save checkpoint: {e}", 33)

def load_checkpoint(path):
    try:
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        debug_message(f"Failed to load checkpoint: {e}", 33)
    return None

def wait_for_restock_if_needed(item_id, required_remaining):
    if PREVIEW_MODE or not RESTOCK_WAIT_ENABLED:
        return True
    start = time.time()
    while True:
        try:
            have = Items.BackpackCount(item_id, -1)
        except Exception:
            have = 0
        if have >= required_remaining:
            return True
        # Attempt auto restock from pack animals
        if AUTO_RESTOCK_ENABLED:
            pulled = attempt_autorestock_hay_from_packs(item_id, RESTOCK_BATCH_COUNT)
            if pulled > 0:
                debug_message(f"Auto-restocked {pulled} hay from pack animals.", 68)
                continue
        if time.time() - start > RESTOCK_WAIT_TIMEOUT_SEC:
            debug_message("Restock wait timed out.", 33)
            return False
        debug_message(f"Waiting for restock of {get_item_name(item_id)}... need {required_remaining}, have {have}", 67)
        pause_ms(RESTOCK_POLL_MS)

def _get_pack_container_from_mobile(mob):
    """Resolve the pack container Item from a mobile, or None."""
    try:
        pack_container = mob.Backpack if hasattr(mob, 'Backpack') else None
        if pack_container:
            # Some environments expose .Serial directly; support both
            serial = pack_container.Serial if hasattr(pack_container, 'Serial') else pack_container
            cont_item = Items.FindBySerial(serial)
            if cont_item:
                return cont_item
    except Exception as e:
        debug_message(f"Pack resolve failed: {e}", 33)
    return None

def _find_nearby_pack_mobiles():
    """Return a list of nearby pack mobiles, preferring configured serials then nearby name patterns."""
    global PACK_ROUND_ROBIN_INDEX
    candidates = []
    # Hardcoded serials first
    for s in PACKHORSE_SERIALS:
        try:
            mob = Mobiles.FindBySerial(int(s))
            if mob:
                candidates.append(mob)
        except Exception:
            continue
    # Nearby by name/body filter
    try:
        f = Mobiles.Filter()
        f.RangeMax = int(PACK_SEARCH_RANGE)
        # Do not rely on Name filter (not universal); we'll filter manually
        Mobiles.ApplyFilter(f)
        nearby = Mobiles.GetList()
        # If Name filter unsupported, filter manually by name substring
        for m in nearby:
            try:
                nm = (m.Name or "").lower()
                # match any known pattern
                name_hit = any(pat in nm for pat in [p.lower() for p in PACK_NAME_FILTERS])
                body_hit = False
                try:
                    if PACK_BODY_IDS:
                        body_hit = int(getattr(m, 'Body', -1)) in [int(b) for b in PACK_BODY_IDS]
                except Exception:
                    body_hit = False
                if name_hit or body_hit:
                    # Avoid duplicates if already listed
                    if all(x.Serial != m.Serial for x in candidates):
                        candidates.append(m)
            except Exception:
                continue
    except Exception:
        pass
    # Filter out packs we've marked depleted
    if candidates:
        try:
            candidates = [m for m in candidates if int(m.Serial) not in PACK_DEPLETED_SERIALS]
        except Exception:
            pass

    # Apply round-robin ordering so we don't always start from the same mob
    if candidates:
        try:
            start = PACK_ROUND_ROBIN_INDEX % len(candidates)
            ordered = candidates[start:] + candidates[:start]
            PACK_ROUND_ROBIN_INDEX = (PACK_ROUND_ROBIN_INDEX + 1) % max(1, len(candidates))
            candidates = ordered
        except Exception:
            pass

    if not candidates and PROMPT_FOR_PACK_ON_MISS:
        try:
            debug_message("No pack animals auto-detected. Target a pack animal to use...", 33)
            sel = Target.PromptTarget()
            if sel != -1:
                mob = Mobiles.FindBySerial(sel)
                if mob:
                    candidates.append(mob)
                    # cache for subsequent calls during this run
                    try:
                        if all(int(x) != int(sel) for x in PACKHORSE_SERIALS):
                            PACKHORSE_SERIALS.append(int(sel))
                    except Exception:
                        pass
        except Exception:
            pass
    if not candidates and DEBUG_MODE:
        try:
            # Diagnostics: list nearby mobiles to help refine filters
            f2 = Mobiles.Filter()
            f2.RangeMax = int(PACK_SEARCH_RANGE)
            Mobiles.ApplyFilter(f2)
            test_list = Mobiles.GetList()
            debug_message(f"No pack animals matched. Nearby mobiles ({len(test_list)} within {PACK_SEARCH_RANGE}):", 33)
            for mm in test_list[:8]:
                try:
                    debug_message(f"- {mm.Serial} name='{mm.Name}' body={getattr(mm,'Body',None)}", 33)
                except Exception:
                    pass
        except Exception:
            pass
    return candidates

def _find_hay_items_in_container(container_item, hay_item_id):
    """Return a list of hay items (by ItemID) in the given container.
    Note: This version only reads current contents (no opening). Use the mob-aware
    wrapper below to ensure contents are populated when needed.
    """
    items = []
    try:
        contains = Items.FindBySerial(container_item.Serial).Contains
    except Exception:
        contains = None
    if not contains:
        return items
    for it in contains:
        try:
            if int(it.ItemID) == int(hay_item_id):
                items.append(it)
        except Exception:
            continue
    return items

def _open_pack_and_poll_contents(mob, container_serial, timeout_ms=2500):
    """Open the pack via UseMobile and poll for the container contents to populate."""
    try:
        try:
            Mobiles.UseMobile(mob.Serial)
        except Exception:
            try:
                Misc.UseObject(mob.Serial)
            except Exception:
                pass
    except Exception as e:
        debug_message(f"UseMobile during poll failed: {e}", 33)
    elapsed = 0
    step = 200
    while elapsed <= timeout_ms:
        Misc.Pause(step)
        elapsed += step
        try:
            cont = Items.FindBySerial(container_serial)
            if cont and getattr(cont, 'Contains', None):
                return cont.Contains
        except Exception:
            pass
    return []

def _move_item_to_container(it, dest_container):
    for attempt in range(1, 1 + 3):
        try:
            Items.Move(it, dest_container, 0)
            pause_ms(350)
        except Exception as e:
            debug_message(f"Pack move error ({attempt}) {it.Serial}: {e}", 33)
            pause_ms(300)
            continue
        # Verify
        try:
            moved_ref = Items.FindBySerial(it.Serial)
            if moved_ref and moved_ref.Container == dest_container.Serial:
                return True
        except Exception:
            pass
        pause_ms(250)
    return False

def attempt_autorestock_hay_from_packs(item_id, desired_count):
    """Try to pull up to desired_count hay items from pack animals into the player's backpack.
    Returns the number of items successfully moved.
    """
    total_moved = 0
    packs = _find_nearby_pack_mobiles()
    if not packs:
        debug_message("No pack animals found nearby for auto-restock.", 33)
        return 0
    for mob in packs:
        if total_moved >= desired_count:
            break
        cont = _get_pack_container_from_mobile(mob)
        if not cont:
            debug_message(f"Could not resolve pack container for mobile {mob.Serial}", 33)
            continue
        # Ensure contents are populated; open and poll if needed
        try:
            contains = Items.FindBySerial(cont.Serial).Contains
        except Exception:
            contains = None
        if not contains:
            debug_message(f"Pack {mob.Serial} container {cont.Serial} empty list; opening and polling...", 67)
            contains = _open_pack_and_poll_contents(mob, cont.Serial, timeout_ms=2500)
        # Enumerate and filter hay
        hay_items = []
        for it in (contains or []):
            try:
                if int(it.ItemID) == int(item_id):
                    hay_items.append(it)
            except Exception:
                continue
        if not hay_items:
            # mark this pack as depleted of the requested item
            try:
                PACK_DEPLETED_SERIALS.add(int(mob.Serial))
            except Exception:
                pass
            continue
        for it in hay_items:
            if total_moved >= desired_count:
                break
            if _move_item_to_container(it, Player.Backpack):
                total_moved += 1
                # unmark depletion if we successfully moved from this pack
                try:
                    if int(mob.Serial) in PACK_DEPLETED_SERIALS:
                        PACK_DEPLETED_SERIALS.discard(int(mob.Serial))
                except Exception:
                    pass
    return total_moved

def place_points_with_checkpoint(points, item_id, cp_path, cp_state_key="placed_walls", label="Placing walls", center=None):
    placed_set = set()

    # Load existing checkpoint
    cp = load_checkpoint(cp_path)
    if cp and cp.get(cp_state_key):
        for t in cp.get(cp_state_key, []):
            placed_set.add(tuple(t))

    # Skip already placed
    remaining_points = [p for p in points if (p[0], p[1]) not in placed_set]
    debug_message(f"{label}: {len(placed_set)} already placed, {len(remaining_points)} remaining", 67)

    # Place with periodic checkpointing and restock handling
    placed_since_cp = 0
    failures = 0

    for idx, (x, y) in enumerate(remaining_points, 1):
        debug_message(f"{label}: {idx} out of {len(remaining_points)}", 67)

        if not PREVIEW_MODE:
            if not goto_location_with_wiggle(x, y, center=center):
                debug_message(f"Could not reach position ({x}, {y})", 33)
                failures += 1
                if failures >= MAX_PHASE_FAILURES:
                    debug_message("Too many failures in this phase; aborting early.", 33)
                    break
                continue

        # Ensure we have at least 1 item; if none, wait for restock
        if not PREVIEW_MODE:
            try:
                have = Items.BackpackCount(item_id, -1)
            except Exception:
                have = 0
            if have <= 0:
                # Save checkpoint before waiting
                cp_out = cp or {}
                cp_out.update({
                    "seed": cp_out.get("seed"),
                    cp_state_key: list(placed_set),
                })
                save_checkpoint(cp_path, cp_out)
                if not wait_for_restock_if_needed(item_id, 1):
                    break

        if place_item(x, y, item_id):
            placed_set.add((x, y))
            ALL_PLACED_COORDS.add((x, y))
            placed_since_cp += 1
        else:
            failures += 1
            if failures >= MAX_PHASE_FAILURES:
                debug_message("Too many placement failures; aborting early.", 33)
                break

        if PREVIEW_MODE:
            pause_ms(PREVIEW_BREATHER_MS)
        else:
            pause_ms(POINT_BREATHER_MS)

        # Periodic checkpoint
        if placed_since_cp >= CHECKPOINT_EVERY_N:
            cp_out = cp or {}
            cp_out.update({
                "seed": cp_out.get("seed"),
                cp_state_key: list(placed_set),
            })
            save_checkpoint(cp_path, cp_out)
            placed_since_cp = 0

    # Final checkpoint
    cp_out = cp or {}
    cp_out.update({
        "seed": cp_out.get("seed"),
        cp_state_key: list(placed_set),
    })
    save_checkpoint(cp_path, cp_out)

    return placed_set

# ============================= Main =============================

def display_configuration():
    debug_message("Current Maze Configuration:", 67)
    debug_message(f"Size: {MAZE_CONFIG['width']} x {MAZE_CONFIG['height']} (cell_size={MAZE_CONFIG['cell_size']})", 67)
    debug_message(f"Seed: {MAZE_CONFIG['seed']}", 67)
    debug_message(f"Preview: {PREVIEW_MODE} (show_solution={MAZE_CONFIG['show_solution']})", 67)

def get_first_available_item_id(item_ids, required_count):
    if isinstance(item_ids, int) or item_ids is None:
        item_ids = [item_ids]
    for item_id in item_ids:
        if item_id is None:
            continue
        if PREVIEW_MODE:
            return item_id
        try:
            if Items.BackpackCount(item_id, -1) >= required_count:
                return item_id
        except Exception:
            pass
    for item_id in item_ids:
        if item_id is not None:
            return item_id
    return None

def choose_best_seed_in_preview(center_x, center_y):
    tries = int(MAZE_CONFIG.get("tries_in_preview", 5))
    best = None
    for _ in range(tries):
        s = random.randint(0, 1000000)
        m = generate_maze(MAZE_CONFIG["width"], MAZE_CONFIG["height"], s)
        if best is None or m["score"] > best["score"]:
            best = m
    debug_message(f"Chosen seed {best['seed']} with score {best['score']}", 68)
    return best

def preview_maze(center_x, center_y, maze):
    # Walls
    wall_points = build_wall_points_from_grid(center_x, center_y, maze, MAZE_CONFIG["cell_size"])
    wall_item_ids = MAZE_CONFIG["wall_item_ids"]
    wall_item_id = get_first_available_item_id(wall_item_ids, 1)
    # Report total hay required for this maze
    debug_message(f"Hay required: {len(wall_points)}", 67)
    for i, (x, y) in enumerate(wall_points, 1):
        preview_item_at(x, y, -1, wall_item_id, PREVIEW_DEFAULT_HUE)
        # Light pacing to ensure packets render reliably
        pause_ms(max(1, PREVIEW_BREATHER_MS // 3))
        if i % 40 == 0:
            pause_ms(PREVIEW_BREATHER_MS)
    # Solution overlay
    if MAZE_CONFIG.get("show_solution", False):
        sol_points = build_solution_points_from_grid(center_x, center_y, maze, MAZE_CONFIG["cell_size"])
        sol_item_ids = MAZE_CONFIG["solution_item_ids"]
        sol_item_id = get_first_available_item_id(sol_item_ids, 1)
        for i, (x, y) in enumerate(sol_points, 1):
            # Draw solution slightly above/below wall Z to prevent visual overlap issues
            preview_item_at(x, y, -2, sol_item_id, PREVIEW_SOLUTION_HUE)
            # Slightly higher pacing for overlay to avoid missing renders
            pause_ms(max(1, PREVIEW_BREATHER_MS // 2))
            if i % 40 == 0:
                pause_ms(PREVIEW_BREATHER_MS)

def create_maze_arrangement(center_x, center_y):
    debug_message("Beginning maze arrangement...", 67)

    center = (center_x, center_y)
    z = -1

    # Determine seed and generate maze
    seed = MAZE_CONFIG.get("seed")
    if seed is None:
        seed = random.randint(0, 1000000)
        MAZE_CONFIG["seed"] = seed

    maze = generate_maze(MAZE_CONFIG["width"], MAZE_CONFIG["height"], seed)

    if PREVIEW_MODE:
        # Optionally reselect best seed among tries
        if MAZE_CONFIG.get("prefer_winding", False):
            maze = choose_best_seed_in_preview(center_x, center_y)
        preview_maze(center_x, center_y, maze)
        debug_message("Preview complete.", 67)
        return

    # Real placement
    # Move to center first if possible
    if not goto_location_with_wiggle(center_x, center_y, center=center):
        debug_message("Could not reach center position!", 33)
        return

    wall_points = build_wall_points_from_grid(center_x, center_y, maze, MAZE_CONFIG["cell_size"])

    wall_item_ids = MAZE_CONFIG["wall_item_ids"]
    wall_item_id = get_first_available_item_id(wall_item_ids, 1)
    if wall_item_id is None:
        debug_message("No wall item configured or found.", 33)
        return

    # Prepare checkpoint
    cp_path = checkpoint_path(center_x, center_y, maze["width"], maze["height"], maze["seed"])
    cp = load_checkpoint(cp_path) or {}
    cp.setdefault("seed", maze["seed"])
    save_checkpoint(cp_path, cp)

    placed = place_points_with_checkpoint(
        wall_points,
        wall_item_id,
        cp_path,
        cp_state_key="placed_walls",
        label="Placing hay walls",
        center=center,
    )
    debug_message(f"Placed {len(placed)} maze wall tiles.", 68 if placed else 33)

    debug_message("Maze arrangement complete!", 67)

def main():
    display_configuration()

    center_x = Player.Position.X
    center_y = Player.Position.Y

    if PREVIEW_MODE and MAZE_CONFIG.get("prefer_winding", False):
        # Score multiple seeds and preview the best
        best = choose_best_seed_in_preview(center_x, center_y)
        preview_maze(center_x, center_y, best)
        return

    create_maze_arrangement(center_x, center_y)

if __name__ == "__main__":
    main()
