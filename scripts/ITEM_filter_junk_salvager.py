"""
ITEM Filter Organizer Junk Salvager - a Razor Enhanced Python Script for Ultima Online

A Strict Item Filter , configurable to save items by type and by tier of their properties 
- Moves low tier items to a junk backpack based on Tier configuration
- Salvages items in the "junk" (red) backpack ( unchained )
- Configurable Tier reservations by their properties ( Vanquishing , Greater Slaying , Invulnerable )

Adjust the settings to your liking , default setting =
- only save leather , plate , and maces , of tier 1 highest ( invulnable , vanquishing ) 

Requirements:
- Any configured salvage tool in player's backpack ( tinker tools , or sewing kit )
- A red dyed backpack that will hold the salvagable items

# TODO:
- have equip_slot be apart of the item dicts properties 
- implement single item strictness 
- add shields

HOTKEY:: O
VERSION::20250714
"""
#//========================================================================================

# SETTINGS
DEBUG_MODE = False  # Set to True to enable debug/info messages
AUTO_SALVAGE = True      # Set to False to skip auto-salvaging (for debugging)

# ITEM TYPE-based filtering , SAVE itmes you favor , set to False types unfavored
SAVE_ITEM_WEAPON_AXE = False
SAVE_ITEM_WEAPON_SWORD = False
SAVE_ITEM_WEAPON_MACE = True # defaulting only maces
SAVE_ITEM_WEAPON_FENCING = False
SAVE_ITEM_WEAPON_ARCHERY = False
SAVE_ITEM_WEAPON_UNKNOWN = False

# Default is only saving leather and plate armor 
SAVE_ITEM_ARMOR_LEATHER = True # defaulting leather armor for mages
SAVE_ITEM_ARMOR_PLATE = True # defaulting plate armor for warriors
SAVE_ITEM_ARMOR_CHAINMAIL = False
SAVE_ITEM_ARMOR_RINGMAIL = False
SAVE_ITEM_ARMOR_STUDDED = False
SAVE_ITEM_ARMOR_BONE = False

SAVE_ITEM_ARMOR_SHIELD = True

# STRICTEST FILTERING - SINGLE ITEM ID
SAVE_ONLY_THIS_ONE_WEAPON = False # sometimes we only favor a single weapon id 
SAVE_ONLY_THIS_ONE_WEAPON_ID = 0x143D # Hammer Pick

SAVE_ONLY_THIS_ONE_ARMOR = False # sometimes we only favor a single armor id 
SAVE_ONLY_THIS_ONE_ARMOR_ID = 0x0F5C # Leather female plate

SAVE_ONLY_THIS_ONE_SHIELD = False # sometimes we only favor a single shield id 
SAVE_ONLY_THIS_ONE_SHIELD_ID = 0x1BC4 # Order shield

# AFFIX TIER FILTERING
RESERVE_TIERS = {
    'TIER1': True,      # Set to True to reserve Tier 1 items
    'TIER2': True,     # Set to True to reserve Tier 2 items
    'TIER3': True,     # Set to True to reserve Tier 3 items
    'TIER4': True,     # Set to True to reserve Tier 4 items
    'MAGICAL': False   # Set to True to reserve other magical items
}

# TIER AFFIX DEFINITIONS (GLOBAL)
TIER1_AFFIXES = [ # these are the best 
    "Vanquishing",    # +25 damage
    "Greater",        # Slaying +25%
    "Invulnerable"    # +100% armor
]

TIER2_AFFIXES = [
    "Power",             # +20 damage
    "Supremely Accurate", # +25% Hit Chance
    "Fortification"      # +80% armor
]

TIER3_AFFIXES = [
    "Force",        # +15 damage
    "Massive"    # +60% armor
]

TIER4_AFFIXES = [
    "Might",        # +10 damage
    "Substantial"    # +40% armor
]


# Junk Backpack Configuration
JUNK_BACKPACK_ID = 0x0E75 # a backpack 
JUNK_BACKPACK_HUES = [0x0021, 0x0026, 0x002B]  # Range of red hues that are acceptable
JUNK_BACKPACK_SERIAL = 0  # Will be auto-set by find_junk_backpack()

# Arcane Dust
ARCANE_DUST_ITEMID = 0x5745
ARCANE_DUST_COLOR = 0x07ad

# Item Type Configuration
#//========================================================================================
# Weapon Category Info Mapping Split by Sub Type

WEAPON_AXE_INFO = {
    0x0F49: { 'name': 'Axe', 'id': '0x0F49', 'subtype': 'Axe', 'category': 'Weapon' },
    0x0F47: { 'name': 'Battle Axe', 'id': '0x0F47', 'subtype': 'Axe', 'category': 'Weapon' },
    0x0F4B: { 'name': 'Double Axe', 'id': '0x0F4B', 'subtype': 'Axe', 'category': 'Weapon' },
    0x0F45: { 'name': "Executioner's Axe", 'id': '0x0F45', 'subtype': 'Axe', 'category': 'Weapon' },
    0x0F43: { 'name': 'Hatchet', 'id': '0x0F43', 'subtype': 'Axe', 'category': 'Weapon' },
    0x13FB: { 'name': 'Large Battle Axe', 'id': '0x13FB', 'subtype': 'Axe', 'category': 'Weapon' },
    0x1443: { 'name': 'Two Handed Axe', 'id': '0x1443', 'subtype': 'Axe', 'category': 'Weapon' },
    0x13B0: { 'name': 'War Axe', 'id': '0x13B0', 'subtype': 'Axe', 'category': 'Weapon' },
}

