"""
UI WALIA Item Inspection - a Razor Enhanced Python Script for Ultima Online

WALIA ( What Am I Looking At ) , display item information , expanded
a custom gump running in background as a button ( book shelf )
clicking it triggers the item inspection targeter
an inspector target reticle , the player selects an item 
a custom gump displays the item info and the items that can be crafted with it 

** some item properties are not available through api or limited to 4 properties ( spell books dont list their multiple properties )
TODO: 
- separate the crafting json logic , focus on core items with mechanics (recall rune) and weapons armor
- remove the immersive mode toggles , the dev info like hue and item id is hidden now and should be appended to be displayed , there doesnt need to be global toggle for the mode .
- armor values are off , consider displaying more generalized percentage , ideally we want to show true armor value total + modifiers , consider the base item + material ( valorite ) + crafting modifiers ( exceptional ) + property modifier ( invulnerable )
- add base armor values to all items display it on first line 
- increase the gump id of results gump so that we can create multiple results , consider some range that we cycle through so wont clash with other ids 
- 
HOTKEY:: AutoStart on Login
VERSION:: 20250831
"""

import os
import re
import time
import json # maybe we conditionally load this if a crafting_recipe.json is found? that way no dependency for general use

DEBUG_MODE = False  # Set to False to silence debug messages
IMMERSIVE_MODE = False # this is always on now , the dev stuff is hidden , with button on ui to toggle it on

DISPLAY = {
    'show_item_graphic': True,
    'show_item_id': False,
    'show_item_hue': False,
    'show_item_serial': False,
    'show_category': False,
    'show_makes': False,
    'show_rarity': True,
    'show_description': True,
    'use_unicode_title': True,
    'show_title': True,
    'apply_item_hue': True,
    'show_dev_text': False,
    'show_crafting': False,
    'show_crafting_message': False,
}

# Position of the small floating launcher button
LAUNCHER_X = 200
LAUNCHER_Y = 200

# Default position of the results window
RESULTS_X = 200
RESULTS_Y = 250

# Separate gump IDs for the small launcher button and the results window
LAUNCHER_GUMP_ID = 0x7A11A12
RESULTS_GUMP_ID = 0x7A11A13 # this iterates upwards so could see results side by side

# Map item properties to richer text for clarity 
PROPERTY_REMAP = {
    # Accuracy -> Tactics modifier (weapons) — numeric-first formatting
    'accurate': '+ 5 Tactics ( Accurate )',
    'surpassingly accurate': '+ 10 Tactics ( Surpassingly Accurate )',
    'eminently accurate': '+ 15 Tactics ( Eminently Accurate )',
    'eminently accurately': '+ 15 Tactics ( Eminently Accurate )',  # common typo variant
    'exceedingly accurate': '+ 20 Tactics ( Exceedingly Accurate )',
    'supremely accurate': '+ 25 Tactics ( Supremely Accurate )',
    # Damage tiers (weapons) — numeric-first formatting
    'ruin': '+ 1 Damage ( Ruin )',
    'might': '+ 3 Damage ( Might )',
    'force': '+ 5 Damage ( Force )',
    'power': '+ 7 Damage ( Power )',
    'vanquishing': '+ 9 Damage ( Vanquishing )',
    'exceptional': '+ 4 Damage ( Exceptional )',
    # Slayer tiers (keep PvM wording, remove PvP mentions) — numeric-first
    'lesser slaying': '+ 15% vs type ( Lesser Slayer )',
    'slaying': '+ 20% vs type ( Slayer )',
    'greater slaying': '+ 25% vs type ( Greater Slayer )',
    # Durability tiers — now handled dynamically per-slot in _compute_durability_text() because weapons and armor get different durability
    # Armor Rating tiers — now handled dynamically per-slot in _compute_ar_bonus_text() because each item different amount
    'mastercrafted': 'Mastercrafted',
}

# Known items with custom descriptions and colored text
KNOWN_ITEMS = {
    # Key: ItemID (hex or int), Value: list of description lines with HTML color formatting
    0x1F14: [  # Recall Rune
        "this rune stone may store a location",
        "using <basefont color=#3FA9FF>Recall</basefont> or <basefont color=#3FA9FF>GateTravel</basefont> will transport the caster to the location stored in the target rune stone",
        "using <basefont color=#FF6B6B>Mark</basefont> sets the caster's location into the target rune stone",
        "rename the rune stone by double clicking it",
        "a <basefont color=#8B4513>RuneBook</basefont> may store multiple rune stones , by dropping them onto the book"
    ],
}

