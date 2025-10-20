"""
HOME deposit equipment - a Razor Enhanced Python Script for Ultima Online

Move armor and shield items from player backpack into a designated home container

Usage:
- Configure TARGET_CONTAINER_SERIALS with one or more container serials (most-preferred first).
- Optionally adjust which categories to move (armor types and shields).
- Run the script while near your home container so Items.Move succeeds.

TODO:
this could be combined into a larger script that handles bank deposit or home based on player coords
maybe this could try to find a suitable container based on what it finds inside? like an auto sorter based on an current setup 
unknown items get sent into what it thinks might be the "misc" container or a designated "unknown" container

HOTKEY::
VERSION::20250904
"""
DEBUG_MODE = False  # Set True to see debug messages
MOVE_ARMOR = True
MOVE_SHIELDS = True

# Provide one or more serials of valid target containers at home. The script uses the first valid one it finds.
# Example: [0x400ABC12, 0x400DEF34]
TARGET_CONTAINER_SERIALS = [0x40821935]

# Priority index to pick when multiple valid containers are found
TARGET_PRIORITY_INDEX = 0

# ==============================
# Items

# Armor Items - All armor types organized by material
ARMOR_ITEMS = [
    # Leather Armor
    {"name": "Leather Sleeves", "id": 0x13CD, "hue": None},
    {"name": "Leather Leggings", "id": 0x13CB, "hue": None},
    {"name": "Leather Tunic", "id": 0x13CC, "hue": None},
    {"name": "Leather Gloves", "id": 0x13C6, "hue": None},
    {"name": "Leather Cap", "id": 0x1DB9, "hue": None},
    {"name": "Leather Skirt", "id": 0x1C08, "hue": None},
    {"name": "Leather Armor (Female)", "id": 0x1C06, "hue": None},
    {"name": "Leather Mempo", "id": 0x277A, "hue": None},
    {"name": "Leather Shorts", "id": 0x1C00, "hue": None},
    {"name": "Leather Bustier", "id": 0x1C0A, "hue": None},

    # Platemail Armor
    {"name": "Plate Mail Chest", "id": 0x1415, "hue": None},
    {"name": "Plate Mail Legs", "id": 0x1411, "hue": None},
    {"name": "Plate Mail Gorget", "id": 0x1414, "hue": None},
    {"name": "Plate Mail Gloves", "id": 0x1413, "hue": None},
    {"name": "Platemail Mempo", "id": 0x2779, "hue": None},
    {"name": "Helmet", "id": 0x140A, "hue": None},
    {"name": "Bascinet", "id": 0x140C, "hue": None},
    {"name": "Norse Helm", "id": 0x140E, "hue": None},
    {"name": "Close Helm", "id": 0x1408, "hue": None},
    {"name": "Plate Helm", "id": 0x1412, "hue": None},
    {"name": "Platemail Female", "id": 0x1C04, "hue": None},
    {"name": "Platemail Arms", "id": 0x1410, "hue": None},

    # Chainmail Armor
    {"name": "Chainmail Tunic", "id": 0x13BF, "hue": None},
    {"name": "Chainmail Leggings", "id": 0x13BE, "hue": None},
    {"name": "Chainmail Coif", "id": 0x13BB, "hue": None},
    {"name": "Chainmail Tunic (Alt)", "id": 0x13C0, "hue": None},
    {"name": "Chainmail Sleeves", "id": 0x13C3, "hue": None},
    {"name": "Chainmail Gloves", "id": 0x13C4, "hue": None},
    {"name": "Chainmail Leggings (Alt)", "id": 0x13F0, "hue": None},

    # Bone Armor
    {"name": "Bone Armor", "id": 0x1B72, "hue": None},
    {"name": "Bone Legs", "id": 0x1B7B, "hue": None},
    {"name": "Bone Arms", "id": 0x1B73, "hue": None},
    {"name": "Bone Arms (Alt)", "id": 0x144E, "hue": None},
    {"name": "Bone Gloves", "id": 0x1B7A, "hue": None},
    {"name": "Bone Helmet", "id": 0x1B79, "hue": None},
    {"name": "Bone Gloves (Alternate)", "id": 0x1450, "hue": None},
    {"name": "Bone Leggings", "id": 0x1452, "hue": None},
    {"name": "Bone Armor Chest", "id": 0x144F, "hue": None},
    {"name": "Bone Helmet (Alt)", "id": 0x1451, "hue": None},

    # Ringmail Armor
    {"name": "Ring Mail Tunic", "id": 0x13C0, "hue": None},
    {"name": "Ringmail Tunic", "id": 0x13EC, "hue": None},
    {"name": "Ring Mail Sleeves", "id": 0x13C3, "hue": None},
    {"name": "Ring Mail Gloves", "id": 0x13C4, "hue": None},
    {"name": "Ringmail Sleeves", "id": 0x13EE, "hue": None},
    {"name": "Ringmail Leggings", "id": 0x13F0, "hue": None},
    {"name": "Ringmail Gloves", "id": 0x13EB, "hue": None},

    # Studded Armor
    {"name": "Studded Leather Gorget", "id": 0x13C7, "hue": None},
    {"name": "Studded Leather Tunic", "id": 0x13DB, "hue": None},
    {"name": "Studded Leather Sleeves", "id": 0x13D4, "hue": None},
    {"name": "Studded Leather Gloves", "id": 0x13DA, "hue": None},
    {"name": "Studded Leather Leggings", "id": 0x13D6, "hue": None},
    {"name": "Studded Mempo", "id": 0x279D, "hue": None},
    {"name": "Studded Gloves", "id": 0x13D5, "hue": None},
    {"name": "Studded Sleeves", "id": 0x13DC, "hue": None},
    {"name": "Studded Bustier", "id": 0x1C0C, "hue": None},
    {"name": "Studded Armor (Female)", "id": 0x1C02, "hue": None},
]

