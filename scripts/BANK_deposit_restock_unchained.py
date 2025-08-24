"""
BANK Auto Deposit and Restock -  A Razor Enhanced Python script for Ultima Online

move specific items from backpack to bank ( gems , supplies , special items )
restock reagents placing excessive and maintaing a "loadout" 
"resources" for crafting or imbueing are placed in a specific sub container inside the bank  

this script is similar to using an "Organizer" Agent in Razor , this script is slower but has more control 
current item dictionaries are based on UO Unchained , modify as needed

HOTKEY:: N
VERSION::20250808
"""
BANK_PHRASE = "bank"
DEBUG_MODE = False # Set to True to enable debug/info messages
MOVE_GEMS = True # Set to True to enable moving gems to bank
MOVE_SUPPLIES = True # Set to True to enable moving supplies to bank
# Reagent RESTOCK 
REAGENT_RESTOCK = True # Set to True to enable reagent restocking
REAGENT_MIN = 100  # Minimum amount to keep in backpack
REAGENT_MAX = 200  # Amount above which to move to bank
# RESOURCES - crafting or imbue materials 
MOVE_RESOURCES = True  # Set to True to enable moving resources to sub-container
RESOURCE_CONTAINER_SERIALS = [0x40050F9D, 0x40047C80]  # List of possible resource container serials (inside the bank box, by priority)
RESOURCE_CONTAINER_PRIORITY = 0  # Index of the preferred container in the list
# POTION RESTOCK
POTION_RESTOCK = True  # Set to True to enable potion restocking
POTION_TARGET = 10  # Target amount of potions to maintain in backpack
# When True, if missing potions can't be pulled from bank, attempt to fill from kegs using empty bottles
POTION_USE_KEGS = False  # Global toggle to allow/disallow keg usage during restock

# Dictionary of items to deposit: Name -> ItemID
ITEMS_TO_DEPOSIT = {
    'Emerald':       0x0F10,
    'sapphireA':       0x0F11,
    'Ruby':          0x0F13,
    'Citrine':       0x0F15,
    'Amethyst':      0x0F16,
    'Sapphire':      0x0F19,
    'Star Sapphire': 0x0F21,
    'Amber':         0x0F25,
    'Diamond':       0x0F26,
    'Tourmaline':    0x0F2D,
    'TourmalineB':    0x0F18,
    'saphireB':    0x0F0F
}

# Dictionary of supplies to move: Name -> ItemID
SUPPLIES_TO_DEPOSIT = {
    'Arrow': 0x0F42,
    'Enchanted Apple': 0x09D0,
    'Metal Ingot': 0x1BF2,
    'Orb': 0x0EED,
    'empty bottle':    0x0F0E,
    'gold': 0x0EED,
}

# Dictionary of reagents to manage: Name -> ItemID
REAGENTS_TO_MANAGE = {
    'Black Pearl':     0x0F7A,
    'Blood Moss':      0x0F7B,
    'Garlic':         0x0F84,
    'Ginseng':        0x0F85,
    'Mandrake Root':   0x0F86,
    'Nightshade':      0x0F88,
    'Spider Silk':     0x0F8D,
    'Sulfurous Ash':   0x0F8C,
}

# Dictionary of potions to manage: Name -> ItemID
POTIONS_TO_MANAGE = {
    'Greater Heal Potion':    0x0F0C,
    'Greater Cure Potion':    0x0F07,
    'Greater Strength Potion': 0x0F09,
    'Greater Agility Potion': 0x0F08,
    'Total Refresh Potion':   0x0F0B,
    'Greater Magic Resist Potion': 0x0F06,
}

