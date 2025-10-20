"""
HOME deposit scrolls - a Razor Enhanced Python Script for Ultima Online

Move specific items from player backpack into a designated home container

Usage:
- Configure TARGET_CONTAINER_SERIALS with one or more container serials (most-preferred first).
- Optionally adjust which categories to move (currently only magic scrolls).
- Run the script while near your home container so Items.Move succeeds.

TODO:
this coudl be combined into a larger script that handles bank deposit or home based on player coords
maybe this could try to find a suitable container based on what it finds inside? like an auto sorter based on an current setup 
unknown items get sent into what it thinks might be the "misc" container or a designated "unknown" container

HOTKEY::
VERSION::20250828
"""
DEBUG_MODE = False  # Set True to see debug messages
MOVE_MAGIC_SCROLLS = True

# Provide one or more serials of valid target containers at home. The script uses the first valid one it finds.
# Example: [0x400ABC12, 0x400DEF34]
TARGET_CONTAINER_SERIALS = [0x40329D45]

# Priority index to pick when multiple valid containers are found
TARGET_PRIORITY_INDEX = 0

# ==============================
# Items

# Magic Scrolls - All spell scrolls organized by circle
MAGIC_SCROLLS = [
    # Circle 1 Scrolls
    {"name": "1_Clumsy", "id": 0x1F2E, "hue": None},
    {"name": "1_CreateFood", "id": 0x1F2F, "hue": None},
    {"name": "1_Feeblemind", "id": 0x1F30, "hue": None},
    {"name": "1_Heal", "id": 0x1F31, "hue": None},
    {"name": "1_MagicArrow", "id": 0x1F32, "hue": None},
    {"name": "1_NightSight", "id": 0x1F33, "hue": None},
    {"name": "1_ReactiveArmor", "id": 0x1F2D, "hue": None},
    {"name": "1_Weaken", "id": 0x1F34, "hue": None},
    # Circle 2 Scrolls
    {"name": "2_Agility", "id": 0x1F35, "hue": None},
    {"name": "2_Cunning", "id": 0x1F36, "hue": None},
    {"name": "2_Cure", "id": 0x1F37, "hue": None},
    {"name": "2_Harm", "id": 0x1F38, "hue": None},
    {"name": "2_MagicTrap", "id": 0x1F39, "hue": None},
    {"name": "2_MagicUnTrap", "id": 0x1F3A, "hue": None},
    {"name": "2_Protection", "id": 0x1F3B, "hue": None},
    {"name": "2_Strength", "id": 0x1F3C, "hue": None},
    # Circle 3 Scrolls
    {"name": "3_Bless", "id": 0x1F3D, "hue": None},
    {"name": "3_Fireball", "id": 0x1F3E, "hue": None},
    {"name": "3_MagicLock", "id": 0x1F3F, "hue": None},
    {"name": "3_Poison", "id": 0x1F40, "hue": None},
    {"name": "3_Telekinisis", "id": 0x1F41, "hue": None},
    {"name": "3_Teleport", "id": 0x1F42, "hue": None},
    {"name": "3_Unlock", "id": 0x1F43, "hue": None},
    {"name": "3_WallOfStone", "id": 0x1F44, "hue": None},
    # Circle 4 Scrolls
    {"name": "4_ArchCure", "id": 0x1F45, "hue": None},
    {"name": "4_ArchProtection", "id": 0x1F46, "hue": None},
    {"name": "4_Curse", "id": 0x1F47, "hue": None},
    {"name": "4_FireField", "id": 0x1F48, "hue": None},
    {"name": "4_GreaterHeal", "id": 0x1F49, "hue": None},
    {"name": "4_Lightning", "id": 0x1F4A, "hue": None},
    {"name": "4_ManaDrain", "id": 0x1F4B, "hue": None},
    {"name": "4_Recall", "id": 0x1F4C, "hue": None},
    # Circle 5 Scrolls
    {"name": "5_BladeSpirits", "id": 0x1F4D, "hue": None},
    {"name": "5_DispelField", "id": 0x1F4E, "hue": None},
    {"name": "5_Incognito", "id": 0x1F4F, "hue": None},
    {"name": "5_MagicReflect", "id": 0x1F50, "hue": None},
    {"name": "5_MindBlast", "id": 0x1F51, "hue": None},
    {"name": "5_Paralyze", "id": 0x1F52, "hue": None},
    {"name": "5_PoisonField", "id": 0x1F53, "hue": None},
    {"name": "5_SummonCreature", "id": 0x1F54, "hue": None},
    # Circle 6 Scrolls
    {"name": "6_Dispel", "id": 0x1F55, "hue": None},
    {"name": "6_EnergyBolt", "id": 0x1F56, "hue": None},
    {"name": "6_Explosion", "id": 0x1F57, "hue": None},
    {"name": "6_Invisibility", "id": 0x1F58, "hue": None},
    {"name": "6_Mark", "id": 0x1F59, "hue": None},
    {"name": "6_MassCurse", "id": 0x1F5A, "hue": None},
    {"name": "6_ParalyzeField", "id": 0x1F5B, "hue": None},
    {"name": "6_Reveal", "id": 0x1F5C, "hue": None},
    # Circle 7 Scrolls
    {"name": "7_ChainLightning", "id": 0x1F5D, "hue": None},
    {"name": "7_EnergyField", "id": 0x1F5E, "hue": None},
    {"name": "7_Flamestrike", "id": 0x1F5F, "hue": None},
    {"name": "7_GateTravel", "id": 0x1F60, "hue": None},
    {"name": "7_ManaVampire", "id": 0x1F61, "hue": None},
    {"name": "7_MassDispel", "id": 0x1F62, "hue": None},
    {"name": "7_MeteorSwarm", "id": 0x1F63, "hue": None},
    {"name": "7_Polymorph", "id": 0x1F64, "hue": None},
    # Circle 8 Scrolls
    {"name": "8_Earthquake", "id": 0x1F65, "hue": None},
    {"name": "8_EnergyVortex", "id": 0x1F66, "hue": None},
    {"name": "8_Resurrection", "id": 0x1F67, "hue": None},
    {"name": "8_SummonAirElemental", "id": 0x1F68, "hue": None},
    {"name": "8_SummonDaemon", "id": 0x1F69, "hue": None},
    {"name": "8_SummonEarthElemental", "id": 0x1F6A, "hue": None},
    {"name": "8_SummonFireElemental", "id": 0x1F6B, "hue": None},
    {"name": "8_SummonWaterElemental", "id": 0x1F6C, "hue": None},
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

def deposit_magic_scrolls(target_container):
    """Move all magic scrolls from backpack into the target container."""
    total_moved = 0
    for info in MAGIC_SCROLLS:
        moved = deposit_all_matching(info, target_container)
        if moved:
            total_moved += moved
            Misc.Pause(100)
    if total_moved == 0:
        debug_message("No magic scrolls to deposit.", 53)
    else:
        debug_message(f"Total magic scrolls deposited: {total_moved}", 65)

def main():
    debug_message("Starting Home Deposit: Scrolls", 65)

    target_container = pick_target_container()
    if not target_container:
        debug_message("Cannot proceed: No valid target container.", 33)
        return

    debug_message(f"Target container: serial {hex(target_container.Serial)} (ID 0x{target_container.ItemID:04X})", 65)

    if MOVE_MAGIC_SCROLLS:
        deposit_magic_scrolls(target_container)

    debug_message("Home Deposit complete.", 65)

if __name__ == "__main__":
    main()