# Shield Items - All shield types
SHIELD_ITEMS = [
    # Base Shields
    {"name": "Bronze Shield", "id": 0x1B72, "hue": None},
    {"name": "Buckler", "id": 0x1B73, "hue": None},
    {"name": "Metal Kite Shield", "id": 0x1B74, "hue": None},
    {"name": "Shield", "id": 0x1B75, "hue": None},
    {"name": "Heater Shield", "id": 0x1B76, "hue": None},
    {"name": "Shield (Alt)", "id": 0x1B77, "hue": None},
    {"name": "Wooden Shield", "id": 0x1B78, "hue": None},
    {"name": "Shield (Alt2)", "id": 0x1B79, "hue": None},
    {"name": "Wooden Kite Shield", "id": 0x1B7A, "hue": None},
    {"name": "Metal Shield", "id": 0x1B7B, "hue": None},
    {"name": "Chaos Shield", "id": 0x1BC3, "hue": None},
    {"name": "Order Shield", "id": 0x1BC4, "hue": None},

    # Unknown/Special Shields
    {"name": "Shield (Unknown)", "id": 0x1BC5, "hue": None},
    {"name": "Shield (Special 1)", "id": 0x4201, "hue": None},
    {"name": "Shield (Special 2)", "id": 0x4200, "hue": None},
    {"name": "Shield (Special 3)", "id": 0x4202, "hue": None},
    {"name": "Shield (Special 4)", "id": 0x4203, "hue": None},
    {"name": "Shield (Special 5)", "id": 0x4204, "hue": None},
    {"name": "Shield (Special 6)", "id": 0x4205, "hue": None},
    {"name": "Shield (Special 7)", "id": 0x4206, "hue": None},
    {"name": "Shield (Special 8)", "id": 0x4207, "hue": None},
    {"name": "Shield (Special 9)", "id": 0x4208, "hue": None},
    {"name": "Shield (Special 10)", "id": 0x4228, "hue": None},
    {"name": "Shield (Special 11)", "id": 0x4229, "hue": None},
    {"name": "Shield (Special 12)", "id": 0x422A, "hue": None},
    {"name": "Shield (Special 13)", "id": 0x422C, "hue": None},
    {"name": "Shield (Special 14)", "id": 0x7817, "hue": None},
    {"name": "Shield (Special 15)", "id": 0x7818, "hue": None},
    {"name": "Shield (Special 16)", "id": 0xA649, "hue": None},
]

def debug_message(message, color=67):
    """Send a message if DEBUG_MODE is enabled."""
    if DEBUG_MODE:
        Misc.SendMessage(f"[HomeDeposit] {message}", color)

