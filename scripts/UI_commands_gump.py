"""
UI Commands Gump - a Razor Enhanced Python Script for Ultima Online

Build a clickable gump from the shard's say commands , somtimes viewbable by "[help" or "[helpinfo"
Each button sends a chat-say with a leading '[' to trigger the  command.

HOTKEY:: AutoStart on Login
VERSION::20251012
"""

import time
from collections import OrderedDict

DEBUG_MODE = False

BUTTON_STYLE = "large"  # Use one of: "large", "small", "wide"
VERTICAL_ONLY = False    # If True, forces a single column layout
USE_ASPECT_PACKING = True
TARGET_GUMP_WIDTH_RATIO = 16
TARGET_GUMP_HEIGHT_RATIO = 9

# Header configuration (single title at the top)
HEADER_ENABLED = True
HEADER_TEXT = "___  C O M M A N D S  ___"
# Darker, less bright header color for better readability
HEADER_COLOR_HTML = "222222"
HEADER_HEIGHT = 16            
HEADER_GAP_AFTER = 0 # no padding

# Font hex hue colors by name 
FONT_COLORS = {
    "white": 0x0384,
    "gray": 0x0385,
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

# Map style name -> (art_id, width, height) these are gump graphics , we are using them for the size , they are being covered by overlay
BUTTON_STYLE_MAP = {
    "large": (1, 80, 40),
    "small": (2443, 63, 23),
    "wide": (2368, 80, 20),
}

SIZE_FROM_ART = True
FONT_COLOR_NAME = "gray"
FONT_HUE = FONT_COLORS.get(FONT_COLOR_NAME, 0x0385)

# Initial position
GUMP_START_X = 300
GUMP_START_Y = 300
GUMP_ID = 4191917201  # unique-ish

BUTTON_WIDTH = 1
BUTTON_HEIGHT = 1
BUTTON_GAP_X = 0
BUTTON_GAP_Y = 1

# Background panel sizes (auto-sized by content)
PANEL_WIDTH_MIN = 0
PANEL_HEIGHT_MIN = 0

# Optional overlay to darken buttons
SLIVER_OVERLAY_ENABLED = True
SLIVER_OVERLAY_TILE_ART_ID = 2624
SLIVER_OVERLAY_MODE = "full"  # or "stripes"
SLIVER_STRIPE_HEIGHT = 6

# Debounce
_LAST_CLICK_BID = -1
_LAST_CLICK_TS = 0.0

# ===================================================================================
# Commands configuration (structured like ACTIONS in UI_action_buttons.py)
# Each non-header entry will be invoked as Player.ChatSay(f"[{input}")
# type: "header" | "command"
# fields for command: input, label, color
# ===================================================================================
COMMAND_SECTIONS = OrderedDict([
    # Top header bar for the gump itself (kept subtle by global HEADER_* settings)
    ("Header_Commands", {"type": "header", "text": "_____  C O M M A N D S  _____", "color_html": "222222", "height": 16, "gap_after": 2}),

    # Chat & Social
    ("Header_Chat", {"type": "header", "text": "Chat & Social", "color_html": "666666", "height": 14, "gap_after": 2}),
    ("cmd_Chat", {"type": "command", "input": "Chat", "label": "Chat", "color": "light_blue"}),
    ("cmd_ChatToggle", {"type": "command", "input": "ChatToggle", "label": "Chat Toggle", "color": "light_blue"}),
    ("cmd_ChatRules", {"type": "command", "input": "ChatRules", "label": "Chat Rules", "color": "light_blue"}),
    ("cmd_Emote", {"type": "command", "input": "emote", "label": "Emotes", "color": "aqua"}),
    ("cmd_SayC", {"type": "command", "input": "C", "label": "C", "color": "aqua"}),
    ("cmd_Saye", {"type": "command", "input": "e", "label": "e", "color": "aqua"}),
    ("cmd_SayP", {"type": "command", "input": "P", "label": "P", "color": "aqua"}),
    ("cmd_SayT", {"type": "command", "input": "T", "label": "T", "color": "aqua"}),

    # Info & Help
    ("Header_Info", {"type": "header", "text": "Info / Help", "color_html": "666666", "height": 14, "gap_after": 2}),
    ("cmd_Help", {"type": "command", "input": "Help", "label": "Help", "color": "yellow"}),
    ("cmd_HelpInfo", {"type": "command", "input": "HelpInfo", "label": "Help Info", "color": "yellow"}),
    ("cmd_Options", {"type": "command", "input": "options", "label": "Options", "color": "yellow"}),
    ("cmd_StatGump", {"type": "command", "input": "StatGump", "label": "Stats", "color": "beige"}),
    ("cmd_Skills", {"type": "command", "input": "Skills", "label": "Skills", "color": "beige"}),
    ("cmd_Time", {"type": "command", "input": "Time", "label": "Time", "color": "beige"}),
    ("cmd_TimeStamp", {"type": "command", "input": "TimeStamp", "label": "TimeStamp", "color": "beige"}),
    ("cmd_WhatIsIt", {"type": "command", "input": "WhatIsIt", "label": "What Is It", "color": "beige"}),
    ("cmd_whatisthis", {"type": "command", "input": "whatisthis", "label": "What Is This", "color": "beige"}),
    ("cmd_FishMongerStatus", {"type": "command", "input": "FishMongerStatus", "label": "FishMonger", "color": "teal"}),
    ("cmd_RegionStatus", {"type": "command", "input": "RegionStatus", "label": "Region", "color": "teal"}),

    # Guild / Regions
    ("Header_Guild", {"type": "header", "text": "Guild / Regions", "color_html": "666666", "height": 14, "gap_after": 2}),
    ("cmd_FindGuild", {"type": "command", "input": "FindGuild", "label": "Find Guild", "color": "green"}),
    ("cmd_GuildApps", {"type": "command", "input": "GuildApps", "label": "Guild Apps", "color": "green"}),
    ("cmd_GuildRegions", {"type": "command", "input": "GuildRegions", "label": "Guild Regions", "color": "green"}),
    ("cmd_HavenAreas", {"type": "command", "input": "HavenAreas", "label": "Haven Areas", "color": "green"}),

    # PvP / Combat
    ("Header_PvP", {"type": "header", "text": "PvP / Combat", "color_html": "666666", "height": 14, "gap_after": 2}),
    ("cmd_Disarm", {"type": "command", "input": "Disarm", "label": "Disarm", "color": "red"}),
    ("cmd_Hamstring", {"type": "command", "input": "Hamstring", "label": "Hamstring", "color": "red"}),
    ("cmd_Hellfire", {"type": "command", "input": "Hellfire", "label": "Hellfire", "color": "red"}),
    ("cmd_Taunt", {"type": "command", "input": "Taunt", "label": "Taunt", "color": "red"}),
    ("cmd_stun", {"type": "command", "input": "stun", "label": "Stun", "color": "red"}),
    ("cmd_togglepvp", {"type": "command", "input": "togglepvp", "label": "Toggle PvP", "color": "orange"}),
    ("cmd_togglepvpwarning", {"type": "command", "input": "togglepvpwarning", "label": "PvP Warning", "color": "orange"}),
    ("cmd_PvPRanks", {"type": "command", "input": "PvPRanks", "label": "PvP Ranks", "color": "orange"}),
    ("cmd_pouch", {"type": "command", "input": "pouch", "label": "Pouch", "color": "maroon"}),
    ("cmd_pp", {"type": "command", "input": "pp", "label": "PP", "color": "maroon"}),

    # Quests / Events / Seasonal
    ("Header_Quests", {"type": "header", "text": "Quests / Events", "color_html": "666666", "height": 14, "gap_after": 2}),
    ("cmd_Quest", {"type": "command", "input": "quest", "label": "Quest", "color": "purple"}),
    ("cmd_QuestRanking", {"type": "command", "input": "QuestRanking", "label": "Quest Rank", "color": "purple"}),
    ("cmd_Expedition", {"type": "command", "input": "Expedition", "label": "Expedition", "color": "purple"}),
    ("cmd_GlobalQuest", {"type": "command", "input": "GlobalQuest", "label": "Global Quest", "color": "purple"}),
    ("cmd_GQ", {"type": "command", "input": "GQ", "label": "GQ", "color": "purple"}),
    ("cmd_GR", {"type": "command", "input": "GR", "label": "GR", "color": "purple"}),
    ("cmd_GS", {"type": "command", "input": "GS", "label": "GS", "color": "purple"}),
    ("cmd_Halloween", {"type": "command", "input": "Halloween", "label": "Halloween", "color": "purple"}),
    ("cmd_Krampus", {"type": "command", "input": "Krampus", "label": "Krampus", "color": "purple"}),
    ("cmd_ClaimRewards", {"type": "command", "input": "ClaimRewards", "label": "Rewards", "color": "gold"}),
    ("cmd_Raffle", {"type": "command", "input": "Raffle", "label": "Raffle", "color": "gold"}),

    # Economy / Store / Leaderboards
    ("Header_Econ", {"type": "header", "text": "Economy & Store", "color_html": "666666", "height": 14, "gap_after": 2}),
    ("cmd_Store", {"type": "command", "input": "Store", "label": "Store", "color": "gold"}),
    ("cmd_shop", {"type": "command", "input": "shop", "label": "Shop", "color": "gold"}),
    ("cmd_GiveGold", {"type": "command", "input": "GiveGold", "label": "Give Gold", "color": "yellow"}),
    ("cmd_GiveResources", {"type": "command", "input": "GiveResources", "label": "Give Resources", "color": "yellow"}),
    ("cmd_leaderboard", {"type": "command", "input": "leaderboard", "label": "Leaderboard", "color": "light_blue"}),
    ("cmd_lb", {"type": "command", "input": "lb", "label": "LB", "color": "light_blue"}),
    ("cmd_rankings", {"type": "command", "input": "rankings", "label": "Rankings", "color": "light_blue"}),
    ("cmd_ranks", {"type": "command", "input": "ranks", "label": "Ranks", "color": "light_blue"}),

    # Utility / Misc
    ("Header_Utility", {"type": "header", "text": "Utility / Misc", "color_html": "666666", "height": 14, "gap_after": 2}),
    ("cmd_fixme", {"type": "command", "input": "fixme", "label": "FixMe", "color": "gray"}),
    ("cmd_Notice", {"type": "command", "input": "Notice", "label": "Notice", "color": "gray"}),
    ("cmd_Rules", {"type": "command", "input": "Rules", "label": "Rules", "color": "gray"}),
    ("cmd_Toolbar", {"type": "command", "input": "Toolbar", "label": "Toolbar", "color": "gray"}),
    ("cmd_quivergump", {"type": "command", "input": "quivergump", "label": "Quiver", "color": "green"}),
    ("cmd_VetKit", {"type": "command", "input": "VetKit", "label": "Vet Kit", "color": "green"}),
    ("cmd_Password", {"type": "command", "input": "Password", "label": "Password", "color": "brown"}),
    ("cmd_Email", {"type": "command", "input": "Email", "label": "Email", "color": "brown"}),
    ("cmd_Insurance", {"type": "command", "input": "Insurance", "label": "Insurance", "color": "brown"}),
    ("cmd_Join", {"type": "command", "input": "Join", "label": "Join", "color": "brown"}),
    ("cmd_job", {"type": "command", "input": "job", "label": "Job", "color": "brown"}),
    ("cmd_Legacy", {"type": "command", "input": "Legacy", "label": "Legacy", "color": "dark_gray"}),
    ("cmd_Bilgewater", {"type": "command", "input": "Bilgewater", "label": "Bilgewater", "color": "dark_gray"}),
    ("cmd_compendium", {"type": "command", "input": "compendium", "label": "Compendium", "color": "dark_gray"}),
    ("cmd_Event", {"type": "command", "input": "Event", "label": "Event", "color": "dark_gray"}),
    ("cmd_FindHealer", {"type": "command", "input": "FindHealer", "label": "Find Healer", "color": "green"}),
    ("cmd_GetSpecialHue", {"type": "command", "input": "GetSpecialHue", "label": "Special Hue", "color": "light_blue"}),
    ("cmd_Hunger", {"type": "command", "input": "Hunger", "label": "Hunger", "color": "orange"}),
    ("cmd_Notice2", {"type": "command", "input": "Notice", "label": "Notice", "color": "gray"}),
    ("cmd_RegionStatus2", {"type": "command", "input": "RegionStatus", "label": "Region", "color": "teal"}),
    ("cmd_Challenge", {"type": "command", "input": "Challenge", "label": "Challenge", "color": "red"}),
    ("cmd_BossDamage", {"type": "command", "input": "BossDamage", "label": "BossDamage", "color": "red"}),
    ("cmd_BossDmg", {"type": "command", "input": "BossDmg", "label": "BossDmg", "color": "red"}),
    ("cmd_Toolbar2", {"type": "command", "input": "Toolbar", "label": "Toolbar", "color": "gray"}),
    ("cmd_Store2", {"type": "command", "input": "Store", "label": "Store", "color": "gold"}),
])

def _build_commands_from_config():
    """Return layout keys in order and the list of clickable command keys."""
    layout_keys = list(COMMAND_SECTIONS.keys())
    clickable_keys = [k for k in layout_keys if COMMAND_SECTIONS.get(k, {}).get("type") != "header"]
    return layout_keys, clickable_keys

# ===================================================================================
# Utilities from the reference UI
# ===================================================================================

def debug_message(msg, color=67):
    if DEBUG_MODE:
        try:
            Misc.SendMessage(f"[CMD_UI] {msg}", color)
        except Exception:
            pass

def add_centered_label_with_outline(gd, x, y, w, h, text, hue):
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

def _resolve_button_style():
    try:
        art_id, w, h = BUTTON_STYLE_MAP.get(BUTTON_STYLE, BUTTON_STYLE_MAP.get("small"))
    except Exception:
        art_id, w, h = (2443, 63, 23)
    globals()["BUTTON_ART_ID"] = art_id
    if SIZE_FROM_ART:
        try:
            globals()["BUTTON_WIDTH"] = int(w)
            globals()["BUTTON_HEIGHT"] = int(h)
        except Exception:
            pass

def _compute_layout(n_buttons):
    if VERTICAL_ONLY or not n_buttons:
        cols = 1
        rows = max(1, n_buttons)
    elif USE_ASPECT_PACKING:
        target_w = max(1, int(TARGET_GUMP_WIDTH_RATIO * BUTTON_WIDTH))
        target_h = max(1, int(TARGET_GUMP_HEIGHT_RATIO * BUTTON_HEIGHT))
        max_cols_by_w = max(1, int(target_w // max(1, BUTTON_WIDTH)))
        max_rows_by_h = max(1, int(target_h // max(1, BUTTON_HEIGHT)))
        cols = min(max_cols_by_w, n_buttons)
        rows = (n_buttons + cols - 1) // cols
        if rows > max_rows_by_h:
            cols = (n_buttons + max_rows_by_h - 1) // max_rows_by_h
            cols = max(1, min(cols, max_cols_by_w))
            rows = (n_buttons + cols - 1) // cols
    else:
        cols = 1
        rows = max(1, n_buttons)
    gump_w = max(PANEL_WIDTH_MIN, cols * BUTTON_WIDTH + (cols - 1) * BUTTON_GAP_X)
    content_h = rows * BUTTON_HEIGHT + (rows - 1) * BUTTON_GAP_Y
    gump_h = max(PANEL_HEIGHT_MIN, content_h)
    return cols, rows, gump_w, gump_h

# ===================================================================================
# Gump build + input
# ===================================================================================

def sendCommandsGump():
    _resolve_button_style()

    # Build layout and clickable from config
    layout_keys, clickable_keys = _build_commands_from_config()

    # Determine columns based on aspect packing using number of clickable items only
    num_buttons = len(clickable_keys)
    layout_columns, _layout_rows_unused, _target_w, _target_h = _compute_layout(num_buttons)

    # Precompute total height and max width across sections, including top header bar
    total_content_height = 0
    max_content_width = 0
    actions_in_section = 0

    # Account for global header bar at top if enabled
    header_total_h = (HEADER_HEIGHT + max(0, HEADER_GAP_AFTER)) if HEADER_ENABLED else 0
    total_content_height += header_total_h

    for key in layout_keys:
        entry = COMMAND_SECTIONS.get(key, {})
        etype = entry.get("type")
        if etype == "header":
            # close previous section
            if actions_in_section > 0:
                rows = (actions_in_section + max(1, layout_columns) - 1) // max(1, layout_columns)
                total_content_height += rows * BUTTON_HEIGHT + max(0, rows - 1) * BUTTON_GAP_Y
                cols_used = min(max(1, layout_columns), actions_in_section)
                section_w = cols_used * BUTTON_WIDTH + (cols_used - 1) * BUTTON_GAP_X
                if section_w > max_content_width:
                    max_content_width = section_w
                actions_in_section = 0
            # header line height and gap
            h = int(entry.get("height", 0))
            if h > 0:
                total_content_height += h
            total_content_height += max(0, int(entry.get("gap_after", 0)))
        else:
            actions_in_section += 1
    # flush last section
    if actions_in_section > 0:
        rows = (actions_in_section + max(1, layout_columns) - 1) // max(1, layout_columns)
        total_content_height += rows * BUTTON_HEIGHT + max(0, rows - 1) * BUTTON_GAP_Y
        cols_used = min(max(1, layout_columns), actions_in_section)
        section_w = cols_used * BUTTON_WIDTH + (cols_used - 1) * BUTTON_GAP_X
        if section_w > max_content_width:
            max_content_width = section_w

    # Gump dimensions
    gump_w = max(PANEL_WIDTH_MIN, max(BUTTON_WIDTH, max_content_width))
    gump_h = max(PANEL_HEIGHT_MIN, total_content_height)

    gd = Gumps.CreateGump(movable=True)
    Gumps.AddPage(gd, 0)
    Gumps.AddBackground(gd, 0, 0, gump_w, gump_h, 30546)
    # Alpha region: below the top draggable bar
    if header_total_h > 0:
        Gumps.AddAlphaRegion(gd, 0, header_total_h, gump_w, max(0, gump_h - header_total_h))
    else:
        Gumps.AddAlphaRegion(gd, 0, 0, gump_w, gump_h)

    # Draw global header bar
    if HEADER_ENABLED:
        try:
            Gumps.AddImageTiled(gd, 0, 0, gump_w, HEADER_HEIGHT, SLIVER_OVERLAY_TILE_ART_ID)
            Gumps.AddHtml(gd, 4, 1, max(0, gump_w - 8), max(1, HEADER_HEIGHT - 2),
                          f"<center><basefont color=#{HEADER_COLOR_HTML}><b>{HEADER_TEXT}</b></basefont></center>", 0, 0)
            Gumps.AddImageTiled(gd, 0, HEADER_HEIGHT - 1, gump_w, 1, SLIVER_OVERLAY_TILE_ART_ID)
        except Exception:
            pass

    current_y = header_total_h
    current_col = 0
    current_row = 0
    placed_in_section = 0
    clickable_index = 0

    for key in layout_keys:
        entry = COMMAND_SECTIONS.get(key, {})
        etype = entry.get("type")
        if etype == "header":
            # advance past previous section's rows
            if placed_in_section > 0:
                rows = (placed_in_section + max(1, layout_columns) - 1) // max(1, layout_columns)
                current_y += rows * BUTTON_HEIGHT + max(0, rows - 1) * BUTTON_GAP_Y
                placed_in_section = 0
                current_col = 0
                current_row = 0
            # draw section header
            h_text = str(entry.get("text", ""))
            h_color = str(entry.get("color_html", "666666"))
            h = int(entry.get("height", 0))
            try:
                Gumps.AddHtml(gd, 4, current_y, max(0, gump_w - 8), h, f"<center><basefont color=#{h_color}>{h_text}</basefont></center>", 0, 0)
            except Exception:
                pass
            current_y += h + max(0, int(entry.get("gap_after", 0)))
            continue

        # draw a command button
        label_text = str(entry.get("label", entry.get("input", "")))
        color_name = str(entry.get("color", "gray"))
        label_hue = FONT_COLORS.get(color_name, FONT_HUE)

        x = current_col * (BUTTON_WIDTH + BUTTON_GAP_X)
        y = current_y + current_row * (BUTTON_HEIGHT + BUTTON_GAP_Y)
        bid = clickable_index + 1
        try:
            Gumps.AddButton(gd, x, y, BUTTON_ART_ID, BUTTON_ART_ID, bid, 1, 0)
        except Exception:
            Gumps.AddButton(gd, x, y, 4005, 4006, bid, 1, 0)

        if SLIVER_OVERLAY_ENABLED:
            try:
                if SLIVER_OVERLAY_MODE == "full":
                    Gumps.AddImageTiled(gd, x, y, BUTTON_WIDTH, BUTTON_HEIGHT, SLIVER_OVERLAY_TILE_ART_ID)
                else:
                    sh = max(1, int(SLIVER_STRIPE_HEIGHT))
                    Gumps.AddImageTiled(gd, x, y, BUTTON_WIDTH, min(sh, BUTTON_HEIGHT), SLIVER_OVERLAY_TILE_ART_ID)
                    bottom_y = y + max(0, BUTTON_HEIGHT - sh)
                    Gumps.AddImageTiled(gd, x, bottom_y, BUTTON_WIDTH, min(sh, BUTTON_HEIGHT), SLIVER_OVERLAY_TILE_ART_ID)
            except Exception:
                pass

        add_centered_label_with_outline(gd, x, y, BUTTON_WIDTH, BUTTON_HEIGHT, label_text, label_hue)

        clickable_index += 1
        placed_in_section += 1
        current_col += 1
        if current_col >= max(1, layout_columns):
            current_col = 0
            current_row += 1

    Gumps.SendGump(GUMP_ID, Player.Serial, GUMP_START_X, GUMP_START_Y, gd.gumpDefinition, gd.gumpStrings)


def processCommandInput():
    # Build clickable mapping from current config
    _layout_keys, clickable_keys = _build_commands_from_config()

    Gumps.WaitForGump(GUMP_ID, 500)
    data = Gumps.GetGumpData(GUMP_ID)
    if not data:
        return False

    bid = int(getattr(data, 'buttonid', 0))

    global _LAST_CLICK_BID, _LAST_CLICK_TS
    now = time.time()
    if bid > 0 and bid == _LAST_CLICK_BID and (now - _LAST_CLICK_TS) < 0.8:
        return False

    if 1 <= bid <= len(clickable_keys):
        key = clickable_keys[bid - 1]
        meta = COMMAND_SECTIONS.get(key, {})
        cmd_input = str(meta.get("input", "")).strip()
        try:
            _LAST_CLICK_BID = bid
            _LAST_CLICK_TS = now
            if cmd_input:
                Player.ChatSay(f"[{cmd_input}")
                debug_message(f"Command: {cmd_input}")
        except Exception as e:
            debug_message(f"Command error: {e}", 33)
        try:
            Gumps.CloseGump(GUMP_ID)
        except Exception:
            pass
        sendCommandsGump()
    return False


def main():
    sendCommandsGump()
    done = False
    while Player.Connected and not done:
        done = processCommandInput()
        Misc.Pause(100)


if __name__ == "__main__":
    main()
