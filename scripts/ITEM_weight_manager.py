"""
Item Weight Manager - a Razor Enhanced Python Script for Ultima Online

Drops items from your backpack to the ground 
adjust "Always drop" list , and "Maintain minimum" list

1. Dropping all disposable items:
    - Resources (leather, ingots, boards, cut cloth leather, etc.)
    - Magic scrolls (all circles)
    - Pagan reagents
    - Empty bottles , Poison and Lesser potions
2. Maintaining minimum counts for:
    - Magery reagents (200 each)
    - Heal and Cure potions (10 each)
    - Utility potions (5 each)

TODO:
dont drop invisibility potion , it shares id with other potion, check buy hue or name 
add dye and dyetub
add cloth , hide , scales , leather to resources 

HOTKEY:: X
VERSION::20250920
"""

# Global debug mode switch
DEBUG_MODE = False  # Set to True to enable debug/info messages

# Configuration
ENABLE_MANAGED_ITEMS = True  # Set to True to process MANAGED_ITEMS, False to ignore them completely
MAX_REAGENT_COUNT = 200  # Maximum number of reagents to keep

# Potion Quality Management
ENABLE_POTION_QUALITY_FILTER = True  # Set to True to only keep Greater quality potions
KEEP_POTION_QUALITIES = ["Greater"]  # List of potion qualities to keep (others will be dropped)

# Potion Special Hue Protection
# Any potion stack that has a special hue should never be dropped. This is used to protect
# special variants like Invisibility potions that share ItemID with other potions but use a custom hue.
# If TREAT_ANY_NONZERO_HUE_AS_SPECIAL is True, any non-zero Hue will be considered special and protected.
TREAT_ANY_NONZERO_HUE_AS_SPECIAL = True
# If you want to allow specific hues only, list them here (e.g., [0x0481, 0x081A]) and set the flag above to False
SPECIAL_POTION_HUES = []

# Disposable Item Category Toggles
DROP_MAGIC_SCROLLS = True  # Set to True to drop magic scrolls
DROP_PAGAN_REAGENTS = True  # Set to True to drop pagan reagents
DROP_RAW_RESOURCES = True  # Set to True to drop raw resources (ores, leather, etc.)
DROP_CRAFTED_RESOURCES = True  # Set to True to drop crafted resources (boards, ingots, etc.)
DROP_FOOD_ITEMS = True  # Set to True to drop food items
DROP_MISCELLANEOUS_ITEMS = True  # Set to True to drop miscellaneous items
DROP_LESSER_WANDS = True  # Set to True to drop wands except Greater Heal wand