# Enchanting materials with their specific enhancement properties
KNOWN_ENCHANTING_ITEMS = {
    0x3197: [  # Fire Ruby
        "a gem for enchanting",
        "used at an <basefont color=#FFB84D>Enchantment Table</basefont> for  <basefont color=#FF6B6B>Weapon Damage</basefont> , and Spellbook <basefont color=#FF6B6B>Fireball</basefont>, and Armor <basefont color=#FF6B6B>Fire Elemental</basefont>",
        "collected from mining and salvaging <basefont color=#3FA9FF>Magical</basefont> items ",
        #imbuing "used for imbuing <basefont color=#5CB85C>Strength</basefont> properties onto armor , and <basefont color=#FFB84D>Hit Fireball</basefont> onto weapon ",
        #crafting "used for crafting the <basefont color=#FF6B6B>Fiery Spellblade</basefont>",
    ],
    0x573C: [  # Arcanic Rune Stone
        "an enchanting material",
        "used at an <basefont color=#FFB84D>Enchantment Table</basefont> for <basefont color=#FF6B6B>Mastery Damage</basefont> (spellbook)",
        "collected from <basefont color=#8B4513>Scavenging</basefont> and salvaging <basefont color=#3FA9FF>Magical</basefont> items ",
    ],
    0x5748: [  # Bottle Ichor
        "an enchanting material",
        "used at an <basefont color=#FFB84D>Enchantment Table</basefont> for <basefont color=#5CB85C>Weapon Life Leech</basefont>",
        "collected from <basefont color=#8B4513>Scavenging</basefont> and salvaging <basefont color=#3FA9FF>Magical</basefont> items ",
    ],
    0x3198: [  # Blue Diamond
        "an enchanting material",
        "used at an <basefont color=#FFB84D>Enchantment Table</basefont> for <basefont color=#FFB84D>Boss Damage</basefont>",
        "collected from <basefont color=#8B4513>Scavenging</basefont> and salvaging <basefont color=#3FA9FF>Magical</basefont> items ",
    ],
    0x5742: [  # Boura Pelt
        "an enchanting material",
        "used at an <basefont color=#FFB84D>Enchantment Table</basefont> for Armor <basefont color=#8B4513>Giant defense</basefont>, and Spellbook <basefont color=#B084FF>Earth Elemental</basefont>",
        "collected from <basefont color=#8B4513>Scavenging</basefont> and salvaging <basefont color=#3FA9FF>Magical</basefont> items ",
    ],
    0x573B: [  # Crushed Glass
        "an enchanting material",
        "used at an <basefont color=#FFB84D>Enchantment Table</basefont> for <basefont color=#3FA9FF>Blade Spirits</basefont>",
        "collected from <basefont color=#8B4513>Scavenging</basefont> and salvaging <basefont color=#3FA9FF>Magical</basefont> items ",    
    ],
    0x5732: [  # Crystalline (BlackrockCrystaline)
        "an enchanting material",
        "used at an <basefont color=#FFB84D>Enchantment Table</basefont> for <basefont color=#FFB84D>Surging</basefont>",
        "collected from <basefont color=#8B4513>Scavenging</basefont> and salvaging <basefont color=#3FA9FF>Magical</basefont> items ",
    ],
    0x5721: [  # Daemon Claw
        "an enchanting material",
        "used at an <basefont color=#FFB84D>Enchantment Table</basefont> for Weapon <basefont color=#FF6B6B>Savagery</basefont>, and Armor <basefont color=#8B4513>Daemonic defense</basefont>, and Spellbook <basefont color=#B084FF>Summon Daemon</basefont>",
        "collected from <basefont color=#8B4513>Scavenging</basefont> and salvaging <basefont color=#3FA9FF>Magical</basefont> items ",
    ],
    0x26B4: [  # Delicate Scales
        "an enchanting material",
        "used at an <basefont color=#FFB84D>Enchantment Table</basefont> for <basefont color=#5CB85C>Hunter's Luck</basefont>",
        "collected from <basefont color=#8B4513>Scavenging</basefont> and salvaging <basefont color=#3FA9FF>Magical</basefont> items ",
    ],
    0x5737: [  # Elven Fletching
        "an enchanting material",
        "used at an <basefont color=#FFB84D>Enchantment Table</basefont> for Weapon <basefont color=#3FA9FF>Weapon Accuracy</basefont>, and Spellbook <basefont color=#B084FF>Magic Arrow</basefont>",
        "collected from <basefont color=#8B4513>Scavenging</basefont> and salvaging <basefont color=#3FA9FF>Magical</basefont> items ",
    ],
    0x2DB2: [  # Enchanted Essence
        "an enchanting material",
        "used at an <basefont color=#FFB84D>Enchantment Table</basefont> for Spellbook <basefont color=#3FA9FF>Lower Mana Cost</basefont>",
        "collected from <basefont color=#8B4513>Scavenging</basefont> and salvaging <basefont color=#3FA9FF>Magical</basefont> items ",
    ],
    0x5745: [  # Faery Dust
        "an enchanting material",
        "used at an <basefont color=#FFB84D>Enchantment Table</basefont> for Armor <basefont color=#8B4513>Curse Resistance</basefont>, and Spellbook <basefont color=#B084FF>Mind Blast</basefont>",
        "collected from <basefont color=#8B4513>Scavenging</basefont> and salvaging <basefont color=#3FA9FF>Magical</basefont> items ",
    ],
    0x5726: [  # Fey Wings
        "an enchanting material",
        "used at an <basefont color=#FFB84D>Enchantment Table</basefont> for Armor <basefont color=#5CB85C>Evasion</basefont>, and Spellbook <basefont color=#B084FF>Air Elemental</basefont>",
        "collected from <basefont color=#8B4513>Scavenging</basefont> and salvaging <basefont color=#3FA9FF>Magical</basefont> items ",
    ],
    0x572C: [  # Goblin Blood
        "an enchanting material",
        "used at an <basefont color=#FFB84D>Enchantment Table</basefont> for Armor <basefont color=#8B4513>Vermin defense</basefont>",
        "collected from <basefont color=#8B4513>Scavenging</basefont> and salvaging <basefont color=#3FA9FF>Magical</basefont> items ",
    ],
    0x572D: [  # Lava Serpent Crust
        "an enchanting material",
        "used at an <basefont color=#FFB84D>Enchantment Table</basefont> for Armor <basefont color=#8B4513>Draconic defense</basefont>, and Spellbook <basefont color=#B084FF>Flamestrike</basefont>",
        "collected from <basefont color=#8B4513>Scavenging</basefont> and salvaging <basefont color=#3FA9FF>Magical</basefont> items ",
    ],
    0x0F87: [  # Lucky Coin
        "a metal coin of luck used for enchanting",
        "used at an <basefont color=#FFB84D>Enchantment Table</basefont> for Armor <basefont color=#5CB85C>Crafting Luck</basefont>",
        "collected from <basefont color=#8B4513>Scavenging</basefont> and salvaging <basefont color=#3FA9FF>Magical</basefont> items ",
    ],
    0x3191: [  # Luminescent (FungusLuminescent)
        "a glowing mushroom of luminescent fungi",
        "used at an <basefont color=#FFB84D>Enchantment Table</basefont> for Spellbook <basefont color=#3FA9FF>Spell Leech</basefont>",
        "collected from <basefont color=#8B4513>Scavenging</basefont> and salvaging <basefont color=#3FA9FF>Magical</basefont> items ",
        #imbuing "an Imbuing ingredients to imbue the Hit Point Increase, Mana Increase and Stamina Increase property onto items.",
        #crafting "used for crafting the <basefont color=#FF6B6B>Darkglow Potion</basefont>",
    ],
    0x2DB1: [  # Magical Residue
        "an enchanting material",
        "used at an <basefont color=#FFB84D>Enchantment Table</basefont> for Spellbook <basefont color=#3FA9FF>Lower Reagent Cost</basefont>",
        "collected from <basefont color=#8B4513>Scavenging</basefont> and salvaging <basefont color=#3FA9FF>Magical</basefont> items ",
    ],
    0x3190: [  # Parasitic Plant
        "an enchanting material",
        "used at an <basefont color=#FFB84D>Enchantment Table</basefont> for Spellbook <basefont color=#B084FF>Summon Surge</basefont>",
        "collected from <basefont color=#8B4513>Scavenging</basefont> and salvaging <basefont color=#3FA9FF>Magical</basefont> items ",
    ],
    0x573D: [  # Powdered Iron
        "an enchanting material",
        "used at an <basefont color=#FFB84D>Enchantment Table</basefont> for Weapon <basefont color=#FF6B6B>Attack Speed</basefont>, and Spellbook <basefont color=#B084FF>Explosion</basefont>",
        "collected from <basefont color=#8B4513>Scavenging</basefont> and salvaging <basefont color=#3FA9FF>Magical</basefont> items ",
    ],
    0x5747: [  # Raptor Teeth
        "an enchanting material",
        "used at an <basefont color=#FFB84D>Enchantment Table</basefont> for Weapon <basefont color=#FF6B6B>Critical Damage</basefont>",
        "collected from <basefont color=#8B4513>Scavenging</basefont> and salvaging <basefont color=#3FA9FF>Magical</basefont> items ",
    ],
    0x2DB3: [  # Relic Fragment
        "an enchanting material",
        "used at an <basefont color=#FFB84D>Enchantment Table</basefont> for Armor <basefont color=#5CB85C>Archeologist</basefont>, and Spellbook <basefont color=#B084FF>Summon Creature</basefont>",
        "collected from <basefont color=#8B4513>Scavenging</basefont> and salvaging <basefont color=#3FA9FF>Magical</basefont> items ",
    ],
    0x5736: [  # Seed of Renewel
        "an enchanting material",
        "used at an <basefont color=#FFB84D>Enchantment Table</basefont> for Armor <basefont color=#5CB85C>Harvesting Luck</basefont>",
        "collected from <basefont color=#8B4513>Scavenging</basefont> and salvaging <basefont color=#3FA9FF>Magical</basefont> items ",
    ],
    0x5744: [  # Silver Snake
        "an enchanting material",
        "used at an <basefont color=#FFB84D>Enchantment Table</basefont> for Spellbook <basefont color=#3FA9FF>Water Elemental</basefont>",
        "collected from <basefont color=#8B4513>Scavenging</basefont> and salvaging <basefont color=#3FA9FF>Magical</basefont> items ",
    ],
    0x5746: [  # Slith Tongue
        "an enchanting material",
        "used at an <basefont color=#FFB84D>Enchantment Table</basefont> for Armor <basefont color=#8B4513>Poison Resistance</basefont>",
        "collected from <basefont color=#8B4513>Scavenging</basefont> and salvaging <basefont color=#3FA9FF>Magical</basefont> items ",
    ],
    0x5720: [  # Spider Carapace
        "an enchanting material",
        "used at an <basefont color=#FFB84D>Enchantment Table</basefont> for Armor <basefont color=#8B4513>Arachnid defense</basefont>",
        "collected from <basefont color=#8B4513>Scavenging</basefont> and salvaging <basefont color=#3FA9FF>Magical</basefont> items ",
    ],
    0x5731: [  # Undying Flesh
        "an enchanting material",
        "used at an <basefont color=#FFB84D>Enchantment Table</basefont> for Armor <basefont color=#8B4513>Undead defense</basefont>",
        "collected from <basefont color=#8B4513>Scavenging</basefont> and salvaging <basefont color=#3FA9FF>Magical</basefont> items ",
    ],
    0x5722: [  # Vial of Vitriol
        "an enchanting material",
        "used at an <basefont color=#FFB84D>Enchantment Table</basefont> for Weapon <basefont color=#FF6B6B>Mage Killer</basefont>, and Spellbook <basefont color=#B084FF>Harm</basefont>, and Armor <basefont color=#8B4513>Infidel Defense</basefont>",
        "collected from <basefont color=#8B4513>Scavenging</basefont> and salvaging <basefont color=#3FA9FF>Magical</basefont> items ",
    ],
    0x573E: [  # Void Orb
        "an enchanting material",
        "used at an <basefont color=#FFB84D>Enchantment Table</basefont> for Weapon <basefont color=#B084FF>Paragon Conversion</basefont>, and Spellbook <basefont color=#B084FF>Energy Vortex</basefont>",
        "collected from <basefont color=#8B4513>Scavenging</basefont> and salvaging <basefont color=#3FA9FF>Magical</basefont> items ",
    ],
    0x5749: [  # Reflective wolf eye
        "an enchanting material",
        "used at an <basefont color=#FFB84D>Enchantment Table</basefont> for Armor <basefont color=#B084FF>Reflective</basefont>",
        "collected from <basefont color=#8B4513>Scavenging</basefont> and salvaging <basefont color=#3FA9FF>Magical</basefont> items ",
    ],
}

# Append enchanting items to the main known items dictionary
KNOWN_ITEMS.update(KNOWN_ENCHANTING_ITEMS)

# Colors (Razor Enhanced gump label hues)
COLORS = {
    'title': 68,       # blue
    'label': 1153,     # light gray
    'ok': 63,          # green
    'warn': 53,        # yellow
    'bad': 33,         # red
    'cat': 90,         # cyan
}

# Hex colors for HTML text rendering based on tiers
NAME_TIER_COLORS = {
    'common':    '#DDDDDD',
    'uncommon':  '#5CB85C',  # green
    'rare':      '#3FA9FF',  # blue
    'epic':      '#B084FF',  # purple
    'legendary': '#FFB84D',  # orange/gold
    'mythic':    '#FF6B6B',  # red-ish
}

MATERIAL_RARITY = {
    'low':  {'hue': COLORS['ok']}, # green
    'mid':  {'hue': COLORS['warn']}, # yellow
    'high': {'hue': COLORS['bad']}, # red
}

