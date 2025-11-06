"""
UI Loot Item Summary - a Razor Enhanced Python Script for Ultima Online

Display a summary of items in backpack , filtered based on rarity and modifiers 
use arrows to tune the rankings , useful after a boss fight or dungeon run

launchs a persistent gump with button , or set LAUNCHER_UI_BUTTON to False to show results immediately for hotkey

VERSION: 20251028
"""

import time
import os
import json

DEBUG_MODE = False
RANKING_BUTTONS_ENABLED = True # Ranking buttons to adjust the rarity preferences , 
LAUNCHER_UI_BUTTON = False # If True, show persistent launcher button. If False, skip launcher and show results immediately

EXPORT_CSV_LOG = False  # Export compact CSV log of all rating actions (append mode)
EXPORT_PYTHON_DICTIONARY = False  # Export final ratings as Python dict code (for pasting into script) 

# Rarity category lists based on user feedback
# Format: (name, item_id, hue)
# legendary = top
LEGENDARY_ITEMS = [
]

EPIC_ITEMS = [
]

RARE_ITEMS = [
    # Items that should be categorized as RARE
    ("Bulwark Orb",                          0x573E, 0x0AD3),  # 22334, 2771
    ("Holy Orb",                             0x573E, 0x09A4),  # 22334, 2468
    ("Fortune Orb",                          0x573E, 0x2931),  # 22334, 2931
    ("Shadow Orb",                           0x573E, 0x2074),  # 22334, 2074
    ("Doom Orb",                             0x573E, 0x2983),  # 22334, 2983
    ("Death Orb",                            0x573E, 0x2874),  # 22334, 2874
    ("a paralyze arcane scroll",             0x0EF3, 0x06FC),  # 3827, 1788
    ("a spell hue deed",                     0x14F0, 0x0A1F),  # 5360, 2591
    ("Helga Steelbeard's Lost Contract",    0xA614, 0x0A4B),  # 42516, 2635
    ("Guild Buff Token",                     0x2AAA, 0x0489),  # 10922, 1161
    ("a spell hue deed",                     0x14F0, 0x08EB),  # 5360, 2283
    ("an energy bolt arcane scroll",         0x0EF3, 0x06FC),  # 3827, 1788
    ("an explosion arcane scroll",           0x0EF3, 0x06FC),  # 3827, 1788
    ("a fireball arcane scroll",             0x0EF3, 0x06F6),  # 3827, 1782
    ("a summon daemon arcane scroll",        0x0EF3, 0x0A44),  # 3827, 2628
]

UNCOMMON_ITEMS = [
    # Items that should be categorized as UNCOMMON
    ("Runebook Dye",                         0x0E27, 0x0B50),  # 3627, 2896
    ("Rare Furniture Dye",                   0x0E26, 0x0482),  # 3626, 1154
    ("Backpack Dye",                         0x0EFF, 0x09B7),  # 3839, 2487
    ("a lesser paragon chest",               0x09A8, 0x04F1),  # 2472, 1265
    ("a oak runic fletching",                0x5737, 0x0B1B),  # 22327, 2843
    ("a oak runic wooden shaft",             0x1BD4, 0x0B1B),  # 7124, 2843
    ("a shadowiron shard",                   0x5738, 0x05C1),  # 22328, 1473
    ("a tattered  expertly drawn treasure map", 0x14EC, 0x0000),  # 5356, 0
    ("a tattered  cleverly drawn treasure map", 0x14EC, 0x0000),  # 5356, 0
    ("a waterstained treasure map",          0x14EC, 0x0825),  # 5356, 2085
]

COMMON_ITEMS = [
    # Items that should be categorized as COMMON (excluded from display)
    ("a britain runestone",                  0x1F14, 0x0B42),  # 7956, 2882
    ("orange petals",                        0x1021, 0x002B),  # 4129, 43
    ("Potion of Invisibility",               0x0F0A, 0x048D),  # 3850, 1165
    ("Mana Drain Wand",                      0x5006, 0x09CB),  # 20494, 2507
    ("ingots",                               0x1BF2, 0x096A),  # 7154, 2418
    ("Petal of the Rose of Moonglow",        0x1021, 0x0B40),  # 4129, 2880
    ("Petal of the Rose of Minoc",           0x1021, 0x07C6),  # 4129, 1990
    ("half apron",                           0x153B, 0x0321),  # 5435, 801
    ("Candy Bag",                            0x0E76, 0x08BB),  # 3702, 2235
    ("ingots",                               0x1BF2, 0x0971),  # 7154, 2425
    ("lucky coin",                           0x0F87, 0x0496),  # 3975, 1174
    ("ingots",                               0x1BF2, 0x0972),  # 7154, 2418
    ("ingots",                               0x1BF2, 0x0973),  # 7154, 2419
    ("ingots",                               0x1BF2, 0x089F),  # 7154, 2207
    ("cut leather",                          0x1081, 0x0283),  # 4225, 643
    ("Fireball Wand",                        0x5010, 0x0827),  # 20496, 2087
    ("ingots",                               0x1BF2, 0x08A5),  # 7154, 2213
    ("yew board",                            0x1BD7, 0x04A8),  # 7127, 1192
    ("ingots",                               0x1BF2, 0x08AB),  # 7154, 2219
    ("Robust Harpy Feathers",                0x5737, 0x0B42),  # 22327, 2882
    ("Spellbook",                            0x0EFA, 0x06F6),  # 3834, 1782
    ("void orb",                             0x573E, 0x0000),  # 22334, 0
    ("Blue Diamond",                         0x3198, 0x0000),  # 12696, 0
    ("fey wings",                            0x5726, 0x0000),  # 22310, 0
    ("void orb",                             0x573E, 0x0000),  # 22334, 0
    ("Magical Residue",                      0x2DB1, 0x0000),  # 11697, 0
    ("Fire Ruby",                            0x3197, 0x0000),  # 12695, 0
    ("Arcane Dust",                          0x5745, 0x07AD),  # 22341, 1965
    ("seed of renewal",                      0x5736, 0x0000),  # 22326, 0
]

# Combined SPECIFIC_ITEMS list for backward compatibility
SPECIFIC_ITEMS = []
for name, item_id, hue in RARE_ITEMS:
    SPECIFIC_ITEMS.append((name, item_id, hue, "rare"))
for name, item_id, hue in UNCOMMON_ITEMS:
    SPECIFIC_ITEMS.append((name, item_id, hue, "uncommon"))
for name, item_id, hue in COMMON_ITEMS:
    SPECIFIC_ITEMS.append((name, item_id, hue, "common"))

# normalized names for debug 
_SPECIFIC_NAMES = set([ (str(nm).strip().lower()) for (nm, _, _, _) in SPECIFIC_ITEMS ])

# GUMP ID LIMIT = 0xFFFFFFF = 4294967295 # max int , make sure gump ids are under this but high unique 
GUMP_ID_RESULTS =             4291161195  # pseudo random unique id
GUMP_ID_LAUNCHER =            4291161196  # pseudo random unique id

GUMP_RESULTS_X = 180
GUMP_RESULTS_Y = 180
RESULTS_TITLE_HEIGHT = 24
RESULTS_TITLE_TEXT = "______  L O O T  ______"

GUMP_LAUNCHER_X = 120 # treasure chest icon button , x and y is low for laptops , set your desired position
GUMP_LAUNCHER_Y = 120