# Dictionary of resources to deposit: Name -> ItemID
# These are imbueing materials , we are placing them in a sub-container inside the bank box
# Orbs end up in here because of Void Obrs
# TODO: use hue to differentiate 
RESOURCES_TO_DEPOSIT = {
    'AcidSac': 0x0C67,
    'AncientPottery': 0x2243,
    'Bauble': 0x023B,
    'BlackrockCrystaline': 0x5732,
    'BlackrockCrystalineA': 0x5733,
    'BlackrockCrystalineB': 0x5734,
    'BlackrockCrystalineC': 0x5735,
    'BottleOfIchor': 0x5748,
    'CongealedSlugAcid': 0x5742,
    'CrystalOfShame': 0x400B,
    'CrystalShards': 0x5738,
    'CrystalShattered': 0x2248,
    'DaemonClaw': 0x5721,
    'DragonScale': 0x26B4,
    'EarHuman': 0x312F,
    'EarHumanA': 0x3130,
    'FaeryDust': 0x5745,
    'Feather': 0x1BD1,
    'FellowshipCoin': 0x2F60,
    'FireAntGoo': 0x122E,
    'FungusChaga': 0x5743,
    'FungusHeartwood': 0x0D16,
    'FungusLuminescent': 0x3191,
    'FungusMana': 0x7154,
    'FungusZoogi': 0x26B7,
    'GelatinousSkull': 0x1AE0,
    'GoblinBlood': 0x572C,
    'Granite': 0x1779,
    'HealthyGland': 0x1CEF,
    'Hide': 0x1079,
    'HornOfAbyssalInfernal': 0x2DB7,
    'LavaSerpentCrust': 0x572D,
    'Lodestone': 0x5739,
    'LuckyCoin': 0x0F87,
    'PlantParasitic': 0x3190,
    'PlantSeed': 0x0DCF,
    'PlantSeedA': 0x5736,
    'PowderTranslocation': 0x26B8,
    'RaptorTeeth': 0x5747,
    'SilverSerpentVenom': 0x0E24,
    'SlithEye': 0x5749,
    'SlithTongue': 0x5746,
    'SmokeBomb': 0x2808,
    'UndyingFlesh': 0x5731,
    'VialOfVitriol': 0x5722,
    'VialOfVitriolA': 0x5723,
    'VialOfVitriolB': 0x5724,
    'VialOfVitriolC': 0x5725,
    'VoidCore': 0x5728,
    'VoidCrystal': 0x1F19,
    'VoidCrystalA': 0x1F1A,
    'VoidCrystalB': 0x1F1B,
    'VoidEssence': 0x4007,
    'VoidOrb': 0x573E,
    'VoidOrbA': 0x573F,
    'VoidOrbB': 0x5740,
    'VoidOrbC': 0x5741,
    'WoodBarkFragment': 0x318F,
    'WoodLogs': 0x1BDD,
    'WoodSwitch': 0x2F5F,
    'SilverSnakeSkin': 0x5744,
    'FeyWings': 0x5726,
    'EnchantedEssence': 0x2DB2,
    'ElvenFletching': 0x5737,
    'PowderedIron': 0x573D,
    'MagicalResidue': 0x2DB1,
    'RelicFragment': 0x2DB3,
    'SpiderCarapace': 0x5720,
    'ArcanicRuneStone': 0x573C,
    'CrushedGlass': 0x573B,
    'FireRuby': 0x3197,
    'BlueDiamond': 0x3198,
    'WhitePearl': 0x3196,
}

special_items_dict = {
    0x09D0: {  # Berries
        1965: "Arcane Berries",
        6: "Tribal Berry"
    },
    0x0F42: {  # Thorn
        66: "Magical Green Thorn"
    }
}

#//=============================================================================

# dictionaries to map ItemID to Name for easy lookup
ITEMIDS_TO_NAME = {v: k for k, v in ITEMS_TO_DEPOSIT.items()}
SUPPLYIDS_TO_NAME = {v: k for k, v in SUPPLIES_TO_DEPOSIT.items()}
REAGENTIDS_TO_NAME = {v: k for k, v in REAGENTS_TO_MANAGE.items()}
POTIONIDS_TO_NAME = {v: k for k, v in POTIONS_TO_MANAGE.items()}

def debug_message(msg, color=67):
    """Send a debug/status message if SHOW_DEBUG is enabled."""
    if DEBUG_MODE:
        Misc.SendMessage(msg, color)

def manage_reagents(bankBox):
    """Manage reagents based on min/max thresholds"""
    if not REAGENT_RESTOCK:
        return
        
    debug_message("Managing reagents...", 65)
    
    for reagent_id in REAGENTS_TO_MANAGE.values():
        # Count reagents in backpack
        backpack_count = Items.ContainerCount(Player.Backpack.Serial, reagent_id, -1)
        reagent_name = REAGENTIDS_TO_NAME[reagent_id]
        
        if backpack_count > REAGENT_MAX:
            # Move excess to bank
            amount_to_move = backpack_count - REAGENT_MAX
            debug_message(f"Moving {amount_to_move} {reagent_name} to bank", 65)
            Items.Move(Items.FindByID(reagent_id, -1, Player.Backpack.Serial, -1), bankBox, amount_to_move)
            Misc.Pause(600)
        elif backpack_count < REAGENT_MIN:
            # Get reagents from bank
            amount_needed = REAGENT_MIN - backpack_count
            bank_reagent = Items.FindByID(reagent_id, -1, bankBox.Serial, -1)
            if bank_reagent:
                debug_message(f"Getting {amount_needed} {reagent_name} from bank", 65)
                Items.Move(bank_reagent, Player.Backpack, amount_needed)
                Misc.Pause(600)
            else:
                debug_message(f"Warning: No {reagent_name} found in bank!", 33)

