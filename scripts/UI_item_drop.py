"""
UI Item Drop - a Razor Enhanced Python Script for Ultima Online

select and place items on the ground , creating a trail , or in circle

VERSION: 20251015
"""

DEBUG_MODE = False

# GUMP ID LIMIT = 0xFFFFFFF = 4294967295 # max int , make sure gump ids are under this but high unique 
GUMP_ID =                     4121211122
GUMP_START_X = 300
GUMP_START_Y = 300

# Layout - each slot has its own column with buttons underneath
HEADER_HEIGHT = 18
ITEM_SLOT_SIZE = 60
ITEM_SLOT_GAP = 8
BUTTON_WIDTH = 63  # small button from 
BUTTON_HEIGHT = 23  # small button from 
BUTTON_GAP = 2
NAME_LABEL_HEIGHT = 28
HEX_LABEL_HEIGHT = 12

# Calculate gump dimensions based on 3 columns
COLUMN_WIDTH = max(ITEM_SLOT_SIZE, BUTTON_WIDTH)
GUMP_WIDTH = (COLUMN_WIDTH * 3) + (ITEM_SLOT_GAP * 2) + 8  # 3 columns + gaps + padding
INPUT_FIELD_HEIGHT = 20
GUMP_HEIGHT = HEADER_HEIGHT + ITEM_SLOT_SIZE + NAME_LABEL_HEIGHT + (BUTTON_HEIGHT * 4) + (BUTTON_GAP * 3) + HEX_LABEL_HEIGHT + INPUT_FIELD_HEIGHT + 15

# Button style 
BUTTON_ART_ID = 2443  # small wide button
SLIVER_OVERLAY_ENABLED = True
SLIVER_OVERLAY_TILE_ART_ID = 2624
SLIVER_OVERLAY_MODE = "full"

# Font colors
FONT_COLORS = {
    "white": 0x0384,
    "gray": 0x0385,
    "blue": 0x0056,
    "green": 0x0044,
    "red": 0x0020,
    "yellow": 0x0099,
}

# Selected item state - default 3 slots
SELECTED_ITEMS = [
    {"serial": None, "item_id": None, "hue": None, "name": "None", "trail_active": False},
    {"serial": None, "item_id": None, "hue": None, "name": "None", "trail_active": False},
    {"serial": None, "item_id": None, "hue": None, "name": "None", "trail_active": False},
]

# Trail mode state  per-slot
TRAIL_PLACED_COORDS = [set(), set(), set()]  # Track where we've placed items for each slot
TRAIL_LAST_POSITION = [None, None, None]  # Last position for each slot

PAUSE_DURATION_PLACE = 650
MAX_DISTANCE = 2

# Gold special handling
GOLD_ITEM_ID = 0x0EED
GOLD_STACK_DISPLAY_ID = 0x0EEF  # Gold stack image for display
GOLD_DROP_AMOUNT = 20

# Circle placement state
CIRCLE_RADIUS = 2  # Default radius for circle placement
CIRCLE_ACTIVE = [False, False, False]  # Track if circle mode is active for each slot

# Click debounce (using counter)
_LAST_CLICK_BID = -1
_CLICK_COUNTER = 0

#//======================================================================

def debug_message(msg, color=67):
    """Send debug message if DEBUG_MODE is enabled."""
    if DEBUG_MODE:
        try:
            Misc.SendMessage(f"[UI_ITEM_DROP] {msg}", color)
        except Exception:
            pass