WEAPON_SWORD_INFO = {
    0x0F5E: { 'name': 'Broadsword', 'id': '0x0F5E', 'subtype': 'Sword', 'category': 'Weapon' },
    0x1441: { 'name': 'Cutlass', 'id': '0x1441', 'subtype': 'Sword', 'category': 'Weapon' },
    0x13FF: { 'name': 'Katana', 'id': '0x13FF', 'subtype': 'Sword', 'category': 'Weapon' },
    0x0F61: { 'name': 'Longsword', 'id': '0x0F61', 'subtype': 'Sword', 'category': 'Weapon' },
    0x13B6: { 'name': 'Scimitar', 'id': '0x13B6', 'subtype': 'Sword', 'category': 'Weapon' },
    0x13B9: { 'name': 'Viking Sword', 'id': '0x13B9', 'subtype': 'Sword', 'category': 'Weapon' },
}

WEAPON_MACE_INFO = {
    0x13B4: { 'name': 'Club', 'id': '0x13B4', 'subtype': 'Mace', 'category': 'Weapon' },
    0x143D: { 'name': 'Hammer Pick', 'id': '0x143D', 'subtype': 'Mace', 'category': 'Weapon' },
    0x0F5C: { 'name': 'Mace', 'id': '0x0F5C', 'subtype': 'Mace', 'category': 'Weapon' },
    0x143B: { 'name': 'Maul', 'id': '0x143B', 'subtype': 'Mace', 'category': 'Weapon' },
    0x1439: { 'name': 'War Hammer', 'id': '0x1439', 'subtype': 'Mace', 'category': 'Weapon' },
    0x1407: { 'name': 'War Mace', 'id': '0x1407', 'subtype': 'Mace', 'category': 'Weapon' },
    0x0DF0: { 'name': 'Black Staff', 'id': '0x0DF0', 'subtype': 'Mace', 'category': 'Weapon' },
    0x13F8: { 'name': 'Gnarled Staff', 'id': '0x13F8', 'subtype': 'Mace', 'category': 'Weapon' },
    0x0E89: { 'name': 'Quarter Staff', 'id': '0x0E89', 'subtype': 'Mace', 'category': 'Weapon' },
}

WEAPON_FENCING_INFO = {
    0x0EC3: { 'name': 'Cleaver', 'id': '0x0EC3', 'subtype': 'Fencing', 'category': 'Weapon' },
    0x0EC4: { 'name': 'Skinning Knife', 'id': '0x0EC4', 'subtype': 'Fencing', 'category': 'Weapon' },
    0x13F6: { 'name': 'Butcher Knife', 'id': '0x13F6', 'subtype': 'Fencing', 'category': 'Weapon' },
    0x0F52: { 'name': 'Dagger', 'id': '0x0F52', 'subtype': 'Fencing', 'category': 'Weapon' },
    0x0F62: { 'name': 'Spear', 'id': '0x0F62', 'subtype': 'Fencing', 'category': 'Weapon' },
    0x1403: { 'name': 'Short Spear', 'id': '0x1403', 'subtype': 'Fencing', 'category': 'Weapon' },
    0x1405: { 'name': 'War Fork', 'id': '0x1405', 'subtype': 'Fencing', 'category': 'Weapon' },
    0x1401: { 'name': 'Kryss', 'id': '0x1401', 'subtype': 'Fencing', 'category': 'Weapon' },
}

WEAPON_ARCHERY_INFO = {
    0x13B2: { 'name': 'Bow', 'id': '0x13B2', 'subtype': 'Archery', 'category': 'Weapon' },
    0x13B1: { 'name': 'Bow (Alternate)', 'id': '0x13B1', 'subtype': 'Archery', 'category': 'Weapon' },
    0x26C2: { 'name': 'Composite Bow', 'id': '0x26C2', 'subtype': 'Archery', 'category': 'Weapon' },
    0x0F50: { 'name': 'Crossbow', 'id': '0x0F50', 'subtype': 'Archery', 'category': 'Weapon' },
    0x13FD: { 'name': 'Heavy Crossbow', 'id': '0x13FD', 'subtype': 'Archery', 'category': 'Weapon' },
    0x26C3: { 'name': 'Repeating Crossbow', 'id': '0x26C3', 'subtype': 'Archery', 'category': 'Weapon' },
    0x2D1F: { 'name': 'Magical Shortbow', 'id': '0x2D1F', 'subtype': 'Archery', 'category': 'Weapon' },
}

