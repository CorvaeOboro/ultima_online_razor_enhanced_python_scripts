"""
Development Equipment Armor Data - a Razor Enhanced Python Script for Ultima Online

uses the play api to deduce armor values , testing different configurations 
first unequip all armor from the character
for each piece of armor in backpack get the properties , equip it , and note the change in the players AR , and elemental resistances 
note if an item has a Modifier property that may be altering the amount of AR it provides 
store the info to a json file to deduce the base armor values and modifiers amount for every unique item modifier .

VERSION:: 20250902
"""

import os
import json
import time


# Configuration
DEBUG_MODE = True
OUTPUT_DIR = "data"
PAUSE_BETWEEN_TESTS = 1000  # ms - increased for better stability
PROPERTY_WAIT_TIME = 600  # ms
EQUIPMENT_SETTLE_TIME = 1500  # ms - time to wait after equipping/unequipping

# Armor Rating tier bonuses (slot-specific values)
# this is untested on this shard , need validation 
AR_BONUS_TIERS = {
    'defense':        {'neck_hands': 0.4, 'arms_head_legs': 0.7, 'body': 2.2, 'shield': 1, 'pct': 5},
    'guarding':       {'neck_hands': 0.7, 'arms_head_legs': 1.4, 'body': 4.4, 'shield': 1.5, 'pct': 10},
    'hardening':      {'neck_hands': 1.1, 'arms_head_legs': 2.1, 'body': 6.6, 'shield': 2, 'pct': 15},
    'fortification':  {'neck_hands': 1.4, 'arms_head_legs': 2.8, 'body': 8.8, 'shield': 4, 'pct': 20},
    'invulnerable':   {'neck_hands': 1.8, 'arms_head_legs': 3.5, 'body': 11.0, 'shield': 7, 'pct': 25},
}