# Tile layout
TILE_WIDTH = 84
TILE_HEIGHT = 86  # includes space for label
TILE_ICON_Y_OFFSET = 8
TILE_TEXT_Y_OFFSET = 48
TILE_TEXT_HEIGHT = 34
TILE_GAP_X = 4
TILE_GAP_Y = 6
MAX_COLS = 10

# Special rendering metrics for 'legendary' tier , wider text for reading
LEGENDARY_TILE_WIDTH = 156
LEGENDARY_TILE_TEXT_HEIGHT = 44
LEGENDARY_TILE_GAP_X = 12

# Section header
SECTION_HEADER_HEIGHT = 20
SECTION_GAP = 6
OUTER_PADDING = 8

# Colors 
COLORS = {
    'title': 68,      # blue
    'label': 1153,    # light gray
    'ok': 63,         # green
    'warn': 53,       # yellow
    'bad': 33,        # red
    'rare_blue': 89,  # cyan/blue
    'epic_purple': 71,
    'legendary_orange': 1160,
}


_SPECIFIC_ITEMS_INDEX = None
_SPECIFIC_FP = None

# User rating persistence system
# Save relative to this script: up one folder into the 'data' directory
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_DATA_DIR = os.path.normpath(os.path.join(_SCRIPT_DIR, '..', 'data'))
USER_RATINGS_FILE = os.path.join(_DATA_DIR, 'loot_user_ratings.json')
CSV_EXPORT_FILE = os.path.join(_DATA_DIR, 'loot_rating_actions.csv')
PYTHON_CODE_EXPORT_FILE = os.path.join(_DATA_DIR, 'loot_ratings_python_dictionary.txt')
RANK_BUTTON_BASE_ID = 1000  # base id for per-item up/down buttons
EXPORT_BUTTON_ID = 999  # dedicated button ID for export functionality
_BUTTON_ACTIONS = {}
_NEXT_BUTTON_ID = RANK_BUTTON_BASE_ID

# In-memory cache of user ratings loaded from JSON
_USER_RATINGS_CACHE = None  # Dict structure: {"item_key": {"current_tier": str, "history": [...]}}

# Timing  
WAIT_PROPS_QUICK_MS = 400         # initial tooltip props wait
WAIT_PROPS_CLICK_MS = 700         # longer tooltip props wait 
SEARCH_THROTTLE_MS = 40             # small per-item throttle during searchs
LAUNCHER_LOOP_MS = 150            # idle loop delay for launcher processing
GUMP_WAIT_MS = 300                # WaitForGump polling (increased to capture clicks reliably)

# Export button dimensions
EXPORT_BUTTON_HEIGHT = 30
EXPORT_BUTTON_MARGIN = 8
EXPORT_BUTTON_SLIVER_OVERLAY = True  # Toggle to show/hide black sliver overlay on export button

# Name colors in HTML 
NAME_TIER_HTML = {
    'legendary': '#FFB84D',
    'epic': '#B084FF',
    'rare': '#3FA9FF',
    'uncommon': '#5CB85C',
}

# Rows are shown top to bottom in this order
RARITY_ORDER = ['legendary', 'epic', 'rare', 'uncommon']
RARITY_TITLES = {
    'legendary': 'Legendary',
    'epic': 'Epic',
    'rare': 'Rare',
    'uncommon': 'Uncommon',
}

# Select artifact weapon names for highlighting 
KNOWN_ARTIFACT_WEAPON_NAMES = {
    # SWORDS
    "Pridestalker's Blade", "Plague", "Death's Dance", "Zeal", "Spectral Scimitar",
    "Blackthorn's Blade", "Breath of the Dead", "Decapitator", "Butcher's Carver", "Deviousness",
    # AXE TYPES
    "Demonic Embrace", "Galeforce", "The Twins' Rage", "Siege Breaker", "Titan's Fall", "Giant's Will",
    "Windseeker", "Infernal Maw", "Executioner's Calling", "World Splitter", "Frostbite", "Lethality",
    "The Condemner",
    # FENCING
    "Silver Fang", "Serpent's Fang", "Bloodthirster", "Mortal Reminder", "Deathfire Grasp",
    "The Taskmaster", "Corrupted Pike",
    # MACE & STAVES
    "Umbral Shard", "Aegis Breaker", "Harbringer", "The Impaler", "Hellclap", "Tantrum",
    "Mindcry", "The Peacekeeper", "The Absorber", "The Shepherd",
    # ARCHERY
    "Elven Bow", "Widow Maker", "Repugnance", "The Dryad Bow", "Wraith Whisperer", "Bow of Infinite Swarms",
}

#  enchanting/crafting materials (by ItemID)
ENCHANTING_MATERIAL_IDS = {
    0x3198,  # Blue Diamond
    0x2DB3,  # Relic Fragment
    0x2DB2,  # Enchanted Essence
    0x2DB1,  # Magical Residue
    0x3197,  # Fire Ruby
    0x5748,  # Bottle Ichor
    0x5745,  # Faery Dust
    0x5726,  # Fey Wings
    0x5736,  # Seed of Renewal
    0x5744,  # Silver Snake
    0x573E,  # Void Orb
}

# Enhancement scroll type 
ENHANCEMENT_SCROLL_ITEMID = 0x0E34

# Powerscroll detection (by name)
POWERSCROLL_NAME_PATTERNS = [
    'power scroll', 'powerscroll', 'stat scroll'
]

# Treasure Maps
TREASURE_MAP_ITEMID = 0x14EC

# Centralized good modifier dictionary (edit this to tune which modifiers are considered good)
GOOD_MODIFIERS = {
    'weapon': {
        'damage': ['vanquishing', ], #tier 2 power
        #'accuracy': ['supremely accurate'],
    },
    'slayer': ['slayer', 'slaying'],  # includes lesser slaying, greater slaying 
    'armor': ['invulnerable', ], # teir 2 'fortification'
}

# Instrument ItemIDs - these contain "slaying" property but should not be ranked high
INSTRUMENT_ITEM_IDS = {
    0x0EB1,  # Standing Harp
    0x0EB2,  # Lap Harp
    0x0EB3,  # Lute
    0x0E9C,  # Drum
    0x0E9D,  # Tambourine
    0x0E9E,  # Tambourine (tassel)
}

# Exclusions: ignore specific ItemID + Hue combinations entirely
EXCLUDE_ITEMS_BY_HUE = {
    0x0F7E: [0x0026, 0x0021], # bones  red , quest item 
    0x0E79: [0x0026, 0x0021], # pouches red , trapped pouches
    0x0E75: [0x0026, 0x0021], # backpack red , salvage backpack
    0x0EFA: [0x0461], # runebook
    0x097B: [0x0825], # mana steak
}

#//========================================================================

def debug_message(msg, hue=1153):
    if not DEBUG_MODE:
        return
    try:
        Misc.SendMessage(str(msg), int(hue))
    except Exception:
        try:
            print(str(msg))
        except Exception:
            pass

def _format_hex4(val) -> str:
    try:
        numeric_value = int(val) & 0xFFFF
        return f"0x{numeric_value:04X}"
    except Exception:
        return str(val)

