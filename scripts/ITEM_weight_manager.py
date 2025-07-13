"""
Item Weight Manager Script - a Razor Enhanced PythonScript for Ultima Online

Manages items weight in your backpack by:
1. Dropping all disposable items:
   - Magic scrolls (all circles)
   - Pagan reagents
   - Empty bottles , Poison and Lesser potions
2. Maintaining minimum counts for:
   - Regular reagents (200 each)
   - Heal and Cure potions (10 each)
   - Utility potions (5 each)

VERSION::20250621
"""

import sys
from System.Collections.Generic import List
import time

# Global debug mode switch
DEBUG_MODE = False  # Set to True to enable debug/info messages

# Configuration
MAX_REAGENT_COUNT = 200  # Maximum number of reagents to keep

# Items to always drop (no count management)
DISPOSABLE_ITEMS = [
    # Circle 1 Scrolls
    {"name": "1_Clumsy", "id": 0x1F2E, "hue": None},
    {"name": "1_CreateFood", "id": 0x1F2F, "hue": None},
    {"name": "1_Feeblemind", "id": 0x1F30, "hue": None},
    {"name": "1_Heal", "id": 0x1F31, "hue": None},
    {"name": "1_MagicArrow", "id": 0x1F32, "hue": None},
    {"name": "1_NightSight", "id": 0x1F33, "hue": None},
    {"name": "1_ReactiveArmor", "id": 0x1F2D, "hue": None},
    {"name": "1_Weaken", "id": 0x1F34, "hue": None},
    
    # Circle 2 Scrolls
    {"name": "2_Agility", "id": 0x1F35, "hue": None},
    {"name": "2_Cunning", "id": 0x1F36, "hue": None},
    {"name": "2_Cure", "id": 0x1F37, "hue": None},
    {"name": "2_Harm", "id": 0x1F38, "hue": None},
    {"name": "2_MagicTrap", "id": 0x1F39, "hue": None},
    {"name": "2_MagicUnTrap", "id": 0x1F3A, "hue": None},
    {"name": "2_Protection", "id": 0x1F3B, "hue": None},
    {"name": "2_Strength", "id": 0x1F3C, "hue": None},
    
    # Circle 3 Scrolls
    {"name": "3_Bless", "id": 0x1F3D, "hue": None},
    {"name": "3_Fireball", "id": 0x1F3E, "hue": None},
    {"name": "3_MagicLock", "id": 0x1F3F, "hue": None},
    {"name": "3_Poison", "id": 0x1F40, "hue": None},
    {"name": "3_Telekinisis", "id": 0x1F41, "hue": None},
    {"name": "3_Teleport", "id": 0x1F42, "hue": None},
    {"name": "3_Unlock", "id": 0x1F43, "hue": None},
    {"name": "3_WallOfStone", "id": 0x1F44, "hue": None},
    
    # Circle 4 Scrolls
    {"name": "4_ArchCure", "id": 0x1F45, "hue": None},
    {"name": "4_ArchProtection", "id": 0x1F46, "hue": None},
    {"name": "4_Curse", "id": 0x1F47, "hue": None},
    {"name": "4_FireField", "id": 0x1F48, "hue": None},
    {"name": "4_GreaterHeal", "id": 0x1F49, "hue": None},
    {"name": "4_Lightning", "id": 0x1F4A, "hue": None},
    {"name": "4_ManaDrain", "id": 0x1F4B, "hue": None},
    {"name": "4_Recall", "id": 0x1F4C, "hue": None},
    
    # Circle 5 Scrolls
    {"name": "5_BladeSpirits", "id": 0x1F4D, "hue": None},
    {"name": "5_DispelField", "id": 0x1F4E, "hue": None},
    {"name": "5_Incognito", "id": 0x1F4F, "hue": None},
    {"name": "5_MagicReflect", "id": 0x1F50, "hue": None},
    {"name": "5_MindBlast", "id": 0x1F51, "hue": None},
    {"name": "5_Paralyze", "id": 0x1F52, "hue": None},
    {"name": "5_PoisonField", "id": 0x1F53, "hue": None},
    {"name": "5_SummonCreature", "id": 0x1F54, "hue": None},
    
    # Circle 6 Scrolls
    {"name": "6_Dispel", "id": 0x1F55, "hue": None},
    {"name": "6_EnergyBolt", "id": 0x1F56, "hue": None},
    {"name": "6_Explosion", "id": 0x1F57, "hue": None},
    {"name": "6_Invisibility", "id": 0x1F58, "hue": None},
    {"name": "6_Mark", "id": 0x1F59, "hue": None},
    {"name": "6_MassCurse", "id": 0x1F5A, "hue": None},
    {"name": "6_ParalyzeField", "id": 0x1F5B, "hue": None},
    {"name": "6_Reveal", "id": 0x1F5C, "hue": None},
    
    # Circle 7 Scrolls
    {"name": "7_ChainLightning", "id": 0x1F5D, "hue": None},
    {"name": "7_EnergyField", "id": 0x1F5E, "hue": None},
    {"name": "7_Flamestrike", "id": 0x1F5F, "hue": None},
    {"name": "7_GateTravel", "id": 0x1F60, "hue": None},
    {"name": "7_ManaVampire", "id": 0x1F61, "hue": None},
    {"name": "7_MassDispel", "id": 0x1F62, "hue": None},
    {"name": "7_MeteorSwarm", "id": 0x1F63, "hue": None},
    {"name": "7_Polymorph", "id": 0x1F64, "hue": None},
    
    # Circle 8 Scrolls
    {"name": "8_Earthquake", "id": 0x1F65, "hue": None},
    {"name": "8_EnergyVortex", "id": 0x1F66, "hue": None},
    {"name": "8_Resurrection", "id": 0x1F67, "hue": None},
    {"name": "8_SummonAirElemental", "id": 0x1F68, "hue": None},
    {"name": "8_SummonDaemon", "id": 0x1F69, "hue": None},
    {"name": "8_SummonEarthElemental", "id": 0x1F6A, "hue": None},
    {"name": "8_SummonFireElemental", "id": 0x1F6B, "hue": None},
    {"name": "8_SummonWaterElemental", "id": 0x1F6C, "hue": None},
    
    # Pagan Reagents
    {"name": "Pig Iron", "id": 0x0F8A, "hue": None},
    {"name": "Grave Dust", "id": 0x0F8F, "hue": None},
    {"name": "Daemon Blood", "id": 0x0F7D, "hue": None},
    {"name": "Nox Crystal", "id": 0x0F8E, "hue": None},
    {"name": "Bat Wing", "id": 0x0F78, "hue": None},
    {"name": "Bone", "id": 0x0F7E, "hue": None},
    {"name": "Daemon Bone", "id": 0x0F80, "hue": None},
    {"name": "Dragons Blood", "id": 0x0F82, "hue": None},
    {"name": "Executioners Cap", "id": 0x0F83, "hue": None},
    {"name": "Fertile Dirt", "id": 0x0F81, "hue": None},
    
    # Resources
    {"name": "Iron Ore", "id": 0x19B9, "hue": None},
    {"name": "Iron Ore B", "id": 0x19B7, "hue": None},
    {"name": "Cut Leather", "id": 0x1081, "hue": None},
    {"name": "Pile of Hides", "id": 0x1079, "hue": None},
    {"name": "Raw Ribs", "id": 0x09F1, "hue": None},
    {"name": "Fish Steaks", "id": 0x097A, "hue": None},

    # Arrows
    {"name": "CrossbowBolts", "id": 0x1BFB, "hue": None},
    
    # Clothing
    {"name": "Cloth", "id": 0x1766, "hue": None},
    {"name": "Folded Cloth", "id": 0x175D, "hue": None},
    {"name": "Plain Dress", "id": 0x1F01, "hue": None},
    {"name": "Fancy Dress", "id": 0x1F00, "hue": None},
    {"name": "Cloak", "id": 0x1515, "hue": None},
    {"name": "Robe", "id": 0x1F03, "hue": None},
    {"name": "Shirt", "id": 0x1517, "hue": None},
    {"name": "Body Sash", "id": 0x1541, "hue": None},
    
    # Shoes
    {"name": "Sandals", "id": 0x170D, "hue": None},
    {"name": "Shoes", "id": 0x170F, "hue": None},
    {"name": "Boots", "id": 0x170B, "hue": None},
    {"name": "Thigh Boots", "id": 0x1711, "hue": None},
    
    # Empty Bottles
    {"name": "Empty Bottle", "id": 0x0F0E, "hue": None},
    {"name": "Poison Potion", "id": 0x0F0A, "hue": None},
    
    # Boards
    {"name": "Board", "id": 0x1BD7, "hue": None},
    {"name": "Oak Board", "id": 0x1BDD, "hue": None},
    {"name": "Ash Board", "id": 0x1BDE, "hue": None},
    {"name": "Yew Board", "id": 0x1BDF, "hue": None},
    {"name": "Heartwood Board", "id": 0x1BE0, "hue": None},
    {"name": "Bloodwood Board", "id": 0x1BE1, "hue": None},
    {"name": "Frostwood Board", "id": 0x1BE2, "hue": None},
    
    # Leathers
    {"name": "Leather", "id": 0x1078, "hue": None},
    {"name": "Spined Leather", "id": 0x1079, "hue": None},
    {"name": "Horned Leather", "id": 0x107A, "hue": None},
    {"name": "Barbed Leather", "id": 0x107B, "hue": None},
    {"name": "Regular Hide", "id": 0x107C, "hue": None},
    {"name": "Spined Hide", "id": 0x107D, "hue": None},
    {"name": "Horned Hide", "id": 0x107E, "hue": None},
    {"name": "Barbed Hide", "id": 0x107F, "hue": None},
    
    # Ingots
    {"name": "Iron Ingot", "id": 0x1BF2, "hue": None},
    {"name": "Dull Copper Ingot", "id": 0x1BEF, "hue": None},
    {"name": "Shadow Iron Ingot", "id": 0x1BEF, "hue": None},
    {"name": "Copper Ingot", "id": 0x1BEF, "hue": None},
    {"name": "Bronze Ingot", "id": 0x1BEF, "hue": None},
    {"name": "Gold Ingot", "id": 0x1BEF, "hue": None},
    {"name": "Agapite Ingot", "id": 0x1BEF, "hue": None},
    {"name": "Verite Ingot", "id": 0x1BEF, "hue": None},
    {"name": "Valorite Ingot", "id": 0x1BEF, "hue": None},
]

