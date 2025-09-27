"""
Quest Item Turn In - a Razor Enhanced Python Script for Ultima Online

Turn in Items to Quest NPC , Searches for quest items in inventory and gives them to specific NPC
for example : Daemon Bones to Canute , Ancient Vases to Sasha , Strange Eggs to Wellen 

TODO:
- restore the orb , treasure map , and paragon turn in to griphook when returns

HOTKEY:: K ( Kwuest )
VERSION:: 20250926
"""
DEBUG_MODE = True

# Quest Configurations

QUESTS_DUNGEON_SANDSTORM = {
        "ancient_vase": {
        "name": "Sandstorm Ancient Vase",
        "description": "Turn in archaeologically recovered ancient vases to Sasha in Sandstorm.",
        "category": "event",
        "region": "sandstorm",
        "locations": [
            {
                "name": "Sasha the archaeologist (Sandstorm)",
                "x": 1835,
                "y": 944,
                "z": 1,
                "npc_serial": 0x00003767
            }
        ],
        "items": [
            {"name": "Vase", "id": 0xB834, "hue": -1},
            {"name": "Vase", "id": 0xB836, "hue": -1},
            {"name": "Vase", "id": 0xB837, "hue": -1},
            {"name": "Vase", "id": 0xB838, "hue": -1},
            {"name": "Vase", "id": 0xB835, "hue": -1},
            {"name": "Vase", "id": 0xB839, "hue": -1}
        ],
        "turn_in_type": "direct_transfer",
        "container_type": "npc"
    }
}

QUESTS_DUNGEON_SHAME = {
    "dungeon_shame_cocoon_eggs": {
        "name": "Dungeon Shame Cocoon Eggs",
        "description": "Collect Strange Eggs from cocoons and turn in to Wellen the entomologist in Shame.",
        "category": "region",
        "region": "shame",
        "locations": [
            {
                "name": "Wellen the entomologist",
                "x": 505,
                "y": 1570,
                "z": 0,
                "npc_serial": 0x0000130C
            }
        ],
        "items": [
            {"name": "Strange Egg", "id": 0x10D9, "hue": -1}
        ],
        "turn_in_type": "direct_transfer",
        "container_type": "npc"
    },
    "daily_shame_vermin_blood": {
        "name": "Daily: Collect Vermin Blood",
        "description": "Use Blood Vial Kit on nearby corpses of vermin, bugs, spiders, bees; turn in blood to Canute (Daily Quest Giver).",
        "category": "daily",
        "region": "shame",
        "tool": {"name": "Blood Vial Kit", "id": 0xBB33},
        "targets": ["vermin corpse", "bug corpse", "spider corpse", "bee corpse"],
        "locations": [
            {
                "name": "Canute the Daily Quest Giver",
                "x": 1433,
                "y": 1710,
                "z": 31,
                "npc_serial": 0x000000D4
            }
        ],
        "items": [
            {"name": "Vermin Blood", "id": 0x0E24, "hue": 0x09AF}
        ],
        "turn_in_type": "direct_transfer",
        "container_type": "npc"
    }
}

QUESTS_DUNGEON_DECEIT = {
    "daily_deceit_daemon_bone": {
        "name": "Daily: Collect Daemon Bone",
        "description": "Gather Daemon Bone in Deceit and turn in to Canute the Daily Quest Master.",
        "category": "daily",
        "region": "deceit",
        "locations": [
            {
                "name": "Canute The Daily Quest Master",
                "x": 1433,
                "y": 1710,
                "z": 31,
                "npc_serial": 0x000000D4,
                "mobile_id": 0x0190
            }
        ],
        "items": [
            {"name": "Daemon Bone", "id": 0x0F7E, "hue": 0x0B20}
        ],
        "turn_in_type": "direct_transfer",
        "container_type": "npc"
    }
}

