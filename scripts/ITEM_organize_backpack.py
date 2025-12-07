"""ITEM Organize Backpack - a Razor Enhanced Python Script for Ultima Online

Organizes items in the backpack with specific positioning and directional spacing control:
- Reagents: Lower left, left-to-right sorting, combines reagents
- Potions: Above reagents, left-to-right sorting with offset spacing
- Gems: Second Lowest middle, horizontal sorting left-to-right with offset spacing
- Books: Top left, horizontal sorting left-to-right with offset spacing
- Trap pouches: Bottom right, vertical spacing offset, NO stacking
- Runes: Top right, vertical sorting stop-to-bottom with offset stacking
- Tools: Top right middle, horizontal right-to-left with offset stacking

These positions are tuned for a "150" container size without scaling items sizes 
the default is "100" container size so you may want to adjust the x and y values for your settings

Uses server sync method for reliable timing with fallback delays.
Re-fetches items after moves to verify success and prevent errors.

HOTKEY:: U
VERSION::20251024
"""
ORGANIZE_UNKNOWN_ITEMS = True
ORGANIZE_REAGENTS = True
ORGANIZE_POTIONS = True
ORGANIZE_GEMS = True
ORGANIZE_TOOLS = True
ORGANIZE_BOOKS = True

DEBUG_MODE = False  # Set to True to enable debug/info messages
SPACING_OFFSET = 7  # Pixels to offset spacing
MAX_STACK_SIZE = 999  # Maximum items to stack in one location

# Server sync configuration
USE_SERVER_SYNC = True  # Use server sync method for delays (recommended)
FALLBACK_DELAY = 600  # Fallback delay if server sync fails (in milliseconds)

# DELAYS (milliseconds) - used when server sync is disabled
PAUSE_SPELLBOOK_MOVE = 200 # Spellbook placement
PAUSE_SPELLBOOK_ROW_SETTLE = 50
PAUSE_UNKNOWN_ITEM_MOVE = 200 # Unknown items placement grid
PAUSE_GROUP_ITEM_MOVE = 200 # General group item movement (non-spellbook)
# Reagent combining flow (move to character, settle, move back to backpack)
# this is just too slow , we disabled
PAUSE_REAGENTS_MOVE_TO_CHAR = 200
PAUSE_REAGENTS_SETTLE_AFTER_CHAR = 1200
PAUSE_REAGENTS_MOVE_TO_BACKPACK = 200

