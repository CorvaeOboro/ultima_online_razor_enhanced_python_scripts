"""
Development Item to JSON List  - a Razor Enhanced Python Script for Ultima Online

Creates a gump UI for selecting items 
exporting their details to categorized .json files.

Categories:
Trash , Bank , Salvage , Keep , Quest ,
 Food , Update , Orb , Ritual

this is useful to store item ids for use in other scripts 
exported .json files are stored in a 'data' subdirectory next to the script

VERSION::20250722
"""
import os
import json
import shutil
import time

UI_ACTIVE = True
UI_POSITION_X = 400
UI_POSITION_Y = 400

# gump ID= 4294967295  = the max value , randomly select a high number gump so its unique
GUMP_ID =  3429654321

# Base path for data files (set dynamically to a 'data' subdirectory next to the script)
BASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")

# Debug toggles
DEBUG = {
    "SKIP_UI": False,           # Skip creating the UI completely
    "TEST_TARGET": False,       # Test only the targeting system
    "TEST_SPECIFIC_LIST": "",   # Test a specific list (e.g., "Bank Items")
    "VERBOSE_LOGGING": True,    # Enable detailed debug messages
}

# List definitions with file paths
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
]

# Track the current gump ID
current_gump_id = None

def ensure_directory(file_path):
    """Ensure the directory exists for the given file path."""
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        debug_msg(f"Creating directory: {directory}")
        os.makedirs(directory)

def format_item_entry(item):
    """Format item properties into a readable string."""
    debug_msg("Formatting item entry...")
    
    if not item:
        debug_msg("Error: No item provided!", 33)
        return None
        
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    
    # Get name from properties first
    props = Items.GetPropStringList(item)
    name = "Unknown"
    if props and len(props) > 0:
        name = props[0]  # First property is usually the name
    
    entry = {
        "timestamp": timestamp,
        "name": name,
        "itemID": hex(item.ItemID),
        "serial": hex(item.Serial),
        "hue": int(item.Hue),  # Explicitly cast to int
        "properties": []
    }
    
    debug_msg(f"Basic item info: {entry['name']} ({entry['itemID']})")
    debug_msg(f"Hue type: {type(item.Hue)}")  # Log type of item.Hue
    
    # Convert properties to regular list
    if props:
        entry["properties"] = [str(prop) for prop in props]
        debug_msg(f"Found {len(props)} properties: {entry['properties']}")
    else:
        debug_msg("No properties found")
    
    return entry

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
    
    Target.PromptTarget("Select an item to add to " + config['name'])
    target_id = Target.PromptTarget()
    
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

def send_gump():
    """Build and send the item list developer UI gump."""
    debug_msg("Creating gump...")
    
    gd = Gumps.CreateGump(movable=True)
    Gumps.AddPage(gd, 0)
    
    # Calculate dimensions
    width = 300
    height = (len(list_configs) * 60) + 60
    
    # Background
    Gumps.AddBackground(gd, 0, 0, width, height, 30546)
    Gumps.AddAlphaRegion(gd, 0, 0, width, height)
    
    # Title
    Gumps.AddHtml(gd, 20, 20, width-40, 20, "<center><basefont color=#FFFFFF>Item List Developer</basefont></center>", 0, 0)
    
    # Close button
    Gumps.AddButton(gd, width-25, 5, 4017, 4018, 99, 1, 0)
    Gumps.AddTooltip(gd, r"Close")
    
    # List buttons
    y_offset = 50
    for idx, config in enumerate(list_configs, 1):
        # Main button
        Gumps.AddButton(gd, 20, y_offset, 4006, 4007, idx, 1, 0)
        Gumps.AddHtml(gd, 50, y_offset, width-70, 20, 
                      f"<basefont color=#FFFFFF>{config['name']}</basefont>", 0, 0)
        # Description
        Gumps.AddHtml(gd, 50, y_offset+20, width-70, 20,
                      f"<basefont color=#999999><i>{config['description']}</i></basefont>", 0, 0)
        y_offset += 60

    # Send gump
    Gumps.SendGump(GUMP_ID, Player.Serial, UI_POSITION_X, UI_POSITION_Y, gd.gumpDefinition, gd.gumpStrings)

def process_gump_input():
    """Process input from the gump."""
    global UI_ACTIVE
    
    Gumps.WaitForGump(GUMP_ID, 500)
    gd = Gumps.GetGumpData(GUMP_ID)
    if not gd:
        return
        
    if gd.buttonid > 0:  # Button was pressed
        debug_msg(f"Button {gd.buttonid} pressed")
        
        if gd.buttonid == 99:  # Close button
            debug_msg("Close button pressed")
            UI_ACTIVE = False
            return
            
        # Find and process the corresponding list
        for idx, config in enumerate(list_configs, 1):
            if gd.buttonid == idx:
                debug_msg(f"Selected list: {config['name']}")
                target_and_record(config)  # Do targeting and recording
                send_gump()  # Recreate gump after function completes
                break

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
    
    # Initially send the gump
    send_gump()
    debug_msg("Initial gump created")
        
    # Main loop
    while UI_ACTIVE:
        Misc.Pause(50)  # Small pause to reduce CPU usage
        process_gump_input()
    
    debug_msg("Item List Developer closed.")

def debug_msg(message, color=90):
    """Send a debug message if verbose logging is enabled."""
    if DEBUG["VERBOSE_LOGGING"]:
        Misc.SendMessage(f"[DEV_ITEM_TO_LIST] {message}", color)

if __name__ == "__main__":
    main()
