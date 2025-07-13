"""
ITEM Organizer Junk Salvager - a Razor Enhanced Python Script for Ultima Online

- Moves low tier items to a junk backpack based on Tier configuration
- Salvages items in the "junk" (red) backpack ( unchained )
- Configurable Tier reservations by their properties ( Vanquishing , Greater Slaying , Invulnerable )

Requirements:
- Any configured salvage tool in player's backpack ( tinker tools , or sewing kit )
- A red dyed backpack that will hold the salvagable items

VERSION::20250621
"""

import sys
import time
from System.Collections.Generic import List

# Global debug mode switch
DEBUG_MODE = False  # Set to True to enable debug/info messages
AUTO_SALVAGE = True      # Set to False to skip auto-salvaging (for debugging)

# Tier Reservation Configuration = DEFAULT is only saving TEIR 1 affixes
RESERVE_TIERS = {
    'TIER1': True,      # Set to True to reserve Tier 1 items
    'TIER2': False,      # Set to True to reserve Tier 2 items
    'MAGICAL': False    # Set to True to reserve other magical items
}

# Junk Backpack Configuration
JUNK_BACKPACK_ID = 0x0E75 # a backpack 
JUNK_BACKPACK_HUES = [0x0021, 0x0026, 0x002B]  # Range of red hues that are acceptable
JUNK_BACKPACK_SERIAL = 0  # Will be auto-set by find_junk_backpack()

# Item Type Configuration
WEAPON_TYPES = [
    0x0F49,  # Axe
    0x0F47,  # Battle Axe
    0x0F4B,  # Double Axe
    0x0F45,  # Executioner's Axe
    0x0F43,  # Hatchet
    0x13FB,  # Large Battle Axe
    0x0E86,  # Pickaxe
    0x1443,  # Two Handed Axe
    0x13B0,  # War Axe
    0x13F6,  # Butcher Knife
    0x0EC3,  # Cleaver
    0x0F52,  # Dagger
    0x0EC4,  # Skinning Knife
    0x13B4,  # Club
    0x143D,  # Hammer Pick
    0x0F5C,  # Mace
    0x0DF2,  # Magic Wand
    0x143B,  # Maul
    0x26BC,  # Scepter
    0x1439,  # War Hammer
    0x1407,  # War Mace
    0x0F4D,  # Bardiche
    0x143E,  # Halberd
    0x26BA,  # Scythe
    0x13B2,  # Bow
    0x13B1,  # Bow (Alternate)
    0x26C2,  # Composite Bow
    0x0F50,  # Crossbow
    0x13FD,  # Heavy Crossbow
    0x26C3,  # Repeating Crossbow
    0x2D1F,  # Magical Shortbow
    0x26BD,  # Bladed Staff
    0x26BF,  # Double Bladed Staff
    0x26BE,  # Pike
    0x0E87,  # Pitchfork
    0x1403,  # Short Spear
    0x0F62,  # Spear
    0x1405,  # War Fork
    0x0DF0,  # Black Staff
    0x13F8,  # Gnarled Staff
    0x0E89,  # Quarter Staff
    0x0E81,  # Shepherd's Crook
    0x26BB,  # Bone Harvester
    0x26C5,  # Bone Harvester (Alternate)
    0x0F5E,  # Broadsword
    0x26C1,  # Crescent Blade
    0x1441,  # Cutlass
    0x13FF,  # Katana
    0x1401,  # Kryss
    0x1400,  # Kryss (Alternate)
    0x26C0,  # Lance
    0x0F61,  # Longsword
    0x13B6,  # Scimitar
    0x13B9,  # Viking Sword
    0x27A8,  # Bokuto
    0x27A9,  # Daisho
    0x27AD,  # Kama
    0x27A7,  # Lajatang
    0x27A2,  # No-Dachi
    0x27AE,  # Nunchaku
    0x27AF,  # Sai
    0x27AB,  # Tekagi
    0x27A3,  # Tessen
    0x27A6,  # Tetsubo
    0x27A4,  # Wakizashi
    0x27A5,  # Yumi
    0x2D21,  # Assassin Spike
    0x2D24,  # Diamond Mace
    0x2D1E,  # Elven Composite Longbow
    0x2D35,  # Elven Machete
    0x2D20,  # Elven Spellblade
    0x2D22,  # Leafblade
    0x2D2B,  # Magical Shortbow (Alternate)
    0x2D28,  # Ornate Axe
    0x2D33,  # Radiant Scimitar
    0x2D32,  # Rune Blade
    0x2D2F,  # War Cleaver
    0x2D25,  # Wild Staff
    0x406B,  # Soul Glaive
    0x406C,  # Cyclone
    0x4067,  # Boomerang
    0x08FE,  # Bloodblade
    0x0903,  # Disc Mace
    0x090B,  # Dread Sword
    0x0904,  # Dual Pointed Spear
    0x08FD,  # Dual Short Axes
    0x48B2,  # Gargish Axe
    0x48B4,  # Gargish Bardiche
    0x48B0,  # Gargish Battle Axe
    0x48C6,  # Gargish Bone Harvester
    0x48B6,  # Gargish Butcher Knife
    0x48AE,  # Gargish Cleaver
    0x0902,  # Gargish Dagger
    0x48D0,  # Gargish Daisho
    0x48B8,  # Gargish Gnarled Staff
    0x48BA,  # Gargish Katana
    0x48BC,  # Gargish Kryss
    0x48CA,  # Gargish Lance
    0x48C2,  # Gargish Maul
    0x48C8,  # Gargish Pike
    0x48C4,  # Gargish Scythe
    0x0908,  # Gargish Talwar
    0x48CE,  # Gargish Tekagi
    0x48CC,  # Gargish Tessen
    0x48C0,  # Gargish War Hammer
    0x0905,  # Glass Staff
    0x090C,  # Glass Sword
    0x0906,  # Serpentstone Staff
    0x0907,  # Shortblade
    0x0900,  # Stone War Sword
]