def manage_potions(bankBox):
    """Manage potions based on target amount.
    Behavior:
    - Pull potions from bank when available.
    - If still short and POTION_USE_KEGS is True, attempt to fill from kegs using empty bottles.
    """
    if not POTION_RESTOCK:
        return
        
    debug_message("Managing potions...", 65)
    
    for potion_id in POTIONS_TO_MANAGE.values():
        potion_name = POTIONIDS_TO_NAME[potion_id]
        
        # Count potions in backpack
        backpack_count = Items.ContainerCount(Player.Backpack.Serial, potion_id, -1)
        
        if backpack_count < POTION_TARGET:
            potions_needed = POTION_TARGET - backpack_count
            debug_message(f"Need {potions_needed} more {potion_name}. Current: {backpack_count}", 65)
            
            # First, try to get potions directly from bank
            bank_potion = Items.FindByID(potion_id, -1, bankBox.Serial, -1)
            if bank_potion and bank_potion.Amount >= potions_needed:
                debug_message(f"Getting {potions_needed} {potion_name} from bank", 65)
                Items.Move(bank_potion, Player.Backpack, potions_needed)
                Misc.Pause(600)
                continue
            elif bank_potion and bank_potion.Amount > 0:
                # Take what's available
                available = bank_potion.Amount
                debug_message(f"Getting {available} {potion_name} from bank (partial)", 65)
                Items.Move(bank_potion, Player.Backpack, available)
                Misc.Pause(600)
                potions_needed -= available
            
            # If we still need potions, optionally try to make them from kegs and empty bottles
            if potions_needed > 0:
                if POTION_USE_KEGS:
                    debug_message(f"Still need {potions_needed} {potion_name}. Attempting to create from keg...", 65)
                    create_potions_from_keg(bankBox, potion_id, potion_name, potions_needed)
                else:
                    debug_message(f"Still need {potions_needed} {potion_name}, but POTION_USE_KEGS is disabled; skipping keg fill.", 53)

def create_potions_from_keg(bankBox, potion_id, potion_name, amount_needed):
    """Create potions by using a keg and empty bottles from the bank."""
    # THIS IS WORK IN PROGRESS , currently not working
    
    # Find empty bottles in bank (ItemID 0x0F0E)
    empty_bottle_id = 0x0F0E
    bank_bottles = Items.FindByID(empty_bottle_id, -1, bankBox.Serial, -1)
    
    if not bank_bottles or bank_bottles.Amount < amount_needed:
        debug_message(f"Warning: Not enough empty bottles in bank for {potion_name}. Need {amount_needed}, found {bank_bottles.Amount if bank_bottles else 0}", 33)
        return
    
    # Get empty bottles from bank to backpack
    debug_message(f"Getting {amount_needed} empty bottles from bank", 65)
    Items.Move(bank_bottles, Player.Backpack, amount_needed)
    Misc.Pause(600)
    
    # Find appropriate keg in bank
    # Kegs typically have different ItemIDs based on potion type
    # For this implementation, we'll search for kegs by looking for items that might be kegs
    # This is a simplified approach - you may need to adjust keg ItemIDs based on your server
    keg_ids = [0x1940, 0x1941, 0x1942, 0x1943, 0x1944, 0x1945]  # Common keg ItemIDs
    
    keg_found = None
    for keg_id in keg_ids:
        potential_keg = Items.FindByID(keg_id, -1, bankBox.Serial, -1)
        if potential_keg:
            # Additional check could be done here to verify it's the right type of keg
            # For now, we'll use the first keg found
            keg_found = potential_keg
            break
    
    if not keg_found:
        debug_message(f"Warning: No suitable keg found in bank for {potion_name}", 33)
        # Return bottles to bank
        backpack_bottles = Items.FindByID(empty_bottle_id, -1, Player.Backpack.Serial, -1)
        if backpack_bottles:
            Items.Move(backpack_bottles, bankBox, amount_needed)
            Misc.Pause(600)
        return
    
    debug_message(f"Found keg (ID: 0x{keg_found.ItemID:04X}) for {potion_name}", 65)
    
    # Use keg to fill bottles
    for i in range(amount_needed):
        # Find an empty bottle in backpack
        empty_bottle = Items.FindByID(empty_bottle_id, -1, Player.Backpack.Serial, -1)
        if empty_bottle:
            debug_message(f"Using keg to fill bottle {i+1}/{amount_needed}", 65)
            # Use the empty bottle on the keg
            Items.UseItem(empty_bottle)
            Misc.Pause(200)
            Target.TargetExecute(keg_found)
            Misc.Pause(800)  # Wait for the potion to be created
        else:
            debug_message(f"Warning: No empty bottle found in backpack for filling {i+1}", 33)
            break
    
    debug_message(f"Completed potion creation attempt for {potion_name}", 65)