# Equipment slot mapping with item names from UI_walia_item_inspect.py
# needs validation and proper Slot names
EQUIP_SLOT_BY_ITEMID = {
    # --- Armor: Leather ---
    0x13CD: {'slot': 'arms', 'name': 'Leather Sleeves'},
    0x13CB: {'slot': 'legs', 'name': 'Leather Leggings'},
    0x13CC: {'slot': 'body', 'name': 'Leather Tunic'},
    0x13C6: {'slot': 'hand', 'name': 'Leather Gloves'},
    0x1DB9: {'slot': 'head', 'name': 'Leather Cap'},
    0x1C08: {'slot': 'legs', 'name': 'Leather Skirt'},
    0x1C06: {'slot': 'body', 'name': 'Leather Armor (Female)'},
    0x277A: {'slot': 'neck', 'name': 'Leather Mempo'},
    0x1C00: {'slot': 'legs', 'name': 'Leather Shorts'},
    0x1C0A: {'slot': 'body', 'name': 'Leather Bustier'},

    # --- Armor: Platemail ---
    0x1415: {'slot': 'body', 'name': 'Plate Mail Chest'},
    0x1411: {'slot': 'legs', 'name': 'Plate Mail Legs'},
    0x1414: {'slot': 'neck', 'name': 'Plate Mail Gorget'},
    0x1413: {'slot': 'hand', 'name': 'Plate Mail Gloves'},
    0x2779: {'slot': 'neck', 'name': 'Platemail Mempo'},
    0x140A: {'slot': 'head', 'name': 'Helmet'},
    0x140C: {'slot': 'head', 'name': 'Bascinet'},
    0x140E: {'slot': 'head', 'name': 'Norse Helm'},
    0x1408: {'slot': 'head', 'name': 'Close Helm'},
    0x1412: {'slot': 'head', 'name': 'Plate Helm'},
    0x1C04: {'slot': 'body', 'name': 'Platemail Female'},
    0x1410: {'slot': 'arms', 'name': 'Platemail Arms'},

    # --- Armor: Chainmail ---
    0x13BF: {'slot': 'body', 'name': 'Chainmail Tunic'},
    0x13BE: {'slot': 'legs', 'name': 'Chainmail Leggings'},
    0x13BB: {'slot': 'head', 'name': 'Chainmail Coif'},
    0x13C0: {'slot': 'body', 'name': 'Chainmail Tunic (Alt)'},
    0x13C3: {'slot': 'arms', 'name': 'Chainmail Sleeves'},
    0x13C4: {'slot': 'hand', 'name': 'Chainmail Gloves'},
    0x13F0: {'slot': 'legs', 'name': 'Chainmail Leggings (Alt)'},

    # --- Armor: Bone ---
    0x144F: {'slot': 'body', 'name': 'Bone Armor Chest'},
    0x1452: {'slot': 'legs', 'name': 'Bone Leggings'},
    0x144E: {'slot': 'arms', 'name': 'Bone Arms'},
    0x1450: {'slot': 'hand', 'name': 'Bone Gloves'},
    0x1451: {'slot': 'head', 'name': 'Bone Helmet'},

    # --- Armor: Ringmail ---
    0x13EC: {'slot': 'body', 'name': 'Ringmail Tunic'},
    0x13EE: {'slot': 'arms', 'name': 'Ringmail Sleeves'},
    0x13EB: {'slot': 'hand', 'name': 'Ringmail Gloves'},
    0x13F0: {'slot': 'legs', 'name': 'Ringmail Leggings'},

    # --- Armor: Studded ---
    0x13C7: {'slot': 'neck', 'name': 'Studded Leather Gorget'},
    0x13DB: {'slot': 'body', 'name': 'Studded Leather Tunic'},
    0x13D4: {'slot': 'arms', 'name': 'Studded Leather Sleeves'},
    0x13DA: {'slot': 'hand', 'name': 'Studded Leather Gloves'},
    0x13D6: {'slot': 'legs', 'name': 'Studded Leather Leggings'},
    0x279D: {'slot': 'neck', 'name': 'Studded Mempo'},
    0x13D5: {'slot': 'hand', 'name': 'Studded Gloves'},
    0x13DC: {'slot': 'arms', 'name': 'Studded Sleeves'},
    0x1C0C: {'slot': 'body', 'name': 'Studded Bustier'},
    0x1C02: {'slot': 'body', 'name': 'Studded Armor (Female)'},

    # --- Shields ---
    0x1B72: {'slot': 'shield', 'name': 'Shield'},
    0x1B73: {'slot': 'shield', 'name': 'Shield'},
    0x1B74: {'slot': 'shield', 'name': 'Shield'},
    0x1B75: {'slot': 'shield', 'name': 'Shield'},
    0x1B76: {'slot': 'shield', 'name': 'Shield'},
    0x1B77: {'slot': 'shield', 'name': 'Shield'},
    0x1B78: {'slot': 'shield', 'name': 'Shield'},
    0x1B79: {'slot': 'shield', 'name': 'Shield'},
    0x1B7A: {'slot': 'shield', 'name': 'Shield'},
    0x1B7B: {'slot': 'shield', 'name': 'Shield'},
    0x1BC3: {'slot': 'shield', 'name': 'Shield'},
    0x1BC4: {'slot': 'shield', 'name': 'Shield'},
    0x1BC5: {'slot': 'shield', 'name': 'Shield'},
    0x4201: {'slot': 'shield', 'name': 'Shield'},
    0x4200: {'slot': 'shield', 'name': 'Shield'},
    0x4202: {'slot': 'shield', 'name': 'Shield'},
    0x4203: {'slot': 'shield', 'name': 'Shield'},
    0x4204: {'slot': 'shield', 'name': 'Shield'},
    0x4205: {'slot': 'shield', 'name': 'Shield'},
    0x4206: {'slot': 'shield', 'name': 'Shield'},
    0x4207: {'slot': 'shield', 'name': 'Shield'},
    0x4208: {'slot': 'shield', 'name': 'Shield'},
    0x4228: {'slot': 'shield', 'name': 'Shield'},
    0x4229: {'slot': 'shield', 'name': 'Shield'},
    0x422A: {'slot': 'shield', 'name': 'Shield'},
    0x422C: {'slot': 'shield', 'name': 'Shield'},
    0x7817: {'slot': 'shield', 'name': 'Shield'},
    0x7818: {'slot': 'shield', 'name': 'Shield'},
    0xA649: {'slot': 'shield', 'name': 'Shield'},
}

# Armor modifier properties that affect AR/resistances (matching AR_BONUS_TIERS)
MODIFIER_PROPERTIES = {
    'defense', 'guarding', 'hardening', 'fortification', 'invulnerable'
}

