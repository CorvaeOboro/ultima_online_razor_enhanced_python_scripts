"""
HOME deposit resources - a Razor Enhanced Python Script for Ultima Online

Moves gathering resources (ingots, boards, logs, hides, leather, cloth, ores)
from the player's backpack into a designated home container.

Usage:
- Configure TARGET_CONTAINER_SERIALS with one or more container serials (most-preferred first).
- Optionally adjust which resource categories to move.
- Run the script while near your home container so Items.Move succeeds.

HOTKEY::
VERSION::20251016
"""

DEBUG_MODE = False  # Set True to see debug messages

# Resource category toggles
MOVE_INGOTS = True
MOVE_BOARDS = True
MOVE_LOGS = True
MOVE_LEATHER = True
MOVE_HIDES = True
MOVE_ORES = True
MOVE_CLOTH = True

# Provide one or more serials of valid target containers at home. The script uses the first valid one it finds.
# Example: [0x400ABC12, 0x400DEF34]
TARGET_CONTAINER_SERIALS = [0x4064C301]

# Priority index to pick when multiple valid containers are found
TARGET_PRIORITY_INDEX = 0

# ==============================
# Resource Items

# Ingots - All metal ingot types
INGOT_ITEMS = [
    {"name": "Iron Ingot", "id": 0x1BF2, "hue": None},
    {"name": "Dull Copper Ingot", "id": 0x1BEF, "hue": None},
    {"name": "Shadow Iron Ingot", "id": 0x1BEF, "hue": None},
    {"name": "Copper Ingot", "id": 0x1BEF, "hue": None},
    {"name": "Bronze Ingot", "id": 0x1BEF, "hue": None},
    {"name": "Gold Ingot", "id": 0x1BEF, "hue": None},
    {"name": "Agapite Ingot", "id": 0x1BEF, "hue": None},
    {"name": "Verite Ingot", "id": 0x1BEF, "hue": None},
    {"name": "Valorite Ingot", "id": 0x1BEF, "hue": None},
]

# Boards - All wood board types
BOARD_ITEMS = [
    {"name": "Board", "id": 0x1BD7, "hue": None},
    {"name": "Oak Board", "id": 0x1BDD, "hue": None},
    {"name": "Ash Board", "id": 0x1BDE, "hue": None},
    {"name": "Yew Board", "id": 0x1BDF, "hue": None},
    {"name": "Heartwood Board", "id": 0x1BE0, "hue": None},
    {"name": "Bloodwood Board", "id": 0x1BE1, "hue": None},
    {"name": "Frostwood Board", "id": 0x1BE2, "hue": None},
]

# Logs - Raw wood logs (before processing into boards)
LOG_ITEMS = [
    {"name": "Log", "id": 0x1BDD, "hue": None},
    {"name": "Log (Alt)", "id": 0x1BE0, "hue": None},
    {"name": "Log (Alt 2)", "id": 0x1BE1, "hue": None},
    {"name": "Log (Alt 3)", "id": 0x1BE2, "hue": None},
]

# Leather - Processed leather types
LEATHER_ITEMS = [
    {"name": "Leather", "id": 0x1078, "hue": None},
    {"name": "Spined Leather", "id": 0x1079, "hue": None},
    {"name": "Horned Leather", "id": 0x107A, "hue": None},
    {"name": "Barbed Leather", "id": 0x107B, "hue": None},
    {"name": "Cut Leather", "id": 0x1081, "hue": None},
]

# Hides - Raw hides (before processing into leather)
HIDE_ITEMS = [
    {"name": "Regular Hide", "id": 0x107C, "hue": None},
    {"name": "Spined Hide", "id": 0x107D, "hue": None},
    {"name": "Horned Hide", "id": 0x107E, "hue": None},
    {"name": "Barbed Hide", "id": 0x107F, "hue": None},
    {"name": "Pile of Hides", "id": 0x1079, "hue": None},
]

# Ores - Raw ore (before smelting into ingots)
ORE_ITEMS = [
    {"name": "Iron Ore", "id": 0x19B9, "hue": None},
    {"name": "Iron Ore B", "id": 0x19B7, "hue": None},
]

# Cloth - Cloth bolts and cut cloth
CLOTH_ITEMS = [
    {"name": "Cloth Bolt", "id": 0x0F95, "hue": None},
    {"name": "Cloth Bolt (Alt)", "id": 0x0F96, "hue": None},
    {"name": "Cloth Bolt (Alt 2)", "id": 0x0F97, "hue": None},
    {"name": "Cloth Bolt (Alt 3)", "id": 0x0F98, "hue": None},
    {"name": "Cloth Bolt (Alt 4)", "id": 0x0F99, "hue": None},
    {"name": "Cloth Bolt (Alt 5)", "id": 0x0F9A, "hue": None},
    {"name": "Cut Cloth", "id": 0x1766, "hue": None},
    {"name": "Cut Cloth (Alt)", "id": 0x1767, "hue": None},
    {"name": "Cut Cloth (Alt 2)", "id": 0x1768, "hue": None},
]

def debug_message(message, color=67):
    """Send a message if DEBUG_MODE is enabled."""
    if DEBUG_MODE:
        Misc.SendMessage(f"[HomeDeposit-Resources] {message}", color)

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
        debug_message(
            f"Priority index {TARGET_PRIORITY_INDEX} out of range for found containers (count: {len(found)}). Using index 0.",
            53,
        )
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

def deposit_resource_category(resource_list, category_name, target_container):
    """Move all items from a resource category into the target container."""
    total_moved = 0
    for info in resource_list:
        moved = deposit_all_matching(info, target_container)
        if moved:
            total_moved += moved
            Misc.Pause(100)
    if total_moved == 0:
        debug_message(f"No {category_name} to deposit.", 53)
    else:
        debug_message(f"Total {category_name} deposited: {total_moved}", 65)
    return total_moved

def main():
    debug_message("Starting Home Deposit: Resources", 65)

    target_container = pick_target_container()
    if not target_container:
        debug_message("Cannot proceed: No valid target container.", 33)
        return

    debug_message(
        f"Target container: serial {hex(target_container.Serial)} (ID 0x{target_container.ItemID:04X})",
        65,
    )

    total_items = 0

    if MOVE_INGOTS:
        total_items += deposit_resource_category(INGOT_ITEMS, "ingots", target_container)

    if MOVE_BOARDS:
        total_items += deposit_resource_category(BOARD_ITEMS, "boards", target_container)

    if MOVE_LOGS:
        total_items += deposit_resource_category(LOG_ITEMS, "logs", target_container)

    if MOVE_LEATHER:
        total_items += deposit_resource_category(LEATHER_ITEMS, "leather", target_container)

    if MOVE_HIDES:
        total_items += deposit_resource_category(HIDE_ITEMS, "hides", target_container)

    if MOVE_ORES:
        total_items += deposit_resource_category(ORE_ITEMS, "ores", target_container)

    if MOVE_CLOTH:
        total_items += deposit_resource_category(CLOTH_ITEMS, "cloth", target_container)

    if total_items > 0:
        Misc.SendMessage(f"[HomeDeposit-Resources] Deposited {total_items} total resource item(s)", 65)
    else:
        Misc.SendMessage("[HomeDeposit-Resources] No resource items found to deposit", 53)

    debug_message("Home Deposit complete.", 65)

if __name__ == "__main__":
    main()