QUESTS_DUNGEON_DESTARD = {
    "daily_destard_moltendust": {
        "name": "Daily: Moltendust",
        "description": "Collect Moltendust in Destard and turn in to the daily quest giver.",
        "category": "daily",
        "region": "destard",
        "locations": [
            {
                "name": "Canute",
                "x": 1433,
                "y": 1710,
                "z": 31,
                "npc_serial": 0x000000D4
            }
        ],
        "items": [
            {"name": "Moltendust", "id": 0xB8B1, "hue": 0x093D}
        ],
        "turn_in_type": "direct_transfer",
        "container_type": "npc"
    }
}

# currently disabled
QUESTS_GRIPHOOK_GENERAL_DISABLED = {
    "treasure_maps": {
        "name": "Treasure Map Turn-in",
        "description": "Turn in treasure maps via bank NPC gump.",
        "category": "general",
        "region": "britannia",
        "locations": [
            {
                "name": "Luna Bank",
                "x": 1424,
                "y": 1688,
                "z": 20,
                "npc_serial": 0x00003DEC
            },
            {
                "name": "Britain Bank",
                "x": 1424,
                "y": 1693,
                "z": 0,
                "npc_serial": 0x00003DEC
            }
        ],
        "items": [
            {"name": "Treasure Map", "id": 0x14EC, "hue": -1},
            {"name": "Treasure Map", "id": 0x14ED, "hue": -1},
            {"name": "Treasure Map", "id": 0x14EE, "hue": -1},
            {"name": "Treasure Map", "id": 0x14EF, "hue": -1},
            {"name": "Treasure Map", "id": 0x352E, "hue": -1},
            {"name": "Treasure Map", "id": 0x2AAA, "hue": -1},
            {"name": "Treasure Map", "id": 0x2AAB, "hue": -1}
        ],
        "turn_in_type": "gump",
        "gump_id": 1889568190,
        "turn_in_action": 1
    },
    "rare_dyes": {
        "name": "Rare Dye Turn-in",
        "description": "Turn in rare and carpet dyes at Britain bank trader.",
        "category": "general",
        "region": "britannia",
        "locations": [
            {
                "name": "Britain Banks Dye Trader",
                "x": 1424,
                "y": 1693,
                "z": 0,
                "npc_serial": 0x00003DEC
            }
        ],
        "items": [
            {"name": "Rare Dye", "id": 0x0E2A, "hue": -1},
            {"name": "Rare Dye", "id": 0x0E2B, "hue": -1},
            {"name": "Rare Dye", "id": 0x0E25, "hue": -1},
            {"name": "Carpet Dye", "id": 0x7163, "hue": -1}
        ],
        "turn_in_type": "gump",
        "gump_id": 1889568190,
        "turn_in_action": 1
    },
    "empty_paragon_chest": {
        "name": "Empty Paragon Chest Turn-in",
        "description": "Turn in empty paragon chests via gump; validates chest is empty before turn-in.",
        "category": "general",
        "region": "britannia",
        "locations": [
            {
                "name": "Britain Bank Collector",
                "x": 1424,
                "y": 1693,
                "z": 0,
                "npc_serial": 0x00003DEC
            }
        ],
        "items": [
            {"name": "Empty Paragon Chest", "id": 0x0E40, "hue": -1},
            {"name": "Empty Paragon Chest", "id": 0x0E41, "hue": -1},
            {"name": "Greater Paragon Chest", "id": 0x09AB, "hue": -1},
            {"name": "a Paragon Chest", "id": 0x0E43, "hue": -1}
        ],
        "turn_in_type": "gump",
        "gump_id": 1889568190,
        "turn_in_action": 1,
        "validation": {
            "type": "empty_container",
            "message": "Checking if paragon chest is empty..."
        }
    },
}

# Combine all groups into a single QUESTS dictionary 
# currently excluding the QUESTS_GRIPHOOK_GENERAL_DISABLED , until NPC return
QUESTS = {}
for group in ( QUESTS_DUNGEON_SANDSTORM, QUESTS_DUNGEON_SHAME, QUESTS_DUNGEON_DECEIT, QUESTS_DUNGEON_DESTARD):
    QUESTS.update(group)

# Lastly , if not near any item turn in we try to attack specific quest objectives 
QUEST_STATICS_TO_ATTACK = ["A Coccon", "a bonfire crystal", "Demonic Portal","Poisonous Thorns"]
INTERACT_ONLY_STATICS = True  # When true, only interact with statics items  and do NOT attack mobiles