# Items to manage count (keep minimum amount)
MANAGED_ITEMS = [
    # Regular Reagents
    {"name": "Black Pearl", "id": 0x0F7A, "min_count": MAX_REAGENT_COUNT},
    {"name": "Blood Moss", "id": 0x0F7B, "min_count": MAX_REAGENT_COUNT},
    {"name": "Garlic", "id": 0x0F84, "min_count": MAX_REAGENT_COUNT},
    {"name": "Ginseng", "id": 0x0F85, "min_count": MAX_REAGENT_COUNT},
    {"name": "Mandrake Root", "id": 0x0F86, "min_count": MAX_REAGENT_COUNT},
    {"name": "Nightshade", "id": 0x0F88, "min_count": MAX_REAGENT_COUNT},
    {"name": "Spider's Silk", "id": 0x0F8D, "min_count": MAX_REAGENT_COUNT},
    {"name": "Sulfurous Ash", "id": 0x0F8C, "min_count": MAX_REAGENT_COUNT},
    
    # Potions
    {"name": "Heal Potion", "id": 0x0F0C, "min_count": 10},
    {"name": "Cure Potion", "id": 0x0F07, "min_count": 10},
    {"name": "Total Refresh Potion", "id": 0x0F0B, "min_count": 5},
    {"name": "Strength Potion", "id": 0x0F09, "min_count": 5},
]

