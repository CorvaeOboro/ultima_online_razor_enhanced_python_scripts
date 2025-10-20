"""
BANK Deposit and Restock -  A Razor Enhanced Python script for Ultima Online

move specific items from backpack to bank ( gems , supplies , special items )
restock reagents maintaining a "loadout" 
"resources" for crafting or imbueing are placed in a specific sub container inside the bank  

this script is similar to using an "Organizer" Agent in Razor ,
this script is a little slower but has more control and updates and distributes easier then organizer presets

HOTKEY:: N
VERSION::20250923
"""

BANK_PHRASE = "bank"
DEBUG_MODE = False # Set to True to enable debug/info messages
MOVE_GEMS = True # Set to True to enable moving gems to bank
MOVE_SUPPLIES = True # Set to True to enable moving supplies to bank
# Reagent RESTOCK 
REAGENT_RESTOCK = True # Set to True to enable reagent restocking
# Reagent configuration - format: reagent_name: {'id': ItemID, 'min': min_amount, 'max': max_amount}
REAGENTS_CONFIG = {
    'Black Pearl': {'id': 0x0F7A, 'min': 200, 'max': 300},     # Higher min/max due to frequent use
    'Nightshade': {'id': 0x0F88, 'min': 200, 'max': 300},      # Higher min/max due to frequent use
    'Blood Moss': {'id': 0x0F7B, 'min': 100, 'max': 200},      # Standard amounts
    'Garlic': {'id': 0x0F84, 'min': 100, 'max': 200},          # Standard amounts
    'Ginseng': {'id': 0x0F85, 'min': 100, 'max': 200},         # Standard amounts
    'Mandrake Root': {'id': 0x0F86, 'min': 100, 'max': 200},   # Standard amounts
    'Spider Silk': {'id': 0x0F8D, 'min': 100, 'max': 200},     # Standard amounts
    'Sulfurous Ash': {'id': 0x0F8C, 'min': 100, 'max': 200},   # Standard amounts
}

# Mana-based reagent restock profile
# If player's max mana is below this threshold, use lower targets and remove extra Nightshade/Black Pearl bias
LOW_MANA_THRESHOLD = 100
LOW_MANA_MIN = 70
LOW_MANA_MAX = 100
# RESOURCES - crafting or imbue materials 
MOVE_RESOURCES = True  # Set to True to enable moving resources to sub-container
RESOURCE_CONTAINER_SERIALS = [0x40050F9D, 0x40047C80,0x4191C850,0x403047BA]  # List of possible resource container serials (inside the bank box, by priority)
RESOURCE_CONTAINER_PRIORITY = 0  # Index of the preferred container in the list
# POTION RESTOCK
POTION_RESTOCK = True  # Set to True to enable potion restocking
# Potion configuration - format: potion_name: {'id': ItemID, 'target': target_amount}
POTIONS_CONFIG = {
    'Greater Heal Potion': {'id': 0x0F0C, 'target': 5},
    'Greater Cure Potion': {'id': 0x0F07, 'target': 5},
    'Greater Strength Potion': {'id': 0x0F09, 'target': 1},
    'Greater Agility Potion': {'id': 0x0F08, 'target': 0},
    'Total Refresh Potion': {'id': 0x0F0B, 'target': 5},
    'Greater Magic Resist Potion': {'id': 0x0F06, 'target': 0},
}

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

# Dictionary of resources to deposit: Name -> ItemID
# These are imbueing / enchanting materials , we are placing them in a sub-container inside the bank box
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

# Champion Crystals - Exclude from all deposits (different hues)
CHAMPION_CRYSTAL_ID = 0x1F19

# Mastery Orbs - Exclude from resources container (different hues)
MASTERY_ORBS = {
    0x573E: {  # Mastery Orb ItemID
        # Add known hues here as they are discovered
        # Format: hue_value: "Mastery Type Name"
        # These should NOT go into resources container
    }
}

#//=============================================================================