#//======================================================================

def debug_message(message, color=65):
    if DEBUG_MODE:
        Misc.SendMessage(f"[QUEST] {message}", color)

def custom_sqrt(x, epsilon=1e-7):
    """Compute the square root of x """
    if x < 0:
        raise ValueError('Cannot compute sqrt of negative number')
    guess = x / 2.0 if x > 1 else 1.0
    while abs(guess * guess - x) > epsilon:
        guess = (guess + x / guess) / 2.0
    return guess

def find_quest_items(quest_config):
    """Find all quest items in player's backpack for a specific quest."""
    items_found = {}
    
    for item_info in quest_config["items"]:
        items = Items.FindByID(item_info["id"], item_info["hue"], Player.Backpack.Serial)
        if items:
            if not isinstance(items, list):
                items = [items]
            items_found[item_info["id"]] = items
            debug_message(f"Found {len(items)} {item_info['name']}(s)!", 65)
    
    return items_found

def find_nearest_location(locations):
    """Find the nearest quest turn-in location to the player."""
    player_pos = {"x": Player.Position.X, "y": Player.Position.Y}
    nearest = None
    min_distance = float('inf')
    
    for location in locations:
        distance = calculate_distance(player_pos["x"], player_pos["y"], 
                                   location["x"], location["y"])
        if distance < min_distance:
            min_distance = distance
            nearest = location
    
    return nearest, min_distance

def is_within_range(x1, y1, x2, y2, range_tiles=3):
    """Check if two points are within specified range."""
    return abs(x1 - x2) <= range_tiles and abs(y1 - y2) <= range_tiles

def calculate_distance(x1, y1, x2, y2):
    """Calculate distance between two points."""
    return custom_sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def get_direction_to(current_x, current_y, target_x, target_y):
    """Get direction to move towards target."""
    dx = target_x - current_x
    dy = target_y - current_y
    
    # Determine primary direction
    if abs(dx) > abs(dy):
        return "East" if dx > 0 else "West"
    else:
        return "North" if dy < 0 else "South"

def move_to_location(target_x, target_y, target_z, max_distance=300):
    """Move to within range of target location."""
    attempts = 0
    max_attempts = 50  # Prevent infinite loop
    
    while not is_within_range(Player.Position.X, Player.Position.Y, target_x, target_y):
        direction = get_direction_to(Player.Position.X, Player.Position.Y, target_x, target_y)
        Player.Walk(direction)
        Misc.Pause(200)  # Short pause between steps
        
        attempts += 1
        if attempts >= max_attempts:
            debug_message("Could not reach location after maximum attempts!", 33)
            return False
            
        # Break if we're too far
        if calculate_distance(Player.Position.X, Player.Position.Y, target_x, target_y) > max_distance:
            debug_message("Too far from target location!", 33)
            return False
            
    return True

def handle_gump_turn_in(items, quest_config, location):
    """Handle turn-in through gump interface."""
    # First try to move to the NPC
    if not move_to_location(location["x"], location["y"], location["z"]):
        return False

    # Find the NPC
    npc = Mobiles.FindBySerial(location["npc_serial"])
    if not npc:
        debug_message(f"Cannot find NPC at {location['name']}!", 33)
        return False
        
    for item_list in items.values():
        for item in item_list:
            # Target the NPC first
            Mobiles.UseMobile(npc)
            Misc.Pause(1000)  # Increased pause to ensure NPC interaction is ready
            
            # Wait for gump
            if Gumps.WaitForGump(quest_config["gump_id"], 3000):  # Wait up to 3 seconds for gump
                Gumps.SendAction(quest_config["gump_id"], quest_config["turn_in_action"])
                Misc.Pause(1000)  # Wait for turn-in action
                
                # Wait for target cursor
                if Target.WaitForTarget(3000):  # Wait up to 3 seconds for target
                    Target.TargetExecute(item.Serial)  # Target the map
                    Misc.Pause(1500)  # Wait for turn-in to complete
                else:
                    debug_message("Target cursor not received!", 33)
            else:
                debug_message("Expected gump not received!", 33)
    
    # Close any remaining gumps
    Gumps.CloseGump(quest_config["gump_id"])
    return True

