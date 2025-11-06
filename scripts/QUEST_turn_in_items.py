"""
Quest Item Turn In - a Razor Enhanced Python Script for Ultima Online

Turn in Items to Quest NPC , Searches for quest items in inventory and gives them to specific NPC
for example : Daemon Bones to Canute , Ancient Vases to Sasha , Strange Eggs to Wellen 

TODO:
- restore the orb , treasure map , and paragon turn in to griphook when returns

620 2195 = chaos island blood quest 
the remains of a blood elemental 
578 2259

diseased blood 0x0E24 , hue 0x09a7 ,  turn into canute
gather diseased blood , around chaos island 499 2183 , a bloody corpse , the remains of a blood elemental

HOTKEY:: K ( Kwuest )
VERSION:: 20251018
"""
import System
import System.Collections.Generic

DEBUG_MODE = False

# Quest Configurations
QUESTS_WORLD = {
      "daily_hiddenvalley_lizardman_scales": {
        "name": "Daily: Collect Lizardman Scales",
        "description": "Gather Lizardman Scales in Hidden Valley and turn in to Canute the Daily Quest Master.",
        "category": "daily",
        "region": "hiddenvalley",
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
            {"name": "Lizardman Scale", "id": 0x26B2, "hue": 0x0ad5}
        ],
        "turn_in_type": "direct_transfer",
        "container_type": "npc"
    },
    "daily_cyclops_head": {
        "name": "Daily: Collect Cyclops Head",
        "description": "Gather Cyclops Head and turn in to Canute the Daily Quest Master.",
        "category": "daily",
        "region": "world",
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
            {"name": "Cyclops Head", "id": 0xA9B2, "hue": -1}
        ],
        "turn_in_type": "direct_transfer",
        "container_type": "npc"
    },
    "daily_robust_harpy_feathers": {
        "name": "Daily: Collect Robust Harpy Feathers",
        "description": "Gather Robust Harpy Feathers and turn in to Canute the Daily Quest Master.",
        "category": "daily",
        "region": "world",
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
            {"name": "Robust Harpy Feather", "id": 0x5737, "hue": 0x0B42}
        ],
        "turn_in_type": "direct_transfer",
        "container_type": "npc"
    },
    "world_treasure_map_turnin": {
        "name": "World: Treasure Map Turn-in",
        "description": "Turn in basic treasure maps (hue 0) to Carlos in Britain.",
        "category": "world",
        "region": "britain",
        "locations": [
            {
                "name": "Carlos",
                "x": 1437,
                "y": 1701,
                "z": 5,
                "npc_serial": 0x000002D0
            }
        ],
        "items": [
            {"name": "Treasure Map", "id": 0x14EC, "hue": 0x0000}
        ],
        "turn_in_type": "direct_transfer",
        "container_type": "npc"
    }
}

QUESTS_NECRONOMICON = {
    "necronomicon_pages": {
        "name": "Necronomicon Pages Collection",
        "description": "Turn in Page of the Necronomicon Tome to Umbrelle the city witch.",
        "category": "event",
        "region": "luna",
        "locations": [
            {
                "name": "Umbrelle the city witch",
                "x": 1414,
                "y": 1704,
                "z": 12,
                "npc_serial": 0x00000119
            }
        ],
        "items": [
            {"name": "Page of the Necronomicon Tome", "id": 0x7492, "hue": 0x0B02}
        ],
        "turn_in_type": "direct_transfer",
        "container_type": "npc"
    }
}

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
    },
    "daily_diseased_blood": {
        "name": "Daily: Collect Diseased Blood",
        "description": "Collect Diseased Blood and turn in to Canute the Daily Quest Master.",
        "category": "daily",
        "region": "shame",
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
            {"name": "Diseased Blood", "id": 0x0E24, "hue": 0x09A7}
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

QUESTS_DUNGEON_WRONG = {
    "daily_wrong_elfic_artifact": {
        "name": "Daily: Collect Elfic Artifact",
        "description": "Collect Elfic Artifact in Wrong and turn in to Canute the Daily Quest Master.",
        "category": "daily",
        "region": "wrong",
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
            {"name": "Elfic Artifact", "id": 0x241E, "hue": -1},
            {"name": "Elfic Artifact", "id": 0x241D, "hue": -1},
            {"name": "Elfic Artifact", "id": 0x241C, "hue": -1}
        ],
        "turn_in_type": "direct_transfer",
        "container_type": "npc"
    }
}

QUESTS_DEADSTALL_ISLAND = {
    "deadstall_resurrect_lost_souls": {
        "name": "Deadstall Island: Resurrect Lost Souls",
        "description": "Cast Resurrection spell on Lost Souls near Deadstall Island.",
        "category": "spell_quest",
        "region": "deadstall",
        "quest_range": 500,  # How far from Deadstall Island to activate quest
        "locations": [
            {
                "name": "Deadstall Island",
                "x": 391,
                "y": 2026,
                "z": 0
            }
        ],
        "turn_in_type": "spell_cast",
        "spell_name": "Resurrection",
        "target_mobile": {
            "name": "Lost Soul",
            "id": 0x03CA,
            "max_range": 3  # How far Lost Soul can be to cast spell on it
        }
    }
}

