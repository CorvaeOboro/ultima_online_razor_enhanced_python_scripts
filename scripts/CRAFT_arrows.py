"""
CRAFT arrows - a Razor Enhanced Python Script for Ultima Online

Use Bowcraft Fletching Crafting to make arrows from available resources
Logs > Shafts  ||  Shafts + Feather > Arrows

VERSION::20250917
"""

DEBUG_MODE = False
MAKE_BOLTS = False # TODO: implement bolts buttons 

# Fletching tool and gump
FLETCHING_TOOL_ID = 0x1022           # Fletching tool
FLETCHING_TOOL_COLOR = -1
FLETCHING_GUMP_ID = 0x38920ABD       

# Resource item IDs 
LOG_ID = 0x1BDD                      # Logs
BOARD_ID = 0x1BD7                    # Boards
SHAFT_ID = 0x1BD4                    # Arrow Shafts
FEATHER_ID = 0x1BD1                  # Feathers
ARROW_ID = 0x0F3F                    # Arrows

# Button IDs 
# 1) Select Materials category -> click Make Shafts
# 2) Select Ammunition category -> click Make Arrows
BUTTONS = {
    'category_materials': 8,    # Materials category 
    'make_shafts': 9,            # Make Shafts button (under Materials)
    'category_ammunition': 15,   # Ammunition category 
    'make_arrows': 2             # Make Arrows button (under Ammunition)
}

# Delays (ms)
DELAY_OPEN_PAUSE_MS = 800           # After using tool before checking HasGump
DELAY_CATEGORY_CLICK_MS = 600       # After clicking category before item
DELAY_AFTER_CRAFT_MS = 1500         # After clicking item (craft), match bowcraft's 1500ms
DELAY_BETWEEN_CLICKS_MS = 150       # Extra small gap in loops

#//=====================  Helpers  =====================

def debug_message(message, hue=68):
    if not DEBUG_MODE:
        return
    try:
        Misc.SendMessage(f"[CRAFT_arrows] {str(message)}", hue)
    except Exception:
        pass

def find_in_backpack(item_id, color=-1):
    try:
        return Items.FindByID(item_id, color, Player.Backpack.Serial)
    except Exception:
        return None

def get_amount(item_id, color=-1):
    total = 0
    try:
        found = Items.FindByID(item_id, color, Player.Backpack.Serial)
        if not found:
            return 0
        if isinstance(found, list):
            for itm in found:
                total += max(1, int(getattr(itm, 'Amount', 1)))
        else:
            total += max(1, int(getattr(found, 'Amount', 1)))
    except Exception:
        return 0
    return total

def get_amount_regular(item_id):
    """Count only regular-hue (0) stacks for the given item_id."""
    return get_amount(item_id, 0)

def open_fletching_gump():
    """Open the fletching gump (bowcraft style) and verify it's present."""
    tool = find_in_backpack(FLETCHING_TOOL_ID, FLETCHING_TOOL_COLOR)
    if not tool:
        debug_message("No fletching tool found in backpack!", 33)
        return False
    Items.UseItem(tool)
    Misc.Pause(DELAY_OPEN_PAUSE_MS)
    if not Gumps.HasGump(FLETCHING_GUMP_ID):
        debug_message("Fletching gump did not appear!", 33)
        return False
    return True

def ensure_gump_open():
    if not Gumps.HasGump(FLETCHING_GUMP_ID):
        return open_fletching_gump()
    return True

def craft_once(category_button, item_button):
    """Click the category once then the make button once """
    if not ensure_gump_open():
        return False
    try:
        debug_message(f"Click category button {category_button}")
        Gumps.SendAction(FLETCHING_GUMP_ID, int(category_button))
        Misc.Pause(DELAY_CATEGORY_CLICK_MS)
        debug_message(f"Click item button {item_button}")
        Gumps.SendAction(FLETCHING_GUMP_ID, int(item_button))
        Misc.Pause(DELAY_AFTER_CRAFT_MS)
        return True
    except Exception as e:
        debug_message(f"craft_once failed: {e}", 33)
        return False

#//=====================  Main workflow  =====================

def compute_shafts_needed(feathers_count, shafts_count):
    # Each arrow requires 1 feather + 1 shaft
    if feathers_count <= 0:
        return 0
    if shafts_count >= feathers_count:
        return 0
    return max(0, feathers_count - shafts_count)

def compute_max_shafts_craftable():
    # Only count regular (hue 0) logs/boards. Assume 1 resource -> 1 shaft.
    return get_amount_regular(BOARD_ID) + get_amount_regular(LOG_ID)

def run_arrow_crafting():
    # Count resources
    feathers = get_amount(FEATHER_ID)
    shafts = get_amount(SHAFT_ID)
    debug_message(f"Resources: feathers={feathers}, shafts={shafts}, logs={get_amount(LOG_ID)}, boards={get_amount(BOARD_ID)}")

    if feathers <= 0 and shafts <= 0:
        debug_message("No feathers and no shafts; nothing to craft.", 53)
        return

    # Ensure gump open once before start 
    ensure_gump_open()

    # Step 1: Make shafts once if needed and if we have regular wood
    shafts_needed = compute_shafts_needed(feathers, shafts)
    if shafts_needed > 0:
        max_craftable = compute_max_shafts_craftable()
        if max_craftable > 0:
            debug_message(f"Crafting shafts once (needed={shafts_needed}, available_regular_wood={max_craftable})")
            craft_once(BUTTONS['category_materials'], BUTTONS['make_shafts'])
        else:
            debug_message("Insufficient logs/boards to craft shafts.", 53)
    else:
        debug_message("Shafts sufficient for feathers; skipping shaft crafting.")

    # Refresh counts
    feathers = get_amount(FEATHER_ID)
    shafts = get_amount(SHAFT_ID)

    # Step 2: Craft arrows once if materials exist
    if min(feathers, shafts) <= 0:
        debug_message("No matching feathers/shafts to make arrows.", 53)
        return

    debug_message("Crafting arrows once")
    craft_once(BUTTONS['category_ammunition'], BUTTONS['make_arrows'])
    
    # Close gump after crafting
    close_gump()

def close_gump():
    """Close the fletching gump if it's open."""
    try:
        if Gumps.HasGump(FLETCHING_GUMP_ID):
            Gumps.CloseGump(FLETCHING_GUMP_ID)
    except Exception:
        pass

def main():
    try:
        run_arrow_crafting()
    except Exception as e:
        debug_message(f"Error in CRAFT_arrows: {e}", 33)
    finally:
        close_gump()

if __name__ == "__main__":
    main()
