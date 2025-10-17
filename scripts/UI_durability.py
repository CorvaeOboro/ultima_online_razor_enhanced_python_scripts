
"""
UI Durability - a Razor Enhanced Python Script for Ultima Online

Display equipment durability in a minimal custom gump 

WARNING: this fails to get durability for spellbooks and other complex items due to the api read of the properties being limited to 4

STATUS:: WIP , working for some armor but not weapons due to item property limitations 
VERSION:: 20251015
"""

import re  # regex

DEBUG_MODE = False  # Send debug messages to client

SHOW_MINIMAL_PERCENT_ONLY = True   # Only show the percent number, no bars or names
INCLUDE_PERCENT_SYMBOL = False     # If True, append "%" to percent text
SHOW_LAYER_NAMES = False           # Show layer names label on the left
SHOW_ITEM_NAMES = False            # Show item names in tooltip (always available when hovered)
SHOW_BARS = False                  # Show a small fill bar behind the percent
SORT_ASCENDING = True              # Sort by lowest durability first

# Header / compact UI options
SHOW_HEADER = True                 # Show a small draggable header/title at the top
HEADER_TITLE = "Durability"       # Title text
HEADER_HEIGHT = 18                 # Header strip height

# Layer label shortening
USE_SHORT_LAYER_LABELS = True      # If SHOW_LAYER_NAMES is True, use very short labels from mapping below
# Single-letter (or ultra-short) mapping for compact label display
LAYER_SHORT_LABELS = {
    "RightHand": "R",
    "LeftHand": "L",
    "Shoes": "S",
    "Pants": "P",
    "Shirt": "T",       # Tunic/Shirt
    "Head": "H",
    "Gloves": "G",
    "Ring": "Rng",
    "Neck": "N",
    "Waist": "W",
    "InnerTorso": "IT",
    "Bracelet": "B",
    "MiddleTorso": "MT",
    "Earrings": "E",
    "Arms": "A",
    "Cloak": "C",
    "OuterTorso": "OT",
    "OuterLegs": "OL",
    "InnerLegs": "IL",
    "Talisman": "T",
}

# example=4294967295 #  a high pseudo-random gump id to avoid other existing gump ids
GUMP_ID = 3636346716

#GUMP
REFRESH_DURATION = 10000   # ms; also used as Gumps.WaitForGump timeout
ROW_HEIGHT = 20
GUMP_X = 700
GUMP_Y = 25
# Default/full width; actual width is computed per-layout for compact modes
GUMP_W = 230

# Compact-layout tuning (used to compute positions dynamically)
PAD_X = 8
MINIMAL_WIDTH_PERCENT_ONLY = 60     # Width when only showing percent values
MINIMAL_WIDTH_WITH_SHORT_LABEL = 110
PERCENT_COL_W = 30                  # Approximate width reserved for percent text

# Color 
COLOR = {
    "text": 2000,           # white
    "grey_dark": 2999,      # very dark grey (>= 20%)
    "grey_med": 2600,       # medium grey
    "grey_light": 2300,     # light grey (approaches white)
    "danger": 33,           # red for < 10%
}

# Layers order of Equipment
LAYERS = [
    "RightHand", "LeftHand",
    "Shoes", "Pants", "Shirt",
    "Head", "Gloves", "Ring", "Neck", "Waist",
    "InnerTorso", "Bracelet", "MiddleTorso", "Earrings", "Arms",
    "Cloak", "OuterTorso", "OuterLegs", "InnerLegs", "Talisman",
]

#//========================= Utilities =========================

def debug_message(msg, color=68):
    if not DEBUG_MODE:
        return
    try:
        Misc.SendMessage(f"[UI_DURA] {msg}", color)
    except Exception:
        try:
            print(f"[UI_DURA] {msg}")
        except Exception:
            pass

def proper_case(text: str) -> str:
    try:
        return " ".join(word.capitalize() for word in str(text).split())
    except Exception:
        return str(text)

def parse_item_durability(item):
    """Return (current_durability, max_durability) for an item by scanning its property lines. (0, 0) on failure."""
    try:
        Items.WaitForProps(item.Serial, 1000)
        property_lines = Items.GetPropStringList(item.Serial)
        if not property_lines:
            return 0, 0
        
        # Debug: Show all property lines for spellbooks
        item_name = getattr(item, 'Name', '')
        if 'spellbook' in str(item_name).lower():
            debug_message(f"  Property lines for {item_name}:")
            for i, line in enumerate(property_lines[:10]):  # Show first 10 lines
                debug_message(f"    [{i}] {line}")
        
        for property_line in property_lines:
            if not property_line:
                continue
            match = re.search(r"durability\s+(\d+)\s*/\s*(\d+)", str(property_line).lower())
            if match:
                return int(match.group(1)), int(match.group(2))
    except Exception as e:
        debug_message(f"  parse_item_durability error: {e}", 33)
    return 0, 0

