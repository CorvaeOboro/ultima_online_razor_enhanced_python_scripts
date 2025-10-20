"""
HOME deposit enhancement scrolls - a Razor Enhanced Python Script for Ultima Online

Moves all enhancement scrolls (ItemID 0x0E34) from the player's backpack
into a designated home container, handling multiple hues/variants.

HOTKEY::
VERSION::20250912
"""

DEBUG_MODE = False  # Set True to see debug messages

TARGET_CONTAINER_SERIALS = [0x4032B6B1] # Container serial: 0x4032B6B1
ENHANCEMENT_SCROLL_ID = 0x0E34 # Enhancement Scroll ItemID (applies to all hues)
TARGET_PRIORITY_INDEX = 0

def debug_message(message, color=67):
    """Send a message if DEBUG_MODE is enabled."""
    if DEBUG_MODE:
        Misc.SendMessage(f"[HomeDeposit-EnhScrolls] {message}", color)

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

def deposit_all_enhancement_scrolls(target_container):
    """Deposit all enhancement scrolls (ID 0x0E34) from backpack into target container.
    Handles all hue variants by moving each stack found.
    """
    variants = find_all_item_variants(ENHANCEMENT_SCROLL_ID, Player.Backpack.Serial)
    if not variants:
        debug_message("No enhancement scrolls found to deposit.", 53)
        return 0

    moved_total = 0
    stacks_processed = 0

    for it in variants:
        amt = it.Amount if hasattr(it, "Amount") else 1
        # Re-fetch by serial before moving to avoid stale references after prior moves
        latest = Items.FindBySerial(it.Serial)
        if latest is None:
            continue
        if move_item_stack_safe(latest, target_container.Serial, amt):
            moved_total += amt
            stacks_processed += 1
            # small pacing pause between stacks
            Misc.Pause(100)

    if moved_total > 0:
        debug_message(
            f"Deposited {moved_total} enhancement scroll(s) across {stacks_processed} stack(s)",
            65,
        )
    else:
        debug_message("No enhancement scrolls were deposited.", 53)

    return moved_total

def main():
    debug_message("Starting Home Deposit: Enhancement Scrolls", 65)

    target_container = pick_target_container()
    if not target_container:
        debug_message("Cannot proceed: No valid target container.", 33)
        return

    debug_message(
        f"Target container: serial {hex(target_container.Serial)} (ID 0x{target_container.ItemID:04X})",
        65,
    )

    total = deposit_all_enhancement_scrolls(target_container)

    if total > 0:
        debug_message(f"Total enhancement scrolls deposited: {total}", 65)
    debug_message("Home Deposit complete.", 65)

if __name__ == "__main__":
    main()