def debug_message(message, color=67):
    """Send a message if DEBUG_MODE is enabled"""
    if DEBUG_MODE:
        Misc.SendMessage(f"[WeightMgr] {message}", color)

def get_nearby_tiles():
    """Get a list of nearby tile offsets in a spiral pattern."""
    # Spiral pattern offsets from closest to furthest
    offsets = [
        (0, 0), (0, 1), (1, 0), (0, -1), (-1, 0),  # Adjacent
        (1, 1), (1, -1), (-1, -1), (-1, 1),  # Diagonals
        (0, 2), (2, 0), (0, -2), (-2, 0),  # Two tiles out
    ]
    return offsets

def get_player_position():
    """Cache and return the player's current position and map."""
    return {
        'x': Player.Position.X,
        'y': Player.Position.Y,
        'z': Player.Position.Z,
        'map': Player.Map
    }

def find_ground_tile(x_offset, y_offset, player_pos):
    """Find absolute world coordinates for a valid ground tile."""
    # Calculate absolute world position
    world_x = player_pos['x'] + x_offset
    world_y = player_pos['y'] + y_offset
    
    # Get the ground tile Z coordinate at this position
    tiles = Statics.GetStaticsTileInfo(world_x, world_y, player_pos['map'])
    if tiles and len(tiles) > 0:
        # Use the Z of the highest walkable tile
        walkable_tiles = [t for t in tiles]  
        if walkable_tiles:
            world_z = max(t.StaticZ for t in walkable_tiles)
        else:
            world_z = player_pos['z']
    else:
        world_z = player_pos['z']
    
    return world_x, world_y, world_z

