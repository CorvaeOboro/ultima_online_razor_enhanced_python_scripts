"""
HOME deposit runic - a Razor Enhanced Python Script for Ultima Online

Move all runic crafting items (non-default hue variants) from player backpack 
into a designated home container.

Deposits runic versions of:
- Wool (0x0DF8)
- Fletching (0x5737)
- Shafts (0x1BD4)
- Shards (0x5738)
- Soul Fragments (0x0F8E)

Only items with non-default hues (hue != 0) are deposited.

Usage:
- Configure TARGET_CONTAINER_SERIALS with one or more container serials (most-preferred first).
- Run the script while near your home container so Items.Move succeeds.

HOTKEY::
VERSION::20251017
"""

DEBUG_MODE = False  # Set True to see debug messages

# Provide one or more serials of valid target containers at home. The script uses the first valid one it finds.
# Example: [0x400ABC12, 0x400DEF34]
# Set to the user's specified runic materials container serial
TARGET_CONTAINER_SERIALS = [0x40E99CA4]  # CHANGE THIS to your container serial

# Priority index to pick when multiple valid containers are found
TARGET_PRIORITY_INDEX = 0

# ==============================
# Runic Crafting Items
# These are items that have special runic hues (non-zero hue values)
# We only deposit items with hue != 0

RUNIC_ITEMS = [
    {"name": "Runic Wool", "id": 0x0DF8},
    {"name": "Runic Fletching", "id": 0x5737},
    {"name": "Runic Shafts", "id": 0x1BD4},
    {"name": "Runic Shards", "id": 0x5738},
    {"name": "Runic Soul Fragments", "id": 0x0F8E},
]


def debug_message(message, color=67):
    """Send a message if DEBUG_MODE is enabled."""
    if DEBUG_MODE:
        Misc.SendMessage(f"[HomeDepositRunic] {message}", color)


def pick_target_container(container_serials=None, priority_index=None):
    """Select a valid target container from TARGET_CONTAINER_SERIALS by priority.
    Returns the container item object, or None if not found/invalid.
    """
    if container_serials is None:
        container_serials = TARGET_CONTAINER_SERIALS
    if priority_index is None:
        priority_index = TARGET_PRIORITY_INDEX

    if not container_serials:
        debug_message("No TARGET_CONTAINER_SERIALS configured. Please set your home runic chest serial(s).", 33)
        return None

    found = []
    for ser in container_serials:
        cont = Items.FindBySerial(ser)
        # ensure cont is a valid item object
        if cont is not None and hasattr(cont, "Serial") and not isinstance(cont, int):
            found.append(cont)
        else:
            debug_message(f"Container not found or invalid: {hex(ser)}", 53)

    if not found:
        debug_message("No valid target containers found in world. Be near/open your chest and try again.", 33)
        return None

    if priority_index >= len(found):
        debug_message(
            f"Priority index {priority_index} out of range for found containers (count: {len(found)}). Using index 0.",
            53,
        )
        return found[0]

    return found[priority_index]


def find_all_runic_variants(item_id, container_serial):
    """Find all runic variants (non-default hue) of an item in a container.
    Returns a list of all item objects with the specified ItemID and hue != 0.
    """
    variants = []
    all_items = Items.FindAllByID(item_id, -1, container_serial, -1)
    if not all_items:
        return variants
    if not isinstance(all_items, list):
        all_items = [all_items]
    for it in all_items:
        if it and it.Container == container_serial:
            # Only include items with non-default hue
            if hasattr(it, "Hue") and it.Hue != 0:
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


def deposit_all_runic_matching(item_info, target_container):
    """Deposit all runic instances (non-default hue) of an item from backpack into target container.
    Only deposits items with hue != 0.
    """
    item_id = item_info["id"]
    
    # Find all runic variants (non-default hue)
    variants = find_all_runic_variants(item_id, Player.Backpack.Serial)
    if not variants:
        return 0
    
    moved_total = 0
    hue_counts = {}  # Track how many of each hue we moved
    
    for it in variants:
        amt = it.Amount if hasattr(it, "Amount") else 1
        hue = it.Hue if hasattr(it, "Hue") else 0
        
        # Re-fetch by serial before moving to avoid stale references after prior moves
        latest = Items.FindBySerial(it.Serial)
        if latest is None:
            continue
        
        if move_item_stack_safe(latest, target_container.Serial, amt):
            moved_total += amt
            hue_counts[hue] = hue_counts.get(hue, 0) + amt
    
    if moved_total > 0:
        hue_list = ", ".join([f"hue {h}: {c}" for h, c in hue_counts.items()])
        debug_message(f"Deposited {moved_total} {item_info['name']} ({hue_list})", 67)
    
    return moved_total


def deposit_runic_items(target_container):
    """Move all runic crafting items from backpack into the target container."""
    total_moved = 0
    for info in RUNIC_ITEMS:
        moved = deposit_all_runic_matching(info, target_container)
        if moved:
            total_moved += moved
            Misc.Pause(100)
    
    if total_moved == 0:
        debug_message("No runic items to deposit.", 53)
    else:
        debug_message(f"Total runic items deposited: {total_moved}", 65)


def main():
    debug_message("Starting Home Deposit: Runic Crafting Items", 65)

    # Pick target container
    target_container = pick_target_container(TARGET_CONTAINER_SERIALS, TARGET_PRIORITY_INDEX)

    if not target_container:
        debug_message("Cannot proceed: No valid target container.", 33)
        Misc.SendMessage("[HomeDepositRunic] ERROR: No valid container found. Configure TARGET_CONTAINER_SERIALS.", 33)
        return

    # Announce picked container
    debug_message(
        f"Runic container: serial {hex(target_container.Serial)} (ID 0x{target_container.ItemID:04X})",
        65,
    )

    deposit_runic_items(target_container)

    debug_message("Home Deposit (Runic) complete.", 65)
    Misc.SendMessage("[HomeDepositRunic] Deposit complete!", 65)


if __name__ == "__main__":
    main()