def get_item_name(item):
    """Best-effort item name using fast paths, then props as fallback."""
    try:
        item_name_attribute = getattr(item, 'Name', None)
        if item_name_attribute:
            item_name_string = str(item_name_attribute)
            return item_name_string
    except Exception:
        pass
    try:
        Items.WaitForProps(item.Serial, int(WAIT_PROPS_QUICK_MS))
        properties_list_quick = Items.GetPropStringList(item.Serial)
        if properties_list_quick and len(properties_list_quick) > 0:
            item_name_from_quick_properties = str(properties_list_quick[0])
            return item_name_from_quick_properties
        # Try a longer properties wait without clicking
        Items.WaitForProps(item.Serial, int(WAIT_PROPS_CLICK_MS))
        properties_list_extended = Items.GetPropStringList(item.Serial)
        if properties_list_extended and len(properties_list_extended) > 0:
            item_name_from_extended_properties = str(properties_list_extended[0])
            return item_name_from_extended_properties
        item_name_from_property_index_zero = Items.GetPropValue(item.Serial, 0)
        if item_name_from_property_index_zero:
            item_name_string_from_index = str(item_name_from_property_index_zero)
            return item_name_string_from_index
    except Exception:
        pass
    return "Unknown"

def get_properties(item, max_search=16):
    """Collect a list of property strings, trying multiple methods."""
    collected = []
    try:
        serial = item.Serial
        # Quick
        try:
            Items.WaitForProps(serial, int(WAIT_PROPS_QUICK_MS))
            properties_list = Items.GetPropStringList(serial)
            if properties_list:
                collected += [str(prop) for prop in properties_list if prop]
        except Exception:
            pass
        # Longer wait without clicking
        try:
            Items.WaitForProps(serial, int(WAIT_PROPS_CLICK_MS))
            properties_list = Items.GetPropStringList(serial)
            if properties_list:
                for property_string in properties_list:
                    property_string = str(property_string)
                    if property_string and property_string not in collected:
                        collected.append(property_string)
        except Exception:
            pass
        # Index
        try:
            for idx in range(0, max_search):
                property_value = None
                try:
                    property_value = Items.GetPropValue(serial, idx)
                except Exception:
                    property_value = None
                if not property_value:
                    break
                property_string = str(property_value)
                if property_string and property_string not in collected:
                    collected.append(property_string)
        except Exception:
            pass
    except Exception:
        pass
    return collected

def _normalize_name(name_string: str) -> str:
    try:
        return (name_string or '').strip().lower()
    except Exception:
        return str(name_string).strip().lower()

def _standardize_tier(tier: str) -> str:
    """Map external tier names into our internal RARITY_ORDER values."""
    tier_normalized = (tier or '').strip().lower()
    if tier_normalized == 'common':
        tier_normalized = 'uncommon'
    if tier_normalized in RARITY_ORDER:
        return tier_normalized
    return 'uncommon'

def build_specific_items_index() -> dict:
    """Build a lookup dict: (name_norm, item_id, hue) -> tier."""
    index_dict = {}
    for item_tuple in SPECIFIC_ITEMS:
        try:
            # name, item_id, hue, rarity
            item_name, item_id, item_hue, item_tier = item_tuple
            key = (_normalize_name(item_name), int(item_id), int(item_hue))
            index_dict[key] = _standardize_tier(item_tier)
        except Exception:
            continue
    debug_message(f"SPECIFIC_ITEMS index built: {len(index_dict)} entries")
    return index_dict

def _ensure_ratings_file():
    """Ensure the ratings JSON file and directory exist."""
    try:
        directory_path = os.path.dirname(USER_RATINGS_FILE)
        if directory_path and not os.path.isdir(directory_path):
            os.makedirs(directory_path, exist_ok=True)
            debug_message(f"Created ratings dir: {directory_path}")
        if not os.path.exists(USER_RATINGS_FILE):
            # Create empty ratings structure
            initial_data = {
                "_metadata": {
                    "version": "1.0",
                    "created": time.time(),
                    "description": "User item ratings with full history. Each item key maps to current_tier and history array."
                },
                "ratings": {}
            }
            with open(USER_RATINGS_FILE, 'w', encoding='utf-8') as ratings_file:
                json.dump(initial_data, ratings_file, indent=2)
            debug_message(f"Created ratings file: {USER_RATINGS_FILE}")
    except Exception as init_error:
        try:
            Misc.SendMessage(f"Ratings file init failed: {init_error}", 33)
        except Exception:
            pass

def _make_item_key(name: str, item_id: int, hue: int) -> str:
    """Create a unique key for an item based on normalized name, item_id, and hue."""
    name_normalized = _normalize_name(name)
    return f"{name_normalized}|{item_id}|{hue}"

def _load_user_ratings() -> dict:
    """Load user ratings from JSON file. Returns the ratings dict."""
    try:
        _ensure_ratings_file()
        with open(USER_RATINGS_FILE, 'r', encoding='utf-8') as ratings_file:
            data = json.load(ratings_file)
        return data.get('ratings', {})
    except Exception as load_error:
        debug_message(f"Failed to load user ratings: {load_error}", 33)
        return {}

def _save_user_ratings(ratings: dict):
    """Save user ratings to JSON file."""
    try:
        _ensure_ratings_file()
        # Load existing data to preserve metadata
        try:
            with open(USER_RATINGS_FILE, 'r', encoding='utf-8') as ratings_file:
                data = json.load(ratings_file)
        except Exception:
            data = {}
        
        # Update metadata
        if '_metadata' not in data:
            data['_metadata'] = {}
        data['_metadata']['version'] = '1.0'
        data['_metadata']['last_updated'] = time.time()
        data['ratings'] = ratings
        
        # Write atomically using temp file
        temp_file = USER_RATINGS_FILE + '.tmp'
        with open(temp_file, 'w', encoding='utf-8') as temp_ratings_file:
            json.dump(data, temp_ratings_file, indent=2)
        
        # Replace original file
        if os.path.exists(USER_RATINGS_FILE):
            os.remove(USER_RATINGS_FILE)
        os.rename(temp_file, USER_RATINGS_FILE)
        
        debug_message(f"Saved user ratings: {len(ratings)} items")
    except Exception as save_error:
        try:
            Misc.SendMessage(f"Failed to save ratings: {save_error}", 33)
        except Exception:
            pass

def _get_tier_index(tier: str) -> int:
    """Get numeric index for tier (lower is better). Returns 999 for unknown."""
    tier_map = {'legendary': 0, 'epic': 1, 'rare': 2, 'uncommon': 3, 'common': 4}
    return tier_map.get(tier, 999)

def _apply_rating_action(current_tier: str, action: str) -> str:
    """Apply up/down action to current tier and return new tier."""
    current_idx = _get_tier_index(current_tier)
    if action == 'up':
        # Move up one tier (lower index)
        new_idx = max(0, current_idx - 1)
    elif action == 'down':
        # Move down one tier (higher index)
        new_idx = min(4, current_idx + 1)  # 4 = common
    else:
        return current_tier
    
    # Map back to tier name
    idx_to_tier = {0: 'legendary', 1: 'epic', 2: 'rare', 3: 'uncommon', 4: 'common'}
    return idx_to_tier.get(new_idx, current_tier)