def move_resources_to_subcontainer(bankBox, resourceContainer):
    """
    Move all resource items (from RESOURCES_TO_DEPOSIT) from backpack to a specific sub-container in the bank box.
    Args:
        bankBox: Serial of the main bank box container
        resourceContainer: Serial of the sub-container inside the bank box
    """
    debug_message("Moving resources to bank sub-container...", 65)
    for resource_name, resource_id in RESOURCES_TO_DEPOSIT.items():
        # Find all matching items in backpack
        items = Items.FindByID(resource_id, -1, Player.Backpack.Serial)
        if not items:
            continue
        if not isinstance(items, list):
            items = [items]
        for item in items:
            amount = item.Amount if hasattr(item, 'Amount') else 1
            debug_message(f"Moving {amount} {resource_name} (0x{resource_id:04X}) to resource container", 65)
            Items.Move(item, resourceContainer, amount)
            Misc.Pause(600)

def main():
    # Open bank box
    debug_message("Attempting to open bank box...", 65)
    Player.ChatSay(1, BANK_PHRASE)
    Misc.Pause(500)

    # Get bank box container
    bankBox = Player.Bank

    if bankBox == None:
        debug_message("ERROR: Bank box None ", 33)
        return

    # Log bank box serial
    debug_message("Bank box serial: " + hex(bankBox.Serial), 65)
    # Log player's backpack serial
    debug_message("Backpack serial: " + hex(Player.Backpack.Serial), 65)

    # Check if bank box serial is valid
    if bankBox.Serial == 0:
        debug_message("Error: Bank box serial is 0.", 33)
        stop()
        return

    # Flag to check if any items were moved
    items_moved = False

    # Move gems if enabled
    if MOVE_GEMS:
        for item_id in ITEMS_TO_DEPOSIT.values():
            items = Items.FindAllByID(item_id, -1, Player.Backpack.Serial, -1)
            for item in items:
                Items.Move(item, bankBox, 0)
                Misc.Pause(600)
                items_moved = True
                debug_message(f"Moved {ITEMIDS_TO_NAME[item_id]} to bank", 65)

    # Move supplies if enabled
    if MOVE_SUPPLIES:
        for item_id in SUPPLIES_TO_DEPOSIT.values():
            items = Items.FindAllByID(item_id, -1, Player.Backpack.Serial, -1)
            for item in items:
                Items.Move(item, bankBox, 0)
                Misc.Pause(600)
                items_moved = True
                debug_message(f"Moved {SUPPLYIDS_TO_NAME[item_id]} to bank", 65)

        for item_id, hue_dict in special_items_dict.items():
            for hue, name in hue_dict.items():
                items = Items.FindAllByID(item_id, hue, Player.Backpack.Serial, -1)
                for item in items:
                    Items.Move(item, bankBox, 0)
                    Misc.Pause(600)
                    items_moved = True
                    debug_message(f"Moved {name} to bank", 65)

    # Optionally move resources to a specific sub-container in the bank
    if MOVE_RESOURCES:
        # Find all matching resource containers in the bank
        found_containers = []
        for serial in RESOURCE_CONTAINER_SERIALS:
            container = Items.FindBySerial(serial)
            # Only append valid item objects (not ints)
            if container is not None and hasattr(container, "Container") and container.Container == bankBox.Serial:
                if hasattr(container, "Serial") and not isinstance(container, int):
                    found_containers.append(container)
                else:
                    debug_message(f"Skipping invalid container for serial {serial}: type={type(container)}", 33)
        if not found_containers:
            debug_message("Resource container serial not found in bank. Skipping resource move.", 33)
        else:
            # Warn if multiple containers found
            if len(found_containers) > 1:
                debug_message(f"Warning: Multiple resource containers found in bank: {[hex(c.Serial) for c in found_containers]}", 53)
            if RESOURCE_CONTAINER_PRIORITY < len(found_containers):
                debug_message(f"Using priority container: {hex(found_containers[RESOURCE_CONTAINER_PRIORITY].Serial)}", 53)
                resourceContainer = found_containers[RESOURCE_CONTAINER_PRIORITY]
                move_resources_to_subcontainer(bankBox, resourceContainer.Serial)
            else:
                debug_message(f"Priority index {RESOURCE_CONTAINER_PRIORITY} out of range for found containers (count: {len(found_containers)}). Skipping resource move.", 33)

    # Manage reagents
    manage_reagents(bankBox)
    
    # Manage potions
    manage_potions(bankBox)

    if not items_moved:
        debug_message("No items were moved to bank.", 65)


if __name__ == "__main__":
    main()
