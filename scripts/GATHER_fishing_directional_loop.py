"""
GATHER FISH Directional Loop - A Razor Enhanced Python Script for Ultima Online

fishing in the direction the player is facing, 
then chop fish and drop boots/shoes as configured.

STATUS: not working , in progress updating to match current shard
VERSION::20250818
"""

from System.Collections.Generic import List
from System import Int32

# --- GLOBAL SETTINGS ---
SHOW_DEBUG = False          # Toggle to show/hide debug messages
FISH_CHOP_ENABLED = True   # Set to False to skip fish chopping
SHOE_DROP_ENABLED = True   # Set to False to skip shoe dropping

# List of fishing pole item IDs (add more as needed)
FISHING_POLE_ID_LIST = [
    0x0DBF,  # Standard fishing pole
    0x0DC0,  # Fishing pole variant
]

FISHING_ATTEMPTS = 5      # How many times to cast per cycle
FISHING_PAUSE = 1200       # Pause between casts (ms)
WAIT_FOR_BITE = 7500      # Wait after last cast (ms)

# Targeting behavior
TARGET_DISTANCE_TILES = 2  # How many tiles in front to target (closer than before)
PRE_TARGET_DELAY = 1000     # Small delay after using the rod before targeting (ms)
PREFERRED_TARGET_DISTANCE = 3  # Distance to actually target when casting (closest-first)
AFTER_TARGET_CHECK_DELAY = 1000  # Time to wait for journal feedback after targeting (ms)

# Common water static IDs seen across shards (prioritized)
# Prioritize shard-confirmed order: 6042 first
WATER_STATIC_IDS = [6042, 6044, 6043, 6041, 6040]

# --- OPTIONAL MANUAL OVERRIDES ---
# If you know an exact working pole serial and/or target tile, set these.
# Example from user: pole serial 0x407CC45C and target (1507, 1721, -5, 6044)
OVERRIDE_POLE_SERIAL = None           # e.g., 0x407CC45C or None
OVERRIDE_TARGET = None                # e.g., (1507, 1721, -5, 6044) or None
# Try a single world offset from current player position once per cast (before other candidates)
# Based on validation: +4 X, +0 Y works reliably on this shard
CUSTOM_RELATIVE_OFFSET = (4, 0)       # e.g., (4, 0) or None
DEBUG_OVERRIDE_ONLY = False           # If True and OVERRIDE_TARGET set, do ONLY the override click per cast

# --- DEBUG MESSAGE HELPER ---
def debug_message(msg, color=55):
    if SHOW_DEBUG:
        Misc.SendMessage(msg, color)

# --- FISH AND TOOL DATA ---
fishIDList = [
    ['FishType1', 0x09CF, None],
    ['FishType2', 0x09CC, None],
    ['FishType3', 0x09CD, None],
    ['FishType4', 0x44C6, None],
    ['FishType5', 0x4306, None],
    ['FishType6', 0x4307, None],
    ['FishType7', 0x4303, None],
    ['FishType8', 0x44C4, None],
    ['FishType9', 0x44C3, None],
    ['FishType10', 0x09CE, None]
]
knifeIDList = [
    ['Butcher Knife', 0x0F52, None],
    ['Dagger', 0x0F53, None],
    ['Sword', 0x0F54, None]
]
shoeIDList = [
    ['boot', 0x170B, None],
    ['thighboot', 0x1711, None],
    ['smallfish', 0x0DD6, None],
    ['sandal', 0x170D, None],
    ['shoe', 0x170F, None],
    ['emptypitcher', 0x0FF6, None]
]

# --- UTILITY: Direction + Tile in Front ---
def get_direction_offset(direction):
    """Return (dx, dy) for either numeric (0-7) or string directions."""
    # Numeric mapping
    numeric = {
        0: (0, -1),  # N
        1: (1, -1),  # NE
        2: (1, 0),   # E
        3: (1, 1),   # SE
        4: (0, 1),   # S
        5: (-1, 1),  # SW
        6: (-1, 0),  # W
        7: (-1, -1), # NW
    }
    # String mapping (as seen in your logs: "East")
    textual = {
        'North': (0, -1),
        'Northeast': (1, -1),
        'East': (1, 0),
        'Southeast': (1, 1),
        'South': (0, 1),
        'Southwest': (-1, 1),
        'West': (-1, 0),
        'Northwest': (-1, -1),
        # Some UIs may use arrows/short names
        'Up': (0, -1), 'Right': (1, 0), 'Down': (0, 1), 'Left': (-1, 0),
        'NE': (1, -1), 'SE': (1, 1), 'SW': (-1, 1), 'NW': (-1, -1),
    }
    if isinstance(direction, int):
        return numeric.get(direction, (0, 0))
    return textual.get(str(direction), (0, 0))