# dictionaries to map ItemID to Name for easy lookup
ITEMIDS_TO_NAME = {v: k for k, v in ITEMS_TO_DEPOSIT.items()}
SUPPLYIDS_TO_NAME = {v: k for k, v in SUPPLIES_TO_DEPOSIT.items()}
REAGENTIDS_TO_NAME = {v['id']: k for k, v in REAGENTS_CONFIG.items()}
POTIONIDS_TO_NAME = {v['id']: k for k, v in POTIONS_CONFIG.items()}

def debug_message(msg, color=67):
    """Send a debug/status message if SHOW_DEBUG is enabled."""
    if DEBUG_MODE:
        Misc.SendMessage(msg, color)

def log_player_mana_info():
    """Log detailed mana information for debugging purposes."""
    try:
        try:
            mm = Player.ManaMax
        except Exception:
            mm = None
        try:
            m = Player.Mana
        except Exception:
            m = None
        debug_message(f"[Mana Debug] ManaMax={mm} (type={type(mm).__name__}), Mana={m} (type={type(m).__name__})", 68)
    except Exception as e:
        debug_message(f"[Mana Debug] Error reading mana fields: {e}", 33)

def get_player_max_mana():
    """Return player's maximum mana capacity using Player.ManaMax like the UI scripts do."""
    try:
        try:
            mm = Player.ManaMax
        except Exception:
            mm = 0
        try:
            im = int(mm)
        except Exception:
            im = 0
        if im and im > 0:
            debug_message(f"[Mana Debug] Using ManaMax={mm} -> int={im} for profile selection", 68)
            return im
        # Fallback: derive max mana from components if ManaMax is unavailable on this shard or client
        try:
            base_int = int(Player.Int or 0)
        except Exception:
            base_int = 0
        try:
            max_mana_inc = int(Player.MaximumManaIncrease or 0)
        except Exception:
            max_mana_inc = 0
        try:
            mana_inc = int(Player.ManaIncrease or 0)
        except Exception:
            mana_inc = 0
        try:
            cur_mana = int(Player.Mana or 0)
        except Exception:
            cur_mana = 0
        computed = base_int + max_mana_inc + mana_inc
        # Ensure we never report less than current mana
        chosen = max(computed, cur_mana)
        debug_message(
            f"[Mana Debug] Fallback compute: Int={base_int}, MaximumManaIncrease={max_mana_inc}, ManaIncrease={mana_inc}, current Mana={cur_mana} => computed={computed}, chosen={chosen}",
            68
        )
        return chosen
    except Exception:
        return 0

def get_reagents_config_for_mana():
    """Build a reagent config adjusted for player's total mana.
    - If max mana < LOW_MANA_THRESHOLD: use LOW_MANA_MIN..LOW_MANA_MAX for ALL reagents (no extra NS/BP).
    - Otherwise: use REAGENTS_CONFIG as-is (pure mage/higher mana profile).
    """
    total_mana = get_player_max_mana()
    # Shallow copy preserving ids
    adjusted = {}
    if total_mana < LOW_MANA_THRESHOLD:
        debug_message(f"Using low-mana reagent profile (max mana: {total_mana}) -> {LOW_MANA_MIN}-{LOW_MANA_MAX} each, no NS/BP extra", 65)
        for name, cfg in REAGENTS_CONFIG.items():
            adjusted[name] = {'id': cfg['id'], 'min': LOW_MANA_MIN, 'max': LOW_MANA_MAX}
    else:
        debug_message(f"Using standard reagent profile (max mana: {total_mana})", 65)
        for name, cfg in REAGENTS_CONFIG.items():
            adjusted[name] = {'id': cfg['id'], 'min': cfg['min'], 'max': cfg['max']}
    return adjusted

