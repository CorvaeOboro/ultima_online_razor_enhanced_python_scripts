"""
SPELL poison field - a Razor Enhanced Python script for Ultima Online

cast poison field on nearest enemy

HOTKEY:: D
VERSION::20251016
"""
import time
import random
from System.Collections.Generic import List
from Scripts.glossary.enemies import GetEnemyNotorieties, GetEnemies
from Scripts.utilities.mobiles import GetEmptyMobileList

DEBUG_MODE = False
MANA_REQUIRED = True
REAGENT_REQUIRED = True
EQUIP_SPELLBOOK = False  # equip spellbook from backpack if not equipped, set False to require manual equip, were using staff 
SAFE_MODE = False  # extra conservative pacing and movement

# Targeting Mode: 'mobile' targets the enemy directly, 'ground' targets the ground at enemy position
TARGET_MODE = 'mobile'  # Options: 'mobile', 'ground'
TEST_Z_OFFSETS = True  # Try Z-1, Z-2 if initial target fails (only for ground mode)
CHECK_LINE_OF_SIGHT = False  # Verify line of sight before targeting (can cause issues)
Z_OFFSETS_TO_TRY = [0, -1, -2, 1]  # Z offsets to try in order if targeting fails

CAST_DELAY_MS = 1200
TARGET_POST_EXECUTE_DELAY_MS = 1
EQUIP_DELAY_MS = 1
LOOP_YIELD_MS = 40
JITTER_MS = 50
RATE_MIN_GAP_MS = 300

#//===============  Spell/Combat Config =======================

SPELL_NAME = "Poison Field"
# Typical reagents for Poison Field: Black Pearl, Nightshade, Spider's Silk
REAGENTS = {
    0xF7A: 1,  # Black Pearl
    0xF88: 1,  # Nightshade
    0xF8D: 1,  # Spider's Silk
}
SPELL_MANA = 15
SPELL_RANGE = 10  # max tile range for targeting
MIN_MANA_TO_TRY = 6

# Safety / Failure Handling
MAX_APPROACH_TIME_MS = 6000  # max time to try to walk into range with an active cursor
MAX_TOTAL_RUNTIME_MS = 12000

# Movement tuning (borrowed/adapted from RITUAL_feast.py)
MAX_DISTANCE = 2  # desired proximity tolerance for walking to a tile
GOTO_BASE_DELAY = 240
WALK_REPEATS_PER_DIR = 2
CENTER_BIAS_ENABLED = True
CENTER_NUDGE_DISTANCE = 3
CENTER_NUDGE_STEPS = 2
LAST_ACTION_MS = 0

#//===============  Utilities =======================

def debug_message(message, color=67):
    if not DEBUG_MODE:
        return
    try:
        Misc.SendMessage(f"[PoisonField] {message}", color)
    except Exception:
        print(f"[PoisonField] {message}")

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

#//===============  Movement helpers =======================

def get_direction(from_x, from_y, to_x, to_y):
    dx = to_x - from_x
    dy = to_y - from_y
    if dx == 0:
        if dy < 0:
            return 0  # N
        return 4  # S
    elif dy == 0:
        if dx > 0:
            return 2  # E
        return 6  # W
    elif dx > 0:
        if dy < 0:
            return 1  # NE
        return 3  # SE
    else:
        if dy < 0:
            return 7  # NW
        return 5  # SW

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
        dirs = [base_dir, (base_dir + 1) % 8, (base_dir + 7) % 8]
        moved = False
        for d in dirs:
            for _ in range(WALK_REPEATS_PER_DIR):
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
            step_delay = int(step_delay * 1.25) + 40
            pause_ms(step_delay)
    return (abs(Player.Position.X - tx) <= MAX_DISTANCE and
            abs(Player.Position.Y - ty) <= MAX_DISTANCE)

def goto_location_with_wiggle(x, y, center=None):
    target_x = int(float(x))
    target_y = int(float(y))

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

#//===============  Enemy selection =======================

def find_enemy():
    enemies = GetEnemies(Mobiles, 0, 12, GetEnemyNotorieties())
    if len(enemies) == 0:
        return None
    elif len(enemies) == 1:
        return enemies[0]
    else:
        enemiesInWarMode = GetEmptyMobileList(Mobiles)
        enemiesInWarMode.AddRange([enemy for enemy in enemies if enemy.WarMode])
        if len(enemiesInWarMode) == 0:
            return Mobiles.Select(enemies, 'Nearest')
        elif len(enemiesInWarMode) == 1:
            return enemiesInWarMode[0]
        else:
            return Mobiles.Select(enemiesInWarMode, 'Nearest')

