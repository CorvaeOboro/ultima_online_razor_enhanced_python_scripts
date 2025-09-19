"""
UI Action Buttons - a Razor Enhanced Python Script for Ultima Online

button layout for emotes , say , and scripts
a template for "macro like buttons" with added customization for size and color

edit ACTIONS with your favored emotes and scripts , all known emotes via "[emote" are listed below for reference

HOTKEY:: AutoStart on Login
VERSION::20250918
"""

import time
from collections import OrderedDict

DEBUG_MODE = False

BUTTON_STYLE = "small" # Use one of: "large", "small", "wide"

VERTICAL_ONLY = True           # If True, forces a single column layout

USE_ASPECT_PACKING = False     # If True, pack buttons within TARGET_GUMP_WIDTH/HEIGHT
TARGET_GUMP_WIDTH_RATIO = 16        # 16x9 wide aspect ratio 
TARGET_GUMP_HEIGHT_RATIO = 9       

# ACTIONS = macro like buttons of emotes say and scripts 
ACTIONS = OrderedDict([
    # Headers
    ("Header_Emotes", {"type": "header", "text": "_____  A C T I O N S  _____", "color_html": "222222", "height": 16}),
    #Say actions 
    ("Say_Hail", {"type": "say", "input": "Hail", "label": "Hail", "color": "white"}),
    # Emote actions 
    ("Emote_bow", {"type": "emote", "input": "bow", "label": "Bow", "color": "white"}),
    ("Emote_applaud", {"type": "emote", "input": "applaud", "label": "Applaud", "color": "gray"}),
    ("Emote_giggle", {"type": "emote", "input": "giggle", "label": "Giggle", "color": "gray"}),
    ("Emote_sacrifice", {"type": "emote", "input": "sacrifice", "label": "Sacrifice", "color": "blue"}),
    # Script actions 
    #("Header_Scripts", {"type": "header", "text": "SCRIPTS", "color_html": "224477", "height": 16}),
    ("Script_RITUAL_spiral.py", {"type": "script", "input": "RITUAL_spiral_round.py", "label": "Spiral", "color": "purple"}),
    ("Script_ITEM_weight_manager.py", {"type": "script", "input": "ITEM_weight_manager.py", "label": "Drop", "color": "red"}),
])

# Emote definitions: key = emote command name (after [emote ), value = display label
EMOTES = {
    # Core + confirmed set
    "ah": "Ah",                    
    "ahha": "Ahha",                
    "applaud": "Applaud",          
    "blownose": "Blow Nose",       
    "bow": "Bow",
    "bscough": "BS Cough",         
    "burp": "Burp",                
    "clearthroat": "Clear Throat", 
    "cough": "Cough",              
    "cry": "Cry",
    "faint": "Faint",              
    "fart": "Fart",
    "gasp": "Gasp",
    "giggle": "Giggle",
    "groan": "Groan",
    "growl": "Growl",
    "hey": "Hey",
    "hiccup": "Hiccup",            
    "huh": "Huh",
    "kiss": "Kiss",                
    "laugh": "Laugh",
    "no": "No",
    "oh": "Oh",
    "oooh": "Oooh",                
    "oops": "Oops",                
    "puke": "Puke",
    "punch": "Punch",
    "scream": "Scream",
    "shush": "Shush",
    "sigh": "Sigh",
    "slap": "Slap",
    "sneeze": "Sneeze",
    "sniff": "Sniff",
    "snore": "Snore",
    "spit": "Spit",
    "stickouttongue": "Stick Out Tongue",  
    "tapfoot": "Tap Foot",          
    "whistle": "Whistle",           
    "woohoo": "Woohoo",             
    "yawn": "Yawn",
    "yea": "Yea",
    "yell": "Yell",                 

    "sacrifice": "Sacrifice",       
    # Unlock-required emotes (may not work unless unlocked on shard)
    "fireworks": "Fireworks",       # requires unlock
    "juggle": "Juggle",             # requires unlock
    "diarrhea": "Diarrhea",         # requires unlock
    "parrot": "Parrot",             # requires unlock
    "insults": "Insults",           # requires unlock
    "snowballs": "Snowballs",       # requires unlock
}