def get_equipped_durability():
    """Return list of (layer_name, current_durability, max_durability, item_name) for equipped items having durability."""
    equipped_durability_rows = []
    for layer_name in LAYERS:
        try:
            equipped_item = Player.GetItemOnLayer(layer_name)
            if not equipped_item:
                continue
            
            item_name = proper_case(getattr(equipped_item, 'Name', '') or 'Item')
            
            # Debug: Check if this is a spellbook
            if 'spellbook' in item_name.lower():
                debug_message(f"Found spellbook on {layer_name}: {item_name} (0x{equipped_item.ItemID:04X})")
            
            current_durability, max_durability = parse_item_durability(equipped_item)
            
            # Debug: Show durability found
            if 'spellbook' in item_name.lower():
                debug_message(f"  Spellbook durability: {current_durability}/{max_durability}")
            
            if current_durability <= 0 and max_durability <= 0:
                continue
            
            equipped_durability_rows.append((layer_name, current_durability, max_durability, item_name))
        except Exception as e:
            debug_message(f"Error checking {layer_name}: {e}", 33)
            continue
    return equipped_durability_rows

def percent_to_hue(percentage):
    """Map percentage [0..100] to hue. Below 10 -> red. 10..40 -> lighter greys, >=40 -> dark grey."""
    try:
        if percentage < 10.0:
            return COLOR["danger"]
        if percentage >= 40.0:
            return COLOR["grey_dark"]
        if percentage < 20.0:
            return COLOR["grey_light"]
        if percentage < 30.0:
            return COLOR["grey_med"]
        return COLOR["grey_dark"]
    except Exception:
        return COLOR["text"]

def make_percent_text(percentage):
    percent_text = f"{percentage:.0f}"
    if INCLUDE_PERCENT_SYMBOL:
        return percent_text + "%"
    return percent_text

#//========================= UI Rendering =========================

def get_layer_label(layer_name: str) -> str:
    """Return label for a layer based on configuration. Either full layer name or short mapping."""
    try:
        if not SHOW_LAYER_NAMES:
            return ""
        if USE_SHORT_LAYER_LABELS:
            return LAYER_SHORT_LABELS.get(layer_name, layer_name[:1])
        return layer_name
    except Exception:
        return layer_name

def compute_layout(number_of_rows: int):
    """Compute compact layout measurements and positions based on enabled features."""
    try:
        # Decide width based on compactness
        if SHOW_MINIMAL_PERCENT_ONLY and not SHOW_LAYER_NAMES and not SHOW_BARS:
            width = MINIMAL_WIDTH_PERCENT_ONLY
        elif SHOW_MINIMAL_PERCENT_ONLY and SHOW_LAYER_NAMES and USE_SHORT_LAYER_LABELS and not SHOW_BARS:
            width = MINIMAL_WIDTH_WITH_SHORT_LABEL
        else:
            width = GUMP_W

        # Columns
        label_x = PAD_X
        percent_x = max(PAD_X, width - PAD_X - PERCENT_COL_W)

        # Bar area placed between label and percent if enabled
        if SHOW_BARS and not SHOW_MINIMAL_PERCENT_ONLY:
            bar_x = max(label_x + 50 if SHOW_LAYER_NAMES else PAD_X, PAD_X)
            bar_w = max(40, percent_x - bar_x - 6)
        else:
            bar_x = 0
            bar_w = 0

        header_h = HEADER_HEIGHT if SHOW_HEADER else 0
        content_y = header_h + 4 if header_h > 0 else 4
        total_h = content_y + (ROW_HEIGHT * number_of_rows) + 6

        return {
            "width": width,
            "label_x": label_x,
            "percent_x": percent_x,
            "bar_x": bar_x,
            "bar_w": bar_w,
            "header_h": header_h,
            "content_y": content_y,
            "total_h": total_h,
        }
    except Exception:
        # Fallback to legacy dimensions
        return {
            "width": GUMP_W,
            "label_x": 10,
            "percent_x": 180,
            "bar_x": 130,
            "bar_w": 90,
            "header_h": HEADER_HEIGHT if SHOW_HEADER else 0,
            "content_y": (HEADER_HEIGHT if SHOW_HEADER else 0) + 4,
            "total_h": ((HEADER_HEIGHT if SHOW_HEADER else 0) + 4) + (ROW_HEIGHT * number_of_rows) + 6,
        }

def draw_header(gump_data, layout):
    if not SHOW_HEADER:
        return
    try:
        # Simple header text; the whole gump is movable so header acts as a visual handle
        title_x = max(PAD_X, int(layout["width"] / 2) - max(0, len(HEADER_TITLE)) * 3)
        # Dark gray header using HTML
        header_html = f'<BASEFONT COLOR="#404040">{HEADER_TITLE}</BASEFONT>'
        Gumps.AddHtml(gump_data, title_x, 2, layout["width"] - title_x - PAD_X, HEADER_HEIGHT, header_html, False, False)
    except Exception:
        pass