# Item Exclusions - Items that should never be dropped even if they match disposable categories
EXCLUDED_ITEMS = [
    {"name": "Blue Fish Steak", "id": 0x097B, "hue": 0x0825},  # Special blue fish steaks to keep
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

# ============================================================================
# DISPOSABLE ITEM CATEGORIES
# ============================================================================

# Magic Scrolls - All spell scrolls organized by circle
MAGIC_SCROLLS = [
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
]

# Pagan Reagents - Necromancy and other special reagents
PAGAN_REAGENTS = [
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
]

# Raw Resources - Mining, lumberjacking, and other raw materials
RAW_RESOURCES = [
    # Ores
    {"name": "Iron Ore", "id": 0x19B9, "hue": None},
    {"name": "Iron Ore B", "id": 0x19B7, "hue": None},
    
    # Raw Materials
    {"name": "Cut Leather", "id": 0x1081, "hue": None},
    {"name": "Pile of Hides", "id": 0x1079, "hue": None},
    {"name": "Raw Ribs", "id": 0x09F1, "hue": None},
    {"name": "Fish Steaks", "id": 0x097A, "hue": None},
    
    # Ammunition
    {"name": "CrossbowBolts", "id": 0x1BFB, "hue": None},
]

# Crafted Resources - Processed materials like boards, ingots, leather
CRAFTED_RESOURCES = [
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

# Food Items - consumable food items 
FOOD_ITEMS = [
    # Fruits
    {"name": "Peach", "id": 0x09D2, "hue": None},
    {"name": "Apple", "id": 0x09D0, "hue": None},
    {"name": "Grapes", "id": 0x09D1, "hue": None},
    {"name": "Pear", "id": 0x0994, "hue": None},
    {"name": "Banana", "id": 0x171F, "hue": None},
    {"name": "Pumpkin", "id": 0x0C6A, "hue": None},
    {"name": "Onion", "id": 0x0C6D, "hue": None},
    {"name": "Carrot", "id": 0x0C78, "hue": None},
    {"name": "Squash", "id": 0x0C6C, "hue": None},

    # Vegetables
    {"name": "Lettuce", "id": 0x0C70, "hue": None},
    {"name": "Cabbage", "id": 0x0C7B, "hue": None},
 
    # Baked Goods
    {"name": "Muffins", "id": 0x09EB, "hue": None},
    {"name": "Bread Loaf", "id": 0x103B, "hue": None},
    
    # Meats
    {"name": "Cheese", "id": 0x097D, "hue": None},
    {"name": "Sausage", "id": 0x09C0, "hue": None},
    {"name": "Cooked Bird", "id": 0x09B7, "hue": None},
    {"name": "Cut of Ribs", "id": 0x09F2, "hue": None},
    {"name": "Ham", "id": 0x09C9, "hue": None},
    {"name": "Leg of Lamb", "id": 0x160A, "hue": None},
    {"name": "Chicken Leg", "id": 0x1608, "hue": None},
    {"name": "Fish Steak", "id": 0x097A, "hue": None},
    {"name": "Fish Steak 2", "id": 0x097B, "hue": None},
    {"name": "Bacon", "id": 0x097E, "hue": None},
]

# Potion Items - All potion types that may have quality variations
POTION_ITEMS = [
    {"name": "Heal Potion", "id": 0x0F0C, "hue": None},
    {"name": "Cure Potion", "id": 0x0F07, "hue": None},
    {"name": "Mana Potion", "id": 0x0F0D, "hue": None},
    {"name": "Total Refresh Potion", "id": 0x0F0B, "hue": None},
    {"name": "Strength Potion", "id": 0x0F09, "hue": None},
    {"name": "Agility Potion", "id": 0x0F08, "hue": None},
    {"name": "Magic Resist Potion", "id": 0x0F06, "hue": None},
    {"name": "Poison Potion", "id": 0x0F0A, "hue": None},
]

# Miscellaneous Items - Empty bottles, potions, and other items
MISCELLANEOUS_ITEMS = [
    {"name": "Empty Bottle", "id": 0x0F0E, "hue": None},
    {"name": "Water Pitcher", "id": 0x1F9D, "hue": None},
]

LESSER_WANDS = {
    0x0DF2: "WandA",
    0x0DF5: "WandD",
    0x5010: "WandFireball",
    0x0DF3: "WandHarm",
    0x0DF4: "WandHeal",
    0x5011: "WandLightning",
    0x500E: "WandManaDrain",
}

LESSER_WAND_ITEMS = [
    {"name": name, "id": item_id, "hue": None}
    for item_id, name in sorted(LESSER_WANDS.items())
]

# Items to always drop regardless of category toggles
ALWAYS_TRASH_ITEMS = [
    {"name": "5 ore", "id": 0x19B7, "hue": 0x0000},
    {"name": "cut of raw ribs", "id": 0x09F1, "hue": 0x0000},
    {"name": "fire horn", "id": 0x0FC7, "hue": 0x0466},
    {"name": "ore", "id": 0x19B7, "hue": 0x0000},
    {"name": "fork", "id": 0x09F5, "hue": 0x0000},
    {"name": "knife", "id": 0x09F6, "hue": 0x0000},
    {"name": "plate", "id": 0x09D7, "hue": 0x0000},
]

# Items to always drop (no count management) - Generated dynamically based on toggles
# This will be populated at runtime by get_enabled_disposable_items()
DISPOSABLE_ITEMS = []

def get_enabled_disposable_items():
    """Generate the disposable items list based on enabled categories."""
    enabled_items = []
    
    if DROP_MAGIC_SCROLLS:
        enabled_items.extend(MAGIC_SCROLLS)
        debug_message(f"Added {len(MAGIC_SCROLLS)} magic scrolls to disposable list", 67)
    
    if DROP_PAGAN_REAGENTS:
        enabled_items.extend(PAGAN_REAGENTS)
        debug_message(f"Added {len(PAGAN_REAGENTS)} pagan reagents to disposable list", 67)
    
    if DROP_RAW_RESOURCES:
        enabled_items.extend(RAW_RESOURCES)
        debug_message(f"Added {len(RAW_RESOURCES)} raw resources to disposable list", 67)
    
    if DROP_CRAFTED_RESOURCES:
        enabled_items.extend(CRAFTED_RESOURCES)
        debug_message(f"Added {len(CRAFTED_RESOURCES)} crafted resources to disposable list", 67)
    
    if DROP_FOOD_ITEMS:
        enabled_items.extend(FOOD_ITEMS)
        debug_message(f"Added {len(FOOD_ITEMS)} food items to disposable list", 67)
    
    if DROP_MISCELLANEOUS_ITEMS:
        enabled_items.extend(MISCELLANEOUS_ITEMS)
        debug_message(f"Added {len(MISCELLANEOUS_ITEMS)} miscellaneous items to disposable list", 67)

    if DROP_LESSER_WANDS:
        enabled_items.extend(LESSER_WAND_ITEMS)
        debug_message(f"Added {len(LESSER_WAND_ITEMS)} lesser wands to disposable list", 67)
    
    # Always-trash items are unconditionally added
    enabled_items.extend(ALWAYS_TRASH_ITEMS)
    debug_message(f"Added {len(ALWAYS_TRASH_ITEMS)} always-trash items to disposable list", 67)
    
    debug_message(f"Total disposable items enabled: {len(enabled_items)}", 67)
    return enabled_items


def debug_message(message, color=67):
    """Send a message if DEBUG_MODE is enabled"""
    if DEBUG_MODE:
        Misc.SendMessage(f"[ITEM_weight_manager.py] {message}", color)

def get_item_name(item):
    """Get the actual name of an item by examining its properties."""
    try:
        # Try to get the item name from properties
        if hasattr(item, 'Name') and item.Name:
            return item.Name
        
        # Fallback: try to get name from property string
        prop_string = Items.GetPropStringList(item.Serial)
        if prop_string and len(prop_string) > 0:
            return prop_string[0]  # First line is usually the item name
        
        return "Unknown Item"
    except:
        return "Unknown Item"

def get_potion_quality(item):
    """Extract potion quality from item name (e.g., 'Greater', 'Lesser', etc.)."""
    try:
        item_name = get_item_name(item)
        if not item_name:
            return "Unknown"
        
        # Common potion quality prefixes
        qualities = ["Greater", "Lesser", "Total", "Deadly", "Lethal"]
        
        for quality in qualities:
            if quality.lower() in item_name.lower():
                return quality
        
        # If no quality prefix found, assume it's a basic/regular potion
        return "Regular"
    except:
        return "Unknown"

def should_keep_potion(item):
    """Determine if a potion should be kept based on its quality."""
    if not ENABLE_POTION_QUALITY_FILTER:
        return True  # Keep all potions if filtering is disabled
    
    quality = get_potion_quality(item)
    should_keep = quality in KEEP_POTION_QUALITIES
    
    debug_message(f"Potion quality check: '{get_item_name(item)}' -> Quality: '{quality}' -> Keep: {should_keep}", 67)
    return should_keep

def is_potion_item(item_id):
    """Check if an item ID corresponds to a potion."""
    return any(potion["id"] == item_id for potion in POTION_ITEMS)

def is_special_hue_potion(item):
    """Return True if a potion item has a protected special hue.

    Rules:
    - If TREAT_ANY_NONZERO_HUE_AS_SPECIAL is True: any Hue != 0x0000 is protected
    - Else: Hue must be in SPECIAL_POTION_HUES to be protected
    Only applies to potion ItemIDs.
    """
    try:
        if not is_potion_item(item.ItemID):
            return False
        hue = item.Hue if hasattr(item, 'Hue') else 0
        if TREAT_ANY_NONZERO_HUE_AS_SPECIAL:
            return hue != 0x0000
        return hue in SPECIAL_POTION_HUES
    except:
        return False

def is_excluded_item(item):
    """Check if an item should be excluded from dropping based on ID and hue."""
    try:
        for excluded in EXCLUDED_ITEMS:
            # Check if item ID matches
            if item.ItemID == excluded["id"]:
                # If exclusion has a specific hue, check it matches
                if excluded.get("hue") is not None:
                    if item.Hue == excluded["hue"]:
                        debug_message(f"Excluding {excluded['name']} (ID: 0x{excluded['id']:04X}, Hue: 0x{excluded['hue']:04X})", 67)
                        return True
                # If no specific hue required, exclude all variants
                else:
                    debug_message(f"Excluding {excluded['name']} (ID: 0x{excluded['id']:04X}, any hue)", 67)
                    return True
        return False
    except:
        return False

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

def find_all_item_variants(item_id, container_serial):
    """Find all variants (different hues) of an item in a container.
    Returns a list of all item objects with the specified ItemID, regardless of hue."""
    all_variants = []
    
    # Use Items.FindAllByID with -1 hue to get all variants, then filter by container
    all_items_of_type = Items.FindAllByID(item_id, -1, container_serial, -1)
    
    if not all_items_of_type:
        debug_message(f"No variants found for ItemID 0x{item_id:04X}", 67)
        return all_variants
    
    # Convert single item to list if needed
    if not isinstance(all_items_of_type, list):
        all_items_of_type = [all_items_of_type]
    
    # Add all found items to our variants list
    for item in all_items_of_type:
        if item and item.Container == container_serial:
            all_variants.append(item)
    
    debug_message(f"Found {len(all_variants)} variants of ItemID 0x{item_id:04X}", 67)
    return all_variants

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
    
    # Check managed items (only if enabled)
    if ENABLE_MANAGED_ITEMS:
        for item_info in MANAGED_ITEMS:
            count = Items.ContainerCount(Player.Backpack.Serial, item_info["id"], -1)
            if count > item_info.get("min_count", 0):
                existing_items[str(item_info["id"])] = count
    
    # Check potion items for quality filtering
    if ENABLE_POTION_QUALITY_FILTER:
        for potion_info in POTION_ITEMS:
            count = Items.ContainerCount(Player.Backpack.Serial, potion_info["id"], -1)
            if count > 0:
                existing_items[f"potion_{potion_info['id']}"] = count
    
    return existing_items

def manage_all_items():
    """Main function to manage all item counts."""
    global DISPOSABLE_ITEMS
    
    # Generate the disposable items list based on enabled categories
    DISPOSABLE_ITEMS = get_enabled_disposable_items()
    
    debug_message(f"Starting item count management... (Managed Items: {'Enabled' if ENABLE_MANAGED_ITEMS else 'Disabled'})", 67)
    debug_message(f"Category Status: Scrolls={DROP_MAGIC_SCROLLS}, Pagan={DROP_PAGAN_REAGENTS}, Raw={DROP_RAW_RESOURCES}, Crafted={DROP_CRAFTED_RESOURCES}, Food={DROP_FOOD_ITEMS}, Misc={DROP_MISCELLANEOUS_ITEMS}", 67)
    
    # First do a bulk check of all items
    existing_items = find_existing_items()
    if not existing_items:
        debug_message("No items to manage!", 67)
        return
    
    # Handle potion quality filtering first (if enabled)
    if ENABLE_POTION_QUALITY_FILTER:
        for potion_info in POTION_ITEMS:
            potion_key = f"potion_{potion_info['id']}"
            if potion_key in existing_items:
                manage_potion_quality(potion_info)
                Misc.Pause(100)
    
    # Handle disposable items that exist
    for item_info in DISPOSABLE_ITEMS:
        # Create the key based on whether the item has a hue
        item_key = f"{item_info['id']}_{item_info.get('hue', '')}" if "hue" in item_info and item_info["hue"] is not None else str(item_info["id"])
        
        if item_key in existing_items:
            drop_all_items(item_info)
            Misc.Pause(100)
    
    # Handle managed items that exceed minimum (only if enabled)
    if ENABLE_MANAGED_ITEMS:
        for item_info in MANAGED_ITEMS:
            if str(item_info["id"]) in existing_items:
                manage_item_count(item_info)
                Misc.Pause(100)
    else:
        debug_message("Managed items processing is disabled", 67)
    
    debug_message("Item count management complete!", 67)

def drop_all_items(item_info):
    """Drop all instances of an item, including all variants with different hues."""
    # Find items with specific hue if specified
    if "hue" in item_info and item_info["hue"] is not None:
        items = Items.FindByID(item_info["id"], item_info["hue"], Player.Backpack.Serial)
        if not items:
            return
        
        # Convert single item to list
        if not isinstance(items, list):
            items = [items]
        
        # Filter out excluded items
        items_to_drop = [item for item in items if not is_excluded_item(item)]
        
        if not items_to_drop:
            debug_message(f"All {item_info['name']} items are excluded from dropping", 67)
            return
        
        count = len(items_to_drop)
        debug_message(f"Dropping {count} {item_info['name']} (specific hue)", 67)
        
        # Drop each stack separately
        for item in items_to_drop:
            try_drop_items(item, item.Amount if hasattr(item, 'Amount') else 1)
            Misc.Pause(100)
    else:
        # Find ALL variants of this ItemID (all hues)
        all_variants = find_all_item_variants(item_info["id"], Player.Backpack.Serial)
        
        if not all_variants:
            return
        
        # Filter out excluded items
        items_to_drop = [item for item in all_variants if not is_excluded_item(item)]
        
        if not items_to_drop:
            debug_message(f"All {item_info['name']} items are excluded from dropping", 67)
            return
        
        total_count = sum(item.Amount if hasattr(item, 'Amount') else 1 for item in items_to_drop)
        excluded_count = len(all_variants) - len(items_to_drop)
        
        debug_message(f"Dropping {total_count} {item_info['name']} ({len(items_to_drop)} stacks, {excluded_count} excluded)", 67)
        
        # Drop each variant stack separately
        for item in items_to_drop:
            amount = item.Amount if hasattr(item, 'Amount') else 1
            debug_message(f"  Dropping {amount} items from stack (hue: 0x{item.Hue:04X})", 67)
            try_drop_items(item, amount)
            Misc.Pause(100)

def manage_item_count(item_info):
    """Manage count for a specific item, handling all variants with different hues."""
    # Find ALL variants of this ItemID (all hues)
    all_variants = find_all_item_variants(item_info["id"], Player.Backpack.Serial)
    
    if not all_variants:
        return
    
    # Calculate total count across all variants
    total_count = sum(item.Amount if hasattr(item, 'Amount') else 1 for item in all_variants)
    amount_to_drop = total_count - item_info["min_count"]
    
    if amount_to_drop > 0:
        debug_message(f"Need to drop {amount_to_drop} {item_info['name']} (total: {total_count}, across {len(all_variants)} stacks)", 67)
        
        # Drop from variants until we reach the desired amount
        remaining_to_drop = amount_to_drop
        
        for item in all_variants:
            if remaining_to_drop <= 0:
                break
            
            # If this is a potion with a special hue, never drop from this stack
            if is_potion_item(item_info["id"]) and is_special_hue_potion(item):
                debug_message(f"  Skipping special-hue potion stack (hue: 0x{item.Hue:04X})", 67)
                continue

            item_amount = item.Amount if hasattr(item, 'Amount') else 1
            drop_from_this_stack = min(item_amount, remaining_to_drop)
            
            debug_message(f"  Dropping {drop_from_this_stack} from stack (hue: {item.Hue})", 67)
            amount_dropped = try_drop_items(item, drop_from_this_stack)
            
            remaining_to_drop -= amount_dropped
            
            Misc.Pause(100)
        
        # If we couldn't drop all items, wait and try again
        if remaining_to_drop > 0:
            Misc.Pause(500)
            debug_message(f"Retrying to drop remaining {remaining_to_drop} items", 67)
            
            # Refresh the variant list and try again
            updated_variants = find_all_item_variants(item_info["id"], Player.Backpack.Serial)
            new_total = sum(item.Amount if hasattr(item, 'Amount') else 1 for item in updated_variants)
            final_to_drop = new_total - item_info["min_count"]
            
            if final_to_drop > 0 and updated_variants:
                try_drop_items(updated_variants[0], final_to_drop)

def manage_potion_quality(potion_info):
    """Manage potion quality by dropping unwanted quality potions."""
    # Find ALL variants of this potion ItemID (all hues)
    all_variants = find_all_item_variants(potion_info["id"], Player.Backpack.Serial)
    
    if not all_variants:
        return
    
    potions_to_drop = []
    potions_to_keep = []
    
    # Categorize potions by quality, but never drop special-hue potions
    for item in all_variants:
        if is_special_hue_potion(item):
            debug_message(f"Protecting special-hue potion: {get_item_name(item)} (Hue: 0x{item.Hue:04X})", 67)
            potions_to_keep.append(item)
            continue
        if should_keep_potion(item):
            potions_to_keep.append(item)
        else:
            potions_to_drop.append(item)
    
    if potions_to_drop:
        total_to_drop = sum(item.Amount if hasattr(item, 'Amount') else 1 for item in potions_to_drop)
        total_to_keep = sum(item.Amount if hasattr(item, 'Amount') else 1 for item in potions_to_keep)
        
        debug_message(f"Potion quality filter for {potion_info['name']}: Keeping {total_to_keep}, Dropping {total_to_drop}", 67)
        
        # Drop each unwanted potion (excluding any special-hue potions which were already filtered)
        for item in potions_to_drop:
            amount = item.Amount if hasattr(item, 'Amount') else 1
            quality = get_potion_quality(item)
            debug_message(f"  Dropping {amount} {quality} {potion_info['name']} (hue: {item.Hue})", 67)
            try_drop_items(item, amount)
            Misc.Pause(100)
    else:
        debug_message(f"No unwanted quality potions found for {potion_info['name']}", 67)


if __name__ == "__main__":
    manage_all_items()