def _export_csv_action(name: str, item_id: int, hue: int, action: str, from_tier: str, to_tier: str):
    """Export a single rating action to CSV file (append mode)."""
    if not EXPORT_CSV_LOG:
        return
    try:
        # Ensure directory exists
        directory_path = os.path.dirname(CSV_EXPORT_FILE)
        if directory_path and not os.path.isdir(directory_path):
            os.makedirs(directory_path, exist_ok=True)
        
        # Create header if file doesn't exist
        if not os.path.exists(CSV_EXPORT_FILE):
            with open(CSV_EXPORT_FILE, 'w', encoding='utf-8') as csv_file:
                csv_file.write('timestamp,name,item_id,hue,action,from_tier,to_tier\n')
        
        # Append action
        timestamp = time.time()
        name_sanitized = str(name).replace('\n', ' ').replace(',', ';')
        with open(CSV_EXPORT_FILE, 'a', encoding='utf-8') as csv_file:
            csv_file.write(f'{timestamp},{name_sanitized},{item_id},{hue},{action},{from_tier},{to_tier}\n')
        
        debug_message(f"CSV export: {name_sanitized} {action} {from_tier}->{to_tier}")
    except Exception as export_error:
        debug_message(f"CSV export failed: {export_error}", 33)

def _export_python_dictionary():
    """Export all current ratings as Python dict code for pasting into script."""
    if not EXPORT_PYTHON_DICTIONARY:
        return
    try:
        global _USER_RATINGS_CACHE
        if _USER_RATINGS_CACHE is None:
            _USER_RATINGS_CACHE = _load_user_ratings()
        
        if not _USER_RATINGS_CACHE:
            debug_message("No ratings to export as Python code")
            return
        
        # Organize by tier
        by_tier = {'legendary': [], 'epic': [], 'rare': [], 'uncommon': [], 'common': []}
        for item_key, rating_data in _USER_RATINGS_CACHE.items():
            tier = rating_data.get('current_tier', 'uncommon')
            name = rating_data.get('name', '')
            item_id = int(rating_data.get('item_id', 0))
            hue = int(rating_data.get('hue', 0))
            
            if tier in by_tier:
                by_tier[tier].append((name, item_id, hue))
        
        # Generate Python dictionary
        lines = []
        lines.append('# Generated from user ratings on ' + str(time.time()))
        lines.append('# Copy and paste these into your script to set default ratings for updated base script\n')
        
        for tier in ['legendary', 'epic', 'rare', 'uncommon', 'common']:
            items = by_tier[tier]
            if not items:
                continue
            
            var_name = tier.upper() + '_ITEMS'
            lines.append(f'{var_name} = [')
            
            for name, item_id, hue in sorted(items, key=lambda x: (x[0].lower(), x[1], x[2])):
                # Format with proper padding for readability
                name_padded = f'"{name}"'.ljust(45)
                item_id_hex = f'0x{item_id:04X}'
                hue_hex = f'0x{hue:04X}'
                comment = f'# {item_id}, {hue}'
                lines.append(f'    ({name_padded}, {item_id_hex}, {hue_hex}),  {comment}')
            
            lines.append(']\n')
        
        # Write to file
        directory_path = os.path.dirname(PYTHON_CODE_EXPORT_FILE)
        if directory_path and not os.path.isdir(directory_path):
            os.makedirs(directory_path, exist_ok=True)
        
        with open(PYTHON_CODE_EXPORT_FILE, 'w', encoding='utf-8') as python_file:
            python_file.write('\n'.join(lines))
        
        try:
            Misc.SendMessage(f"Python code exported to: {os.path.basename(PYTHON_CODE_EXPORT_FILE)}", 68)
        except Exception:
            pass
        
        debug_message(f"Python code export complete: {len(_USER_RATINGS_CACHE)} items")
        
    except Exception as export_error:
        try:
            Misc.SendMessage(f"Python export failed: {export_error}", 33)
        except Exception:
            pass

def _export_loot_to_json(tiers_map: dict):
    """Export current loot summary to JSON file."""
    try:
        # Ensure directory exists
        parent_directory = os.path.dirname(_DATA_DIR)
        if not os.path.isdir(_DATA_DIR):
            os.makedirs(_DATA_DIR, exist_ok=True)
        
        # Build export data structure
        export_data = {
            "_metadata": {
                "script": "UI_loot_item_summary.py",
                "version": "20251015",
                "timestamp": time.time(),
                "player_name": Player.Name
            },
            "loot_summary": {}
        }
        
        # Organize items by tier
        for tier in RARITY_ORDER:
            items = tiers_map.get(tier, [])
            if not items:
                continue
            
            export_data["loot_summary"][tier] = []
            for item_data in items:
                item_entry = {
                    "name": item_data.get('name', ''),
                    "item_id": item_data.get('item_id', 0),
                    "item_id_hex": hex(item_data.get('item_id', 0)),
                    "hue": item_data.get('hue', 0),
                    "hue_hex": hex(item_data.get('hue', 0)),
                    "serial": item_data.get('serial', 0),
                    "detail": item_data.get('detail', '')
                }
                export_data["loot_summary"][tier].append(item_entry)
        
        # Generate filename with timestamp
        timestamp_str = str(int(time.time()))
        player_name = Player.Name
        # Sanitize player name for filename
        safe_name = "".join(c for c in player_name if c.isalnum() or c in (' ', '_', '-')).strip()
        safe_name = safe_name.replace(' ', '_')
        
        filename = f"loot_summary_{safe_name}_{timestamp_str}.json"
        filepath = os.path.join(_DATA_DIR, filename)
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as json_file:
            json.dump(export_data, json_file, indent=2)
        
        # User feedback
        try:
            Misc.SendMessage(f"Loot exported to: {filename}", 68)
        except Exception:
            pass
        
        debug_message(f"Loot export complete: {filepath}")
        
    except Exception as export_error:
        try:
            Misc.SendMessage(f"Loot export failed: {export_error}", 33)
        except Exception:
            pass
        debug_message(f"Loot export error: {export_error}", 33)

def _record_user_rating(entry: dict):
    """Record a user rating action with history"""
    global _USER_RATINGS_CACHE
    try:
        name = str(entry.get('name', ''))
        item_id = int(entry.get('item_id', 0))
        hue = int(entry.get('hue', 0))
        current_category = str(entry.get('category', ''))
        action = str(entry.get('action', ''))
        
        # Load ratings if not cached
        if _USER_RATINGS_CACHE is None:
            _USER_RATINGS_CACHE = _load_user_ratings()
        
        # Create item key
        item_key = _make_item_key(name, item_id, hue)
        
        # Get or create rating entry
        if item_key not in _USER_RATINGS_CACHE:
            _USER_RATINGS_CACHE[item_key] = {
                "name": name,
                "item_id": item_id,
                "hue": hue,
                "current_tier": current_category,
                "history": []
            }
        
        rating_entry = _USER_RATINGS_CACHE[item_key]
        
        # Calculate new tier based on action
        old_tier = rating_entry.get('current_tier', current_category)
        new_tier = _apply_rating_action(old_tier, action)
        
        # Record history entry
        history_entry = {
            "timestamp": time.time(),
            "action": action,
            "from_tier": old_tier,
            "to_tier": new_tier
        }
        rating_entry['history'].append(history_entry)
        rating_entry['current_tier'] = new_tier
        
        # Save to disk
        _save_user_ratings(_USER_RATINGS_CACHE)
        
        # Export to CSV if enabled
        _export_csv_action(name, item_id, hue, action, old_tier, new_tier)
        
        # Export Python code if enabled
        _export_python_dictionary()
        
        # User feedback
        try:
            Misc.SendMessage(f"Rated {action}: {name} ({hex(item_id)}) {old_tier} → {new_tier}", 63)
        except Exception:
            pass
        
        debug_message(f"Recorded rating: {item_key} {old_tier} → {new_tier} (action={action})")
        
    except Exception as e:
        try:
            Misc.SendMessage(f"Failed to record rating: {e}", 33)
        except Exception:
            pass