def manage_reagents(bankBox):
    """Manage reagents based on individual min/max thresholds"""
    if not REAGENT_RESTOCK:
        return
        
    debug_message("Managing reagents...", 65)
    
    # Build mana-aware configuration
    mana_reagents_config = get_reagents_config_for_mana()
    
    for reagent_name, reagent_config in mana_reagents_config.items():
        reagent_id = reagent_config['id']
        reagent_min = reagent_config['min']
        reagent_max = reagent_config['max']
        
        # Count reagents in backpack
        backpack_count = Items.ContainerCount(Player.Backpack.Serial, reagent_id, -1)
        
        if backpack_count > reagent_max:
            # Move excess to bank
            amount_to_move = backpack_count - reagent_max
            debug_message(f"Moving {amount_to_move} {reagent_name} to bank (current: {backpack_count}, max: {reagent_max})", 65)
            Items.Move(Items.FindByID(reagent_id, -1, Player.Backpack.Serial, -1), bankBox, amount_to_move)
            Misc.Pause(600)
        elif backpack_count < reagent_min:
            # Get reagents from bank
            amount_needed = reagent_min - backpack_count
            bank_reagent = Items.FindByID(reagent_id, -1, bankBox.Serial, -1)
            if bank_reagent:
                debug_message(f"Getting {amount_needed} {reagent_name} from bank (current: {backpack_count}, min: {reagent_min})", 65)
                Items.Move(bank_reagent, Player.Backpack, amount_needed)
                Misc.Pause(600)
            else:
                debug_message(f"Warning: No {reagent_name} found in bank!", 33)

def manage_potions(bankBox):
    """Manage potions based on target amount.
    Behavior:
    - Pull potions from bank when available.
    """
    if not POTION_RESTOCK:
        return
        
    debug_message("Managing potions...", 65)
    
    for potion_name, potion_config in POTIONS_CONFIG.items():
        potion_id = potion_config['id']
        potion_target = potion_config['target']
        
        # Count potions in backpack
        backpack_count = Items.ContainerCount(Player.Backpack.Serial, potion_id, -1)
        
        if backpack_count < potion_target:
            potions_needed = potion_target - backpack_count
            debug_message(f"Need {potions_needed} more {potion_name}. Current: {backpack_count}, Target: {potion_target}", 65)
            
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
            
            # If we still need potions after checking bank, log the shortage
            if potions_needed > 0:
                debug_message(f"Warning: Still need {potions_needed} {potion_name} but none available in bank", 33)

def is_excluded_item(item, item_id):
    """
    Check if an item should be excluded from resource container deposits.
    Returns True if item should be excluded (champion crystals or mastery orbs).
    """
    # Exclude champion crystals (all hues)
    if item_id == CHAMPION_CRYSTAL_ID:
        debug_message(f"Excluding Champion Crystal (0x{item_id:04X}, hue: {item.Hue}) from resources", 68)
        return True
    
    # Exclude mastery orbs (ItemID 0x573E, all hues)
    if item_id == 0x573E:
        hue = item.Hue if hasattr(item, 'Hue') else 0
        if item_id in MASTERY_ORBS:
            # Known mastery orb
            orb_name = MASTERY_ORBS[item_id].get(hue, f"Unknown Mastery Orb (hue: {hue})")
            debug_message(f"Excluding {orb_name} (0x{item_id:04X}) from resources", 68)
        else:
            debug_message(f"Excluding Mastery Orb (0x{item_id:04X}, hue: {hue}) from resources", 68)
        return True
    
    return False

def move_resources_to_subcontainer(bankBox, resourceContainer):
    """
    Move all resource items (from RESOURCES_TO_DEPOSIT) from backpack to a specific sub-container in the bank box.
    Excludes champion crystals (0x1F19) and mastery orbs (0x573E) regardless of hue.
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
            # Check if item should be excluded
            if is_excluded_item(item, resource_id):
                continue
            
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

    # Verbose mana debug and threshold info
    log_player_mana_info()
    current_max_mana = get_player_max_mana()
    debug_message(f"[Mana Debug] LOW_MANA_THRESHOLD={LOW_MANA_THRESHOLD}, resolved max mana={current_max_mana}", 68)

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
