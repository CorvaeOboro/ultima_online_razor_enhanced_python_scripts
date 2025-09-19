"""
UI WAILA Item Inspect - a Razor Enhanced Python Script for Ultima Online

WAILA ( What Am I Looking At ) , display item information , formatted with extra details
a custom gump running in background as a button ( book shelf )
clicking the info bookshelf button triggers the item inspection targeter then select an item 
a custom gump displays the item info and the items that can be crafted with it 

** some item properties are not available through api or limited to 4 properties ( spell books dont list their multiple properties )

TODO: 
- armor values update ( currently only 30% of modifier combinations known)
- add materials handling
- remove the crafting json logic ( we are adding data directly to the script currently )
- weapon exceptional = +20 dmg

** issues = item properties through api limited to 4 ? therefore the display is not displaying the full properties **

TROUBLESHOOTING:
- if "import" errors , download iron python 3.4.2 and copy the files in its "Lib" folder into your RazorEnhanced "Lib" folder 

HOTKEY:: AutoStart on Login
VERSION:: 20250909
"""

import re # regex parsing the text
import os # reading the crafting json , could remove if hardcoded data
import json # maybe we conditionally load this if a crafting_recipe.json is found? that way no dependency for general use

DEBUG_MODE = False  # Set to True for debugging messages
SHOW_TECHNICAL_INFO = False  # Set to True to show ItemID, Hue, Serial in results
SHOW_CLOSE_BUTTON = False  # hiding the close button , its cleaner , right click to close
HUE_TEXT_COLORIZED_BY_HUE = False  # currently not working , because of needed conversion from hue to html color

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

# Gump positions
LAUNCHER_X = 200
LAUNCHER_Y = 200
RESULTS_X = 200
RESULTS_Y = 250

# Separate gump IDs for the small launcher button and the results window
LAUNCHER_GUMP_ID = 0x7A11A12
RESULTS_GUMP_ID_BASE = 0x7A11A13 # base ID for cycling results gumps
RESULTS_GUMP_ID_MAX_OFFSET = 10 # cycle through 10 different IDs (0-9)

# Runtime state for cycling gump IDs
_CURRENT_GUMP_OFFSET = 0

# Map item properties to richer text for clarity 
PROPERTY_REMAP = {
    # Accuracy -> Tactics modifier (weapons) — numeric-first formatting , yellow color
    'accurate': '<basefont color=#5CB85C>+ 5 Tactics</basefont> <basefont color=#FFB84D>( Accurate )</basefont>',
    'surpassingly accurate': '<basefont color=#5CB85C>+ 10 Tactics</basefont> <basefont color=#FFB84D>( Surpassingly Accurate )</basefont>',
    'eminently accurate': '<basefont color=#5CB85C>+ 15 Tactics</basefont> <basefont color=#FFB84D>( Eminently Accurate )</basefont>',
    'eminently accurately': '<basefont color=#5CB85C>+ 15 Tactics</basefont> <basefont color=#FFB84D>( Eminently Accurate )</basefont>',  # common typo variant
    'exceedingly accurate': '<basefont color=#5CB85C>+ 20 Tactics</basefont> <basefont color=#FFB84D>( Exceedingly Accurate )</basefont>',
    'supremely accurate': '<basefont color=#5CB85C>+ 25 Tactics</basefont> <basefont color=#FFB84D>( Supremely Accurate )</basefont>',
    # Damage tiers (weapons) — numeric-first formatting , red color
    'ruin': '<basefont color=#FF6B6B>+ 1 Damage</basefont> <basefont color=#FFB84D>( Ruin )</basefont>',
    'might': '<basefont color=#FF6B6B>+ 3 Damage</basefont> <basefont color=#FFB84D>( Might )</basefont>',
    'force': '<basefont color=#FF6B6B>+ 5 Damage</basefont> <basefont color=#FFB84D>( Force )</basefont>',
    'power': '<basefont color=#FF6B6B>+ 7 Damage</basefont> <basefont color=#FFB84D>( Power )</basefont>',
    'vanquishing': '<basefont color=#FF6B6B>+ 9 Damage</basefont> <basefont color=#FFB84D>( Vanquishing )</basefont>',
    'exceptional': '<basefont color=#FF6B6B>+ 20 Damage</basefont> <basefont color=#FFB84D>( Exceptional )</basefont>', # default was +4 damage , unchained = +20
    # Slayer tiers — numeric-first , orange
    'lesser slaying': '<basefont color=#B084FF>+ 15%</basefont> vs type <basefont color=#FFB84D>( Lesser Slayer )</basefont>',
    'slaying': '<basefont color=#B084FF>+ 20%</basefont> vs type <basefont color=#FFB84D>( Slayer )</basefont>',
    'greater slaying': '<basefont color=#B084FF>+ 25%</basefont> vs type <basefont color=#FFB84D>( Greater Slayer )</basefont>',
    # Durability tiers — numeric-first formatting with light grey numbers and medium grey names
    'durable': '<basefont color=#888888>+ 5 Durability</basefont> <basefont color=#AAAAAA>( Durable )</basefont>',
    'substantial': '<basefont color=#888888>+ 10 Durability</basefont> <basefont color=#AAAAAA>( Substantial )</basefont>',
    'massive': '<basefont color=#888888>+ 15 Durability</basefont> <basefont color=#AAAAAA>( Massive )</basefont>',
    'fortified': '<basefont color=#888888>+ 20 Durability</basefont> <basefont color=#AAAAAA>( Fortified )</basefont>',
    'indestructible': '<basefont color=#888888>+ 25 Durability</basefont> <basefont color=#AAAAAA>( Indestructible )</basefont>',
    # Armor Rating tiers — will be dynamically calculated with "Base + Additional AR (Modifier)"  since this is unique to each item
    # These are placeholders - actual values calculated in _compute_ar_modifier_text()
    'defense': 'PLACEHOLDER_AR_MODIFIER',
    'guarding': 'PLACEHOLDER_AR_MODIFIER', 
    'hardening': 'PLACEHOLDER_AR_MODIFIER',
    'fortification': 'PLACEHOLDER_AR_MODIFIER',
    'invulnerable': 'PLACEHOLDER_AR_MODIFIER',
    # Durability tiers — now handled dynamically per-slot in _compute_durability_text() because weapons and armor get different durability
    # Armor Rating tiers — now handled dynamically per-slot in _compute_ar_bonus_text() because each item different amount
    'mastercrafted': '<basefont color=#3FA9FF>Mastercrafted</basefont>',
}

# Accuracy modifier keys to support weapon-type specific skill mapping (bows use Archery instead of Tactics)
ACCURACY_KEYS = {
    'accurate',
    'surpassingly accurate',
    'eminently accurate',
    'eminently accurately',  # common typo variant
    'exceedingly accurate',
    'supremely accurate',
}

# Known items with custom descriptions and colored text (hue-aware via tuple keys)
# Key: (ItemID, Hue or None) -> list[str]
# Use Hue=None to apply to all hues. Add specific entries like (0x0996, 0x005F) to override for that hue only.
KNOWN_ITEMS = {
    (0x1F14, None): [  # Recall Rune (all hues)
        "this rune stone may store a location",
        "using <basefont color=#3FA9FF>Recall</basefont> or <basefont color=#3FA9FF>GateTravel</basefont> will transport the caster to the location stored in the target rune stone",
        "using <basefont color=#FF6B6B>Mark</basefont> sets the caster's location into the target rune stone",
        "rename the rune stone by double clicking it",
        "a <basefont color=#8B4513>RuneBook</basefont> may store multiple rune stones , by dropping them onto the book"
    ],
    (0x0996, None): [  # Mento Seasoning (all hues) , special hue sometimes 0x005F
        "a <basefont color=#228B22>Cooking</basefont> ingredient",
        "used in <basefont color=#32CD32>Bowl of Marinated Rocks</basefont> (Grants 10% physical resistance for 10 min) ",   
        "used in <basefont color=#228B22>Colorful Salad</basefont>, <basefont color=#228B22>Pork Meal</basefont>",   
        "collected from <basefont color=#3FA9FF>Humanoid</basefont> enemies",
    ],
    (0x099F, None): [  # Samuel Secret Sauce (all hues)
        "a <basefont color=#228B22>Cooking</basefont> ingredient",
        "used in <basefont color=#32CD32>Pixie Leg Feast</basefont> (Grants increased spell surging chance for 15 min) ",   
        "used in <basefont color=#32CD32>Charcuterie Board</basefont> (Grants 10% magical resistance for 10 min) ",   
        "used in <basefont color=#228B22>Salmon Meal</basefont>, <basefont color=#228B22>Spicy Fish Bowl</basefont> ",   
        "collected from <basefont color=#3FA9FF>Humanoid</basefont> enemies",
    ],
    (0x3199, None): [  # Brilliant Amber (all hues)
        "a rare gem",
        "collected from <basefont color=#8B4513>Lumberjacking</basefont>",  
    ],
    (0x4FB6, None): [  # N token for raffle (all hues)
        "a token for raffle",
        "turn in at the <basefont color=#3FA9FF>Britain</basefont> bank top right corner",  
    ],
}