# Runtime state
_IS_TARGETING = False
_LAST_TARGET_SERIAL = None
_LAST_TARGET_ITEMID = None
_LAST_TARGET_NAME = None
_LAST_USAGES = None

#//=============================================================================
# Equipment slot mapping (by ItemID)
# Source: mirrored from scripts/ITEM_filter_junk_salvager.py item catalogs
# Slots: head, neck, body, legs, arms, hand, weapon1h, weapon2h, shield
# Note: Handedness for some weapons needs verification , some may be wrong
EQUIP_SLOT_BY_ITEMID = {
    # --- Shields ---
    0x1B72: 'shield', 0x1B73: 'shield', 0x1B74: 'shield', 0x1B75: 'shield',
    0x1B76: 'shield', 0x1B77: 'shield', 0x1B78: 'shield', 0x1B79: 'shield',
    0x1B7A: 'shield', 0x1B7B: 'shield', 0x1BC3: 'shield', 0x1BC4: 'shield',
    0x1BC5: 'shield', 0x4201: 'shield', 0x4200: 'shield', 0x4202: 'shield',
    0x4203: 'shield', 0x4204: 'shield', 0x4205: 'shield', 0x4206: 'shield',
    0x4207: 'shield', 0x4208: 'shield', 0x4228: 'shield', 0x4229: 'shield',
    0x422A: 'shield', 0x422C: 'shield', 0x7817: 'shield', 0x7818: 'shield',
    0xA649: 'shield',

    # --- Armor: Leather ---
    0x13CD: 'arms',  # Leather Sleeves
    0x13CB: 'legs',  # Leather Leggings
    0x13CC: 'body',  # Leather Tunic
    0x13C6: 'hand',  # Leather Gloves
    0x1DB9: 'head',  # Leather Cap
    0x1C08: 'legs',  # Leather Skirt (treated as legs)
    0x1C06: 'body',  # Leather Armor (Female)
    0x277A: 'neck',  # Leather Mempo
    0x1C00: 'legs',  # Leather Shorts
    0x1C0A: 'body',  # Leather Bustier

    # --- Armor: Platemail ---
    0x1415: 'body',  # Plate Mail Chest
    0x1411: 'legs',  # Plate Mail Legs
    0x1414: 'neck',  # Plate Mail Gorget
    0x1413: 'hand',  # Plate Mail Gloves
    0x2779: 'neck',  # Platemail Mempo
    0x140A: 'head',  # Helmet
    0x140C: 'head',  # Bascinet
    0x140E: 'head',  # Norse Helm
    0x1408: 'head',  # Close Helm
    0x1412: 'head',  # Plate Helm
    0x1C04: 'body',  # Platemail Female
    0x1410: 'arms',  # Platemail Arms

    # --- Armor: Chainmail ---
    0x13BF: 'body',  # Chainmail Tunic
    0x13BE: 'legs',  # Chainmail Leggings
    0x13BB: 'head',  # Chainmail Coif
    0x13C0: 'body',  # Chainmail Tunic (Alt)
    0x13C3: 'arms',  # Chainmail Sleeves
    0x13C4: 'hand',  # Chainmail Gloves
    0x13F0: 'legs',  # Chainmail Leggings (Alt)

    # --- Armor: Bone ---
    0x144F: 'body',  # Bone Armor Chest
    0x1452: 'legs',  # Bone Leggings
    0x144E: 'arms',  # Bone Arms
    0x1450: 'hand',  # Bone Gloves (Alt)
    0x1451: 'head',  # Bone Helmet
    # Note: file also listed some shield IDs under Bone; those are mapped above

    # --- Armor: Ringmail ---
    0x13EC: 'body',  # Ringmail Tunic
    0x13EE: 'arms',  # Ringmail Sleeves
    0x13EB: 'hand',  # Ringmail Gloves
    0x13F0: 'legs',  # Ringmail Leggings
    0x13C0: 'body',  # Ring Mail Tunic (dup from alt)
    0x13C3: 'arms',  # Ring Mail Sleeves (dup)
    0x13C4: 'hand',  # Ring Mail Gloves (dup)

    # --- Armor: Studded ---
    0x13C7: 'neck',  # Studded Leather Gorget
    0x13DB: 'body',  # Studded Leather Tunic
    0x13D4: 'arms',  # Studded Leather Sleeves
    0x13DA: 'hand',  # Studded Leather Gloves
    0x13D6: 'legs',  # Studded Leather Leggings
    0x279D: 'neck',  # Studded Mempo
    0x13D5: 'hand',  # Studded Gloves
    0x13DC: 'arms',  # Studded Sleeves
    0x1C0C: 'body',  # Studded Bustier
    0x1C02: 'body',  # Studded Armor (Female)

    # --- Weapons: Axes ---
    0x0F49: 'weapon1h',  # Axe 
    0x0F47: 'weapon2h',  # Battle Axe
    0x0F4B: 'weapon2h',  # Double Axe
    0x0F45: 'weapon2h',  # Executioner's Axe
    0x0F43: 'weapon1h',  # Hatchet
    0x13FB: 'weapon2h',  # Large Battle Axe
    0x1443: 'weapon2h',  # Two Handed Axe
    0x13B0: 'weapon1h',  # War Axe

    # --- Weapons: Swords ---
    0x0F5E: 'weapon1h',  # Broadsword
    0x1441: 'weapon1h',  # Cutlass
    0x13FF: 'weapon1h',  # Katana
    0x0F61: 'weapon1h',  # Longsword
    0x13B6: 'weapon1h',  # Scimitar
    0x13B9: 'weapon1h',  # Viking Sword

    # --- Weapons: Maces & Staves ---
    0x13B4: 'weapon1h',  # Club
    0x143D: 'weapon1h',  # Hammer Pick
    0x0F5C: 'weapon1h',  # Mace
    0x143B: 'weapon2h',  # Maul
    0x1439: 'weapon2h',  # War Hammer
    0x1407: 'weapon1h',  # War Mace
    0x0DF0: 'weapon2h',  # Black Staff
    0x13F8: 'weapon2h',  # Gnarled Staff
    0x0E89: 'weapon2h',  # Quarter Staff

    # --- Weapons: Fencing ---
    0x0EC3: 'weapon1h',  # Cleaver
    0x0EC4: 'weapon1h',  # Skinning Knife
    0x13F6: 'weapon1h',  # Butcher Knife
    0x0F52: 'weapon1h',  # Dagger
    0x0F62: 'weapon2h',  # Spear
    0x1403: 'weapon2h',  # Short Spear
    0x1405: 'weapon1h',  # War Fork
    0x1401: 'weapon1h',  # Kryss

    # --- Weapons: Archery ---
    0x13B2: 'weapon2h',  # Bow
    0x13B1: 'weapon2h',  # Bow (Alternate)
    0x26C2: 'weapon2h',  # Composite Bow
    0x0F50: 'weapon2h',  # Crossbow
    0x13FD: 'weapon2h',  # Heavy Crossbow
    0x26C3: 'weapon2h',  # Repeating Crossbow
    0x2D1F: 'weapon2h',  # Magical Shortbow

    # --- Weapons: Unknown/mixed (best-effort) ---
    0x0E86: 'weapon1h',  # Pickaxe 
    0x0DF2: 'weapon1h',  # Magic Wand (assume 1H)
    0x26BC: 'weapon1h',  # Scepter (assume 1H)
    0x0F4D: 'weapon2h',  # Bardiche
    0x143E: 'weapon2h',  # Halberd
    0x26BA: 'weapon2h',  # Scythe
    0x26BD: 'weapon2h',  # Bladed Staff
    0x26BF: 'weapon2h',  # Double Bladed Staff
    0x26BE: 'weapon2h',  # Pike
    0x0E87: 'weapon2h',  # Pitchfork (treated 2H)
    0x0E81: 'weapon2h',  # Shepherd's Crook (staff-like)
    0x26BB: 'weapon2h',  # Bone Harvester
    0x26C5: 'weapon2h',  # Bone Harvester (Alt)
    0x26C1: 'weapon1h',  # Crescent Blade (assume 1H)
    0x1400: 'weapon1h',  # Kryss (Alt)
    0x26C0: 'weapon2h',  # Lance
    0x27A8: 'weapon1h',  # Bokuto (assume 1H)
    0x27A9: 'weapon2h',  # Daisho (often 2H)
    0x27AD: 'weapon1h',  # Kama (assume 1H)
    0x27A7: 'weapon2h',  # Lajatang
    0x27A2: 'weapon2h',  # No-Dachi
    0x27AE: 'weapon1h',  # Nunchaku
    0x27AF: 'weapon1h',  # Sai
    0x27AB: 'weapon1h',  # Tekagi
    0x27A3: 'weapon1h',  # Tessen (assume 1H)
    0x27A6: 'weapon2h',  # Tetsubo
    0x27A4: 'weapon1h',  # Wakizashi (assume 1H)
    0x27A5: 'weapon2h',  # Yumi (bow)
    0x2D21: 'weapon1h',  # Assassin Spike
    0x2D24: 'weapon1h',  # Diamond Mace
    0x2D1E: 'weapon2h',  # Elven Composite Longbow
    0x2D35: 'weapon1h',  # Elven Machete
    0x2D20: 'weapon1h',  # Elven Spellblade
    0x2D22: 'weapon1h',  # Leafblade
    0x2D2B: 'weapon2h',  # Magical Shortbow (Alt)
    0x2D28: 'weapon2h',  # Ornate Axe
    0x2D33: 'weapon1h',  # Radiant Scimitar
    0x2D32: 'weapon1h',  # Rune Blade
    0x2D2F: 'weapon2h',  # War Cleaver
    0x2D25: 'weapon2h',  # Wild Staff
    0x406B: 'weapon2h',  # Soul Glaive (throwing, treated 2H)
    0x406C: 'weapon2h',  # Cyclone (throwing)
    0x4067: 'weapon2h',  # Boomerang (throwing)
    0x08FE: 'weapon1h',  # Bloodblade (assume 1H)
    0x0903: 'weapon1h',  # Disc Mace
    0x090B: 'weapon1h',  # Dread Sword
    0x0904: 'weapon2h',  # Dual Pointed Spear
    0x08FD: 'weapon2h',  # Dual Short Axes
    0x48B2: 'weapon2h',  # Gargish Axe
    0x48B4: 'weapon2h',  # Gargish Bardiche
    0x48B0: 'weapon2h',  # Gargish Battle Axe
    0x48C6: 'weapon2h',  # Gargish Bone Harvester
    0x48B6: 'weapon1h',  # Gargish Butcher Knife
    0x48AE: 'weapon1h',  # Gargish Cleaver
    0x0902: 'weapon1h',  # Gargish Dagger
    0x48D0: 'weapon2h',  # Gargish Daisho
    0x48B8: 'weapon2h',  # Gargish Gnarled Staff
    0x48BA: 'weapon1h',  # Gargish Katana
    0x48BC: 'weapon1h',  # Gargish Kryss
    0x48CA: 'weapon2h',  # Gargish Lance
    0x48C2: 'weapon2h',  # Gargish Maul
    0x48C8: 'weapon2h',  # Gargish Pike
    0x48C4: 'weapon2h',  # Gargish Scythe
    0x0908: 'weapon1h',  # Gargish Talwar
    0x48CE: 'weapon1h',  # Gargish Tekagi
    0x48CC: 'weapon1h',  # Gargish Tessen
    0x48C0: 'weapon2h',  # Gargish War Hammer
    0x0905: 'weapon2h',  # Glass Staff
    0x090C: 'weapon1h',  # Glass Sword
    0x0906: 'weapon2h',  # Serpentstone Staff
    0x0907: 'weapon1h',  # Shortblade
    0x0900: 'weapon1h',  # Stone War Sword
}

