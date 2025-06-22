"""
Development Item Inspector - a Razor Enhanced Python Script for Ultima Online

Returns information of all items in player's backpack and equipment, writes to .json file.
- Items API methods
- Properties system

Outputs information about:
- Basic item properties (ID, Color, etc)
- Extended properties (Name, Stats, etc)

DOCUMENTATION:
https://razorenhanced.net/dokuwiki/doku.php?id=item_func

VERSION::20250621
"""

import sys
from System.Collections.Generic import List
import time
import json

def get_basic_info(item):
    """Get basic item information available through direct API calls."""
    return {
        "Serial": hex(item.Serial),
        "ItemID": hex(item.ItemID),
        "Color": hex(item.Hue),
        "Position": f"({item.Position.X}, {item.Position.Y}, {item.Position.Z})",
        "Container": hex(item.Container) if item.Container else "None",
        "RootContainer": hex(item.RootContainer) if item.RootContainer else "None",
        "Amount": item.Amount,
        "IsContainer": item.IsContainer,
        "IsCorspe": item.IsCorspe,  # Note: This is the actual API spelling
        "IsCorpse": item.IsCorpse,
        "IsDoor": item.IsDoor,
        "IsResource": item.IsResource,
        "IsPotion": item.IsPotion,
        "IsVirtueShield": item.IsVirtueShield,
        "Weight": item.Weight
    }

def get_properties(item):
    """Get all available item properties."""
    Items.WaitForProps(item.Serial, 1000)
    props = Items.GetPropStringList(item.Serial)
    if not props:
        return []
    
    # Convert from List[string] to Python list
    return [str(prop) for prop in props]

def get_equipment_info(item):
    """Get equipment-specific information if item is equippable."""
    info = {}
    
    # Try to get layer information
    try:
        info["Layer"] = Items.GetLayer(item)
    except:
        info["Layer"] = "Unknown"
    
    # Check if item is currently equipped
    try:
        info["IsEquipped"] = Player.CheckLayer(item.Layer)
    except:
        info["IsEquipped"] = False
    
    return info

def get_container_contents(container):
    """Get information about container contents if item is a container."""
    if not container.IsContainer:
        return None
    
    contents = []
    items = Items.FindBySerial(container.Serial).Contains
    if items:
        for item in items:
            contents.append({
                "Serial": hex(item.Serial),
                "ItemID": hex(item.ItemID),
                "Name": Items.GetPropValue(item.Serial, 0) or "Unknown",
                "Amount": item.Amount
            })
    
    return contents

def inspect_item(item):
    """Perform deep inspection of a single item."""
    Misc.SendMessage(f"Inspecting item: {hex(item.Serial)}", 67)
    
    # Build comprehensive item data
    item_data = {
        "Basic Info": get_basic_info(item),
        "Properties": get_properties(item),
        "Equipment Info": get_equipment_info(item),
        "Contents": get_container_contents(item) if item.IsContainer else None
    }
    
    # Try to get name from properties
    try:
        item_data["Name"] = Items.GetPropValue(item.Serial, 0) or "Unknown"
    except:
        item_data["Name"] = "Unknown"
    
    # Additional special checks
    if item.IsPotion:
        item_data["Potion Type"] = "Unknown"  # Add specific potion type detection if needed
    
    if item.IsResource:
        item_data["Resource Type"] = "Unknown"  # Add specific resource type detection if needed
    
    return item_data

def print_item_data(data, indent=0):
    """Pretty print item data with proper indentation."""
    indent_str = "  " * indent
    
    for key, value in data.items():
        if isinstance(value, dict):
            Misc.SendMessage(f"{indent_str}{key}:", 67)
            print_item_data(value, indent + 1)
        elif isinstance(value, list):
            Misc.SendMessage(f"{indent_str}{key}:", 67)
            for item in value:
                if isinstance(item, dict):
                    print_item_data(item, indent + 1)
                else:
                    Misc.SendMessage(f"{indent_str}  {item}", 67)
        else:
            Misc.SendMessage(f"{indent_str}{key}: {value}", 67)

def inspect_backpack():
    """Main function to inspect all items in player's backpack."""
    if not Player.Backpack:
        Misc.SendMessage("No backpack found!", 33)
        return
    
    Misc.SendMessage("Starting backpack inspection...", 67)
    
    # Get all items in backpack
    items = Items.FindBySerial(Player.Backpack.Serial).Contains
    if not items:
        Misc.SendMessage("No items found in backpack!", 33)
        return
    
    # Create output directory if it doesn't exist
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    
    # Inspect each item
    all_items_data = []
    for item in items:
        try:
            item_data = inspect_item(item)
            all_items_data.append(item_data)
            print_item_data(item_data)
            Misc.SendMessage("-" * 40, 67)
        except Exception as e:
            Misc.SendMessage(f"Error inspecting item {hex(item.Serial)}: {str(e)}", 33)
    
    Misc.SendMessage(f"Inspection complete! Found {len(all_items_data)} items.", 67)
    
    # Save to JSON file for further analysis
    try:
        with open(f'item_inspection_{timestamp}.json', 'w') as f:
            json.dump(all_items_data, f, indent=2)
        Misc.SendMessage(f"Saved detailed output to item_inspection_{timestamp}.json", 67)
    except Exception as e:
        Misc.SendMessage(f"Error saving JSON file: {str(e)}", 33)

if __name__ == "__main__":
    inspect_backpack()