# Additional quality modifiers (don't affect AR but worth tracking)
QUALITY_MODIFIERS = {
    'durable', 'substantial', 'massive', 'fortified', 'indestructible',
    'exceptional', 'mastercrafted'
}


def debug_msg(message, color=90):
    """Debug message output using techniques from DEV_api_player.py"""
    if not DEBUG_MODE:
        return
    try:
        Misc.SendMessage(f"[ARMOR_DATA] {message}", color)
    except Exception:
        print(f"[ARMOR_DATA] {message}")


def get_player_stats():
    """Get current player AR, resistances, and core stats using Player API"""
    try:
        stats = {
            'ar': Player.AR,
            'fire_resist': Player.FireResistance,
            'cold_resist': Player.ColdResistance,
            'poison_resist': Player.PoisonResistance,
            'energy_resist': Player.EnergyResistance,
            'str': Player.Str,
            'dex': Player.Dex,
            'int': Player.Int
        }
        return stats
    except Exception as e:
        debug_msg(f"Error getting player stats: {e}", 33)
        return None


def get_item_name(item):
    """Get clean item name using techniques from UI_walia_item_inspect.py"""
    try:
        name = getattr(item, 'Name', None)
        if name:
            return str(name).strip()
    except Exception:
        pass
    
    try:
        serial = int(getattr(item, 'Serial', 0))
        if serial:
            Items.WaitForProps(serial, PROPERTY_WAIT_TIME)
            props = Items.GetPropStringList(serial)
            if props and len(props) > 0:
                return str(props[0]).strip()
    except Exception:
        pass
    
    return 'Unknown'


def get_item_properties(item):
    """Get item properties using techniques from UI_walia_item_inspect.py"""
    try:
        serial = getattr(item, 'Serial', 0)
        if not serial:
            return []
            
        Items.WaitForProps(serial, PROPERTY_WAIT_TIME)
        property_list = Items.GetPropStringList(serial) or []
        
        # Skip name line if it duplicates the item name
        item_name = get_item_name(item)
        if property_list and len(property_list) > 0:
            first_prop = str(property_list[0]).strip()
            if first_prop.lower() == item_name.lower():
                property_list = property_list[1:]
        
        return [str(prop).strip() for prop in property_list if prop is not None]
    except Exception as e:
        debug_msg(f"Error getting properties for {getattr(item, 'Serial', 'unknown')}: {e}", 33)
        return []


def detect_equipped_layer(item):
    """Detect which layer an item is equipped to by scanning all layers"""
    try:
        item_serial = item.Serial
        armor_layers = ["Head", "Neck", "Shirt", "Pants", "Shoes", "Arms", "Gloves", "Ring", "Waist", "InnerTorso", "Bracelet", "MiddleTorso", "Earrings", "Cloak", "OuterTorso", "OuterLegs", "InnerLegs", "LeftHand", "RightHand"]
        
        for layer in armor_layers:
            try:
                equipped_item = Player.GetItemOnLayer(layer)
                if equipped_item and equipped_item.Serial == item_serial:
                    return layer
            except Exception:
                continue
        
        return None
    except Exception:
        return None


def get_item_base_name(item_id):
    """Get base item name from ItemID lookup"""
    try:
        item_data = EQUIP_SLOT_BY_ITEMID.get(int(item_id))
        return item_data['name'] if item_data else None
    except Exception:
        return None


def is_armor_item(item):
    """Check if item is armor or shield - filter obvious non-armor first"""
    try:
        item_id = getattr(item, 'ItemID', 0)
        if not item_id:
            return False
        
        # Quick filter: exclude obvious non-armor items
        non_armor_ids = {
            0x0EFA,  # Runebook
            0x0F0E,  # Spellbook
            0x1F14,  # Deed
            0x14F0,  # Bag
            0x0E76,  # Bag of Sending
            0x0E75,  # Backpack
            # Add more non-armor IDs as needed
        }
        
        if item_id in non_armor_ids:
            return False
        
        # Check if it's in our known armor mapping first
        if item_id in EQUIP_SLOT_BY_ITEMID:
            return True
        
        # For unknown items, try to equip and see if it goes to armor layers
        armor_layers = ["Head", "Neck", "Shirt", "Pants", "Shoes", "Arms", "Gloves", "Ring", "Waist", "InnerTorso", "Bracelet", "MiddleTorso", "Earrings", "Cloak", "OuterTorso", "OuterLegs", "InnerLegs", "LeftHand", "RightHand"]
        
        try:
            Player.EquipItem(item.Serial)
            Misc.Pause(300)  # Short pause for equip
            
            # Check if it equipped to any armor layer
            equipped_layer = detect_equipped_layer(item)
            is_armor = equipped_layer is not None
            
            # Unequip the item
            if is_armor:
                Items.Move(item.Serial, Player.Backpack.Serial, 1)
                Misc.Pause(300)
            
            return is_armor
            
        except Exception:
            return False
            
    except Exception:
        return False