#//===============  Spellbook and requirements =======================

def check_spellbook():
    # If auto-equip is disabled, skip spellbook check (using staff or other casting item)
    if not EQUIP_SPELLBOOK:
        return True
    
    # Check if equipped
    for layer in ['LeftHand', 'RightHand']:
        item = Player.GetItemOnLayer(layer)
        if item and item.ItemID == 0x0EFA:  # Spellbook
            return True
    
    # Try to equip from backpack
    spellbook = Items.FindByID(0x0EFA, -1, Player.Backpack.Serial, -1)
    if spellbook:
        debug_message("Equipping spellbook...")
        Player.EquipItem(spellbook)
        Misc.Pause(EQUIP_DELAY_MS)  # Only pause if we actually equipped
        return True
    debug_message("No spellbook found!", 33)
    return False

def have_mana():
    if not MANA_REQUIRED:
        return True
    if Player.Mana >= max(MIN_MANA_TO_TRY, SPELL_MANA):
        return True
    debug_message(f"Low mana: {Player.Mana}/{SPELL_MANA}", 33)
    return False

def have_reagents():
    if not REAGENT_REQUIRED:
        return True
    for itemid, qty in REAGENTS.items():
        if Items.BackpackCount(itemid) < qty:
            debug_message(f"Missing reagent 0x{itemid:X}", 33)
            return False
    return True

def in_spell_range(mobile):
    try:
        return Player.DistanceTo(mobile) <= SPELL_RANGE
    except Exception:
        # fallback: compute by coordinates
        dx = abs(int(mobile.Position.X) - int(Player.Position.X))
        dy = abs(int(mobile.Position.Y) - int(Player.Position.Y))
        return max(dx, dy) <= SPELL_RANGE

def check_line_of_sight(mobile):
    """Check if player has line of sight to the mobile."""
    if not CHECK_LINE_OF_SIGHT:
        return True
    try:
        # Use Statics.CheckLineOfSight for visibility check
        px, py, pz = Player.Position.X, Player.Position.Y, Player.Position.Z
        mx, my, mz = mobile.Position.X, mobile.Position.Y, mobile.Position.Z
        has_los = Statics.CheckLineOfSight(px, py, pz, mx, my, mz, Player.Map)
        if not has_los:
            debug_message(f"No line of sight to enemy at ({mx}, {my}, {mz})", 33)
        return has_los
    except Exception as e:
        debug_message(f"LOS check error: {e}", 33)
        return True  # Assume visible if check fails

def execute_target(enemy):
    """Execute target on enemy using configured mode.
    
    Args:
        enemy: Mobile object to target
    
    Returns:
        True if targeting executed, False otherwise
    """
    try:
        if TARGET_MODE == 'mobile':
            # Target the mobile directly (like SPELL_attack_nearest.py)
            debug_message(f"Targeting mobile directly (serial: {enemy.Serial})...", 68)
            Target.TargetExecute(enemy)
            Misc.Pause(TARGET_POST_EXECUTE_DELAY_MS)
            return True
        else:
            # Target ground at enemy position with Z offset testing
            ex = int(enemy.Position.X)
            ey = int(enemy.Position.Y)
            ez = int(enemy.Position.Z)
            offsets = Z_OFFSETS_TO_TRY if TEST_Z_OFFSETS else [0]
            
            for z_offset in offsets:
                target_z = ez + z_offset
                try:
                    debug_message(f"Targeting ground at ({ex}, {ey}, {target_z}) [Z offset: {z_offset}]...", 68)
                    Target.TargetExecute(ex, ey, target_z)
                    Misc.Pause(TARGET_POST_EXECUTE_DELAY_MS)
                    # For ground targeting, try next offset if this one fails
                    Misc.Pause(100)
                    if not Target.HasTarget():
                        debug_message(f"Ground target executed with Z offset {z_offset}", 68)
                        return True
                except Exception as e:
                    debug_message(f"Target execute error with Z offset {z_offset}: {e}", 33)
                    continue
            
            debug_message("All Z offset attempts failed", 33)
            return False
    except Exception as e:
        debug_message(f"Target execution error: {e}", 33)
        return False

#//===============  Core routine =======================