def tileInFront(distance: int = None):
    """
    Get the tile in front of the player based on facing direction.
    The Z is hardcoded to -5 for sea tiles (known info for most OSI/UOR shards).
    """
    direction = Player.Direction
    playerX = Player.Position.X
    playerY = Player.Position.Y
    playerZ = Player.Position.Z
    playerMap = Player.Map
    debug_message(f"Player position: X={playerX}, Y={playerY}, Z={playerZ}, Map={playerMap}")
    debug_message(f"Player direction: {direction}")

    dx, dy = get_direction_offset(direction)
    dist = TARGET_DISTANCE_TILES if distance is None else max(0, int(distance))
    tileX = playerX + (dx * dist)
    tileY = playerY + (dy * dist)
    tileZ = -5  # For the sea we know it is -5
    dxt = tileX - playerX
    dyt = tileY - playerY
    # Manhattan and Chebyshev distances are often more relevant on tile grids; include both
    manhattan = abs(dxt) + abs(dyt)
    chebyshev = max(abs(dxt), abs(dyt))
    debug_message(
        f"Target tile (dist={dist}): X={tileX}, Y={tileY}, Z={tileZ}, Map={playerMap} | dX={dxt}, dY={dyt}, tiles(Cheb)={chebyshev}, tiles(Manh)={manhattan}"
    )
    return tileX, tileY, tileZ, playerMap

# --- FISHING MODULE ---
def get_fishing_pole():
    """
    Return an equipped fishing pole if present; otherwise try to equip one
    from backpack. Returns the item (object) or None if unavailable.
    """
    # Check both hands first
    for hand in ['LeftHand', 'RightHand']:
        in_hand = Player.GetItemOnLayer(hand)
        if in_hand and in_hand.ItemID in FISHING_POLE_ID_LIST:
            debug_message(f"Using equipped fishing pole in {hand} (0x{in_hand.ItemID:X})")
            return in_hand

    # Try to equip from backpack
    backpack = Player.Backpack.Serial
    for pole_id in FISHING_POLE_ID_LIST:
        item = Items.FindByID(pole_id, -1, backpack, 0, 0)
        if item:
            debug_message(f"Found fishing pole in backpack: 0x{pole_id:X}, equipping...")
            Player.EquipItem(item)
            Misc.Pause(600)
            # Verify it's equipped now
            for hand in ['LeftHand', 'RightHand']:
                in_hand = Player.GetItemOnLayer(hand)
                if in_hand and in_hand.ItemID == pole_id:
                    return in_hand

    debug_message("No fishing pole equipped or in backpack!", 33)
    return None

