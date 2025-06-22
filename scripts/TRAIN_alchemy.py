"""
TRAIN Alchemy - a Razor Enhanced Python script for Ultima Online
training Alchemy skill using crafting tools and gumps.

Training by alchemy skill:
0 - 30: Train at NPC Alchemist.
30 - 45: Agility Potion.
45 - 55: Strength Potion.
55 - 65: Greater Agility Potion.
65 - 75: Greater Strength Potion.
75 - 85: Greater Heal Potion.
85 - 95: Greater Cure Potion.
95 - 100: Greater Conflagration Potion.

Training by alchemy skill using only Poison:
0 - 30: Train at NPC Alchemist.
25 - 35: Lesser posion
35 - 65: Poison
65 - 99: Greater posion
99 - 100: Deadly posion

poison only uses nightshade reagent
finds a mortar and pestle , use , interacts with gump to make max of poison 
make posion potion , drink poison , 
this is useful if can gain immunity to poison such as through necromancy or custom shard mechanics

VERSION::20250621
"""

import sys
from System.Collections.Generic import List

# Script configuration
SCRIPT_NAME = "Train Alchemy"
SCRIPT_VERSION = "1.0"
POISON_ONLY_MODE = True  # Set to True to train using only poison potions

# Color constants
COLOR_NORMAL = 0x3B2
COLOR_SUCCESS = 0x44
COLOR_ERROR = 0x24
COLOR_WARNING = 0x37

# Gump IDs for Alchemy
GUMP_ALCHEMY = 949095101  # Correct gump ID
GUMP_BUTTON_TOXIC = 22    # Toxic category button
GUMP_BUTTON_MAKE_ALL = 9  # Make maximum amount

# Poison potion buttons (after clicking Toxic category)
POISON_BUTTONS = {
    "Lesser Poison": 9,    # Lesser poison button
    "Poison": 16,         # Regular poison button
    "Greater Poison": 16,  # Greater poison button
    "Deadly Poison": 23   # Deadly poison button
}

# Item IDs
ITEM_MORTAR_AND_PESTLE = 0x0E9B
ITEM_EMPTY_BOTTLE = 0x0F0E
ITEM_NIGHTSHADE = 0x0F88
ITEM_POISON_POTIONS = {
    "Lesser Poison": 0x0F0A,
    "Poison": 0x0F0A,
    "Greater Poison": 0x0F0A,
    "Deadly Poison": 0x0F0A
}

# Regular potions and their reagent requirements
REGULAR_POTIONS = {
    "Agility": {
        "skill_needed": 30.0,
        "reagents": {
            "Blood Moss": 1,
            "Ginseng": 1
        }
    },
    "Strength": {
        "skill_needed": 45.0,
        "reagents": {
            "Mandrake Root": 1,
            "Nightshade": 1
        }
    },
    "Greater Agility": {
        "skill_needed": 55.0,
        "reagents": {
            "Blood Moss": 3,
            "Ginseng": 3,
            "Spider's Silk": 1
        }
    },
    "Greater Strength": {
        "skill_needed": 65.0,
        "reagents": {
            "Mandrake Root": 3,
            "Nightshade": 3,
            "Spider's Silk": 1
        }
    },
    "Greater Heal": {
        "skill_needed": 75.0,
        "reagents": {
            "Ginseng": 7,
            "Garlic": 7,
            "Spider's Silk": 1,
            "Mandrake Root": 1
        }
    },
    "Greater Cure": {
        "skill_needed": 85.0,
        "reagents": {
            "Garlic": 6,
            "Ginseng": 6,
            "Mandrake Root": 2
        }
    },
    "Greater Conflagration": {
        "skill_needed": 95.0,
        "reagents": {
            "Spider's Silk": 5,
            "Sulfurous Ash": 5,
            "Black Pearl": 5
        }
    }
}

# Poison potions (only need Nightshade)
POISON_POTIONS = {
    "Lesser Poison": {
        "skill_needed": 25.0,
        "nightshade_amount": 1,
    },
    "Poison": {
        "skill_needed": 35.0,
        "nightshade_amount": 2,
    },
    "Greater Poison": {
        "skill_needed": 65.0,
        "nightshade_amount": 4,
    },
    "Deadly Poison": {
        "skill_needed": 99.0,
        "nightshade_amount": 8,
    }
}

# Reagent IDs
ITEM_REAGENTS = {
    "Black Pearl": 0x0F7A,
    "Blood Moss": 0x0F7B,
    "Garlic": 0x0F84,
    "Ginseng": 0x0F85,
    "Mandrake Root": 0x0F86,
    "Nightshade": 0x0F88,
    "Spider's Silk": 0x0F8D,
    "Sulfurous Ash": 0x0F8C
}

def debug_message(message):
    """Log debug messages with timestamp"""
    Misc.SendMessage(f"[Alchemy] {message}", COLOR_NORMAL)

def find_tool():
    """Find mortar and pestle in backpack"""
    tool = Items.FindByID(ITEM_MORTAR_AND_PESTLE, -1, Player.Backpack.Serial)
    if tool:
        debug_message(f"Found mortar and pestle: 0x{tool.Serial:X}")
    return tool

def count_reagent(reagent_id):
    """Count how many of a specific reagent are in the backpack"""
    items = Items.FindByID(reagent_id, -1, Player.Backpack.Serial)
    if items:
        return items.Amount
    return 0

def check_reagents(potion, potion_type):
    """Check if we have enough reagents for a potion"""
    if potion_type == "regular":
        for reagent, amount in REGULAR_POTIONS[potion]["reagents"].items():
            reagent_id = ITEM_REAGENTS[reagent]
            if count_reagent(reagent_id) < amount:
                return False
    elif potion_type == "poison":
        reagent_id = ITEM_NIGHTSHADE
        if count_reagent(reagent_id) < POISON_POTIONS[potion]["nightshade_amount"]:
            return False
    return True

