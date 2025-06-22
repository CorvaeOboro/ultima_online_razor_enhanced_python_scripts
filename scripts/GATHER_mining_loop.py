"""
GATHER MINING - A Razor Enhanced Python Script for Ultima Online

Continously mine from the cursor position 
- Handles pickaxe equipping
- Drops all ore to the ground for now

VERSION::20250621
"""

import sys
import random  # Import random for randomizing positions

# Constants
TOOL_ID = 0x0E86  # Pickaxe item ID

# List of ore item IDs and colors to process
oresList = [
    ['Iron Ore', 0x19B9, None],
    ['Dull Copper Ore', 0x19BA, None],
    ['Shadow Iron Ore', 0x19B8, None],
    ['Copper Ore', 0x19B7, None],
    ['Bronze Ore', 0x19B6, None],
    ['Gold Ore', 0x19B5, None],
    ['Agapite Ore', 0x19B4, None],
    ['Verite Ore', 0x19B3, None],
    ['Valorite Ore', 0x19B2, None],
    # Add other ore types here if necessary
]

def get_pickaxe():
    """Get the pickaxe currently in hand or equip one from the backpack."""
    # Check both hands for the pickaxe
    for hand in ['LeftHand', 'RightHand']:
        item = Player.GetItemOnLayer(hand)
        if item and item.ItemID == TOOL_ID:
            return item

    # If not in hands, find in backpack and equip
    pickaxe = Items.FindByID(TOOL_ID, -1, Player.Backpack.Serial, 0, 0)
    if pickaxe:
        Player.EquipItem(pickaxe)
        Misc.Pause(500)
        # Check hands again after equipping
        for hand in ['LeftHand', 'RightHand']:
            item = Player.GetItemOnLayer(hand)
            if item and item.ItemID == TOOL_ID:
                return item
    return None

def get_random_nearby_tile(radius=2):
    """Get a random tile near the player within a specified radius."""
    playerX = Player.Position.X
    playerY = Player.Position.Y
    playerZ = Player.Position.Z

    # Generate random offsets within the radius
    dx = random.randint(-radius, radius)
    dy = random.randint(-radius, radius)
    # Ensure that (dx, dy) is not (0, 0)
    while dx == 0 and dy == 0:
        dx = random.randint(-radius, radius)
        dy = random.randint(-radius, radius)
    tileX = playerX + dx
    tileY = playerY + dy
    tileZ = playerZ
    return tileX, tileY, tileZ

def move_ores(oresList):
    """Move ores from the backpack to random tiles near the player."""
    playerBackpack = Player.Backpack.Serial

    # For each item ID in the list
    for ore in oresList:
        itemName, itemID, itemColor = ore
        if itemColor is None:
            itemColor = -1  # Use -1 to ignore color
        while True:
            foundItem = Items.FindByID(itemID, itemColor, playerBackpack, 0, 0)
            if foundItem:
                tileX, tileY, tileZ = get_random_nearby_tile()
                Items.MoveOnGround(foundItem, 0, tileX, tileY, tileZ)
                Misc.Pause(500)
            else:
                Misc.Pause(100)
                break

def mine_vein():
    """Main mining loop."""
    Journal.Clear()
    while not Journal.Search("There is no metal here to mine."):
        if Journal.Search("That is too far away."):
            Player.ChatSay(67, "Too Far Away")
            #sys.exit(99)
        if Player.Weight >= Player.MaxWeight:
            Player.ChatSay(67, "Overweight!")
            move_ores(oresList)
            #sys.exit(99)
        Journal.Clear()
        pickaxe = get_pickaxe()
        if pickaxe:
            Items.UseItem(pickaxe.Serial)
            Target.WaitForTarget(2500, False)
            #tiles = Statics.GetStaticsTileInfo(target.X, target.Y, Player.Map)
            Target.TargetExecuteRelative( Player.Serial, 1 )
            
        else:
            Player.ChatSay(67, "No Pickaxe")
            sys.exit(99)
    else:
        move_ores(oresList)
        #sys.exit(99)

def main():
    """Main execution function."""
    #target = Target.PromptGroundTarget('Select vein to mine')
    mine_vein()

if __name__ == '__main__':
    main()