def add_centered_label_with_outline(gd, x, y, w, h, text, hue):
    """Draw a centered label with black outline for readability."""
    try:
        approx_char_px = 6
        text_x = x + (w // 2) - max(0, len(text)) * approx_char_px // 2
        text_y = y + (h // 2) - 7
        outline_color = 0  # black
        offsets_r1 = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
        offsets_r2 = [(-2, 0), (2, 0), (0, -2), (0, 2), (-2, -1), (-2, 1), (2, -1), (2, 1), (-1, -2), (1, -2), (-1, 2), (1, 2)]
        for dx, dy in offsets_r2:
            Gumps.AddLabel(gd, text_x + dx, text_y + dy, outline_color, text)
        for dx, dy in offsets_r1:
            Gumps.AddLabel(gd, text_x + dx, text_y + dy, outline_color, text)
        Gumps.AddLabel(gd, text_x, text_y, hue, text)
    except Exception:
        pass

def get_item_name(item):
    """Get item name using properties, stripping amount prefix and whitespace."""
    try:
        nm = getattr(item, 'Name', None)
        if nm:
            nm = str(nm)
        else:
            Items.WaitForProps(item.Serial, 600)
            props = Items.GetPropStringList(item.Serial)
            if props and len(props) > 0:
                nm = str(props[0])
            else:
                return "Unknown"
        
        # Strip leading whitespace
        nm = nm.lstrip()
        
        # Remove amount prefix (e.g., "5 Black Pearls" -> "Black Pearls")
        # Check if first word is a number
        parts = nm.split(None, 1)  # Split on first whitespace
        if len(parts) > 1:
            try:
                int(parts[0])  # Try to parse first part as number
                nm = parts[1]  # Use everything after the number
            except ValueError:
                pass  # Not a number, keep original
        
        return nm
    except Exception:
        pass
    return "Unknown"

def is_valid_position(x, y, z):
    """Check if position is valid for item placement."""
    try:
        return (
            Player.Position.X - MAX_DISTANCE <= x <= Player.Position.X + MAX_DISTANCE
            and Player.Position.Y - MAX_DISTANCE <= y <= Player.Position.Y + MAX_DISTANCE
            and Statics.GetLandID(x, y, Player.Map) not in [0x0001]
        )
    except Exception:
        return False

def generate_circle_points(center_x, center_y, radius, points):
    """Generate points in a circle pattern using hardcoded isometric grid coordinates.
    specific rounded patterns for isometric diagonal viewpoint
    """
    # circle patterns for isometric grid (relative offsets from center)
    # These are tuned to look circular on isometric display
    CIRCLE_PATTERNS = {
        1: [
            (0, -1), (1, 0), (0, 1), (-1, 0)
        ],
        2: [
            (0, -2), (1, -2), (2, -1), (2, 0),
            (2, 1), (1, 2), (0, 2), (-1, 2),
            (-2, 1), (-2, 0), (-2, -1), (-1, -2)
        ],
        3: [
            (0, -3), (1, -3), (2, -2), (3, -1),
            (3, 0), (3, 1), (2, 2), (1, 3),
            (0, 3), (-1, 3), (-2, 2), (-3, 1),
            (-3, 0), (-3, -1), (-2, -2), (-1, -3)
        ],
        4: [
            (0, -4), (1, -4), (2, -3), (3, -2),
            (4, -1), (4, 0), (4, 1), (3, 2),
            (2, 3), (1, 4), (0, 4), (-1, 4),
            (-2, 3), (-3, 2), (-4, 1), (-4, 0),
            (-4, -1), (-3, -2), (-2, -3), (-1, -4)
        ],
        5: [
            (0, -5), (1, -5), (2, -4), (3, -3),
            (4, -2), (5, -1), (5, 0), (5, 1),
            (4, 2), (3, 3), (2, 4), (1, 5),
            (0, 5), (-1, 5), (-2, 4), (-3, 3),
            (-4, 2), (-5, 1), (-5, 0), (-5, -1),
            (-4, -2), (-3, -3), (-2, -4), (-1, -5)
        ],
        6: [
            (0, -6), (1, -6), (2, -5), (3, -4),
            (4, -3), (5, -2), (6, -1), (6, 0),
            (6, 1), (5, 2), (4, 3), (3, 4),
            (2, 5), (1, 6), (0, 6), (-1, 6),
            (-2, 5), (-3, 4), (-4, 3), (-5, 2),
            (-6, 1), (-6, 0), (-6, -1), (-5, -2),
            (-4, -3), (-3, -4), (-2, -5), (-1, -6)
        ]
    }
    
    # Get pattern for this radius, default to radius 2 if not found
    pattern = CIRCLE_PATTERNS.get(radius, CIRCLE_PATTERNS[2])
    
    # Convert relative offsets to absolute coordinates
    result = []
    for dx, dy in pattern:
        x = center_x + dx
        y = center_y + dy
        result.append((x, y))
    
    return result

def get_direction(from_x, from_y, to_x, to_y):
    """Calculate direction from one point to another."""
    dx = to_x - from_x
    dy = to_y - from_y
    
    if dx == 0:
        if dy < 0: return 0  # North
        return 4  # South
    elif dy == 0:
        if dx > 0: return 2  # East
        return 6  # West
    elif dx > 0:
        if dy < 0: return 1  # Northeast
        return 3  # Southeast
    else:
        if dy < 0: return 7  # Northwest
        return 5  # Southwest

def dir_to_str(d):
    """Convert direction number to string."""
    mapping = {0: "North", 1: "Northeast", 2: "East", 3: "Southeast",
               4: "South", 5: "Southwest", 6: "West", 7: "Northwest"}
    return mapping.get(int(d) % 8, "North")

def attempt_walk_toward(tx, ty, max_steps=6):
    """Walk toward target position."""
    last_pos = (Player.Position.X, Player.Position.Y)
    
    for step in range(max_steps):
        if (abs(Player.Position.X - tx) <= MAX_DISTANCE and
            abs(Player.Position.Y - ty) <= MAX_DISTANCE):
            return True
        
        base_dir = get_direction(Player.Position.X, Player.Position.Y, tx, ty)
        dirs = [base_dir, (base_dir+1)%8, (base_dir+7)%8]
        
        moved = False
        for d in dirs:
            for attempt in range(2):  # Try twice per direction to ensure movement
                try:
                    Player.Walk(dir_to_str(d))
                    Misc.Pause(250)
                    
                    cur_pos = (Player.Position.X, Player.Position.Y)
                    if cur_pos != last_pos:
                        moved = True
                        last_pos = cur_pos
                        break
                except Exception:
                    pass
            
            if moved:
                break
        
        if not moved:
            Misc.Pause(600)  # Extra pause if stuck
    
    return (abs(Player.Position.X - tx) <= MAX_DISTANCE and
            abs(Player.Position.Y - ty) <= MAX_DISTANCE)

def place_circle(slot_index, radius):
    """Place items in a circle pattern using ritual framework."""
    global CIRCLE_ACTIVE
    
    selected_item = SELECTED_ITEMS[slot_index]
    
    if selected_item["item_id"] is None:
        Misc.SendMessage("No item selected!", 33)
        return False
    
    # Get center position (player's current position)
    center_x = Player.Position.X
    center_y = Player.Position.Y
    center_z = Player.Position.Z
    
    # Generate circle points (hardcoded patterns)
    points = generate_circle_points(center_x, center_y, radius, 0)  # points param unused now
    num_points = len(points)
    
    # Check if we have enough items
    item_count = Items.BackpackCount(selected_item["item_id"], selected_item["hue"])
    if item_count < num_points:
        Misc.SendMessage(f"Need {num_points} items, only have {item_count}!", 33)
        return False
    
    Misc.SendMessage(f"Starting circle placement: {num_points} items at radius {radius}", 68)
    debug_message(f"Circle center: ({center_x}, {center_y}), radius: {radius}, points: {num_points}", 67)
    CIRCLE_ACTIVE[slot_index] = True
    
    placed_count = 0
    failed_count = 0
    
    # Place items at each point
    for i, (x, y) in enumerate(points, 1):
        if not CIRCLE_ACTIVE[slot_index]:
            Misc.SendMessage("Circle placement cancelled", 33)
            break
        
        debug_message(f"Placing item {i} of {num_points}", 67)
        
        # Try to walk to position
        if not attempt_walk_toward(x, y):
            debug_message(f"Could not reach position ({x}, {y})", 33)
            failed_count += 1
            if failed_count >= 3:
                Misc.SendMessage("Too many failures, stopping circle placement", 33)
                break
            continue
        
        # Determine drop amount (special handling for gold)
        is_gold = (selected_item["item_id"] == GOLD_ITEM_ID)
        drop_amount = GOLD_DROP_AMOUNT if is_gold else 1
        
        # Find item
        item = Items.FindByID(selected_item["item_id"], selected_item["hue"], Player.Backpack.Serial)
        if not item:
            Misc.SendMessage(f"Out of {selected_item['name']}!", 33)
            break
        
        # Place item
        try:
            initial_count = Items.BackpackCount(selected_item["item_id"], selected_item["hue"])
            Items.MoveOnGround(item, drop_amount, x, y, center_z)
            Misc.Pause(PAUSE_DURATION_PLACE)
            
            new_count = Items.BackpackCount(selected_item["item_id"], selected_item["hue"])
            if new_count < initial_count:
                placed_count += 1
            else:
                failed_count += 1
        except Exception as e:
            debug_message(f"Error placing item: {e}", 33)
            failed_count += 1
    
    CIRCLE_ACTIVE[slot_index] = False
    Misc.SendMessage(f"Circle complete! Placed {placed_count} items", 68)
    return True

def cancel_circle(slot_index):
    """Cancel active circle placement."""
    global CIRCLE_ACTIVE
    CIRCLE_ACTIVE[slot_index] = False
    Misc.SendMessage(f"Circle placement cancelled for slot {slot_index + 1}", 53)

def place_item_at_feet(quiet=False, slot_index=None):
    """Place one item at the player's feet using ritual-style placement.
    Special handling: Gold is placed 20 at a time instead of 1.
    """
    global SELECTED_ITEMS, ACTIVE_SLOT
    
    # Use specified slot or active slot
    if slot_index is None:
        slot_index = ACTIVE_SLOT
    
    selected_item = SELECTED_ITEMS[slot_index]
    
    if selected_item["item_id"] is None:
        if not quiet:
            Misc.SendMessage("No item selected!", 33)
        return False
    
    # Find the item in backpack
    item = Items.FindByID(selected_item["item_id"], selected_item["hue"], Player.Backpack.Serial)
    if not item:
        if not quiet:
            Misc.SendMessage(f"Could not find {selected_item['name']} in backpack!", 33)
        return False
    
    # Get player position
    x = Player.Position.X
    y = Player.Position.Y
    z = -1  # Use -1 for auto-stacking
    
    # Validate position
    if not is_valid_position(x, y, z):
        if not quiet:
            Misc.SendMessage("Invalid position for item placement!", 33)
        return False
    
    # Determine drop amount - special handling for gold
    is_gold = (selected_item["item_id"] == GOLD_ITEM_ID)
    drop_amount = GOLD_DROP_AMOUNT if is_gold else 1
    
    try:
        # Get initial count
        initial_count = Items.BackpackCount(selected_item["item_id"], selected_item["hue"])
        
        # Check if we have enough for the drop amount
        if initial_count < drop_amount:
            if not quiet:
                Misc.SendMessage(f"Not enough {selected_item['name']} (need {drop_amount}, have {initial_count})", 33)
            return False
        
        # Place the item
        Items.MoveOnGround(item, drop_amount, x, y, z)
        Misc.Pause(PAUSE_DURATION_PLACE)
        
        # Verify placement
        new_count = Items.BackpackCount(selected_item["item_id"], selected_item["hue"])
        if new_count < initial_count:
            if not quiet:
                amount_text = f" ({drop_amount})" if is_gold else ""
                Misc.SendMessage(f"Placed {selected_item['name']}{amount_text} at feet", 68)
            return True
        else:
            if not quiet:
                Misc.SendMessage("Item placement failed!", 33)
            return False
            
    except Exception as e:
        if not quiet:
            Misc.SendMessage(f"Error placing item: {e}", 33)
        debug_message(f"Placement error: {e}", 33)
        return False

def toggle_trail_mode(slot_index):
    """Toggle trail mode on/off for a specific slot."""
    global TRAIL_PLACED_COORDS, TRAIL_LAST_POSITION, SELECTED_ITEMS
    
    if SELECTED_ITEMS[slot_index]["item_id"] is None:
        Misc.SendMessage("Select an item first!", 33)
        return
    
    SELECTED_ITEMS[slot_index]["trail_active"] = not SELECTED_ITEMS[slot_index]["trail_active"]
    
    if SELECTED_ITEMS[slot_index]["trail_active"]:
        # Reset trail tracking for this slot
        TRAIL_PLACED_COORDS[slot_index] = set()
        TRAIL_LAST_POSITION[slot_index] = None
        Misc.SendMessage(f"Trail mode ENABLED for slot {slot_index + 1}", 68)
        debug_message(f"Trail mode started for slot {slot_index + 1}", 67)
    else:
        Misc.SendMessage(f"Trail mode DISABLED for slot {slot_index + 1}", 53)
        debug_message(f"Trail mode stopped for slot {slot_index + 1}. Placed {len(TRAIL_PLACED_COORDS[slot_index])} items", 67)

def trail_mode_loop():
    """Main loop for trail mode - places items as player walks for all active slots."""
    global TRAIL_PLACED_COORDS, TRAIL_LAST_POSITION, SELECTED_ITEMS
    
    # Get current position
    current_pos = (Player.Position.X, Player.Position.Y)
    
    # Check each slot for active trail mode
    for slot_index in range(3):
        if not SELECTED_ITEMS[slot_index]["trail_active"]:
            continue
        
        # Check if player has moved to a new location for this slot
        if current_pos != TRAIL_LAST_POSITION[slot_index]:
            # Check if we haven't already placed at this location for this slot
            if current_pos not in TRAIL_PLACED_COORDS[slot_index]:
                # Try to place item
                if place_item_at_feet(quiet=True, slot_index=slot_index):
                    TRAIL_PLACED_COORDS[slot_index].add(current_pos)
                    debug_message(f"Trail item placed at {current_pos} for slot {slot_index + 1}. Total: {len(TRAIL_PLACED_COORDS[slot_index])}", 68)
                else:
                    # Out of items or error - stop trail mode for this slot
                    Misc.SendMessage(f"Trail mode stopped for slot {slot_index + 1} - out of items or error", 33)
                    SELECTED_ITEMS[slot_index]["trail_active"] = False
            
            # Update last position for this slot
            TRAIL_LAST_POSITION[slot_index] = current_pos

def select_item_target(slot_index):
    """Prompt user to target an item to select."""
    global SELECTED_ITEMS
    
    Misc.SendMessage(f"Select an item for slot {slot_index + 1}...", 68)
    
    try:
        # Clear any existing target
        Target.Cancel()
        Misc.Pause(100)
        
        # Prompt for target - returns serial directly
        serial = Target.PromptTarget("Select an item from your backpack")
        
        if serial <= -1:
            Misc.SendMessage("Selection cancelled.", 53)
            return False
        
        # Get the item
        item = Items.FindBySerial(serial)
        if not item:
            Misc.SendMessage("Invalid item selected!", 33)
            return False
        
        # Check if item is in backpack
        if item.Container != Player.Backpack.Serial:
            Misc.SendMessage("Item must be in your backpack!", 33)
            return False
        
        # Store item information
        SELECTED_ITEMS[slot_index]["serial"] = item.Serial
        SELECTED_ITEMS[slot_index]["item_id"] = item.ItemID
        SELECTED_ITEMS[slot_index]["hue"] = item.Hue
        SELECTED_ITEMS[slot_index]["name"] = get_item_name(item)
        
        Misc.SendMessage(f"Slot {slot_index + 1}: {SELECTED_ITEMS[slot_index]['name']}", 68)
        debug_message(f"Selected item: ID=0x{SELECTED_ITEMS[slot_index]['item_id']:04X}, Hue=0x{SELECTED_ITEMS[slot_index]['hue']:04X}", 67)
        return True
        
    except Exception as e:
        Misc.SendMessage(f"Error selecting item: {e}", 33)
        debug_message(f"Selection error: {e}", 33)
        return False

def render_gump():
    """Render the main UI gump with 3 columns, each with item slot and buttons underneath."""
    global SELECTED_ITEMS
    
    gd = Gumps.CreateGump(movable=True)
    Gumps.AddPage(gd, 0)
    
    # Background
    Gumps.AddBackground(gd, 0, 0, GUMP_WIDTH, GUMP_HEIGHT, 30546)
    Gumps.AddAlphaRegion(gd, 0, 0, GUMP_WIDTH, GUMP_HEIGHT)
    
    # Header
    try:
        Gumps.AddHtml(gd, 2, 0, GUMP_WIDTH - 4, HEADER_HEIGHT,
                      "<center><basefont color=#3FA9FF>DROP</basefont></center>", 0, 0)
    except Exception:
        pass
    
    # Calculate column positions
    first_column_x = 4
    slot_y = HEADER_HEIGHT + 2
    
    # Render 3 columns (one for each slot)
    for i in range(3):
        column_x = first_column_x + (i * (COLUMN_WIDTH + ITEM_SLOT_GAP))
        selected_item = SELECTED_ITEMS[i]
        
        # Center item slot within column
        slot_x = column_x + (COLUMN_WIDTH - ITEM_SLOT_SIZE) // 2
        
        # Display selected item or placeholder
        if selected_item["item_id"] is not None:
            try:
                # Center the item in the slot with offset (left 10, up 10)
                item_x = slot_x + ITEM_SLOT_SIZE // 2 - 10
                item_y = slot_y + ITEM_SLOT_SIZE // 2 - 10
                
                # Use gold stack image for display if gold is selected
                display_item_id = selected_item["item_id"]
                if selected_item["item_id"] == GOLD_ITEM_ID:
                    display_item_id = GOLD_STACK_DISPLAY_ID
                
                if selected_item["hue"] is not None and selected_item["hue"] != 0:
                    Gumps.AddItem(gd, item_x, item_y, display_item_id, selected_item["hue"])
                else:
                    Gumps.AddItem(gd, item_x, item_y, display_item_id)
            except Exception as e:
                debug_message(f"Error displaying item in slot {i}: {e}", 33)
        else:
            # Show placeholder text
            try:
                Gumps.AddHtml(gd, slot_x, slot_y + ITEM_SLOT_SIZE // 2 - 10, ITEM_SLOT_SIZE, 20,
                              f"<center><basefont color=#888888>{i + 1}</basefont></center>", 0, 0)
            except Exception:
                pass
        
        # Item name label below slot
        name_y = slot_y + ITEM_SLOT_SIZE + 2
        try:
            name_text = selected_item["name"] if selected_item["name"] else "None"
            # Truncate long names
            if len(name_text) > 10:
                name_text = name_text[:9] + "..."
            Gumps.AddHtml(gd, column_x, name_y, COLUMN_WIDTH, NAME_LABEL_HEIGHT,
                          f"<center><basefont color=#CCCCCC>{name_text}</basefont></center>", 0, 0)
        except Exception:
            pass
        
        # Button positions (centered in column)
        button_x = column_x + (COLUMN_WIDTH - BUTTON_WIDTH) // 2
        select_button_y = name_y + NAME_LABEL_HEIGHT
        drop_button_y = select_button_y + BUTTON_HEIGHT + BUTTON_GAP
        trail_button_y = drop_button_y + BUTTON_HEIGHT + BUTTON_GAP
        circle_button_y = trail_button_y + BUTTON_HEIGHT + BUTTON_GAP
        
        # Button IDs: slot 0 = 1,2,3,4; slot 1 = 11,12,13,14; slot 2 = 21,22,23,24
        base_button_id = (i * 10) + 1
        
        # Select Item button
        try:
            Gumps.AddButton(gd, button_x, select_button_y, BUTTON_ART_ID, BUTTON_ART_ID, base_button_id, 1, 0)
            if SLIVER_OVERLAY_ENABLED:
                Gumps.AddImageTiled(gd, button_x, select_button_y, BUTTON_WIDTH, BUTTON_HEIGHT, SLIVER_OVERLAY_TILE_ART_ID)
            add_centered_label_with_outline(gd, button_x, select_button_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Select", FONT_COLORS["blue"])
        except Exception as e:
            debug_message(f"Error adding select button for slot {i}: {e}", 33)
        
        # Drop Item button
        try:
            Gumps.AddButton(gd, button_x, drop_button_y, BUTTON_ART_ID, BUTTON_ART_ID, base_button_id + 1, 1, 0)
            if SLIVER_OVERLAY_ENABLED:
                Gumps.AddImageTiled(gd, button_x, drop_button_y, BUTTON_WIDTH, BUTTON_HEIGHT, SLIVER_OVERLAY_TILE_ART_ID)
            
            # Color button based on whether item is selected
            button_color = FONT_COLORS["green"] if selected_item["item_id"] is not None else FONT_COLORS["gray"]
            add_centered_label_with_outline(gd, button_x, drop_button_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Drop", button_color)
        except Exception as e:
            debug_message(f"Error adding drop button for slot {i}: {e}", 33)
        
        # Trail Mode button
        try:
            Gumps.AddButton(gd, button_x, trail_button_y, BUTTON_ART_ID, BUTTON_ART_ID, base_button_id + 2, 1, 0)
            if SLIVER_OVERLAY_ENABLED:
                Gumps.AddImageTiled(gd, button_x, trail_button_y, BUTTON_WIDTH, BUTTON_HEIGHT, SLIVER_OVERLAY_TILE_ART_ID)
            
            # Color button based on trail mode state
            if selected_item["trail_active"]:
                trail_color = FONT_COLORS["red"]  # Red when active
                trail_label = "Stop"
            elif selected_item["item_id"] is not None:
                trail_color = FONT_COLORS["yellow"]  # Yellow when ready
                trail_label = "Trail"
            else:
                trail_color = FONT_COLORS["gray"]  # Gray when disabled
                trail_label = "Trail"
            add_centered_label_with_outline(gd, button_x, trail_button_y, BUTTON_WIDTH, BUTTON_HEIGHT, trail_label, trail_color)
        except Exception as e:
            debug_message(f"Error adding trail button for slot {i}: {e}", 33)
        
        # Circle button
        try:
            Gumps.AddButton(gd, button_x, circle_button_y, BUTTON_ART_ID, BUTTON_ART_ID, base_button_id + 3, 1, 0)
            if SLIVER_OVERLAY_ENABLED:
                Gumps.AddImageTiled(gd, button_x, circle_button_y, BUTTON_WIDTH, BUTTON_HEIGHT, SLIVER_OVERLAY_TILE_ART_ID)
            
            # Color button based on circle mode state
            if CIRCLE_ACTIVE[i]:
                circle_color = FONT_COLORS["red"]  # Red when active
                circle_label = "Cancel"
            elif selected_item["item_id"] is not None:
                circle_color = FONT_COLORS["white"]  # White when ready
                circle_label = "Circle"
            else:
                circle_color = FONT_COLORS["gray"]  # Gray when disabled
                circle_label = "Circle"
            add_centered_label_with_outline(gd, button_x, circle_button_y, BUTTON_WIDTH, BUTTON_HEIGHT, circle_label, circle_color)
        except Exception as e:
            debug_message(f"Error adding circle button for slot {i}: {e}", 33)
        
        # Item hex ID below circle button
        hex_y = circle_button_y + BUTTON_HEIGHT + 2
        try:
            if selected_item["item_id"] is not None:
                hex_text = f"0x{selected_item['item_id']:04X}"
                Gumps.AddHtml(gd, column_x, hex_y, COLUMN_WIDTH, HEX_LABEL_HEIGHT,
                              f"<center><basefont color=#888888>{hex_text}</basefont></center>", 0, 0)
        except Exception:
            pass
    
    # Circle radius preset buttons at bottom
    button_y = GUMP_HEIGHT - INPUT_FIELD_HEIGHT - 5
    label_x = 4
    
    try:
        # Label
        Gumps.AddHtml(gd, label_x, button_y + 2, 50, INPUT_FIELD_HEIGHT,
                      "<basefont color=#CCCCCC>Radius:</basefont>", 0, 0)
        
        # Radius preset buttons (IDs: 99=radius 1, 100=radius 2, 101=radius 3, 102=radius 4, 103=radius 5, 104=radius 6)
        button_start_x = label_x + 52
        button_size = 23  # Square button size for gump 210
        button_spacing = 2
        
        for i, radius_val in enumerate([1, 2, 3, 4, 5, 6]):
            btn_x = button_start_x + (i * (button_size + button_spacing))
            btn_id = 99 + i
            
            # Highlight selected radius
            if CIRCLE_RADIUS == radius_val:
                btn_color = FONT_COLORS["yellow"]
            else:
                btn_color = FONT_COLORS["white"]
            
            Gumps.AddButton(gd, btn_x, button_y, 210, 210, btn_id, 1, 0)
            if SLIVER_OVERLAY_ENABLED:
                Gumps.AddImageTiled(gd, btn_x, button_y, button_size, button_size, SLIVER_OVERLAY_TILE_ART_ID)
            
            # Center label in square button
            label_text = str(radius_val)
            text_x = btn_x + (button_size // 2) - 3
            text_y = button_y + (button_size // 2) - 7
            Gumps.AddLabel(gd, text_x, text_y, btn_color, label_text)
    except Exception as e:
        debug_message(f"Error adding radius buttons: {e}", 33)
    
    # Send gump
    Gumps.SendGump(GUMP_ID, Player.Serial, GUMP_START_X, GUMP_START_Y, gd.gumpDefinition, gd.gumpStrings)

def process_input():
    """Process gump input and handle button clicks.
    Button IDs: 
    - Slot actions: slot 0 = 1,2,3,4; slot 1 = 11,12,13,14; slot 2 = 21,22,23,24
    - Radius presets: 99=radius 1, 100=radius 2, 101=radius 3, 102=radius 4, 103=radius 5, 104=radius 6
    """
    global _LAST_CLICK_BID, _CLICK_COUNTER, CIRCLE_RADIUS
    
    # Wait for gump interaction
    Gumps.WaitForGump(GUMP_ID, 500)
    gump_data = Gumps.GetGumpData(GUMP_ID)
    
    if not gump_data:
        return False
    
    button_id = int(getattr(gump_data, 'buttonid', 0))
    
    # Debounce: ignore repeated same button id (simple counter-based)
    _CLICK_COUNTER += 1
    if button_id > 0 and button_id == _LAST_CLICK_BID and _CLICK_COUNTER < 2:
        return False
    
    if button_id == 0:
        return False
    
    # Reset counter on new button or after threshold
    if button_id != _LAST_CLICK_BID:
        _CLICK_COUNTER = 0
    
    # Handle radius preset buttons (99, 100, 101, 102, 103, 104)
    if button_id >= 99 and button_id <= 104:
        _LAST_CLICK_BID = button_id
        
        radius_map = {99: 1, 100: 2, 101: 3, 102: 4, 103: 5, 104: 6}
        CIRCLE_RADIUS = radius_map[button_id]
        Misc.SendMessage(f"Circle radius set to {CIRCLE_RADIUS}", 68)
        render_gump()
        return False
    
    # Determine slot and action from button_id
    # Slot 0: 1,2,3,4 = Select, Drop, Trail, Circle
    # Slot 1: 11,12,13,14 = Select, Drop, Trail, Circle
    # Slot 2: 21,22,23,24 = Select, Drop, Trail, Circle
    slot_index = button_id // 10
    action_type = button_id % 10
    
    # Validate slot index
    if slot_index < 0 or slot_index > 2:
        return False
    
    _LAST_CLICK_BID = button_id
    
    # Handle actions
    if action_type == 1:
        # Select Item button
        try:
            Gumps.CloseGump(GUMP_ID)
        except Exception:
            pass
        
        select_item_target(slot_index)
        render_gump()
        
    elif action_type == 2:
        # Drop Item button
        place_item_at_feet(slot_index=slot_index)
        render_gump()
        
    elif action_type == 3:
        # Trail Mode button
        toggle_trail_mode(slot_index)
        render_gump()
        
    elif action_type == 4:
        # Circle button
        if CIRCLE_ACTIVE[slot_index]:
            # Cancel active circle
            cancel_circle(slot_index)
        else:
            # Start circle placement
            try:
                Gumps.CloseGump(GUMP_ID)
            except Exception:
                pass
            
            place_circle(slot_index, CIRCLE_RADIUS)
        
        render_gump()
    
    return False

def main():
    """Main entry point."""
    render_gump()
    
    done = False
    while Player.Connected and not done:
        # Process trail mode if active
        trail_mode_loop()
        
        # Process gump input
        done = process_input()
        Misc.Pause(100)

if __name__ == "__main__":
    main()