def draw_rows(gump_data, durability_rows):
    sorted_rows_by_percent = sorted(
        durability_rows,
        key=lambda row: (row[1] / float(row[2])) if row[2] else 0.0,
        reverse=not SORT_ASCENDING,
    )
    number_of_rows = len(sorted_rows_by_percent)

    # Compute compact layout and background
    layout = compute_layout(number_of_rows)
    # Translucent black background
    Gumps.AddAlphaRegion(gump_data, 0, 0, layout["width"], layout["total_h"])

    # Header (visual handle)
    draw_header(gump_data, layout)

    for row_index, (layer_name, current_durability, max_durability, item_name) in enumerate(sorted_rows_by_percent):
        try:
            durability_fraction = (current_durability / float(max_durability)) if max_durability else 0.0
            durability_percent = max(0.0, min(100.0, durability_fraction * 100.0))
            row_y_position = layout["content_y"] + ROW_HEIGHT * row_index

            tooltip_msg = f"<BASEFONT COLOR=\"#FFFF00\">{item_name}</BASEFONT><BR />{current_durability} / {max_durability} ({durability_percent:.1f}%)"
            if SHOW_ITEM_NAMES:
                Gumps.AddTooltip(gump_data, tooltip_msg)

            # Optional layer name on the left
            if SHOW_LAYER_NAMES:
                try:
                    Gumps.AddLabel(gump_data, layout["label_x"], row_y_position, COLOR["text"], get_layer_label(layer_name))
                except Exception:
                    pass

            # Optional bar background + fill
            if SHOW_BARS and not SHOW_MINIMAL_PERCENT_ONLY:
                try:
                    Gumps.AddImageTiled(gump_data, layout["bar_x"], row_y_position + 2, layout["bar_w"], ROW_HEIGHT - 4, 40004)  # background
                    Gumps.AddImageTiled(gump_data, layout["bar_x"], row_y_position + 2, int(layout["bar_w"] * durability_fraction), ROW_HEIGHT - 4, 9354)  # fill
                except Exception:
                    pass

            # Percent text with HTML coloration - brightness increases as durability decreases
            percent_text = make_percent_text(durability_percent)
            # Calculate brightness: darker at 100%, brighter as approaching 0%
            # At 100%: #404040 (dark gray), at 0%: #FFFFFF (white)
            brightness = int(64 + (191 * (1.0 - durability_fraction)))  # 64 to 255
            if durability_percent < 10.0:
                # Critical - red
                color_html = "#FF3333"
            else:
                # Gray scale from dark to bright
                hex_val = f"{brightness:02X}"
                color_html = f"#{hex_val}{hex_val}{hex_val}"
            
            percent_html = f'<BASEFONT COLOR="{color_html}">{percent_text}</BASEFONT>'
            try:
                Gumps.AddHtml(gump_data, layout["percent_x"], row_y_position, PERCENT_COL_W, ROW_HEIGHT, percent_html, False, False)
            except Exception:
                pass
        except Exception:
            continue

#//========================= UI Class =========================

class DurabilityUI:
    def __init__(self):
        self.gump_id = GUMP_ID
        self.gump_x = GUMP_X
        self.gump_y = GUMP_Y
        self.update_interval_ms = REFRESH_DURATION
        self._last_durability_rows = None
        
    def get_durability_data(self):
        """Get current equipment durability data."""
        return get_equipped_durability()
    
    def draw_gump(self):
        """Build and send the durability gump."""
        try:
            durability_rows = self.get_durability_data()
            debug_message(f"Drawing gump with {len(durability_rows)} items")
            
            # Proceed to build and send the gump
            gump_data = Gumps.CreateGump(True, True, False, False)
            debug_message(f"CreateGump successful")
            Gumps.AddPage(gump_data, 0)
            draw_rows(gump_data, durability_rows)
            debug_message(f"draw_rows successful")
            
            try:
                Gumps.CloseGump(self.gump_id)
                Gumps.SendGump(self.gump_id, Player.Serial, 0, 0, gump_data.gumpDefinition, gump_data.gumpStrings)
                debug_message(f"SendGump successful - gump should be moveable", 68)
            except Exception as e:
                # On failure, do not spam retries; wait until next update cycle
                debug_message(f"SendGump error: {e}", 33)
            
            # Store current data
            self._last_durability_rows = durability_rows
            
        except Exception as e:
            debug_message(f"draw_gump error: {e}", 33)
    
    def update(self):
        """Update loop tick: pause, check data, redraw if changed."""
        try:
            Misc.Pause(self.update_interval_ms)
        except Exception:
            pass
        
        # Get current data
        durability_rows = self.get_durability_data()
        
        # Redraw if data changed
        if durability_rows != self._last_durability_rows:
            self.draw_gump()

#//========================= Main =========================

def main():
    debug_message("Durability UI starting...")
    ui = DurabilityUI()
    
    # Initial draw
    ui.draw_gump()
    
    # Update loop - runs continuously
    while True:
        ui.update()

main()