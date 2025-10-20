"""
HOME deposit food - a Razor Enhanced Python Script for Ultima Online

Move all food category items from player backpack into a designated home food container.

Usage:
- Configure TARGET_CONTAINER_SERIALS with one or more container serials (most-preferred first).
- Run the script while near your home container so Items.Move succeeds.

HOTKEY::
VERSION::20250908
"""

DEBUG_MODE = False  # Set True to see debug messages
MOVE_FOOD = True
MOVE_NON_EDIBLE = True  # Also deposit non-edible food-like items (ingredients, preparations, decorative foods/drinks)

# Provide one or more serials of valid target containers at home. The script uses the first valid one it finds.
# Example: [0x400ABC12, 0x400DEF34]
# Set to the user's specified food bag/container serial
TARGET_CONTAINER_SERIALS = [0x40F0E8F9]

 # (Hardcoded additional items formerly from JSON are appended below.)

# Category-specific containers (for future flexibility). For now, both point to the same list.
FOOD_TARGET_CONTAINER_SERIALS = TARGET_CONTAINER_SERIALS
NON_EDIBLE_TARGET_CONTAINER_SERIALS = TARGET_CONTAINER_SERIALS

# Priority index to pick when multiple valid containers are found
TARGET_PRIORITY_INDEX = 0

# ==============================
# Food Items (from scripts/ITEM_food_eater.py)

# Food Categories with their properties (flattened below)
FOOD_CATEGORIES = {
    "FRUITS": {
        "items": [
            {"name": "Peach", "id": 0x09D2},
            {"name": "Apple", "id": 0x09D0},
            {"name": "Grapes", "id": 0x09D1},
            {"name": "Pear", "id": 0x0994},
            {"name": "Banana", "id": 0x171F},
            {"name": "Pumpkin", "id": 0x0C6A},
            {"name": "Onion", "id": 0x09EC},
            {"name": "Carrot", "id": 0x0C78},
            {"name": "Squash", "id": 0x0C6C},
        ]
    },
    "BAKED_GOODS": {
        "items": [
            {"name": "Muffins", "id": 0x09EB},
            {"name": "Bread Loaf", "id": 0x103B},
        ]
    },
    "MEATS": {
        "items": [
            {"name": "Cheese", "id": 0x097D},
            {"name": "Sausage", "id": 0x09C0},
            {"name": "Cooked Bird", "id": 0x09B7},
            {"name": "Cut of Ribs", "id": 0x09F2},
            {"name": "Ham", "id": 0x09C9},
            {"name": "Leg of Lamb", "id": 0x160A},
            {"name": "Chicken Leg", "id": 0x1608},
            {"name": "Fish Steak", "id": 0x097A},
            {"name": "Fish Steak 2", "id": 0x097B},
            {"name": "Bacon", "id": 0x097E},
        ]
    },
}

# Flatten categories into a single list of item descriptors like the equipment script
FOOD_ITEMS = [
    {"name": item["name"], "id": item["id"], "hue": None}
    for cat in FOOD_CATEGORIES.values()
    for item in cat["items"]
]

# Append additional discovered food items (hardcoded from data/items_food.json)
# These cover seafoods, lettuces, coconuts, alternate variants, etc.
_ADDITIONAL_FOOD_HARDCODED = [
    {"name": "lobster", "id": 0x44D3, "hue": None},
    {"name": "crab", "id": 0x44D2, "hue": None},
    {"name": "head of lettuce", "id": 0x0C70, "hue": None},
    {"name": "coconut", "id": 0x1726, "hue": None},
    {"name": "slice of bacon", "id": 0x0979, "hue": None},
    {"name": "wheel of cheese", "id": 0x097E, "hue": None},
    {"name": "squash (variant)", "id": 0x0C72, "hue": None},
]

# De-duplicate by (id,hue) before extending
_existing_keys = set((it["id"], it.get("hue", None)) for it in FOOD_ITEMS)
for it in _ADDITIONAL_FOOD_HARDCODED:
    _k = (it["id"], it.get("hue", None))
    if _k not in _existing_keys:
        FOOD_ITEMS.append(it)
        _existing_keys.add(_k)

# ==============================
# Non-Edible Food-like Items (from wiki/gump_crafting_*.wiki.txt)
# Includes: Ingredients, Preparations (unbaked/uncooked), Meals, Magical Foods, decorative foods/drinks
# Only entries with known numeric IDs are included here.