# Item Categories with properties
ITEM_GROUPS = {
    "REAGENTS": { # start 40 offset x = +15
        "items": [
            {"name": "Black Pearl", "id": 0x0F7A, "x": 40, "y": 300},
            {"name": "Blood Moss", "id": 0x0F7B, "x": 55, "y": 300},
            {"name": "Garlic", "id": 0x0F84, "x": 70, "y": 300},
            {"name": "Ginseng", "id": 0x0F85, "x": 85, "y": 300},
            {"name": "Mandrake Root", "id": 0x0F86, "x": 100, "y": 300},
            {"name": "Nightshade", "id": 0x0F88, "x": 115, "y": 300},
            {"name": "Spider's Silk", "id": 0x0F8D, "x": 130, "y": 300},
            {"name": "Sulfurous Ash", "id": 0x0F8C, "x": 145, "y": 300},
            # Pagan Reagents
            {"name": "Bat Wing", "id": 0x0F78, "x": 160, "y": 300},
            {"name": "Grave Dust", "id": 0x0F8F, "x": 175, "y": 300},
            {"name": "Daemon Blood", "id": 0x0F7D, "x": 190, "y": 300},
            {"name": "Nox Crystal", "id": 0x0F8E, "x": 215, "y": 300},
            {"name": "Pig Iron", "id": 0x0F8A, "x": 230, "y": 300}
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
    "GEMS": { # start 48 offset x = +12 
        "items": [
            {"name": "Ruby",          "id": 0x0F13, "x": 48,  "y": 120},  # Red
            {"name": "Amber",         "id": 0x0F25, "x": 60,  "y": 120},  # Orange
            {"name": "Citrine",       "id": 0x0F15, "x": 72,  "y": 120},  # Yellow
            {"name": "Tourmaline",    "id": 0x0F18, "x": 84,  "y": 120},  # GreenPink
            {"name": "Diamond",       "id": 0x0F26, "x": 96,  "y": 120},  # White/Clear
            {"name": "Emerald",       "id": 0x0F10, "x": 108, "y": 120},  # Green
            {"name": "Sapphire",      "id": 0x0F11, "x": 120, "y": 120},  # Blue
            {"name": "Star Sapphire", "id": 0x0F0F, "x": 132, "y": 120},  # Blue
            {"name": "Amethyst",      "id": 0x0F16, "x": 144, "y": 120},  # Violet
            # No Drop Gems Alternate IDs
            {"name": "sapphireA",     "id": 0x0F19, "x": 156, "y": 120},  # Blue  extras in world
            {"name": "saphireB",      "id": 0x0F21, "x": 168, "y": 120},  # Blue extras in world
            {"name": "TourmalineB",   "id": 0x0F2D, "x": 180, "y": 120},  # GreenPink extras in world
        ],
        "move_to_char": False
    },
    "BOOKS": {
        "items": [
            {"name": "Spellbook", "id": 0x0EFA, "x": 45, "y": 65}
        ],
        "move_to_char": False,
        "is_spellbook": True  # Special flag for spellbook handling
    },
    "TRAP_POUCHES": {
        "items": [
            {"name": "Trap Pouch", "id": 0x0E79, "x": 300, "y": 120}
        ],
        "move_to_char": False
    },
    "RUNES": {
        "items": [
            {"name": "Recall Rune", "id": 0x1F14, "x": 300, "y": 80},
        ],
        "move_to_char": False
    },
    "BANDAGES": {
        "items": [
            {"name": "Bandages", "id": 0x0E21, "x": 300, "y": 75}
        ],
        "move_to_char": False
    },
    "TOOLS": { # start 125 offset x = +10
        "items": [
            {"name": "Sewing Kit", "id": 0x0F9D, "x": 125, "y": 20},
            {"name": "Lockpicks", "id": 0x14FC, "x": 135, "y": 20},
            {"name": "Backpack", "id": 0x0E75, "x": 145, "y": 20},
            {"name": "Bag", "id": 0x0E76, "x": 155, "y": 20},
            {"name": "Pouch", "id": 0x0E79, "x": 165, "y": 20},
            {"name": "Tinker Tools", "id": 0x1EB8, "x": 175, "y": 20},
            {"name": "Scissors", "id": 0x0F9F, "x": 185, "y": 20},
            {"name": "Mortar and Pestle", "id": 0x0E9B, "x": 195, "y": 20},
            {"name": "Smith's Hammer", "id": 0x13E3, "x": 205, "y": 20},
            {"name": "Tongs", "id": 0x0FBB, "x": 215, "y": 20},
            {"name": "Saw", "id": 0x1034, "x": 225, "y": 20},
            {"name": "Plane", "id": 0x102C, "x": 235, "y": 20},
            {"name": "Draw Knife", "id": 0x10E4, "x": 245, "y": 20},
            {"name": "Froe", "id": 0x10E5, "x": 255, "y": 20},
            {"name": "Scorp", "id": 0x10E7, "x": 265, "y": 20},
            {"name": "Inshave", "id": 0x10E6, "x": 275, "y": 20},
            {"name": "Pickaxe", "id": 0x0E86, "x": 285, "y": 20},
            {"name": "Shovel", "id": 0x0F39, "x": 295, "y": 20},
            {"name": "Hatchet", "id": 0x0F43, "x": 305, "y": 20},
            {"name": "Fishing Pole", "id": 0x0DC0, "x": 315, "y": 20}
        ],
        "move_to_char": False
    }
}

# Controls the unknown item box placement and size
UNKNOWN_BOX = {
    'center_x': 80,
    'center_y': 80,
    'width': 65,
    'height': 35,
}
#//============================================================

def debug_message(message, color=68):
    """Send a message if DEBUG_MODE is enabled"""
    if DEBUG_MODE:
        Misc.SendMessage(f"[BackpackOrg] {message}", color)

def server_sync_delay():
    """Synchronize with server using backpack label check.
    This provides a natural server-synced delay that matches server response time.
    More reliable than arbitrary Misc.Pause() delays.
    Falls back to FALLBACK_DELAY if GetLabel fails.
    """
    try:
        # GetLabel forces client to wait for server response
        # This naturally syncs with server tick rate
        Items.GetLabel(Player.Backpack.Serial)
        debug_message("Server sync successful", 68)
    except Exception as e:
        # Fallback to configured delay if GetLabel fails
        debug_message(f"Server sync failed ({e}), using fallback delay: {FALLBACK_DELAY}ms", 53)
        Misc.Pause(FALLBACK_DELAY)

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
    """Place spellbooks in a clean grid (rows/columns) to avoid diagonal stacking.
    - Sorted by hue (then serial) for stable placement
    """
    if not items:
        return

    # Configuration
    columns = 8
    h_spacing = 8
    v_spacing = 10

    # Stable order: by hue, then by serial
    def hue_key(itm):
        return (itm.Hue if itm.Hue > 0 else 0, itm.Serial)

    sorted_items = sorted(items, key=hue_key)

    for idx, book in enumerate(sorted_items):
        try:
            col = idx % columns
            row = idx // columns
            x = base_x + col * h_spacing
            y = base_y + row * v_spacing

            # Re-fetch by serial to avoid stale references after previous moves
            fresh = Items.FindBySerial(book.Serial)
            if not fresh:
                debug_message(f"Spellbook not found by serial {hex(book.Serial)}; skipping.", 33)
                continue

            # Use amount 0 (all) for non-stackables; keep target as backpack at specific coords
            Items.Move(fresh.Serial, Player.Backpack.Serial, 0, x, y)
            
            # Use server sync or fallback delay
            if USE_SERVER_SYNC:
                server_sync_delay()
            else:
                Misc.Pause(PAUSE_SPELLBOOK_MOVE)
            
            # Verify item was moved successfully
            moved_item = Items.FindBySerial(fresh.Serial)
            if moved_item and moved_item.Container != Player.Backpack.Serial:
                debug_message(f"Warning: Spellbook {hex(fresh.Serial)} may not have moved correctly", 33)

            # Small extra pause after finishing each row to let container settle
            if col == columns - 1:
                if USE_SERVER_SYNC:
                    server_sync_delay()
                else:
                    Misc.Pause(PAUSE_SPELLBOOK_ROW_SETTLE)
        except Exception as e:
            debug_message(f"Error placing spellbook idx={idx} serial={hex(book.Serial)}: {e}", 33)
    debug_message(f"Placed {len(sorted_items)} spellbooks in grid {columns} per row.", 65)

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
            if USE_SERVER_SYNC:
                server_sync_delay()
            else:
                Misc.Pause(PAUSE_REAGENTS_MOVE_TO_CHAR)
        
        # Then move them to their designated spot in backpack
        if USE_SERVER_SYNC:
            server_sync_delay()
        else:
            Misc.Pause(PAUSE_REAGENTS_SETTLE_AFTER_CHAR)  # Extra pause 
        items_on_char = find_items_by_id(items[0].ItemID)
        if items_on_char:
            stack_count = 0
            current_x = target_x
            current_y = target_y
            
            for item in items_on_char:
                Items.Move(item.Serial, Player.Backpack.Serial, item.Amount, current_x, current_y)
                if USE_SERVER_SYNC:
                    server_sync_delay()
                else:
                    Misc.Pause(PAUSE_REAGENTS_MOVE_TO_BACKPACK)

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
        
        try:
            # Re-fetch item to ensure it still exists
            item_obj = Items.FindBySerial(item.Serial)
            if not item_obj:
                continue
                
            Items.Move(item_obj.Serial, Player.Backpack.Serial, item_obj.Amount, x, y)
            
            # Use server sync or fallback delay
            if USE_SERVER_SYNC:
                server_sync_delay()
            else:
                Misc.Pause(PAUSE_UNKNOWN_ITEM_MOVE)
        except Exception as e:
            debug_message(f"Error moving unknown item {item.Serial:X}: {e}", 33)
    debug_message(f"Finished moving unknown items to center box.", 65)

def organize_backpack():
    """Organize items in backpack by type, honoring group enable globals."""
    debug_message("Starting backpack organization...", 65)

    group_enabled = {
        "REAGENTS": ORGANIZE_REAGENTS,
        "POTIONS": ORGANIZE_POTIONS,
        "GEMS": ORGANIZE_GEMS,
        "TOOLS": ORGANIZE_TOOLS,
    }

    for group_name, group_config in ITEM_GROUPS.items():
        # Only process group if enabled or not explicitly toggled
        if group_name in group_enabled and not group_enabled[group_name]:
            debug_message(f"Skipping {group_name} organization (disabled)", 65)
            continue
        debug_message(f"Processing {group_name}...", 65)
        total_items = 0

        # Special-case: handle spellbooks with dedicated grid function
        if group_config.get("is_spellbook", False):
            # Collect all spellbooks using the group's item definitions (usually 0x0EFA)
            base_x = group_config["items"][0]["x"]
            base_y = group_config["items"][0]["y"]
            spellbooks = []
            for item_def in group_config["items"]:
                spellbooks.extend(find_items_by_id(item_def["id"], sort_by_hue=True))
            if spellbooks:
                total_items = len(spellbooks)
                debug_message(f"Found {total_items} Spellbooks. Placing in rows of 8...", 65)
                move_spellbooks(spellbooks, base_x, base_y)
            else:
                debug_message("No Spellbooks found.", 65)
        else:
            # Default handling for non-spellbook groups
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
                        try:
                            # Re-fetch item to ensure it still exists
                            item_obj = Items.FindBySerial(item.Serial)
                            if not item_obj:
                                debug_message(f"Item {item.Serial:X} not found, skipping", 33)
                                continue
                                
                            Items.Move(item_obj.Serial, Player.Backpack.Serial, item_obj.Amount, current_x, current_y)
                            
                            # Use server sync or fallback delay
                            if USE_SERVER_SYNC:
                                server_sync_delay()
                            else:
                                Misc.Pause(PAUSE_GROUP_ITEM_MOVE)
                            
                            # Verify item was moved
                            moved_item = Items.FindBySerial(item_obj.Serial)
                            if moved_item and moved_item.Container != Player.Backpack.Serial:
                                debug_message(f"Warning: Item {item_obj.Serial:X} may not have moved correctly", 33)
                                
                        except Exception as e:
                            debug_message(f"Error moving item {item.Serial:X}: {e}", 33)
                            
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