def do_fishing_cycle():
    """
    Perform a fishing cycle: cast rod several times at the tile in front.
    Uses multiple staticIDs for water tiles (covers most custom/OSI shards).
    """
    pole = get_fishing_pole()
    if not pole:
        debug_message("Fishing cycle aborted: No fishing pole available.", 33)
        return

    # Compute a farther tile for info, and a closer, preferred tile for the actual cast
    farX, farY, farZ, mapID = tileInFront(TARGET_DISTANCE_TILES)
    tileX, tileY, tileZ, _ = tileInFront(PREFERRED_TARGET_DISTANCE)
    # Summarize current player position again just before casting, in case movement occurred
    pX = Player.Position.X
    pY = Player.Position.Y
    pZ = Player.Position.Z
    pMap = Player.Map
    dX = tileX - pX
    dY = tileY - pY
    manh = abs(dX) + abs(dY)
    cheb = max(abs(dX), abs(dY))
    debug_message(
        f"Fishing cycle: Player(X={pX},Y={pY},Z={pZ},Map={pMap})\n  Preferred Target: (X={tileX},Y={tileY},Z={tileZ}) dX={dX}, dY={dY}, tiles(Cheb)={cheb}, tiles(Manh)={manh}\n  Far Config Target: (X={farX},Y={farY},Z={farZ})"
    )

    # Helper to cast and evaluate at a specific distance
    def cast_to_distance(dist):
        tX, tY, tZ, _ = tileInFront(dist)
        pXc, pYc = Player.Position.X, Player.Position.Y
        dXc, dYc = tX - pXc, tY - pYc
        cheb, manh = max(abs(dXc), abs(dYc)), abs(dXc) + abs(dYc)
        debug_message(
            f"Attempting target (dist={dist}): Target(X={tX},Y={tY},Z={tZ}) | dX={dXc}, dY={dYc}, tiles(Cheb)={cheb}, tiles(Manh)={manh}"
        )
        
        # If debug override-only mode is on, perform exactly the proven 3-step sequence and return
        if DEBUG_OVERRIDE_ONLY and OVERRIDE_TARGET is not None:
            ox, oy, oz, oid = OVERRIDE_TARGET
            Journal.Clear()
            debug_message(f"[DEBUG-ONLY] Override click (X={ox},Y={oy},Z={oz}) sid={oid}")
            if OVERRIDE_POLE_SERIAL is not None:
                Items.UseItem(OVERRIDE_POLE_SERIAL)
            else:
                Items.UseItem(pole)
            Target.WaitForTarget(10000, False)
            # Small arming delay to ensure reticle is fully active
            Misc.Pause(150)
            pre_has = Target.HasTarget()
            Target.TargetExecute(int(ox), int(oy), int(oz), int(oid))
            Misc.Pause(50)
            post_has = Target.HasTarget()
            debug_message(f"[DEBUG-ONLY] reticle pre={pre_has} post={post_has}")
            if post_has:
                # Click had no effect; cancel to avoid stuck reticle
                Target.Cancel()
            Misc.Pause(AFTER_TARGET_CHECK_DELAY)
            # Hard-stop if shard reports no fish here
            if stop_if_no_fish():
                return False
            # Evaluate minimal feedback
            fail_phrases = [
                "You need to be closer to the water to fish",
                "There is no water here",
                "You can't fish there",
                "Target cannot be seen",
            ]
            success_phrases = [
                "You fish a",
                "You pull out",
                "You fail to catch anything",
                "You fish up",
            ]
            for phrase in fail_phrases:
                if Journal.Search(phrase):
                    debug_message(f"[DEBUG-ONLY] FAIL '{phrase}'", 33)
                    return False
            for phrase in success_phrases:
                if Journal.Search(phrase):
                    debug_message(f"[DEBUG-ONLY] SUCCESS '{phrase}'", 67)
                    return True
            debug_message("[DEBUG-ONLY] NO_FEEDBACK", 55)
            return False

        # Build a lateral fan of candidate coordinates around forward tiles at distances [dist, dist+1]
        dx, dy = get_direction_offset(Player.Direction)
        distances = [dist, dist + 1]
        candidates = []
        # First, if a custom relative offset is configured, try it ONCE for the preferred distance only
        if CUSTOM_RELATIVE_OFFSET is not None and dist == PREFERRED_TARGET_DISTANCE:
            px, py = Player.Position.X, Player.Position.Y
            offx, offy = CUSTOM_RELATIVE_OFFSET
            candidates.append((px + offx, py + offy, f"d{dist}:custom:+{offx},+{offy}"))
        for d in distances:
            bx, by, _, _ = tileInFront(d)
            label_base = f"d{d}:base"
            if abs(dx) == 1 and dy == 0:  # East/West: try +Y first (your success), then base, then -Y
                candidates.append((bx, by + 1, f"d{d}:perp:+Y"))
                candidates.append((bx, by, label_base))
                candidates.append((bx, by - 1, f"d{d}:perp:-Y"))
            elif abs(dy) == 1 and dx == 0:  # North/South
                candidates.append((bx + 1, by, f"d{d}:perp:+X"))
                candidates.append((bx, by, label_base))
                candidates.append((bx - 1, by, f"d{d}:perp:-X"))
            else:
                candidates.append((bx, by + (1 if dy > 0 else -1), f"d{d}:diag:Ystep"))
                candidates.append((bx, by, label_base))
                candidates.append((bx + (1 if dx > 0 else -1), by, f"d{d}:diag:Xstep"))

        # Define sub-attempts: ONE try per coordinate with preferred static ID only, then move on
        PREFERRED_SID = WATER_STATIC_IDS[0] if WATER_STATIC_IDS else None
        sub_attempts = []
        for (cx, cy, label) in candidates:
            sub_attempts.append((cx, cy, -5, PREFERRED_SID, f"{label}:static:{PREFERRED_SID}@-5"))

        # Detect phrases
        # Do NOT include the targeting prompt as a failure
        prompt_phrase = "What water do you want to fish in?"
        busy_phrase = "You are already fishing"
        fail_phrases = [
            "You need to be closer to the water to fish",
            "There is no water here",
            "You can't fish there",
            "Target cannot be seen",
        ]
        success_phrases = [
            "You fish a",
            "You pull out",
            "You fail to catch anything",
            "You fish up",
        ]

        # Run sub-attempts:
        # For each coordinate, try SIDs in WATER_STATIC_IDS order.
        # If NO_FEEDBACK, advance to next SID. On FAIL phrase, move to next coordinate.
        for (sx, sy, sz, sid, label) in sub_attempts:
            # If already fishing, skip issuing new target to avoid spam
            if Journal.Search(busy_phrase):
                debug_message(f"{label}: detected 'already fishing' — pausing.", 53)
                Journal.Clear()
                Misc.Pause(1200)
                return True
            # Try each water SID in order for this coordinate
            for try_sid in WATER_STATIC_IDS:
                Journal.Clear()
                # Use the pole and ensure the target cursor is actually active
                if OVERRIDE_POLE_SERIAL is not None:
                    Items.UseItem(OVERRIDE_POLE_SERIAL)
                else:
                    Items.UseItem(pole)
                Misc.Pause(PRE_TARGET_DELAY)
                Target.WaitForTarget(12000, False)
                # Extra assurance: poll HasTarget to ensure the cursor is up
                waited = 0
                while not Target.HasTarget() and waited < 2000:
                    Misc.Pause(50)
                    waited += 50
                pre_has = Target.HasTarget()
                Target.TargetExecute(int(sx), int(sy), int(sz), int(try_sid))
                Misc.Pause(50)
                post_has = Target.HasTarget()
                debug_message(f"{label}:SID={try_sid} reticle pre={pre_has} post={post_has}")
                if post_has:
                    Target.Cancel()
                debug_message(f"{label}: click (X={sx},Y={sy},Z={sz}) sid={try_sid}")
                Misc.Pause(AFTER_TARGET_CHECK_DELAY)
                # Hard-stop if shard reports no fish here
                if stop_if_no_fish():
                    return False

                matched_fail = None
                for phrase in fail_phrases:
                    if Journal.Search(phrase):
                        matched_fail = phrase
                        break
                matched_ok = None
                for phrase in success_phrases:
                    if Journal.Search(phrase):
                        matched_ok = phrase
                        break
                # If already fishing, treat as busy and stop spamming
                if Journal.Search(busy_phrase):
                    debug_message(f"{label}: detected 'already fishing' — pausing.", 53)
                    Journal.Clear()
                    Misc.Pause(1200)
                    return True

                if matched_ok:
                    debug_message(f"{label}: SUCCESS '{matched_ok}' using SID={try_sid}", 67)
                    return True
                if matched_fail:
                    debug_message(f"{label}: FAIL '{matched_fail}' on SID={try_sid}", 33)
                    # On a real fail, don't try other SIDs for this coord; move to next coordinate
                    break
                # NO_FEEDBACK -> try next SID
                debug_message(f"{label}: NO_FEEDBACK on SID={try_sid} — trying next SID", 55)
            # After trying all SIDs for this coordinate, move on to next coordinate
            
        # If all coordinates tried with no success, try OVERRIDE as a last resort
        if OVERRIDE_TARGET is not None:
            ox, oy, oz, oid = OVERRIDE_TARGET
            Journal.Clear()
            debug_message(f"[OVERRIDE-LAST] (X={ox},Y={oy},Z={oz}) sid={oid}")
            # Use override pole serial if provided, else use detected pole
            if OVERRIDE_POLE_SERIAL is not None:
                Items.UseItem(OVERRIDE_POLE_SERIAL)
            else:
                Items.UseItem(pole)
            Target.WaitForTarget(10000, False)
            Misc.Pause(150)
            pre_has = Target.HasTarget()
            Target.TargetExecute(int(ox), int(oy), int(oz), int(oid))
            Misc.Pause(50)
            post_has = Target.HasTarget()
            debug_message(f"[OVERRIDE-LAST] reticle pre={pre_has} post={post_has}")
            if post_has:
                Target.Cancel()
            Misc.Pause(AFTER_TARGET_CHECK_DELAY)
            if Journal.Search(busy_phrase):
                debug_message("[OVERRIDE-LAST] detected 'already fishing' — pausing.", 53)
                Journal.Clear()
                Misc.Pause(1200)
                return True
            for phrase in fail_phrases:
                if Journal.Search(phrase):
                    debug_message(f"[OVERRIDE-LAST] FAIL '{phrase}'", 33)
                    break
            else:
                for phrase in success_phrases:
                    if Journal.Search(phrase):
                        debug_message(f"[OVERRIDE-LAST] SUCCESS '{phrase}'", 67)
                        return True
                debug_message("[OVERRIDE-LAST] NO_FEEDBACK", 55)

        # If all sub-attempts failed
        debug_message(
            f"Cast result: FAIL (all modes) at target base (X={tX},Y={tY}) | dX={dXc}, dY={dYc}, tiles(Cheb)={cheb}",
            33,
        )
        return False

    had_successful_target = False
    for i in range(FISHING_ATTEMPTS):
        # If already fishing, stop issuing new casts this cycle
        if Journal.Search("You are already fishing"):
            debug_message("Detected 'already fishing' — pausing.", 53)
            Journal.Clear()
            Misc.Pause(1200)
            had_successful_target = True
            break
        debug_message(f"Casting attempt {i+1} of {FISHING_ATTEMPTS}")
        # Try preferred distance first, then fallback to configured farther distance
        if cast_to_distance(PREFERRED_TARGET_DISTANCE):
            had_successful_target = True
            Misc.Pause(FISHING_PAUSE)
            continue
        # Fallback distance
        if cast_to_distance(TARGET_DISTANCE_TILES):
            had_successful_target = True
        Misc.Pause(FISHING_PAUSE)
    if had_successful_target:
        debug_message(f"Waiting {WAIT_FOR_BITE}ms for bites...")
        Misc.Pause(WAIT_FOR_BITE)
    else:
        debug_message("Skipping bite wait: no successful targets this cycle.", 53)