def check_empty_bottles():
    """Check if we have empty bottles"""
    return count_reagent(ITEM_EMPTY_BOTTLE) > 0

def wait_for_gump():
    """Wait for the alchemy gump to appear"""
    return Gumps.WaitForGump(GUMP_ALCHEMY, 2000)

def make_potion(potion_name, potion_type):
    """
    Attempt to make a specific potion
    Returns True if successful, False otherwise
    """
    # Find mortar and pestle
    tool = find_tool()
    if not tool:
        debug_message("No mortar and pestle found!")
        return False

    # Check reagents
    if not check_reagents(potion_name, potion_type):
        debug_message(f"Not enough reagents for {potion_name}")
        return False

    # Use the tool
    debug_message(f"Using mortar and pestle: 0x{tool.Serial:X}")
    Items.UseItem(tool)
    if not wait_for_gump():
        debug_message("No alchemy gump appeared!")
        return False

    # Select the potion in the gump and make it
    if potion_type == "poison":
        Gumps.SendAction(GUMP_ALCHEMY, GUMP_BUTTON_TOXIC)
        if not Gumps.WaitForGump(GUMP_ALCHEMY, 1000):
            debug_message("No response after selecting Toxic category!")
            return False
        Gumps.SendAction(GUMP_ALCHEMY, POISON_BUTTONS[potion_name])
    else:
        Gumps.SendAction(GUMP_ALCHEMY, GUMP_BUTTON_MAKE_ALL)
    
    # Wait for crafting animation
    Misc.Pause(2000)
    return True

def make_max_poison(potion_name):
    """
    Make the maximum number of poison potions possible
    Returns True if successful, False otherwise
    """
    # Find mortar and pestle
    tool = find_tool()
    if not tool:
        debug_message("No mortar and pestle found!")
        return False

    # Check for empty bottles
    if not check_empty_bottles():
        debug_message("No empty bottles available!")
        return False

    # Calculate how many potions we can make based on nightshade amount
    nightshade_count = count_reagent(ITEM_NIGHTSHADE)
    nightshade_needed = POISON_POTIONS[potion_name]["nightshade_amount"]
    
    if nightshade_count < nightshade_needed:
        debug_message(f"Not enough nightshade for {potion_name}")
        return False

    # Use the tool and wait for gump
    debug_message(f"Using mortar and pestle: 0x{tool.Serial:X}")
    Items.UseItem(tool)
    if not Gumps.WaitForGump(GUMP_ALCHEMY, 1000):
        debug_message("No alchemy gump appeared!")
        return False

    # Click the Toxic category first
    debug_message("Selecting Toxic category")
    Gumps.SendAction(GUMP_ALCHEMY, GUMP_BUTTON_TOXIC)
    if not Gumps.WaitForGump(GUMP_ALCHEMY, 1000):
        debug_message("No response after selecting Toxic category!")
        return False

    # Select the specific poison type
    debug_message(f"Selecting {potion_name}")
    Gumps.SendAction(GUMP_ALCHEMY, POISON_BUTTONS[potion_name])
    if not Gumps.WaitForGump(GUMP_ALCHEMY, 1000):
        debug_message("No response after selecting poison type!")
        return False

    # Make maximum amount
    debug_message("Making maximum amount")
    Gumps.SendAction(GUMP_ALCHEMY, GUMP_BUTTON_MAKE_ALL)
    
    # Wait for crafting animation - longer wait since making multiple
    Misc.Pause(5000)
    return True

def drink_poison():
    """Find and drink a poison potion"""
    for potion_name in ITEM_POISON_POTIONS:
        potion = Items.FindByID(ITEM_POISON_POTIONS[potion_name], -1, Player.Backpack.Serial)
        if potion:
            debug_message(f"Drinking {potion_name}")
            Items.UseItem(potion)
            #Misc.Pause(1000)  # Wait for drinking animation
            return True
    return False

def train_alchemy():
    """Main training loop"""
    debug_message(f"Starting {SCRIPT_NAME} v{SCRIPT_VERSION}")
    debug_message("Poison Only Mode: " + ("Enabled" if POISON_ONLY_MODE else "Disabled"))
    
    while not Player.IsGhost:
        current_skill = Player.GetSkillValue("Alchemy")
        debug_message(f"Current Alchemy skill: {current_skill}")
        
        # Determine which potion to make based on skill
        potion_to_make = None
        if POISON_ONLY_MODE:
            for potion, info in POISON_POTIONS.items():
                if current_skill >= info["skill_needed"]:
                    potion_to_make = potion
        else:
            for potion, info in REGULAR_POTIONS.items():
                if current_skill >= info["skill_needed"]:
                    potion_to_make = potion
        
        if not potion_to_make:
            debug_message("No suitable potion found for current skill level")
            break
            
        debug_message(f"Making {potion_to_make}")
        if POISON_ONLY_MODE:
            if not make_max_poison(potion_to_make):
                debug_message("Failed to make poison potions, waiting 5 seconds...")
                Misc.Pause(1000)
                continue
                
            # Try to drink the poison we just made
            if not drink_poison():
                debug_message("No poison potions found to drink")
        else:
            if not make_potion(potion_to_make, "regular"):
                debug_message("Failed to make potion, waiting 5 seconds...")
                Misc.Pause(1000)
                continue
            
        # Small pause between attempts
        Misc.Pause(100)
        
    debug_message("Training complete or interrupted")

# Start the script
if __name__ == "__main__":
    train_alchemy()