# Enchanting materials with their specific enhancement properties (hue-aware via tuple keys)
KNOWN_ENCHANTING_ITEMS = {
    (0x3197, None): [  # Fire Ruby (all hues)
        "a gem for enchanting",
        "used at an <basefont color=#FFB84D>Enchantment Table</basefont> for  <basefont color=#FF6B6B>Weapon Damage</basefont> , and Spellbook <basefont color=#FF6B6B>Fireball</basefont>, and Armor <basefont color=#FF6B6B>Fire Elemental</basefont>",
        "collected from mining and salvaging <basefont color=#3FA9FF>Magical</basefont> items ",
        #imbuing "used for imbuing <basefont color=#5CB85C>Strength</basefont> properties onto armor , and <basefont color=#FFB84D>Hit Fireball</basefont> onto weapon ",
        #crafting "used for crafting the <basefont color=#FF6B6B>Fiery Spellblade</basefont>",
    ],
    (0x573C, None): [  # Arcanic Rune Stone
        "an enchanting material",
        "used at an <basefont color=#FFB84D>Enchantment Table</basefont> for <basefont color=#FF6B6B>Mastery Damage</basefont> (spellbook)",
        "collected from <basefont color=#8B4513>Scavenging</basefont> and salvaging <basefont color=#3FA9FF>Magical</basefont> items ",
    ],
    (0x5748, None): [  # Bottle Ichor
        "an enchanting material",
        "used at an <basefont color=#FFB84D>Enchantment Table</basefont> for <basefont color=#5CB85C>Weapon Lifesteal</basefont>",
        "collected from <basefont color=#8B4513>Scavenging</basefont> and salvaging <basefont color=#3FA9FF>Magical</basefont> items ",
    ],
    (0x3198, None): [  # Blue Diamond
        "an enchanting material",
        "used at an <basefont color=#FFB84D>Enchantment Table</basefont> for <basefont color=#FFB84D>Boss Damage</basefont>",
        "collected from <basefont color=#8B4513>Scavenging</basefont> and salvaging <basefont color=#3FA9FF>Magical</basefont> items ",
    ],
    (0x5742, None): [  # Boura Pelt
        "an enchanting material",
        "used at an <basefont color=#FFB84D>Enchantment Table</basefont> for Armor <basefont color=#8B4513>Giant defense</basefont>, and Spellbook <basefont color=#B084FF>Earth Elemental</basefont>",
        "collected from <basefont color=#8B4513>Scavenging</basefont> and salvaging <basefont color=#3FA9FF>Magical</basefont> items ",
    ],
    (0x573B, None): [  # Crushed Glass
        "an enchanting material",
        "used at an <basefont color=#FFB84D>Enchantment Table</basefont> for <basefont color=#3FA9FF>Blade Spirits</basefont>",
        "collected from <basefont color=#8B4513>Scavenging</basefont> and salvaging <basefont color=#3FA9FF>Magical</basefont> items ",    
    ],
    (0x5732, None): [  # Crystalline (BlackrockCrystaline)
        "an enchanting material",
        "used at an <basefont color=#FFB84D>Enchantment Table</basefont> for <basefont color=#FFB84D>Surging</basefont>",
        "collected from <basefont color=#8B4513>Scavenging</basefont> and salvaging <basefont color=#3FA9FF>Magical</basefont> items ",
    ],
    (0x5721, None): [  # Daemon Claw
        "an enchanting material",
        "used at an <basefont color=#FFB84D>Enchantment Table</basefont> for Weapon <basefont color=#FF6B6B>Savagery</basefont>, and Armor <basefont color=#8B4513>Daemonic defense</basefont>, and Spellbook <basefont color=#B084FF>Summon Daemon</basefont>",
        "collected from <basefont color=#8B4513>Scavenging</basefont> and salvaging <basefont color=#3FA9FF>Magical</basefont> items ",
    ],
    (0x26B4, None): [  # Delicate Scales
        "an enchanting material",
        "used at an <basefont color=#FFB84D>Enchantment Table</basefont> for <basefont color=#5CB85C>Hunter's Luck</basefont>",
        "collected from <basefont color=#8B4513>Scavenging</basefont> and salvaging <basefont color=#3FA9FF>Magical</basefont> items ",
    ],
    (0x5737, None): [  # Elven Fletching
        "an enchanting material",
        "used at an <basefont color=#FFB84D>Enchantment Table</basefont> for Weapon <basefont color=#3FA9FF>Weapon Accuracy</basefont>, and Spellbook <basefont color=#B084FF>Magic Arrow</basefont>",
        "collected from <basefont color=#8B4513>Scavenging</basefont> and salvaging <basefont color=#3FA9FF>Magical</basefont> items ",
    ],
    (0x2DB2, None): [  # Enchanted Essence
        "an enchanting material",
        "used at an <basefont color=#FFB84D>Enchantment Table</basefont> for Spellbook <basefont color=#3FA9FF>Lower Mana Cost</basefont>",
        "collected from <basefont color=#8B4513>Scavenging</basefont> and salvaging <basefont color=#3FA9FF>Magical</basefont> items ",
    ],
    (0x5745, None): [  # Faery Dust
        "an enchanting material",
        "used at an <basefont color=#FFB84D>Enchantment Table</basefont> for Armor <basefont color=#8B4513>Curse Resistance</basefont>, and Spellbook <basefont color=#B084FF>Mind Blast</basefont>",
        "collected from <basefont color=#8B4513>Scavenging</basefont> and salvaging <basefont color=#3FA9FF>Magical</basefont> items ",
    ],
    (0x5726, None): [  # Fey Wings
        "an enchanting material",
        "used at an <basefont color=#FFB84D>Enchantment Table</basefont> for Armor <basefont color=#5CB85C>Evasion</basefont>, and Spellbook <basefont color=#B084FF>Air Elemental</basefont>",
        "collected from <basefont color=#8B4513>Scavenging</basefont> and salvaging <basefont color=#3FA9FF>Magical</basefont> items ",
    ],
    (0x572C, None): [  # Goblin Blood
        "an enchanting material",
        "used at an <basefont color=#FFB84D>Enchantment Table</basefont> for Armor <basefont color=#8B4513>Vermin defense</basefont>",
        "collected from <basefont color=#8B4513>Scavenging</basefont> and salvaging <basefont color=#3FA9FF>Magical</basefont> items ",
    ],
    (0x572D, None): [  # Lava Serpent Crust
        "an enchanting material",
        "used at an <basefont color=#FFB84D>Enchantment Table</basefont> for Armor <basefont color=#8B4513>Draconic defense</basefont>, and Spellbook <basefont color=#B084FF>Flamestrike</basefont>",
        "collected from <basefont color=#8B4513>Scavenging</basefont> and salvaging <basefont color=#3FA9FF>Magical</basefont> items ",
    ],
    (0x0F87, None): [  # Lucky Coin
        "a metal coin of luck used for enchanting",
        "used at an <basefont color=#FFB84D>Enchantment Table</basefont> for Armor <basefont color=#5CB85C>Crafting Luck</basefont>",
        "collected from <basefont color=#8B4513>Scavenging</basefont> and salvaging <basefont color=#3FA9FF>Magical</basefont> items ",
    ],
    (0x3191, None): [  # Luminescent (FungusLuminescent)
        "a glowing mushroom of luminescent fungi",
        "used at an <basefont color=#FFB84D>Enchantment Table</basefont> for Spellbook <basefont color=#3FA9FF>Spell Lifesteal</basefont>",
        "collected from <basefont color=#8B4513>Scavenging</basefont> and salvaging <basefont color=#3FA9FF>Magical</basefont> items ",
        #imbuing "an Imbuing ingredients to imbue the Hit Point Increase, Mana Increase and Stamina Increase property onto items.",
        #crafting "used for crafting the <basefont color=#FF6B6B>Darkglow Potion</basefont>",
    ],
    (0x2DB1, None): [  # Magical Residue
        "an enchanting material",
        "used at an <basefont color=#FFB84D>Enchantment Table</basefont> for Spellbook <basefont color=#3FA9FF>Lower Reagent Cost</basefont>",
        "collected from <basefont color=#8B4513>Scavenging</basefont> and salvaging <basefont color=#3FA9FF>Magical</basefont> items ",
    ],
    (0x3190, None): [  # Parasitic Plant
        "an enchanting material",
        "used at an <basefont color=#FFB84D>Enchantment Table</basefont> for Spellbook <basefont color=#B084FF>Summon Surge</basefont>",
        "collected from <basefont color=#8B4513>Scavenging</basefont> and salvaging <basefont color=#3FA9FF>Magical</basefont> items ",
    ],
    (0x573D, None): [  # Powdered Iron
        "an enchanting material",
        "used at an <basefont color=#FFB84D>Enchantment Table</basefont> for Weapon <basefont color=#FF6B6B>Attack Speed</basefont>, and Spellbook <basefont color=#B084FF>Explosion</basefont>",
        "collected from <basefont color=#8B4513>Scavenging</basefont> and salvaging <basefont color=#3FA9FF>Magical</basefont> items ",
    ],
    (0x5747, None): [  # Raptor Teeth
        "an enchanting material",
        "used at an <basefont color=#FFB84D>Enchantment Table</basefont> for Weapon <basefont color=#FF6B6B>Critical Damage</basefont>",
        "collected from <basefont color=#8B4513>Scavenging</basefont> and salvaging <basefont color=#3FA9FF>Magical</basefont> items ",
    ],
    (0x2DB3, None): [  # Relic Fragment
        "an enchanting material",
        "used at an <basefont color=#FFB84D>Enchantment Table</basefont> for Armor <basefont color=#5CB85C>Archeologist</basefont>, and Spellbook <basefont color=#B084FF>Summon Creature</basefont>",
        "collected from <basefont color=#8B4513>Scavenging</basefont> and salvaging <basefont color=#3FA9FF>Magical</basefont> items ",
    ],
    (0x5736, None): [  # Seed of Renewel
        "an enchanting material",
        "used at an <basefont color=#FFB84D>Enchantment Table</basefont> for Armor <basefont color=#5CB85C>Harvesting Luck</basefont>",
        "collected from <basefont color=#8B4513>Scavenging</basefont> and salvaging <basefont color=#3FA9FF>Magical</basefont> items ",
    ],
    (0x5744, None): [  # Silver Snake
        "an enchanting material",
        "used at an <basefont color=#FFB84D>Enchantment Table</basefont> for Spellbook <basefont color=#3FA9FF>Water Elemental</basefont>",
        "collected from <basefont color=#8B4513>Scavenging</basefont> and salvaging <basefont color=#3FA9FF>Magical</basefont> items ",
    ],
    (0x5746, None): [  # Slith Tongue
        "an enchanting material",
        "used at an <basefont color=#FFB84D>Enchantment Table</basefont> for Armor <basefont color=#8B4513>Poison Resistance</basefont>",
        "collected from <basefont color=#8B4513>Scavenging</basefont> and salvaging <basefont color=#3FA9FF>Magical</basefont> items ",
    ],
    (0x5720, None): [  # Spider Carapace
        "an enchanting material",
        "used at an <basefont color=#FFB84D>Enchantment Table</basefont> for Armor <basefont color=#8B4513>Arachnid defense</basefont>",
        "collected from <basefont color=#8B4513>Scavenging</basefont> and salvaging <basefont color=#3FA9FF>Magical</basefont> items ",
    ],
    (0x5731, None): [  # Undying Flesh
        "a crafting and enchanting material",
        "used at an <basefont color=#FFB84D>Enchantment Table</basefont> for Armor <basefont color=#8B4513>Undead defense</basefont>",
        "used in <basefont color=#FFB84D>Tinkering</basefont> to craft the <basefont color=#CF9FFF>Dark Passage Lantern</basefont> , an important Summoner item",
        "collected from <basefont color=#8B4513>Scavenging</basefont> and salvaging <basefont color=#3FA9FF>Magical</basefont> items ",
    ],
    (0x5722, None): [  # Vial of Vitriol
        "an enchanting material",
        "used at an <basefont color=#FFB84D>Enchantment Table</basefont> for Weapon <basefont color=#FF6B6B>Mage Killer</basefont>, and Spellbook <basefont color=#B084FF>Harm</basefont>, and Armor <basefont color=#8B4513>Infidel Defense</basefont>",
        "collected from <basefont color=#8B4513>Scavenging</basefont> and salvaging <basefont color=#3FA9FF>Magical</basefont> items ",
    ],
    (0x573E, None): [  # Void Orb
        "an enchanting material",
        "used at an <basefont color=#FFB84D>Enchantment Table</basefont> for Weapon <basefont color=#B084FF>Paragon Conversion</basefont>, and Spellbook <basefont color=#B084FF>Energy Vortex</basefont>",
        "collected from <basefont color=#8B4513>Scavenging</basefont> and salvaging <basefont color=#3FA9FF>Magical</basefont> items ",
    ],
    (0x5749, None): [  # Reflective wolf eye
        "an enchanting material",
        "used at an <basefont color=#FFB84D>Enchantment Table</basefont> for Armor <basefont color=#B084FF>Reflective</basefont>",
        "collected from <basefont color=#8B4513>Scavenging</basefont> and salvaging <basefont color=#3FA9FF>Magical</basefont> items ",
    ],
}

# Known items used in quest with custom descriptions and colored text and reward item id
# quest description notes = trying to be minimal here , just enough to tell where to go ( quest giver ) and why ( rewards ) without overload about specifics
# notably choosing not to include the amount needed for turn in ( could be misunderstood that you need all 15 at once )
KNOWN_QUEST_ITEMS = {
    # Key: (ItemID, Hue or None) -> list[str]
    (0x5737, 0x0b42): [  # Robust Harpy Feather
        "a quest item",
        #"a quest item for <basefont color=#3FA9FF>Sky is the Limit</basefont>",
        "<basefont color=#3FA9FF>Canute</basefont> in Britain is offering the reward of <basefont color=#8B4513>Random Runic Component</basefont> or <basefont color=#FFB84D>Treasure Map</basefont> or <basefont color=#32CD32>Food Supply Crate</basefont>",
        #"<basefont color=#3FA9FF>Sky is the Limit</basefont>",
    ],
    (0x241E, None): [  # Elfic Artifact
        "a quest item",
        #"a quest item for <basefont color=#3FA9FF>Stolen Artifacts</basefont>",
        "<basefont color=#3FA9FF>Canute</basefont> in Britain is offering the reward of <basefont color=#8B4513>Random Bulk Resource</basefont> or <basefont color=#FFB84D>3,000 Gold</basefont> or <basefont color=#CF9FFF>Random Mastery Orb</basefont>",
        #"<basefont color=#3FA9FF>Stolen Artifacts</basefont>",
    ],
    (0x1F19, 0x0829): [  # Wrong Champion Crystal
        "a crystal to <basefont color=#FF6B6B>Awaken Champions</basefont>",
        "place at the Altar of <basefont color=#FF6B6B>Wrong</basefont>",
    ],
}

KNOWN_SCROLL_ITEMS = {
    # Key: (ItemID, Hue or None) -> list[str]
    (0x0E34, 0x0808): [  # Spellbook Enhancement Scroll
        "apply to a <basefont color=#FF6B6B>Spellbook</basefont>",
    ],
    (0x0E34, 0x0808): [  # Weapon Enhancement Scroll
        "apply to a <basefont color=#FF6B6B>Weapon</basefont>",
    ],
    (0x0E34, 0x0808): [  # Armor Enhancement Scroll
        "apply to a <basefont color=#FF6B6B>Armor</basefont>",
    ],
}

# Append enchanting items to the main known items dictionary
KNOWN_ITEMS.update(KNOWN_ENCHANTING_ITEMS)
KNOWN_ITEMS.update(KNOWN_QUEST_ITEMS)
KNOWN_ITEMS.update(KNOWN_SCROLL_ITEMS)

