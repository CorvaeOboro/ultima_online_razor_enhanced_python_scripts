"""
Development Item to JSON List  - a Razor Enhanced Python Script for Ultima Online

Creates a gump UI for selecting items 
exporting their details to categorized .json files.

Categories:
Trash , Bank , Salvage , Keep , Quest ,
 Food , Update , Orb , Ritual

this is useful to store item ids for use in other scripts 
exported .json files are stored in a 'data' subdirectory next to the script

VERSION::20250919
"""
import os
import json
import shutil
import time

# Base path for data files is a 'data' subdirectory next to the script
BASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")

# Item List Category definitions with file paths
list_configs = [
    {
        "name": "Trash",
        "file": os.path.join(BASE_PATH, "items_trash.json"),
        "description": "Items to automatically throw away"
    },
    {
        "name": "Bank",
        "file": os.path.join(BASE_PATH, "items_bank.json"),
        "description": "Items to move to bank"
    },
    {
        "name": "Salvage",
        "file": os.path.join(BASE_PATH, "items_salvage.json"),
        "description": "Items to consider for salvage"
    },
    {
        "name": "Keep",
        "file": os.path.join(BASE_PATH, "items_keep.json"),
        "description": "Important items to never throw away"
    },
    {
        "name": "Quest",
        "file": os.path.join(BASE_PATH, "items_quest.json"),
        "description": "Items needed for quest turn-ins"
    },
    {
        "name": "Food",
        "file": os.path.join(BASE_PATH, "items_food.json"),
        "description": "Food items for consumption or scripts"
    },
    {
        "name": "Update",
        "file": os.path.join(BASE_PATH, "items_update.json"),
        "description": "Items whose art we want to update"
    },
    {
        "name": "Ritual",
        "file": os.path.join(BASE_PATH, "items_ritual.json"),
        "description": "Items used in rituals"
    },
    {
        "name": "Orb",
        "file": os.path.join(BASE_PATH, "items_orb.json"),
        "description": "Items whose art we want to update"
    },
    {
        "name": "Resource",
        "file": os.path.join(BASE_PATH, "items_resource.json"),
        "description": "Resource items: ingots, boards, leather, cloth, etc. for crafting or scripts"
    },
        {
        "name": "Rare",
        "file": os.path.join(BASE_PATH, "items_rare.json"),
        "description": "Rare items: paragon chest , decoration"
    },
    {
        "name": "Unknown",
        "file": os.path.join(BASE_PATH, "items_unknown.json"),
        "description": "Unknown items that could use better description , to add to walia"
    },
    {
        "name": "EnhancementScroll",
        "file": os.path.join(BASE_PATH, "items_enhancement_scroll.json"),
        "description": "Enhancement scrolls"
    },
]

UI_ACTIVE = True
GUMP_START_X = 400
GUMP_START_Y = 400

# gump ID= 4294967295  = the max value , randomly select a high number gump so its unique
GUMP_ID =  3429654321

# UI Style selection and layout
BUTTON_STYLE = "small"            # one of: "large", "small", "wide"
VERTICAL_ONLY = True              # Keep a single column layout for categories
USE_ASPECT_PACKING = False        # Not needed for a simple vertical list
TARGET_GUMP_WIDTH_RATIO = 16
TARGET_GUMP_HEIGHT_RATIO = 9

# Map style name -> (art_id, width, height)
BUTTON_STYLE_MAP = {
    "large": (1, 80, 40),
    "small": (2443, 63, 23),
    "wide":  (2368, 80, 20),
}

SIZE_FROM_ART = True              # Derive button dimensions from art

# Button sizing will be resolved at runtime
BUTTON_WIDTH = 1
BUTTON_HEIGHT = 1
BUTTON_GAP_X = 0
BUTTON_GAP_Y = 1

# Background panel sizing minimums
PANEL_WIDTH_MIN = 0
PANEL_HEIGHT_MIN = 0