def find_armor_in_backpack():
    """Find all armor items in player's backpack"""
    armor_items = []
    try:
        backpack = Player.Backpack
        if not backpack:
            debug_msg("No backpack found", 33)
            return armor_items
        
        for item in backpack.Contains:
            if is_armor_item(item):
                armor_items.append(item)
        
        debug_msg(f"Found {len(armor_items)} armor items in backpack")
        return armor_items
    except Exception as e:
        debug_msg(f"Error finding armor in backpack: {e}", 33)
        return armor_items


def unequip_all_armor():
    """Unequip ALL items from armor layers by moving to backpack"""
    debug_msg("Scanning all equipment layers for items to unequip...")
    unequipped_count = 0
    
    try:
        backpack_serial = int(Player.Backpack.Serial)
        debug_msg(f"Backpack serial: {hex(backpack_serial)}")
        
        # Define armor layers - unequip EVERYTHING from these layers (using valid layer names)
        armor_layers = ["Head", "Neck", "Shirt", "Pants", "Shoes", "Arms", "Gloves", "Ring", "Waist", "InnerTorso", "Bracelet", "MiddleTorso", "Earrings", "Cloak", "OuterTorso", "OuterLegs", "InnerLegs", "LeftHand", "RightHand"]
        
        # Scan all layers and unequip EVERYTHING (not just known armor)
        equipped_items = []
        for layer in armor_layers:
            try:
                item = Player.GetItemOnLayer(layer)
                if item is None:
                    continue
                
                # Debug all equipped items
                item_serial = item.Serial
                item_id = item.ItemID
                item_name = get_item_name(item)
                
                debug_msg(f"Layer {layer}: {item_name} (Serial: {hex(item_serial)}, ItemID: {hex(item_id)})")
                
                # Add ALL items to unequip list (not just recognized armor)
                equipped_items.append((layer, item))
                debug_msg(f"  -> UNEQUIP: Will remove this item", 63)
                    
            except Exception as e:
                debug_msg(f"Layer {layer}: Error - {e}")
        
        debug_msg(f"Found {len(equipped_items)} items to unequip from armor layers")
        
        # Unequip each armor item by moving to backpack with delays
        for layer, item in equipped_items:
            try:
                item_serial = item.Serial
                debug_msg(f"Moving layer {layer} item {hex(item_serial)} to backpack...")
                Items.Move(item_serial, backpack_serial, 1)
                Misc.Pause(500)  # Longer delay between each move
                unequipped_count += 1
                debug_msg(f"  -> Successfully moved {get_item_name(item)}", 63)
            except Exception as e:
                item_serial = item.Serial
                debug_msg(f"  -> ERROR moving item {hex(item_serial)}: {e}", 33)
        
        debug_msg(f"Unequipped {unequipped_count} armor pieces total")
        Misc.Pause(EQUIPMENT_SETTLE_TIME)  # Extra wait for all stats to update
        
        # Final verification that all items are removed from armor layers
        remaining_items = []
        for layer in armor_layers:
            try:
                item = Player.GetItemOnLayer(layer)
                if item:  # Remove ANY item from armor layers, not just recognized armor
                    remaining_items.append((layer, item))
            except Exception:
                continue
        
        if remaining_items:
            debug_msg(f"WARNING: {len(remaining_items)} armor items still equipped after unequip:", 33)
            for layer, item in remaining_items:
                debug_msg(f"  - {layer}: {get_item_name(item)}", 33)
                # Force move to backpack
                try:
                    Items.Move(item.Serial, backpack_serial, 1)
                    Misc.Pause(500)
                    debug_msg(f"  -> Force moved {get_item_name(item)}", 63)
                except Exception as e:
                    debug_msg(f"  -> Failed to force move: {e}", 33)
        else:
            debug_msg("All armor successfully removed", 63)
        
    except Exception as e:
        debug_msg(f"Error during unequip process: {e}", 33)


