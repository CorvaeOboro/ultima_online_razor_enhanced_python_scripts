"""
GATHER LUMBERJACK - A Razor Enhanced Python Script for Ultima Online

Continously lumberjack from the cursor position or self
- Handles axe equipping
- Drops all logs , focused on secondary resources
- currently self targeted harvesting

VERSION::20250621
"""
MAX_WEIGHT = 390
SELF_HARVEST = True  # Set to True for shards that support self-targeting for harvesting
HARVEST_DELAY = 2100

# List of valid axes for lumberjacking
AXE_TYPES = {
    'Hatchet': 0x0F43,
    'Battle Axe': 0x0F47,
    'Double Axe': 0x0F4B,
    'Executioner Axe': 0x0F45,
    'Large Battle Axe': 0x13FB,
    'Two Handed Axe': 0x1443,
    'War Axe': 0x13B0,
    'Gargoyle Axe': 0x48B2,
}

# List of log item IDs to process
logIDList = [
    ['Log', 0x1BDD, None],  # Regular Log
    # Add other log types here if necessary
]

def get_hatchet():
    """Get any valid lumberjacking tool currently in hand or equip one from the backpack."""
    # Check both hands for any valid axe
    for hand in ['LeftHand', 'RightHand']:
        item = Player.GetItemOnLayer(hand)
        if item and item.ItemID in AXE_TYPES.values():
            Misc.SendMessage(f"Using {next((name for name, id in AXE_TYPES.items() if id == item.ItemID), 'Unknown')} for lumberjacking", 67)
            return item

    # Unequip any currently equipped weapons
    for hand in ['LeftHand', 'RightHand']:
        item = Player.GetItemOnLayer(hand)
        if item:
            Misc.SendMessage(f"Unequipping {item.Name if item.Name else 'item'} from {hand}...", 67)
            Player.UnEquipItemByLayer(hand)
            Misc.Pause(600)

    # If not in hands, find any valid axe in backpack and equip
    for axe_id in AXE_TYPES.values():
        axe = Items.FindByID(axe_id, -1, Player.Backpack.Serial, 0, 0)
        if axe:
            axe_name = next((name for name, id in AXE_TYPES.items() if id == axe.ItemID), 'Unknown')
            Misc.SendMessage(f"Found {axe_name} in backpack, equipping...", 67)
            Player.EquipItem(axe)
            Misc.Pause(600)  # Increased pause to ensure unequip/equip completes
            # Check hands again after equipping
            for hand in ['LeftHand', 'RightHand']:
                item = Player.GetItemOnLayer(hand)
                if item and item.ItemID == axe.ItemID:
                    return item
                    
    Misc.SendMessage("No valid lumberjacking tool found!", 33)
    return None

def get_harvest_target():
    """Get the target for harvesting based on shard configuration"""
    if SELF_HARVEST:
        return Player.Serial
    else:
        return get_tile_in_front()

def get_tile_in_front():
    """Calculate the tile coordinates in front of the player based on direction."""
    direction = Player.Direction
    playerX = Player.Position.X
    playerY = Player.Position.Y
    playerZ = Player.Position.Z

    # Directional offsets
    offsets = {
        0: (0, -1),  # North
        1: (1, -1),  # NE
        2: (1, 0),   # East
        3: (1, 1),   # SE
        4: (0, 1),   # South
        5: (-1, 1),  # SW
        6: (-1, 0),  # West
        7: (-1, -1)  # NW
    }

    dx, dy = offsets.get(direction, (0, 0))
    tileX = playerX + dx
    tileY = playerY + dy
    tileZ = playerZ
    return tileX, tileY, tileZ

def move_logs(logIDList):
    """Move logs from the backpack to the tile in front of the player."""
    tileX, tileY, tileZ = get_tile_in_front()
    playerBackpack = Player.Backpack.Serial

    # For each item ID in the list
    for log in logIDList:
        itemName, itemID, itemColor = log
        if itemColor is None:
            itemColor = -1  # Use -1 to ignore color
        while True:
            foundItem = Items.FindByID(itemID, itemColor, playerBackpack, 0, 0)
            if foundItem:
                Items.MoveOnGround(foundItem, 0, tileX, tileY, tileZ)
                Misc.Pause(500)
            else:
                Misc.Pause(100)
                break

def chop_tree(target):
    """Main tree chopping function"""
    # Get or equip a hatchet
    hatchet = get_hatchet()
    if not hatchet:
        return

    while True:
        # Weight check
        if Player.Weight >= MAX_WEIGHT:
            Misc.SendMessage("Too heavy to continue!", 33)
            return

        # Use the hatchet
        Items.UseItem(hatchet)
        Misc.Pause(500)

        # Target based on harvesting mode
        if SELF_HARVEST:
            Target.TargetExecute(target)  # target is Player.Serial
        else:
            # For manual targeting, use coordinates
            Target.TargetExecute(target.X, target.Y, target.Z)

        # Wait for chopping harvest delay specific to shard
        Misc.Pause(HARVEST_DELAY)

def main():
    """Main execution function."""
    if SELF_HARVEST:
        target = Player.Serial
    else:
        target = Target.PromptGroundTarget('Select tree to chop')
        if target.X == 0 and target.Y == 0:  # Invalid target
            Misc.SendMessage("Invalid target location!", 33)
            return
    
    chop_tree(target)

if __name__ == '__main__':
    main()