# Optional dark overlay on buttons for readability
SLIVER_OVERLAY_ENABLED = True
SLIVER_OVERLAY_TILE_ART_ID = 2624
SLIVER_OVERLAY_MODE = "full"     # "full" or "stripes"
SLIVER_STRIPE_HEIGHT = 6

# Font hex hue colors by name
FONT_COLORS = {
    "white": 0x0384,
    "gray": 0x0385,
    "dark_gray": 0x07AF,
    "gold": 0x08A5,
    "yellow": 0x0099,
    "red": 0x0020,
    "dark_red": 0x0024,
    "maroon": 0x0021,
    "orange": 0x0030,
    "beige": 0x002D,
    "brown": 0x01BB,
    "green": 0x0044,
    "dark_green": 0x0042,
    "lime": 0x0040,
    "teal": 0x0058,
    "aqua": 0x005F,
    "light_blue": 0x005A,
    "blue": 0x0056,
    "dark_blue": 0x0001,
    "purple": 0x01A2,
}
FONT_COLOR_NAME = "white"
FONT_HUE = FONT_COLORS.get(FONT_COLOR_NAME, 0x0384)

# Click debounce tracking
_LAST_CLICK_BID = -1
_LAST_CLICK_TS = 0.0

# Header configuration for draggable title bar
HEADER_HEIGHT = 20
HEADER_TEXT = "I T E M      LIST"
HEADER_COLOR_HTML = "BBBBBB"  # grey

# Track last UI refresh to distinguish intentional refresh from user-close
_LAST_REFRESH_TS = 0.0

# Debug toggles
DEBUG = {
    "SKIP_UI": False,           # Skip creating the UI completely
    "TEST_TARGET": False,       # Test only the targeting system
    "TEST_SPECIFIC_LIST": "",   # Test a specific list (e.g., "Bank Items")
    "VERBOSE_LOGGING": True,    # Enable detailed debug messages
}

#//===========================================================================

def ensure_directory(file_path):
    """Ensure the directory exists for the given file path."""
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        debug_msg(f"Creating directory: {directory}")
        os.makedirs(directory)

def format_hex(value):
    """Return zero-padded 4-digit uppercase hex with 0x prefix, e.g., 0x00F2."""
    try:
        iv = int(value)
    except Exception:
        iv = 0
    return f"0x{iv & 0xFFFF:04X}"

def clean_item_name(name, item):
    """Remove ONLY the leading amount if it matches the item's Amount property, e.g., '3 Blue Diamond' -> 'Blue Diamond'."""
    if not name:
        return name
    n = str(name)
    try:
        amt = int(getattr(item, 'Amount', 0))
    except Exception:
        amt = 0
    if amt > 0:
        prefix = f"{amt} "
        if n.startswith(prefix):
            n = n[len(prefix):]
    return n.strip()

def format_item_entry(item):
    """Format item properties into a readable string."""
    debug_msg("Formatting item entry...")
    
    if not item:
        debug_msg("Error: No item provided!", 33)
        return None

    # Get name from properties first
    props = Items.GetPropStringList(item)
    name = "Unknown"
    if props and len(props) > 0:
        name = props[0]  # First property is usually the name
    name = clean_item_name(name, item)
    
    entry = {
        "name": name,
        "itemID": format_hex(item.ItemID),
        "hue": format_hex(int(item.Hue)),
        "properties": []
    }
    
    debug_msg(f"Basic item info: {entry['name']} ({entry['itemID']}, hue {entry['hue']})")
    
    # Convert properties to regular list
    if props:
        entry["properties"] = [str(prop) for prop in props]
        debug_msg(f"Found {len(props)} properties: {entry['properties']}")
    else:
        debug_msg("No properties found")
    
    return entry

# ======================== UI Helper Functions ========================

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

def _resolve_button_style():
    """Resolve the selected style into art id and button dimensions."""
    try:
        art_id, w, h = BUTTON_STYLE_MAP.get(BUTTON_STYLE, BUTTON_STYLE_MAP.get("small"))
    except Exception:
        art_id, w, h = (2443, 63, 23)
    globals()["BUTTON_ART_ID"] = art_id
    if SIZE_FROM_ART:
        try:
            globals()["BUTTON_WIDTH"] = int(w)
            globals()["BUTTON_HEIGHT"] = int(h)
        except Exception:
            pass