def handle_direct_transfer(items, quest_config, location):
    """Handle direct item transfer to NPC or container, with auto-navigation if out of range."""
    # Always attempt to move to the NPC location first
    if not move_to_location(location["x"], location["y"], location["z"]):
        debug_message(f"Failed to navigate to NPC at {location['name']} ({location['x']}, {location['y']}, {location['z']})!", 33)
        return False

    # Find the NPC
    npc = Mobiles.FindBySerial(location["npc_serial"])
    if not npc:
        debug_message(f"Cannot find NPC at {location['name']}!", 33)
        return False

    #  check distance to NPC and try to move closer if needed
    if hasattr(npc, 'Position'):
        dist = custom_sqrt((Player.Position.X - npc.Position.X) ** 2 + (Player.Position.Y - npc.Position.Y) ** 2)
        if dist > 2:  # If not close enough, try to move closer
            debug_message(f"Too far from NPC ({dist:.1f} tiles), moving closer...", 67)
            if not move_to_location(npc.Position.X, npc.Position.Y, npc.Position.Z):
                debug_message(f"Failed to move close enough to NPC at {npc.Position.X}, {npc.Position.Y}, {npc.Position.Z}", 33)
                return False

    for item_list in items.values():
        for item in item_list:
            Items.Move(item, npc.Serial, 0)
            Misc.Pause(500)
    
    return True

def handle_location_drop(items, quest_config, location):
    """Handle dropping items at specific coordinates."""
    drop_point = location["drop_point"]
    
    # Move to drop location
    if not move_to_location(drop_point["x"], drop_point["y"], drop_point["z"]):
        return False
    
    for item_list in items.values():
        total_items = len(item_list)
        items_dropped = 0
        
        while items_dropped < total_items:
            stack_size = min(quest_config["max_stack_size"], 
                           total_items - items_dropped)
            
            Items.MoveOnGround(item_list[items_dropped].Serial, stack_size,
                             drop_point["x"], drop_point["y"], drop_point["z"])
            Misc.Pause(500)
            items_dropped += stack_size
    
    return True

def handle_npc_turn_in(items, quest_config, location):
    """Handle turn-in to NPC."""
    # First try to move to the NPC
    if not move_to_location(location["x"], location["y"], location["z"]):
        return False

    # Find the NPC
    npc = Mobiles.FindBySerial(location["npc_serial"])
    if not npc:
        debug_message(f"Cannot find NPC at {location['name']}!", 33)
        return False
        
    for item_list in items.values():
        for item in item_list:
            Mobiles.UseMobile(npc)
            Misc.Pause(1000)
            Target.TargetExecute(item.Serial)
            Misc.Pause(1500)
    
    return True

def validate_empty_container(item, quest_config):
    """Validate if a container is empty."""
    debug_message(quest_config["validation"]["message"], 67)
    if Items.ContainerCount(item, True) > 0:
        debug_message("Container is not empty!", 33)
        return False
    return True

