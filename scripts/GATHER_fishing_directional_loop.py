"""
GATHER FISH Directional Loop - A Razor Enhanced Python Script for Ultima Online

fishing in the direction the player is facing, 
then chop fish and drop boots/shoes as configured.

VERSION::20250621
"""

# --- GLOBAL SETTINGS ---
SHOW_DEBUG = True          # Toggle to show/hide debug messages
FISH_CHOP_ENABLED = True   # Set to False to skip fish chopping
SHOE_DROP_ENABLED = True   # Set to False to skip shoe dropping
# List of fishing pole item IDs (add more as needed)
FISHING_POLE_ID_LIST = [
    0x0DBF,  # Standard fishing pole
    0x0DC0,  # Another fishing pole variant
    0x4024B291,  # Example custom/rare pole (serial, not itemID)
    # Add more itemIDs or serials as needed
]
FISHING_ATTEMPTS = 5      # How many times to cast per cycle
FISHING_PAUSE = 500       # Pause between casts (ms)
WAIT_FOR_BITE = 7500      # Wait after last cast (ms)
OFFSET_MULTIPLIER = 8

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

# --- UTILITY: Tile in Front ---
def tileInFront():
    """
    Get the tile in front of the player based on facing direction.
    The Z is hardcoded to -5 for sea tiles (known info for most OSI/UOR shards).
    """
    direction = Player.Direction
    playerX = Player.Position.X
    playerY = Player.Position.Y
    playerZ = Player.Position.Z
    playerMap = Player.Map
    debug_message(f"Player position: X={playerX}, Y={playerY}, Z={playerZ}")
    debug_message(f"Player direction: {direction}")
    direction_mapping = {
        'North': (0, -1),
        'East': (1, 0),
        'South': (0, 1),
        'West': (-1, 0),
        'Up': (0, -1),
        'Right': (1, 0),
        'Down': (0, 1),
        'Left': (-1, 0)
    }
    dx, dy = direction_mapping.get(direction, (0, 0))
    tileX = playerX + (dx * OFFSET_MULTIPLIER)
    tileY = playerY + (dy * OFFSET_MULTIPLIER)
    tileZ = -5  # For the sea we know it is -5
    debug_message(f"Tile in front: X={tileX}, Y={tileY}, Z={tileZ}, Map={playerMap}")
    return tileX, tileY, tileZ, playerMap

# --- FISHING MODULE ---
def find_fishing_pole():
    """
    Find the first available fishing pole in the player's backpack from the ID list.
    Returns the item serial or None if not found.
    """
    backpack = Player.Backpack.Serial
    for pole_id in FISHING_POLE_ID_LIST:
        item = Items.FindByID(pole_id, -1, backpack)
        if item:
            debug_message(f"Found fishing pole: 0x{pole_id:X} (serial: 0x{item.Serial:X})")
            return item.Serial
    debug_message("No fishing pole found in backpack!", 33)
    return None

def do_fishing_cycle():
    """
    Perform a fishing cycle: cast rod several times at the tile in front.
    Uses multiple staticIDs for water tiles (covers most custom/OSI shards).
    """
    fishing_pole_serial = find_fishing_pole()
    if not fishing_pole_serial:
        debug_message("Fishing cycle aborted: No fishing pole available.", 33)
        return
    tileX, tileY, tileZ, mapID = tileInFront()
    debug_message(f"Starting fishing cycle at tile X={tileX}, Y={tileY}, Z={tileZ}")
    for i in range(FISHING_ATTEMPTS):
        debug_message(f"Casting fishing rod attempt {i+1}/{FISHING_ATTEMPTS}")
        Items.UseItem(fishing_pole_serial)
        Target.WaitForTarget(10000, False)
        if i == 0:
            Target.TargetExecute(tileX, tileY, tileZ)
            debug_message(f"Targeted tile with no staticID.")
        else:
            staticIDs = [6040, 6041, 6042, 6043]
            staticID = staticIDs[(i-1)%len(staticIDs)]
            Target.TargetExecute(tileX, tileY, tileZ, staticID)
            debug_message(f"Targeted tile with staticID={staticID}")
        Misc.Pause(FISHING_PAUSE)
    debug_message(f"Waiting {WAIT_FOR_BITE}ms for bites...")
    Misc.Pause(WAIT_FOR_BITE)

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
    Move all shoes/boots (and optionally pitchers) in backpack to the tile in front of the player.
    """
    tileX, tileY, tileZ, _ = tileInFront()
    playerBackpack = Player.Backpack.Serial
    debug_message(f"Dropping shoes/boots at tile X={tileX}, Y={tileY}, Z={tileZ}")
    for shoe in shoeIDList:
        itemName, itemID, itemColor = shoe
        if itemColor is None:
            itemColor = -1
        foundItem = Items.FindByID(itemID, itemColor, playerBackpack, 0, 0)
        if foundItem:
            debug_message(f"Dropping {itemName} (ID: {hex(itemID)}) at ({tileX},{tileY},{tileZ})")
            Items.MoveOnGround(foundItem, 0, tileX, tileY, tileZ)
            Misc.Pause(1600)
        else:
            debug_message(f"No {itemName} (ID: {hex(itemID)}) found in backpack.")
            Misc.Pause(100)

# --- MAIN LOOP ---
def main():
    debug_message("Starting GATHER FISH main all script.")
    while True:
        debug_message("--- New fishing cycle ---", 53)
        do_fishing_cycle()
        # Could check for 'no bites' or overweight here for more advanced logic
        if FISH_CHOP_ENABLED:
            debug_message("Chopping all fish in backpack after fishing cycle.", 68)
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
