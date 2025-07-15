"""
BANK Auto Deposit and Restock -  A Razor Enhanced Python script for Ultima Online

move specific items from backpack to bank ( gems , supplies , special items )
restock reagents placing excessive and maintaing a "loadout" 
"resources" for crafting or imbueing are placed in a specific sub container inside the bank  

this script is similar to using an "Organizer" Agent in Razor , this script is slower but has more control 
current item dictionaries are based on UO Unchained , modify as needed

HOTKEY:: N
VERSION::20250714
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
RESOURCE_CONTAINER_SERIAL = 0x468092DD  # Set to the serial of your resource container (inside the bank box)

# Dictionary of items to deposit: Name -> ItemID
items_to_deposit = {
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
supplies_to_deposit = {
    'Arrow': 0x0F42,
    'Enchanted Apple': 0x09D0,
    'Metal Ingot': 0x1BF2,
    'Orb': 0x0EED,
    'empty bottle':    0x0F0E,
    'gold': 0x0EED,
}

# Dictionary of reagents to manage: Name -> ItemID
reagents_to_manage = {
    'Black Pearl':     0x0F7A,
    'Blood Moss':      0x0F7B,
    'Garlic':         0x0F84,
    'Ginseng':        0x0F85,
    'Mandrake Root':   0x0F86,
    'Nightshade':      0x0F88,
    'Spider Silk':     0x0F8D,
    'Sulfurous Ash':   0x0F8C,
}

# Dictionary of item IDs with specific hues and names for special items: ItemID -> {Hue -> Name}

# Dictionary of resources to deposit: Name -> ItemID
resources_to_deposit = {
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
itemIDs_to_name = {v: k for k, v in items_to_deposit.items()}
supplyIDs_to_name = {v: k for k, v in supplies_to_deposit.items()}
reagentIDs_to_name = {v: k for k, v in reagents_to_manage.items()}

def debug_message(msg, color=67):
    """Send a debug/status message if SHOW_DEBUG is enabled."""
    if DEBUG_MODE:
        Misc.SendMessage(msg, color)

def manage_reagents(bankBox):
    """Manage reagents based on min/max thresholds"""
    if not REAGENT_RESTOCK:
        return
        
    debug_message("Managing reagents...", 65)
    
    for reagent_id in reagents_to_manage.values():
        # Count reagents in backpack
        backpack_count = Items.ContainerCount(Player.Backpack.Serial, reagent_id, -1)
        reagent_name = reagentIDs_to_name[reagent_id]
        
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

def move_resources_to_subcontainer(bankBox, resourceContainer):
    """
    Move all resource items (from resources_to_deposit) from backpack to a specific sub-container in the bank box.
    Args:
        bankBox: Serial of the main bank box container
        resourceContainer: Serial of the sub-container inside the bank box
    """
    debug_message("Moving resources to bank sub-container...", 65)
    for resource_name, resource_id in resources_to_deposit.items():
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
        for item_id in items_to_deposit.values():
            items = Items.FindAllByID(item_id, -1, Player.Backpack.Serial, -1)
            for item in items:
                Items.Move(item, bankBox, 0)
                Misc.Pause(600)
                items_moved = True
                debug_message(f"Moved {itemIDs_to_name[item_id]} to bank", 65)

    # Move supplies if enabled
    if MOVE_SUPPLIES:
        for item_id in supplies_to_deposit.values():
            items = Items.FindAllByID(item_id, -1, Player.Backpack.Serial, -1)
            for item in items:
                Items.Move(item, bankBox, 0)
                Misc.Pause(600)
                items_moved = True
                debug_message(f"Moved {supplyIDs_to_name[item_id]} to bank", 65)

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
        resourceContainer = RESOURCE_CONTAINER_SERIAL  
        if resourceContainer:
            move_resources_to_subcontainer(bankBox, resourceContainer)
        else:
            debug_message("Resource container serial not set. Skipping resource move.", 33)

    # Manage reagents
    manage_reagents(bankBox)

    if not items_moved:
        debug_message("No items were moved to bank.", 65)


if __name__ == "__main__":
    main()