# Remap common crafting material names to backpack tooltip names
# we maybe remove this , this is for crafting info 
MATERIAL_NAME_REMAP = {
    'flour': 'open sack of flour',
    'raw ribs': 'cut of raw ribs',
    'sack of flour': 'open sack of flour',
    'bag of flour': 'open sack of flour',
    'flour sack': 'open sack of flour',
    'water': 'pitcher of water',
    'water pitcher': 'pitcher of water',
    'pitcher water': 'pitcher of water',
    'ball of dough': 'dough',
    'dough ball': 'dough',
    'honey': 'jar of honey',
    'jar honey': 'jar of honey',
    'honey jar': 'jar of honey',
    'jar of honey': 'jar of honey',
    'raw fish steaks': 'raw fish steak',
}

def debug_msg(message, color=90):
    if not DEBUG_MODE:
        return
    try:
        Misc.SendMessage(f"[WALIA] {message}", color)
    except Exception:
        try:
            print(f"[WALIA] {message}")
        except Exception:
            pass

def get_equip_slot(item_id):
    """Return equip slot for an item id, or None if unknown."""
    try:
        return EQUIP_SLOT_BY_ITEMID.get(int(item_id))
    except Exception:
        return EQUIP_SLOT_BY_ITEMID.get(item_id)

def get_weapon_abilities(item_id):
    """Get weapon abilities for an item using Razor Enhanced API.
    Returns tuple of (primary_ability, secondary_ability) or (None, None) if not a weapon.
    """
    try:
        abilities = Items.GetWeaponAbility(int(item_id))
        if abilities:
            # Handle ValueTuple[str, str] return type
            primary, secondary = abilities.Item1, abilities.Item2
            # Filter out "Invalid" responses
            if primary == "Invalid":
                primary = None
            if secondary == "Invalid":
                secondary = None
            return primary, secondary
    except Exception as e:
        debug_msg(f"Error getting weapon abilities for {item_id}: {e}", COLORS['warn'])
    return None, None

def get_item_properties(item_serial, delay=500):
    """Get detailed item properties using Items.GetProperties() API.
    Returns list of Property objects with more comprehensive information.
    """
    try:
        properties = Items.GetProperties(int(item_serial), int(delay))
        if properties:
            return list(properties)
    except Exception as e:
        debug_msg(f"Error getting properties for serial {item_serial}: {e}", COLORS['warn'])
    return []

def apply_display_preset(immersive: bool):
    """Apply preset for immersive vs dev/technical display."""
    global IMMERSIVE_MODE, DISPLAY
    IMMERSIVE_MODE = bool(immersive)
    if IMMERSIVE_MODE:
        DISPLAY.update({
            'show_item_graphic': True,
            'show_item_id': False,
            'show_item_hue': False,
            'show_item_serial': False,
            'show_category': False,
            'show_makes': False,
            'show_rarity': False,
            'show_description': True,
        })
    else:
        DISPLAY.update({
            'show_item_graphic': True,
            'show_item_id': True,
            'show_item_hue': True,
            'show_item_serial': False,
            'show_category': True,
            'show_makes': True,
            'show_rarity': True,
            'show_description': True,
        })

# Initialize to immersive by default (DEV off)
apply_display_preset(True)

def _singularize(word: str) -> str:
    if len(word) > 3 and word.endswith('s'):
        return word[:-1]
    return word

def name_to_fuzzy_key(name: str) -> str:
    try:
        n = (name or '').strip().lower()
        if not n or n == 'unknown':
            return ''
        n = re.sub(r"[^a-z0-9\s]", " ", n)
        toks = [t for t in n.split() if t]
        out = []
        for t in toks:
            if t.isdigit():
                continue
            if t not in ('raw','cooked'):
                t = _singularize(t)
            out.append(t)
        if not out:
            return ''
        out.sort()
        return ' '.join(out)
    except Exception:
        return ''

def _script_root_paths():
    here = os.path.abspath(os.path.dirname(__file__))
    project_root = os.path.abspath(os.path.join(here, os.pardir))
    data_dir = os.path.join(project_root, 'data')
    return project_root, data_dir

def _find_latest_crafting_json(data_dir: str) -> str:
    if not os.path.isdir(data_dir):
        return None
    candidates = []
    for name in os.listdir(data_dir):
        if not name.lower().endswith('.json'):
            continue
        if not name.lower().startswith('gump_crafting'):
            continue
        full = os.path.join(data_dir, name)
        try:
            mtime = os.path.getmtime(full)
        except Exception:
            continue
        candidates.append((mtime, full))
    if not candidates:
        return None
    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]

def _read_json(path: str):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def _normalize_items(json_root):
    # Case 1: already a list of items
    if isinstance(json_root, list):
        return json_root
    # Case 2: structured by categories
    items = []
    cats = (json_root or {}).get('categories', {})
    for cat_key, cat_data in cats.items():
        for it in (cat_data.get('items') or []):
            parsed = (it or {}).get('parsed') or {}
            if parsed:
                if 'category' not in parsed:
                    parsed['category'] = cat_key
                # carry button ids if present
                if 'button_info' in it and 'item_info_button_id' not in parsed:
                    parsed['item_info_button_id'] = it.get('button_info')
                if 'button_make' in it and 'item_make_button_id' not in parsed:
                    parsed['item_make_button_id'] = it.get('button_make')
                items.append(parsed)
    return items

def _to_int_id(v):
    try:
        if v is None:
            return None
        if isinstance(v, int):
            return v
        s = str(v).strip()
        if s.lower().startswith('0x'):
            return int(s, 16)
        return int(s)
    except Exception:
        return None

def _normalize_material_name(nm: str) -> str:
    n = (nm or '').strip().lower()
    if not n:
        return n
    return MATERIAL_NAME_REMAP.get(n, n)

def build_material_index(items: list) -> dict:
    """Build index mapping material identifiers to recipes.
    Returns dict with:
    - by_id: {int item_id -> [recipe dicts]}
    - by_name: {normalized_name -> [recipe dicts]}
    - by_fuzzy: {fuzzy_key -> [recipe dicts]}
    """
    idx = {
        'by_id': {},
        'by_name': {},
        'by_fuzzy': {},
    }
    for rec in (items or []):
        mats = rec.get('materials') or []
        for m in mats:
            # id-based
            mid = _to_int_id(m.get('id') if m.get('id') is not None else m.get('id_hex'))
            if isinstance(mid, int):
                idx['by_id'].setdefault(int(mid), []).append(rec)
            # name-based
            nm = _normalize_material_name(m.get('name'))
            if nm:
                idx['by_name'].setdefault(nm, []).append(rec)
                fk = name_to_fuzzy_key(nm)
                if fk:
                    idx['by_fuzzy'].setdefault(fk, []).append(rec)
    return idx