def pick_target_container():
    """Select a valid target container from TARGET_CONTAINER_SERIALS by priority.
    Returns the container item object, or None if not found/invalid.
    """
    if not TARGET_CONTAINER_SERIALS:
        debug_message("No TARGET_CONTAINER_SERIALS configured. Please set your home chest serial(s).", 33)
        return None

    found = []
    for ser in TARGET_CONTAINER_SERIALS:
        cont = Items.FindBySerial(ser)
        # ensure cont is a valid item object
        if cont is not None and hasattr(cont, "Serial") and not isinstance(cont, int):
            found.append(cont)
        else:
            debug_message(f"Container not found or invalid: {hex(ser)}", 53)

    if not found:
        debug_message("No valid target containers found in world. Be near/open your chest and try again.", 33)
        return None

    if TARGET_PRIORITY_INDEX >= len(found):
        debug_message(f"Priority index {TARGET_PRIORITY_INDEX} out of range for found containers (count: {len(found)}). Using index 0.", 53)
        return found[0]

    return found[TARGET_PRIORITY_INDEX]

def find_all_item_variants(item_id, container_serial):
    """Find all variants (different hues) of an item in a container.
    Returns a list of all item objects with the specified ItemID, regardless of hue.
    """
    variants = []
    all_items = Items.FindAllByID(item_id, -1, container_serial, -1)
    if not all_items:
        return variants
    if not isinstance(all_items, list):
        all_items = [all_items]
    for it in all_items:
        if it and it.Container == container_serial:
            variants.append(it)
    return variants

def move_item_stack_safe(item_obj, target_container_serial, amount):
    """Move a specific amount from a stack to target container, with pauses and basic retry prevention.
    After move, waits and returns True if action attempted.
    """
    if not item_obj or amount <= 0:
        return False
    try:
        Items.Move(item_obj, target_container_serial, amount)
        Misc.Pause(600)
        return True
    except Exception as e:
        debug_message(f"Move error for {hex(item_obj.ItemID)}: {e}", 33)
        Misc.Pause(300)
        return False

def deposit_all_matching(item_info, target_container):
    """Deposit all instances of an item from backpack into target container.
    Handles specific hue if given; otherwise deposits all hue variants (multiple stacks).
    """
    item_id = item_info["id"]
    hue = item_info.get("hue", None)

    if hue is not None:
        items = Items.FindByID(item_id, hue, Player.Backpack.Serial)
        if not items:
            return 0
        if not isinstance(items, list):
            items = [items]
        moved_total = 0
        for it in items:
            amt = it.Amount if hasattr(it, "Amount") else 1
            if move_item_stack_safe(it, target_container.Serial, amt):
                moved_total += amt
        if moved_total > 0:
            debug_message(f"Deposited {moved_total} {item_info['name']} (specific hue)", 67)
        return moved_total
    else:
        # All variants across hues
        variants = find_all_item_variants(item_id, Player.Backpack.Serial)
        if not variants:
            return 0
        moved_total = 0
        for it in variants:
            amt = it.Amount if hasattr(it, "Amount") else 1
            # Re-fetch by serial before moving to avoid stale references after prior moves
            latest = Items.FindBySerial(it.Serial)
            if latest is None:
                continue
            if move_item_stack_safe(latest, target_container.Serial, amt):
                moved_total += amt
        if moved_total > 0:
            debug_message(f"Deposited {moved_total} {item_info['name']} across {len(variants)} stack(s)", 67)
        return moved_total

def deposit_armor(target_container):
    """Move all armor items from backpack into the target container."""
    total_moved = 0
    for info in ARMOR_ITEMS:
        moved = deposit_all_matching(info, target_container)
        if moved:
            total_moved += moved
            Misc.Pause(100)
    if total_moved == 0:
        debug_message("No armor items to deposit.", 53)
    else:
        debug_message(f"Total armor items deposited: {total_moved}", 65)

def deposit_shields(target_container):
    """Move all shield items from backpack into the target container."""
    total_moved = 0
    for info in SHIELD_ITEMS:
        moved = deposit_all_matching(info, target_container)
        if moved:
            total_moved += moved
            Misc.Pause(100)
    if total_moved == 0:
        debug_message("No shield items to deposit.", 53)
    else:
        debug_message(f"Total shield items deposited: {total_moved}", 65)

def main():
    debug_message("Starting Home Deposit: Equipment", 65)

    target_container = pick_target_container()
    if not target_container:
        debug_message("Cannot proceed: No valid target container.", 33)
        return

    debug_message(f"Target container: serial {hex(target_container.Serial)} (ID 0x{target_container.ItemID:04X})", 65)

    if MOVE_ARMOR:
        deposit_armor(target_container)

    if MOVE_SHIELDS:
        deposit_shields(target_container)

    debug_message("Home Deposit complete.", 65)

if __name__ == "__main__":
    main()
