"""
Development Item Inspector - a Razor Enhanced Python Script for Ultima Online

Returns information of all items in player's backpack writes to a JSON file
under the parent `data/` directory of this script.

Outputs information about:
- Basic item properties (ID, Color, etc)
- Extended properties (Name, Stats, etc)

Simple mode = only names , dedupe on , no properties = this is useful to check if we have crafting materials 
Full mode = all properties , no dedupe , all contents 

DOCUMENTATION:
https://razorenhanced.net/dokuwiki/doku.php?id=item_func

VERSION::20250621
"""
import time
import json
import os
import re

DEBUG_MODE = False     # print each item's details to chat; default off

# Simple
# Performance/verbosity controls
THROTTLE_MS = 100            # pause between item inspections
INCLUDE_PROPERTIES = True   # properties calls are expensive; default off
INCLUDE_CONTENTS = True     # container deep inspection; default off
INCLUDE_EQUIPMENT = False     # also gather equipped items if API available

# Output controls
DEDUP_UNIQUE_GRAPHIC_COLOR = False  # if True, only one per (ItemID, Hue)

OUTPUT_SERIAL = False
OUTPUT_POSITION = False
OUTPUT_IS_CONTAINER = False
OUTPUT_CONTAINER = False          # include Container id
OUTPUT_ROOT_CONTAINER = False     # include RootContainer id
OUTPUT_WEIGHT = False
OUTPUT_PROPERTIES = True         # include "Properties" key in JSON
OUTPUT_CONTENTS = False           # include "Contents" key in JSON

def fmt_hex4(val) -> str:
    """Format integer as 0xFFFF (4-digit, zero-padded, uppercase)."""
    try:
        n = int(val) & 0xFFFF
        return f"0x{n:04X}"
    except Exception:
        return str(val)

def _clean_leading_amount(name: str, amount: int) -> str:
    """Remove leading quantity prefixes like '10 Iron Ingot', '(10) Iron Ingot', '10x Iron Ingot'."""
    try:
        amt = int(amount)
    except Exception:
        return name
    if not name or amt <= 1:
        return name
    # Build regex matching common prefixes
    pattern = r'^\s*(?:\(|\[)?\s*' + re.escape(str(amt)) + r'\s*(?:\)|\])?\s*(?:x|×|X)?\s*[:\-*]?\s*'
    return re.sub(pattern, '', name).strip()

def get_item_name(item, amount_hint=None):
    """Best-effort item name using fast paths, then props as fallback."""
    try:
        nm = getattr(item, 'Name', None)
        if nm:
            nm = str(nm)
            return _clean_leading_amount(nm, amount_hint if amount_hint is not None else getattr(item, 'Amount', 1))
    except Exception:
        pass
    try:
        # First attempt: quick wait
        Items.WaitForProps(item.Serial, 400)
        props = Items.GetPropStringList(item.Serial)
        if props and len(props) > 0:
            nm = str(props[0])
            return _clean_leading_amount(nm, amount_hint if amount_hint is not None else getattr(item, 'Amount', 1))
        # Second attempt: trigger tooltip via single click
        Items.SingleClick(item.Serial)
        Misc.Pause(150)
        Items.WaitForProps(item.Serial, 600)
        props = Items.GetPropStringList(item.Serial)
        if props and len(props) > 0:
            nm = str(props[0])
            return _clean_leading_amount(nm, amount_hint if amount_hint is not None else getattr(item, 'Amount', 1))
        # Fallback to GetPropValue index 0
        name0 = Items.GetPropValue(item.Serial, 0)
        if name0:
            nm = str(name0)
            return _clean_leading_amount(nm, amount_hint if amount_hint is not None else getattr(item, 'Amount', 1))
    except Exception:
        pass
    return "Unknown"

def get_basic_info(item):
    """Get basic item information with per-field output control."""
    data = {
        "ItemID": fmt_hex4(item.ItemID),
        "Color": fmt_hex4(item.Hue),
        "Amount": item.Amount,
    }
    if OUTPUT_SERIAL:
        data["Serial"] = hex(item.Serial)
    if OUTPUT_POSITION:
        try:
            data["Position"] = f"({item.Position.X}, {item.Position.Y}, {item.Position.Z})"
        except Exception:
            data["Position"] = "(?, ?, ?)"
    if OUTPUT_CONTAINER:
        data["Container"] = hex(item.Container) if getattr(item, 'Container', 0) else "None"
    if OUTPUT_ROOT_CONTAINER:
        data["RootContainer"] = hex(item.RootContainer) if getattr(item, 'RootContainer', 0) else "None"
    if OUTPUT_IS_CONTAINER:
        data["IsContainer"] = bool(getattr(item, 'IsContainer', False))
    if OUTPUT_WEIGHT:
        data["Weight"] = getattr(item, 'Weight', 0)
    return data