# Razor Enhanced helpers -----------------------------

def _pause(ms):
    try:
        Misc.Pause(int(ms))
    except Exception:
        time.sleep(ms/1000.0)

def _clean_leading_amount(name: str, amount: int) -> str:
    try:
        amt = int(amount)
    except Exception:
        return name
    if not name:
        return name
    if amt > 1:
        pattern = r'^\s*(?:\(|\[)?\s*' + re.escape(str(amt)) + r'\s*(?:\)|\])?\s*(?:x|×|X)?\s*[:\-*]?\s*'
        cleaned = re.sub(pattern, '', name).strip()
        if cleaned != name:
            return cleaned
    generic = re.sub(r'^\s*(?:\(|\[)?\s*\d+\s*(?:\)|\])?\s*(?:x|×|X)?\s*[:\-*]?\s*', '', name).strip()
    return generic

def get_item_name(item, amount_hint=None):
    try:
        nm = item.Name
        if nm:
            nm = str(nm)
            amt = amount_hint if amount_hint is not None else item.Amount
            return _clean_leading_amount(nm, amt)
    except Exception:
        pass
    try:
        Items.WaitForProps(item.Serial, 400)
        props = Items.GetPropStringList(item.Serial)
        if props:
            nm = str(props[0])
            amt = amount_hint if amount_hint is not None else item.Amount
            return _clean_leading_amount(nm, amt)
        Items.SingleClick(item.Serial)
        _pause(150)
        Items.WaitForProps(item.Serial, 600)
        props = Items.GetPropStringList(item.Serial)
        if props:
            nm = str(props[0])
            amt = amount_hint if amount_hint is not None else item.Amount
            return _clean_leading_amount(nm, amt)
    except Exception:
        pass
    return 'Unknown'

def _fmt_hex4(v: int) -> str:
    try:
        return f"0x{int(v)&0xFFFF:04X}"
    except Exception:
        return "0x0000"

# WALIA core -----------------------------

def _rarity_for_recipe(rec: dict) -> str:
    # Simple heuristic: use skill_required or material count
    try:
        sr = float(rec.get('skill_required') or 0)
    except Exception:
        sr = 0.0
    mats = rec.get('materials') or []
    if sr >= 90 or len(mats) >= 5:
        return 'high'
    if sr >= 70 or len(mats) >= 3:
        return 'mid'
    return 'low'

def find_usages_for_item(item, index: dict) -> list:
    """Return list of recipes that use the targeted item as a material.
    Matches by itemID, normalized name, or fuzzy name.
    """
    matches = []
    try:
        gid = int(item.ItemID)
    except Exception:
        gid = None
    name = get_item_name(item, amount_hint=getattr(item, 'Amount', 1))
    n_norm = _normalize_material_name(name)
    fkey = name_to_fuzzy_key(n_norm)

    seen = set()
    # by id
    if isinstance(gid, int) and gid in index.get('by_id', {}):
        for r in index['by_id'][gid]:
            k = (r.get('category'), r.get('name'))
            if k not in seen:
                matches.append(r)
                seen.add(k)
    # by normalized name
    if n_norm and n_norm in index.get('by_name', {}):
        for r in index['by_name'][n_norm]:
            k = (r.get('category'), r.get('name'))
            if k not in seen:
                matches.append(r)
                seen.add(k)
    # by fuzzy
    if fkey and fkey in index.get('by_fuzzy', {}):
        for r in index['by_fuzzy'][fkey]:
            k = (r.get('category'), r.get('name'))
            if k not in seen:
                matches.append(r)
                seen.add(k)
    return matches

def _build_item_description(name: str, usages: list) -> str:
    try:
        total = len(usages or [])
        if total <= 0:
            return "No known crafting usages found."
        cats = sorted({(u.get('category') or 'Unknown') for u in usages})
        cats_txt = ', '.join(cats[:6]) + ("…" if len(cats) > 6 else "")
        return f"Used in {total} recipes across: {cats_txt}"
    except Exception:
        return ""

def _stylize_unicode(text: str, style: str = 'fullwidth') -> str:
    """Return a unicode-styled variant of ASCII text.
    Styles:
    - 'fullwidth': convert ASCII to fullwidth and convert space to fullwidth space (\u3000).
    - 'fullwidth_nospace': convert ASCII to fullwidth but keep regular ASCII space ' '.
    """
    if not text:
        return text
    if style in ('fullwidth', 'fullwidth_nospace'):
        out = []
        for ch in text:
            o = ord(ch)
            if 0x21 <= o <= 0x7E:  # visible ASCII
                out.append(chr(o - 0x21 + 0xFF01))
            elif ch == ' ':
                if style == 'fullwidth':
                    out.append('\u3000')  # fullwidth space
                else:
                    out.append(' ')       # keep normal space
            else:
                out.append(ch)
        return ''.join(out)
    return text

def _derive_name_color(prop_list: list) -> str:
    """Infer item Name color from properties. Looks for 'Magical Intensity X (Tier)'.
    Returns an HTML hex color string or default white when unknown.
    """
    try:
        if not prop_list:
            return '#FFFFFF'
        import re as _re
        for ln in prop_list:
            s = str(ln).strip()
            m = _re.search(r"magical\s+intensity\s*\d+\s*\(([^)]+)\)", s, flags=_re.IGNORECASE)
            if m:
                tier = m.group(1).strip().lower()
                # Normalize common tier names
                if tier in NAME_TIER_COLORS:
                    return NAME_TIER_COLORS[tier]
                # Map aliases
                alias = {
                    'epic': 'epic', 'legend': 'legendary', 'legendary': 'legendary',
                    'mythic': 'mythic', 'rare': 'rare', 'uncommon': 'uncommon', 'common': 'common'
                }.get(tier)
                if alias and alias in NAME_TIER_COLORS:
                    return NAME_TIER_COLORS[alias]
                return '#FFFFFF'
    except Exception:
        pass
    return '#FFFFFF'

# Modular text section rendering system
class TextSection:
    """Represents a section of text with multiple lines and formatting."""
    def __init__(self, lines: list, category: str, priority: int = 100, separator_before: bool = False):
        self.lines = lines  # List of raw HTML strings (preserves existing formatting)
        self.category = category
        self.priority = priority  # Lower numbers = higher priority (displayed first)
        self.separator_before = separator_before
    
    def to_html(self) -> str:
        """Convert to HTML with line breaks, ensuring each line has proper color formatting."""
        if not self.lines:
            return ""
        # Join with <br> but ensure each line maintains its formatting
        formatted_lines = []
        for line in self.lines:
            # If line doesn't have basefont color, it will inherit from parent or default to black
            # Make sure each line is properly wrapped
            if line.strip():
                formatted_lines.append(line)
        return "<br>".join(formatted_lines)
    
    def height_estimate(self) -> int:
        """Estimate height in pixels for this section."""
        if not self.lines:
            return 0
        base_height = len(self.lines) * 18  # 18px per line
        separator_height = 18 if self.separator_before else 0
        return base_height + separator_height

def _property_color_for_line(raw_lower: str) -> str:
    """Return HTML hex color for a given property line (lowercased)."""
    try:
        if not raw_lower:
            return '#CCCCCC'
        if raw_lower.startswith('durability'):
            return '#AAAAAA'  # grey for durability
        # Add more rules as needed
    except Exception:
        pass
    return '#CCCCCC'

def _wrap_line_with_default_color(line: str, default_color: str = '#BBBBBB') -> str:
    """Wrap a line with default color, preserving existing basefont tags."""
    if not line.strip():
        return line
    
    # If line has no basefont tags, just wrap it
    if '<basefont' not in line:
        return f"<basefont color={default_color}>{line}</basefont>"
    
    # Split on basefont tags to inject default color around them
    import re
    
    # Find all basefont color tags and their positions
    basefont_pattern = r'<basefont\s+color=[^>]*>'
    end_pattern = r'</basefont>'
    
    result = f"<basefont color={default_color}>"
    last_pos = 0
    
    # Find all basefont start tags
    for match in re.finditer(basefont_pattern, line):
        # Add text before this basefont tag with default color
        if match.start() > last_pos:
            text_before = line[last_pos:match.start()]
            if text_before.strip():
                result += text_before
        
        # Close default color before custom color
        result += f"</basefont>{match.group()}"
        last_pos = match.end()
        
        # Find the corresponding end tag
        remaining_text = line[last_pos:]
        end_match = re.search(end_pattern, remaining_text)
        if end_match:
            # Add the colored text
            colored_text = remaining_text[:end_match.end()]
            result += colored_text
            last_pos += end_match.end()
            # Restart default color after custom color
            result += f"<basefont color={default_color}>"
    
    # Add any remaining text
    if last_pos < len(line):
        remaining = line[last_pos:]
        if remaining.strip():
            result += remaining
    
    result += "</basefont>"
    return result