# --- FISH CHOP MODULE ---
def chop_all_fish():
    """
    Use a knife (of any type) on all fish types in the player's backpack.
    """
    playerBackpack = Player.Backpack.Serial
    knife = None
    for tool in knifeIDList:
        _, toolID, _ = tool
        knife = Items.FindByID(toolID, -1, playerBackpack)
        if knife:
            debug_message(f"Found knife: 0x{toolID:X}")
            break
    if not knife:
        debug_message("No knife found in backpack.", 33)
        return
    for fish in fishIDList:
        fishName, fishID, fishColor = fish
        if fishColor is None:
            fishColor = -1
        fishItems = Items.FindAllByID(fishID, fishColor, playerBackpack, False)
        debug_message(f"Found {len(fishItems)} of {fishName} (ID: {hex(fishID)}) in backpack.")
        for fishItem in fishItems:
            Items.UseItem(knife)
            Target.WaitForTarget(10000, False)
            Target.TargetExecute(fishItem)
            Misc.Pause(600)
            debug_message(f"Used knife on {fishName} (ID: {hex(fishID)})", 65)

# --- SHOE DROP MODULE ---
def drop_all_shoes():
    """
    Move all shoes/boots (and optionally pitchers) in backpack to the player's absolute world position.
    """
    px, py, pz = Player.Position.X, Player.Position.Y, Player.Position.Z
    playerBackpack = Player.Backpack.Serial
    debug_message(f"Dropping shoes/boots at player pos X={px}, Y={py}, Z={pz}")
    for shoe in shoeIDList:
        itemName, itemID, itemColor = shoe
        if itemColor is None:
            itemColor = -1
        foundItem = Items.FindByID(itemID, itemColor, playerBackpack, 0, 0)
        if foundItem:
            debug_message(f"Dropping {itemName} (ID: {hex(itemID)}) at ({px},{py},{pz})")
            Items.MoveOnGround(foundItem.Serial, 0, px, py, pz)
            Misc.Pause(1600)
        else:
            debug_message(f"No {itemName} (ID: {hex(itemID)}) found in backpack.")
            Misc.Pause(100)