# Known artifact weapons with special descriptions (match by ItemID and exact Name)
# Format: {'item_id': int, 'name': str, 'description': str}
# Example: "Aegis Breaker" shares the same ItemID as a normal mace (0x0F5C) but includes an extra description.
KNOWN_ARTIFACT_WEAPON_ITEMS = [
    # SWORDS
    { 'item_id': 0x0F5E, 'name': "Pridestalker's Blade", 'description': '<basefont color=#FFB84D>Stacking Attack Speed (3)</basefont>' },  # broadsword
    { 'item_id': 0x1441, 'name': 'Plague', 'description': '<basefont color=#5CB85C>Disease enemy</basefont>' },                  # cutlass
    { 'item_id': 0x13FF, 'name': "Death's Dance", 'description': '<basefont color=#FF6B6B>Extra damage if enemy injured</basefont>' },          # katana
    { 'item_id': 0x0F61, 'name': 'Zeal', 'description': '<basefont color=#FFB84D>Stacking Attack Speed (3)</basefont>' },                    # longsword
    { 'item_id': 0x13B6, 'name': 'Spectral Scimitar', 'description': '<basefont color=#FF6B6B>Ignore Armor</basefont>' },       # scimitar
    { 'item_id': 0x13B9, 'name': "Blackthorn's Blade", 'description': '<basefont color=#FF6B6B>Stacking Damage (3)</basefont>' },     # viking sword
    { 'item_id': 0x26BB, 'name': 'Breath of the Dead', 'description': '<basefont color=#FF6B6B>Damage at the cost of your own life</basefont>' },      # bone harvester
    { 'item_id': 0x0EC3, 'name': 'Decapitator', 'description': '<basefont color=#FF6B6B>Bleeding damage</basefont>' },             # cleaver
    { 'item_id': 0x13F6, 'name': "Butcher's Carver", 'description': '<basefont color=#FF6B6B>Lifesteal</basefont>' },       # butcher knife
    { 'item_id': 0x0EC4, 'name': 'Deviousness', 'description': '<basefont color=#FF6B6B>Lifesteal</basefont>' },             # skinning knife
    # AXE TYPES
    { 'item_id': 0x0F4D, 'name': 'Demonic Embrace', 'description': '<basefont color=#FF6B6B>Burning damage</basefont>, <basefont color=#FF6B6B>extra vs burning</basefont>' },         # bardiche
    { 'item_id': 0x26BA, 'name': 'Galeforce', 'description': '<basefont color=#FF6B6B>Creates fire field under enemy</basefont>' },               # scythe
    { 'item_id': 0x0F4B, 'name': "The Twins' Rage", 'description': '<basefont color=#FFB84D>Double Attack</basefont>' },        # double axe
    { 'item_id': 0x13B0, 'name': 'Siege Breaker', 'description': '<basefont color=#FF6B6B>Shatters Armor</basefont>' },           # war axe
    { 'item_id': 0x1443, 'name': "Titan's Fall", 'description': '<basefont color=#FFB84D>Stacking Accuracy (3)</basefont>' },           # two handed axe
    { 'item_id': 0x13FB, 'name': "Giant's Will", 'description': '<basefont color=#FF6B6B>Double damage</basefont>' },           # large battle axe
    { 'item_id': 0x0F43, 'name': 'Windseeker', 'description': '<basefont color=#FFB84D>Stacking Attack Speed (3)</basefont>' },              # hatchet
    { 'item_id': 0x143E, 'name': 'Infernal Maw', 'description': '<basefont color=#FF6B6B>Creates fire field under enemy</basefont>' },            # halberd
    { 'item_id': 0x0F45, 'name': "Executioner's Calling", 'description': '<basefont color=#FF6B6B>Extra damage if enemy injured</basefont>' },  # executioner's axe
    { 'item_id': 0x0F47, 'name': 'World Splitter', 'description': '<basefont color=#FF6B6B>Stacking Damage (3)</basefont>' },          # battle axe
    { 'item_id': 0x0F49, 'name': 'Frostbite', 'description': '<basefont color=#FF6B6B>Stacking Damage (3)</basefont>' },               # axe
    { 'item_id': 0x26BD, 'name': 'Lethality', 'description': '<basefont color=#5CB85C>Lethal poison</basefont>' },               # bladed staff
    { 'item_id': 0x2D28, 'name': 'The Condemner', 'description': '<basefont color=#FF6B6B>Stacking Damage (3)</basefont>' },           # ornate axe
    # FENCING
    { 'item_id': 0x1400, 'name': 'Silver Fang', 'description': '<basefont color=#5CB85C>Infect damage</basefont>' },             # kryss
    { 'item_id': 0x0F52, 'name': "Serpent's Fang", 'description': '<basefont color=#FF6B6B>Extra damage vs poisoned</basefont>' },         # dagger
    { 'item_id': 0x1405, 'name': 'Bloodthirster', 'description': '<basefont color=#FF6B6B>Lifesteal</basefont>' },           # war fork
    { 'item_id': 0x0E87, 'name': 'No Current Artifact for Pitchfork', 'description': 'PENDING' }, # pitchfork
    { 'item_id': 0x0F62, 'name': 'Mortal Reminder', 'description': '<basefont color=#3FA9FF>Stun enemy</basefont>' },         # spear
    { 'item_id': 0x26BF, 'name': 'Deathfire Grasp', 'description': '<basefont color=#FF6B6B>Summons a meteor over enemy</basefont>' },         # double bladed staff
    { 'item_id': 0x26BE, 'name': 'The Taskmaster', 'description': '<basefont color=#5CB85C>Poison surrounding enemies</basefont>' },          # pike
    { 'item_id': 0x1403, 'name': 'Corrupted Pike', 'description': '<basefont color=#B084FF>Curses enemy</basefont>' },          # short spear
    # MACE & STAVES
    { 'item_id': 0x13B4, 'name': 'Umbral Shard', 'description': '<basefont color=#FF6B6B>Bleeding damage</basefont>' },            # club
    { 'item_id': 0x0F5C, 'name': 'Aegis Breaker', 'description': '<basefont color=#FF6B6B>Shatters Armor</basefont>' },# Aegis Breaker already present for mace (0x0F5C)
    { 'item_id': 0x143B, 'name': 'Harbringer', 'description': '<basefont color=#FF6B6B>Burning damage</basefont>, <basefont color=#FF6B6B>extra vs burning</basefont>' },              # maul
    { 'item_id': 0x0E86, 'name': 'No Current PickAxe Artifact', 'description': 'PENDING' },# pickaxe
    { 'item_id': 0x143D, 'name': 'The Impaler', 'description': '<basefont color=#FF6B6B>Lifesteal</basefont>' },             # hammer pick
    { 'item_id': 0x1439, 'name': 'Hellclap', 'description': '<basefont color=#FF6B6B>Burning damage</basefont>, <basefont color=#FF6B6B>extra vs burning</basefont>' },                # war hammer
    { 'item_id': 0x1407, 'name': 'Tantrum', 'description': '<basefont color=#3FA9FF>Stun enemy</basefont>' },                 # war mace
    { 'item_id': 0x0E89, 'name': 'Mindcry', 'description': '<basefont color=#FFB84D>Stacking Accuracy (3)</basefont>' },                 # quarter staff
    { 'item_id': 0x13F8, 'name': 'The Peacekeeper', 'description': '<basefont color=#3FA9FF>Calms surrounding creatures</basefont>' },         # gnarled staff
    { 'item_id': 0x0DF0, 'name': 'The Absorber', 'description': '<basefont color=#B084FF>Gain spell reflection</basefont>' },            # black staff
    { 'item_id': 0x0E81, 'name': 'The Shepherd', 'description': 'PENDING' },            # shepherd's crook
    # ARCHERY
    { 'item_id': 0x13B2, 'name': 'Elven Bow', 'description': '<basefont color=#5CB85C>Heals friendly creatures</basefont>' },               # bow
    { 'item_id': 0x13FD, 'name': 'Widow Maker', 'description': '<basefont color=#B084FF>Shadow step</basefont>' },             # heavy crossbow
    { 'item_id': 0x0F50, 'name': 'Repugnance', 'description': '<basefont color=#FFB84D>Knockback</basefont>, <basefont color=#FF6B6B>more damage if pinned</basefont>' },              # crossbow
    { 'item_id': 0x26C2, 'name': 'The Dryad Bow', 'description': '<basefont color=#FFB84D>Distance based damage</basefont>' },           # composite bow
    { 'item_id': 0x26C3, 'name': 'Wraith Whisperer', 'description': '<basefont color=#FF6B6B>Ignore armor</basefont>' },        # repeating crossbow
    { 'item_id': 0x27A5, 'name': 'Bow of Infinite Swarms', 'description': '<basefont color=#FFB84D>Stacking Attack speed (3)</basefont>' },  # yumi
]

# Colors (Razor Enhanced gump label hues)
COLORS = {
    'title': 68,       # blue
    'label': 1153,     # light gray
    'ok': 63,          # green
    'warn': 53,        # yellow
    'bad': 33,         # red
    'cat': 90,         # cyan
    'info': 1153,      # light gray for info messages
    'success': 63,     # green for success messages
}

# Define which properties are considered "modifiers" that should be displayed first
MODIFIER_PROPERTIES = {
    'accurate', 'surpassingly accurate', 'eminently accurate', 'eminently accurately', 
    'exceedingly accurate', 'supremely accurate',
    'ruin', 'might', 'force', 'power', 'vanquishing', 'exceptional',
    'durable', 'substantial', 'massive', 'fortified', 'indestructible',
    'defense', 'guarding', 'hardening', 'fortification', 'invulnerable',
}

MATERIAL_PROPERTIES = {
    'silver', 'shadow', 'copper', 'bronze', 'golden', 'agapite', 'verite', 'valorite',
    'spined', 'horned', 'barbed',
    'oak', 'ash', 'yew', 'heartwood', 'bloodwood', 'frostwood'
}

# Modifier color categories
MODIFIER_COLORS = {
    'durability': '#CD853F',  # Light brown for durability modifiers
    'damage': '#FF8C00',      # Orange for damage modifiers  
    'skill': '#FFD700',       # Yellow for skill modifiers
    'default': '#CCCCCC'      # Default gray for other modifiers
}

# Durability tier bonuses (fixed values for both weapons and armor)
DURABILITY_TIERS = {
    'durable': 5,
    'substantial': 10,
    'massive': 15,
    'fortified': 20,
    'indestructible': 25,
}