def ensure_specific_items_index():
    global _SPECIFIC_ITEMS_INDEX, _SPECIFIC_FP
    # Fingerprint current SPECIFIC_ITEMS so edits during runtime trigger rebuild
    try:
        fingerprint = hash(repr(SPECIFIC_ITEMS))
    except Exception:
        fingerprint = None
    if _SPECIFIC_ITEMS_INDEX is None or (_SPECIFIC_FP is not None and fingerprint is not None and fingerprint != _SPECIFIC_FP):
        try:
            _SPECIFIC_ITEMS_INDEX = build_specific_items_index()
            _SPECIFIC_FP = fingerprint
        except Exception as index_error:
            debug_message(f"Failed building SPECIFIC_ITEMS index: {index_error}", 33)

def get_specific_override_tier(name: str, item_id: int, hue: int) -> str:
    """Return the override tier if this item triple is in SPECIFIC_ITEMS, else ''."""
    try:
        ensure_specific_items_index()
        key = (_normalize_name(name), int(item_id), int(hue))
        return _SPECIFIC_ITEMS_INDEX.get(key, '')
    except Exception:
        return ''

def get_user_rating_tier(name: str, item_id: int, hue: int) -> str:
    """Return the user's rated tier for this item, or '' if no rating exists."""
    global _USER_RATINGS_CACHE
    try:
        # Load ratings if not cached
        if _USER_RATINGS_CACHE is None:
            _USER_RATINGS_CACHE = _load_user_ratings()
        
        item_key = _make_item_key(name, item_id, hue)
        rating_entry = _USER_RATINGS_CACHE.get(item_key)
        
        if rating_entry:
            tier = rating_entry.get('current_tier', '')
            debug_message(f"User rating found: {name} ({hex(item_id)}) → {tier}")
            return tier
        
        return ''
    except Exception as rating_error:
        debug_message(f"Failed to get user rating: {rating_error}", 33)
        return ''

#//========================================================================

class ClassResult(object):
    __slots__ = ("tier", "reason", "detail", "matched_mods")
    def __init__(self, tier: str, reason: str, detail: str = "", matched_mods=None):
        self.tier = tier
        self.reason = reason
        self.detail = detail
        self.matched_mods = matched_mods or []

def _contains_any(text: str, words: list) -> str:
    text_lowercase = (text or '').lower()
    for word in words:
        if word in text_lowercase:
            return word
    return ""

def _collect_matches(text: str, words: list) -> list:
    text_lowercase = (text or '').lower()
    found_matches = []
    for word in words:
        if word in text_lowercase:
            found_matches.append(word)
    return found_matches

def _is_excluded(item_id: int, hue: int) -> bool:
    try:
        item_id_int = int(item_id)
        hue_int = int(hue)
    except Exception:
        return False
    excluded_hues = EXCLUDE_ITEMS_BY_HUE.get(item_id_int)
    if not excluded_hues:
        return False
    return hue_int in excluded_hues

def _is_common_item(name: str, item_id: int, hue: int) -> bool:
    """Check if an item is in COMMON_ITEMS and should be excluded from display."""
    try:
        name_normalized = _normalize_name(name)
        item_id_int = int(item_id)
        hue_int = int(hue)
        for common_name, common_id, common_hue in COMMON_ITEMS:
            if name_normalized == _normalize_name(common_name) and item_id_int == int(common_id) and hue_int == int(common_hue):
                return True
    except Exception:
        pass
    return False

def classify_item(item, name: str, props: list) -> ClassResult:
    """Return ClassResult if the item is considered good, else None.
    Priority order maps to highest shown tier first.
    """
    try:
        item_id = int(item.ItemID)
    except Exception:
        item_id = getattr(item, 'ItemID', 0)
    hue = getattr(item, 'Hue', 0)
    name_low = (name or '').lower()
    props_low = [str(p).lower() for p in (props or [])]
    combined = name_low + "\n" + "\n".join(props_low)

    # Exclusions first: if this ItemID+Hue is configured to be ignored
    if _is_excluded(item_id, hue):
        return None
    
    # Exclude instruments - they have "slaying" property but shouldn't be ranked high
    if int(item_id) in INSTRUMENT_ITEM_IDS:
        return None

    # 1) Legendary: known artifacts by name, Power Scrolls, or top-tier vanquishing + slayer
    if name in KNOWN_ARTIFACT_WEAPON_NAMES:
        return ClassResult('legendary', 'Artifact', 'Artifact Weapon', matched_mods=[])
    # Power Scrolls outrank Enhancement Scrolls
    if _contains_any(combined, POWERSCROLL_NAME_PATTERNS):
        return ClassResult('legendary', 'Power Scroll', 'Power Scroll', matched_mods=[])
    # Vanquishing + slayer combo (both must actually be present)
    dmg_matches = _collect_matches(combined, GOOD_MODIFIERS['weapon']['damage'])
    slayer_matches = _collect_matches(combined, GOOD_MODIFIERS['slayer'])
    if dmg_matches and slayer_matches:
        return ClassResult('legendary', 'Vanquishing + Slayer', '', matched_mods=list(set([match.title() for match in dmg_matches + slayer_matches])))

    # 2) Epic: Enhancement Scrolls, strong slayer weapons or strong armor mods
    if int(item_id) == ENHANCEMENT_SCROLL_ITEMID:
        # Include the actual enhancement lines from properties so users can see what it does
        enhancement_lines = []
        try:
            for property_item in (props or []):
                property_string = str(property_item).strip()
                property_lowercase = property_string.lower()
                if not property_string:
                    continue
                # Heuristics to include meaningful enhancement info and avoid generic name lines
                if 'enhanc' in property_lowercase or 'by +' in property_lowercase or '%'+'' in property_string or 'protection' in property_lowercase or 'summon' in property_lowercase or 'damage' in property_lowercase or 'chance' in property_lowercase:
                    enhancement_lines.append(property_string)
        except Exception:
            pass
        return ClassResult('epic', 'Enhancement Scroll', '', matched_mods=enhancement_lines)
    if slayer_matches:
        return ClassResult('epic', 'Slayer', '', matched_mods=[match.title() for match in slayer_matches])
    armor_matches = _collect_matches(combined, GOOD_MODIFIERS['armor'])
    if armor_matches:
        # show the exact matched armor tier(s), do not substitute with a different tier
        return ClassResult('epic', 'Armor', '', matched_mods=[match.title() for match in armor_matches])

    # 3) Rare: top weapon mods or rare materials
    if dmg_matches:
        return ClassResult('rare', 'Weapon Damage', '', matched_mods=[match.title() for match in dmg_matches])
    # Accuracy tier as rare if desired
    acc_matches = _collect_matches(combined, GOOD_MODIFIERS['weapon']['accuracy'])
    if acc_matches:
        return ClassResult('rare', 'Accuracy', '', matched_mods=[match.title() for match in acc_matches])
    if int(item_id) in ENCHANTING_MATERIAL_IDS:
        return ClassResult('rare', 'Rare Material', 'Material')
    # Treasure Maps
    if int(item_id) == TREASURE_MAP_ITEMID:
        return ClassResult('rare', 'Treasure Map', 'Treasure Map')

    # 4) Uncommon: Currently nothing explicit; rely on hue fallback below

    # Fallback inclusion: any item with a non-default hue (hue != 0)
    try:
        if int(hue) != 0:
            return ClassResult('uncommon', 'Colored Item', f"Hue {_format_hex4(hue)}", matched_mods=[])
    except Exception:
        if hue and hue != 0:
            return ClassResult('uncommon', 'Colored Item', f"Hue {hue}", matched_mods=[])

    return None

