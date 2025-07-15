"""
SPELL bless other - A Razor Enhanced Python script for Ultima Online
cast Bless on the nearest blue player

HOTKEY:: H
VERSION::20250713
"""

BLESS_MANA_COST = 14
MAX_RANGE = 12  # Maximum range to search for players

def find_nearest_blue_player():
    """Find the nearest non-criminal player"""
    filter = Mobiles.Filter()
    filter.Enabled = True
    filter.RangeMax = MAX_RANGE
    filter.IsHuman = True
    filter.IsGhost = False
    filter.Friend = True  # Only target blue players
    
    players = Mobiles.ApplyFilter(filter)
    nearest = None
    min_dist = MAX_RANGE
    
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
        Misc.SendMessage("Not enough mana")
        return False
    
    Spells.Cast("Bless")
    Target.WaitForTarget(2000, True)
    Target.TargetExecute(target.Serial)
    return True

# ============================================================
target = find_nearest_blue_player()
if target:

    # Check if target already has Bless buff
    #if target.BuffsExist('Bless'):
    #    Misc.Pause(1000)
    #    continue
    
    Misc.SendMessage(f"Casting Bless on {target.Name}")
    cast_bless(target)