# Armor Rating tier bonuses , these are rough estimates for fallback , the actual data is in ARMOR_DATA_BY_ITEMID
AR_BONUS_TIERS = {
    'defense':        {'neck_hands': 0.4, 'arms_head_legs': 0.7, 'body': 2.2, 'shield': 1, 'pct': 5},
    'guarding':       {'neck_hands': 0.7, 'arms_head_legs': 1.4, 'body': 4.4, 'shield': 1.5, 'pct': 10},
    'hardening':      {'neck_hands': 1.1, 'arms_head_legs': 2.1, 'body': 6.6, 'shield': 2, 'pct': 15},
    'fortification':  {'neck_hands': 1.4, 'arms_head_legs': 2.8, 'body': 8.8, 'shield': 4, 'pct': 20},
    'invulnerable':   {'neck_hands': 1.8, 'arms_head_legs': 3.5, 'body': 11.0, 'shield': 7, 'pct': 25},
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
# Equipment data mapping (by ItemID)
# Includes: Type, Layer, Base AR, AR modifiers, DEX penalty
# Source: Incomplete DATA_item_armor_data_to_wiki.py results ( 137 / 432 ) items recorded ~30%
ARMOR_DATA_BY_ITEMID = {
    # Comprehensive armor data from testing analysis
    # Format: item_id: {'type': str, 'layer': str, 'name': str, 'base_ar': int, 'ar_modifiers': dict, 'dex_penalty': int}
    
    # --- Platemail Armor ---
    0x140C: {'type': 'Platemail', 'layer': 'Head', 'name': 'bascinet', 'base_ar': 3, 'ar_modifiers': {}, 'dex_penalty': 0},
    0x1408: {'type': 'Platemail', 'layer': 'Head', 'name': 'close helmet', 'base_ar': 4, 'ar_modifiers': {'Defense': 6, 'Guarding': 7}, 'dex_penalty': 0},
    0x1C04: {'type': 'Platemail', 'layer': 'InnerTorso', 'name': 'female plate', 'base_ar': 10, 'ar_modifiers': {'Defense': 16, 'Hardening': 19}, 'dex_penalty': -5},
    0x140A: {'type': 'Platemail', 'layer': 'Head', 'name': 'helmet', 'base_ar': 4, 'ar_modifiers': {'Defense': 6, 'Hardening': 8}, 'dex_penalty': 0},
    0x140E: {'type': 'Platemail', 'layer': 'Head', 'name': 'norse helm', 'base_ar': 4, 'ar_modifiers': {}, 'dex_penalty': 0},
    0x1F0B: {'type': 'Platemail', 'layer': 'Head', 'name': 'orc helm', 'base_ar': 0, 'ar_modifiers': {'Guarding': 6}, 'dex_penalty': 0},
    0x1412: {'type': 'Platemail', 'layer': 'Head', 'name': 'plate helm', 'base_ar': 4, 'ar_modifiers': {'Defense': 7, 'Fortification': 9, 'Guarding': 7}, 'dex_penalty': -1},
    0x1410: {'type': 'Platemail', 'layer': 'Arms', 'name': 'platemail arms', 'base_ar': 5, 'ar_modifiers': {'Defense': 7, 'Fortification': 9, 'Guarding': 8}, 'dex_penalty': -2},
    0x1413: {'type': 'Platemail', 'layer': 'Gloves', 'name': 'platemail gloves', 'base_ar': 2, 'ar_modifiers': {'Fortification': 4, 'Guarding': 4}, 'dex_penalty': -2},
    0x1414: {'type': 'Platemail', 'layer': 'Neck', 'name': 'platemail gorget', 'base_ar': 2, 'ar_modifiers': {'Defense': 3}, 'dex_penalty': -1},
    0x1411: {'type': 'Platemail', 'layer': 'Pants', 'name': 'platemail legs', 'base_ar': 7, 'ar_modifiers': {'Fortification': 14, 'Guarding': 11}, 'dex_penalty': -6},
    0x2779: {'type': 'Platemail', 'layer': 'Neck', 'name': 'platemail mempo', 'base_ar': 0, 'ar_modifiers': {'Defense': 1}, 'dex_penalty': 0},
    0x1415: {'type': 'Platemail', 'layer': 'InnerTorso', 'name': 'platemail tunic', 'base_ar': 11, 'ar_modifiers': {'Defense': 16, 'Fortification': 22, 'Guarding': 18}, 'dex_penalty': -8},
    
    # --- Bone Armor ---
    0x144F: {'type': 'Bone', 'layer': 'InnerTorso', 'name': 'bone armor', 'base_ar': 11, 'ar_modifiers': {'Defense': 16, 'Guarding': 18}, 'dex_penalty': -6},
    0x144E: {'type': 'Bone', 'layer': 'Arms', 'name': 'bone arms', 'base_ar': 0, 'ar_modifiers': {'Defense': 7}, 'dex_penalty': -2},
    0x1450: {'type': 'Bone', 'layer': 'Gloves', 'name': 'bone gloves', 'base_ar': 2, 'ar_modifiers': {'Guarding': 4, 'Hardening': 4}, 'dex_penalty': -1},
    0x1451: {'type': 'Bone', 'layer': 'Head', 'name': 'bone helmet', 'base_ar': 0, 'ar_modifiers': {'Hardening': 8}, 'dex_penalty': 0},
    0x1452: {'type': 'Bone', 'layer': 'Pants', 'name': 'bone leggings', 'base_ar': 0, 'ar_modifiers': {'Defense': 10}, 'dex_penalty': -4},
    
    # --- Chainmail Armor ---
    0x13BB: {'type': 'Chainmail', 'layer': 'Head', 'name': 'chainmail coif', 'base_ar': 4, 'ar_modifiers': {}, 'dex_penalty': 0},
    0x13BE: {'type': 'Chainmail', 'layer': 'Pants', 'name': 'chainmail leggings', 'base_ar': 6, 'ar_modifiers': {}, 'dex_penalty': -3},
    0x13BF: {'type': 'Chainmail', 'layer': 'InnerTorso', 'name': 'chainmail tunic', 'base_ar': 10, 'ar_modifiers': {'Defense': 15, 'Guarding': 17}, 'dex_penalty': -5},
    
    # --- Leather Armor ---
    0x1C06: {'type': 'Leather', 'layer': 'InnerTorso', 'name': 'female leather armor', 'base_ar': 5, 'ar_modifiers': {'Defense': 10, 'Fortification': 15, 'Guarding': 12}, 'dex_penalty': 0},
    0x1C0A: {'type': 'Leather', 'layer': 'InnerTorso', 'name': 'leather bustier', 'base_ar': 5, 'ar_modifiers': {'Defense': 10}, 'dex_penalty': 0},
    0x1DB9: {'type': 'Leather', 'layer': 'Head', 'name': 'leather cap', 'base_ar': 2, 'ar_modifiers': {}, 'dex_penalty': 0},
    0x13C6: {'type': 'Leather', 'layer': 'Gloves', 'name': 'leather gloves', 'base_ar': 1, 'ar_modifiers': {'Defense': 2, 'Fortification': 3}, 'dex_penalty': 0},
    0x13C7: {'type': 'Leather', 'layer': 'Neck', 'name': 'leather gorget', 'base_ar': 1, 'ar_modifiers': {'Defense': 2, 'Guarding': 2}, 'dex_penalty': 0},
    0x13CB: {'type': 'Leather', 'layer': 'Pants', 'name': 'leather leggings', 'base_ar': 3, 'ar_modifiers': {'Guarding': 7}, 'dex_penalty': 0},
    0x277A: {'type': 'Leather', 'layer': 'Neck', 'name': 'leather mempo', 'base_ar': 0, 'ar_modifiers': {'Hardening': 2}, 'dex_penalty': 0},
    0x1C00: {'type': 'Leather', 'layer': 'Pants', 'name': 'leather shorts', 'base_ar': 3, 'ar_modifiers': {'Hardening': 8}, 'dex_penalty': 0},
    0x1C08: {'type': 'Leather', 'layer': 'Pants', 'name': 'leather skirt', 'base_ar': 3, 'ar_modifiers': {'Defense': 6, 'Fortification': 9, 'Guarding': 7, 'Hardening': 8}, 'dex_penalty': 0},
    0x13CD: {'type': 'Leather', 'layer': 'Arms', 'name': 'leather sleeves', 'base_ar': 2, 'ar_modifiers': {'Defense': 4, 'Fortification': 6, 'Hardening': 6, 'Invulnerable': 7}, 'dex_penalty': 0},
    0x13CC: {'type': 'Leather', 'layer': 'InnerTorso', 'name': 'leather tunic', 'base_ar': 5, 'ar_modifiers': {'Defense': 10}, 'dex_penalty': 0},
    
    # --- Ringmail Armor ---
    0x13EB: {'type': 'Ringmail', 'layer': 'Gloves', 'name': 'ringmail gloves', 'base_ar': 2, 'ar_modifiers': {}, 'dex_penalty': -1},
    0x13F0: {'type': 'Ringmail', 'layer': 'Pants', 'name': 'ringmail leggings', 'base_ar': 5, 'ar_modifiers': {'Defense': 8}, 'dex_penalty': -1},
    0x13EE: {'type': 'Ringmail', 'layer': 'Arms', 'name': 'ringmail sleeves', 'base_ar': 0, 'ar_modifiers': {'Defense': 6, 'Guarding': 6}, 'dex_penalty': -1},
    0x13EC: {'type': 'Ringmail', 'layer': 'InnerTorso', 'name': 'ringmail tunic', 'base_ar': 8, 'ar_modifiers': {}, 'dex_penalty': -2},
    
    # --- Studded Armor ---
    0x1C02: {'type': 'Studded', 'layer': 'InnerTorso', 'name': 'studded armor', 'base_ar': 6, 'ar_modifiers': {'Hardening': 14}, 'dex_penalty': 0},
    0x1C0C: {'type': 'Studded', 'layer': 'InnerTorso', 'name': 'studded bustier', 'base_ar': 6, 'ar_modifiers': {'Hardening': 14}, 'dex_penalty': 0},
    0x13D5: {'type': 'Studded', 'layer': 'Gloves', 'name': 'studded gloves', 'base_ar': 1, 'ar_modifiers': {'Guarding': 3}, 'dex_penalty': 0},
    0x13D6: {'type': 'Studded', 'layer': 'Neck', 'name': 'studded gorget', 'base_ar': 1, 'ar_modifiers': {'Defense': 2}, 'dex_penalty': 0},
    0x13DA: {'type': 'Studded', 'layer': 'Pants', 'name': 'studded leggings', 'base_ar': 4, 'ar_modifiers': {}, 'dex_penalty': 0},
    0x279D: {'type': 'Studded', 'layer': 'Neck', 'name': 'studded mempo', 'base_ar': 0, 'ar_modifiers': {'Guarding': 2}, 'dex_penalty': 0},
    0x13DC: {'type': 'Studded', 'layer': 'Arms', 'name': 'studded sleeves', 'base_ar': 2, 'ar_modifiers': {'Defense': 5, 'Guarding': 5}, 'dex_penalty': 0},
    0x13DB: {'type': 'Studded', 'layer': 'InnerTorso', 'name': 'studded tunic', 'base_ar': 8, 'ar_modifiers': {'Defense': 11, 'Hardening': 14}, 'dex_penalty': 0},
    
    # --- Other Armor ---
    0x1718: {'type': 'Other', 'layer': 'Head', 'name': "wizard's hat", 'base_ar': 0, 'ar_modifiers': {'Defense': 5}, 'dex_penalty': 0},
    
    # --- Shields ---
    0x1BC4: {'type': 'Shield', 'layer': 'LeftHand', 'name': 'Order shield', 'base_ar': 0, 'ar_modifiers': {'Fortification': 27}, 'dex_penalty': 0},
    0x1B72: {'type': 'Shield', 'layer': 'LeftHand', 'name': 'bronze shield', 'base_ar': 1, 'ar_modifiers': {'Defense': 1, 'Hardening': 1}, 'dex_penalty': 0},
    0x1B73: {'type': 'Shield', 'layer': 'LeftHand', 'name': 'buckler', 'base_ar': 1, 'ar_modifiers': {}, 'dex_penalty': 0},
    0x1B76: {'type': 'Shield', 'layer': 'LeftHand', 'name': 'heater shield', 'base_ar': 1, 'ar_modifiers': {}, 'dex_penalty': 0},
    0x1B77: {'type': 'Shield', 'layer': 'LeftHand', 'name': 'metal kite shield', 'base_ar': 1, 'ar_modifiers': {'Hardening': 1}, 'dex_penalty': 0},
    0x1B74: {'type': 'Shield', 'layer': 'LeftHand', 'name': 'metal shield', 'base_ar': 1, 'ar_modifiers': {'Defense': 1}, 'dex_penalty': 0},
    0x1B78: {'type': 'Shield', 'layer': 'LeftHand', 'name': 'tear kite shield', 'base_ar': 1, 'ar_modifiers': {'Hardening': 1}, 'dex_penalty': 0},
    0x1B7A: {'type': 'Shield', 'layer': 'LeftHand', 'name': 'wooden shield', 'base_ar': 1, 'ar_modifiers': {'Hardening': 1}, 'dex_penalty': 0},
}

# Weapon data dictionary (by ItemID)
# Format: item_id: {'type': str, 'hands': str, 'name': str, 'skill': str}
WEAPON_DATA_BY_ITEMID = {
    # --- Axes ---
    0x0F49: {'type': 'Axe', 'hands': '1h', 'name': 'axe', 'skill': 'Swordsmanship'},
    0x0F47: {'type': 'Axe', 'hands': '2h', 'name': 'battle axe', 'skill': 'Swordsmanship'},
    0x0F4B: {'type': 'Axe', 'hands': '2h', 'name': 'double axe', 'skill': 'Swordsmanship'},
    0x0F45: {'type': 'Axe', 'hands': '2h', 'name': "executioner's axe", 'skill': 'Swordsmanship'},
    0x0F43: {'type': 'Axe', 'hands': '1h', 'name': 'hatchet', 'skill': 'Swordsmanship'},
    0x13FB: {'type': 'Axe', 'hands': '2h', 'name': 'large battle axe', 'skill': 'Swordsmanship'},
    0x1443: {'type': 'Axe', 'hands': '2h', 'name': 'two handed axe', 'skill': 'Swordsmanship'},
    0x13B0: {'type': 'Axe', 'hands': '1h', 'name': 'war axe', 'skill': 'Swordsmanship'},

    # --- Swords ---
    0x0F5E: {'type': 'Sword', 'hands': '1h', 'name': 'broadsword', 'skill': 'Swordsmanship'},
    0x1441: {'type': 'Sword', 'hands': '1h', 'name': 'cutlass', 'skill': 'Swordsmanship'},
    0x13FF: {'type': 'Sword', 'hands': '1h', 'name': 'katana', 'skill': 'Swordsmanship'},
    0x0F61: {'type': 'Sword', 'hands': '1h', 'name': 'longsword', 'skill': 'Swordsmanship'},
    0x13B6: {'type': 'Sword', 'hands': '1h', 'name': 'scimitar', 'skill': 'Swordsmanship'},
    0x13B9: {'type': 'Sword', 'hands': '1h', 'name': 'viking sword', 'skill': 'Swordsmanship'},

    # --- Maces & Staves ---
    0x13B4: {'type': 'Mace', 'hands': '1h', 'name': 'club', 'skill': 'Mace Fighting'},
    0x143D: {'type': 'Mace', 'hands': '1h', 'name': 'hammer pick', 'skill': 'Mace Fighting'},
    0x0F5C: {'type': 'Mace', 'hands': '1h', 'name': 'mace', 'skill': 'Mace Fighting'},
    0x143B: {'type': 'Mace', 'hands': '2h', 'name': 'maul', 'skill': 'Mace Fighting'},
    0x1439: {'type': 'Mace', 'hands': '2h', 'name': 'war hammer', 'skill': 'Mace Fighting'},
    0x1407: {'type': 'Mace', 'hands': '1h', 'name': 'war mace', 'skill': 'Mace Fighting'},
    0x0DF0: {'type': 'Staff', 'hands': '2h', 'name': 'black staff', 'skill': 'Mace Fighting'},
    0x13F8: {'type': 'Staff', 'hands': '2h', 'name': 'gnarled staff', 'skill': 'Mace Fighting'},
    0x0E89: {'type': 'Staff', 'hands': '2h', 'name': 'quarter staff', 'skill': 'Mace Fighting'},

    # --- Fencing ---
    0x0EC3: {'type': 'Sword', 'hands': '1h', 'name': 'cleaver', 'skill': 'Sword'}, # originally fencing moved to swords
    0x0EC4: {'type': 'Sword', 'hands': '1h', 'name': 'skinning knife', 'skill': 'Sword'}, # originally fencing moved to swords
    0x13F6: {'type': 'Sword', 'hands': '1h', 'name': 'butcher knife', 'skill': 'Sword'}, # originally fencing moved to swords
    0x0F52: {'type': 'Fencing', 'hands': '1h', 'name': 'dagger', 'skill': 'Fencing'},
    0x0F62: {'type': 'Fencing', 'hands': '2h', 'name': 'spear', 'skill': 'Fencing'},
    0x1403: {'type': 'Fencing', 'hands': '2h', 'name': 'short spear', 'skill': 'Fencing'},
    0x1405: {'type': 'Fencing', 'hands': '1h', 'name': 'war fork', 'skill': 'Fencing'},
    0x1401: {'type': 'Fencing', 'hands': '1h', 'name': 'kryss', 'skill': 'Fencing'},

    # --- Archery ---
    0x13B2: {'type': 'Bow', 'hands': '2h', 'name': 'bow', 'skill': 'Archery'},
    0x13B1: {'type': 'Bow', 'hands': '2h', 'name': 'bow', 'skill': 'Archery'},
    0x26C2: {'type': 'Bow', 'hands': '2h', 'name': 'composite bow', 'skill': 'Archery'},
    0x0F50: {'type': 'Crossbow', 'hands': '2h', 'name': 'crossbow', 'skill': 'Archery'},
    0x13FD: {'type': 'Crossbow', 'hands': '2h', 'name': 'heavy crossbow', 'skill': 'Archery'},
    0x26C3: {'type': 'Crossbow', 'hands': '2h', 'name': 'repeating crossbow', 'skill': 'Archery'},
    0x2D1F: {'type': 'Bow', 'hands': '2h', 'name': 'magical shortbow', 'skill': 'Archery'},

    # --- Mixed/Special ---
    0x0E86: {'type': 'Tool', 'hands': '1h', 'name': 'pickaxe', 'skill': 'Mining'},
    0x0DF2: {'type': 'Wand', 'hands': '1h', 'name': 'magic wand', 'skill': 'Magery'},
    0x26BC: {'type': 'Scepter', 'hands': '1h', 'name': 'scepter', 'skill': 'Mace Fighting'},
    0x0F4D: {'type': 'Polearm', 'hands': '2h', 'name': 'bardiche', 'skill': 'Swordsmanship'},
    0x143E: {'type': 'Polearm', 'hands': '2h', 'name': 'halberd', 'skill': 'Swordsmanship'},
    0x26BA: {'type': 'Polearm', 'hands': '2h', 'name': 'scythe', 'skill': 'Mace Fighting'},
    0x26BD: {'type': 'Staff', 'hands': '2h', 'name': 'bladed staff', 'skill': 'Swordsmanship'},
    0x26BF: {'type': 'Staff', 'hands': '2h', 'name': 'double bladed staff', 'skill': 'Swordsmanship'},
    0x26BE: {'type': 'Polearm', 'hands': '2h', 'name': 'pike', 'skill': 'Fencing'},
    0x0E87: {'type': 'Tool', 'hands': '2h', 'name': 'pitchfork', 'skill': 'Fencing'},
    0x0E81: {'type': 'Staff', 'hands': '2h', 'name': "shepherd's crook", 'skill': 'Mace Fighting'},
    0x26BB: {'type': 'Polearm', 'hands': '2h', 'name': 'bone harvester', 'skill': 'Swordsmanship'},
    0x26C5: {'type': 'Polearm', 'hands': '2h', 'name': 'bone harvester', 'skill': 'Swordsmanship'},
    0x26C1: {'type': 'Sword', 'hands': '1h', 'name': 'crescent blade', 'skill': 'Swordsmanship'},
    0x1400: {'type': 'Fencing', 'hands': '1h', 'name': 'kryss', 'skill': 'Fencing'},
    0x26C0: {'type': 'Polearm', 'hands': '2h', 'name': 'lance', 'skill': 'Fencing'},
    0x27A8: {'type': 'Sword', 'hands': '1h', 'name': 'bokuto', 'skill': 'Swordsmanship'},
    0x27A9: {'type': 'Sword', 'hands': '2h', 'name': 'daisho', 'skill': 'Swordsmanship'},
    0x27AD: {'type': 'Fencing', 'hands': '1h', 'name': 'kama', 'skill': 'Fencing'},
    0x27A7: {'type': 'Fencing', 'hands': '2h', 'name': 'lajatang', 'skill': 'Fencing'},
    0x27A2: {'type': 'Sword', 'hands': '2h', 'name': 'no-dachi', 'skill': 'Swordsmanship'},
    0x27AE: {'type': 'Fencing', 'hands': '1h', 'name': 'nunchaku', 'skill': 'Fencing'},
    0x27AF: {'type': 'Fencing', 'hands': '1h', 'name': 'sai', 'skill': 'Fencing'},
    0x27AB: {'type': 'Fencing', 'hands': '1h', 'name': 'tekagi', 'skill': 'Fencing'},
    0x27A3: {'type': 'Fencing', 'hands': '1h', 'name': 'tessen', 'skill': 'Fencing'},
    0x27A6: {'type': 'Mace', 'hands': '2h', 'name': 'tetsubo', 'skill': 'Mace Fighting'},
    0x27A4: {'type': 'Sword', 'hands': '1h', 'name': 'wakizashi', 'skill': 'Swordsmanship'},
    0x27A5: {'type': 'Bow', 'hands': '2h', 'name': 'yumi', 'skill': 'Archery'},
    0x2D21: {'type': 'Fencing', 'hands': '1h', 'name': 'assassin spike', 'skill': 'Fencing'},
    0x2D24: {'type': 'Mace', 'hands': '1h', 'name': 'diamond mace', 'skill': 'Mace Fighting'},
    0x2D1E: {'type': 'Bow', 'hands': '2h', 'name': 'elven composite longbow', 'skill': 'Archery'},
    0x2D35: {'type': 'Sword', 'hands': '1h', 'name': 'elven machete', 'skill': 'Swordsmanship'},
    0x2D20: {'type': 'Sword', 'hands': '1h', 'name': 'elven spellblade', 'skill': 'Swordsmanship'},
    0x2D22: {'type': 'Sword', 'hands': '1h', 'name': 'leafblade', 'skill': 'Swordsmanship'},
    0x2D2B: {'type': 'Bow', 'hands': '2h', 'name': 'magical shortbow', 'skill': 'Archery'},
    0x2D28: {'type': 'Axe', 'hands': '2h', 'name': 'ornate axe', 'skill': 'Swordsmanship'},
    0x2D33: {'type': 'Sword', 'hands': '1h', 'name': 'radiant scimitar', 'skill': 'Swordsmanship'},
    0x2D32: {'type': 'Sword', 'hands': '1h', 'name': 'rune blade', 'skill': 'Swordsmanship'},
    0x2D2F: {'type': 'Axe', 'hands': '2h', 'name': 'war cleaver', 'skill': 'Swordsmanship'},
    0x2D25: {'type': 'Staff', 'hands': '2h', 'name': 'wild staff', 'skill': 'Mace Fighting'},
    0x406B: {'type': 'Throwing', 'hands': '2h', 'name': 'soul glaive', 'skill': 'Throwing'},
    0x406C: {'type': 'Throwing', 'hands': '2h', 'name': 'cyclone', 'skill': 'Throwing'},
    0x4067: {'type': 'Throwing', 'hands': '2h', 'name': 'boomerang', 'skill': 'Throwing'},
    0x08FE: {'type': 'Sword', 'hands': '1h', 'name': 'bloodblade', 'skill': 'Swordsmanship'},
    0x0903: {'type': 'Mace', 'hands': '1h', 'name': 'disc mace', 'skill': 'Mace Fighting'},
    0x090B: {'type': 'Sword', 'hands': '1h', 'name': 'dread sword', 'skill': 'Swordsmanship'},
    0x0904: {'type': 'Fencing', 'hands': '2h', 'name': 'dual pointed spear', 'skill': 'Fencing'},
    0x08FD: {'type': 'Axe', 'hands': '2h', 'name': 'dual short axes', 'skill': 'Swordsmanship'},
    0x48B2: {'type': 'Axe', 'hands': '2h', 'name': 'gargish axe', 'skill': 'Swordsmanship'},
    0x48B4: {'type': 'Polearm', 'hands': '2h', 'name': 'gargish bardiche', 'skill': 'Swordsmanship'},
    0x48B0: {'type': 'Axe', 'hands': '2h', 'name': 'gargish battle axe', 'skill': 'Swordsmanship'},
    0x48C6: {'type': 'Polearm', 'hands': '2h', 'name': 'gargish bone harvester', 'skill': 'Swordsmanship'},
    0x48B6: {'type': 'Fencing', 'hands': '1h', 'name': 'gargish butcher knife', 'skill': 'Fencing'},
    0x48AE: {'type': 'Fencing', 'hands': '1h', 'name': 'gargish cleaver', 'skill': 'Fencing'},
    0x0902: {'type': 'Fencing', 'hands': '1h', 'name': 'gargish dagger', 'skill': 'Fencing'},
    0x48D0: {'type': 'Sword', 'hands': '2h', 'name': 'gargish daisho', 'skill': 'Swordsmanship'},
    0x48B8: {'type': 'Staff', 'hands': '2h', 'name': 'gargish gnarled staff', 'skill': 'Mace Fighting'},
    0x48BA: {'type': 'Sword', 'hands': '1h', 'name': 'gargish katana', 'skill': 'Swordsmanship'},
    0x48BC: {'type': 'Fencing', 'hands': '1h', 'name': 'gargish kryss', 'skill': 'Fencing'},
    0x48CA: {'type': 'Polearm', 'hands': '2h', 'name': 'gargish lance', 'skill': 'Fencing'},
    0x48C2: {'type': 'Mace', 'hands': '2h', 'name': 'gargish maul', 'skill': 'Mace Fighting'},
    0x48C8: {'type': 'Polearm', 'hands': '2h', 'name': 'gargish pike', 'skill': 'Fencing'},
    0x48C4: {'type': 'Polearm', 'hands': '2h', 'name': 'gargish scythe', 'skill': 'Mace Fighting'},
    0x0908: {'type': 'Sword', 'hands': '1h', 'name': 'gargish talwar', 'skill': 'Swordsmanship'},
    0x48CE: {'type': 'Fencing', 'hands': '1h', 'name': 'gargish tekagi', 'skill': 'Fencing'},
    0x48CC: {'type': 'Fencing', 'hands': '1h', 'name': 'gargish tessen', 'skill': 'Fencing'},
    0x48C0: {'type': 'Mace', 'hands': '2h', 'name': 'gargish war hammer', 'skill': 'Mace Fighting'},
    0x0905: {'type': 'Staff', 'hands': '2h', 'name': 'glass staff', 'skill': 'Mace Fighting'},
    0x090C: {'type': 'Sword', 'hands': '1h', 'name': 'glass sword', 'skill': 'Swordsmanship'},
    0x0906: {'type': 'Staff', 'hands': '2h', 'name': 'serpentstone staff', 'skill': 'Mace Fighting'},
    0x0907: {'type': 'Sword', 'hands': '1h', 'name': 'shortblade', 'skill': 'Swordsmanship'},
    0x0900: {'type': 'Sword', 'hands': '1h', 'name': 'stone war sword', 'skill': 'Swordsmanship'},
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
        Misc.SendMessage(f"[WAILA] {message}", color)
    except Exception:
        try:
            print(f"[WAILA] {message}")
        except Exception:
            pass

def resolve_artifact_weapon_description(item_id: int, item_name: str):
    """Return artifact description if this item matches a known artifact weapon by id and name.
    Matching is case-insensitive on name and exact on item_id.
    """
    try:
        iid = int(item_id)
    except Exception:
        iid = item_id
    nm = (item_name or '').strip()
    if not nm or iid is None:
        return None
    low = nm.lower()
    try:
        for entry in (KNOWN_ARTIFACT_WEAPON_ITEMS or []):
            try:
                if int(entry.get('item_id')) == iid and str(entry.get('name', '')).strip().lower() == low:
                    return entry.get('description')
            except Exception:
                continue
    except Exception:
        pass
    return None

def get_modifier_color_category(property_text):
    """Determine the color category for a modifier based on its content."""
    text_lower = property_text.lower()
    
    # Durability modifiers (light brown)
    if any(word in text_lower for word in ['durability', 'durable', 'substantial', 'massive', 'fortified', 'indestructible']):
        return 'durability'
    
    # Damage modifiers (orange)
    if any(word in text_lower for word in ['damage', 'ruin', 'might', 'force', 'power', 'vanquishing']):
        return 'damage'
    
    # Skill modifiers (yellow) - includes tactics, skills, and other stat bonuses
    if any(word in text_lower for word in ['tactics', 'skill', 'accurate', 'anatomy', 'archery', 'fencing', 'mace', 'swords', 'wrestling']):
        return 'skill'
    
    # Default for other modifiers
    return 'default'

def format_modifier_text(property_text):
    """Format modifier text with appropriate colors and extract numeric values."""
    color_category = get_modifier_color_category(property_text)
    color = MODIFIER_COLORS[color_category]
    
    # Look for patterns like "+5", "+ 10", "20", etc.
    number_match = re.search(r'[+\-]?\s*(\d+)', property_text)
    if number_match:
        number = number_match.group(1)
        # Replace the number in the text with colored version
        formatted_text = re.sub(
            r'([+\-]?\s*)(\d+)',
            f'<basefont color={color}>\\1{number}</basefont>',
            property_text,
            count=1
        )
        return formatted_text
    else:
        # No number found, just color the whole text
        return f'<basefont color={color}>{property_text}</basefont>'

def get_armor_data(item_id):
    """Return armor data for an item id, or None if unknown."""
    try:
        return ARMOR_DATA_BY_ITEMID.get(int(item_id))
    except Exception:
        return ARMOR_DATA_BY_ITEMID.get(item_id)

def get_weapon_data(item_id):
    """Return weapon data for an item id, or None if unknown."""
    try:
        return WEAPON_DATA_BY_ITEMID.get(int(item_id))
    except Exception:
        return WEAPON_DATA_BY_ITEMID.get(item_id)

def get_equip_slot(item_id):
    """Return equip layer for an item id, or None if unknown."""
    armor_data = get_armor_data(item_id)
    if armor_data:
        return armor_data.get('layer')
    return None

def is_weapon(item_id):
    """Check if an item is a weapon."""
    return get_weapon_data(item_id) is not None

def is_armor(item_id):
    """Check if an item is armor or shield."""
    return get_armor_data(item_id) is not None

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

def _resolve_known_item_lines(item_id: int, item_hue: int, treat_hue_as_agnostic: bool = False) -> list:
    """Resolve known item description lines using the new tuple-key system only.

    Priority:
      1) If treat_hue_as_agnostic: (item_id, None)
      2) Else: if hue in (0, None) -> (item_id, None)
      3) Else: (item_id, hue) -> (item_id, None)
      4) Scan fallback over tuple keys for this item_id
    """
    # 1/2. Tuple-key lookups
    try:
        iid = int(item_id)
    except Exception:
        iid = item_id
    # Use flexible int/hex conversion for hue
    hue = _to_int_id(item_hue)
    if hue is None:
        try:
            hue = int(item_hue)
        except Exception:
            hue = 0

    # When hue is agnostic (weapons/armor), skip hue-specific
    if treat_hue_as_agnostic:
        if (iid, None) in KNOWN_ITEMS and isinstance(KNOWN_ITEMS[(iid, None)], list):
            return KNOWN_ITEMS[(iid, None)]
    else:
        # If hue is effectively "no hue" (0/None), prefer the generic (iid, None)
        if hue in (0, None):
            if (iid, None) in KNOWN_ITEMS and isinstance(KNOWN_ITEMS[(iid, None)], list):
                return KNOWN_ITEMS[(iid, None)]
        # Otherwise attempt exact hue match first, then generic
        if (iid, hue) in KNOWN_ITEMS and isinstance(KNOWN_ITEMS[(iid, hue)], list):
            return KNOWN_ITEMS[(iid, hue)]
        if (iid, None) in KNOWN_ITEMS and isinstance(KNOWN_ITEMS[(iid, None)], list):
            return KNOWN_ITEMS[(iid, None)]

    # Scan fallback: find any tuple key matching iid, prefer None hue
    try:
        for k, v in KNOWN_ITEMS.items():
            if isinstance(k, tuple) and len(k) == 2 and k[0] == iid and isinstance(v, list):
                # Prefer None hue explicitly
                if k[1] is None:
                    return v
        # If none had None hue, return the first matching iid tuple
        for k, v in KNOWN_ITEMS.items():
            if isinstance(k, tuple) and len(k) == 2 and k[0] == iid and isinstance(v, list):
                return v
    except Exception:
        pass

    # Nothing found
    return []

def get_next_results_gump_id():
    """Get the next cycling RESULTS_GUMP_ID and increment the counter."""
    global _CURRENT_GUMP_OFFSET
    current_id = RESULTS_GUMP_ID_BASE + _CURRENT_GUMP_OFFSET
    _CURRENT_GUMP_OFFSET = (_CURRENT_GUMP_OFFSET + 1) % RESULTS_GUMP_ID_MAX_OFFSET
    return current_id

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
    material_index = {
        'by_id': {},
        'by_name': {},
        'by_fuzzy': {},
    }
    for recipe_entry in (items or []):
        material_entries = recipe_entry.get('materials') or []
        for material_entry in material_entries:
            # Index by material id (supports both decimal and hex id fields)
            material_id_value = _to_int_id(
                material_entry.get('id') if material_entry.get('id') is not None else material_entry.get('id_hex')
            )
            if isinstance(material_id_value, int):
                material_index['by_id'].setdefault(int(material_id_value), []).append(recipe_entry)
            # Index by normalized material name (and fuzzy key variant)
            normalized_material_name = _normalize_material_name(material_entry.get('name'))
            if normalized_material_name:
                material_index['by_name'].setdefault(normalized_material_name, []).append(recipe_entry)
                fuzzy_material_key = name_to_fuzzy_key(normalized_material_name)
                if fuzzy_material_key:
                    material_index['by_fuzzy'].setdefault(fuzzy_material_key, []).append(recipe_entry)
    return material_index

# Razor Enhanced helpers -----------------------------

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
        item_name_text = item.Name
        if item_name_text:
            item_name_text = str(item_name_text)
            amount_to_strip = amount_hint if amount_hint is not None else item.Amount
            return _clean_leading_amount(item_name_text, amount_to_strip)
    except Exception:
        pass
    try:
        Items.WaitForProps(item.Serial, 400)
        property_strings = Items.GetPropStringList(item.Serial)
        if property_strings:
            item_name_text = str(property_strings[0])
            amount_to_strip = amount_hint if amount_hint is not None else item.Amount
            return _clean_leading_amount(item_name_text, amount_to_strip)
        Items.SingleClick(item.Serial)
        Misc.Pause(150)
        Items.WaitForProps(item.Serial, 600)
        property_strings = Items.GetPropStringList(item.Serial)
        if property_strings:
            item_name_text = str(property_strings[0])
            amount_to_strip = amount_hint if amount_hint is not None else item.Amount
            return _clean_leading_amount(item_name_text, amount_to_strip)
    except Exception:
        pass
    return 'Unknown'

def _format_hex4(v: int) -> str:
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
    matching_recipe_entries = []
    try:
        target_item_id = int(item.ItemID)
    except Exception:
        target_item_id = None
    target_item_display_name = get_item_name(item, amount_hint=getattr(item, 'Amount', 1))
    normalized_target_item_name = _normalize_material_name(target_item_display_name)
    fuzzy_target_item_key = name_to_fuzzy_key(normalized_target_item_name)

    seen_recipe_keys = set()
    # Match by exact item id
    if isinstance(target_item_id, int) and target_item_id in index.get('by_id', {}):
        for recipe_entry in index['by_id'][target_item_id]:
            recipe_key = (recipe_entry.get('category'), recipe_entry.get('name'))
            if recipe_key not in seen_recipe_keys:
                matching_recipe_entries.append(recipe_entry)
                seen_recipe_keys.add(recipe_key)
    # Match by normalized item name
    if normalized_target_item_name and normalized_target_item_name in index.get('by_name', {}):
        for recipe_entry in index['by_name'][normalized_target_item_name]:
            recipe_key = (recipe_entry.get('category'), recipe_entry.get('name'))
            if recipe_key not in seen_recipe_keys:
                matching_recipe_entries.append(recipe_entry)
                seen_recipe_keys.add(recipe_key)
    # Match by fuzzy key variant
    if fuzzy_target_item_key and fuzzy_target_item_key in index.get('by_fuzzy', {}):
        for recipe_entry in index['by_fuzzy'][fuzzy_target_item_key]:
            recipe_key = (recipe_entry.get('category'), recipe_entry.get('name'))
            if recipe_key not in seen_recipe_keys:
                matching_recipe_entries.append(recipe_entry)
                seen_recipe_keys.add(recipe_key)
    return matching_recipe_entries

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
        for ln in prop_list:
            s = str(ln).strip()
            m = re.search(r"magical\s+intensity\s*\d+\s*\(([^)]+)\)", s, flags=re.IGNORECASE)
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
            return '#888888'  # Medium grey for regular properties
        if raw_lower.startswith('durability'):
            return '#888888'  # Medium grey for durability
        # Add more rules as needed
    except Exception:
        pass
    return '#888888'  # Medium grey for all regular properties

def _wrap_line_with_default_color(line: str, default_color: str = '#BBBBBB') -> str:
    """Wrap a line with default color, preserving existing basefont tags."""
    if not line.strip():
        return line
    
    # If line has no basefont tags, just wrap it
    if '<basefont' not in line:
        return f"<basefont color={default_color}>{line}</basefont>"
    
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

def _split_line_for_wrapping(line: str, max_chars: int = 30) -> list:
    """Split a long line into multiple lines based on character count and word boundaries."""
    
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

def _compute_ar_bonus_text(equipment_slot: str, property_text_lowercase: str) -> str or None:
    """Return a slot-specific Armor Rating (AR) bonus label for an AR tier line.
    Parameters:
      - equipment_slot: logical slot name (e.g., 'head', 'body', 'shield')
      - property_text_lowercase: item property line already lowercased
    Returns:
      - A formatted text string like "+ 1.4 AR ( Fortification )" or None if not applicable.
    """
    # Validate input
    if not equipment_slot or not property_text_lowercase:
        return None
    
    # Identify which AR tier keyword is present in the property text
    matched_tier_key = None
    for tier_key in AR_BONUS_TIERS.keys():
        if tier_key in property_text_lowercase:
            matched_tier_key = tier_key
            break
    if not matched_tier_key:
        return None
    
    tier_values = AR_BONUS_TIERS[matched_tier_key]
    
    # Map the equipment slot to the appropriate numeric bucket
    normalized_slot = (equipment_slot or '').lower()
    if normalized_slot in ('neck', 'hand'):
        armor_rating_bonus_delta = tier_values['neck_hands']
    elif normalized_slot in ('arms', 'head', 'legs'):
        armor_rating_bonus_delta = tier_values['arms_head_legs']
    elif normalized_slot == 'body':
        armor_rating_bonus_delta = tier_values['body']
    elif normalized_slot == 'shield':
        armor_rating_bonus_delta = tier_values['shield']
    else:
        # Non-armor/shield slots: do not display AR bonus; suppress line
        return None
    
    # Numeric-first formatting
    return f"+ {armor_rating_bonus_delta:g} AR ( {matched_tier_key.capitalize()} )"

def _is_weapon_slot(equip_slot: str) -> bool:
    slot = (equip_slot or '').lower()
    return slot in ('weapon1h', 'weapon2h')

def _compute_durability_text(equip_slot: str, raw_lower: str) -> str or None:
    """Return durability text tailored for armor vs weapons. None if not a durability tier line."""
    if not raw_lower:
        return None
    # Exceptional is percent-based per spec
    if 'exceptional' == raw_lower.strip():
        if _is_weapon_slot(equip_slot):
            return '+ 20% durability ( Exceptional )'
        else:
            return '+ 20% durability ( Exceptional )'
    for k, val in DURABILITY_TIERS.items():
        if k in raw_lower:
            if _is_weapon_slot(equip_slot):
                return f"+ {val} durability ( {k.capitalize()} )"
            else:
                return f"+ {val} durability ( {k.capitalize()} )"
    return None

def _compute_ar_modifier_text(item_id: int, modifier_name: str) -> str:
    """Compute AR modifier text in 'Base + Additional AR (Modifier)' format."""
    if item_id not in ARMOR_DATA_BY_ITEMID:
        return f"<basefont color=#888888>+ AR</basefont> <basefont color=#AAAAAA>( {modifier_name.capitalize()} )</basefont>"
    
    armor_data = ARMOR_DATA_BY_ITEMID[item_id]
    base_ar = armor_data.get('base_ar', 0)
    ar_modifiers = armor_data.get('ar_modifiers', {})
    
    # Find the total AR for this specific modifier (stored value is total, not bonus)
    modifier_total_ar = ar_modifiers.get(modifier_name.capitalize(), 0)
    
    if modifier_total_ar > 0:
        # Calculate the actual bonus by subtracting base AR from total AR
        modifier_bonus = modifier_total_ar - base_ar
        return f"<basefont color=#3FA9FF>{base_ar} + {modifier_bonus} AR</basefont> <basefont color=#AAAAAA>( {modifier_name.capitalize()} )</basefont>"
    else:
        return f"<basefont color=#888888>+ AR</basefont> <basefont color=#AAAAAA>( {modifier_name.capitalize()} )</basefont>"

def _equip_slot_and_type(item_id: int) -> tuple:
    """Return (slot, friendly_type). friendly_type includes detailed armor/weapon info."""
    try:
        slot = get_equip_slot(int(item_id) if item_id is not None else 0)
    except Exception:
        slot = None
    
    # Check armor data first for detailed info
    if item_id in ARMOR_DATA_BY_ITEMID:
        armor_data = ARMOR_DATA_BY_ITEMID[item_id]
        armor_type = armor_data['type']
        layer = armor_data['layer']
        if armor_type == 'Shield':
            typ = f"Shield ({layer})"
        else:
            typ = f"{armor_type} ( {layer} )"
        return slot, typ
    
    # Check weapon data
    if item_id in WEAPON_DATA_BY_ITEMID:
        weapon_data = WEAPON_DATA_BY_ITEMID[item_id]
        weapon_type = weapon_data['type']
        hands = weapon_data['hands']
        typ = f"{weapon_type} ({hands.upper()})"
        return slot, typ
    
    # Fallback to generic slot-based detection
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
    
    # 1. Item properties section (highest priority) - separated into modifiers, regular properties, and durability status
    modifier_lines = []
    regular_lines = []
    durability_lines = []
    try:
        Items.WaitForProps(getattr(target_item, 'Serial', 0), 400)
        property_list = Items.GetPropStringList(getattr(target_item, 'Serial', 0)) or []
        debug_msg(f"RAW PROPERTIES: Found {len(property_list)} properties", COLORS['cat'])
        for i, prop in enumerate(property_list):
            debug_msg(f"  [{i}] {repr(prop)}", COLORS['cat'])
        
        # Skip name line if duplicates title
        if property_list and property_list[0].strip().lower() == (item_display_name or '').strip().lower():
            property_list = property_list[1:]
            debug_msg(f"SKIPPED duplicate name line, {len(property_list)} properties remaining", COLORS['cat'])
        
        # Check if this is a weapon for special processing
        is_weapon = item_id in WEAPON_DATA_BY_ITEMID
        weapon_damage_text = None
        weapon_speed_text = None
        weapon_skill_text = None
        weapon_intensity_text = None
        hue_text = None
        
        # Process each property with slot-aware rendering and separate modifiers from regular properties
        debug_msg(f"PROCESSING {len(property_list[:12])} properties (limited to 12), is_weapon={is_weapon}", COLORS['cat'])
        for prop_idx, prop in enumerate(property_list[:12]):  # Limit to prevent overflow
            try:
                raw_line = str(prop).strip()
                low = raw_line.lower()
                debug_msg("\n--- PROPERTY {}: {} ---".format(prop_idx+1, repr(raw_line)), COLORS['cat'])
                
                # Check if this is a durability status line (e.g., "durability 46 / 51")
                is_durability_status = re.match(r'durability\s+\d+\s*/\s*\d+', low)
                
                # Check for hue property (e.g., "Metallic (#2311)" or "Inferno (#2136)")
                hue_match = re.match(r'(.+?)\s*\(#(\d+)\)', raw_line)
                if hue_match:
                    hue_name, hue_number = hue_match.groups()
                    hue_number = int(hue_number)
                    
                    # Get item's actual hue for verification
                    item_hue = int(getattr(target_item, 'Hue', 0) or 0)
                    debug_msg(f"  → HUE PROPERTY: name='{hue_name}', number={hue_number}, item_hue={item_hue}", COLORS['success'])
                    
                    # Verify hue matches (allow for some tolerance in case of conversion differences)
                    if abs(hue_number - item_hue) <= 1:
                        if HUE_TEXT_COLORIZED_BY_HUE and item_hue > 0:
                            # Convert hue to hex color (simplified conversion)
                            hue_hex = f"#{item_hue:04X}FF"  # Add alpha for visibility
                            hue_text = f"<basefont color={hue_hex}>Hue: {hue_name.strip()} ( {hue_number} )</basefont>"
                        else:
                            hue_text = f"<basefont color=#444444>Hue: {hue_name.strip()} ( {hue_number} )</basefont>"
                        debug_msg(f"  → HUE TEXT: {hue_text}", COLORS['success'])
                        continue
                    else:
                        debug_msg(f"  → HUE MISMATCH: property={hue_number}, item={item_hue}", COLORS['warn'])
                
                # Special weapon property handling
                if is_weapon:
                    # Extract weapon damage (e.g., "weapon damage 8 - 32")
                    damage_match = re.match(r'weapon damage (\d+) - (\d+)', low)
                    if damage_match:
                        min_dmg, max_dmg = damage_match.groups()
                        weapon_damage_text = f"<basefont color=#FF6B6B>{min_dmg} - {max_dmg} damage</basefont>"
                        debug_msg(f"  → WEAPON DAMAGE: {weapon_damage_text}", COLORS['success'])
                        continue
                    
                    # Extract weapon speed (e.g., "weapon speed 30")
                    speed_match = re.match(r'weapon speed (\d+)', low)
                    if speed_match:
                        speed = speed_match.group(1)
                        weapon_speed_text = f"<basefont color=#FFB84D>{speed} speed</basefont>"
                        debug_msg(f"  → WEAPON SPEED: {weapon_speed_text}", COLORS['success'])
                        continue
                    
                    # Extract skill required (e.g., "skill required: mace fighting")
                    skill_match = re.match(r'skill required: (.+)', low)
                    if skill_match:
                        skill = skill_match.group(1)
                        weapon_skill_text = f"<basefont color=#666666>Skill: {skill.title()}</basefont>"
                        debug_msg(f"  → WEAPON SKILL: {weapon_skill_text}", COLORS['success'])
                        continue
                    
                    # Extract magical intensity (e.g., "Magical Intensity: 0 (Common)")
                    intensity_match = re.match(r'magical intensity: \d+ \((.+)\)', low)
                    if intensity_match:
                        tier = intensity_match.group(1).lower()
                        tier_color = NAME_TIER_COLORS.get(tier, '#DDDDDD')
                        weapon_intensity_text = f"<basefont color={tier_color}>Magical Intensity: {raw_line.split(': ', 1)[1]}</basefont>"
                        debug_msg(f"  → WEAPON INTENSITY: {weapon_intensity_text}", COLORS['success'])
                        continue
                
                # Check if this looks like a modifier FIRST (before slot-aware transformations)
                # Exclude durability status lines from being treated as modifiers
                is_modifier = (low in MODIFIER_PROPERTIES or 
                              re.search(r'[+\-]\s*\d+', raw_line) or
                              any(keyword in low for keyword in ['damage', 'tactics', 'skill', 'accurate']))
                
                debug_msg(f"  Is durability status: {bool(is_durability_status)}", COLORS['cat'])
                debug_msg(f"  Is modifier: {is_modifier} (in MODIFIER_PROPERTIES: {low in MODIFIER_PROPERTIES})", COLORS['cat'])
                if re.search(r'[+\-]\s*\d+', raw_line):
                    debug_msg("    Has +/- numbers: {}".format(re.search(r'[+\-]\s*\d+', raw_line).group()), COLORS['cat'])
                modifier_keywords = [kw for kw in ['damage', 'tactics', 'skill', 'accurate'] if kw in low]
                if modifier_keywords:
                    debug_msg(f"    Has modifier keywords: {modifier_keywords}", COLORS['cat'])
                
                # Apply slot-aware transformations (only for non-modifiers)
                slot_ar_text = _compute_ar_bonus_text(equip_slot, low) if not is_modifier else None
                slot_dura_text = _compute_durability_text(equip_slot, low) if not is_modifier else None
                debug_msg(f"  Slot AR text: {repr(slot_ar_text)}", COLORS['cat'])
                debug_msg(f"  Slot Dura text: {repr(slot_dura_text)}", COLORS['cat'])
                
                if slot_ar_text:
                    debug_msg(f"    Processing slot AR text: {repr(slot_ar_text)}", COLORS['cat'])
                    final_text = slot_ar_text
                    # AR bonuses are regular properties
                    color = _property_color_for_line(low)
                    debug_msg(f"    AR color: {repr(color)}", COLORS['cat'])
                    safe_text = final_text.replace('<','&lt;').replace('>','&gt;') if '<basefont' not in final_text else final_text
                    formatted_line = f"<basefont color={color}>{safe_text}</basefont>"
                    regular_lines.append(formatted_line)
                    debug_msg("  → REGULAR (AR): " + repr(formatted_line), COLORS['success'])
                elif slot_dura_text:
                    final_text = slot_dura_text
                    # Durability is a regular property
                    color = _property_color_for_line(low)
                    safe_text = final_text.replace('<','&lt;').replace('>','&gt;') if '<basefont' not in final_text else final_text
                    formatted_line = f"<basefont color={color}>{safe_text}</basefont>"
                    regular_lines.append(formatted_line)
                    debug_msg("  → REGULAR (Dura): " + repr(formatted_line), COLORS['success'])
                elif is_durability_status:
                    # This is a durability status line - format with grey color
                    safe_text = raw_line.replace('<','&lt;').replace('>','&gt;')
                    formatted_line = f"<basefont color=#888888>{safe_text}</basefont>"
                    durability_lines.append(formatted_line)
                    debug_msg("  → DURABILITY STATUS: " + repr(formatted_line), COLORS['info'])
                elif is_modifier:
                    # This is a modifier property - use remapped text with HTML colors or format with colored text
                    if low in PROPERTY_REMAP:
                        # Check if this is an AR modifier placeholder that needs dynamic calculation
                        if PROPERTY_REMAP[low] == 'PLACEHOLDER_AR_MODIFIER':
                            final_text = _compute_ar_modifier_text(item_id, low)
                        # Special handling for "exceptional" - different for weapons vs armor
                        elif low == 'exceptional':
                            if is_weapon:
                                final_text = '<basefont color=#FF6B6B>+ 20 Damage</basefont> <basefont color=#FFB84D>( Exceptional )</basefont>'
                            else:
                                # For armor, exceptional gives durability bonus
                                final_text = '<basefont color=#888888>+ 20% Durability</basefont> <basefont color=#AAAAAA>( Exceptional )</basefont>'
                        # Accuracy set: use Archery for bows/crossbows instead of Tactics
                        elif low in ACCURACY_KEYS:
                            weapon_info = WEAPON_DATA_BY_ITEMID.get(item_id, {})
                            weapon_type = weapon_info.get('type', '') if weapon_info else ''
                            base_text = PROPERTY_REMAP[low]
                            if weapon_type in ('Bow', 'Crossbow'):
                                # Replace 'Tactics' with 'Archery' in the remapped string
                                final_text = base_text.replace('Tactics', 'Archery')
                            else:
                                final_text = base_text
                        else:
                            final_text = PROPERTY_REMAP[low]
                        # Don't escape HTML for remapped properties since they have color formatting
                        modifier_lines.append(final_text)
                        debug_msg("  → MODIFIER (Remapped): " + repr(final_text), COLORS['warn'])
                    else:
                        # Format modifier with appropriate color category
                        formatted_text = format_modifier_text(raw_line)
                        modifier_lines.append(formatted_text)
                        debug_msg("  → MODIFIER (Formatted): " + repr(formatted_text), COLORS['warn'])
                else:
                    # Regular property - apply default color and escape HTML
                    final_text = PROPERTY_REMAP.get(low, raw_line)
                    safe_text = final_text.replace('<','&lt;').replace('>','&gt;') if '<basefont' not in final_text else final_text
                    color = _property_color_for_line(low)
                    formatted_line = f"<basefont color={color}>{safe_text}</basefont>"
                    regular_lines.append(formatted_line)
                    debug_msg("  → REGULAR (Default): " + repr(formatted_line), COLORS['success'])
                    
            except Exception as prop_error:
                debug_msg(f"  ERROR processing property {prop_idx+1}: {prop_error}", COLORS['bad'])
                continue
        
        debug_msg("\nPROPERTY SEPARATION RESULTS:", COLORS['cat'])
        debug_msg(f"  Modifier lines ({len(modifier_lines)}):", COLORS['cat'])
        for i, line in enumerate(modifier_lines):
            debug_msg(f"    [{i}] {repr(line)}", COLORS['cat'])
        debug_msg(f"  Regular lines ({len(regular_lines)}):", COLORS['cat'])
        for i, line in enumerate(regular_lines):
            debug_msg(f"    [{i}] {repr(line)}", COLORS['cat'])
        debug_msg(f"  Durability lines ({len(durability_lines)}):", COLORS['cat'])
        for i, line in enumerate(durability_lines):
            debug_msg(f"    [{i}] {repr(line)}", COLORS['cat'])
        
        # Add weapon damage/speed section first for weapons (priority 5)
        if is_weapon and (weapon_damage_text or weapon_speed_text):
            weapon_combat_lines = []
            if weapon_damage_text and weapon_speed_text:
                # Combine damage and speed on one line
                weapon_combat_lines.append(f"{weapon_damage_text}   {weapon_speed_text}")
            elif weapon_damage_text:
                weapon_combat_lines.append(weapon_damage_text)
            elif weapon_speed_text:
                weapon_combat_lines.append(weapon_speed_text)
            
            sections.append(TextSection(weapon_combat_lines, 'weapon_combat', 5))
            debug_msg(f"ADDED SECTION: weapon_combat (priority 5, {len(weapon_combat_lines)} lines)", COLORS['warn'])
        
        # Add modifier properties (priority 10)
        if modifier_lines:
            sections.append(TextSection(modifier_lines, 'modifiers', 10))
            debug_msg(f"ADDED SECTION: modifiers (priority 10, {len(modifier_lines)} lines)", COLORS['warn'])
        
        # Add artifact weapon description right below modifiers (priority 12)
        try:
            artifact_desc = resolve_artifact_weapon_description(item_id, item_display_name)
        except Exception:
            artifact_desc = None
        if artifact_desc:
            sep_needed_art = bool(modifier_lines)
            sections.append(TextSection([f"<basefont color=#FF550F>Artifact: {artifact_desc}</basefont>"], 'artifact', 12, separator_before=sep_needed_art))
            debug_msg(f"ADDED SECTION: artifact (priority 12, 1 line, separator: {sep_needed_art})", COLORS['info'])

        # Add regular properties after modifiers (priority 15) with separator if modifiers exist
        if regular_lines:
            separator_needed = bool(modifier_lines) or bool(is_weapon and (weapon_damage_text or weapon_speed_text))
            sections.append(TextSection(regular_lines, 'properties', 15, separator_before=separator_needed))
            debug_msg(f"ADDED SECTION: properties (priority 15, {len(regular_lines)} lines, separator: {separator_needed})", COLORS['success'])
            
    except Exception as e:
        debug_msg(f"Error processing properties: {e}", COLORS['warn'])
    
    # Add total AR section for armor items (priority 5 - above modifiers)
    if item_id in ARMOR_DATA_BY_ITEMID:
        armor_data = ARMOR_DATA_BY_ITEMID[item_id]
        base_ar = armor_data.get('base_ar', 0)
        ar_modifiers = armor_data.get('ar_modifiers', {})
        
        # Calculate total AR - find the highest AR modifier that matches current item properties
        total_ar = base_ar
        current_ar_modifier = None
        current_ar_bonus = 0
        
        # Check which AR modifier is currently active on this item by looking at processed properties
        for prop_line in (modifier_lines + regular_lines):
            for modifier_name, modifier_total_ar in ar_modifiers.items():
                if modifier_name.lower() in prop_line.lower():
                    if modifier_total_ar > current_ar_bonus:  # Use highest AR modifier if multiple
                        current_ar_modifier = modifier_name
                        current_ar_bonus = modifier_total_ar
                        total_ar = modifier_total_ar  # Use the total AR directly since it's stored as total
                        break
        
        if total_ar > 0:
            total_ar_line = f"<basefont color=#CCCCCC>{total_ar} AR </basefont>"
            sections.append(TextSection([total_ar_line], 'total_ar', 5))
            debug_msg(f"ADDED SECTION: total_ar (priority 5, 1 lines) - Base: {base_ar}, Modifier: {current_ar_modifier}({current_ar_bonus}), Total: {total_ar}", COLORS['info'])
    
    # Add durability status last (priority 25) with separator if other sections exist - OUTSIDE try block
    if durability_lines:
        separator_needed = bool(modifier_lines or regular_lines)
        sections.append(TextSection(durability_lines, 'durability', 25, separator_before=separator_needed))
        debug_msg(f"ADDED SECTION: durability (priority 25, {len(durability_lines)} lines, separator: {separator_needed})", COLORS['info'])
    
    # 2. Known item descriptions section (high priority) - hue-aware
    try:
        # Determine if hue should be ignored (weapons/armor can be any hue)
        # Avoid calling is_weapon() here since a local variable named `is_weapon` may exist in this scope
        treat_hue_as_agnostic = (get_weapon_data(item_id) is not None) or (get_armor_data(item_id) is not None)
        try:
            item_hue = int(getattr(target_item, 'Hue', 0) or 0)
        except Exception:
            item_hue = 0

        known_lines = _resolve_known_item_lines(item_id, item_hue, treat_hue_as_agnostic=treat_hue_as_agnostic)
        if known_lines:
            debug_msg(
                f"Adding {len(known_lines)} known item descriptions (hue-aware: {'yes' if not treat_hue_as_agnostic else 'no'})",
                COLORS['cat']
            )
            # Show a separator before every known-item line except the first
            have_rendered_any_known = False
            need_separator_before_next = False

            for i, desc_line in enumerate(known_lines):
                # Allow inline separator control via markers in description list
                raw = (desc_line or '').strip().lower()
                if raw in ('---', '[sep]', '[separator]'):
                    debug_msg(f"  Known desc [{i}] requested separator", COLORS['cat'])
                    need_separator_before_next = True
                    continue  # Do not render a line for the marker itself

                debug_msg(f"  Known desc [{i}] (hue={item_hue}): {repr(desc_line)}", COLORS['cat'])
                # Wrap line with default color, preserving existing basefont tags
                formatted_line = _wrap_line_with_default_color(desc_line, '#BBBBBB')
                debug_msg(f"    Formatted: {repr(formatted_line)}", COLORS['cat'])

                # Split long lines for word wrapping at 30 characters
                wrapped_lines = _split_line_for_wrapping(formatted_line, 30)

                # Add each line as its own section for better layout control
                for j, wl in enumerate(wrapped_lines):
                    # Apply separator on the first wrapped visual line when:
                    #  - We've already rendered at least one known line (separator between lines), or
                    #  - A marker explicitly requested a separator
                    sep_flag = (j == 0) and ((have_rendered_any_known) or (need_separator_before_next))
                    sections.append(TextSection([wl], 'known', 8, separator_before=sep_flag))
                    if j == 0:
                        # After the first visual line of this description, we have rendered content
                        have_rendered_any_known = True
                        need_separator_before_next = False
            # Ensure there is a separator before the next (non-known) section in the results
            sections.append(TextSection([], 'known_end_separator', 9, separator_before=True))
            debug_msg("ADDED known item lines as individual sections (priority 8) with dynamic separators and trailing separator", COLORS['info'])
    except Exception as e:
        debug_msg(f"Error adding known item descriptions: {e}", COLORS['warn'])
    
    # 3. Equipment type section (medium priority)
    equipment_lines = []
    if equip_slot or friendly_type != 'Unknown':
        equipment_lines.append(f"<basefont color=#BBBBBB>Type: {friendly_type}</basefont>")
        
        # Weapon abilities - check weapon data dictionary directly
        debug_msg(f"Checking weapon abilities: equip_slot='{equip_slot}', item_id={item_id} (0x{item_id:04X})", COLORS['cat'])
        
        # Check if item is in weapon data
        is_weapon = item_id in WEAPON_DATA_BY_ITEMID
        weapon_data = WEAPON_DATA_BY_ITEMID.get(item_id)
        debug_msg(f"Weapon lookup: is_weapon={is_weapon}, weapon_data={weapon_data}", COLORS['cat'])
        
        if is_weapon:
            debug_msg(f"Item is weapon, getting abilities...", COLORS['cat'])
            primary_ability, secondary_ability = get_weapon_abilities(item_id)
            debug_msg(f"Raw API result: primary='{primary_ability}', secondary='{secondary_ability}'", COLORS['cat'])
            if primary_ability:
                equipment_lines.append(f"<basefont color=#333333>Primary: {primary_ability}</basefont>")  # previous color: #FFD700 (yellow)
            if secondary_ability:
                equipment_lines.append(f"<basefont color=#333333>Secondary: {secondary_ability}</basefont>")  # previous color: #87CEEB (light blue)

        else:
            debug_msg(f"Item is not in weapon data dictionary", COLORS['cat'])
    
    if equipment_lines:
        sections.append(TextSection(equipment_lines, 'equipment_type', 30, separator_before=True))
        debug_msg(f"ADDED SECTION: equipment_type (priority 30, {len(equipment_lines)} lines)", COLORS['cat'])
    
    # 4. Weapon intensity section (second-to-last priority for weapons)
    if is_weapon and weapon_intensity_text:
        sections.append(TextSection([weapon_intensity_text], 'weapon_intensity', 35, separator_before=True))
        debug_msg(f"ADDED SECTION: weapon_intensity (priority 35, 1 line)", COLORS['cat'])
    
    # 5. Hue section (near bottom priority)
    if hue_text:
        sections.append(TextSection([hue_text], 'hue_info', 40, separator_before=True))
        debug_msg(f"ADDED SECTION: hue_info (priority 40, 1 line)", COLORS['cat'])
    
    # 6. Weapon skill section (last priority for weapons)
    if is_weapon and weapon_skill_text:
        sections.append(TextSection([weapon_skill_text], 'weapon_skill', 45, separator_before=True))
        debug_msg(f"ADDED SECTION: weapon_skill (priority 45, 1 line)", COLORS['cat'])
    
    # 7. Technical/dev info section (lowest priority) - shown when SHOW_TECHNICAL_INFO is True
    if SHOW_TECHNICAL_INFO:
        dev_lines = []
        dev_lines.append(f"<basefont color=#999999>ItemID: {_format_hex4(item_id)}</basefont>")
        if item_hue > 0:
            dev_lines.append(f"<basefont color=#999999>Hue: {item_hue}</basefont>")
        dev_lines.append(f"<basefont color=#999999>Serial: {item_serial}</basefont>")
        
        if dev_lines:
            sections.append(TextSection(dev_lines, 'technical_info', 50))
            debug_msg(f"ADDED SECTION: technical_info (priority 50, {len(dev_lines)} lines)", COLORS['cat'])
    
    # Sort by priority
    debug_msg("\nSECTION ORDERING:", COLORS['cat'])
    debug_msg(f"  Before sorting ({len(sections)} sections):", COLORS['cat'])
    for i, section in enumerate(sections):
        debug_msg(f"    [{i}] {section.category} (priority {section.priority}, {len(section.lines)} lines, separator: {section.separator_before})", COLORS['cat'])
    
    sections.sort(key=lambda x: x.priority)
    
    debug_msg(f"  After sorting:", COLORS['cat'])
    for i, section in enumerate(sections):
        debug_msg(f"    [{i}] {section.category} (priority {section.priority}, {len(section.lines)} lines, separator: {section.separator_before})", COLORS['cat'])
    
    return sections

def show_walia_gump(target_item, usages: list, gump_id=None):
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
    
    # Dynamic height based on actual content - more precise calculation
    base_padding = 20  # Top/bottom margins
    title_space = 60 if DISPLAY.get('show_title', True) else 0  # Title section
    item_graphic_space = 70 if DISPLAY.get('show_item_graphic', True) else 0  # Item graphic
    crafting_space = (max_rows_to_render * 24) if DISPLAY.get('show_crafting', False) else 0
    
    gump_height = base_padding + title_space + max(item_graphic_space, content_height_px) + crafting_space
    debug_msg(f"Gump sizing: base={base_padding}, title={title_space}, content={content_height_px}, item_graphic={item_graphic_space}, crafting={crafting_space}, total={gump_height}", COLORS['cat'])

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
        
        # Check if title is long enough to wrap to second line
        # Estimate: ~25-30 characters per line for <big><b> text in 300px width
        title_length = len(title_text)
        title_wraps = title_length > 20  # Conservative threshold for line wrapping
        
        # Adjust title height and spacing if it wraps
        if title_wraps:
            title_height = 50  # Extra height for wrapped title
            content_spacing = 52  # Extra spacing below title
            debug_msg(f"Long title detected ({title_length} chars), using wrapped layout", COLORS['cat'])
        else:
            title_height = 30  # Normal title height
            content_spacing = 32  # Normal spacing below title
            debug_msg(f"Normal title length ({title_length} chars), using standard layout", COLORS['cat'])
        
        Gumps.AddHtml(gump, 10, title_y, gump_width - 20, title_height, title_html, 0, 0)
        content_top_y = title_y + content_spacing


    # Item graphic on left
    if DISPLAY.get('show_item_graphic', True):
        item_top_y = content_top_y + 8  # Increased spacing from 4 to 8
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
    
    debug_msg("\nFINAL HTML RENDERING:", COLORS['cat'])
    debug_msg(f"  Rendering {len(text_sections)} sections starting at Y={current_y}", COLORS['cat'])
    
    for section_idx, section in enumerate(text_sections):
        debug_msg("\n  Section [{}]: {} (priority {})".format(section_idx, section.category, section.priority), COLORS['cat'])
        debug_msg(f"    Lines: {len(section.lines)}, Separator: {section.separator_before}, Y: {current_y}", COLORS['cat'])
        
        if section.separator_before:
            # Add separator line
            separator_html = "<basefont color=#444444>─────────</basefont>"
            debug_msg(f"    Adding separator at Y={current_y}: {repr(separator_html)}", COLORS['cat'])
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
        debug_msg(f"    Generated HTML ({len(section_html) if section_html else 0} chars): {repr(section_html[:100])}{'...' if section_html and len(section_html) > 100 else ''}", COLORS['cat'])
        
        if section_html:
            section_height = len(section.lines) * 18
            debug_msg(f"    Rendering at Y={current_y}, height={section_height}", COLORS['cat'])
            for line_idx, line in enumerate(section.lines):
                debug_msg(f"      Line [{line_idx}]: {repr(line)}", COLORS['cat'])
            
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

    # Close button (optional based on global setting)
    if SHOW_CLOSE_BUTTON:
        Gumps.AddButton(gump, gump_width-30, 8, 4017, 4018, 1, 1, 0)
        Gumps.AddTooltip(gump, "Close")

    # Send gump with cycling ID (or reuse provided ID for DEV toggle)
    current_gump_id = gump_id if gump_id is not None else get_next_results_gump_id()
    Gumps.SendGump(current_gump_id, Player.Serial, RESULTS_X, RESULTS_Y, gump.gumpDefinition, gump.gumpStrings)
    return current_gump_id

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
                Misc.Pause(180)
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
    """Handle clicks from any of the cycling results gumps (close button only)."""
    # Check all possible cycling gump IDs
    for offset in range(RESULTS_GUMP_ID_MAX_OFFSET):
        gump_id = RESULTS_GUMP_ID_BASE + offset
        if not Gumps.HasGump(gump_id):
            continue
            
        Gumps.WaitForGump(gump_id, 5)  # Short wait for each
        gd = Gumps.GetGumpData(gump_id)
        if not gd or gd.buttonid <= 0:
            continue
            
        # Process the button press and consume it
        if gd.buttonid == 1:
            # Close button pressed - close the gump
            debug_msg("Close button pressed", COLORS['info'])
            Gumps.CloseGump(gump_id)
            return

def walia_run_once(index: dict):
    # Prompt for a target using Razor Enhanced Target system
    try:
        Misc.SendMessage("Target an item to inspect usages...", COLORS['title'])
    except Exception:
        pass
    debug_msg("Prompting for target")
    try:
        Target.Cancel()
        Misc.Pause(100)
        sel = Target.PromptTarget("Select an item to inspect")
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
    debug_msg(f"Target acquired: serial={hex(sel)} id={_format_hex4(getattr(it,'ItemID',0))}")
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
    # this needs rework for crafting recipes , currently focused on equipment
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
            Misc.Pause(50)
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