def verify_no_armor_equipped():
    """Verify that no items are equipped on armor layers"""
    armor_layers = ["Head", "Neck", "Shirt", "Pants", "Shoes", "Arms", "Gloves", "Ring", "Waist", "InnerTorso", "Bracelet", "MiddleTorso", "Earrings", "Cloak", "OuterTorso", "OuterLegs", "InnerLegs", "LeftHand", "RightHand"]
    
    equipped_items = []
    for layer in armor_layers:
        item = Player.GetItemOnLayer(layer)
        if item:  # Check for ANY item on armor layers, not just recognized armor
            equipped_items.append((layer, item))
    
    if len(equipped_items) == 0:
        debug_msg("VERIFIED: No armor items equipped - clean slate confirmed", 63)
        return True
    else:
        debug_msg(f"ERROR: {len(equipped_items)} armor items still equipped:", 33)
        for layer, item in equipped_items:
            debug_msg(f"  - {layer}: {get_item_name(item)}", 33)
        return False


def verify_single_item_equipped(expected_item):
    """Verify that only the expected item is equipped on armor layers"""
    armor_layers = ["Head", "Neck", "Shirt", "Pants", "Shoes", "Arms", "Gloves", "Ring", "Waist", "InnerTorso", "Bracelet", "MiddleTorso", "Earrings", "Cloak", "OuterTorso", "OuterLegs", "InnerLegs", "LeftHand", "RightHand"]
    
    equipped_items = []
    for layer in armor_layers:
        item = Player.GetItemOnLayer(layer)
        if item:  # Check for ANY item on armor layers
            equipped_items.append((layer, item))
    
    if len(equipped_items) == 0:
        debug_msg("WARNING: No armor items equipped", 33)
        return False
    elif len(equipped_items) == 1:
        layer, item = equipped_items[0]
        if item.Serial == expected_item.Serial:
            debug_msg(f"VERIFIED: Only {get_item_name(item)} equipped on {layer}", 63)
            return True
        else:
            debug_msg(f"ERROR: Wrong item equipped - expected {get_item_name(expected_item)}, found {get_item_name(item)}", 33)
            return False
    else:
        debug_msg(f"ERROR: Multiple armor items equipped ({len(equipped_items)} items)", 33)
        for layer, item in equipped_items:
            debug_msg(f"  - {layer}: {get_item_name(item)}", 33)
        return False


def equip_item(item):
    """Equip an item and wait for stats to update"""
    try:
        Player.EquipItem(item.Serial)
        Misc.Pause(EQUIPMENT_SETTLE_TIME)  # Longer wait for equip and stats update
        return True
    except Exception as e:
        debug_msg(f"Error equipping item {item.Serial}: {e}", 33)
        return False


def unequip_item(item):
    """Unequip an item by moving to backpack"""
    try:
        backpack_serial = Player.Backpack.Serial
        Items.Move(item.Serial, backpack_serial, 1)
        Misc.Pause(EQUIPMENT_SETTLE_TIME)  # Longer wait for move and stats update
        return True
    except Exception as e:
        debug_msg(f"Error moving item {hex(item.Serial)} to backpack: {e}", 33)
        return False


def extract_modifiers_from_properties(properties):
    """Extract AR modifier properties and quality modifiers"""
    ar_modifiers = []
    quality_modifiers = []
    
    for prop in properties:
        prop_lower = prop.lower().strip()
        
        # Check for AR-affecting modifiers first
        for modifier in MODIFIER_PROPERTIES:
            if modifier in prop_lower:
                ar_modifiers.append(modifier.title())
                break
        
        # Check for quality modifiers
        for modifier in QUALITY_MODIFIERS:
            if modifier in prop_lower:
                quality_modifiers.append(modifier.title())
                break
    
    return ar_modifiers, quality_modifiers


