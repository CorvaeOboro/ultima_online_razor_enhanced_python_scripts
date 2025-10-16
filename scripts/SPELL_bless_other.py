"""
SPELL bless other - A Razor Enhanced Python script for Ultima Online

cast Bless on the nearest blue player

HOTKEY:: H
VERSION::20251015
"""
import System
import System.Collections.Generic

DEBUG_MODE = False
BLESS_MANA_COST = 14
MAX_RANGE = 12  # Maximum range to search for players

def debug_message(message, color=67):
    """Send debug message to game client"""
    if not DEBUG_MODE:
        return
    try:
        if message:
            Misc.SendMessage(f"[BLESS] {message}", color)
        else:
            Misc.SendMessage("", color)
    except Exception:
        if message:
            print(f"[BLESS] {message}")
        else:
            print("")

def find_nearest_blue_player():
    """Find the nearest non-criminal player"""
    mobile_filter = Mobiles.Filter()
    mobile_filter.Enabled = True
    mobile_filter.RangeMax = MAX_RANGE
    mobile_filter.IsHuman = True
    mobile_filter.IsGhost = False
    # Create .NET List[Byte] for notorieties: 1=Innocent (blue), 2=Friend (green)
    notoriety_list = System.Collections.Generic.List[System.Byte]()
    notoriety_list.Add(1)
    notoriety_list.Add(2)
    mobile_filter.Notorieties = notoriety_list
    mobile_filter.CheckIgnoreObject = True
    
    players = Mobiles.ApplyFilter(mobile_filter)
    debug_message(f"Found {len(players)} players within {MAX_RANGE} tiles", 67)
    
    nearest = None
    min_dist = MAX_RANGE + 1
    
    for player in players:
        if player.Serial == Player.Serial:  # Skip self
            continue
            
        dist = Player.DistanceTo(player)
        if dist < min_dist:
            min_dist = dist
            nearest = player
    
    return nearest

def cast_bless(target):
    """Cast Bless on the target"""
    if Player.Mana < BLESS_MANA_COST:
        debug_message("Not enough mana", 33)
        return False
    
    debug_message(f"Casting Bless spell...", 67)
    Spells.Cast("Bless")
    Target.WaitForTarget(2000, True)
    Target.TargetExecute(target.Serial)
    Misc.Pause(500)  # Wait for spell to complete
    return True

# ============================================================
# MAIN 
# ============================================================

target = find_nearest_blue_player()

if target:
    # Check if target already has Bless buff
    # Note: Player.BuffsExist() only works on Player, not other mobiles
    # For other mobiles, would need to check via Mobiles.GetPropStringList()
    
    distance = Player.DistanceTo(target)
    debug_message(f"Target found: {target.Name} ({distance} tiles away)", 68)
    
    if cast_bless(target):
        debug_message(f"Bless cast successfully on {target.Name}", 68)
    else:
        debug_message(f"Failed to cast Bless", 33)
else:
    debug_message(f"No friendly players found within {MAX_RANGE} tiles", 53)


