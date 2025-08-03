"""
ITEM Organize Backpack - a Razor Enhanced Python Script for Ultima Online

Organizes items in the backpack with specific positioning and directional spacing control:
- Reagents: Lower left, left-to-right sorting, combines reagents
- Potions: Above reagents, left-to-right sorting with offset spacing
- Gems: Upper middle, vertical sorting top-to-bottom with offset spacing
- Books: Top left, horizontal sorting left-to-right with offset spacing
- Trap pouches: Bottom right, vertical spacing offset, NO stacking
- Runes: Top right, vertical sorting top-to-bottom with offset stacking
- Bandages: Top right middle, horizontal right-to-left with offset stacking

These positions are tuned for a "150" container size without scaling items sizes 
the default is "100" container size so you may want to adjust the x and y values for your settings

TODO:
- move unknown items to the center , optional 
- offset the pouches vertically

VERSION::20250722
"""
ORGANIZE_UNKNOWN_ITEMS = True
ORGANIZE_REAGENTS = True
ORGANIZE_POTIONS = True
ORGANIZE_GEMS = True
ORGANIZE_TOOLS = True

DEBUG_MODE = True  # Set to True to enable debug/info messages
SPACING_OFFSET = 7  # Pixels to offset spacing
MAX_STACK_SIZE = 999  # Maximum items to stack in one location

# Item Categories with properties
ITEM_GROUPS = {
    "REAGENTS": {
        "items": [
            {"name": "Black Pearl", "id": 0x0F7A, "x": 60, "y": 300},
            {"name": "Blood Moss", "id": 0x0F7B, "x": 70, "y": 300},
            {"name": "Garlic", "id": 0x0F84, "x": 80, "y": 300},
            {"name": "Ginseng", "id": 0x0F85, "x": 90, "y": 300},
            {"name": "Mandrake Root", "id": 0x0F86, "x": 100, "y": 300},
            {"name": "Nightshade", "id": 0x0F88, "x": 110, "y": 300},
            {"name": "Spider's Silk", "id": 0x0F8D, "x": 120, "y": 300},
            {"name": "Sulfurous Ash", "id": 0x0F8C, "x": 130, "y": 300},
            # Pagan Reagents
            {"name": "Bat Wing", "id": 0x0F78, "x": 160, "y": 300},
            {"name": "Grave Dust", "id": 0x0F8F, "x": 180, "y": 300},
            {"name": "Daemon Blood", "id": 0x0F7D, "x": 200, "y": 300},
            {"name": "Nox Crystal", "id": 0x0F8E, "x": 220, "y": 300},
            {"name": "Pig Iron", "id": 0x0F8A, "x": 240, "y": 300}
        ],
        "move_to_char": True  # Special flag for reagents to combine them into one stack
    },
    "POTIONS": {
        "items": [
            {"name": "Heal", "id": 0x0F0C, "x": 0, "y": 100},
            {"name": "Cure", "id": 0x0F07, "x": 55, "y": 100},
            {"name": "Total Refresh", "id": 0x0F0B, "x": 65, "y": 100},
            {"name": "Strength", "id": 0x0F09, "x": 75, "y": 100},
            {"name": "Mana Potion", "id": 0x0F0D, "x": 85, "y": 100},
            
        ],
        "move_to_char": False
    },
    "GEMS": {
        "items": [
            {"name": "Emerald",       "id": 0x0F10, "x": 60,   "y": 115},
            {"name": "sapphireA",     "id": 0x0F11, "x": 70,  "y": 115},
            {"name": "Ruby",          "id": 0x0F13, "x": 80,  "y": 115},
            {"name": "Citrine",       "id": 0x0F15, "x": 90,  "y": 115},
            {"name": "Amethyst",      "id": 0x0F16, "x": 100,  "y": 115},
            {"name": "Sapphire",      "id": 0x0F19, "x": 110,  "y": 115},
            {"name": "Star Sapphire", "id": 0x0F21, "x": 120,  "y": 115},
            {"name": "Amber",         "id": 0x0F25, "x": 130,  "y": 115},
            {"name": "Diamond",       "id": 0x0F26, "x": 140,  "y": 115},
            {"name": "Tourmaline",    "id": 0x0F2D, "x": 150,  "y": 115},
            {"name": "TourmalineB",   "id": 0x0F18, "x": 160, "y": 115},
            {"name": "saphireB",      "id": 0x0F0F, "x": 170, "y": 115}
        ],
        "move_to_char": False
    },
    "BOOKS": {
        "items": [
            {"name": "Spellbook", "id": 0x0EFA, "x": 20, "y": 20}
        ],
        "move_to_char": False,
        "is_spellbook": True  # Special flag for spellbook handling
    },
    "TRAP_POUCHES": {
        "items": [
            {"name": "Trap Pouch", "id": 0x0E79, "x": 300, "y": 200}
        ],
        "move_to_char": False
    },
    "RUNES": {
        "items": [
            {"name": "Recall Rune", "id": 0x1F14, "x": 300, "y": 0},
            {"name": "Gate Rune", "id": 0x1F14, "x": 300, "y": 50}  # Same ID, different hue
        ],
        "move_to_char": False
    },
    "BANDAGES": {
        "items": [
            {"name": "Bandages", "id": 0x0E21, "x": 300, "y": 75}
        ],
        "move_to_char": False
    },
    "TOOLS": {
        "items": [
            {"name": "Sewing Kit", "id": 0x0F9D, "x": 200, "y": 20},
            {"name": "Lockpicks", "id": 0x14FC, "x": 210, "y": 20},
            {"name": "Backpack", "id": 0x0E75, "x": 220, "y": 20},
            {"name": "Bag", "id": 0x0E76, "x": 230, "y": 20},
            {"name": "Pouch", "id": 0x0E79, "x": 240, "y": 20},
            {"name": "Tinker Tools", "id": 0x1EB8, "x": 250, "y": 20},
            {"name": "Scissors", "id": 0x0F9F, "x": 260, "y": 20},
            {"name": "Mortar and Pestle", "id": 0x0E9B, "x": 270, "y": 20},
            {"name": "Smith's Hammer", "id": 0x13E3, "x": 280, "y": 20},
            {"name": "Tongs", "id": 0x0FBB, "x": 290, "y": 20},
            {"name": "Saw", "id": 0x1034, "x": 200, "y": 30},
            {"name": "Plane", "id": 0x102C, "x": 210, "y": 30},
            {"name": "Draw Knife", "id": 0x10E4, "x": 220, "y": 30},
            {"name": "Froe", "id": 0x10E5, "x": 230, "y": 30},
            {"name": "Scorp", "id": 0x10E7, "x": 240, "y": 30},
            {"name": "Inshave", "id": 0x10E6, "x": 250, "y": 30},
            {"name": "Pickaxe", "id": 0x0E86, "x": 260, "y": 30},
            {"name": "Shovel", "id": 0x0F39, "x": 270, "y": 30},
            {"name": "Hatchet", "id": 0x0F43, "x": 280, "y": 30},
            {"name": "Fishing Pole", "id": 0x0DC0, "x": 290, "y": 30}
        ],
        "move_to_char": False
    }
}