NON_EDIBLE_FOODLIKE_ITEMS = [
    # Ingredients
    {"name": "cake mix", "id": 0x103F, "hue": None},
    {"name": "cookie mix", "id": 0x103F, "hue": None},
    {"name": "dough", "id": 0x103D, "hue": None},
    {"name": "sweet dough", "id": 0x103D, "hue": None},
    {"name": "sack of flour", "id": 0x1039, "hue": None},
    {"name": "Mento Seasoning", "id": 0x0996, "hue": None},
    {"name": "Aunt Pearl's Home-Made Snacks", "id": 0x0990, "hue": None},

    # Preparations (unbaked/uncooked)
    {"name": "unbaked apple pie", "id": 0x1042, "hue": None},
    {"name": "unbaked fruit pie", "id": 0x1042, "hue": None},
    {"name": "unbaked meat pie", "id": 0x1042, "hue": None},
    {"name": "unbaked peach cobbler", "id": 0x1042, "hue": None},
    {"name": "unbaked pumpkin pie", "id": 0x1042, "hue": None},
    {"name": "unbaked quiche", "id": 0x1042, "hue": None},
    {"name": "uncooked cheese pizza", "id": 0x1083, "hue": None},
    {"name": "uncooked sausage pizza", "id": 0x1083, "hue": None},
    {"name": "cut of raw ribs", "id": 0x09F1, "hue": None},
    {"name": "raw chicken leg", "id": 0x1607, "hue": None},

    # Meals (decorative/served items)
    {"name": "roast pig", "id": 0x09BB, "hue": None},
    {"name": "Ham Meal", "id": 0x70B8, "hue": None},
    {"name": "Pear Salad", "id": 0x70B7, "hue": None},
    {"name": "Vegetables Meal", "id": 0x70B1, "hue": None},
    {"name": "Chicken Legs Bowl", "id": 0x70BB, "hue": None},
    {"name": "Coconut Bowl", "id": 0x70C1, "hue": None},
    {"name": "Goby Fish Bowl", "id": 0x70B9, "hue": None},
    {"name": "Bacon and Egg Meal", "id": 0x7486, "hue": None},
    {"name": "Colorful Salad", "id": 0x70B7, "hue": None},
    {"name": "Fruit Pie (meal)", "id": 0x1041, "hue": None},
    {"name": "Lamb Leg Meal", "id": 0x7486, "hue": None},
    {"name": "Lime Pie (meal)", "id": 0x1041, "hue": None},
    {"name": "Pork Meal", "id": 0x7485, "hue": None},
    {"name": "Porridge Meal", "id": 0x70B9, "hue": None},
    {"name": "Salmon Meal", "id": 0x7483, "hue": None},
    {"name": "Spicy Fish Bowl", "id": 0x70B9, "hue": None},
    {"name": "Vegetable Pizza (meal)", "id": 0x1040, "hue": None},

    # Magical Foods (decorative/special)
    {"name": "Banana Pie", "id": 0x1041, "hue": None},
    {"name": "Bowl of Lich Goo", "id": 0x15FB, "hue": None},
    {"name": "Bowl of Marinated Rocks", "id": 0x70C1, "hue": None},
    {"name": "Britannia’s Finest Fruits", "id": 0x0993, "hue": None},
    {"name": "Charcuterie Board", "id": 0x70D1, "hue": None},
    {"name": "Crab Cake (Beetle Food)", "id": 0x1041, "hue": None},
    {"name": "Dragon Meat Feast", "id": 0xB93D, "hue": None},
    {"name": "Farmers Feast", "id": 0x7487, "hue": None},
    {"name": "Juicy Apple Pie", "id": 0x1041, "hue": None},
    {"name": "Lucky Lollipop", "id": 0x468E, "hue": None},
    {"name": "Mermaid Meat Feast", "id": 0x7483, "hue": None},
    {"name": "Nimble Nut Feast", "id": 0x70D6, "hue": None},
    {"name": "Pixie Leg Feast", "id": 0x7486, "hue": None},
    {"name": "Red Velvet Cake", "id": 0x09E9, "hue": None},
]


def debug_message(message, color=67):
    """Send a message if DEBUG_MODE is enabled."""
    if DEBUG_MODE:
        Misc.SendMessage(f"[HomeDepositFood] {message}", color)


def pick_target_container(container_serials=None, priority_index=None):
    """Select a valid target container from TARGET_CONTAINER_SERIALS by priority.
    Returns the container item object, or None if not found/invalid.
    """
    if container_serials is None:
        container_serials = TARGET_CONTAINER_SERIALS
    if priority_index is None:
        priority_index = TARGET_PRIORITY_INDEX

    if not container_serials:
        debug_message("No TARGET_CONTAINER_SERIALS configured. Please set your home food chest serial(s).", 33)
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


def deposit_food(target_container):
    """Move all food items from backpack into the target container."""
    total_moved = 0
    for info in FOOD_ITEMS:
        moved = deposit_all_matching(info, target_container)
        if moved:
            total_moved += moved
            Misc.Pause(100)
    if total_moved == 0:
        debug_message("No food items to deposit.", 53)
    else:
        debug_message(f"Total food items deposited: {total_moved}", 65)


def deposit_non_edible_foodlikes(target_container):
    """Move all non-edible food-like items (ingredients, preparations, meals, magical foods) into the target container."""
    total_moved = 0
    for info in NON_EDIBLE_FOODLIKE_ITEMS:
        moved = deposit_all_matching(info, target_container)
        if moved:
            total_moved += moved
            Misc.Pause(100)
    if total_moved == 0:
        debug_message("No non-edible food-like items to deposit.", 53)
    else:
        debug_message(f"Total non-edible food-like items deposited: {total_moved}", 65)


def main():
    debug_message("Starting Home Deposit: Food", 65)

    # Pick containers per category (currently both point to the same serials)
    target_food_container = pick_target_container(FOOD_TARGET_CONTAINER_SERIALS, TARGET_PRIORITY_INDEX)
    target_non_edible_container = pick_target_container(NON_EDIBLE_TARGET_CONTAINER_SERIALS, TARGET_PRIORITY_INDEX)

    if not target_food_container and not target_non_edible_container:
        debug_message("Cannot proceed: No valid target container.", 33)
        return

    # Announce picked containers (they may be the same)
    if target_food_container:
        debug_message(
            f"Food container: serial {hex(target_food_container.Serial)} (ID 0x{target_food_container.ItemID:04X})",
            65,
        )
    if target_non_edible_container and (not target_food_container or target_non_edible_container.Serial != target_food_container.Serial):
        debug_message(
            f"Non-edible container: serial {hex(target_non_edible_container.Serial)} (ID 0x{target_non_edible_container.ItemID:04X})",
            65,
        )

    if MOVE_FOOD and target_food_container:
        deposit_food(target_food_container)

    if MOVE_NON_EDIBLE and target_non_edible_container:
        deposit_non_edible_foodlikes(target_non_edible_container)

    debug_message("Home Deposit (Food) complete.", 65)


if __name__ == "__main__":
    main()