def _estimate_text_width(text: str, char_width: int = 7) -> int:
    """Estimate text width in pixels, ignoring HTML tags."""
    import re
    # Remove HTML tags for width calculation
    clean_text = re.sub(r'<[^>]+>', '', text)
    return len(clean_text) * char_width

def _split_line_for_wrapping(line: str, max_chars: int = 30) -> list:
    """Split a long line into multiple lines based on character count and word boundaries."""
    import re
    
    # Remove HTML tags to get clean text for length calculation
    clean_text = re.sub(r'<[^>]+>', '', line)
    
    # If line is short enough, return as-is
    if len(clean_text) <= max_chars:
        return [line]
    
    # For lines with HTML formatting, we need HTML-aware splitting
    if '<basefont' in line:
        return _split_html_line(line, max_chars)
    
    # Simple word-based wrapping for plain text
    words = line.split()
    lines = []
    current_line = ""
    
    for word in words:
        test_line = f"{current_line} {word}".strip()
        if len(test_line) <= max_chars:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
            # Handle very long single words
            if len(word) > max_chars:
                lines.append(current_line)
                current_line = ""
    
    if current_line:
        lines.append(current_line)
    
    return lines if lines else [line]

def _split_html_line(line: str, max_chars: int = 30) -> list:
    """Split HTML-formatted line while preserving color formatting."""
    import re
    
    # Extract text segments and their formatting
    segments = []
    basefont_pattern = r'<basefont\s+color=([^>]*)>(.*?)</basefont>'
    last_pos = 0
    
    # Find all basefont segments
    for match in re.finditer(basefont_pattern, line):
        # Add any text before this basefont
        if match.start() > last_pos:
            prefix_text = line[last_pos:match.start()].strip()
            if prefix_text:
                segments.append(('default', prefix_text))
        
        # Add the colored segment
        color = match.group(1)
        text = match.group(2)
        segments.append((color, text))
        last_pos = match.end()
    
    # Add any remaining text
    if last_pos < len(line):
        suffix_text = line[last_pos:].strip()
        if suffix_text:
            segments.append(('default', suffix_text))
    
    # If no HTML found, treat as plain text
    if not segments:
        segments = [('default', line)]
    
    # Now split segments into lines based on character count
    lines = []
    current_line_segments = []
    current_char_count = 0
    
    for color, text in segments:
        words = text.split()
        for word in words:
            word_len = len(word)
            # Check if adding this word would exceed limit
            space_needed = 1 if current_char_count > 0 else 0
            if current_char_count + space_needed + word_len > max_chars and current_line_segments:
                # Finish current line
                lines.append(_rebuild_html_line(current_line_segments))
                current_line_segments = []
                current_char_count = 0
            
            # Add word to current line
            current_line_segments.append((color, word))
            current_char_count += word_len + (1 if current_char_count > 0 else 0)
    
    # Add final line if any segments remain
    if current_line_segments:
        lines.append(_rebuild_html_line(current_line_segments))
    
    return lines if lines else [line]

def _rebuild_html_line(segments: list) -> str:
    """Rebuild HTML line from color/text segments."""
    if not segments:
        return ""
    
    result = "<basefont color=#BBBBBB>"  # Start with default color
    current_color = '#BBBBBB'
    
    for i, (color, word) in enumerate(segments):
        # Add space before word (except first)
        if i > 0:
            result += " "
        
        # Change color if needed
        if color != 'default' and color != current_color:
            result += f"</basefont><basefont color={color}>{word}</basefont><basefont color=#BBBBBB>"
            current_color = '#BBBBBB'
        else:
            result += word
    
    result += "</basefont>"
    return result

def _compute_ar_bonus_text(equip_slot: str, raw_lower: str) -> str or None:
    """Given an equip slot and a property line (lowercased), return a slot-specific AR bonus text.
    Returns None when not an AR tier line.
    """
    # Slot-aware AR bonus computation for armor rating tiers
    if not equip_slot or not raw_lower:
        return None
    # Identify AR tier keyword
    tiers = {
        'defense':        {'neck_hands': 0.4, 'arms_head_legs': 0.7, 'body': 2.2, 'shield': 1, 'pct': 5},
        'guarding':       {'neck_hands': 0.7, 'arms_head_legs': 1.4, 'body': 4.4, 'shield': 1.5, 'pct': 10},
        'hardening':      {'neck_hands': 1.1, 'arms_head_legs': 2.1, 'body': 6.6, 'shield': 2, 'pct': 15},
        'fortification':  {'neck_hands': 1.4, 'arms_head_legs': 2.8, 'body': 8.8, 'shield': 4, 'pct': 20},
        'invulnerable': {'neck_hands': 1.8, 'arms_head_legs': 3.5, 'body': 11.0, 'shield': 7, 'pct': 25},
    }
    found = None
    for key in tiers.keys():
        if key in raw_lower:
            found = key
            break
    if not found:
        return None
    t = tiers[found]
    # Map slot to appropriate bucket
    slot = (equip_slot or '').lower()
    if slot in ('neck', 'hand'):
        delta = t['neck_hands']
    elif slot in ('arms', 'head', 'legs'):
        delta = t['arms_head_legs']
    elif slot == 'body':
        delta = t['body']
    elif slot == 'shield':
        delta = t['shield']
    else:
        # Non-armor/shield slots: do not display AR percent; suppress line
        return None
    # Numeric-first formatting
    return f"+ {delta:g} AR ( {found.capitalize()} )"

def _is_weapon_slot(equip_slot: str) -> bool:
    slot = (equip_slot or '').lower()
    return slot in ('weapon1h', 'weapon2h')

def _compute_durability_text(equip_slot: str, raw_lower: str) -> str or None:
    """Return durability text tailored for armor vs weapons. None if not a durability tier line."""
    if not raw_lower:
        return None
    tiers_fixed = {
        'durable': 5,
        'substantial': 10,
        'massive': 15,
        'fortified': 20,
        'indestructible': 25,
    }
    # Exceptional is percent-based per spec
    if 'exceptional' == raw_lower.strip():
        if _is_weapon_slot(equip_slot):
            return '+ 20% durability ( Exceptional )'
        else:
            return '+ 20% durability ( Exceptional )'
    for k, val in tiers_fixed.items():
        if k in raw_lower:
            if _is_weapon_slot(equip_slot):
                return f"+ {val} durability ( {k.capitalize()} )"
            else:
                return f"+ {val} durability ( {k.capitalize()} )"
    return None

def _equip_slot_and_type(item_id: int) -> tuple:
    """Return (slot, friendly_type). friendly_type is one of Armor, Weapon, Shield, Unknown."""
    try:
        slot = get_equip_slot(int(item_id) if item_id is not None else 0)
    except Exception:
        slot = None
    s = (slot or '').lower()
    if s in ('weapon1h', 'weapon2h'):
        typ = 'Weapon' + (' (2H)' if s == 'weapon2h' else ' (1H)')
    elif s == 'shield':
        typ = 'Shield'
    elif s in ('head','neck','body','legs','arms','hand'):
        typ = 'Armor'
    else:
        typ = 'Unknown'
    return slot, typ