# Font hex hue colors by name
FONT_COLORS = {
    "white": 0x0384,
    "gray": 0x0385,        # default
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

# Map style name -> (art_id, width, height)
BUTTON_STYLE_MAP = {
    "large": (1, 80, 40),    # closest to in-game "macro" button
    "small": (2443, 63, 23), # small wide button
    "wide": (2368, 80, 20), #  wide button
}

SIZE_FROM_ART = True #  If True, BUTTON_WIDTH/HEIGHT will be set from the selected style's size

# Default font color by name
FONT_COLOR_NAME = "gray"
FONT_HUE = FONT_COLORS.get(FONT_COLOR_NAME, 0x0385)

# Initial position , keep small for laptops
GUMP_START_X = 450
GUMP_START_Y = 450

#gump ID= 4294967295  = the max value , randomly select a high number gump so its unique
GUMP_ID = 4191917191

# Button sizing derives from selected BUTTON_STYLE (see _resolve_button_style) overridden at runtime by the style resolver.
BUTTON_WIDTH = 1
BUTTON_HEIGHT = 1
BUTTON_GAP_X = 0
BUTTON_GAP_Y = 1

# Background
PANEL_WIDTH_MIN = 0
PANEL_HEIGHT_MIN = 0

# darken button using AddImageTiled  
SLIVER_OVERLAY_ENABLED = True
SLIVER_OVERLAY_TILE_ART_ID = 2624   # dark tile used in other UIs
SLIVER_OVERLAY_MODE = "full"        # "full" to cover entire button, or "stripes" for top/bottom bands
SLIVER_STRIPE_HEIGHT = 6            # used when SLIVER_OVERLAY_MODE == "stripes"

# Click debounce 
_LAST_CLICK_BID = -1
_LAST_CLICK_TS = 0.0

#//======================================================================
def debug_message(msg, color=67):
    if DEBUG_MODE:
        try:
            Misc.SendMessage(f"[EMOTE_UI] {msg}", color)
        except Exception:
            pass

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

def _build_actions_from_config():
    """Return ACTIONS keys in insertion order and the list of clickable action keys.
    ACTIONS dict insertion order is the rendering order.
    """
    layout_keys_in_order = list(ACTIONS.keys())
    clickable_keys = [k for k in layout_keys_in_order if ACTIONS.get(k, {}).get("type") != "header"]
    return layout_keys_in_order, clickable_keys

def _resolve_button_style():
    """Resolve the currently selected BUTTON_STYLE into art id and optional size.
    Sets globals: BUTTON_ART_ID, (optionally) BUTTON_WIDTH, BUTTON_HEIGHT
    """
    try:
        art_id, w, h = BUTTON_STYLE_MAP.get(BUTTON_STYLE, BUTTON_STYLE_MAP.get("small"))
    except Exception:
        art_id, w, h = (2443, 63, 23)
    # Set art id globally (used by AddButton)
    globals()["BUTTON_ART_ID"] = art_id
    # Optionally override size from style
    if SIZE_FROM_ART:
        try:
            globals()["BUTTON_WIDTH"] = int(w)
            globals()["BUTTON_HEIGHT"] = int(h)
        except Exception:
            pass

def _compute_layout(number_of_buttons_to_render):
    """Compute the grid dimensions and overall gump dimensions based on layout toggles.
    - If VERTICAL_ONLY: one column with 'number_of_buttons_to_render' rows
    - Else if USE_ASPECT_PACKING: compute a grid that fits within TARGET_GUMP_WIDTH/HEIGHT
    Returns: (number_of_columns, number_of_rows, gump_width_pixels, gump_height_pixels)
    """
    if VERTICAL_ONLY or not number_of_buttons_to_render:
        number_of_columns = 1
        number_of_rows = max(1, number_of_buttons_to_render)
    elif USE_ASPECT_PACKING:
        # Compute the maximum columns and rows that fit in the target gump size
        # TARGET_GUMP_WIDTH and TARGET_GUMP_HEIGHT are aspect ratio multipliers
        # scaled from the current button dimensions to derive target pixel bounds.
        target_width_pixels = max(1, int(TARGET_GUMP_WIDTH_RATIO * BUTTON_WIDTH))
        target_height_pixels = max(1, int(TARGET_GUMP_HEIGHT_RATIO * BUTTON_HEIGHT))
        maximum_columns_by_width = max(1, int(target_width_pixels // max(1, BUTTON_WIDTH)))
        maximum_rows_by_height = max(1, int(target_height_pixels // max(1, BUTTON_HEIGHT)))

        number_of_columns = min(maximum_columns_by_width, number_of_buttons_to_render)
        number_of_rows = (number_of_buttons_to_render + number_of_columns - 1) // number_of_columns

        if number_of_rows > maximum_rows_by_height:
            number_of_columns = (number_of_buttons_to_render + maximum_rows_by_height - 1) // maximum_rows_by_height
            number_of_columns = max(1, min(number_of_columns, maximum_columns_by_width))
            number_of_rows = (number_of_buttons_to_render + number_of_columns - 1) // number_of_columns
    else:
        number_of_columns = 1
        number_of_rows = max(1, number_of_buttons_to_render)

    gump_width_pixels = max(PANEL_WIDTH_MIN, number_of_columns * BUTTON_WIDTH + (number_of_columns - 1) * BUTTON_GAP_X)
    content_height_pixels = number_of_rows * BUTTON_HEIGHT + (number_of_rows - 1) * BUTTON_GAP_Y
    gump_height_pixels = max(PANEL_HEIGHT_MIN, content_height_pixels)
    return number_of_columns, number_of_rows, gump_width_pixels, gump_height_pixels

def sendEmoteGump():
    # Resolve button style and art before computing layout
    _resolve_button_style()

    # Build universal action registry and layout
    layout_keys, clickable_keys = _build_actions_from_config()
    number_of_buttons_to_render = len(clickable_keys)

    # Compute base layout (columns/rows) from aspect targets
    layout_columns, _layout_rows_unused, _target_gump_width, _target_gump_height = _compute_layout(number_of_buttons_to_render)

    # Pre-compute exact total content height and maximum content width across sections
    total_content_height = 0
    max_content_width_pixels = 0
    current_section_action_count = 0
    for layout_key in layout_keys:
        entry = ACTIONS.get(layout_key, {})
        entry_type = entry.get("type")
        if entry_type == "header":
            # Close previous section block
            if current_section_action_count > 0:
                section_rows = (current_section_action_count + max(1, layout_columns) - 1) // max(1, layout_columns)
                total_content_height += section_rows * BUTTON_HEIGHT + max(0, section_rows - 1) * BUTTON_GAP_Y
                # Width used in this section equals up to layout_columns buttons
                section_cols_used = min(max(1, layout_columns), current_section_action_count)
                section_width_px = section_cols_used * BUTTON_WIDTH + (section_cols_used - 1) * BUTTON_GAP_X
                if section_width_px > max_content_width_pixels:
                    max_content_width_pixels = section_width_px
                current_section_action_count = 0
            # Add header height and section gap
            header_height = int(entry.get("height", 0))
            if header_height > 0:
                total_content_height += header_height
            gap_after = int(entry.get("gap_after", 0))
            total_content_height += max(0, gap_after)
            # Header width is full gump width; we will size gump to max_content_width_pixels later
        else:
            current_section_action_count += 1
    # Flush final section
    if current_section_action_count > 0:
        section_rows = (current_section_action_count + max(1, layout_columns) - 1) // max(1, layout_columns)
        total_content_height += section_rows * BUTTON_HEIGHT + max(0, section_rows - 1) * BUTTON_GAP_Y
        section_cols_used = min(max(1, layout_columns), current_section_action_count)
        section_width_px = section_cols_used * BUTTON_WIDTH + (section_cols_used - 1) * BUTTON_GAP_X
        if section_width_px > max_content_width_pixels:
            max_content_width_pixels = section_width_px

    # Final gump width/height tightly fit content
    gump_width = max(PANEL_WIDTH_MIN, max(BUTTON_WIDTH, max_content_width_pixels))
    gump_height = max(PANEL_HEIGHT_MIN, total_content_height)

    # Build gump
    gump_builder = Gumps.CreateGump(movable=True)
    Gumps.AddPage(gump_builder, 0)

    # Background sized to include all headers and sections 
    Gumps.AddBackground(gump_builder, 0, 0, gump_width, gump_height, 30546)
    Gumps.AddAlphaRegion(gump_builder, 0, 0, gump_width, gump_height)

    # Rendering state
    content_origin_x = 0
    current_draw_y = 0
    current_row_in_section = 0
    current_col_in_section = 0
    placed_actions_in_section = 0
    clickable_button_index = 0  # maps to clickable_keys order

    # Draw items
    for layout_key in layout_keys:
        entry = ACTIONS.get(layout_key, {})
        entry_type = entry.get("type")
        if entry_type == "header":
            # Before starting a new header, advance by the height of the previous section's rows
            if placed_actions_in_section > 0:
                section_rows = (placed_actions_in_section + max(1, layout_columns) - 1) // max(1, layout_columns)
                current_draw_y += section_rows * BUTTON_HEIGHT + max(0, section_rows - 1) * BUTTON_GAP_Y
                placed_actions_in_section = 0
            header_text = str(entry.get("text", ""))
            header_color_html = str(entry.get("color_html", "FFFFFF"))
            header_height = int(entry.get("height", 0))
            try:
                Gumps.AddHtml(gump_builder, 4, current_draw_y, max(0, gump_width - 8), header_height, f"<center><basefont color=#{header_color_html}>{header_text}</basefont></center>", 0, 0)
            except Exception:
                pass
            gap_after = int(entry.get("gap_after", 0))
            current_draw_y += header_height + max(0, gap_after)
            # Reset section row/col counters
            current_row_in_section = 0
            current_col_in_section = 0
            continue

        # Render an actionable button
        label_text = str(entry.get("label", entry.get("input", "")))
        color_name = str(entry.get("color", FONT_COLOR_NAME))
        label_hue = FONT_COLORS.get(color_name, FONT_HUE)

        # Position using section-local row/col and global layout_columns
        button_x = content_origin_x + current_col_in_section * (BUTTON_WIDTH + BUTTON_GAP_X)
        button_y = current_draw_y + current_row_in_section * (BUTTON_HEIGHT + BUTTON_GAP_Y)
        button_id = clickable_button_index + 1

        try:
            Gumps.AddButton(gump_builder, button_x, button_y, BUTTON_ART_ID, BUTTON_ART_ID, button_id, 1, 0)
        except Exception:
            Gumps.AddButton(gump_builder, button_x, button_y, 4005, 4006, button_id, 1, 0)

        if SLIVER_OVERLAY_ENABLED:
            try:
                if SLIVER_OVERLAY_MODE == "full":
                    Gumps.AddImageTiled(gump_builder, button_x, button_y, BUTTON_WIDTH, BUTTON_HEIGHT, SLIVER_OVERLAY_TILE_ART_ID)
                else:
                    stripe_h = max(1, int(SLIVER_STRIPE_HEIGHT))
                    Gumps.AddImageTiled(gump_builder, button_x, button_y, BUTTON_WIDTH, min(stripe_h, BUTTON_HEIGHT), SLIVER_OVERLAY_TILE_ART_ID)
                    bottom_y = button_y + max(0, BUTTON_HEIGHT - stripe_h)
                    Gumps.AddImageTiled(gump_builder, button_x, bottom_y, BUTTON_WIDTH, min(stripe_h, BUTTON_HEIGHT), SLIVER_OVERLAY_TILE_ART_ID)
            except Exception:
                pass

        add_centered_label_with_outline(gump_builder, button_x, button_y, BUTTON_WIDTH, BUTTON_HEIGHT, label_text, label_hue)

        # Advance section-local column/row
        clickable_button_index += 1
        placed_actions_in_section += 1
        current_col_in_section += 1
        if current_col_in_section >= max(1, layout_columns):
            current_col_in_section = 0
            current_row_in_section += 1

    Gumps.SendGump(GUMP_ID, Player.Serial, GUMP_START_X, GUMP_START_Y, gump_builder.gumpDefinition, gump_builder.gumpStrings)

def processActionInput():
    """Poll for gump interactions, handle action button clicks based on ACTIONS layout, and refresh the UI.
    Applies a short debounce so the same button id does not trigger repeatedly while the gump refreshes.
    Returns False to keep the main loop running.
    """
    # Ensure layout is in sync with current config and get clickable keys
    _layout_keys_in_order, clickable_keys = _build_actions_from_config()

    # Wait briefly for input without tearing down the gump; only refresh on click
    Gumps.WaitForGump(GUMP_ID, 500)
    gump_data = Gumps.GetGumpData(GUMP_ID)
    if not gump_data:
        return False

    button_identifier = int(getattr(gump_data, 'buttonid', 0))

    # Debounce: ignore repeated same button id within a short interval after refresh
    global _LAST_CLICK_BID, _LAST_CLICK_TS
    current_time_seconds = time.time()
    if button_identifier > 0 and button_identifier == _LAST_CLICK_BID and (current_time_seconds - _LAST_CLICK_TS) < 0.8:
        return False

    # Map button id to clickable action
    if 1 <= button_identifier <= len(clickable_keys):
        action_key = clickable_keys[button_identifier - 1]
        action_meta = ACTIONS.get(action_key, {})
        action_type = str(action_meta.get("type", "")).lower()
        action_input = str(action_meta.get("input", ""))

        try:
            _LAST_CLICK_BID = button_identifier
            _LAST_CLICK_TS = current_time_seconds
            if action_type == "emote":
                Player.ChatSay(f"[emote {action_input}")    # emote
                debug_message(f"Emote: {action_input}")
            elif action_type == "say":
                Player.ChatSay(action_input)                # say
                debug_message(f"Say: {action_input}") 
            elif action_type == "script":
                Misc.ScriptRun(action_input)                # script
                debug_message(f"Ran script: {action_input}") 
            else:
                debug_message(f"Unknown action type: {action_type}")
        except Exception as error:
            debug_message(f"Action error: {error}", 33)

        # Refresh the gump after a click 
        try:
            Gumps.CloseGump(GUMP_ID)
        except Exception:
            pass
        sendEmoteGump()

    return False

def main():
    sendEmoteGump()
    done = False
    while Player.Connected and not done:
        done = processActionInput()
        Misc.Pause(100)

if __name__ == "__main__":
    main()