WEAPON_UNKNOWN_INFO = {
    0x0E86: { 'name': 'Pickaxe', 'id': '0x0E86', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Axe
    0x0DF2: { 'name': 'Magic Wand', 'id': '0x0DF2', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Mace
    0x26BC: { 'name': 'Scepter', 'id': '0x26BC', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Mace
    0x1439: { 'name': 'War Hammer', 'id': '0x1439', 'subtype': 'Unknown', 'category': 'Weapon' },  # confirmed
    0x0F4D: { 'name': 'Bardiche', 'id': '0x0F4D', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Axe
    0x143E: { 'name': 'Halberd', 'id': '0x143E', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Axe
    0x26BA: { 'name': 'Scythe', 'id': '0x26BA', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Axe
    0x26BD: { 'name': 'Bladed Staff', 'id': '0x26BD', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Polearm
    0x26BF: { 'name': 'Double Bladed Staff', 'id': '0x26BF', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Polearm
    0x26BE: { 'name': 'Pike', 'id': '0x26BE', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Polearm
    0x0E87: { 'name': 'Pitchfork', 'id': '0x0E87', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Fencing
    0x0E81: { 'name': "Shepherd's Crook", 'id': '0x0E81', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Mace
    0x26BB: { 'name': 'Bone Harvester', 'id': '0x26BB', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Axe
    0x26C5: { 'name': 'Bone Harvester (Alternate)', 'id': '0x26C5', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Axe
    0x26C1: { 'name': 'Crescent Blade', 'id': '0x26C1', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Sword
    0x1400: { 'name': 'Kryss (Alternate)', 'id': '0x1400', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Fencing
    0x26C0: { 'name': 'Lance', 'id': '0x26C0', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Polearm
    0x27A8: { 'name': 'Bokuto', 'id': '0x27A8', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Mace
    0x27A9: { 'name': 'Daisho', 'id': '0x27A9', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Sword
    0x27AD: { 'name': 'Kama', 'id': '0x27AD', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Fencing
    0x27A7: { 'name': 'Lajatang', 'id': '0x27A7', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Polearm
    0x27A2: { 'name': 'No-Dachi', 'id': '0x27A2', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Sword
    0x27AE: { 'name': 'Nunchaku', 'id': '0x27AE', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Mace
    0x27AF: { 'name': 'Sai', 'id': '0x27AF', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Fencing
    0x27AB: { 'name': 'Tekagi', 'id': '0x27AB', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Fencing
    0x27A3: { 'name': 'Tessen', 'id': '0x27A3', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Fencing
    0x27A6: { 'name': 'Tetsubo', 'id': '0x27A6', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Mace
    0x27A4: { 'name': 'Wakizashi', 'id': '0x27A4', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Sword
    0x27A5: { 'name': 'Yumi', 'id': '0x27A5', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Archery
    0x2D21: { 'name': 'Assassin Spike', 'id': '0x2D21', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Fencing
    0x2D24: { 'name': 'Diamond Mace', 'id': '0x2D24', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Mace
    0x2D1E: { 'name': 'Elven Composite Longbow', 'id': '0x2D1E', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Archery
    0x2D35: { 'name': 'Elven Machete', 'id': '0x2D35', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Sword
    0x2D20: { 'name': 'Elven Spellblade', 'id': '0x2D20', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Sword
    0x2D22: { 'name': 'Leafblade', 'id': '0x2D22', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Fencing
    0x2D2B: { 'name': 'Magical Shortbow (Alternate)', 'id': '0x2D2B', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Archery
    0x2D28: { 'name': 'Ornate Axe', 'id': '0x2D28', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Axe
    0x2D33: { 'name': 'Radiant Scimitar', 'id': '0x2D33', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Sword
    0x2D32: { 'name': 'Rune Blade', 'id': '0x2D32', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Sword
    0x2D2F: { 'name': 'War Cleaver', 'id': '0x2D2F', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Axe
    0x2D25: { 'name': 'Wild Staff', 'id': '0x2D25', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Mace
    0x406B: { 'name': 'Soul Glaive', 'id': '0x406B', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Throwing
    0x406C: { 'name': 'Cyclone', 'id': '0x406C', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Throwing
    0x4067: { 'name': 'Boomerang', 'id': '0x4067', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Throwing
    0x08FE: { 'name': 'Bloodblade', 'id': '0x08FE', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Sword
    0x0903: { 'name': 'Disc Mace', 'id': '0x0903', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Mace
    0x090B: { 'name': 'Dread Sword', 'id': '0x090B', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Sword
    0x0904: { 'name': 'Dual Pointed Spear', 'id': '0x0904', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Fencing
    0x08FD: { 'name': 'Dual Short Axes', 'id': '0x08FD', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Axe
    0x48B2: { 'name': 'Gargish Axe', 'id': '0x48B2', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Axe
    0x48B4: { 'name': 'Gargish Bardiche', 'id': '0x48B4', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Axe
    0x48B0: { 'name': 'Gargish Battle Axe', 'id': '0x48B0', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Axe
    0x48C6: { 'name': 'Gargish Bone Harvester', 'id': '0x48C6', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Axe
    0x48B6: { 'name': 'Gargish Butcher Knife', 'id': '0x48B6', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Fencing
    0x48AE: { 'name': 'Gargish Cleaver', 'id': '0x48AE', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Fencing
    0x0902: { 'name': 'Gargish Dagger', 'id': '0x0902', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Fencing
    0x48D0: { 'name': 'Gargish Daisho', 'id': '0x48D0', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Sword
    0x48B8: { 'name': 'Gargish Gnarled Staff', 'id': '0x48B8', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Mace
    0x48BA: { 'name': 'Gargish Katana', 'id': '0x48BA', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Sword
    0x48BC: { 'name': 'Gargish Kryss', 'id': '0x48BC', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Fencing
    0x48CA: { 'name': 'Gargish Lance', 'id': '0x48CA', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Polearm
    0x48C2: { 'name': 'Gargish Maul', 'id': '0x48C2', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Mace
    0x48C8: { 'name': 'Gargish Pike', 'id': '0x48C8', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Polearm
    0x48C4: { 'name': 'Gargish Scythe', 'id': '0x48C4', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Axe
    0x0908: { 'name': 'Gargish Talwar', 'id': '0x0908', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Sword
    0x48CE: { 'name': 'Gargish Tekagi', 'id': '0x48CE', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Fencing
    0x48CC: { 'name': 'Gargish Tessen', 'id': '0x48CC', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Fencing
    0x48C0: { 'name': 'Gargish War Hammer', 'id': '0x48C0', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Mace
    0x0905: { 'name': 'Glass Staff', 'id': '0x0905', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Mace
    0x090C: { 'name': 'Glass Sword', 'id': '0x090C', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Sword
    0x0906: { 'name': 'Serpentstone Staff', 'id': '0x0906', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Mace
    0x0907: { 'name': 'Shortblade', 'id': '0x0907', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Fencing
    0x0900: { 'name': 'Stone War Sword', 'id': '0x0900', 'subtype': 'Unknown', 'category': 'Weapon' },  # guess: Sword
}

# Merge all to get the full WEAPON_INFO :
WEAPON_INFO = {**WEAPON_AXE_INFO, **WEAPON_SWORD_INFO, **WEAPON_MACE_INFO, **WEAPON_FENCING_INFO, **WEAPON_ARCHERY_INFO, **WEAPON_UNKNOWN_INFO}

# Shield Info Mapping
# Each entry: itemID: { 'name': ..., 'id': ..., 'subtype': ..., 'category': ... }
SHIELD_BASE_INFO = {
    0x1B72: { 'name': 'Bronze Shield', 'id': '0x1B72', 'subtype': 'Shield', 'category': 'Shield' },
    0x1B73: { 'name': 'Buckler', 'id': '0x1B73', 'subtype': 'Shield', 'category': 'Shield' },
    0x1B74: { 'name': 'Metal Kite Shield', 'id': '0x1B74', 'subtype': 'Shield', 'category': 'Shield' },
    0x1B75: { 'name': 'Shield', 'id': '0x1B75', 'subtype': 'Shield', 'category': 'Shield' },
    0x1B76: { 'name': 'Heater Shield', 'id': '0x1B76', 'subtype': 'Shield', 'category': 'Shield' },
    0x1B77: { 'name': 'Shield', 'id': '0x1B77', 'subtype': 'Shield', 'category': 'Shield' },
    0x1B78: { 'name': 'Wooden Shield', 'id': '0x1B78', 'subtype': 'Shield', 'category': 'Shield' },
    0x1B79: { 'name': 'Shield', 'id': '0x1B79', 'subtype': 'Shield', 'category': 'Shield' },
    0x1B7A: { 'name': 'Wooden Kite Shield', 'id': '0x1B7A', 'subtype': 'Shield', 'category': 'Shield' },
    0x1B7B: { 'name': 'Metal Shield', 'id': '0x1B7B', 'subtype': 'Shield', 'category': 'Shield' },
    0x1BC3: { 'name': 'Chaos Shield', 'id': '0x1BC3', 'subtype': 'Shield', 'category': 'Shield' },
    0x1BC4: { 'name': 'Order Shield', 'id': '0x1BC4', 'subtype': 'Shield', 'category': 'Shield' },
}

SHIELD_UNKNOWN_INFO = {
    0x1BC5: { 'name': 'Shield', 'id': '0x1BC5', 'subtype': 'Unknown', 'category': 'Shield' },
    0x4201: { 'name': 'Shield', 'id': '0x4201', 'subtype': 'Unknown', 'category': 'Shield' },  # guess: Shield
    0x4200: { 'name': 'Shield', 'id': '0x4200', 'subtype': 'Unknown', 'category': 'Shield' },  # guess: Shield
    0x4202: { 'name': 'Shield', 'id': '0x4202', 'subtype': 'Unknown', 'category': 'Shield' },  # guess: Shield
    0x4203: { 'name': 'Shield', 'id': '0x4203', 'subtype': 'Unknown', 'category': 'Shield' },  # guess: Shield
    0x4204: { 'name': 'Shield', 'id': '0x4204', 'subtype': 'Unknown', 'category': 'Shield' },  # guess: Shield
    0x4205: { 'name': 'Shield', 'id': '0x4205', 'subtype': 'Unknown', 'category': 'Shield' },  # guess: Shield
    0x4206: { 'name': 'Shield', 'id': '0x4206', 'subtype': 'Unknown', 'category': 'Shield' },  # guess: Shield
    0x4207: { 'name': 'Shield', 'id': '0x4207', 'subtype': 'Unknown', 'category': 'Shield' },  # guess: Shield
    0x4208: { 'name': 'Shield', 'id': '0x4208', 'subtype': 'Unknown', 'category': 'Shield' },  # guess: Shield
    0x4228: { 'name': 'Shield', 'id': '0x4228', 'subtype': 'Unknown', 'category': 'Shield' },  # guess: Shield
    0x4229: { 'name': 'Shield', 'id': '0x4229', 'subtype': 'Unknown', 'category': 'Shield' },  # guess: Shield
    0x422A: { 'name': 'Shield', 'id': '0x422A', 'subtype': 'Unknown', 'category': 'Shield' },  # guess: Shield
    0x422C: { 'name': 'Shield', 'id': '0x422C', 'subtype': 'Unknown', 'category': 'Shield' },  # guess: Shield
    0x7817: { 'name': 'Shield', 'id': '0x7817', 'subtype': 'Unknown', 'category': 'Shield' },  # guess: Shield
    0x7818: { 'name': 'Shield', 'id': '0x7818', 'subtype': 'Unknown', 'category': 'Shield' },  # guess: Shield
    0xA649: { 'name': 'Shield', 'id': '0xA649', 'subtype': 'Unknown', 'category': 'Shield' },  # guess: Shield
}

SHIELD_INFO = {**SHIELD_BASE_INFO, **SHIELD_UNKNOWN_INFO}

# Armor Info Mapping
# Each entry: itemID: { 'name': ..., 'id': ..., 'subtype': ..., 'category': ... }

ARMOR_LEATHER_INFO = {
    0x13CD: { 'name': 'Leather Sleeves', 'id': '0x13CD', 'subtype': 'Leather', 'category': 'Armor' },
    0x13CB: { 'name': 'Leather Leggings', 'id': '0x13CB', 'subtype': 'Leather', 'category': 'Armor' },
    0x13CC: { 'name': 'Leather Tunic', 'id': '0x13CC', 'subtype': 'Leather', 'category': 'Armor' },
    0x13C6: { 'name': 'Leather Gloves', 'id': '0x13C6', 'subtype': 'Leather', 'category': 'Armor' },
    0x1DB9: { 'name': 'Leather Cap', 'id': '0x1DB9', 'subtype': 'Leather', 'category': 'Armor' },
    0x1C08: { 'name': 'Leather Skirt', 'id': '0x1C08', 'subtype': 'Leather', 'category': 'Armor' },
    0x1C06: { 'name': 'Leather Armor (Female)', 'id': '0x1C06', 'subtype': 'Leather', 'category': 'Armor' },
    0x277A: { 'name': 'Leather Mempo', 'id': '0x277A', 'subtype': 'Leather', 'category': 'Armor' },
    0x1C00: { 'name': 'Leather Shorts', 'id': '0x1C00', 'subtype': 'Leather', 'category': 'Armor' },
    0x1C0A: { 'name': 'Leather Bustier', 'id': '0x1C0A', 'subtype': 'Leather', 'category': 'Armor' },
}

ARMOR_PLATEMAIL_INFO = {
    0x13EC: { 'name': 'Plate Mail Arms', 'id': '0x13EC', 'subtype': 'Platemail', 'category': 'Armor' },
    0x1415: { 'name': 'Plate Mail Chest', 'id': '0x1415', 'subtype': 'Platemail', 'category': 'Armor' },
    0x1411: { 'name': 'Plate Mail Legs', 'id': '0x1411', 'subtype': 'Platemail', 'category': 'Armor' },
    0x1414: { 'name': 'Plate Mail Gorget', 'id': '0x1414', 'subtype': 'Platemail', 'category': 'Armor' },
    0x1413: { 'name': 'Plate Mail Gloves', 'id': '0x1413', 'subtype': 'Platemail', 'category': 'Armor' },
    0x2779: { 'name': 'Platemail Mempo', 'id': '0x2779', 'subtype': 'Platemail', 'category': 'Armor' },
    0x140A: { 'name': 'Helmet', 'id': '0x140A', 'subtype': 'Platemail', 'category': 'Armor' },
    0x140C: { 'name': 'Bascinet', 'id': '0x140C', 'subtype': 'Platemail', 'category': 'Armor' },
    0x140E: { 'name': 'Norse Helm', 'id': '0x140E', 'subtype': 'Platemail', 'category': 'Armor' },
    0x1408: { 'name': 'Close Helm', 'id': '0x1408', 'subtype': 'Platemail', 'category': 'Armor' },
    0x1412: { 'name': 'Plate Helm', 'id': '0x1412', 'subtype': 'Platemail', 'category': 'Armor' },
    0x1C04: { 'name': 'Platemail Female', 'id': '0x1C04', 'subtype': 'Platemail', 'category': 'Armor' },
    0x1410: { 'name': 'Platemail Arms', 'id': '0x1410', 'subtype': 'Platemail', 'category': 'Armor' },
}

ARMOR_CHAINMAIL_INFO = {
    0x13BF: { 'name': 'Chainmail Tunic', 'id': '0x13BF', 'subtype': 'Chainmail', 'category': 'Armor' },
    0x13BE: { 'name': 'Chainmail Leggings', 'id': '0x13BE', 'subtype': 'Chainmail', 'category': 'Armor' },
    0x13BB: { 'name': 'Chainmail Coif', 'id': '0x13BB', 'subtype': 'Chainmail', 'category': 'Armor' },
    0x13C0: { 'name': 'Chainmail Tunic (Alt)', 'id': '0x13C0', 'subtype': 'Chainmail', 'category': 'Armor' },
    0x13C3: { 'name': 'Chainmail Sleeves', 'id': '0x13C3', 'subtype': 'Chainmail', 'category': 'Armor' },
    0x13C4: { 'name': 'Chainmail Gloves', 'id': '0x13C4', 'subtype': 'Chainmail', 'category': 'Armor' },
    0x13F0: { 'name': 'Chainmail Leggings (Alt)', 'id': '0x13F0', 'subtype': 'Chainmail', 'category': 'Armor' },
}

ARMOR_BONE_INFO = {
    0x1B72: { 'name': 'Bone Armor', 'id': '0x1B72', 'subtype': 'Bone', 'category': 'Armor' },
    0x1B7B: { 'name': 'Bone Legs', 'id': '0x1B7B', 'subtype': 'Bone', 'category': 'Armor' },
    0x1B73: { 'name': 'Bone Arms', 'id': '0x1B73', 'subtype': 'Bone', 'category': 'Armor' },
    0x144E: { 'name': 'Bone Arms', 'id': '0x144E', 'subtype': 'Bone', 'category': 'Armor' },
    0x1B7A: { 'name': 'Bone Gloves', 'id': '0x1B7A', 'subtype': 'Bone', 'category': 'Armor' },
    0x1B79: { 'name': 'Bone Helmet', 'id': '0x1B79', 'subtype': 'Bone', 'category': 'Armor' },
    0x1450: { 'name': 'Bone Gloves (Alternate)', 'id': '0x1450', 'subtype': 'Bone', 'category': 'Armor' },
    0x1452: { 'name': 'Bone Leggings', 'id': '0x1452', 'subtype': 'Bone', 'category': 'Armor' },
    0x144F: { 'name': 'Bone Armor Chest', 'id': '0x144F', 'subtype': 'Bone', 'category': 'Armor' },
    0x1451: { 'name': 'Bone Helmet', 'id': '0x1451', 'subtype': 'Bone', 'category': 'Armor' },
}

ARMOR_RINGMAIL_INFO = {
    0x13C0: { 'name': 'Ring Mail Tunic', 'id': '0x13C0', 'subtype': 'Ringmail', 'category': 'Armor' },
    0x13C3: { 'name': 'Ring Mail Sleeves', 'id': '0x13C3', 'subtype': 'Ringmail', 'category': 'Armor' },
    0x13C4: { 'name': 'Ring Mail Gloves', 'id': '0x13C4', 'subtype': 'Ringmail', 'category': 'Armor' },
    0x13EE: { 'name': 'Ringmail Sleeves', 'id': '0x13EE', 'subtype': 'Ringmail', 'category': 'Armor' },
    0x13F0: { 'name': 'Ringmail Leggings', 'id': '0x13F0', 'subtype': 'Ringmail', 'category': 'Armor' },
    0x13EB: { 'name': 'Ringmail Gloves', 'id': '0x13EB', 'subtype': 'Ringmail', 'category': 'Armor' },
}

ARMOR_STUDDED_INFO = {
    0x13C7: { 'name': 'Studded Leather Gorget', 'id': '0x13C7', 'subtype': 'Studded', 'category': 'Armor' },
    0x13DB: { 'name': 'Studded Leather Tunic', 'id': '0x13DB', 'subtype': 'Studded', 'category': 'Armor' },
    0x13D4: { 'name': 'Studded Leather Sleeves', 'id': '0x13D4', 'subtype': 'Studded', 'category': 'Armor' },
    0x13DA: { 'name': 'Studded Leather Gloves', 'id': '0x13DA', 'subtype': 'Studded', 'category': 'Armor' },
    0x13D6: { 'name': 'Studded Leather Leggings', 'id': '0x13D6', 'subtype': 'Studded', 'category': 'Armor' },
    0x279D: { 'name': 'Studded Mempo', 'id': '0x279D', 'subtype': 'Studded', 'category': 'Armor' },
    0x13D5: { 'name': 'Studded Gloves', 'id': '0x13D5', 'subtype': 'Studded', 'category': 'Armor' },
    0x13DC: { 'name': 'Studded Sleeves', 'id': '0x13DC', 'subtype': 'Studded', 'category': 'Armor' },
    0x1C0C: { 'name': 'Studded Bustier', 'id': '0x1C0C', 'subtype': 'Studded', 'category': 'Armor' },
    0x1C02: { 'name': 'Studded Armor (Female)', 'id': '0x1C02', 'subtype': 'Studded', 'category': 'Armor' },
}

ARMOR_INFO = {**ARMOR_LEATHER_INFO, **ARMOR_PLATEMAIL_INFO, **ARMOR_BONE_INFO, **ARMOR_CHAINMAIL_INFO, **ARMOR_RINGMAIL_INFO, **ARMOR_STUDDED_INFO}

# ITEM SLOT filters , ultima online armor slot ( no feet ) , useful to distinguish 1handed and 2handed weapons 
ITEM_SLOTS = ['head', 'neck', 'body', 'legs', 'arms', 'hand', 'weapon1h', 'weapon2h', 'shield']
# TODO: have equip_slot be apart of the item dicts properties 

# Timing Configuration
MOVE_DELAY = 1000      # Delay moving items (in milliseconds) , depends on server and object delay , 600 works but we are being safe
SCAN_DELAY = 100       # Delay scanning items (in milliseconds) , this is done to not freeze the rendering 

# Salvage Tool Configuration 0x1EBC
SALVAGE_TOOLS = {
    "Tinker's Tools": {'id': 0x1EB8, 'color': -1, 'gump_id': 949095101, 'salvage_action': 63, 'priority': 1},
    "Tinker's ToolsB": {'id': 0x1EBC, 'color': -1, 'gump_id': 949095101, 'salvage_action': 63, 'priority': 1},
    "Sewing Kit": {'id': 0x0F9D, 'color': -1, 'gump_id': 949095101, 'salvage_action': 63, 'priority': 2}
}

#//========================================================================================
class JunkSalvager:
    def __init__(self):
        # Debug colors
        self.colors = {
            'info': 68,      # Blue
            'warning': 33,   # Red
            'success': 63,   # Green
            'important': 53, # Yellow
            'found': 43,     # Purple
            'config': 90     # Gray for config info
        }
        
        # Initialize stats
        self.stats = {
            'tier1_items': 0,
            'tier2_items': 0,
            'tier3_items': 0,
            'tier4_items': 0,
            'other_items': 0,
            'items_moved': 0,
            'items_checked': 0,
            'subtype_junked': 0,
            'subtype_saved': 0
        }
        
        # Show current configuration
        self.show_config()
        
    def show_config(self):
        """Display current configuration settings"""
        self.debug_message("=== Configuration ===", self.colors['config'])
        self.debug_message(f"Reserve Tier 1 items: {'Yes' if RESERVE_TIERS['TIER1'] else 'No'}", self.colors['config'])
        self.debug_message(f"Reserve Tier 2 items: {'Yes' if RESERVE_TIERS['TIER2'] else 'No'}", self.colors['config'])
        self.debug_message(f"Reserve Tier 3 items: {'Yes' if RESERVE_TIERS['TIER3'] else 'No'}", self.colors['config'])
        self.debug_message(f"Reserve Tier 4 items: {'Yes' if RESERVE_TIERS['TIER4'] else 'No'}", self.colors['config'])
        self.debug_message(f"Reserve magical items: {'Yes' if RESERVE_TIERS['MAGICAL'] else 'No'}", self.colors['config'])
        self.debug_message(f"Move delay: {str(MOVE_DELAY)}ms", self.colors['config'])
        self.debug_message(f"Auto-salvage: {'Yes' if AUTO_SALVAGE else 'No'}", self.colors['config'])
        self.debug_message(f"Junk backpack serial: 0x{JUNK_BACKPACK_SERIAL:X}", self.colors['config'])
        self.debug_message("==================", self.colors['config'])
        
    
    def debug_message(self, message, color='info'):
        """Send debug message to client (deprecated, use debug_message instead)"""
        if DEBUG_MODE:
            Misc.SendMessage(f"[JunkSalvager] {message}", self.colors[color] if isinstance(color, str) else color)
    
    def get_item_properties(self, item):
        """Get item properties using multiple methods"""
        properties = []
        
        try:
            Items.WaitForProps(int(item.Serial), 1000)
            prop_list = Items.GetPropStringList(int(item.Serial))
            if prop_list:
                properties.extend(prop_list)
            
            index = 0
            while True:
                prop = Items.GetPropStringByIndex(int(item.Serial), index)
                if not prop:
                    break
                if prop not in properties:
                    properties.append(prop)
                index += 1
                
            return properties
            
        except Exception as e:
            self.debug_message(f"Error getting properties: {str(e)}", 'warning')
            return properties
            
    def has_affix(self, properties, affixes):
        """Check if item has any of the specified affixes"""
        if not properties:
            return False
            
        for prop in properties:
            prop_lower = str(prop).lower()
            for affix in affixes:
                if affix.lower() in prop_lower:
                    return True
        return False
        
    def has_any_affix(self, properties):
        """Check if item has any magical properties"""
        if not properties:
            return False
            
        magic_indicators = [
            "damage increase",
            "defense chance increase",
            "faster casting",
            "faster cast recovery",
            "hit chance increase",
            "lower mana cost",
            "mage armor",
            "spell channeling",
            "strength bonus",
            "swing speed increase"
        ]
        
        for prop in properties:
            prop_lower = str(prop).lower()
            if any(x in prop_lower for x in ["+", "increase", "bonus", "lower"]):
                return True
            if any(x in prop_lower for x in magic_indicators):
                return True
        return False

    def is_salvageable_item(self, item):
        """Check if item is a weapon, armor, or shield that can be salvaged"""
        return item.ItemID in WEAPON_INFO or item.ItemID in ARMOR_INFO or item.ItemID in SHIELD_INFO

    def should_move_to_junk(self, item):
        """Determine if an item should be moved to junk backpack, using subtype AND tier/magical filtering"""
        # First check if it's a weapon, armor, or shield
        if not self.is_salvageable_item(item):
            return False

        # Get item info dict and subtype
        item_id = item.ItemID
        item_info = WEAPON_INFO.get(item_id) or ARMOR_INFO.get(item_id) or SHIELD_INFO.get(item_id)
        subtype = item_info['subtype'] if item_info and 'subtype' in item_info else None
        category = item_info['category'] if item_info and 'category' in item_info else None
        name = item_info['name'] if item_info and 'name' in item_info else str(item_id)

        # Map subtype to config flag
        save_flag = True
        if item_info:
            if item_info['category'] == 'Weapon':
                save_flag = {
                    'Axe': SAVE_ITEM_WEAPON_AXE,
                    'Sword': SAVE_ITEM_WEAPON_SWORD,
                    'Mace': SAVE_ITEM_WEAPON_MACE,
                    'Fencing': SAVE_ITEM_WEAPON_FENCING,
                    'Archery': SAVE_ITEM_WEAPON_ARCHERY,
                    'Unknown': SAVE_ITEM_WEAPON_UNKNOWN
                }.get(subtype, False)
            elif item_info['category'] == 'Armor':
                save_flag = {
                    'Leather': SAVE_ITEM_ARMOR_LEATHER,
                    'Platemail': SAVE_ITEM_ARMOR_PLATE,
                    'Chainmail': SAVE_ITEM_ARMOR_CHAINMAIL,
                    'Ringmail': SAVE_ITEM_ARMOR_RINGMAIL,
                    'Studded': SAVE_ITEM_ARMOR_STUDDED,
                    'Bone': SAVE_ITEM_ARMOR_BONE
                }.get(subtype, False)
            elif item_info['category'] == 'Shield':
                save_flag = SAVE_ITEM_ARMOR_SHIELD

        properties = self.get_item_properties(item)
        affix_str = ', '.join([str(p) for p in properties]) if properties else 'None'
        tier = 'None'
        if self.has_affix(properties, TIER1_AFFIXES):
            tier = 'T1'
        elif self.has_affix(properties, TIER2_AFFIXES):
            tier = 'T2'
        elif self.has_affix(properties, TIER3_AFFIXES):
            tier = 'T3'
        elif self.has_affix(properties, TIER4_AFFIXES):
            tier = 'T4'
        elif self.has_any_affix(properties):
            tier = 'Magical'

        # Debug: show full filtering decision
        self.debug_message(f"[Filter] {name} (ID: {hex(item_id)}) | Cat: {category} | Subtype: {subtype} | Tier: {tier} | Affixes: {affix_str} | SaveFlag: {save_flag}", self.colors['config'])

        # If the subtype is not configured to save, always junk
        if not save_flag:
            self.stats['subtype_junked'] += 1
            self.debug_message(f"JUNKED by subtype filter: {name} (ID: {hex(item_id)})", self.colors['important'])
            return True

        # Passed subtype filter
        self.stats['subtype_saved'] += 1
        # Check tier 1
        if tier == 'T1':
            self.stats['tier1_items'] += 1
            return not RESERVE_TIERS['TIER1']
        # Check tier 2
        if tier == 'T2':
            self.stats['tier2_items'] += 1
            return not RESERVE_TIERS['TIER2']
        # Check tier 3
        if tier == 'T3':
            self.stats['tier3_items'] += 1
            return not RESERVE_TIERS['TIER3']
        # Check tier 4
        if tier == 'T4':
            self.stats['tier4_items'] += 1
            return not RESERVE_TIERS['TIER4']
        # Check other magical items
        if tier == 'Magical':
            self.stats['other_items'] += 1
            return not RESERVE_TIERS['MAGICAL']
        # Non-magical weapons/armor go to junk
        return True


    def find_salvage_tool(self):
        """Find any available salvage tool in player's backpack"""
        for tool_name, tool_config in SALVAGE_TOOLS.items():
            tool = Items.FindByID(tool_config['id'], tool_config['color'], Player.Backpack.Serial)
            if tool:
                return tool_name, tool, tool_config
        return None, None, None

    def salvage_junk_backpack(self):
        """Salvage items in the junk backpack"""
        if JUNK_BACKPACK_SERIAL == 0:
            self.debug_message("No junk backpack serial configured!", 'warning')
            return False
            
        tool_name, tool, tool_config = self.find_salvage_tool()
        if not tool:
            self.debug_message("No salvage tool found!", 'warning')
            return False
            
        self.debug_message(f"Using {tool_name} to salvage junk backpack", 'info')
        
        # Use the tool
        Items.UseItem(tool)
        Misc.Pause(500)
        
        # Select salvage option
        Gumps.WaitForGump(tool_config['gump_id'], 1000)
        Gumps.SendAction(tool_config['gump_id'], tool_config['salvage_action'])
        Misc.Pause(1000)
        
        # Target the junk backpack
        Target.WaitForTarget(1000)
        Target.TargetExecute(JUNK_BACKPACK_SERIAL)
        Misc.Pause(1000)
        
        # Use any resulting arcane dust
        dust = Items.FindByID(ARCANE_DUST_ITEMID, ARCANE_DUST_COLOR, Player.Backpack.Serial)
        if dust:
            self.debug_message(f"Using Arcane Dust (ID: 0x{ARCANE_DUST_ITEMID:X}, Color: 0x{ARCANE_DUST_COLOR:X})", 'info')
            Items.UseItem(dust)
            Target.WaitForTarget(1000)
            Target.TargetExecute(JUNK_BACKPACK_SERIAL)
            return True
        else:
            self.debug_message(f"No Arcane Dust (ID: 0x{ARCANE_DUST_ITEMID:X}, Color: 0x{ARCANE_DUST_COLOR:X}) found after salvaging.", 'warning')
        return False

    def process_inventory(self):
        """Process inventory and move unwanted items to junk backpack"""
        if JUNK_BACKPACK_SERIAL == 0:
            self.debug_message("No junk backpack serial configured!", 'warning')
            return False
            
        junk_backpack = Items.FindBySerial(JUNK_BACKPACK_SERIAL)
        if not junk_backpack:
            self.debug_message("Junk backpack not found!", 'warning')
            return False
            
        self.debug_message("Processing inventory for junk items...", 'info')
        
        items = Items.FindBySerial(Player.Backpack.Serial).Contains
        for item in items:
            self.stats['items_checked'] += 1
            
            if self.should_move_to_junk(item):
                Items.Move(item, junk_backpack, 0)
                self.stats['items_moved'] += 1
                Misc.Pause(MOVE_DELAY)
                
        self.show_stats()
        return True

    def show_stats(self):
        """Display item processing statistics"""
        self.debug_message("=== Processing Stats ===", 'important')
        self.debug_message(f"Items checked: {self.stats['items_checked']}", 'info')
        self.debug_message(f"Tier 1 items found: {self.stats['tier1_items']}", 'info')
        self.debug_message(f"Tier 2 items found: {self.stats['tier2_items']}", 'info')
        self.debug_message(f"Other magical items: {self.stats['other_items']}", 'info')
        self.debug_message(f"Items moved to junk: {self.stats['items_moved']}", 'info')
        self.debug_message(f"Subtype-junked: {self.stats['subtype_junked']} | Subtype-saved: {self.stats['subtype_saved']}", 'config')

    def find_junk_backpack(self):
        """Find the red junk backpack in player's backpack"""
        if not Player.Backpack:
            self.debug_message("No backpack found!", 33)
            return None
        # Try each hue in our acceptable range
        for hue in JUNK_BACKPACK_HUES:
            junk = Items.FindByID(JUNK_BACKPACK_ID, hue, Player.Backpack.Serial)
            if junk:
                self.debug_message(f"Found junk backpack (hue: 0x{hue:X}): 0x{junk.Serial:X}", 68)
                return junk.Serial
        self.debug_message(f"No junk backpack found with hues {[f'0x{h:X}' for h in JUNK_BACKPACK_HUES]}! Place a red backpack in your backpack.", 33)
        return None

# find junk backpack on script load
JUNK_BACKPACK_SERIAL = JunkSalvager().find_junk_backpack() or 0

def main():
    """Main function to run the junk salvager"""
    try:
        salvager = JunkSalvager()
        if salvager.process_inventory():
            if AUTO_SALVAGE:
                salvager.salvage_junk_backpack()
    except Exception as e:
        Misc.SendMessage(f"Error: {str(e)}", 33)

if __name__ == "__main__":
    main()
