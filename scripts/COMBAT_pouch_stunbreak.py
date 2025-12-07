"""
 COMBAT POUCH STUN BREAK - A Razor Enhanced Python Script for Ultima Online
 
 Activate to trigger a "stun break" by opening a trapped pouch in inventory to break paralyze
 Supports multiple trapped pouch hues and context-aware pouch trapping
 refreshes untrapped pouches when safe to do so

say "[pouch"

HOTKEY:: D
VERSION::20250923
"""

DEBUG_MODE = False
DO_PARALYZE_CHECK = True
ENABLE_POUCH_REFRESH = True

# Pouch settings
POUCH_TYPE = 0x0E79  # pouch item id
TRAPPED_POUCH_HUES = [0x0021, 0x0026]  # red hue variants for trapped pouches
DANGER_HEALTH_THRESHOLD = 60  # Below this health % is considered dangerous

# Bank locations (include coords used by SPELL_recall_bank.py)
BANK_LOCATIONS = [
    {"x": 1416, "y": 1687, "range": 20},  # Britain Bank (from SPELL_recall_bank.py)
    {"x": 1438, "y": 1695, "range": 30},  # Britain Bank (alternate area)
]

def debug_message(msg, color=67, always=False):
    """Send debug message with optional color and force display"""
    if DEBUG_MODE or always:
        Misc.SendMessage(f"[Pouch] {msg}", color)

def is_paralyzed():
    """Check if player is paralyzed"""
    if not DO_PARALYZE_CHECK:
        return False
    try:
        return Player.Paralyzed
    except AttributeError:
        debug_message("Could not check Player.Paralyzed", 33)
        return False

def is_in_combat():
    """Check if player is in combat"""
    try:
        return Player.InCombat
    except AttributeError:
        debug_message("Could not check Player.InCombat", 33)
        return False

def is_in_danger():
    """Check if player is in danger (low health, combat, or paralyzed)"""
    health_percent = (Player.Hits / Player.HitsMax) * 100 if Player.HitsMax > 0 else 100
    low_health = health_percent < DANGER_HEALTH_THRESHOLD
    in_combat = is_in_combat()
    paralyzed = is_paralyzed()
    
    if low_health:
        debug_message(f"In danger: Low health ({health_percent:.1f}%)", 33)
    if in_combat:
        debug_message("In danger: In combat", 33)
    if paralyzed:
        debug_message("In danger: Paralyzed", 33)
    
    return low_health or in_combat or paralyzed

def is_full_health():
    """Return True if Hits are at maximum and max > 0"""
    try:
        return Player.HitsMax > 0 and Player.Hits == Player.HitsMax
    except AttributeError:
        debug_message("Could not check Player.Hits/HitsMax", 33)
        return False

def is_at_bank():
    """Check if player is at a bank location"""
    player_x = Player.Position.X
    player_y = Player.Position.Y
    
    for bank in BANK_LOCATIONS:
        distance = ((player_x - bank["x"]) ** 2 + (player_y - bank["y"]) ** 2) ** 0.5
        if distance <= bank["range"]:
            debug_message(f"At bank location: {bank['x']}, {bank['y']}", 68)
            return True
    return False

def get_trapped_pouches():
    """Get all trapped pouches (with any of the trapped hues)"""
    trapped_pouches = []
    for item in Player.Backpack.Contains:
        if item.ItemID == POUCH_TYPE and item.Hue in TRAPPED_POUCH_HUES:
            trapped_pouches.append(item)
    return trapped_pouches

def get_untrapped_pouches():
    """Get all untrapped pouches (not having trapped hues)"""
    untrapped_pouches = []
    for item in Player.Backpack.Contains:
        if item.ItemID == POUCH_TYPE and item.Hue not in TRAPPED_POUCH_HUES:
            untrapped_pouches.append(item)
    return untrapped_pouches

def cast_magic_trap_on_pouch(pouch):
    """Cast Magic Trap on a specific pouch"""
    debug_message(f"Casting Magic Trap on pouch (Serial: {pouch.Serial})", 68)
    Spells.CastMagery('Magic Trap')
    Target.WaitForTarget(3000, False)
    
    if Target.HasTarget:
        Target.TargetExecute(pouch)
        Misc.Pause(2500)  # Wait for spell to complete
        return True
    else:
        debug_message('No target cursor for Magic Trap!', 33)
        return False

def refresh_untrapped_pouches():
    """Refresh untrapped pouches by casting Magic Trap on them"""
    # Strict safety gate: only proceed if at bank OR (full health AND not in combat/paralyzed)
    if not (is_at_bank() or (is_full_health() and not is_in_combat() and not is_paralyzed())):
        debug_message("Skipping pouch refresh - not at bank and not fully safe", 33)
        return False
    
    untrapped = get_untrapped_pouches()
    if not untrapped:
        debug_message("No untrapped pouches to refresh", 68)
        return True
    
    debug_message(f"Refreshing {len(untrapped)} untrapped pouches...", 68)
    success_count = 0
    
    for pouch in untrapped:
        # Re-affirm safety before each cast
        if not (is_at_bank() or (is_full_health() and not is_in_combat() and not is_paralyzed())):
            debug_message("Stopping pouch refresh - safety condition no longer met", 33)
            break
            
        if cast_magic_trap_on_pouch(pouch):
            success_count += 1
        else:
            debug_message("Failed to cast Magic Trap", 33)
            break
    
    debug_message(f"Successfully refreshed {success_count} out of {len(untrapped)} pouches", 68)
    return success_count > 0

def use_trapped_pouch():
    """Use a trapped pouch to break stun/paralyze"""
    trapped_pouches = get_trapped_pouches()
    
    if not trapped_pouches:
        debug_message('NO TRAPPED POUCHES FOUND', 47, always=True)
        return False
    
    # Use the first available trapped pouch
    pouch = trapped_pouches[0]
    debug_message('STUN BREAK - Using trapped pouch', 37, always=True)
    Items.UseItem(pouch)
    return True

def should_refresh_pouches():
    """Determine if we should refresh untrapped pouches based on context"""
    if not ENABLE_POUCH_REFRESH:
        return False

    untrapped = get_untrapped_pouches()
    if not untrapped:
        return False

    # Allow at bank regardless of combat state
    if is_at_bank():
        debug_message("Context allows pouch refresh: At bank location", 68)
        return True

    # Otherwise only allow when fully safe: full HP, not in combat, not paralyzed
    if is_full_health() and not is_in_combat() and not is_paralyzed():
        debug_message("Context allows pouch refresh: Full health and safe", 68)
        return True

    return False

def main():
    """Main function - orchestrates the pouch stun break functionality"""
    debug_message("=== Pouch Stun Break Script Started ===", 68, always=True)
    
    
    # Always attempt to use a trapped pouch (main functionality)
    if is_paralyzed() or True:  # Always try to use pouch when script is run since we dont always have access to "paralyzed" variable
        use_success = use_trapped_pouch()
        if not use_success:
            debug_message("No trapped pouches available for stun break", 47, always=True)


    if should_refresh_pouches():
        refresh_success = refresh_untrapped_pouches()
        if refresh_success:
            debug_message("Pouch refresh completed successfully", 68)
        else:
            debug_message("Pouch refresh failed or interrupted", 33)
    debug_message("=== Pouch Stun Break Script Completed ===", 68, always=True)

if __name__ == "__main__":
    main()