SHIELD_TYPES = [
    0x1B72,  # Bronze Shield
    0x1B73,  # Buckler
    0x1B74,  # Metal Kite Shield
    0x1B75,  # Shield
    0x1B76,  # Heater Shield
    0x1B77,  # Shield
    0x1B78,  # Wooden Shield
    0x1B79,  # Shield
    0x1B7A,  # Wooden Kite Shield
    0x1B7B,  # Metal Shield
    0x1BC3,  # Chaos Shield
    0x1BC4,  # Order Shield
    0x1BC5,  # Shield
    0x4201,  # Shield
    0x4200,  # Shield
    0x4202,  # Shield
    0x4203,  # Shield
    0x4204,  # Shield
    0x4205,  # Shield
    0x4206,  # Shield
    0x4207,  # Shield
    0x4208,  # Shield
    0x4228,  # Shield
    0x4229,  # Shield
    0x422A,  # Shield
    0x422C,  # Shield
    0x7817,  # Shield
    0x7818,  # Shield
    0xA649,  # Shield
]

ARMOR_TYPES = [
    0x13BF,  # Chainmail Tunic
    0x13BE,  # Chainmail Leggings
    0x13BB,  # Chainmail Coif
    0x13C0,  # Ring Mail Tunic
    0x13C3,  # Ring Mail Sleeves
    0x13C4,  # Ring Mail Gloves
    0x13EC,  # Plate Mail Arms
    0x1415,  # Plate Mail Chest
    0x1411,  # Plate Mail Legs
    0x1414,  # Plate Mail Gorget
    0x1413,  # Plate Mail Gloves
    0x140A,  # Helmet
    0x140C,  # Bascinet
    0x140E,  # Norse Helm
    0x13C7,  # Studded Leather Gorget
    0x13DB,  # Studded Leather Tunic
    0x13D4,  # Studded Leather Sleeves
    0x13DA,  # Studded Leather Gloves
    0x13D6,  # Studded Leather Leggings
    0x1B72,  # Bone Armor
    0x1B7B,  # Bone Legs
    0x1B73,  # Bone Arms
    0x144E,  # Bone Arms
    0x1B7A,  # Bone Gloves
    0x1B79,  # Bone Helmet
    0x1450,  # Bone Gloves (Alternate)
    0x2779,  # Platemail Mempo
    0x1408,  # Close Helm
    0x13EE,  # Ringmail Sleeves
    0x13D5,  # Studded Gloves
    0x13CD,  # Leather Sleeves
    0x1412,  # Plate Helm
    0x13CB,  # Leather Leggings
    0x13F0,  # Ringmail Leggings
    0x144F,  # Bone Armor Chest
    0x13DC,  # Studded Sleeves
    0x1DB9,  # Leather Cap
    0x279D,  # Studded Mempo
    0x1C08,  # Leather Skirt
    0x1C06,  # Leather Armor (Female)
    0x13CC,  # Leather Tunic
    0x1410,  # Platemail Arms
    0x1452,  # Bone Leggings
    0x277A,  # Leather Mempo
    0x1C0C,  # Studded Bustier
    0x13C6,  # Leather Gloves
    0x1C04,  # Platemail Female
    0x1C00,  # Leather Shorts
    0x1C0A,  # LeatherBustier
    0x1C02,  # StuddedArmorF
    0x1451,  # BoneHelmet
    0x1452,  # BoneLeggings
    0x13EB,  # RingmailGloves
    0x1C02,  # StuddedArmorF
]