# --- PICKUP GROUND FISH MODULE ---
def collect_ground_fish(max_distance=2):
    """
    Pick up fish items on the ground near the player into the backpack using Items.Filter,
    mirroring the approach in PICKUP_gold_and_meditate.py but for all fish graphics.
    """
    # Build list of fish graphics (IDs)
    fish_ids = [fid for _, fid, _ in fishIDList]
    # Include smallfish from shoeIDList if present
    for name, iid, _ in shoeIDList:
        if name.lower() == 'smallfish':
            fish_ids.append(iid)
            break

    # Create filter for ground items within range
    f = Items.Filter()
    f.Enabled = True
    f.OnGround = True
    f.RangeMin = 0
    f.RangeMax = int(max_distance)
    f.Graphics = List[Int32]([Int32(i) for i in fish_ids])
    items = Items.ApplyFilter(f)

    if not items:
        debug_message("No ground fish nearby to collect.", 53)
        return

    picked = 0
    failed = 0
    for it in items:
        # Only move if actually on ground
        if it.Container == 0 or it.Container == 0xFFFFFFFF:
            try:
                Items.Move(it, Player.Backpack, 0)
                Misc.Pause(400)
                picked += 1
            except Exception as e:
                debug_message(f"Failed to pick ground fish {it.Serial:X}: {e}", 33)
                failed += 1
    if picked:
        debug_message(f"Collected {picked} ground fish to backpack. Failed: {failed}", 68)
    else:
        debug_message("No eligible ground fish to collect (post-filter).", 53)