def test_armor_piece(item, baseline_stats):
    """Test a single armor piece and record the stat changes"""
    debug_msg(f"Testing {get_item_name(item)}...")
    
    # Get item properties
    properties = get_item_properties(item)
    ar_modifiers, quality_modifiers = extract_modifiers_from_properties(properties)
    
    # Equip the item
    if not equip_item(item):
        return None
    
    # Verify only this item is equipped
    if not verify_single_item_equipped(item):
        debug_msg("Equipment verification failed - skipping this item", 33)
        unequip_item(item)
        return None
    
    # Additional delay before measuring stats
    debug_msg("Waiting for stats to stabilize...")
    Misc.Pause(EQUIPMENT_SETTLE_TIME)
    
    # Get stats after equipping
    equipped_stats = get_player_stats()
    if not equipped_stats:
        unequip_item(item)
        return None
    
    # Detect the actual layer this item equipped to (must be done while still equipped)
    equipped_layer = detect_equipped_layer(item)
    
    # Calculate deltas including stat changes
    deltas = {
        'ar_delta': equipped_stats['ar'] - baseline_stats['ar'],
        'fire_delta': equipped_stats['fire_resist'] - baseline_stats['fire_resist'],
        'cold_delta': equipped_stats['cold_resist'] - baseline_stats['cold_resist'],
        'poison_delta': equipped_stats['poison_resist'] - baseline_stats['poison_resist'],
        'energy_delta': equipped_stats['energy_resist'] - baseline_stats['energy_resist'],
        'str_delta': equipped_stats['str'] - baseline_stats['str'],
        'dex_delta': equipped_stats['dex'] - baseline_stats['dex'],
        'int_delta': equipped_stats['int'] - baseline_stats['int']
    }
    
    # Unequip the item
    unequip_item(item)
    
    # Build result object with proper type conversion for JSON
    result = {
        'item_name': get_item_name(item),
        'item_id': hex(int(item.ItemID)),
        'layer': equipped_layer,
        'properties': properties,
        'ar_modifiers': ar_modifiers,
        'quality_modifiers': quality_modifiers,
        'deltas': {k: int(v) for k, v in deltas.items()},
        'timestamp': time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())
    }
    
    debug_msg(f"AR: {deltas['ar_delta']:+d}, STR: {deltas['str_delta']:+d}, "
             f"DEX: {deltas['dex_delta']:+d}, INT: {deltas['int_delta']:+d}")
    if ar_modifiers:
        debug_msg(f"AR Modifiers: {', '.join(ar_modifiers)}", 67)
    
    return result


def save_results_to_json(results):
    """Save armor test results to universal JSON database"""
    try:
        # Ensure output directory exists
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        output_path = os.path.join(project_root, OUTPUT_DIR)
        
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        
        # Universal database filename
        universal_db = os.path.join(output_path, "armor_universal_database.json")
        
        # Load existing data or create new
        existing_data = {'metadata': {'total_entries': 0}, 'armor_entries': []}
        if os.path.exists(universal_db):
            try:
                with open(universal_db, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            except Exception as e:
                debug_msg(f"Error loading existing database: {e}", 33)
        
        # Append new results
        existing_data['armor_entries'].extend(results)
        
        # Update metadata
        existing_data['metadata'] = {
            'script_version': '20250902',
            'last_updated': time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime()),
            'total_entries': len(existing_data['armor_entries']),
            'player_name': str(Player.Name) if hasattr(Player, 'Name') else 'Unknown',
            'session_items_added': len(results)
        }
        
        # Write updated database
        with open(universal_db, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, indent=2, ensure_ascii=False)
        
        debug_msg(f"Added {len(results)} entries to universal database: {universal_db}")
        debug_msg(f"Total database entries: {existing_data['metadata']['total_entries']}")
        return universal_db
        
    except Exception as e:
        debug_msg(f"Error saving results: {e}", 33)
        return None