def _compute_layout(num_buttons):
    """Compute columns/rows and overall gump size based on layout toggles."""
    if VERTICAL_ONLY or not num_buttons:
        cols = 1
        rows = max(1, num_buttons)
    elif USE_ASPECT_PACKING:
        target_w_px = max(1, int(TARGET_GUMP_WIDTH_RATIO * BUTTON_WIDTH))
        target_h_px = max(1, int(TARGET_GUMP_HEIGHT_RATIO * BUTTON_HEIGHT))
        max_cols = max(1, int(target_w_px // max(1, BUTTON_WIDTH)))
        max_rows = max(1, int(target_h_px // max(1, BUTTON_HEIGHT)))
        cols = min(max_cols, num_buttons)
        rows = (num_buttons + cols - 1) // cols
        if rows > max_rows:
            cols = (num_buttons + max_rows - 1) // max_rows
            cols = max(1, min(cols, max_cols))
            rows = (num_buttons + cols - 1) // cols
    else:
        cols = 1
        rows = max(1, num_buttons)
    gump_w = max(PANEL_WIDTH_MIN, cols * BUTTON_WIDTH + (cols - 1) * BUTTON_GAP_X)
    content_h = rows * BUTTON_HEIGHT + (rows - 1) * BUTTON_GAP_Y
    gump_h = max(PANEL_HEIGHT_MIN, content_h)
    return cols, rows, gump_w, gump_h

def write_item_entry(config, entry):
    """Write the item entry to the corresponding list file."""
    file_path = config["file"]
    debug_msg(f"z Writing to file: {file_path} (type: {type(file_path).__name__})")
    
    # Ensure directory exists
    ensure_directory(file_path)
    
    # Check if file exists and back it up if necessary
    if os.path.exists(file_path):
        debug_msg(f"File exists, backing up: {file_path}")
        backup_path = f"{file_path}.bak"
        shutil.copy(file_path, backup_path)
        debug_msg(f"Backup created: {backup_path}")
    
    # Read existing data or initialize an empty list
    try:
        debug_msg(f"Attempting to read file: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            debug_msg(f"File opened, reading data (type: {type(f).__name__})")
            data = json.load(f)
            debug_msg(f"Loaded existing data: {len(data)} entries (type: {type(data).__name__}, repr: {repr(data)})")
    except (ValueError, FileNotFoundError):
        debug_msg(f"Error reading file or no existing data, initializing empty list")
        data = []
        debug_msg(f"Initialized empty list (type: {type(data).__name__}, repr: {repr(data)})")
    
    # Append new entry and write to file
    debug_msg(f"Appending new entry to data (type: {type(entry).__name__}, repr: {repr(entry)})")
    data.append(entry)
    debug_msg(f"Updated data: {len(data)} entries (type: {type(data).__name__}, repr: {repr(data)})")
    
    try:
        debug_msg(f"Attempting to write data to file: {file_path}")
        with open(file_path, 'w', encoding='utf-8') as f:
            debug_msg(f"File opened, writing data (type: {type(data).__name__})")
            json.dump(data, f, indent=4)
            debug_msg(f"Successfully wrote {len(data)} entries to file")
            return True
    except Exception as e:
        debug_msg(f"Error writing to file: {str(e)}", 33)
        return False

def extract_all_items_in_container_to_file():
    """Prompt user to target a container, then export all contained items to a JSON file named by the container serial.

    Output path example: <script_dir>/../data/item_container_<serial>.json
    """
    debug_msg("Starting container extraction ...", 0x0099)

    # Prompt for container target
    try:
        Target.Cancel()
    except Exception:
        pass
    Misc.Pause(120)
    cont_serial = Target.PromptTarget("Select a CONTAINER to export its items")
    if cont_serial <= -1:
        debug_msg("Container target cancelled or invalid", 33)
        return False

    container = Items.FindBySerial(cont_serial)
    if not container:
        debug_msg(f"Could not find container by serial: {cont_serial}", 33)
        return False

    # Gather contents (direct children)
    try:
        contents = list(getattr(container, 'Contains', []) or [])
    except Exception:
        contents = []

    debug_msg(f"Container serial {cont_serial} has {len(contents)} direct items")

    entries = []
    for idx, it in enumerate(contents, 1):
        try:
            entry = format_item_entry(it)
            if entry:
                # Augment with source container serial for traceability
                entry["containerSerial"] = int(cont_serial)
                entries.append(entry)
        except Exception as e:
            debug_msg(f"Skipping item at index {idx} due to error: {e}", 33)
        Misc.Pause(10)

    # Build output file path using raw serial 
    out_file = os.path.join(BASE_PATH, f"item_container_{int(cont_serial)}.json")
    ensure_directory(out_file)

    try:
        with open(out_file, 'w', encoding='utf-8') as f:
            json.dump(entries, f, indent=4)
        debug_msg(f"Wrote {len(entries)} items to {out_file}", 0x0044)
        return True
    except Exception as e:
        debug_msg(f"Failed writing container export: {e}", 33)
        return False

def try_repair_ndjson(file_path):
    """Attempt to repair a legacy NDJSON/JSONL file into a valid JSON array."""
    objects = []
    try:
        debug_msg(f"Attempting to read file: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            debug_msg(f"File opened, reading lines (type: {type(f).__name__})")
            lines = [line.strip() for line in f if line.strip()]
            buffer = ""
            brace_count = 0
            for line in lines:
                brace_count += line.count("{") - line.count("}")
                buffer += line
                if brace_count == 0 and buffer:
                    try:
                        debug_msg(f"Attempting to parse JSON from buffer (type: {type(buffer).__name__}, repr: {repr(buffer)})")
                        obj = json.loads(buffer)
                        debug_msg(f"Parsed JSON object (type: {type(obj).__name__}, repr: {repr(obj)})")
                        objects.append(obj)
                    except Exception as e:
                        debug_msg(f"Skipping invalid NDJSON block: {buffer}", 33)
                    buffer = ""
                else:
                    buffer += "\n"
        return objects if objects else None
    except Exception as e:
        debug_msg(f"NDJSON repair failed: {str(e)}", 33)
        return None

def target_and_record(config):
    """Target an item and record its properties."""
    debug_msg(f"Starting target selection for {config['name']}...")
    
    # Prompt for target
    Target.Cancel()  # Cancel any existing target
    Misc.Pause(100)  # Small pause before new target
    
    target_id = Target.PromptTarget("Select an item to add to " + config['name'])
    
    if target_id > -1:  # Valid target selected
        debug_msg(f"Target selected: {target_id}")
        item = Items.FindBySerial(target_id)
        
        if item:
            props = Items.GetPropStringList(item)
            name = "Unknown"
            if props and len(props) > 0:
                name = props[0]
            debug_msg(f"Found item: {name}")
            
            entry = format_item_entry(item)
            if entry:
                return write_item_entry(config, entry)
        else:
            debug_msg("Error: Could not find targeted item!", 33)
    else:
        debug_msg("Target cancelled or invalid", 33)
    
    return False

def test_target_selection(config):
    """Test the target selection system directly."""
    debug_msg(f"Testing target selection for: {config['name']}")
    result = target_and_record(config)
    debug_msg(f"Target test {'succeeded' if result else 'failed'}", 90 if result else 33)
    return result

def sendCategoryGump():
    """Build and send the standardized item category UI gump."""
    debug_msg("Creating category gump...")
    _resolve_button_style()

    clickable_configs = list(list_configs)
    # +1 for special Extract All Items in Container button
    num_buttons = len(clickable_configs) + 1
    layout_cols, _layout_rows, gump_w, gump_h = _compute_layout(num_buttons)
    # Include header bar height
    gump_h = max(HEADER_HEIGHT, gump_h + HEADER_HEIGHT)

    gd = Gumps.CreateGump(movable=True)
    Gumps.AddPage(gd, 0)

    # Background
    Gumps.AddBackground(gd, 0, 0, gump_w, gump_h, 30546)
    Gumps.AddAlphaRegion(gd, 0, 0, gump_w, gump_h)

    # Header (draggable area)
    try:
        Gumps.AddHtml(gd, 4, 2, max(0, gump_w - 8), HEADER_HEIGHT-2, f"<center><basefont color=#{HEADER_COLOR_HTML}>{HEADER_TEXT}</basefont></center>", 0, 0)
    except Exception:
        pass

    # Render category buttons
    current_row = 0
    current_col = 0
    for idx, config in enumerate(clickable_configs, 1):
        button_x = current_col * (BUTTON_WIDTH + BUTTON_GAP_X)
        button_y = HEADER_HEIGHT + current_row * (BUTTON_HEIGHT + BUTTON_GAP_Y)
        button_id = idx

        # Button art
        try:
            Gumps.AddButton(gd, button_x, button_y, BUTTON_ART_ID, BUTTON_ART_ID, button_id, 1, 0)
        except Exception:
            Gumps.AddButton(gd, button_x, button_y, 4005, 4006, button_id, 1, 0)

        # Optional dark overlay for readability
        if SLIVER_OVERLAY_ENABLED:
            try:
                if SLIVER_OVERLAY_MODE == "full":
                    Gumps.AddImageTiled(gd, button_x, button_y, BUTTON_WIDTH, BUTTON_HEIGHT, SLIVER_OVERLAY_TILE_ART_ID)
                else:
                    stripe_h = max(1, int(SLIVER_STRIPE_HEIGHT))
                    Gumps.AddImageTiled(gd, button_x, button_y, BUTTON_WIDTH, min(stripe_h, BUTTON_HEIGHT), SLIVER_OVERLAY_TILE_ART_ID)
                    bottom_y = button_y + max(0, BUTTON_HEIGHT - stripe_h)
                    Gumps.AddImageTiled(gd, button_x, bottom_y, BUTTON_WIDTH, min(stripe_h, BUTTON_HEIGHT), SLIVER_OVERLAY_TILE_ART_ID)
            except Exception:
                pass

        # Label and sublabel (description)
        add_centered_label_with_outline(gd, button_x, button_y, BUTTON_WIDTH, BUTTON_HEIGHT, str(config.get("name", "")), FONT_HUE)

        # Advance grid position
        current_col += 1
        if current_col >= max(1, layout_cols):
            current_col = 0
            current_row += 1

    # Add the special Extract All Items in Container button as the final button
    button_x = current_col * (BUTTON_WIDTH + BUTTON_GAP_X)
    button_y = HEADER_HEIGHT + current_row * (BUTTON_HEIGHT + BUTTON_GAP_Y)
    special_button_id = len(clickable_configs) + 1
    try:
        Gumps.AddButton(gd, button_x, button_y, BUTTON_ART_ID, BUTTON_ART_ID, special_button_id, 1, 0)
    except Exception:
        Gumps.AddButton(gd, button_x, button_y, 4005, 4006, special_button_id, 1, 0)
    if SLIVER_OVERLAY_ENABLED:
        try:
            if SLIVER_OVERLAY_MODE == "full":
                Gumps.AddImageTiled(gd, button_x, button_y, BUTTON_WIDTH, BUTTON_HEIGHT, SLIVER_OVERLAY_TILE_ART_ID)
            else:
                stripe_h = max(1, int(SLIVER_STRIPE_HEIGHT))
                Gumps.AddImageTiled(gd, button_x, button_y, BUTTON_WIDTH, min(stripe_h, BUTTON_HEIGHT), SLIVER_OVERLAY_TILE_ART_ID)
                bottom_y = button_y + max(0, BUTTON_HEIGHT - stripe_h)
                Gumps.AddImageTiled(gd, button_x, bottom_y, BUTTON_WIDTH, min(stripe_h, BUTTON_HEIGHT), SLIVER_OVERLAY_TILE_ART_ID)
        except Exception:
            pass
    add_centered_label_with_outline(gd, button_x, button_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Extract All Items in Container", FONT_HUE)

    Gumps.SendGump(GUMP_ID, Player.Serial, GUMP_START_X, GUMP_START_Y, gd.gumpDefinition, gd.gumpStrings)
    # Mark the time we refreshed/sent the gump
    global _LAST_REFRESH_TS
    _LAST_REFRESH_TS = time.time()

def processCategoryInput():
    """Poll for gump interactions, handle category clicks with debounce, then refresh UI."""
    clickable_configs = list(list_configs)

    Gumps.WaitForGump(GUMP_ID, 500)
    gump_data = Gumps.GetGumpData(GUMP_ID)
    if not gump_data:
        # If the gump is missing and we didn't just refresh it ourselves,
        # treat this as user closed (right-click) and stop the script.
        if (time.time() - _LAST_REFRESH_TS) > 0.9:
            return True
        return False

    button_identifier = int(getattr(gump_data, 'buttonid', 0))

    # Debounce to prevent duplicate triggers during refresh
    global _LAST_CLICK_BID, _LAST_CLICK_TS
    now_ts = time.time()
    if button_identifier > 0 and button_identifier == _LAST_CLICK_BID and (now_ts - _LAST_CLICK_TS) < 0.8:
        return False

    if 1 <= button_identifier <= len(clickable_configs):
        config = clickable_configs[button_identifier - 1]
        try:
            _LAST_CLICK_BID = button_identifier
            _LAST_CLICK_TS = now_ts
            debug_msg(f"Selected category: {config['name']}")
            target_and_record(config)
        except Exception as e:
            debug_msg(f"Category action error: {e}", 33)

        # Refresh UI
        try:
            Gumps.CloseGump(GUMP_ID)
        except Exception:
            pass
        sendCategoryGump()
    elif button_identifier == (len(clickable_configs) + 1):
        # Special Extract All Items in Container action
        try:
            _LAST_CLICK_BID = button_identifier
            _LAST_CLICK_TS = now_ts
            debug_msg("Selected: Extract All Items in Container")
            extract_all_items_in_container_to_file()
        except Exception as e:
            debug_msg(f"Extract All Items in Container error: {e}", 33)

        # Refresh UI
        try:
            Gumps.CloseGump(GUMP_ID)
        except Exception:
            pass
        sendCategoryGump()

    return False

def main():
    global UI_ACTIVE

    debug_msg("Starting Item List Developer...")

    # Test specific list if specified
    if DEBUG["TEST_SPECIFIC_LIST"]:
        config = next((config for config in list_configs if config["name"] == DEBUG["TEST_SPECIFIC_LIST"]), None)
        if config:
            debug_msg(f"Testing specific list: {config['name']}")
            test_target_selection(config)
            return
        else:
            debug_msg(f"List not found: {DEBUG['TEST_SPECIFIC_LIST']}", 33)
            return

    # Test targeting system only
    if DEBUG["TEST_TARGET"]:
        debug_msg("Testing target selection system...")
        test_target_selection(list_configs[0])  # Use first list for testing
        return

    # Skip UI if specified
    if DEBUG["SKIP_UI"]:
        debug_msg("Skipping UI creation...")
        return

    # Normal UI operation
    UI_ACTIVE = True

    # Initially send the standardized gump
    sendCategoryGump()
    debug_msg("Initial category gump created")

    # Main loop using debounced input pattern
    done = False
    while Player.Connected and not done:
        done = processCategoryInput()
        Misc.Pause(100)

    debug_msg("Item List Developer closed.")

def debug_msg(message, color=90):
    """Send a debug message if verbose logging is enabled."""
    if DEBUG["VERBOSE_LOGGING"]:
        Misc.SendMessage(f"[DEV_ITEM_TO_LIST] {message}", color)

if __name__ == "__main__":
    main()