# --- MAIN LOOP ---
def main():
    debug_message("Starting GATHER FISH main all script.")
    while True:
        debug_message("--- New fishing cycle ---", 53)
        do_fishing_cycle()
        # Could check for 'no bites' or overweight here for more advanced logic
        if FISH_CHOP_ENABLED:
            debug_message("Chopping all fish in backpack after fishing cycle.", 68)
            # Pick up any fish on the ground nearby before chopping
            collect_ground_fish(max_distance=2)
            chop_all_fish()
        else:
            debug_message("Fish chopping disabled.", 53)
        if SHOE_DROP_ENABLED:
            debug_message("Dropping all shoes/boots after fishing cycle.", 68)
            drop_all_shoes()
        else:
            debug_message("Shoe dropping disabled.", 53)
        # Add more logic here if you want to break/stop

# --- JOURNAL & WEIGHT CHECKS ---
def check_no_bites_in_journal():
    """
    Check the journal for any 'no fish are biting' or equivalent message.
    Returns True if such a message is found, False otherwise.
    """
    no_bites_phrases = [
        "no fish are biting",
        "there are no fish here",
        "you fail to catch anything",
        "the fish don't seem interested"
    ]
    for phrase in no_bites_phrases:
        if Journal.Search(phrase):
            debug_message(f"Journal: Detected no bites message: '{phrase}'", 53)
            return True
    return False

# Stop script immediately if shard shows a hard no-fish message
def stop_if_no_fish():
    phrases = [
        "the fish dont seem to be biting here.",  # without apostrophe (as reported)
        "The fish don't seem to be biting here.", # with apostrophe / capitalized
    ]
    for p in phrases:
        if Journal.Search(p):
            Player.HeadMessage(33, "NO FISH")
            Misc.ScriptStop("GATHER_fishing_directional_loop.py")
            return True
    return False

def is_player_overweight(threshold_pct=98):
    """
    Check if the player is overweight (by % of max weight).
    Returns True if overweight, False otherwise.
    """
    current = Player.Weight
    maxweight = Player.MaxWeight
    percent = (current / float(maxweight)) * 100 if maxweight > 0 else 0
    debug_message(f"Weight check: {current}/{maxweight} ({percent:.1f}%)")
    return percent >= threshold_pct

if __name__ == "__main__":
    main()
