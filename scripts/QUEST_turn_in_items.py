"""
Quest Turn-in Script - a Razor Enhanced Python Script for Ultima Online

Handles multiple quest types with different turn-in methods:
1. Gump-based turn-ins (e.g., treasure maps , dyes , empty chests)
2. Direct item transfers (e.g. give to NPC)
3. Location-based drops (e.g., placing items at specific coordinates)

Features:
- Detection of available quests based on inventory items
- Multiple turn-in locations and NPCs
- Different turn-in mechanics per quest type
- Quest assumption based on player location
- Pathfinding to turn-in locations

Quest Dictionary example is for Unchained , modify for your shard

VERSION::20250621
"""
import math

# Quest Configuration
QUESTS = {
    "treasure_maps": {
        "name": "Treasure Map Turn-in",
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
            {"name": "Treasure Map", "id": 0x14EC, "hue": -1},  # Level 1
            {"name": "Treasure Map", "id": 0x14ED, "hue": -1},  # Level 2
            {"name": "Treasure Map", "id": 0x14EE, "hue": -1},  # Level 3
            {"name": "Treasure Map", "id": 0x14EF, "hue": -1},  # Level 4
            {"name": "Treasure Map", "id": 0x352E, "hue": -1},  # Level 5+ (custom shards)
            {"name": "Treasure Map", "id": 0x2AAA, "hue": -1},  # Example custom
            {"name": "Treasure Map", "id": 0x2AAB, "hue": -1},  # Example custom
        ],
        "turn_in_type": "gump",
        "gump_id": 1889568190,
        "turn_in_action": 1
    },
    "rare_dyes": {
        "name": "Rare Dye Turn-in",
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
            {"name": "Rare Dye ", "id": 0x0E2A, "hue": -1},
            {"name": "Rare Dye ", "id": 0x0E2B, "hue": -1},
            {"name": "Rare Dye ", "id": 0x0E25, "hue": -1},
            {"name": "Carpet Dye", "id": 0x7163, "hue": -1}
        ],
        "turn_in_type": "gump",
        "gump_id": 1889568190,
        "turn_in_action": 1
    },
    "empty_paragon_chest": {
        "name": "Empty Paragon Chest Turn-in",
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
    "ancient_vase": {
        "name": "Sandstorm Ancient Vase",
        "locations": [
            {
                "name": " Sasha the archaeologist ",
                "x": 1833,
                "y": 953,
                "z": 1,
                "npc_serial": 0x00004279
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
        "container_type": "npc"  # Transfer directly to NPC 
    },
    "strange_egg": {
        "name": "Shame Strange Egg",
        "locations": [
            {
                "name": " Wellen the entomologist ",
                "x": 510,
                "y": 1563,
                "z": 0,
                "npc_serial": 0x000000C1
            }
        ],
        "items": [
            {"name": "Strange Egg", "id": 0x10D9, "hue": -1}
        ],
        "turn_in_type": "direct_transfer",
        "container_type": "npc"  # Transfer directly to NPC 
    },

}

def find_quest_items(quest_config):
    """Find all quest items in player's backpack for a specific quest."""
    items_found = {}
    
    for item_info in quest_config["items"]:
        items = Items.FindByID(item_info["id"], item_info["hue"], Player.Backpack.Serial)
        if items:
            if not isinstance(items, list):
                items = [items]
            items_found[item_info["id"]] = items
            Misc.SendMessage(f"Found {len(items)} {item_info['name']}(s)!", 65)
    
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
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

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
            Misc.SendMessage("Could not reach location after maximum attempts!", 33)
            return False
            
        # Break if we're too far
        if calculate_distance(Player.Position.X, Player.Position.Y, target_x, target_y) > max_distance:
            Misc.SendMessage("Too far from target location!", 33)
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
        Misc.SendMessage(f"Cannot find NPC at {location['name']}!", 33)
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
                    Misc.SendMessage("Target cursor not received!", 33)
            else:
                Misc.SendMessage("Expected gump not received!", 33)
    
    # Close any remaining gumps
    Gumps.CloseGump(quest_config["gump_id"])
    return True

def handle_direct_transfer(items, quest_config, location):
    """Handle direct item transfer to NPC or container."""
    # First try to move to the NPC
    if not move_to_location(location["x"], location["y"], location["z"]):
        return False

    # Find the NPC
    npc = Mobiles.FindBySerial(location["npc_serial"])
    if not npc:
        Misc.SendMessage(f"Cannot find NPC at {location['name']}!", 33)
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
        Misc.SendMessage(f"Cannot find NPC at {location['name']}!", 33)
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
    Misc.SendMessage(quest_config["validation"]["message"], 67)
    if Items.ContainerCount(item, True) > 0:
        Misc.SendMessage("Container is not empty!", 33)
        return False
    return True

def handle_quest_mobiles_fallback():
    """If not near turn-in, find and attack specific quest mobiles."""
    quest_mobiles = ["A Coccon", "a bonfire crystal"]
    found = False
    mobile_filter = Mobiles.Filter()
    mobile_filter.Enabled = True
    mobiles = Mobiles.ApplyFilter(mobile_filter)
    for mobile in mobiles:
        if mobile.Name in quest_mobiles:
            Misc.SendMessage("All Attack")  # Replace with your shard's attack macro if needed
            Target.TargetExecute(mobile.Serial)
            Misc.SendMessage(f"Targeted quest mobile: {mobile.Name} (0x{mobile.Serial:X})", 68)
            Misc.Pause(1000)
            found = True
    if not found:
        Misc.SendMessage("No quest mobiles found for fallback action.", 33)

def process_quest(quest_name, quest_config):
    """Process a specific quest turn-in."""
    # Find quest items
    items = find_quest_items(quest_config)
    if not items:
        Misc.SendMessage(f"No items found for {quest_config['name']}!", 33)
        return False
    
    # Find nearest turn-in location
    location, distance = find_nearest_location(quest_config["locations"])
    if not location:
        Misc.SendMessage("No valid turn-in location found!", 33)
        return False
    
    # Check if we're in range
    if not is_within_range(Player.Position.X, Player.Position.Y, 
                          location["x"], location["y"]):
        Misc.SendMessage(f"Move closer to {location['name']} to turn in items!", 33)
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
        Misc.SendMessage(f"Unknown turn-in type: {quest_config['turn_in_type']}", 33)
        return False

def main():
    """Main script execution."""
    quests_available = False
    
    for quest_name, quest_config in QUESTS.items():
        Misc.SendMessage(f"Checking for {quest_config['name']} items...", 67)
        if find_quest_items(quest_config):
            quests_available = True
            Misc.SendMessage(f"Processing {quest_config['name']}...", 67)
            if process_quest(quest_name, quest_config):
                Misc.SendMessage(f"Completed {quest_config['name']}!", 67)
            else:
                Misc.SendMessage(f"Failed to complete {quest_config['name']}!", 33)
    
    if not quests_available:
        Misc.SendMessage("No quest items found in backpack!", 33)


if __name__ == '__main__':
    main()