def handle_leftover_target(enemy):
    if not Target.HasTarget():
        return False
    debug_message("Leftover target detected. Moving into range to execute...", 67)
    start = now_ms()
    while Target.HasTarget() and (now_ms() - start) < MAX_APPROACH_TIME_MS:
        # Update enemy reference may move
        if enemy is None or not Mobiles.FindBySerial(enemy.Serial):
            debug_message("Enemy lost. Cancelling target.", 33)
            Target.Cancel()
            return False
        ex = int(enemy.Position.X)
        ey = int(enemy.Position.Y)
        if not in_spell_range(enemy):
            goto_location_with_wiggle(ex, ey, center=(ex, ey))
            Misc.Pause(50)
            continue
        # Check line of sight if enabled
        if CHECK_LINE_OF_SIGHT and not check_line_of_sight(enemy):
            debug_message("No line of sight to enemy, moving...", 33)
            goto_location_with_wiggle(ex, ey, center=(ex, ey))
            Misc.Pause(50)
            continue
        # Now in range - execute target
        if execute_target(enemy):
            return True
        # If targeting failed, try moving slightly and retry once
        debug_message("Target failed, adjusting position...", 33)
        goto_location_with_wiggle(ex - 1, ey - 1, center=(ex, ey))
        Misc.Pause(200)
        if execute_target(enemy):
            return True
    # Timed out - cancel to avoid stuck cursor
    if Target.HasTarget():
        Target.Cancel()
    return False

def cast_poison_field(enemy):
    # Requirements
    if not have_mana() or not have_reagents():
        return False
    if not check_spellbook():
        return False

    # If target is already up, try to resolve it first (move->execute)
    if handle_leftover_target(enemy):
        return True

    # Cast to bring up target cursor (even if currently out of range)
    debug_message(f"Casting {SPELL_NAME}...")
    Spells.CastMagery(SPELL_NAME)
    Target.WaitForTarget(5000, False)
    Misc.Pause(40)

    # If no target cursor, give up
    if not Target.HasTarget():
        debug_message("No target cursor after casting.", 33)
        return False

    # Approach and execute when in range
    start = now_ms()
    while Target.HasTarget() and (now_ms() - start) < MAX_APPROACH_TIME_MS:
        if enemy is None or not Mobiles.FindBySerial(enemy.Serial):
            debug_message("Enemy lost during approach. Cancelling target.", 33)
            Target.Cancel()
            return False
        ex = int(enemy.Position.X)
        ey = int(enemy.Position.Y)
        if not in_spell_range(enemy):
            goto_location_with_wiggle(ex, ey, center=(ex, ey))
            Misc.Pause(50)
            continue
        # Check line of sight if enabled
        if CHECK_LINE_OF_SIGHT and not check_line_of_sight(enemy):
            debug_message("No line of sight, repositioning...", 33)
            goto_location_with_wiggle(ex, ey, center=(ex, ey))
            Misc.Pause(50)
            continue
        # In range -> execute target
        debug_message(f"In range. Executing target (mode: {TARGET_MODE})...", 68)
        if execute_target(enemy):
            Misc.Pause(CAST_DELAY_MS)
            return True
        # If targeting failed, try adjusting position and retry once
        debug_message("Target failed, adjusting position for retry...", 33)
        goto_location_with_wiggle(ex - 1, ey, center=(ex, ey))
        Misc.Pause(200)
        if execute_target(enemy):
            Misc.Pause(CAST_DELAY_MS)
            return True
        # Give up after retry
        debug_message("Target execution failed after retry", 33)
        break

    # Timeout - cancel cursor
    debug_message("Timed out approaching target. Cancelling.", 33)
    if Target.HasTarget():
        Target.Cancel()
    return False

#//===============  Main =======================

def main():
    start = now_ms()

    # If a target cursor is already active, try to resolve it first
    enemy = find_enemy()
    if Target.HasTarget():
        if enemy:
            handled = handle_leftover_target(enemy)
            if handled:
                return
        else:
            Target.Cancel()
            debug_message("Cancelled stray target (no enemy).", 33)
            return

    # Find/validate target
    if not enemy:
        debug_message("No enemies found.", 33)
        return

    # Attempt cast-flow
    success = cast_poison_field(enemy)
    if not success:
        debug_message("Failed to cast/execute Poison Field.", 33)
        return

    # Soft guard against runaway
    elapsed = now_ms() - start
    if elapsed > MAX_TOTAL_RUNTIME_MS:
        debug_message("Run exceeded max runtime guard.", 33)

if __name__ == "__main__":
    main()
