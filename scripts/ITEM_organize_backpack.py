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

VERSION::20250621
"""

import time
from System.Collections.Generic import List
from System import Int32

# Global
DEBUG_MODE = False  # Set to True to enable debug/info messages
SPACING_OFFSET = 5  # Pixels to offset spacing
MAX_STACK_SIZE = 55  # Maximum items to stack in one location

# Item Categories with their properties
ITEM_GROUPS = {
    "REAGENTS": {
        "items": [
            {"name": "Black Pearl", "id": 0x0F7A, "x": 0, "y": 300},
            {"name": "Blood Moss", "id": 0x0F7B, "x": 20, "y": 300},
            {"name": "Garlic", "id": 0x0F84, "x": 40, "y": 300},
            {"name": "Ginseng", "id": 0x0F85, "x": 60, "y": 300},
            {"name": "Mandrake Root", "id": 0x0F86, "x": 80, "y": 300},
            {"name": "Nightshade", "id": 0x0F88, "x": 100, "y": 300},
            {"name": "Spider's Silk", "id": 0x0F8D, "x": 120, "y": 300},
            {"name": "Sulfurous Ash", "id": 0x0F8C, "x": 140, "y": 300},
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
            {"name": "Heal", "id": 0x0F0C, "x": 40, "y": 100},
            {"name": "Cure", "id": 0x0F07, "x": 55, "y": 100},
            {"name": "Total Refresh", "id": 0x0F0B, "x": 70, "y": 100},
            {"name": "Strength", "id": 0x0F09, "x": 85, "y": 100}
        ],
        "move_to_char": False
    },
    "GEMS": {
        "items": [
            {"name": "Star Sapphire", "id": 0x0F0F, "x": 0, "y": 115},
            {"name": "Ruby", "id": 0x0F13, "x": 20, "y": 115},
            {"name": "Diamond", "id": 0x0F26, "x": 40, "y": 115},
            {"name": "Emerald", "id": 0x0F10, "x": 60, "y": 115},
            {"name": "Sapphire", "id": 0x0F11, "x": 80, "y": 115},
            {"name": "Amethyst", "id": 0x0F16, "x": 100, "y": 115}
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
            {"name": "Trap Pouch", "id": 0x0E79, "x": 300, "y": 300}
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
    }
}

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

def organize_backpack():
    """Organize items in backpack by type."""
    debug_message("Starting backpack organization...", 65)
    
    for group_name, group_config in ITEM_GROUPS.items():
        debug_message(f"Processing {group_name}...", 65)
        total_items = 0
        
        for item_def in group_config["items"]:
            items = find_items_by_id(item_def["id"], sort_by_hue=True)
            if items:
                total_items += len(items)
                debug_message(f"Found {len(items)} {item_def['name']}...", 65)
                move_items(items, item_def["x"], item_def["y"], group_config)
                
        if total_items > 0:
            debug_message(f"Finished {group_name}: {total_items} items organized", 65)
        else:
            debug_message(f"No {group_name} found to organize", 65)
    
    debug_message("Backpack organization complete!", 65)

def main():
    organize_backpack()

if __name__ == "__main__":
    main()