QUESTS_HALLOWEEN = {
    "halloween_candy_collection": {
        "name": "Halloween: Candy Collection",
        "description": "Collect Halloween Candy and deposit into Candy Bag.",
        "category": "event",
        "region": "world",
        "items": [
            {"name": "Halloween Candy", "id": 0x7177, "hue": -1}
        ],
        "turn_in_type": "container_deposit",
        "target_container": {
            "name": "Candy Bag",
            "id": 0x0E76,
            "hue": 0x08BB
        }
    }
}

QUESTS_EXILE = {
    "exile_britain_blueprint": {
        "name": "Exile: Britain Blueprint",
        "description": "Turn in A Britain Blueprint to Peter in Exile.",
        "category": "region",
        "region": "exile",
        "locations": [
            {
                "name": "Peter",
                "x": 4231,
                "y": 3752,
                "z": 0,
                "npc_serial": 0x0001076F
            }
        ],
        "items": [
            {"name": "A Britain Blueprint", "id": 0x14ED, "hue": 0x0B48},
            {"name": "A Compromising Blueprint", "id": 0x14F1, "hue": 0x0B48}
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
for group in ( QUESTS_WORLD, QUESTS_NECRONOMICON, QUESTS_DUNGEON_SANDSTORM, QUESTS_DUNGEON_SHAME, QUESTS_DUNGEON_DECEIT, QUESTS_DUNGEON_DESTARD, QUESTS_DUNGEON_WRONG, QUESTS_DEADSTALL_ISLAND, QUESTS_HALLOWEEN, QUESTS_EXILE):
    QUESTS.update(group)

# Lastly , if not near any item turn in we try to attack specific quest objectives 
# Cocoon (0x9F83), Daemonic Totem (0xB829) - Similar to Poisonous Thorns, attack these quest objects
# imprisoned eclipse (0x6E19) - LUNA quest
QUEST_STATICS_TO_ATTACK = ["A Cocoon", "Daemonic Totem", "a bonfire crystal", "Demonic Portal", "Poisonous Thorns", "imprisoned eclipse"]
INTERACT_ONLY_STATICS = True  # When true, only interact with statics items  and do NOT attack mobiles
USE_ALL_ATTACK = True  # When true, say "All Attack" and target the quest entity to command pets/party

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

    # Sequentially re-scan and move items one-by-one. This handles non-stacking
    moved_any = False
    attempt_round = 0
    MAX_ROUNDS = 15
    while attempt_round < MAX_ROUNDS:
        attempt_round += 1
        remaining = find_quest_items(quest_config)
        if not remaining:
            break

        # Move each found item individually with safe pacing
        for item_list in remaining.values():
            for item in item_list:
                try:
                    # Non-stackables should move amount=1. For stackables, server treats 1 as single unit; repeated loop drains stack.
                    Items.Move(item, npc.Serial, 1)
                    Misc.Pause(650)
                    moved_any = True
                except Exception as e:
                    debug_message(f"Move failed for item 0x{getattr(item, 'Serial', 0):X}: {e}", 33)
                    Misc.Pause(300)

        # Small backoff between rounds to allow server/inventory refresh
        Misc.Pause(600)

    return moved_any

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

def handle_container_deposit(items, quest_config):
    """Handle depositing items into a specific container in backpack."""
    target_container_info = quest_config["target_container"]
    
    # Search for the target container in backpack
    target_container = Items.FindByID(
        target_container_info["id"], 
        target_container_info["hue"], 
        Player.Backpack.Serial
    )
    
    if not target_container:
        debug_message(f"Cannot find {target_container_info['name']} (0x{target_container_info['id']:04X}, hue 0x{target_container_info['hue']:04X}) in backpack!", 33)
        return False
    
    debug_message(f"Found {target_container_info['name']} in backpack", 68)
    
    # Move items into the container
    moved_any = False
    attempt_round = 0
    MAX_ROUNDS = 15
    
    while attempt_round < MAX_ROUNDS:
        attempt_round += 1
        remaining = find_quest_items(quest_config)
        if not remaining:
            break
        
        # Move each found item individually
        for item_list in remaining.values():
            for item in item_list:
                try:
                    Items.Move(item, target_container.Serial, 0)  # 0 = move entire stack
                    Misc.Pause(650)
                    moved_any = True
                    debug_message(f"Moved {item.Name if hasattr(item, 'Name') else 'item'} to {target_container_info['name']}", 68)
                except Exception as e:
                    debug_message(f"Move failed for item 0x{getattr(item, 'Serial', 0):X}: {e}", 33)
                    Misc.Pause(300)
        
        # Small backoff between rounds
        Misc.Pause(600)
    
    return moved_any

def validate_empty_container(item, quest_config):
    """Validate if a container is empty."""
    debug_message(quest_config["validation"]["message"], 67)
    if Items.ContainerCount(item, True) > 0:
        debug_message("Container is not empty!", 33)
        return False
    return True

def handle_spell_cast(quest_config, location):
    """Handle spell casting quest (e.g., Resurrection on Lost Souls)."""
    target_info = quest_config["target_mobile"]
    max_range = target_info.get("max_range", 8)
    
    Misc.SendMessage(f"[QUEST] Searching for {target_info['name']} (0x{target_info['id']:04X}) within {max_range} tiles...", 68)
    
    # Search for target mobile
    mobile_filter = Mobiles.Filter()
    mobile_filter.Enabled = True
    mobile_filter.RangeMax = max_range
    
    # Create .NET List for Bodies filter
    body_list = System.Collections.Generic.List[System.Int32]()
    body_list.Add(target_info["id"])
    mobile_filter.Bodies = body_list
    
    # Create .NET List for Notorieties (all types)
    notoriety_list = System.Collections.Generic.List[System.Byte]()
    for i in range(8):
        notoriety_list.Add(i)
    mobile_filter.Notorieties = notoriety_list
    
    mobiles = Mobiles.ApplyFilter(mobile_filter)
    
    Misc.SendMessage(f"[QUEST] Found {len(mobiles) if mobiles else 0} matching mobiles", 68)
    
    if not mobiles or len(mobiles) == 0:
        Misc.SendMessage(f"[QUEST] No {target_info['name']} found within {max_range} tiles!", 33)
        return False
    
    # Find nearest target
    nearest_mobile = None
    min_distance = float('inf')
    
    for mobile in mobiles:
        if mobile and hasattr(mobile, 'Position'):
            dist = calculate_distance(Player.Position.X, Player.Position.Y, 
                                     mobile.Position.X, mobile.Position.Y)
            if dist < min_distance:
                min_distance = dist
                nearest_mobile = mobile
    
    if not nearest_mobile:
        debug_message(f"No valid {target_info['name']} found!", 33)
        return False
    
    debug_message(f"Found {target_info['name']} at {min_distance:.1f} tiles away", 68)
    
    # Cast Resurrection spell
    spell_name = quest_config["spell_name"]
    debug_message(f"Casting {spell_name} on {target_info['name']}...", 68)
    
    # Cast the spell
    Spells.CastMagery(spell_name)
    Misc.Pause(1500)  # Wait for spell to be ready
    
    # Wait for target cursor
    if Target.WaitForTarget(3000):
        Target.TargetExecute(nearest_mobile)
        Misc.Pause(1000)
        debug_message(f"Cast {spell_name} on {target_info['name']}!", 68)
        return True
    else:
        debug_message("Target cursor not received after casting spell!", 33)
        return False

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
                        # If USE_ALL_ATTACK is enabled, command pets/party to attack
                        if USE_ALL_ATTACK:
                            Player.ChatSay(0, "All Attack")
                            Misc.Pause(200)
                            Target.WaitForTarget(2000, False)
                            Target.TargetExecute(mobile)
                            Misc.Pause(300)
                            debug_message(f"Commanded All Attack on {mname}", 68)
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
                    # If USE_ALL_ATTACK is enabled, command pets/party to attack the static object
                    if USE_ALL_ATTACK:
                        Player.ChatSay(0, "All Attack")
                        Misc.Pause(200)
                        Target.WaitForTarget(2000, False)
                        Target.TargetExecute(itm)
                        Misc.Pause(300)
                        debug_message(f"Commanded All Attack on {iname}", 68)
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
    
    # Handle container deposit quests (no location needed)
    if quest_config["turn_in_type"] == "container_deposit":
        items = find_quest_items(quest_config)
        if not items:
            debug_message(f"No items found for {quest_config['name']}!", 33)
            return False
        return handle_container_deposit(items, quest_config)
    
    # Find nearest turn-in location
    location, distance = find_nearest_location(quest_config["locations"])
    if not location:
        debug_message("No valid turn-in location found!", 33)
        return False
    
    # Handle spell casting quests differently
    if quest_config["turn_in_type"] == "spell_cast":
        # Check if we're in range of quest location (use quest_range if specified, otherwise default to 15)
        quest_range = quest_config.get("quest_range", 15)
        if not is_within_range(Player.Position.X, Player.Position.Y, 
                              location["x"], location["y"], range_tiles=quest_range):
            debug_message(f"Move closer to {location['name']} (within {quest_range} tiles) to perform quest!", 33)
            return False
        
        debug_message(f"Within {quest_range} tiles of {location['name']}, searching for targets...", 68)
        return handle_spell_cast(quest_config, location)
    
    # For item-based quests, find quest items
    items = find_quest_items(quest_config)
    if not items:
        debug_message(f"No items found for {quest_config['name']}!", 33)
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
        # Spell-cast quests don't require items in backpack
        if quest_config.get("turn_in_type") == "spell_cast":
            debug_message(f"Checking for {quest_config['name']} quest...", 67)
            quests_available = True
            debug_message(f"Processing {quest_config['name']}...", 67)
            if process_quest(quest_name, quest_config):
                debug_message(f"Completed {quest_config['name']}!", 67)
            else:
                debug_message(f"Failed to complete {quest_config['name']}!", 33)
        else:
            # Item-based quests
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