def build_text_sections(target_item, usages: list) -> list:
    """Build list of TextSection objects for modular gump content."""
    sections = []
    
    # Get basic item info
    item_display_name = get_item_name(target_item, amount_hint=getattr(target_item, 'Amount', 1))
    item_id = int(getattr(target_item, 'ItemID', 0) or 0)
    equip_slot, friendly_type = _equip_slot_and_type(item_id)
    
    # 1. Item properties section (highest priority)
    property_lines = []
    try:
        Items.WaitForProps(getattr(target_item, 'Serial', 0), 400)
        property_list = Items.GetPropStringList(getattr(target_item, 'Serial', 0)) or []
        # Skip name line if duplicates title
        if property_list and property_list[0].strip().lower() == (item_display_name or '').strip().lower():
            property_list = property_list[1:]
        
        # Process each property with slot-aware rendering
        for prop in property_list[:12]:  # Limit to prevent overflow
            raw_line = str(prop).strip()
            low = raw_line.lower()
            
            # Apply slot-aware transformations
            slot_ar_text = _compute_ar_bonus_text(equip_slot, low)
            slot_dura_text = _compute_durability_text(equip_slot, low)
            
            if slot_ar_text:
                final_text = slot_ar_text
            elif slot_dura_text:
                final_text = slot_dura_text
            else:
                final_text = PROPERTY_REMAP.get(low, raw_line)
            
            # Escape HTML but preserve existing color formatting
            safe_text = final_text.replace('<','&lt;').replace('>','&gt;') if '<basefont' not in final_text else final_text
            color = _property_color_for_line(low)
            property_lines.append(f"<basefont color={color}>{safe_text}</basefont>")
        
        if property_lines:
            sections.append(TextSection(property_lines, 'properties', 10))
    except Exception as e:
        debug_msg(f"Error processing properties: {e}", COLORS['warn'])
    
    # 2. Known item descriptions section (high priority) - EACH LINE AS SEPARATE SECTION WITH PROPER COLOR WRAPPING
    try:
        if item_id in KNOWN_ITEMS:
            debug_msg(f"Adding {len(KNOWN_ITEMS[item_id])} known item descriptions as separate sections")
            for i, desc_line in enumerate(KNOWN_ITEMS[item_id]):
                # Wrap line with default color, preserving existing basefont tags
                formatted_line = _wrap_line_with_default_color(desc_line, '#BBBBBB')
                
                # Split long lines for word wrapping at 30 characters
                wrapped_lines = _split_line_for_wrapping(formatted_line, max_chars=35)
                
                # Create sections for each wrapped line
                for j, wrapped_line in enumerate(wrapped_lines):
                    priority = 20 + i + (j * 0.1)  # Maintain order with sub-priorities for wrapped lines
                    # Add separator before each new description entry (not just the first one)
                    separator_needed = (j == 0 and (i == 0 and bool(property_lines) or i > 0))
                    section_id = f'known_desc_{i}_{j}' if len(wrapped_lines) > 1 else f'known_desc_{i}'
                    sections.append(TextSection([wrapped_line], section_id, priority, separator_before=separator_needed))
    except Exception as e:
        debug_msg(f"Error adding known descriptions: {e}", COLORS['warn'])
    
    # 3. Equipment type section (medium priority)
    equipment_lines = []
    if equip_slot or friendly_type != 'Unknown':
        equipment_lines.append(f"<basefont color=#BBBBBB>Type: {friendly_type}</basefont>")
        
        # Weapon abilities
        if _is_weapon_slot(equip_slot):
            primary_ability, secondary_ability = get_weapon_abilities(item_id)
            if primary_ability:
                equipment_lines.append(f"<basefont color=#FFD700>Primary: {primary_ability}</basefont>")
            if secondary_ability:
                equipment_lines.append(f"<basefont color=#87CEEB>Secondary: {secondary_ability}</basefont>")
    
    if equipment_lines:
        sections.append(TextSection(equipment_lines, 'equipment_type', 30, separator_before=True))
    
    # 4. Technical/dev info section (lowest priority)
    if not IMMERSIVE_MODE:
        dev_lines = []
        if DISPLAY.get('show_item_id', True):
            dev_lines.append(f"<basefont color=#999999>ItemID: {_fmt_hex4(item_id)}</basefont>")
        if DISPLAY.get('show_item_hue', True):
            dev_lines.append(f"<basefont color=#999999>Hue: {getattr(target_item,'Hue',0)}</basefont>")
        if DISPLAY.get('show_item_serial', True):
            try:
                dev_lines.append(f"<basefont color=#999999>Serial: {hex(getattr(target_item,'Serial',0))}</basefont>")
            except Exception:
                pass
        
        if dev_lines:
            sections.append(TextSection(dev_lines, 'dev_info', 90, separator_before=True))
    
    # 5. Crafting description section (if enabled)
    if DISPLAY.get('show_description', True) and DISPLAY.get('show_crafting', False):
        description_text = _build_item_description(item_display_name, usages)
        if description_text:
            craft_lines = [f"<basefont color=#CCCCCC><i>{description_text}</i></basefont>"]
            sections.append(TextSection(craft_lines, 'crafting_desc', 80, separator_before=True))
    
    # Sort by priority
    sections.sort(key=lambda x: x.priority)
    return sections

def show_walia_gump(target_item, usages: list):
    debug_msg(f"Showing results gump; usages={len(usages) if usages else 0}")

    # Build modular text sections
    text_sections = build_text_sections(target_item, usages)
    debug_msg(f"Built {len(text_sections)} text sections")
    
    item_display_name = get_item_name(target_item, amount_hint=getattr(target_item, 'Amount', 1))
    item_graphic_id = int(getattr(target_item, 'ItemID', 0) or 0)
    title_display_name = (item_display_name[:1].upper() + item_display_name[1:]) if item_display_name else "Unknown"
    if DISPLAY.get('use_unicode_title', True):
        try:
            title_display_name = _stylize_unicode(title_display_name, 'fullwidth_nospace')
        except Exception:
            pass
    title_text = f"{title_display_name}"

    gump = Gumps.CreateGump(movable=True)
    Gumps.AddPage(gump, 0)

    # Base sizes with dynamic height based on text lines
    max_rows_to_render = min(15, len(usages) or 1)
    
    # Calculate height based on text sections
    total_text_height = sum(section.height_estimate() for section in text_sections)
    text_height_px = max(60, total_text_height)

    # Calculate total content height
    content_height_px = text_height_px

    # Narrower layout and compact padding
    gump_width = 320
    # Dynamic height based on content
    gump_height = 150 + content_height_px + (max_rows_to_render * 24 if DISPLAY.get('show_crafting', False) else 0)

    Gumps.AddBackground(gump, 0, 0, gump_width, gump_height, 30546)
    Gumps.AddAlphaRegion(gump, 0, 0, gump_width, gump_height)

    # Title section using unicode styling and HTML for better formatting
    show_title_flag = DISPLAY.get('show_title', True)
    content_top_y = 8
    if show_title_flag:
        # Use HTML for title to get better control over unicode styling
        try:
            property_list = Items.GetPropStringList(getattr(target_item, 'Serial', 0)) or []
            name_hex_color = _derive_name_color(property_list)
        except Exception:
            name_hex_color = '#FFFFFF'
        
        title_html = f"<center><basefont color={name_hex_color}><big><b>{title_text}</b></big></basefont></center>"
        title_y = 10
        Gumps.AddHtml(gump, 10, title_y, gump_width - 20, 30, title_html, 0, 0)
        content_top_y = title_y + 32  # space for larger title

    # DEV toggle button anchored in the lower-right area
    dev_mode_on = (not IMMERSIVE_MODE)
    dev_toggle_label = "DEV: ON" if dev_mode_on else "DEV: OFF"
    button_width = 20
    button_height = 20
    show_dev_text_flag = DISPLAY.get('show_dev_text', False)
    if show_dev_text_flag:
        # Reserve space for label to the right of the button and keep label's right edge flush with the gump edge
        label_width = 96
        label_padding = 4
        dev_button_x = max(0, gump_width - (button_width + label_padding + label_width))
        dev_button_y = max(0, gump_height - button_height)
        Gumps.AddButton(gump, dev_button_x, dev_button_y, 9212, 9213, 77, 1, 0)
        label_x = dev_button_x + button_width + label_padding
        label_y = dev_button_y + 2
        # Darker grey label
        Gumps.AddHtml(gump, label_x, label_y, label_width, 20, f"<basefont color=#555555>{dev_toggle_label}</basefont>", 0, 0)
    else:
        # No label: place the button so it touches the lower-right corner
        dev_button_x = max(0, gump_width - button_width)
        dev_button_y = max(0, gump_height - button_height)
        Gumps.AddButton(gump, dev_button_x, dev_button_y, 9212, 9213, 77, 1, 0)

    # Item graphic on left
    if DISPLAY.get('show_item_graphic', True):
        item_top_y = content_top_y + 4
        # Try to apply hue if enabled and API supports it; otherwise fallback to no hue
        try:
            if DISPLAY.get('apply_item_hue', True):
                Gumps.AddItem(gump, 20, item_top_y, item_graphic_id, getattr(target_item, 'Hue', 0))
            else:
                Gumps.AddItem(gump, 20, item_top_y, item_graphic_id)
        except Exception:
            Gumps.AddItem(gump, 20, item_top_y, item_graphic_id)
        # Slightly larger layout reservation for item icon to avoid overlap
        item_icon_height = 60
    else:
        item_top_y = content_top_y + 6
        item_icon_height = 0

    # Text content area to the right of the icon
    additional_image_spacing_px = 8
    text_x, text_y, text_width = 64 + additional_image_spacing_px, content_top_y + 2, (gump_width - 80)

    # Render text sections separately to preserve HTML formatting
    current_y = text_y + 2
    text_offset_right_px = 4
    
    for section in text_sections:
        if section.separator_before and current_y > text_y + 2:
            # Add separator line
            separator_html = "<basefont color=#444444>─────────</basefont>"
            Gumps.AddHtml(
                gump,
                text_x + text_offset_right_px,
                current_y,
                text_width - text_offset_right_px,
                18,
                separator_html,
                0,
                0,
            )
            current_y += 18
        
        # Render section content
        section_html = section.to_html()
        if section_html:
            section_height = len(section.lines) * 18
            Gumps.AddHtml(
                gump,
                text_x + text_offset_right_px,
                current_y,
                text_width - text_offset_right_px,
                section_height,
                section_html,
                0,
                0,
            )
            current_y += section_height
    
    # Track where content ends for crafting table positioning
    content_bottom_y = current_y + 10
    # Calculate item icon bottom for layout
    item_bottom_y = item_top_y + item_icon_height if DISPLAY.get('show_item_graphic', True) else content_top_y

    # Crafting section (table/messages) can be disabled entirely via master toggle
    if DISPLAY.get('show_crafting', False):
        # Only draw crafting table when usages exist AND at least one of Category/Makes is enabled
        show_category_flag = DISPLAY.get('show_category', True)
        show_makes_flag = DISPLAY.get('show_makes', True)
        show_rarity_flag = DISPLAY.get('show_rarity', True)
        if usages and len(usages) > 0 and (show_category_flag or show_makes_flag):
            table_top_y = max(content_bottom_y, item_bottom_y)
            # Column headers for narrower width
            category_col_x = 10
            makes_col_x = 92
            rarity_col_x = max(188, gump_width - 90)
            if show_category_flag:
                Gumps.AddLabel(gump, category_col_x, table_top_y, COLORS['cat'], "Category")
            if show_makes_flag:
                Gumps.AddLabel(gump, makes_col_x, table_top_y, COLORS['cat'], "Makes")
            if show_rarity_flag:
                Gumps.AddLabel(gump, rarity_col_x, table_top_y, COLORS['cat'], "Rarity")

            row_y = table_top_y + 16
            # Sort by category then name
            usages_sorted_list = sorted(usages, key=lambda r: ((r.get('category') or '').lower(), (r.get('name') or '').lower()))
            for usage_record in usages_sorted_list[:max_rows_to_render]:
                category_name = usage_record.get('category') or 'Unknown'
                product_name = usage_record.get('name') or 'Unknown'
                rarity_key = _rarity_for_recipe(usage_record)
                rarity_hue = MATERIAL_RARITY[rarity_key]['hue']
                if show_category_flag:
                    Gumps.AddLabel(gump, category_col_x, row_y, COLORS['label'], str(category_name))
                # Product name (wrap limited width)
                if show_makes_flag:
                    makes_col_width = max(120, gump_width - makes_col_x - 120)
                    Gumps.AddHtml(gump, makes_col_x, row_y-2, makes_col_width, 22, f"<basefont color=#FFFFFF>{product_name}</basefont>", 0, 0)
                if show_rarity_flag:
                    Gumps.AddLabel(gump, rarity_col_x, row_y, rarity_hue, rarity_key.upper())
                row_y += 24
        else:
            # Either no usages or crafting table is hidden by settings; place message below content without blocking
            if DISPLAY.get('show_crafting_message', False):
                row_y = max(content_bottom_y, item_bottom_y) + 8
                if usages and len(usages) > 0 and not (show_category_flag or show_makes_flag):
                    message_text = "<basefont color=#9A9A9A>Crafting usages hidden (settings).</basefont>"
                else:
                    message_text = "<basefont color=#D8D066>No known crafting usages found.</basefont>"
                # Align with text panel to reduce excess padding
                Gumps.AddHtml(gump, text_x, row_y, text_width, 22, message_text, 0, 0)

    # Close button
    Gumps.AddButton(gump, gump_width-30, 8, 4017, 4018, 1, 1, 0)
    Gumps.AddTooltip(gump, "Close")

    # Send gump
    Gumps.SendGump(RESULTS_GUMP_ID, Player.Serial, RESULTS_X, RESULTS_Y, gump.gumpDefinition, gump.gumpStrings)