def analyze_results(results):
    """Analyze and summarize the armor test results"""
    if not results:
        return
    
    debug_msg("=== ARMOR DATA ANALYSIS ===", 67)
    
    # Group by layer
    by_layer = {}
    for result in results:
        layer = result['layer'] or 'unknown'
        if layer not in by_layer:
            by_layer[layer] = []
        by_layer[layer].append(result)
    
    # Analyze each layer
    for layer, items in by_layer.items():
        debug_msg(f"--- {layer.upper()} LAYER ---", 63)
        
        for item in items:
            deltas = item['deltas']
            ar_modifiers = item.get('ar_modifiers', [])
            quality_modifiers = item.get('quality_modifiers', [])
            all_modifiers = ar_modifiers + quality_modifiers
            modifier_text = f" ({', '.join(all_modifiers)})" if all_modifiers else ""
            
            debug_msg(f"{item['item_name']}{modifier_text}:")
            debug_msg(f"  AR: {deltas['ar_delta']:+d}, "
                     f"F: {deltas['fire_delta']:+d}, "
                     f"C: {deltas['cold_delta']:+d}, "
                     f"P: {deltas['poison_delta']:+d}, "
                     f"E: {deltas['energy_delta']:+d}")
    
    # Summary statistics
    total_items = len(results)
    items_with_ar_modifiers = len([r for r in results if r.get('ar_modifiers', [])])
    unique_ar_modifiers = set()
    unique_quality_modifiers = set()
    for result in results:
        unique_ar_modifiers.update(result.get('ar_modifiers', []))
        unique_quality_modifiers.update(result.get('quality_modifiers', []))
    
    debug_msg(f"=== SUMMARY ===", 67)
    debug_msg(f"Total items tested: {total_items}")
    debug_msg(f"Items with AR modifiers: {items_with_ar_modifiers}")
    debug_msg(f"Unique AR modifiers: {len(unique_ar_modifiers)}")
    if unique_ar_modifiers:
        debug_msg(f"AR Modifiers: {', '.join(sorted(unique_ar_modifiers))}")
    debug_msg(f"Unique quality modifiers: {len(unique_quality_modifiers)}")
    if unique_quality_modifiers:
        debug_msg(f"Quality Modifiers: {', '.join(sorted(unique_quality_modifiers))}")


def main():
    """Main function to test all armor pieces"""
    try:
        debug_msg("Starting Equipment Armor Data Collection", 67)
        
        # Get baseline stats (no armor equipped)
        debug_msg("Step 1: Unequipping all armor...")
        unequip_all_armor()
        
        baseline_stats = get_player_stats()
        if not baseline_stats:
            debug_msg("Failed to get baseline stats", 33)
            return
        
        debug_msg(f"Baseline - AR: {baseline_stats['ar']}, "
                 f"Fire: {baseline_stats['fire_resist']}, "
                 f"Cold: {baseline_stats['cold_resist']}, "
                 f"Poison: {baseline_stats['poison_resist']}, "
                 f"Energy: {baseline_stats['energy_resist']}")
        
        # Find all armor in backpack
        debug_msg("Step 2: Finding armor items in backpack...")
        armor_items = find_armor_in_backpack()
        
        if not armor_items:
            debug_msg("No armor items found in backpack", 33)
            return
        
        # Test each armor piece
        debug_msg("Step 3: Testing each armor piece...")
        results = []
        for i, item in enumerate(armor_items, 1):
            debug_msg(f"Testing item {i}/{len(armor_items)}: {get_item_name(item)}")
            
            # Ensure clean slate before each test
            debug_msg(f"Unequipping all armor before testing item {i}...")
            unequip_all_armor()
            
            # Verify clean slate
            if not verify_no_armor_equipped():
                debug_msg("Failed to achieve clean slate - forcing manual unequip", 33)
                # Force unequip any remaining items
                for retry in range(3):
                    unequip_all_armor()
                    if verify_no_armor_equipped():
                        break
                    debug_msg(f"Retry {retry + 1}/3: Still have armor equipped", 33)
                else:
                    debug_msg("CRITICAL: Cannot achieve clean slate - skipping this item", 33)
                    continue
            
            # Get fresh baseline stats for this test
            baseline_stats = get_player_stats()
            if not baseline_stats:
                debug_msg("Failed to get baseline stats for this test", 33)
                continue
            
            result = test_armor_piece(item, baseline_stats)
            if result:
                results.append(result)
            
            # Longer pause between tests for stability
            Misc.Pause(EQUIPMENT_SETTLE_TIME)
        
        # Save results
        debug_msg("Step 4: Saving results...")
        filepath = save_results_to_json(results)
        
        # Analyze results
        debug_msg("Step 5: Analyzing results...")
        analyze_results(results)
        
        debug_msg(f"Armor data collection complete! Tested {len(results)} items.", 67)
        if filepath:
            debug_msg(f"Data saved to: {os.path.basename(filepath)}", 67)
        
    except Exception as e:
        debug_msg(f"Error in main: {e}", 33)


if __name__ == '__main__':
    main()