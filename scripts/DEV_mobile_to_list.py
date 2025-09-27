"""
Development Mobile to JSON List  - a Razor Enhanced Python Script for Ultima Online

Creates a gump UI for selecting mobiles (creatures/NPCs)
and exporting their details to categorized .json files.

Categories:
Boss , Quest , Tameable , Monster , Friend , Enemy

Exported .json files are stored in a 'data' subdirectory next to the script.

VERSION::20250923
"""
import os
import json
import shutil
import time

UI_ACTIVE = True
GUMP_START_X = 420
GUMP_START_Y = 420

# Big unique gump id
GUMP_ID = 3469664363

# ========================
# Standardized UI Settings
# ========================
# Adopted from DEV_item_to_list.py for consistent look/feel.

# Style selection and layout
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
HEADER_TEXT = "_____  M O B I L E  L I S T S  _____"
HEADER_COLOR_HTML = "BBBBBB"  # grey

# Base path for data files (a 'data' folder adjacent to scripts)
BASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")

# Debug toggles
DEBUG = {
    "SKIP_UI": False,           # Skip creating the UI completely
    "TEST_TARGET": False,       # Test only the targeting system
    "TEST_SPECIFIC_LIST": "",   # Test a specific list (e.g., "Boss")
    "VERBOSE_LOGGING": True,    # Enable detailed debug messages
}

# List definitions with file paths
list_configs = [
    {
        "name": "Boss",
        "file": os.path.join(BASE_PATH, "mobiles_boss.json"),
        "description": "High-threat bosses and raid targets",
    },
    {
        "name": "Quest",
        "file": os.path.join(BASE_PATH, "mobiles_quest.json"),
        "description": "Quest-related mobiles",
    },
    {
        "name": "Tameable",
        "file": os.path.join(BASE_PATH, "mobiles_tameable.json"),
        "description": "Animals or creatures intended to be tamed",
    },
    {
        "name": "Monster",
        "file": os.path.join(BASE_PATH, "mobiles_monster.json"),
        "description": "General enemies and mobs",
    },
    {
        "name": "Friend",
        "file": os.path.join(BASE_PATH, "mobiles_friend.json"),
        "description": "Allies, friendlies, or party members",
    },
    {
        "name": "Enemy",
        "file": os.path.join(BASE_PATH, "mobiles_enemy.json"),
        "description": "Hostiles or PvP enemies",
    },
]

# Track current gump ID and last refresh time
current_gump_id = None
_LAST_REFRESH_TS = 0.0

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

def clean_mobile_name(name):
    """Clean/normalize a mobile's name."""
    if not name:
        return "Unknown"
    return str(name).strip()

def get_mobile_properties_list(mobile):
    """
    Retrieve a list of property strings for the given mobile.
    Uses Mobiles.GetPropStringList(mobile) when available; falls back gracefully.
    """
    try:
        props = Mobiles.GetPropStringList(mobile)
        if props:
            return [str(p) for p in props]
    except Exception:
        pass
    # Fallback: synthesize a minimal property list from known attributes
    props = []
    try:
        nm = getattr(mobile, "Name", None)
        if nm:
            props.append(str(nm))
    except Exception:
        pass
    try:
        hits = getattr(mobile, "Hits", None)
        if hits is not None:
            props.append(f"Hits: {int(hits)}")
    except Exception:
        pass
    try:
        notor = getattr(mobile, "Notoriety", None)
        if notor is not None:
            props.append(f"Notoriety: {int(notor)}")
    except Exception:
        pass
    return props

def format_mobile_entry(mobile):
    """Format mobile properties into a readable JSON-friendly dict."""
    debug_msg("Formatting mobile entry...")

    if not mobile:
        debug_msg("Error: No mobile provided!", 33)
        return None

    props = get_mobile_properties_list(mobile)

    # Name: first property is usually the display name if props exist
    name = "Unknown"
    if props and len(props) > 0:
        name = props[0]
    name = clean_mobile_name(name)

    # Extract safe attributes with getattr fallbacks
    serial = getattr(mobile, "Serial", 0)
    hue = getattr(mobile, "Hue", 0)
    body = getattr(mobile, "Body", 0)
    pos = getattr(mobile, "Position", None)
    pos_x = getattr(pos, "X", None) if pos is not None else None
    pos_y = getattr(pos, "Y", None) if pos is not None else None
    hits = getattr(mobile, "Hits", None)
    notoriety = getattr(mobile, "Notoriety", None)
    is_human = getattr(mobile, "IsHuman", None)
    is_paragon = getattr(mobile, "Paragon", None)

    entry = {
        "name": name,
        "serial": str(serial),
        "hue": format_hex(int(hue)),
        "bodyID": format_hex(int(body)),
        "hits": int(hits) if isinstance(hits, (int, float)) else None,
        "notoriety": int(notoriety) if isinstance(notoriety, (int, float)) else None,
        "isHuman": bool(is_human) if isinstance(is_human, bool) else None,
        "isParagon": bool(is_paragon) if isinstance(is_paragon, bool) else None,
        "position": {
            "x": int(pos_x) if isinstance(pos_x, (int, float)) else None,
            "y": int(pos_y) if isinstance(pos_y, (int, float)) else None,
        },
        "properties": props or [],
    }

    debug_msg(
        f"Mobile info: {entry['name']} (Serial {entry['serial']}, body {entry['bodyID']}, hue {entry['hue']})"
    )

    return entry