def send_launcher_gump():
    """Create and send a tiny floating gump with a single inspect button."""
    debug_msg("Building launcher gump...")
    gd = Gumps.CreateGump(movable=True)
    Gumps.AddPage(gd, 0)

    width, height = 75, 55
    Gumps.AddBackground(gd, 0, 0, width, height, 30546)
    Gumps.AddAlphaRegion(gd, 0, 0, width, height)

    # Simple centered button (only one) over a clean background
    
    try:
        Gumps.AddItem(gd, 32, 26, 0x14F5)  # centered-ish spyglass icon
    except Exception:
        pass
    # Small hint label; background (not the button) is draggable
    try:
        Gumps.AddHtml(gd, 3, 0, 68, 16, "<center><basefont color=#3FA9FF>INFO</basefont></center>", 0, 0)
    except Exception:
        pass
    Gumps.AddButton(gd, 5, 18, 9815, 9815, 1, 1, 0) # bookshelf
    Gumps.AddTooltip(gd, "Get Item Info")

    Gumps.SendGump(LAUNCHER_GUMP_ID, Player.Serial, LAUNCHER_X, LAUNCHER_Y, gd.gumpDefinition, gd.gumpStrings)
    debug_msg("Launcher gump sent")

def process_launcher_input(index: dict) -> bool:
    """Handle clicks from the launcher. Returns False when launcher should close."""
    Gumps.WaitForGump(LAUNCHER_GUMP_ID, 100)
    gd = Gumps.GetGumpData(LAUNCHER_GUMP_ID)
    if not gd:
        return True  # keep running; gump may not be visible yet
    if gd.buttonid > 0:
        # Only button id 1 exists: trigger inspection
        if gd.buttonid == 1:
            debug_msg("Launcher button clicked -> start targeting", 90)
            global _IS_TARGETING
            if _IS_TARGETING:
                debug_msg("Ignored click: targeting already in progress", COLORS['warn'])
                return True
            _IS_TARGETING = True
            try:
                # Debounce to prevent the button click from leaking into the world click buffer
                _pause(180)
                walia_run_once(index)
            finally:
                _IS_TARGETING = False
            # Re-send the launcher after action completes
            send_launcher_gump()
            return True
        # Any other id could be a close; rebuild by default
        send_launcher_gump()
        return True
    return True

def process_results_input():
    """Handle clicks from the results gump (e.g., DEV toggle)."""
    Gumps.WaitForGump(RESULTS_GUMP_ID, 50)
    gd = Gumps.GetGumpData(RESULTS_GUMP_ID)
    if not gd:
        return
    if gd.buttonid == 77:
        debug_msg("DEV toggle pressed", COLORS['cat'])
        apply_display_preset(immersive=not IMMERSIVE_MODE)
        # Reopen the last results with new display settings (inline)
        try:
            it = None
            if _LAST_TARGET_SERIAL:
                it = Items.FindBySerial(_LAST_TARGET_SERIAL)
            if it is None:
                class _Shim:
                    pass
                it = _Shim()
                setattr(it, 'Serial', _LAST_TARGET_SERIAL or 0)
                setattr(it, 'ItemID', _LAST_TARGET_ITEMID or 0)
                setattr(it, 'Hue', 0)
                setattr(it, 'Amount', 1)
                setattr(it, 'Name', _LAST_TARGET_NAME or "")
            show_walia_gump(it, _LAST_USAGES or [])
        except Exception as e:
            debug_msg(f"Failed to reopen results: {e}", COLORS['bad'])

def walia_run_once(index: dict):
    # Prompt for a target using Razor Enhanced Target system
    try:
        Misc.SendMessage("Target an item to inspect usages...", COLORS['title'])
    except Exception:
        pass
    debug_msg("Prompting for target")
    try:
        Target.Cancel()
        _pause(100)
        Target.PromptTarget("Select an item to inspect")
        sel = Target.PromptTarget()
    except Exception:
        sel = -1
    if sel is None or sel < 0:
        debug_msg("Target cancelled by user", COLORS['warn'])
        try:
            Misc.SendMessage("Target cancelled.", COLORS['warn'])
        except Exception:
            print("Target cancelled.")
        return
    try:
        it = Items.FindBySerial(sel)
    except Exception:
        it = None
    if not it:
        debug_msg(f"Target serial not found: {sel}", COLORS['bad'])
        try:
            Misc.SendMessage("Could not find targeted item.", COLORS['bad'])
        except Exception:
            print("Could not find targeted item.")
        return
    debug_msg(f"Target acquired: serial={hex(sel)} id={_fmt_hex4(getattr(it,'ItemID',0))}")
    usages = find_usages_for_item(it, index)
    debug_msg(f"Usages found: {len(usages)}")
    # cache last results for UI toggles
    try:
        global _LAST_TARGET_SERIAL, _LAST_TARGET_ITEMID, _LAST_TARGET_NAME, _LAST_USAGES
        _LAST_TARGET_SERIAL = getattr(it, 'Serial', None)
        _LAST_TARGET_ITEMID = getattr(it, 'ItemID', None)
        _LAST_TARGET_NAME = get_item_name(it, amount_hint=getattr(it, 'Amount', 1))
        _LAST_USAGES = usages[:]
    except Exception:
        pass
    try:
        show_walia_gump(it, usages)
    except Exception as e:
        try:
            Misc.SendMessage(f"Error showing WALIA gump: {e}", COLORS['bad'])
        except Exception:
            print(f"Error showing WALIA gump: {e}")

def main():
    # Load latest crafting crawl and build the material index once
    debug_msg("Starting WALIA")
    _, data_dir = _script_root_paths()
    src = _find_latest_crafting_json(data_dir)
    if not src:
        try:
            Misc.SendMessage("No gump_crafting_*.json found in /data.", COLORS['bad'])
        except Exception:
            print("No gump_crafting_*.json found in /data.")
        return
    try:
        debug_msg(f"Loading data from: {src}")
        raw = _read_json(src)
        items = _normalize_items(raw)
        debug_msg(f"Items loaded: {len(items)}")
        index = build_material_index(items)
        debug_msg("Material index built")
        # Send the persistent launcher and loop handling input
        send_launcher_gump()
        debug_msg("Entering UI loop")
        while True:
            _pause(50)
            keep_running = process_launcher_input(index)
            process_results_input()
            if not keep_running:
                break
    except Exception as e:
        try:
            Misc.SendMessage(f"WALIA error: {e}", COLORS['bad'])
        except Exception:
            print(f"WALIA error: {e}")

if __name__ == "__main__":
    main()