def handle_quest_mobiles_fallback():
    """If not near turn-in, engage quest targets.

    When INTERACT_ONLY_STATICS is True, only interact with ground statics/items
    (e.g., Poisonous Thorns) and DO NOT attack mobiles.
    """
    
    found = False
    # Search in a reasonable radius to avoid targeting far-away spawns
    SEARCH_RANGE_TILES = 12
    if not INTERACT_ONLY_STATICS:
        mobile_filter = Mobiles.Filter()
        mobile_filter.Enabled = True
        mobile_filter.RangeMax = SEARCH_RANGE_TILES
        mobiles = Mobiles.ApplyFilter(mobile_filter)
        for mobile in mobiles:
            try:
                if mobile and hasattr(mobile, 'Name'):
                    mname = str(mobile.Name).strip()
                    # Case-insensitive matching; allow partial contains either way
                    targets_lc = [t.lower() for t in QUEST_STATICS_TO_ATTACK]
                    if any(t in mname.lower() or mname.lower() in t for t in targets_lc):
                        debug_message(f"Engaging quest mobile: {mname} (0x{mobile.Serial:X}) within {SEARCH_RANGE_TILES} tiles", 68)
                        # Use proper attack API rather than just targeting
                        Player.Attack(mobile)
                        Misc.Pause(300)
                        found = True
            except Exception as e:
                debug_message(f"Error while trying to attack quest mobile: {e}", 33)
    if INTERACT_ONLY_STATICS or not found:
        # If no mobiles matched, try to find statics/items with matching names (e.g., Poisonous Thorns)
        items_found = False
        try:
            if hasattr(Items, 'Filter'):
                item_filter = Items.Filter()
                item_filter.Enabled = True
                item_filter.OnGround = True
                item_filter.RangeMax = SEARCH_RANGE_TILES
                nearby_items = Items.ApplyFilter(item_filter)
            else:
                nearby_items = []
        except Exception:
            nearby_items = []

        targets_lc = [t.lower() for t in QUEST_STATICS_TO_ATTACK]
        for itm in nearby_items:
            try:
                iname = str(getattr(itm, 'Name', '')).strip()
                if not iname:
                    continue
                if any(t in iname.lower() or iname.lower() in t for t in targets_lc):
                    debug_message(f"Interacting with quest object: {iname} (0x{itm.Serial:X}) within {SEARCH_RANGE_TILES} tiles", 68)
                    # Try a DoubleClick/use interaction for statics
                    try:
                        Items.DoubleClick(itm)
                    except Exception:
                        try:
                            Items.UseItem(itm)
                        except Exception:
                            pass
                    Misc.Pause(300)
                    items_found = True
            except Exception as e:
                debug_message(f"Error while trying to interact with quest object: {e}", 33)
        if not items_found:
            debug_message("No quest mobiles or objects found for fallback action.", 33)

def process_quest(quest_name, quest_config):
    """Process a specific quest turn-in."""
    # Find quest items
    items = find_quest_items(quest_config)
    if not items:
        debug_message(f"No items found for {quest_config['name']}!", 33)
        return False
    
    # Find nearest turn-in location
    location, distance = find_nearest_location(quest_config["locations"])
    if not location:
        debug_message("No valid turn-in location found!", 33)
        return False
    
    # Check if we're in range
    if not is_within_range(Player.Position.X, Player.Position.Y, 
                          location["x"], location["y"]):
        debug_message(f"Move closer to {location['name']} to turn in items!", 33)
        handle_quest_mobiles_fallback()
        return False
    
    # Validate items if necessary
    if "validation" in quest_config:
        for item_list in items.values():
            for item in item_list:
                if not validate_empty_container(item, quest_config):
                    return False
    
    # Handle turn-in based on type
    if quest_config["turn_in_type"] == "gump":
        return handle_gump_turn_in(items, quest_config, location)
    elif quest_config["turn_in_type"] == "direct_transfer":
        return handle_direct_transfer(items, quest_config, location)
    elif quest_config["turn_in_type"] == "location_drop":
        return handle_location_drop(items, quest_config, location)
    elif quest_config["turn_in_type"] == "npc":
        return handle_npc_turn_in(items, quest_config, location)
    else:
        debug_message(f"Unknown turn-in type: {quest_config['turn_in_type']}", 33)
        return False

def main():
    """Main script execution."""
    quests_available = False
    
    for quest_name, quest_config in QUESTS.items():
        debug_message(f"Checking for {quest_config['name']} items...", 67)
        if find_quest_items(quest_config):
            quests_available = True
            debug_message(f"Processing {quest_config['name']}...", 67)
            if process_quest(quest_name, quest_config):
                debug_message(f"Completed {quest_config['name']}!", 67)
            else:
                debug_message(f"Failed to complete {quest_config['name']}!", 33)
    
    if not quests_available:
        debug_message("No quest items found in backpack! Searching for quest mobiles to attack...", 33)
        handle_quest_mobiles_fallback()

if __name__ == '__main__':
    main()