def write_mobile_entry(config, entry):
    """Write the mobile entry to the corresponding list file."""
    file_path = config["file"]
    debug_msg(f"Writing to file: {file_path}")

    # Ensure directory exists
    ensure_directory(file_path)

    # Backup current file (if exists)
    if os.path.exists(file_path):
        debug_msg(f"File exists, backing up: {file_path}")
        backup_path = f"{file_path}.bak"
        shutil.copy(file_path, backup_path)
        debug_msg(f"Backup created: {backup_path}")

    # Load existing or create new list
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, list):
                debug_msg("Invalid JSON root (not a list). Reinitializing.", 33)
                data = []
    except (ValueError, FileNotFoundError):
        debug_msg("No existing data or invalid JSON; starting new list")
        data = []

    data.append(entry)

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        debug_msg(f"Successfully wrote {len(data)} entries to file")
        return True
    except Exception as e:
        debug_msg(f"Error writing to file: {str(e)}", 33)
        return False

def target_and_record(config):
    """Target a mobile and record its properties."""
    debug_msg(f"Starting mobile target selection for {config['name']}...")

    # Prompt for target (cancel old first)
    Target.Cancel()
    Misc.Pause(100)

    # Prompt for target with single PromptTarget call that returns serial
    target_id = Target.PromptTarget("Select a mobile to add to " + config["name"])

    if target_id > -1:
        debug_msg(f"Target selected: {target_id}")
        mobile = Mobiles.FindBySerial(target_id)

        if mobile:
            entry = format_mobile_entry(mobile)
            if entry:
                return write_mobile_entry(config, entry)
            else:
                debug_msg("Error creating entry from mobile", 33)
        else:
            debug_msg("Error: Could not find targeted mobile!", 33)
    else:
        debug_msg("Target cancelled or invalid", 33)

    return False

def test_target_selection(config):
    """Test the target selection system directly."""
    debug_msg(f"Testing mobile target selection for: {config['name']}")
    result = target_and_record(config)
    debug_msg(f"Target test {'succeeded' if result else 'failed'}", 90 if result else 33)
    return result

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

def sendCategoryGump():
    """Build and send the standardized mobile category UI gump."""
    debug_msg("Creating category gump...")
    _resolve_button_style()

    clickable_configs = list(list_configs)
    num_buttons = len(clickable_configs)
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

        # Label
        add_centered_label_with_outline(gd, button_x, button_y, BUTTON_WIDTH, BUTTON_HEIGHT, str(config.get("name", "")), FONT_HUE)

        # Advance grid position
        current_col += 1
        if current_col >= max(1, layout_cols):
            current_col = 0
            current_row += 1

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

    return False

def main():
    global UI_ACTIVE

    debug_msg("Starting Mobile List Developer...")

    if DEBUG["TEST_SPECIFIC_LIST"]:
        config = next((c for c in list_configs if c["name"] == DEBUG["TEST_SPECIFIC_LIST"]), None)
        if config:
            debug_msg(f"Testing specific list: {config['name']}")
            test_target_selection(config)
            return
        else:
            debug_msg(f"List not found: {DEBUG['TEST_SPECIFIC_LIST']}", 33)
            return

    if DEBUG["TEST_TARGET"]:
        debug_msg("Testing target selection system...")
        test_target_selection(list_configs[0])
        return

    if DEBUG["SKIP_UI"]:
        debug_msg("Skipping UI creation...")
        return

    UI_ACTIVE = True
    # Initially send the standardized gump
    sendCategoryGump()
    debug_msg("Initial category gump created")

    # Main loop using debounced input pattern
    done = False
    while Player.Connected and not done:
        done = processCategoryInput()
        Misc.Pause(100)

    debug_msg("Mobile List Developer closed.")

def debug_msg(message, color=90):
    """Send a debug message if verbose logging is enabled."""
    if DEBUG["VERBOSE_LOGGING"]:
        try:
            Misc.SendMessage(f"[DEV_MOBILE_TO_LIST] {message}", color)
        except Exception:
            # If not in-game, ignore SendMessage failures
            pass


if __name__ == "__main__":
    main()