# Controls the unknown item box placement and size
UNKNOWN_BOX = {
    'center_x': 65,
    'center_y': 80,
    'width': 70,
    'height': 45,
}
#//============================================================

def debug_message(message, color=68):
    """Send a message if DEBUG_MODE is enabled"""
    if DEBUG_MODE:
        Misc.SendMessage(f"[BackpackOrg] {message}", color)

def find_items_by_id(item_id, sort_by_hue=False):
    """Find all items with matching ID in backpack."""
    items = []
    
    # Search through all items in backpack
    for item in Player.Backpack.Contains:
        if item.ItemID == item_id:
            items.append(item)
    
    if sort_by_hue:
        # Sort items by hue, handling default hue (0 or -1) specially
        items.sort(key=lambda x: x.Hue if x.Hue > 0 else 9999)
    
    return items

def move_spellbooks(items, base_x, base_y):
    """Special handling for spellbooks - organize by hue."""
    if not items:
        return
        
    # Group spellbooks by hue
    hue_groups = {}
    for item in items:
        hue = item.Hue if item.Hue > 0 else 0
        if hue not in hue_groups:
            hue_groups[hue] = []
        hue_groups[hue].append(item)
    
    # Sort hues for consistent ordering
    sorted_hues = sorted(hue_groups.keys())
    
    # Position variables
    current_x = base_x
    current_y = base_y
    books_per_row = 5
    book_spacing = 5
    row_spacing = 10
    
    # Place books by hue groups
    for hue in sorted_hues:
        books = hue_groups[hue]
        for i, book in enumerate(books):
            # Calculate position
            x = current_x + (i % books_per_row) * book_spacing
            y = current_y + (i // books_per_row) * row_spacing
            
            # Move the book
            Items.Move(book.Serial, Player.Backpack.Serial, book.Amount, x, y)
            Misc.Pause(600)
            
            if i > 0 and i % books_per_row == books_per_row - 1:
                debug_message(f"Placed {i+1} spellbooks of hue {hue}", 65)
        
        # Move to next group position
        current_x += book_spacing * books_per_row + 10
        if current_x > base_x + book_spacing * books_per_row * 3:
            current_x = base_x
            current_y += row_spacing * 3

def move_items(items, target_x, target_y, group_config):
    """Move items to target location with appropriate handling."""
    if not items:
        return
    
    # Special handling for spellbooks
    if group_config.get("is_spellbook", False):
        move_spellbooks(items, target_x, target_y)
        return
    
    if group_config.get("move_to_char", False):
        # First move reagents to character
        for item in items:
            Items.Move(item.Serial, Player.Serial, item.Amount, 0, 0)
            Misc.Pause(600)
        
        # Then move them to their designated spot in backpack
        Misc.Pause(1200)  # Extra pause to ensure items are on character
        items_on_char = find_items_by_id(items[0].ItemID)
        if items_on_char:
            stack_count = 0
            current_x = target_x
            current_y = target_y
            
            for item in items_on_char:
                Items.Move(item.Serial, Player.Backpack.Serial, item.Amount, current_x, current_y)
                Misc.Pause(600)
                
                stack_count += 1
                if stack_count >= MAX_STACK_SIZE:
                    # Start a new stack
                    current_x += SPACING_OFFSET * MAX_STACK_SIZE
                    stack_count = 0
                else:
                    # Offset within current stack
                    current_x += SPACING_OFFSET
                    current_y += SPACING_OFFSET
    else:
        # Regular item stacking
        stack_count = 0
        current_x = target_x
        current_y = target_y
        
        for item in items:
            Items.Move(item.Serial, Player.Backpack.Serial, item.Amount, current_x, current_y)
            Misc.Pause(600)
            
            stack_count += 1
            if stack_count >= MAX_STACK_SIZE:
                # Start a new stack
                current_x += SPACING_OFFSET * MAX_STACK_SIZE
                stack_count = 0
            else:
                # Offset within current stack
                current_x += SPACING_OFFSET
                current_y += SPACING_OFFSET

def get_known_item_ids():
    """Return a set of all known item IDs from ITEM_GROUPS."""
    ids = set()
    for group in ITEM_GROUPS.values():
        for item_def in group["items"]:
            ids.add(item_def["id"])
    return ids


def move_unknown_items_to_center_box():
    """Move all items not in any group to a center box, spreading them evenly to fill the box shape."""
    center_x = UNKNOWN_BOX['center_x']
    center_y = UNKNOWN_BOX['center_y']
    box_width = UNKNOWN_BOX['width']
    box_height = UNKNOWN_BOX['height']
    known_ids = get_known_item_ids()
    unknown_items = [item for item in Player.Backpack.Contains if item.ItemID not in known_ids]
    n = len(unknown_items)
    if not unknown_items:
        debug_message("No unknown items to move to center box.", 65)
        return

    # Calculate best-fit grid (cols x rows) for n items in box
    max_cols = max(1, int(box_width // SPACING_OFFSET))
    max_rows = max(1, int(box_height // SPACING_OFFSET))
    # Try to make the grid as square as possible, but fit in the box
    best_cols = min(max_cols, int((n * box_width / box_height) ** 0.5 + 0.5))
    best_cols = max(1, min(max_cols, best_cols))
    best_rows = max(1, min(max_rows, (n + best_cols - 1) // best_cols))
    # If too many rows, clamp cols/rows
    if best_rows > max_rows:
        best_rows = max_rows
        best_cols = max(1, (n + best_rows - 1) // best_rows)
        best_cols = min(best_cols, max_cols)

    debug_message(f"Moving {n} unknown items in a {best_cols}x{best_rows} grid in center box...", 65)
    for idx, item in enumerate(unknown_items):
        row = idx // best_cols
        col = idx % best_cols
        x = center_x + col * (box_width // max(1, best_cols - 1)) if best_cols > 1 else center_x
        y = center_y + row * (box_height // max(1, best_rows - 1)) if best_rows > 1 else center_y
        Items.Move(item.Serial, Player.Backpack.Serial, item.Amount, x, y)
        Misc.Pause(600)
    debug_message(f"Finished moving unknown items to center box.", 65)

def organize_backpack():
    """Organize items in backpack by type, honoring group enable globals."""
    debug_message("Starting backpack organization...", 65)

    group_enabled = {
        "REAGENTS": ORGANIZE_REAGENTS,
        "POTIONS": ORGANIZE_POTIONS,
        "GEMS": ORGANIZE_GEMS,
        "TOOLS": ORGANIZE_TOOLS,
        # Add more group toggles here if needed
    }

    for group_name, group_config in ITEM_GROUPS.items():
        # Only process group if enabled or not explicitly toggled
        if group_name in group_enabled and not group_enabled[group_name]:
            debug_message(f"Skipping {group_name} organization (disabled)", 65)
            continue
        debug_message(f"Processing {group_name}...", 65)
        total_items = 0

        for item_def in group_config["items"]:
            items = find_items_by_id(item_def["id"], sort_by_hue=True)
            if items:
                total_items += len(items)
                debug_message(f"Found {len(items)} {item_def['name']}...", 65)
                # Each type gets its own stack at its own x/y
                stack_count = 0
                current_x = item_def["x"]
                current_y = item_def["y"]
                for item in items:
                    Items.Move(item.Serial, Player.Backpack.Serial, item.Amount, current_x, current_y)
                    Misc.Pause(600)
                    stack_count += 1
                    if stack_count >= MAX_STACK_SIZE:
                        current_x += SPACING_OFFSET * MAX_STACK_SIZE
                        stack_count = 0
                    else:
                        current_x += SPACING_OFFSET
                        current_y += SPACING_OFFSET

        if total_items > 0:
            debug_message(f"Finished {group_name}: {total_items} items organized", 65)
        else:
            debug_message(f"No {group_name} found to organize", 65)

    debug_message("Backpack organization complete!", 65)
    if ORGANIZE_UNKNOWN_ITEMS:
        move_unknown_items_to_center_box()

def main():
    organize_backpack()

if __name__ == "__main__":
    main()