def try_drop_items(item, amount_to_drop):
    """Attempt to drop items on nearby tiles, returns amount successfully dropped."""
    tiles = get_nearby_tiles()
    amount_dropped = 0
    
    # Cache player position once
    player_pos = get_player_position()
    
    # Try each position
    for x_offset, y_offset in tiles:
        if amount_dropped >= amount_to_drop:
            break
            
        # Find valid ground tile
        x, y, z = find_ground_tile(x_offset, y_offset, player_pos)
        
        # Try to drop up to 20 items at a time
        drop_amount = min(200, amount_to_drop - amount_dropped)
        
        # Attempt the drop
        Items.MoveOnGround(item.Serial, drop_amount, x, y, z)
        Misc.Pause(500)  # Give server time to process
        
        # Count this as a successful drop and move on
        amount_dropped += drop_amount
        debug_message(f"Dropped {drop_amount} {item.Name} at ({x}, {y}, {z})", 67)
    
    return amount_dropped

def find_existing_items():
    """Pre-check all items in backpack and return a dict of item_id -> count."""
    existing_items = {}
    
    # Check disposable items
    for item_info in DISPOSABLE_ITEMS:
        # For items with a specific hue (color)
        if "hue" in item_info and item_info["hue"] is not None:
            items = Items.FindByID(item_info["id"], item_info["hue"], Player.Backpack.Serial)
            if items:
                if not isinstance(items, list):
                    items = [items]
                existing_items[f"{item_info['id']}_{item_info['hue']}"] = len(items)
        # For items without a specific hue
        else:
            count = Items.ContainerCount(Player.Backpack.Serial, item_info["id"], -1)
            if count > 0:
                existing_items[str(item_info["id"])] = count
    
    # Check managed items
    for item_info in MANAGED_ITEMS:
        count = Items.ContainerCount(Player.Backpack.Serial, item_info["id"], -1)
        if count > item_info.get("min_count", 0):
            existing_items[str(item_info["id"])] = count
    
    return existing_items

def manage_all_items():
    """Main function to manage all item counts."""
    debug_message("Starting item count management...", 67)
    
    # First do a bulk check of all items
    existing_items = find_existing_items()
    if not existing_items:
        debug_message("No items to manage!", 67)
        return
    
    # Handle disposable items that exist
    for item_info in DISPOSABLE_ITEMS:
        # Create the key based on whether the item has a hue
        item_key = f"{item_info['id']}_{item_info.get('hue', '')}" if "hue" in item_info and item_info["hue"] is not None else str(item_info["id"])
        
        if item_key in existing_items:
            drop_all_items(item_info)
            Misc.Pause(100)
    
    # Handle managed items that exceed minimum
    for item_info in MANAGED_ITEMS:
        if str(item_info["id"]) in existing_items:
            manage_item_count(item_info)
            Misc.Pause(100)
    
    debug_message("Item count management complete!", 67)

def drop_all_items(item_info):
    """Drop all instances of an item."""
    # Find items with specific hue if specified
    if "hue" in item_info and item_info["hue"] is not None:
        items = Items.FindByID(item_info["id"], item_info["hue"], Player.Backpack.Serial)
    else:
        items = Items.FindByID(item_info["id"], -1, Player.Backpack.Serial)
    
    if not items:
        return
    
    # Convert single item to list
    if not isinstance(items, list):
        items = [items]
    
    # Count items with specific hue if specified
    if "hue" in item_info and item_info["hue"] is not None:
        count = len(items)
    else:
        count = Items.ContainerCount(Player.Backpack.Serial, item_info["id"], -1)
    
    debug_message(f"Dropping {count} {item_info['name']}", 67)
    try_drop_items(items[0], count)

def manage_item_count(item_info):
    """Manage count for a specific item."""
    # For managed items, we don't need to check hue
    items = Items.FindByID(item_info["id"], -1, Player.Backpack.Serial)
    if not items:
        return
    
    # Convert single item to list
    if not isinstance(items, list):
        items = [items]
    
    total_count = Items.ContainerCount(Player.Backpack.Serial, item_info["id"], -1)
    amount_to_drop = total_count - item_info["min_count"]
    
    if amount_to_drop > 0:
        debug_message(f"Need to drop {amount_to_drop} {item_info['name']}", 67)
        amount_dropped = try_drop_items(items[0], amount_to_drop)
        
        # If we couldn't drop all items, wait and try again
        if amount_dropped < amount_to_drop:
            Misc.Pause(500)
            new_count = Items.ContainerCount(Player.Backpack.Serial, item_info["id"], -1)
            remaining_to_drop = new_count - item_info["min_count"]
            if remaining_to_drop > 0:
                try_drop_items(items[0], remaining_to_drop)

# Run the manager
if __name__ == "__main__":
    manage_all_items()