def get_properties(item):
    """Get all available item properties (optional)."""
    if not INCLUDE_PROPERTIES:
        return []
    try:
        serial = item.Serial

        def to_list(lst):
            try:
                return [str(x) for x in (lst or [])]
            except Exception:
                return []

        def merge_preserve(existing, new_items):
            seen = set(existing)
            for s in new_items:
                if s and s not in seen:
                    existing.append(s)
                    seen.add(s)
            return existing

        collected = []

        # 1) Quick initial fetch
        try:
            Items.WaitForProps(serial, 400)
            collected = merge_preserve(collected, to_list(Items.GetPropStringList(serial)))
        except Exception:
            pass

        # 2) SingleClick retries with increasing waits (helps tooltips like spellbooks)
        try:
            attempts = 3
            waits = [600, 800, 1000]
            for i in range(attempts):
                try:
                    Items.SingleClick(serial)
                except Exception:
                    pass
                try:
                    Misc.Pause(150)
                except Exception:
                    pass
                try:
                    Items.WaitForProps(serial, waits[i] if i < len(waits) else 800)
                    props_list = to_list(Items.GetPropStringList(serial))
                    collected = merge_preserve(collected, props_list)
                except Exception:
                    continue
                # If we already have a healthy number of lines, stop early
                if len(collected) >= 6:
                    break
        except Exception:
            pass

        # 3) Index-based fallback to capture hidden lines
        try:
            for idx in range(0, 20):
                try:
                    v = Items.GetPropValue(serial, idx)
                except Exception:
                    v = None
                if not v:
                    # some clients return None after last valid index
                    break
                collected = merge_preserve(collected, [str(v)])
        except Exception:
            pass

        return collected
    except Exception:
        return []

def get_equipment_info(item):
    """Get equipment-specific information if item is equippable."""
    info = {}
    
    # Try to get layer information
    try:
        info["Layer"] = Items.GetLayer(item.Serial)
    except:
        info["Layer"] = "Unknown"
    
    # Check if item is currently equipped
    try:
        info["IsEquipped"] = Player.CheckLayer(item.Layer)
    except:
        info["IsEquipped"] = False
    
    return info

def get_equipped_items():
    """Collect equipped items using Layer enum if present, falling back to numeric layers.
    Returns (list_of_items, set_of_serials) for quick membership checks.
    """
    if not INCLUDE_EQUIPMENT:
        return [], set()
    equipped = []
    # Try common Layer-based API
    try:
        layer_names = [
            'RightHand','LeftHand','Shoes','Pants','Shirt','Helm','Gloves','Ring','Talisman',
            'Neck','Waist','Bracelet','Cloak','Robe','Earrings','Arms','Chest','Skirt','Dress','Sash','Apron'
        ]
        LayerClass = globals().get('Layer', None)
        for ln in layer_names:
            try:
                ly = getattr(LayerClass, ln, None) if LayerClass else None
                if ly is None:
                    continue
                it = Player.GetItemOnLayer(ly)
                if it:
                    equipped.append(it)
            except Exception:
                continue
    except Exception:
        pass
    # Fallback: probe numeric layers 1..30
    try:
        for ly in range(1, 31):
            try:
                it = Player.GetItemOnLayer(ly)
                if it:
                    equipped.append(it)
            except Exception:
                continue
    except Exception:
        pass
    # Deduplicate
    seen = set()
    dedup = []
    for it in equipped:
        try:
            s = int(it.Serial)
        except Exception:
            continue
        if s in seen:
            continue
        seen.add(s)
        dedup.append(it)
    return dedup, seen

def get_container_contents(container):
    """Get information about container contents if item is a container."""
    if (not INCLUDE_CONTENTS) or (not OUTPUT_CONTENTS) or (not container.IsContainer):
        return None
    
    contents = []
    items = Items.FindBySerial(container.Serial).Contains
    if items:
        for item in items:
            contents.append({
                "Serial": hex(item.Serial),
                "ItemID": hex(item.ItemID),
                "Name": get_item_name(item, amount_hint=getattr(item, 'Amount', 1)),
                "Amount": item.Amount
            })
    
    return contents

