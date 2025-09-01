"""
Development Mobile to JSON List - a Razor Enhanced Python Script for Ultima Online

Creates a gump UI for targeting a mobile/creature/NPC
and exporting its details to categorized .json files.

Categories:
Boss , Quest , Tameable , Monster , Friend , Enemy

Exported .json files are stored in a 'data' subdirectory next to the script.

VERSION::20250829
"""
import os
import json
import shutil

UI_ACTIVE = True
UI_POSITION_X = 420
UI_POSITION_Y = 420

# Big unique gump id 
GUMP_ID = 3469664363

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

# Track current gump ID
current_gump_id = None


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

    Target.PromptTarget("Select a mobile to add to " + config["name"])
    target_id = Target.PromptTarget()

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


def send_gump():
    """Build and send the mobile list developer UI gump."""
    debug_msg("Creating mobile gump...")

    gd = Gumps.CreateGump(movable=True)
    Gumps.AddPage(gd, 0)

    # Dimensions (compact vertical layout like the item version)
    width = 320
    row_height = 40
    top_pad = 40
    bottom_pad = 20
    height = (len(list_configs) * row_height) + top_pad + bottom_pad

    # Background
    Gumps.AddBackground(gd, 0, 0, width, height, 30546)
    Gumps.AddAlphaRegion(gd, 0, 0, width, height)

    # Title
    Gumps.AddHtml(
        gd,
        20,
        14,
        width - 40,
        20,
        "<center><basefont color=#FFFFFF>Mobile List Developer</basefont></center>",
        0,
        0,
    )

    # Close
    Gumps.AddButton(gd, width - 25, 5, 4017, 4018, 99, 1, 0)
    Gumps.AddTooltip(gd, r"Close")

    # Buttons
    y_offset = top_pad
    for idx, config in enumerate(list_configs, 1):
        Gumps.AddButton(gd, 20, y_offset + 2, 4006, 4007, idx, 1, 0)
        Gumps.AddHtml(
            gd,
            50,
            y_offset,
            width - 70,
            16,
            f"<basefont color=#FFFFFF>{config['name']}</basefont>",
            0,
            0,
        )
        Gumps.AddHtml(
            gd,
            50,
            y_offset + 14,
            width - 70,
            16,
            f"<basefont color=#999999><i>{config['description']}</i></basefont>",
            0,
            0,
        )
        y_offset += row_height

    # Send gump
    Gumps.SendGump(GUMP_ID, Player.Serial, UI_POSITION_X, UI_POSITION_Y, gd.gumpDefinition, gd.gumpStrings)


def process_gump_input():
    """Process input from the gump."""
    global UI_ACTIVE

    Gumps.WaitForGump(GUMP_ID, 500)
    gd = Gumps.GetGumpData(GUMP_ID)
    if not gd:
        return

    if gd.buttonid > 0:
        debug_msg(f"Button {gd.buttonid} pressed")

        if gd.buttonid == 99:
            debug_msg("Close button pressed")
            UI_ACTIVE = False
            return

        # Find the selected category
        for idx, config in enumerate(list_configs, 1):
            if gd.buttonid == idx:
                debug_msg(f"Selected list: {config['name']}")
                target_and_record(config)
                send_gump()  # Reopen after operation
                break


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
    send_gump()
    debug_msg("Initial gump created")

    while UI_ACTIVE:
        Misc.Pause(50)
        process_gump_input()

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