#//=============== Collect backpack items and filter

def collect_good_items_from_backpack(max_items_per_tier=100):
    """Search backpack, classify items, and return dict tier -> list of dicts for UI."""
    if not Player.Backpack:
        Misc.SendMessage("No backpack found!", 33)
        return {}

    items = Items.FindBySerial(Player.Backpack.Serial).Contains
    items = list(items) if items else []

    tiers = {tier_key: [] for tier_key in RARITY_ORDER}

    def _format_detail_from_classresult(class_result: ClassResult) -> str:
        # Prefer the actual matched modifiers exactly as found
        if class_result and getattr(class_result, 'matched_mods', None):
            try:
                # Join and keep original capitalization already applied
                return ", ".join([str(modifier) for modifier in class_result.matched_mods if modifier])
            except Exception:
                pass
        # Otherwise show explicit detail if provided, else the reason label
        if class_result and class_result.detail:
            return str(class_result.detail)
        if class_result and class_result.reason:
            return str(class_result.reason)
        return ""

    for item in items:
        try:
            item_name = get_item_name(item)
            item_properties = get_properties(item)
            classification = classify_item(item, item_name, item_properties)
            if not classification:
                continue
            # Apply SPECIFIC_ITEMS override if present
            try:
                current_hue = int(getattr(item, 'Hue', 0))
                current_item_id = int(item.ItemID)
                
                # CRITICAL: Exclude items explicitly marked as COMMON
                if _is_common_item(item_name, current_item_id, current_hue):
                    debug_message(f"Excluding COMMON item: '{item_name}' id={hex(current_item_id)} hue={hex(current_hue)}")
                    continue
                
                # Priority 1: User ratings (highest priority - user's explicit choices)
                user_tier = get_user_rating_tier(item_name, current_item_id, current_hue)
                if user_tier:
                    # If user rated as 'common', exclude the item entirely
                    if user_tier == 'common':
                        debug_message(f"Excluding item with 'common' user rating: '{item_name}' id={hex(current_item_id)} hue={hex(current_hue)}")
                        continue
                    # Apply user rating if it's a valid display tier
                    if user_tier in RARITY_ORDER and user_tier != classification.tier:
                        debug_message(f"User rating applied: '{item_name}' id={hex(current_item_id)} hue={hex(current_hue)} {classification.tier} -> {user_tier}")
                        classification.tier = user_tier
                # Priority 2: SPECIFIC_ITEMS override (script-defined overrides)
                elif True:  # Use elif to ensure user ratings take precedence
                    override_tier = get_specific_override_tier(item_name, current_item_id, current_hue)
                    if override_tier:
                        # If override tier is 'common', exclude the item entirely
                        if override_tier == 'common':
                            debug_message(f"Excluding item with 'common' override: '{item_name}' id={hex(current_item_id)} hue={hex(current_hue)}")
                            continue
                        # Otherwise apply the override if it's a valid display tier
                        if override_tier in RARITY_ORDER and override_tier != classification.tier:
                            debug_message(f"Override tier: '{item_name}' id={hex(current_item_id)} hue={hex(current_hue)} {classification.tier} -> {override_tier}")
                            classification.tier = override_tier
                    elif _normalize_name(item_name) in _SPECIFIC_NAMES:
                        # Helpful diagnostic: we expected an override name but the (id,hue) didn't match
                        debug_message(f"No SPECIFIC_ITEMS match for '{item_name}' with id={hex(current_item_id)} hue={hex(current_hue)}")
            except Exception:
                pass
            tile = {
                'serial': int(item.Serial),
                'item_id': int(item.ItemID),
                'hue': int(getattr(item, 'Hue', 0)),
                'name': item_name,
                'detail': _format_detail_from_classresult(classification),
            }
            tier_items_list = tiers.get(classification.tier)
            if tier_items_list is not None and len(tier_items_list) < max_items_per_tier:
                tier_items_list.append(tile)
        except Exception:
            continue
        # throttle a little to avoid spam
        try:
            Misc.Pause(int(SEARCH_THROTTLE_MS))
        except Exception:
            time.sleep(SEARCH_THROTTLE_MS / 1000.0)

    return {tier_key: tier_items for tier_key, tier_items in tiers.items() if tier_items}

#//=============== UI Rendering

def _measure_rows(tiers_map: dict) -> list:
    """Return a list of section dicts with layout metrics for rendering rows."""
    sections = []
    def _tier_tile_metrics(tier: str):
        if tier == 'legendary':
            return LEGENDARY_TILE_WIDTH, TILE_HEIGHT, LEGENDARY_TILE_GAP_X, LEGENDARY_TILE_TEXT_HEIGHT
        return TILE_WIDTH, TILE_HEIGHT, TILE_GAP_X, TILE_TEXT_HEIGHT
    for tier in RARITY_ORDER:
        tiles = tiers_map.get(tier)
        if not tiles:
            continue
        count = len(tiles)
        cols = min(MAX_COLS, max(1, count))
        tile_w, tile_h, gap_x, text_h = _tier_tile_metrics(tier)
        rows = (count + cols - 1) // cols
        width = OUTER_PADDING*2 + cols*tile_w + (cols-1)*gap_x
        height = OUTER_PADDING*2 + SECTION_HEADER_HEIGHT + rows*tile_h + (rows-1)*TILE_GAP_Y
        sections.append({
            'tier': tier,
            'title': RARITY_TITLES.get(tier, tier.title()),
            'count': count,
            'cols': cols,
            'rows': rows,
            'width': width,
            'height': height,
            'tiles': tiles,
            'tile_w': tile_w,
            'tile_h': tile_h,
            'gap_x': gap_x,
            'text_h': text_h,
        })
    return sections

def _html_name_line(tier: str, name: str, detail: str) -> str:
    color = NAME_TIER_HTML.get(tier, '#CCCCCC')
    name_html = f"<basefont color={color}>{name}</basefont>"
    if detail:
        return f"<center>{name_html}<br/><basefont color=#AAAAAA>{detail}</basefont></center>"
    return f"<center>{name_html}</center>"

def _tier_header_hue(tier: str) -> int:
    if tier == 'legendary':
        return COLORS['legendary_orange']
    if tier == 'epic':
        return COLORS['epic_purple']
    if tier == 'rare':
        return COLORS['rare_blue']
    return COLORS['ok']