def inspect_item(item, is_equipped=False):
    """Perform deep inspection of a single item."""
    if DEBUG_MODE:
        Misc.SendMessage(f"Inspecting item: {hex(item.Serial)}", 67)
    
    # Build comprehensive item data
    item_data = {
        "Basic Info": get_basic_info(item)
    }
    if OUTPUT_PROPERTIES:
        item_data["Properties"] = get_properties(item)
    if OUTPUT_CONTENTS and INCLUDE_CONTENTS and item.IsContainer:
        item_data["Contents"] = get_container_contents(item)
    # Only attach equipment details for equipped items
    if is_equipped:
        item_data["Equipment Info"] = get_equipment_info(item)
    
    # Try to get name from properties and strip leading quantity
    item_data["Name"] = get_item_name(item, amount_hint=getattr(item, 'Amount', 1))
    
    # Additional special checks
    # Optional extras removed to reduce API calls
    
    return item_data

def print_item_data(data, indent=0):
    """Pretty print item data with proper indentation."""
    indent_str = "  " * indent
    
    for key, value in data.items():
        if isinstance(value, dict):
            if DEBUG_MODE:
                Misc.SendMessage(f"{indent_str}{key}:", 67)
            print_item_data(value, indent + 1)
        elif isinstance(value, list):
            if DEBUG_MODE:
                Misc.SendMessage(f"{indent_str}{key}:", 67)
            for item in value:
                if isinstance(item, dict):
                    print_item_data(item, indent + 1)
                else:
                    if DEBUG_MODE:
                        Misc.SendMessage(f"{indent_str}  {item}", 67)
        else:
            if DEBUG_MODE:
                Misc.SendMessage(f"{indent_str}{key}: {value}", 67)

def inspect_backpack():
    """Main function to inspect all items in player's backpack."""
    if not Player.Backpack:
        Misc.SendMessage("No backpack found!", 33)
        return
    
    Misc.SendMessage("Starting backpack inspection...", 67)
    
    # Get backpack items
    items = Items.FindBySerial(Player.Backpack.Serial).Contains
    items = list(items) if items else []

    # Optionally add equipped items via helper
    equipped_items, equipped_serials = ([], set())
    if INCLUDE_EQUIPMENT:
        equipped_items, equipped_serials = get_equipped_items()
        # Merge and dedup
        try:
            seen = set()
            merged = []
            for it in items + equipped_items:
                try:
                    s = int(it.Serial)
                except Exception:
                    continue
                if s in seen:
                    continue
                seen.add(s)
                merged.append(it)
            items = merged
        except Exception:
            pass
    # Optional dedup by (ItemID, Hue)
    if DEDUP_UNIQUE_GRAPHIC_COLOR and items:
        try:
            seen_gc = set()
            dedup_list = []
            for it in items:
                try:
                    key = (int(it.ItemID), int(it.Hue))
                except Exception:
                    continue
                if key in seen_gc:
                    continue
                seen_gc.add(key)
                dedup_list.append(it)
            items = dedup_list
        except Exception:
            pass

    if not items:
        Misc.SendMessage("No items found in backpack!", 33)
        return
    
    # Output path under parent data/ directory
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    here = os.path.abspath(os.path.dirname(__file__))
    project_root = os.path.abspath(os.path.join(here, os.pardir))
    data_dir = os.path.join(project_root, 'data')
    try:
        os.makedirs(data_dir, exist_ok=True)
    except Exception:
        pass
    
    # Inspect each item
    all_items_data = []
    for item in items:
        try:
            is_eq = int(item.Serial) in equipped_serials if INCLUDE_EQUIPMENT else False
            item_data = inspect_item(item, is_equipped=is_eq)
            all_items_data.append(item_data)
            if DEBUG_MODE:
                print_item_data(item_data)
                Misc.SendMessage("-" * 40, 67)
        except Exception as e:
            Misc.SendMessage(f"Error inspecting item {hex(item.Serial)}: {str(e)}", 33)
        # Throttle to avoid overloading client
        try:
            Misc.Pause(int(THROTTLE_MS))
        except Exception:
            time.sleep(THROTTLE_MS / 1000.0)
    
    Misc.SendMessage(f"Inspection complete! Found {len(all_items_data)} items.", 67)
    
    # Save to JSON file for further analysis
    out_path = os.path.join(data_dir, f'item_inspection_{timestamp}.json')
    try:
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(all_items_data, f, indent=2, ensure_ascii=False)
        Misc.SendMessage(f"Saved detailed output to {out_path}", 67)
    except Exception as e:
        Misc.SendMessage(f"Error saving JSON file: {str(e)}", 33)

if __name__ == "__main__":
    inspect_backpack()