# Timing Configuration
MOVE_DELAY = 1000      # Delay between moving items (in milliseconds)
SCAN_DELAY = 100       # Delay between scanning items (in milliseconds)

# Salvage Tool Configuration 0x1EBC
SALVAGE_TOOLS = {
    "Tinker's Tools": {
        'id': 0x1EB8,
        'color': -1,
        'gump_id': 949095101,
        'salvage_action': 63,
        'priority': 1
    },
        "Tinker's ToolsB": {
        'id': 0x1EBC,
        'color': -1,
        'gump_id': 949095101,
        'salvage_action': 63,
        'priority': 1
    },
    "Sewing Kit": {
        'id': 0x0F9D,
        'color': -1,
        'gump_id': 949095101,
        'salvage_action': 63,
        'priority': 2
    }
}

def debug_message(message, color=68):
    """Send a debug/info message if DEBUG_MODE is enabled"""
    if DEBUG_MODE:
        Misc.SendMessage(f"[JunkSalvager] {message}", color)

class JunkSalvager:
    def __init__(self):
        # Tier definitions
        self.tier1_affixes = [
            "Vanquishing",    # +25 damage
            "Greater",        # Slaying +25%
            "Invulnerable"    # +100% armor
        ]
        
        self.tier2_affixes = [
            "Power",             # +20 damage
            "Supremely Accurate", # +25% Hit Chance
            "Fortification"      # +80% armor
        ]
        
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
            'other_items': 0,
            'items_moved': 0,
            'items_checked': 0
        }
        
        # Show current configuration
        self.show_config()
        
    def show_config(self):
        """Display current configuration settings"""
        debug_message("=== Configuration ===", self.colors['config'])
        debug_message(f"Reserve Tier 1 items: {'Yes' if RESERVE_TIERS['TIER1'] else 'No'}", self.colors['config'])
        debug_message(f"Reserve Tier 2 items: {'Yes' if RESERVE_TIERS['TIER2'] else 'No'}", self.colors['config'])
        debug_message(f"Reserve magical items: {'Yes' if RESERVE_TIERS['MAGICAL'] else 'No'}", self.colors['config'])
        debug_message(f"Move delay: {str(MOVE_DELAY)}ms", self.colors['config'])
        debug_message(f"Auto-salvage: {'Yes' if AUTO_SALVAGE else 'No'}", self.colors['config'])
        debug_message(f"Junk backpack serial: 0x{JUNK_BACKPACK_SERIAL:X}", self.colors['config'])
        debug_message("==================", self.colors['config'])
        
    def debug(self, message, color='info'):
        """Send debug message to client (deprecated, use debug_message instead)"""
        debug_message(str(message), self.colors[color] if isinstance(color, str) else color)
    
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
            self.debug(f"Error getting properties: {str(e)}", 'warning')
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
        return item.ItemID in WEAPON_TYPES or item.ItemID in ARMOR_TYPES or item.ItemID in SHIELD_TYPES

    def should_move_to_junk(self, item):
        """Determine if an item should be moved to junk backpack"""
        # First check if it's a weapon or armor
        if not self.is_salvageable_item(item):
            return False

        properties = self.get_item_properties(item)
        
        # Check tier 1
        if self.has_affix(properties, self.tier1_affixes):
            self.stats['tier1_items'] += 1
            return not RESERVE_TIERS['TIER1']
            
        # Check tier 2
        if self.has_affix(properties, self.tier2_affixes):
            self.stats['tier2_items'] += 1
            return not RESERVE_TIERS['TIER2']
            
        # Check other magical items
        if self.has_any_affix(properties):
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
            self.debug("No junk backpack serial configured!", 'warning')
            return False
            
        tool_name, tool, tool_config = self.find_salvage_tool()
        if not tool:
            self.debug("No salvage tool found!", 'warning')
            return False
            
        self.debug(f"Using {tool_name} to salvage junk backpack", 'info')
        
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
        dust = Items.FindByID(0x2DB4, -1, Player.Backpack.Serial)
        if dust:
            Items.UseItem(dust)
            Target.WaitForTarget(1000)
            Target.TargetExecute(JUNK_BACKPACK_SERIAL)
            return True
            
        return False

    def process_inventory(self):
        """Process inventory and move unwanted items to junk backpack"""
        if JUNK_BACKPACK_SERIAL == 0:
            self.debug("No junk backpack serial configured!", 'warning')
            return False
            
        junk_backpack = Items.FindBySerial(JUNK_BACKPACK_SERIAL)
        if not junk_backpack:
            self.debug("Junk backpack not found!", 'warning')
            return False
            
        self.debug("Processing inventory for junk items...", 'info')
        
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
        self.debug("=== Processing Stats ===", 'important')
        self.debug(f"Items checked: {self.stats['items_checked']}", 'info')
        self.debug(f"Tier 1 items found: {self.stats['tier1_items']}", 'info')
        self.debug(f"Tier 2 items found: {self.stats['tier2_items']}", 'info')
        self.debug(f"Other magical items: {self.stats['other_items']}", 'info')
        self.debug(f"Items moved to junk: {self.stats['items_moved']}", 'info')
        self.debug("=====================", 'important')

def find_junk_backpack():
    """Find the red junk backpack in player's backpack"""
    if not Player.Backpack:
        Misc.SendMessage("No backpack found!", 33)
        return None
        
    # Try each hue in our acceptable range
    for hue in JUNK_BACKPACK_HUES:
        junk = Items.FindByID(JUNK_BACKPACK_ID, hue, Player.Backpack.Serial)
        if junk:
            Misc.SendMessage(f"Found junk backpack (hue: 0x{hue:X}): 0x{junk.Serial:X}", 68)
            return junk.Serial
            
    Misc.SendMessage(f"No junk backpack found with hues {[f'0x{h:X}' for h in JUNK_BACKPACK_HUES]}! Place a red backpack in your backpack.", 33)
    return None

# Auto-find junk backpack on script load
JUNK_BACKPACK_SERIAL = find_junk_backpack() or 0

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