def render_summary_gump(tiers_map: dict):
    global _BUTTON_ACTIONS, _NEXT_BUTTON_ID
    if not tiers_map:
        Misc.SendMessage("No good items found.", 53)
        return

    rarity_sections_layout = _measure_rows(tiers_map)
    if not rarity_sections_layout:
        Misc.SendMessage("No good items found.", 53)
        return

    # Overall gump size is max width of sections and sum of heights + gaps
    gump_total_width = max(section_data['width'] for section_data in rarity_sections_layout)
    gump_total_height = RESULTS_TITLE_HEIGHT + sum(section_data['height'] for section_data in rarity_sections_layout) + SECTION_GAP*(len(rarity_sections_layout)-1) + EXPORT_BUTTON_HEIGHT + EXPORT_BUTTON_MARGIN

    # reset button mappings each render (only needed if buttons are enabled)
    if RANKING_BUTTONS_ENABLED:
        _BUTTON_ACTIONS = {}
        _NEXT_BUTTON_ID = RANK_BUTTON_BASE_ID
    debug_message(f"Rendering summary gump. User ratings file: {USER_RATINGS_FILE}")
    debug_message(f"Sections to render: {len(rarity_sections_layout)}")

    gump_definition = Gumps.CreateGump(movable=True)
    Gumps.AddPage(gump_definition, 0)

    # Background + alpha
    Gumps.AddBackground(gump_definition, 0, 0, gump_total_width, gump_total_height, 30546)
    Gumps.AddAlphaRegion(gump_definition, 0, 0, gump_total_width, gump_total_height)

    # Title bar (draggable background area with only a label on top)
    try:
        Gumps.AddHtml(gump_definition, 8, 2, gump_total_width-16, RESULTS_TITLE_HEIGHT-2,
                      f"<center><basefont color=#3FA9FF>{RESULTS_TITLE_TEXT}</basefont></center>", 0, 0)
    except Exception:
        pass

    current_vertical_position = RESULTS_TITLE_HEIGHT
    for section_data in rarity_sections_layout:
        # Section header
        section_horizontal_position = max(0, (gump_total_width - section_data['width']) // 2)
        Gumps.AddLabel(gump_definition, section_horizontal_position + OUTER_PADDING, current_vertical_position + 2, _tier_header_hue(section_data['tier']), f"{section_data['title']} ({section_data['count']})")

        # Tile grid origin
        tile_grid_vertical_position = current_vertical_position + OUTER_PADDING + SECTION_HEADER_HEIGHT
        section_content_width = section_data['width'] - 2*OUTER_PADDING

        # Render tiles centered per row
        total_items_in_section = section_data['count']
        columns_per_row = section_data['cols']
        total_rows_in_section = section_data['rows']
        item_tiles_list = section_data['tiles']
        item_index = 0
        for row_index in range(total_rows_in_section):
            row_start_item_index = row_index * columns_per_row
            row_end_item_index = min(row_start_item_index + columns_per_row, total_items_in_section)
            items_count_in_current_row = max(0, row_end_item_index - row_start_item_index)
            if items_count_in_current_row <= 0:
                continue
            # Use per-tier tile metrics
            tile_width_pixels = section_data.get('tile_w', TILE_WIDTH)
            tile_height_pixels = section_data.get('tile_h', TILE_HEIGHT)
            tile_horizontal_gap_pixels = section_data.get('gap_x', TILE_GAP_X)
            tile_text_height_pixels = section_data.get('text_h', TILE_TEXT_HEIGHT)
            current_row_total_width = items_count_in_current_row * tile_width_pixels + (items_count_in_current_row - 1) * tile_horizontal_gap_pixels
            row_origin_horizontal_position = section_horizontal_position + OUTER_PADDING + max(0, (section_content_width - current_row_total_width) // 2)
            item_tile_vertical_position = tile_grid_vertical_position + row_index * (tile_height_pixels + TILE_GAP_Y)
            for column_index in range(items_count_in_current_row):
                current_tile_data = item_tiles_list[row_start_item_index + column_index]
                tile_horizontal_position = row_origin_horizontal_position + column_index * (tile_width_pixels + tile_horizontal_gap_pixels)
                # Item icon - offset left 10px and up 5px
                icon_x_offset = tile_horizontal_position + tile_width_pixels//2 - 10
                icon_y_offset = item_tile_vertical_position + TILE_ICON_Y_OFFSET - 5
                try:
                    Gumps.AddItem(gump_definition, icon_x_offset, icon_y_offset, int(current_tile_data['item_id']), int(current_tile_data['hue']))
                except Exception:
                    try:
                        Gumps.AddItem(gump_definition, icon_x_offset, icon_y_offset, int(current_tile_data['item_id']))
                    except Exception:
                        pass
                # Name + detail
                item_html_formatted_text = _html_name_line(section_data['tier'], current_tile_data.get('name', ''), current_tile_data.get('detail', ''))
                Gumps.AddHtml(gump_definition, tile_horizontal_position, item_tile_vertical_position + TILE_TEXT_Y_OFFSET, tile_width_pixels, tile_text_height_pixels, item_html_formatted_text, 0, 0)

                # Up/Down ranking buttons at bottom of tile (optional)
                if RANKING_BUTTONS_ENABLED:
                    try:
                        # Compute positions - raised up 20 pixels total, moved right 5px
                        ranking_button_vertical_position = item_tile_vertical_position + TILE_TEXT_Y_OFFSET + tile_text_height_pixels - 14 - 20
                        # Rank down button offset right by 12px (7px original + 5px adjustment)
                        rank_down_button_horizontal_position = tile_horizontal_position + tile_width_pixels - 22 + 12
                        rank_down_button_vertical_position = ranking_button_vertical_position
                        # Rank up button moves directly above, sharing the same X
                        rank_up_button_horizontal_position = rank_down_button_horizontal_position
                        rank_up_button_vertical_position = rank_down_button_vertical_position - 18

                        # Allocate button IDs
                        rank_up_button_id = _NEXT_BUTTON_ID; _NEXT_BUTTON_ID += 1
                        rank_down_button_id = _NEXT_BUTTON_ID; _NEXT_BUTTON_ID += 1

                        # Map actions
                        _BUTTON_ACTIONS[rank_up_button_id] = {
                            'name': current_tile_data.get('name', ''),
                            'item_id': current_tile_data.get('item_id', 0),
                            'hue': current_tile_data.get('hue', 0),
                            'serial': current_tile_data.get('serial', 0),
                            'category': section_data['tier'],
                            'action': 'up',
                        }
                        _BUTTON_ACTIONS[rank_down_button_id] = {
                            'name': current_tile_data.get('name', ''),
                            'item_id': current_tile_data.get('item_id', 0),
                            'hue': current_tile_data.get('hue', 0),
                            'serial': current_tile_data.get('serial', 0),
                            'category': section_data['tier'],
                            'action': 'down',
                        }
                        debug_message(f"Mapped buttons: up_id={rank_up_button_id}, down_id={rank_down_button_id} -> '{current_tile_data.get('name','')}', id={hex(int(current_tile_data.get('item_id',0)))}, hue={hex(int(current_tile_data.get('hue',0)))}, serial={int(current_tile_data.get('serial',0))}, tier={section_data['tier']}")

                        # Draw buttons (using small arrow gumps image ids)
                        # Up arrow (buttonID=up_id, page=1, quit=0) using gump #2436
                        Gumps.AddButton(gump_definition, rank_up_button_horizontal_position, rank_up_button_vertical_position, 2436, 2436, rank_up_button_id, 1, 0)
                        Gumps.AddTooltip(gump_definition, "Rank Up")
                        # Down arrow
                        Gumps.AddButton(gump_definition, rank_down_button_horizontal_position, rank_down_button_vertical_position, 2438, 2438, rank_down_button_id, 1, 0)
                        Gumps.AddTooltip(gump_definition, "Rank Down")
                    except Exception:
                        pass

        current_vertical_position += section_data['height'] + SECTION_GAP

    # Export button at bottom 
    export_button_y = current_vertical_position + EXPORT_BUTTON_MARGIN - 15
    export_button_width = 80
    export_button_height = 40
    export_button_x = (gump_total_width - export_button_width) // 2
    
    # Button
    Gumps.AddButton(gump_definition, export_button_x, export_button_y, 1, 1, EXPORT_BUTTON_ID, 1, 0)
    
    # Overlay
    if EXPORT_BUTTON_SLIVER_OVERLAY:
        Gumps.AddImageTiled(gump_definition, export_button_x, export_button_y, export_button_width, export_button_height, 2624)
    
    # Label - 
    label_text = "EXPORT"
    label_hue = 0x0385
    approx_char_px = 6
    text_x = export_button_x + (export_button_width // 2) - max(0, len(label_text)) * approx_char_px // 2
    text_y = export_button_y + (export_button_height // 2) - 7
    outline_color = 0
    offsets_r1 = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    offsets_r2 = [(-2, 0), (2, 0), (0, -2), (0, 2), (-2, -1), (-2, 1), (2, -1), (2, 1), (-1, -2), (1, -2), (-1, 2), (1, 2)]
    for dx, dy in offsets_r2:
        Gumps.AddLabel(gump_definition, text_x + dx, text_y + dy, outline_color, label_text)
    for dx, dy in offsets_r1:
        Gumps.AddLabel(gump_definition, text_x + dx, text_y + dy, outline_color, label_text)
    Gumps.AddLabel(gump_definition, text_x, text_y, label_hue, label_text)

    # Close button (top-right)
    # Close button (buttonID=0 closes by convention)
    Gumps.AddButton(gump_definition, gump_total_width-26, 4, 4017, 4018, 0, 1, 0)
    Gumps.AddTooltip(gump_definition, "Close")

    #  actually send the gump to the client
    debug_message(f"SendGump GUMP_ID={hex(GUMP_ID_RESULTS)} size=({gump_total_width}x{gump_total_height})")
    Gumps.SendGump(GUMP_ID_RESULTS, Player.Serial, GUMP_RESULTS_X, GUMP_RESULTS_Y, gump_definition.gumpDefinition, gump_definition.gumpStrings)

def show_and_interact_summary(tiers_map: dict):
    """Render the summary and process ranking button clicks until the gump closes."""
    # Close any existing results gump before showing new results
    try:
        Gumps.CloseGump(GUMP_ID_RESULTS)
        Misc.Pause(100)
    except Exception:
        pass
    
    # If ranking buttons are disabled, just render and exit (no interaction loop)
    if not RANKING_BUTTONS_ENABLED:
        render_summary_gump(tiers_map)
        return
    # Ensure ratings file exists early when buttons enabled
    try:
        _ensure_ratings_file()
    except Exception:
        pass
    render_summary_gump(tiers_map)
    while True:
        try:
            Gumps.WaitForGump(GUMP_ID_RESULTS, int(GUMP_WAIT_MS))
            gump_data = Gumps.GetGumpData(GUMP_ID_RESULTS)
        except Exception:
            gump_data = None
        if not gump_data:
            debug_message("Summary gump closed or not found; exiting interaction loop.")
            break
        button_id = getattr(gump_data, 'buttonid', 0)
        debug_message(f"Gump interaction: buttonid={button_id}")
        
        # Check for close button (buttonid=0)
        if button_id == 0:
            debug_message("Close button pressed; exiting interaction loop.")
            try:
                Gumps.CloseGump(GUMP_ID_RESULTS)
            except Exception:
                pass
            break
        
        button_action_entry = None
        if button_id and button_id > 0:
            # Check for export button
            if button_id == EXPORT_BUTTON_ID:
                debug_message("Export button pressed")
                _export_loot_to_json(tiers_map)
                # Re-render to keep gump open
                render_summary_gump(tiers_map)
            else:
                button_action_entry = _BUTTON_ACTIONS.get(int(button_id))
                if button_action_entry:
                    debug_message(f"Button match: {button_id} -> action={button_action_entry.get('action')} item={button_action_entry.get('name')} id={hex(int(button_action_entry.get('item_id',0)))}")
                    _record_user_rating(button_action_entry)
                # Re-render to reset button state and keep interaction going
                render_summary_gump(tiers_map)
        else:
            debug_message("No button pressed; waiting...")
        if button_id and button_id > 0 and not button_action_entry:
            debug_message(f"Button {button_id} not mapped. Mappings={len(_BUTTON_ACTIONS)} sample={(list(_BUTTON_ACTIONS.keys())[:4])}")
        try:
            Misc.Pause(int(GUMP_WAIT_MS))
        except Exception:
            time.sleep(GUMP_WAIT_MS / 1000.0)

#//=============== Launcher gump (persistent button)

def send_launcher_gump():
    gump_definition = Gumps.CreateGump(movable=True)
    Gumps.AddPage(gump_definition, 0)
    width, height = 75, 55
    Gumps.AddBackground(gump_definition, 0, 0, width, height, 30546)
    Gumps.AddAlphaRegion(gump_definition, 0, 0, width, height)
    try:
        Gumps.AddHtml(gump_definition, 3, 0, 68, 16, "<center><basefont color=#3FA9FF>LOOT</basefont></center>", 0, 0)
    except Exception:
        pass
    try:
        Gumps.AddItem(gump_definition, 32, 26, 0xBCA4)  # treasure chest icon
    except Exception:
        pass
    Gumps.AddButton(gump_definition, 5, 18, 9815, 9815, 1, 1, 0)
    Gumps.AddTooltip(gump_definition, "Show Good Loot Summary")
    Gumps.SendGump(GUMP_ID_LAUNCHER, Player.Serial, GUMP_LAUNCHER_X, GUMP_LAUNCHER_Y, gump_definition.gumpDefinition, gump_definition.gumpStrings)

def process_launcher_input():
    """Wait for launcher button click and trigger summary. Recreates gump if closed."""
    try:
        Gumps.WaitForGump(GUMP_ID_LAUNCHER, int(GUMP_WAIT_MS))
        launcher_gump_data = Gumps.GetGumpData(GUMP_ID_LAUNCHER)
    except Exception:
        launcher_gump_data = None
    
    if not launcher_gump_data:
        # Launcher gump was closed, recreate it
        send_launcher_gump()
        return
    
    if launcher_gump_data.buttonid > 0:
        # Trigger search and show results
        tiers_map = collect_good_items_from_backpack()
        show_and_interact_summary(tiers_map)
        # The gump remains open so user can press the button again later

#//=============== Entrypoint

def run_once():
    tiers_map = collect_good_items_from_backpack()
    show_and_interact_summary(tiers_map)

def run_persistent():
    """Show a persistent launcher button gump that triggers the summary on click."""
    send_launcher_gump()
    # WaitForGump in process_launcher_input handles all interactions
    # No loop needed - gump is static and doesn't require updates
    while Player.Connected:
        process_launcher_input()
        Misc.Pause(1000)  # Small pause to prevent CPU spinning

if __name__ == '__main__':
    # Start in persistent mode so you always have a button to click after fights
    # Unless LAUNCHER_UI_BUTTON is False, then skip launcher and show results immediately
    if LAUNCHER_UI_BUTTON:
        run_persistent()
    else:
        run_once()
