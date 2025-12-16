"""
QUEST global events - a Razor Enhanced Python script for Ultima Online

Display combined information about global events , event points , danger , haven , and challenge combined .
Opens and get info from the global events gumps, display claim button , and colorized border based on status .

Global Events Information:
- Command: "[event" opens the main event menu gump
- Individual event gumps details have unique IDs and button mappings
For each event , Click corresponding event button on EVENTS_LIST_GUMP_ID (0x9564fc6d)
   - Detail gump opens (hides events list underneath) , Read detail gump data , Press back button (button 0) on detail gump
   - Events list revealed again (was never closed) , Continue to next event
Close all gumps at end
- Claim button (button 1) available when points >= 50
- Confirmation gump (ID: 0x11775c2e) with button 1 to confirm

Auto-Claim ( off by default ) config by target number of points , saving specific events for higher rewards ( 750 )

STATUS:: WIP
VERSION:: 20251027
"""

import re
import os
import json
import time

DEBUG_MODE = False
SKIP_SEASONAL_EVENTS = True  # Skip seasonal events 
AUTO_CLAIM_ENABLED = False
SHOW_ZONE_STATUS_BORDER = True  # Show colored border behind event names (red=danger, blue=safe)
USE_DYNAMIC_ZONE_STATUS = True  # Read zone status from [rotation and [HavenAreas and [Challenge gumps

# Events not in this dict will NOT be auto-claimed 
AUTO_CLAIM_CONFIG = {
    'Delucia': 50,      # 
    'Shame': 50,        # 
    'Luna': 750,        # skin dye
    'Sandstorm': 50,    # 
    'Destard': 50,      # 
    'Bilgewater': 50,   # 
    'Doom': 50,         # ???
    'Deceit': 750,      # 750 Doom Key
    'Eventide': 50,     # 
    'Wrong': 750,       # skin dye
    'Exile': 50,        # 
}

# JSON Export Configuration
EXPORT_TO_JSON = False  # Export all extracted gump data to JSON
BASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
OUTPUT_FILE = os.path.join(BASE_PATH, "global_events_data.json")

EVENT_PAGE_BUTTONS = list(range(10, 170, 10))  # [10, 20, 30, ..., 150, 160]

KNOWN_EVENTS_BUTTON_ID = {
    10: 'Delucia',
    20: 'Shame',
    30: 'Luna',
    40: 'Valentines',
    50: 'Sandstorm',
    60: 'Easter',
    70: 'StPatrick',
    80: 'Destard',
    90: 'Bilgewater',
    100: 'Doom',
    110: 'Krampus',
    120: 'Deceit',
    130: 'Eventide',
    140: 'Wrong',
    150: 'Halloween',
    160: 'Exile',
}

# Seasonal events (can be skipped with SKIP_SEASONAL_EVENTS flag)
SEASONAL_EVENTS = {
    40: 'Valentines',    # Valentine's Day
    60: 'Easter',        # Easter
    70: 'StPatrick',     # St. Patrick's Day
    110: 'Krampus',      # Christmas/Winter
    150: 'Halloween',    # Halloween
}

# Event display configuration - colors, formatting, and item IDs with positioning
EVENT_DISPLAY_CONFIG = {
    'Delucia': {
        'display_name': 'DELUCIA',
        'color': '#FFD700',  # Gold
        'main_icon': {'item_id': 0x0E76, 'hue': 0, 'offset_x': 0, 'offset_y': 5},  # Bag
        'reward_icon': {'item_id': 45241, 'hue': 0, 'offset_x': 0, 'offset_y': -5}  # Triceratops
    },
    'Shame': {
        'display_name': 'SHAME',
        'color': '#4A6741',  # Dark desaturated green
        'main_icon': {'item_id': 0x212B, 'hue': 0, 'offset_x': -15, 'offset_y': -5},  # Terrathan
        'reward_icon': {'item_id': 0x10D9, 'hue': 0, 'offset_x': -19, 'offset_y': 2}  # Spider egg sac
    },
    'Luna': {
        'display_name': 'LUNA',
        'color': '#87CEEB',  # Sky blue
        'main_icon': {'item_id': 0x0F8B, 'hue': 0, 'offset_x': -4, 'offset_y': 5},  # Moon
        'reward_icon': {'item_id': 0x0F8B, 'hue': 2101, 'offset_x': 0, 'offset_y': 5}  # Blue moon eclipse
    },
    'Valentines': {
        'display_name': 'VALENTINES',
        'color': '#FF1493',  # Deep pink
        'main_icon': {'item_id': 0x0C3B, 'hue': 33, 'offset_x': 0, 'offset_y': 0},  # Rose
        'reward_icon': {'item_id': 0x0C3B, 'hue': 33, 'offset_x': 0, 'offset_y': 0}  # Pink rose
    },
    'Sandstorm': {
        'display_name': 'SANDSTORM',
        'color': '#DEB887',  # Burlywood/sand
        'main_icon': {'item_id': 0xB838, 'hue': 0, 'offset_x': 0, 'offset_y': -23},  # Large vase
        'reward_icon': {'item_id': 8499, 'hue': 0, 'offset_x': 0, 'offset_y': -5}  # Straw
    },
    'Easter': {
        'display_name': 'EASTER',
        'color': '#98FB98',  # Pale green
        'main_icon': {'item_id': 0x09B5, 'hue': 0, 'offset_x': 0, 'offset_y': 0},  # Egg
        'reward_icon': {'item_id': 0x09B5, 'hue': 63, 'offset_x': 0, 'offset_y': 0}  # Green egg
    },
    'StPatrick': {
        'display_name': "ST. PATRICK'S",
        'color': '#00FF00',  # Bright green
        'main_icon': {'item_id': 0x74A1, 'hue': 0, 'offset_x': 0, 'offset_y': 0},  # Clover
        'reward_icon': {'item_id': 0x0EED, 'hue': 0, 'offset_x': 0, 'offset_y': 0}  # Gold coins
    },
    'Destard': {
        'display_name': 'DESTARD',
        'color': '#FF4500',  # Orange red
        'main_icon': {'item_id': 0x20D6, 'hue': 43, 'offset_x': 0, 'offset_y': -15},  # Dragon mini
        'reward_icon': {'item_id': 0x5454, 'hue': 0x0ad3, 'offset_x': 0, 'offset_y': -8}  # Bonfire wisp
    },
    'Bilgewater': {
        'display_name': 'BILGEWATER',
        'color': '#20B2AA',  # Light sea green
        'main_icon': {'item_id': 0x348B, 'hue': 0, 'offset_x': 0, 'offset_y': 0},  # Water rocks
        'reward_icon': {'item_id': 0x09CF, 'hue': 0, 'offset_x': 0, 'offset_y': -5}  # Blue fish 0x09CC ,  item_fish_bigA_0x09CF
    },
    'Doom': {
        'display_name': 'D O O M',
        'color': '#8B0000',  # Dark red/blood red
        'main_icon': {'item_id': 0xBF71, 'hue': 0, 'offset_x': 5, 'offset_y': -10},  # Doom key
        'reward_icon': {'item_id': 9781, 'hue': 0, 'offset_x': -5, 'offset_y': -20}  # Drake
    },
    'Krampus': {
        'display_name': 'KRAMPUS',
        'color': '#B22222',  # Fire brick red
        'main_icon': {'item_id': 0x0F50, 'hue': 0, 'offset_x': 0, 'offset_y': 0},  # Horns
        'reward_icon': {'item_id': 0x0F50, 'hue': 33, 'offset_x': 0, 'offset_y': 0}  # Red horns
    },
    'Deceit': {
        'display_name': 'DECEIT',
        'color': '#DC143C',  # Crimson
        'main_icon': {'item_id': 0x0F7E, 'hue': 0, 'offset_x': 0, 'offset_y': 3},  # Bone
        'reward_icon': {'item_id': 0xBF71, 'hue': 0, 'offset_x': 0, 'offset_y': -3}  # Doom key
    },
    'Eventide': {
        'display_name': 'EVENTIDE',
        'color': '#4B0082',  # Indigo
        'main_icon': {'item_id': 0x0A12, 'hue': 0, 'offset_x': 0, 'offset_y': 0},  # Torch
        'reward_icon': {'item_id': 16381, 'hue': 0, 'offset_x': 0, 'offset_y': 0}  # Skeletal hound
    },
    'Wrong': {
        'display_name': 'WRONG',
        'color': '#8B7355',  # Desaturated brown
        'main_icon': {'item_id': 0xBCA4, 'hue': 0, 'offset_x': 0, 'offset_y': 0},  # treasure
        'reward_icon': {'item_id': 0x7163, 'hue': 63, 'offset_x': 0, 'offset_y': 0}  # Green bottle skin
    },
    'Halloween': {
        'display_name': 'HALLOWEEN',
        'color': '#FF8C00',  # Dark orange
        'main_icon': {'item_id': 0x0C6E, 'hue': 0, 'offset_x': 0, 'offset_y': 0},  # Pumpkin
        'reward_icon': {'item_id': 0x0C6E, 'hue': 33, 'offset_x': 0, 'offset_y': 0}  # Orange pumpkin
    },
    'Exile': {
        'display_name': 'EXILE',
        'color': '#4169E1',  # Royal blue
        'main_icon': {'item_id': 0x0E7F, 'hue': 0, 'offset_x': 0, 'offset_y': 0},  # Mini knight , barrel small Item 0x0E7F
        'reward_icon': {'item_id': 0x3BB5, 'hue': 0, 'offset_x': 0, 'offset_y': 0}  # Ankh pendant
    },
}

KNOWN_EVENT_DETAIL_GUMPS = {
    0xf1c6b41c: 'Delucia',
    0xdbadbd25: 'Shame',
    0x6d43d454: 'Sandstorm',
    0x6d0e4221: 'Deceit',
    0xb2670244: 'Exile',
    0x9ac2865a: 'Wrong',
    0xeffa927b: 'Eventide',
    0xe2412e40: 'Doom',
    0x9c5d11db: 'Bilgewater',
    0xc3febd38: 'Destard',
    0xf24257ed: 'Luna',
}

EVENT_NAME_REMAPPING = {
    'Pagan Night': 'Destard',  # Destard event shows as "Pagan Night" in gump
}

# Static zone status classification - used when USE_DYNAMIC_ZONE_STATUS = False
DANGER_ZONE_EVENTS = [
    #'Deceit', 'Wrong'
]

SAFE_ZONE_EVENTS = [
    #'Luna'
]

# Dynamic zone status gump IDs
DANGER_ZONES_GUMP_ID = 0x4a319301  # [rotation command
HAVEN_AREAS_GUMP_ID = 0x7fd25f55   # [HavenAreas command
CHALLENGE_GUMP_ID = 0x260d2c93     # [challenge command

# Gump IDs
EVENTS_LIST_GUMP_ID = 0x9564fc6d  # Global events list gump (opened by [event command)
CLAIM_CONFIRM_GUMP_ID = 0x11775c2e  # Claim confirmation gump

# Button IDs
BUTTON_BACK = 0  # Back button in detail gumps
BUTTON_CLAIM = 1  # Claim button in detail gumps
BUTTON_CONFIRM_CLAIM = 1  # Confirm button in claim confirmation gump

# Timing 
WAIT_GUMP_MS = 1000  # Max time to wait for gumps to appear
COMMAND_DELAY = 50  # Legacy delay 
RECOVERY_TIMEOUT = 3  # Max recovery attempts before giving up
MAX_EVENT_READ_RETRIES = 2  # Number of times to retry reading an event page before marking as error

TEXT_COMMAND_MIN_GAP_MS = 800
TEXT_COMMAND_JOURNAL_WAIT_MS = 450
TEXT_COMMAND_WARNING_PATTERNS = [
    'too many',
    'too quickly',
    'too fast',
    'must wait',
    'you have to wait',
]

DELAY_BEFORE_EVENT_COMMAND = 100  # Wait before using [event command to avoid "too many commands" warning
DELAY_AFTER_DETAIL_GUMP_OPEN = 20  # Wait after clicking event button for detail gump
DELAY_AFTER_BACK_BUTTON = 15  # Wait after pressing back button to return to events list
DELAY_AFTER_EVENTS_LIST_ALREADY_OPEN = 10  # When events list is already open
DELAY_RECOVERY_REOPEN = 20  # When reopening after failure

# Display gump configuration
DISPLAY_GUMP_ID = 4125312742  # Unique ID for display gump
DISPLAY_X = 400
DISPLAY_Y = 100
DISPLAY_WIDTH = 320  # Very compact width for tight spacing
DISPLAY_HEIGHT = 600
SHOW_TEXT_OUTLINE = True  # Add black outline around all text
TEXT_OUTLINE_THICKNESS = 2  # Outline thickness in pixels

# Column positions
COL_ICON_X = 15        # Main event icon
COL_NAME_X = 55        # Event name
COL_REWARD_X = 140     # Reward item icon 
COL_POINTS_X = 190     # Points display 
COL_BUTTON_X = 235     # Claim button 

# Button configuration - using small black button style with sliver overlay
CUSTOM_BUTTON_WIDTH = 63
CUSTOM_BUTTON_HEIGHT = 23
CUSTOM_BUTTON_ART_ID = 2443  # Small black button 
CUSTOM_BUTTON_ART_ID_PRESSED = 2443  # Same for pressed state
SLIVER_OVERLAY_TILE_ART_ID = 2624  # Dark tile overlay for solid black appearance

COLORS = {
    'title': 68,       # blue
    'label': 1153,     # light gray
    'ok': 63,          # green
    'warn': 53,        # yellow
    'bad': 33,         # red
    'info': 90,        # cyan
}

HTML_COLORS = {
    'header': '#CCCCCC',       # light gray
    'title': '#555555',        # dark gray
    'event_name': '#3FA9FF',   # blue
    'points_low': '#888888',   # gray (< 50 points)
    'points_high': '#90EE90',  # light green (>= 50 points)
    'claimable': '#FFD700',    # gold
    'error': '#FF6B6B',        # red
}

# =================================================

def debug_message(msg, color=68, level=1):
    """Send debug message to game client."""
    if DEBUG_MODE:
        try:
            prefix = "[GlobalEvents]"
            Misc.SendMessage(f"{prefix} {msg}", color)
        except Exception:
            print(f"[GlobalEvents] {msg}")

def server_sync_delay():
    """Synchronize with server using backpack label check.
    More reliable than arbitrary Misc.Pause() delays.
    """
    try:
        # GetLabel forces client to wait for server response
        Items.GetLabel(Player.Backpack.Serial)
    except Exception:
        # Fallback to minimal pause if GetLabel fails
        Misc.Pause(50)

_LAST_TEXT_COMMAND_MS = 0

def _now_ms():
    try:
        return int(time.time() * 1000)
    except Exception:
        return 0

def _notify_throttle_warning(msg):
    try:
        Misc.SendMessage(msg, COLORS['warn'])
    except Exception:
        print(msg)

def send_text_command(command_text, min_gap_ms=None, journal_wait_ms=None):
    global _LAST_TEXT_COMMAND_MS

    if min_gap_ms is None:
        min_gap_ms = TEXT_COMMAND_MIN_GAP_MS
    if journal_wait_ms is None:
        journal_wait_ms = TEXT_COMMAND_JOURNAL_WAIT_MS

    gap_waited = 0
    now_ms = _now_ms()
    if _LAST_TEXT_COMMAND_MS and now_ms:
        elapsed = now_ms - _LAST_TEXT_COMMAND_MS
        if elapsed < min_gap_ms:
            gap_waited = min_gap_ms - elapsed
            Misc.Pause(int(gap_waited))

    after_ts = time.time()
    try:
        Player.ChatSay(0, command_text)
    except Exception as e:
        debug_message(f"ChatSay failed for '{command_text}': {e}", COLORS['bad'])
        return False

    Misc.Pause(int(journal_wait_ms))
    _LAST_TEXT_COMMAND_MS = _now_ms()

    warning_line = None
    try:
        entries = Journal.GetJournalEntry(after_ts)
        for ent in entries or []:
            txt = str(getattr(ent, 'Text', ent))
            low = txt.lower()
            for pat in TEXT_COMMAND_WARNING_PATTERNS:
                if pat in low:
                    warning_line = txt
                    break
            if warning_line:
                break
    except Exception:
        warning_line = None

    if warning_line:
        _notify_throttle_warning(
            f"[GlobalEvents] Command warning after '{command_text}' "
            f"(min_gap_ms={int(min_gap_ms)}, waited_ms={int(gap_waited)}, journal_wait_ms={int(journal_wait_ms)}): {warning_line}"
        )
        return False

    if DEBUG_MODE:
        debug_message(
            f"Sent command '{command_text}' (min_gap_ms={int(min_gap_ms)}, waited_ms={int(gap_waited)}, journal_wait_ms={int(journal_wait_ms)})",
            COLORS['info']
        )

    return True

def wait_for_gump(gump_id, timeout_ms=WAIT_GUMP_MS):
    """Wait for a specific gump ID to appear."""
    try:
        result = Gumps.WaitForGump(gump_id, timeout_ms)
        if result:
            Misc.Pause(200)
            return True
        return False
    except Exception as e:
        debug_message(f"wait_for_gump error: {e}", COLORS['bad'])
        return False

def clean_html_tags(text):
    """Remove HTML tags from text."""
    if not text:
        return ''
    cleaned = re.sub(r'<[^>]+>', '', text)
    return cleaned.strip()

def _quick_get_gump_lines(gump_id):
    try:
        lines = Gumps.GetLineList(gump_id, True)
        if not lines:
            return []
        return [str(ln).strip() for ln in lines]
    except Exception:
        return []

def _extract_event_points_from_lines(lines):
    try:
        for line in lines or []:
            cleaned = clean_html_tags(line)
            m = re.search(r'Your\s+(.+?)\s+event\s+points\s*:\s*(\d+)', cleaned, re.IGNORECASE)
            if m:
                return (m.group(1).strip(), int(m.group(2)))
    except Exception:
        return (None, None)
    return (None, None)

def _is_event_detail_gump(gump_id):
    lines = _quick_get_gump_lines(gump_id)
    name, _pts = _extract_event_points_from_lines(lines)
    return bool(name)

def _wait_for_event_detail_gump(before_gumps, expected_gump_id=None, timeout_ms=WAIT_GUMP_MS):
    start_ms = _now_ms()
    while True:
        now_ms = _now_ms()
        if start_ms and now_ms and (now_ms - start_ms) > int(timeout_ms):
            return None

        try:
            current = set(Gumps.AllGumpIDs() or [])
        except Exception:
            current = set()

        if expected_gump_id and expected_gump_id in current:
            if _is_event_detail_gump(expected_gump_id):
                return expected_gump_id

        new_gumps = [gid for gid in current if gid not in before_gumps and gid != EVENTS_LIST_GUMP_ID]
        for gid in new_gumps:
            if gid in KNOWN_EVENT_DETAIL_GUMPS and _is_event_detail_gump(gid):
                return gid
            if _is_event_detail_gump(gid):
                return gid

        Misc.Pause(50)

def _close_open_event_detail_gumps():
    """Only press BACK on verified event-detail gumps; never touch unrelated gumps."""
    try:
        all_gumps = Gumps.AllGumpIDs() or []
    except Exception:
        all_gumps = []

    for gump_id in all_gumps:
        if gump_id == EVENTS_LIST_GUMP_ID:
            continue

        # Safe close conditions only
        if gump_id in KNOWN_EVENT_DETAIL_GUMPS or _is_event_detail_gump(gump_id):
            try:
                Gumps.SendAction(gump_id, BUTTON_BACK)
                Misc.Pause(100)
            except Exception:
                pass

def snap_text_lines(gump_id, event_name="Unknown"):
    """Capture text lines from a gump with detailed output.
    
    CRITICAL: Always uses the specific gump_id serial provided to avoid reading wrong gumps.
    """
    try:
        # Give gump time to fully populate
        #Misc.Pause(800)
        server_sync_delay()
        
        # CRITICAL: Verify we're reading from the correct gump serial
        debug_message(f"    [GUMP READ] Targeting gump serial: {hex(gump_id)}", COLORS['info'])
        
        for attempt in range(5):  # Increased attempts
            try:
                if attempt > 0:
                    debug_message(f"    Retry {attempt}/5 reading {event_name} gump {hex(gump_id)}...", COLORS['warn'])
                    Misc.Pause(600)  # Longer delay between retries
                    server_sync_delay()
                
                # CRITICAL: Always use the specific gump_id serial to avoid reading wrong gumps
                lines = Gumps.GetLineList(gump_id, True)
                
                if lines and len(lines) > 0:
                    result = [str(ln).strip() for ln in lines]
                    non_empty = [ln for ln in result if ln]
                    
                    # Accept even if only 1 non-empty line found
                    if len(non_empty) >= 1:
                        debug_message(f"\n{'='*60}", COLORS['info'])
                        debug_message(f"GUMP PAGE: {event_name} (Serial: {hex(gump_id)})", COLORS['ok'])
                        debug_message(f"{'='*60}", COLORS['info'])
                        debug_message(f"Extracted {len(result)} total lines ({len(non_empty)} non-empty) on attempt {attempt+1}", COLORS['info'])
                        debug_message(f"{'-'*60}", COLORS['info'])
                        
                        # Print each line with better formatting
                        for idx, line in enumerate(result):
                            cleaned = clean_html_tags(line)
                            if cleaned:  # Only show non-empty lines
                                debug_message(f"  Line {idx:2d}: {cleaned}", COLORS['label'])
                        
                        debug_message(f"{'='*60}\n", COLORS['info'])
                        return result
                    else:
                        debug_message(f"    Attempt {attempt+1}: Got {len(result)} lines but all empty", COLORS['warn'])
                else:
                    debug_message(f"    Attempt {attempt+1}: No lines returned from gump {hex(gump_id)}", COLORS['warn'])
                    
            except Exception as e:
                debug_message(f"    Attempt {attempt+1} ERROR reading gump {hex(gump_id)}: {e}", COLORS['bad'])
        
        debug_message(f"[FAILED] Could not read gump {hex(gump_id)} for {event_name} after 5 attempts", COLORS['bad'])
        return []
    except Exception as e:
        debug_message(f"snap_text_lines error for gump {hex(gump_id)}: {e}", COLORS['bad'])
        return []

# ===== Navigation Functions =====

def open_events_list_gump():
    """Open the events list gump using [event command."""
    debug_message(f"Opening events list gump (ID: {hex(EVENTS_LIST_GUMP_ID)})", COLORS['info'])
    try:
        try:
            Gumps.ResetGump()
        except Exception:
            pass
        
        server_sync_delay()
        
        send_text_command("[event", min_gap_ms=max(TEXT_COMMAND_MIN_GAP_MS, DELAY_BEFORE_EVENT_COMMAND))
         
        # Wait for gump but don't fail if WaitForGump is unreliable
        wait_for_gump(EVENTS_LIST_GUMP_ID, WAIT_GUMP_MS)
        
        # Double sync for gump to fully load
        server_sync_delay()
        server_sync_delay()
        
        debug_message(f"Events list gump should be open, proceeding...", COLORS['ok'])
        return True
    except Exception as e:
        debug_message(f"Error opening events list gump: {e}", COLORS['bad'])
        return False

def read_events_list_for_claimed_status():
    """Read the events list gump to detect which events have been claimed.
    
    The events list gump shows event names with either "VIEW REWARDS" (unclaimed) or 
    "COMPLETED" (claimed) text a few lines after the event name.
    
    Returns:
        List of event names that have been claimed (e.g., ['Destard', 'Luna'])
    """
    claimed_events = []
    
    try:
        debug_message("\n" + "="*60, COLORS['info'])
        debug_message("READING EVENTS LIST GUMP FOR CLAIMED STATUS", COLORS['ok'])
        debug_message("="*60, COLORS['info'])
        
        # Read lines from events list gump (not main menu)
        lines = snap_text_lines(EVENTS_LIST_GUMP_ID, "Events List for Claimed Status")
        
        if not lines:
            debug_message("[WARN] No lines read from events list gump", COLORS['warn'])
            return []
        
        # Parse lines to find event names with "COMPLETED" text nearby
        # Strategy: Look for known event names, then check nearby lines for "COMPLETED" or "VIEW REWARDS"
        for i, line in enumerate(lines):
            cleaned = clean_html_tags(line).strip()
            
            # Check if this line contains a known event name
            for event_name in KNOWN_EVENTS_BUTTON_ID.values():
                # Match event name (case-insensitive, allow partial match)
                if event_name.lower() in cleaned.lower():
                    # Check nearby lines (before and after) for "COMPLETED" or "VIEW REWARDS"
                    # Check range: 3 lines before to 5 lines after
                    start_idx = max(0, i - 3)
                    end_idx = min(len(lines), i + 6)
                    
                    has_completed = False
                    has_view_rewards = False
                    
                    for j in range(start_idx, end_idx):
                        check_line = clean_html_tags(lines[j]).strip()
                        
                        if 'completed' in check_line.lower():
                            has_completed = True
                        if 'view rewards' in check_line.lower():
                            has_view_rewards = True
                    
                    # Event is claimed if it has "COMPLETED" text OR lacks "VIEW REWARDS" text
                    if has_completed:
                        if event_name not in claimed_events:
                            claimed_events.append(event_name)
                            debug_message(f"  Found COMPLETED event: {event_name} (has 'COMPLETED' text)", COLORS['ok'])
                    
                    break
        
        # Also check for remapped event names (e.g., "Pagan Night" -> "Destard")
        for i, line in enumerate(lines):
            cleaned = clean_html_tags(line).strip()
            
            # Check remapped names
            for alternate_name, canonical_name in EVENT_NAME_REMAPPING.items():
                if alternate_name.lower() in cleaned.lower():
                    # Check nearby lines for "COMPLETED" or "VIEW REWARDS"
                    start_idx = max(0, i - 3)
                    end_idx = min(len(lines), i + 6)
                    
                    has_completed = False
                    has_view_rewards = False
                    
                    for j in range(start_idx, end_idx):
                        check_line = clean_html_tags(lines[j]).strip()
                        
                        if 'completed' in check_line.lower():
                            has_completed = True
                        if 'view rewards' in check_line.lower():
                            has_view_rewards = True
                    
                    # Event is claimed if it has "COMPLETED" text
                    if has_completed:
                        if canonical_name not in claimed_events:
                            claimed_events.append(canonical_name)
                            debug_message(f"  Found COMPLETED event: {canonical_name} (shown as '{alternate_name}', has 'COMPLETED' text)", COLORS['ok'])
                    
                    break
        
        debug_message(f"\nTotal completed events found: {len(claimed_events)}", COLORS['info'])
        debug_message("="*60 + "\n", COLORS['info'])
        
        return claimed_events
        
    except Exception as e:
        debug_message(f"Error reading events list for claimed status: {e}", COLORS['bad'])
        return []

def read_events_list_gump(skip_read=False):
    """Read and debug the events list gump content.
    
    Args:
        skip_read: If True, skip reading the gump (for subsequent reopens)
    """
    if skip_read:
        debug_message("Skipping events list read (already captured)", COLORS['info'])
        return []
    
    try:
        debug_message("\n" + "="*60, COLORS['info'])
        debug_message("READING EVENTS LIST GUMP", COLORS['ok'])
        debug_message("="*60, COLORS['info'])
        
        # Read lines from events list gump
        lines = snap_text_lines(EVENTS_LIST_GUMP_ID, "Events List")
        
        if lines and len(lines) > 0:
            return lines
        else:
            debug_message("[WARN] No lines read from events list gump", COLORS['warn'])
            return []
            
    except Exception as e:
        debug_message(f"Error reading events list gump: {e}", COLORS['bad'])
        return []

def open_event_detail(event_name, button_id, detail_gump_id):
    """Open detail gump for a specific event."""
    debug_message(f"\n>>> Opening {event_name} detail page (button {button_id})...", COLORS['info'])
    try:
        server_sync_delay()
        Gumps.SendAction(EVENTS_LIST_GUMP_ID, button_id)
        
        if detail_gump_id:
            # Wait but don't fail on unreliable WaitForGump
            wait_for_gump(detail_gump_id, WAIT_GUMP_MS)
            Misc.Pause(800)  # Extra time for gump data
            debug_message(f"    {event_name} gump should be open (ID: {hex(detail_gump_id)})", COLORS['ok'])
        else:
            Misc.Pause(1200)  # Longer wait without specific gump ID
            debug_message(f"    [WARN] {event_name} gump ID unknown, using delay", COLORS['warn'])
        
        server_sync_delay()
        return True
    except Exception as e:
        debug_message(f"    [ERROR] Failed to open {event_name}: {e}", COLORS['bad'])
        return False

def close_all_event_gumps():
    """Close all event-related gumps to prevent stuck states."""
    try:
        debug_message(f"    Closing all event gumps...", COLORS['info'])
        
        # Try to close all known gump IDs
        gumps_to_close = [
            EVENTS_LIST_GUMP_ID,
            CLAIM_CONFIRM_GUMP_ID
        ]
        
        # Add all known detail gump IDs
        for gump_id in KNOWN_EVENT_DETAIL_GUMPS.keys():
            gumps_to_close.append(gump_id)
        
        for gump_id in gumps_to_close:
            try:
                Gumps.CloseGump(gump_id)
            except Exception:
                pass  # Ignore errors if gump not open
        
        Misc.Pause(400)
        debug_message(f"    Gumps closed", COLORS['ok'])
        return True
    except Exception as e:
        debug_message(f"    [WARN] Error closing gumps: {e}", COLORS['warn'])
        return False

# ===== Data Extraction Functions =====

def parse_event_detail(lines, event_name, detail_gump_id=None):
    """Parse event detail information from gump lines.
    
    Args:
        lines: List of gump text lines
        event_name: Expected event name
        detail_gump_id: The gump serial that was read (for debug output)
    
    Returns:
        Dictionary with event data:
        - 'name': Event name (may be updated from gump text)
        - 'points': Current points (int)
        - 'description': Event description
        - 'status': Status text
        - 'can_claim': True if points >= 50
        - 'data_valid': True if we successfully extracted data
        - 'discovered_name': True if name was discovered from gump text
    """
    event_data = {
        'name': event_name,
        'points': 0,
        'description': '',
        'status': '',
        'can_claim': False,
        'raw_lines': [],
        'data_valid': False,  # Flag to indicate if we got real data
        'discovered_name': False,  # Flag to indicate if name was discovered from gump
        'gump_serial': hex(detail_gump_id) if detail_gump_id else 'Unknown',  # Store gump serial for debugging
        'event_button_id': None,  # Store button ID for claiming
        'detail_gump_id': detail_gump_id  # Store detail gump ID for claiming
    }
    
    if not lines:
        debug_message(f"    [ERROR] No lines provided to parse for {event_name}", COLORS['bad'])
        return event_data
    
    debug_message(f"\n--- Parsing {event_name} Data ---", COLORS['info'])
    
    # Store and display all cleaned lines
    for idx, line in enumerate(lines):
        cleaned = clean_html_tags(line)
        if cleaned:  # Only store non-empty
            event_data['raw_lines'].append(cleaned)
    
    # Extract points and claimability from lines
    points_found = False
    claim_now_found = False
    discovered_event_name = None
    
    for line in lines:
        cleaned = clean_html_tags(line)
        
        # Look for "Your [EventName] event points : XXX" pattern
        # This pattern confirms the event and can discover unknown event names
        # needs to maybe Match multiple words (e.g., "Pagan Night") using (.+?) instead of (\w+)
        points_match = re.search(r'Your\s+(.+?)\s+event\s+points\s*:\s*(\d+)', cleaned, re.IGNORECASE)
        if points_match:
            discovered_event_name = points_match.group(1)  # Capture the event name
            points = int(points_match.group(2))
            event_data['points'] = points
            points_found = True
            
            # Update event name if discovered from gump (more accurate than button mapping)
            if discovered_event_name:
                # Keep the event name as-is from gump (already properly capitalized)
                # Don't use .capitalize() as it lowercases everything except first letter
                # e.g., "Pagan Night" should stay "Pagan Night", not become "Pagan night"
                discovered_event_name = discovered_event_name.strip()
                
                # CRITICAL: Apply event name remapping if this is an alternate name
                # e.g., "Pagan Night" -> "Destard"
                original_discovered_name = discovered_event_name
                if discovered_event_name in EVENT_NAME_REMAPPING:
                    remapped_name = EVENT_NAME_REMAPPING[discovered_event_name]
                    debug_message(f"    [REMAPPED] Gump shows '{discovered_event_name}' -> using canonical name '{remapped_name}'", COLORS['info'])
                    discovered_event_name = remapped_name
                
                # If the event name was generic (like "Event_Button_XX"), replace it
                if event_name.startswith('Event_Button_'):
                    debug_message(f"    [DISCOVERED] Event name from gump: '{original_discovered_name}' (was: {event_name})", COLORS['ok'])
                    event_data['name'] = discovered_event_name
                    event_data['discovered_name'] = True
                # If names don't match, log a warning but use discovered name
                elif event_name.lower() != discovered_event_name.lower():
                    debug_message(f"    [NAME MISMATCH] Gump says '{original_discovered_name}' but expected '{event_name}'", COLORS['warn'])
                    debug_message(f"    [UPDATED] Using discovered name: '{discovered_event_name}'", COLORS['info'])
                    event_data['name'] = discovered_event_name
                    event_data['discovered_name'] = True
                else:
                    debug_message(f"    [CONFIRMED] Event name: '{discovered_event_name}'", COLORS['ok'])
            
            debug_message(f"    Points detected: {points}", COLORS['ok'])
        
        # Check for "CLAIM NOW" text to determine if claimable
        if 'CLAIM NOW' in cleaned.upper():
            claim_now_found = True
            debug_message(f"    'CLAIM NOW' button detected", COLORS['ok'])
        
        # Collect description/status text (skip pure numbers and button text)
        if cleaned and not re.match(r'^\d+$', cleaned) and 'CLAIM' not in cleaned.upper():
            if not event_data['description']:
                event_data['description'] = cleaned
            elif len(event_data['status']) < 200:  # Limit status text length
                event_data['status'] += cleaned + ' '
    
    if not points_found:
        debug_message(f"    [WARN] No 'Your [EventName] event points : X' pattern found in {event_name} data", COLORS['warn'])
        if detail_gump_id:
            debug_message(f"    [CRITICAL] Was reading from gump serial: {hex(detail_gump_id)}", COLORS['bad'])
            debug_message(f"    [INFO] This gump may not be the event detail page - possible wrong gump read", COLORS['warn'])
        else:
            debug_message(f"    [INFO] This may not be a valid event page or the format has changed", COLORS['info'])
    
    # CRITICAL: Only mark data as valid if we found the event points pattern
    # Without this pattern, we likely read the wrong gump
    if points_found:
        event_data['data_valid'] = True
    else:
        event_data['data_valid'] = False
    
    # Determine if claimable based on "CLAIM NOW" presence AND valid points
    # Must have both CLAIM NOW button AND points > 0 to be truly claimable
    event_data['can_claim'] = claim_now_found and event_data['points'] > 0
    
    if claim_now_found and event_data['points'] == 0:
        debug_message(f"    [WARN] CLAIM NOW found but 0 points - marking as not claimable", COLORS['warn'])
    elif not claim_now_found and event_data['points'] >= 50:
        debug_message(f"    [INFO] Has {event_data['points']} points but no CLAIM NOW button", COLORS['warn'])
    elif claim_now_found and event_data['points'] > 0:
        debug_message(f"    [OK] Event is claimable: CLAIM NOW present + {event_data['points']} points", COLORS['ok'])
    
    claim_status = "CLAIMABLE" if event_data['can_claim'] else "Not claimable"
    claim_color = COLORS['ok'] if event_data['can_claim'] else COLORS['label']
    final_name = event_data['name']  # May have been updated
    debug_message(f"    Status: {event_data['points']} points - {claim_status}", claim_color)
    debug_message(f"    Data Valid: {event_data['data_valid']}", COLORS['info'])
    if event_data['discovered_name']:
        debug_message(f"    Event Name: {final_name} (discovered from gump)", COLORS['ok'])
    debug_message(f"--- End {final_name} Parsing ---\n", COLORS['info'])
    
    return event_data

def save_events_to_json(events_data, raw_gump_data):
    """Save collected events data to JSON file."""
    if not EXPORT_TO_JSON:
        return
    
    try:
        debug_message("\nSaving data to JSON...", COLORS['info'])
        
        # Ensure directory exists
        if not os.path.exists(BASE_PATH):
            os.makedirs(BASE_PATH)
        
        # Build JSON structure
        json_data = {
            "export_info": {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                "script": "QUEST_global_events.py",
                "version": "20251024"
            },
            "summary": {
                "total_events": len(events_data),
                "valid_events": len([e for e in events_data if e.get('data_valid', False)]),
                "claimable_events": len([e for e in events_data if e.get('can_claim', False)]),
                "total_points": sum(e.get('points', 0) for e in events_data)
            },
            "events": [],
            "raw_gump_data": raw_gump_data
        }
        
        # Add event data
        for event in events_data:
            event_entry = {
                "name": event.get('name', 'Unknown'),
                "points": event.get('points', 0),
                "can_claim": event.get('can_claim', False),
                "data_valid": event.get('data_valid', False),
                "discovered_name": event.get('discovered_name', False),
                "description": event.get('description', ''),
                "status": event.get('status', ''),
                "raw_lines": event.get('raw_lines', [])
            }
            json_data['events'].append(event_entry)
        
        # Write JSON file
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(json_data, f, indent=2)
        
        debug_message(f"JSON saved to: {OUTPUT_FILE}", COLORS['ok'])
        debug_message(f"  - {len(events_data)} events exported", COLORS['info'])
        
    except Exception as e:
        debug_message(f"Error saving JSON: {e}", COLORS['bad'])

def create_error_event_entry(event_name, button_id, error_message):
    """Create an error entry for an event that failed to load."""
    return {
        'name': event_name,
        'points': 0,
        'can_claim': False,
        'data_valid': False,
        'description': '',
        'status': f'ERROR: {error_message}',
        'raw_lines': []
    }

def read_danger_zones_gump():
    """Open and read danger zones gump to get list of active danger zones.
    
    Returns:
        List of danger zone names (e.g., ['Deceit', 'Wrong', 'Shame'])
    """
    danger_zones = []
    
    try:
        debug_message("Reading danger zones from [rotation gump...", COLORS['info'])
        
        # Retry up to 3 times if gump fails to open
        for attempt in range(3):
            if attempt > 0:
                debug_message(f"  Retry {attempt}/3 for danger zones gump...", COLORS['warn'])
                Misc.Pause(1000)
            
            # Open danger zones gump
            send_text_command("[rotation")
             
            if wait_for_gump(DANGER_ZONES_GUMP_ID, WAIT_GUMP_MS):
                server_sync_delay()
                break
        else:
            debug_message("  Failed to open danger zones gump after 3 attempts", COLORS['bad'])
            return []
        
        if wait_for_gump(DANGER_ZONES_GUMP_ID, WAIT_GUMP_MS):
            server_sync_delay()
            
            # Read gump lines
            lines = snap_text_lines(DANGER_ZONES_GUMP_ID, "Danger Zones")
            
            if lines:
                # Parse zone names from lines
                # Look for lines that match known event names
                for line in lines:
                    cleaned = clean_html_tags(line)
                    if not cleaned or cleaned.isdigit():
                        continue
                    
                    # Check if line contains any known event name
                    for event_name in KNOWN_EVENTS_BUTTON_ID.values():
                        if event_name in cleaned:
                            if event_name not in danger_zones:
                                danger_zones.append(event_name)
                                debug_message(f"  Found danger zone: {event_name}", COLORS['ok'])
                            break
            
            # Close gump
            try:
                Gumps.CloseGump(DANGER_ZONES_GUMP_ID)
            except Exception:
                pass
        
        debug_message(f"Danger zones found: {len(danger_zones)}", COLORS['info'])
        return danger_zones
        
    except Exception as e:
        debug_message(f"Error reading danger zones: {e}", COLORS['bad'])
        return []

def read_haven_areas_gump():
    """Open and read haven areas gump to get list of safe haven areas.
    
    Returns:
        List of haven area names (e.g., ['Luna', 'Delucia'])
    """
    haven_areas = []
    
    try:
        debug_message("Reading haven areas from [HavenAreas gump...", COLORS['info'])
        
        # Retry up to 3 times if gump fails to open
        for attempt in range(3):
            if attempt > 0:
                debug_message(f"  Retry {attempt}/3 for haven areas gump...", COLORS['warn'])
                Misc.Pause(1000)
            
            # Open haven areas gump
            send_text_command("[HavenAreas")
             
            if wait_for_gump(HAVEN_AREAS_GUMP_ID, WAIT_GUMP_MS):
                server_sync_delay()
                break
        else:
            debug_message("  Failed to open haven areas gump after 3 attempts", COLORS['bad'])
            return []
        
        if wait_for_gump(HAVEN_AREAS_GUMP_ID, WAIT_GUMP_MS):
            server_sync_delay()
            
            # Read gump lines
            lines = snap_text_lines(HAVEN_AREAS_GUMP_ID, "Haven Areas")
            
            if lines:
                # Parse area names from lines
                # Look for lines that match known event names
                for line in lines:
                    cleaned = clean_html_tags(line)
                    if not cleaned or cleaned.isdigit():
                        continue
                    
                    # Check if line contains any known event name
                    for event_name in KNOWN_EVENTS_BUTTON_ID.values():
                        if event_name in cleaned:
                            if event_name not in haven_areas:
                                haven_areas.append(event_name)
                                debug_message(f"  Found haven area: {event_name}", COLORS['ok'])
                            break
            
            # Close gump
            try:
                Gumps.CloseGump(HAVEN_AREAS_GUMP_ID)
            except Exception:
                pass
        
        debug_message(f"Haven areas found: {len(haven_areas)}", COLORS['info'])
        return haven_areas
        
    except Exception as e:
        debug_message(f"Error reading haven areas: {e}", COLORS['bad'])
        return []

def read_challenge_gump():
    """Open and read challenge gump to get current challenge event.
    
    Returns:
        List with challenge event name (e.g., ['Deceit']) or empty list
    """
    challenge_events = []
    
    try:
        debug_message("Reading challenge from [challenge gump...", COLORS['info'])
        
        # Retry up to 3 times if gump fails to open
        for attempt in range(3):
            if attempt > 0:
                debug_message(f"  Retry {attempt}/3 for challenge gump...", COLORS['warn'])
                Misc.Pause(1000)
            
            # Open challenge gump
            send_text_command("[challenge")
             
            if wait_for_gump(CHALLENGE_GUMP_ID, WAIT_GUMP_MS):
                server_sync_delay()
                break
        else:
            debug_message("  Failed to open challenge gump after 3 attempts", COLORS['bad'])
            return []
        
        if wait_for_gump(CHALLENGE_GUMP_ID, WAIT_GUMP_MS):
            server_sync_delay()
            
            # Read gump lines
            lines = snap_text_lines(CHALLENGE_GUMP_ID, "Challenge")
            
            if lines:
                # Parse challenge event names from lines
                # Look for lines that match known event names
                for line in lines:
                    cleaned = clean_html_tags(line)
                    if not cleaned or cleaned.isdigit():
                        continue
                    
                    # Check if line contains any known event name
                    for event_name in KNOWN_EVENTS_BUTTON_ID.values():
                        if event_name in cleaned:
                            if event_name not in challenge_events:
                                challenge_events.append(event_name)
                                debug_message(f"  Found challenge event: {event_name}", COLORS['ok'])
                            break
            
            # Close gump
            try:
                Gumps.CloseGump(CHALLENGE_GUMP_ID)
            except Exception:
                pass
        
        debug_message(f"Challenge events found: {len(challenge_events)}", COLORS['info'])
        return challenge_events
        
    except Exception as e:
        debug_message(f"Error reading challenge: {e}", COLORS['bad'])
        return []

def get_dynamic_zone_status():
    """Get current danger zones, haven areas, and challenge events by reading gumps.
    
    Returns:
        Tuple of (danger_zones_list, haven_areas_list, challenge_events_list)
    """
    if not USE_DYNAMIC_ZONE_STATUS:
        debug_message("Dynamic zone status disabled, using static lists", COLORS['info'])
        return (DANGER_ZONE_EVENTS, SAFE_ZONE_EVENTS, [])
    
    debug_message("\n" + "="*60, COLORS['title'])
    debug_message("READING DYNAMIC ZONE STATUS", COLORS['title'])
    debug_message("="*60, COLORS['title'])
    
    danger_zones = read_danger_zones_gump()
    Misc.Pause(500)  # Brief pause between gump commands
    haven_areas = read_haven_areas_gump()
    Misc.Pause(500)  # Brief pause between gump commands
    challenge_events = read_challenge_gump()
    
    debug_message("="*60 + "\n", COLORS['title'])
    
    return (danger_zones, haven_areas, challenge_events)

def process_event_page(button_id, all_events_data, raw_gump_data, page_number, total_pages, retry_count=0):
    """Process a single event page by clicking its button and reading the detail gump."""
    try:
        retry_text = f" (Retry {retry_count}/{MAX_EVENT_READ_RETRIES})" if retry_count > 0 else ""
        debug_message(f"\n[PAGE {page_number}/{total_pages}] Processing button {button_id}...{retry_text}", COLORS['title'])
        
        # Click the event button directly on known events list gump serial
        # Don't check HasGump - just try to interact with the known gump ID
        server_sync_delay()
        server_sync_delay()
        
        try:
            before_gumps = set(Gumps.AllGumpIDs() or [])
        except Exception:
            before_gumps = set()

        try:
            Gumps.SendAction(EVENTS_LIST_GUMP_ID, button_id)
        except Exception as e:
            debug_message(f"    [ERROR] Failed to click button {button_id}: {e}", COLORS['bad'])
            return 'no_gump'
        
        # Wait for a detail gump to appear
        Misc.Pause(DELAY_AFTER_DETAIL_GUMP_OPEN)
        server_sync_delay()
        
        # Determine event name from button ID first
        event_name = KNOWN_EVENTS_BUTTON_ID.get(button_id, f"Event_Button_{button_id}")
        
        # CRITICAL: Try to find the expected gump serial from KNOWN_EVENT_GUMPS first
        # This ensures we read from the correct detail gump
        detail_gump_id = None
        expected_gump_id = None
        
        # Look up expected gump ID for this event
        for gump_serial, gump_event_name in KNOWN_EVENT_DETAIL_GUMPS.items():
            if gump_event_name == event_name:
                expected_gump_id = gump_serial
                break
        
        # First priority: the expected known gump serial
        try:
            all_gumps = Gumps.AllGumpIDs() or []
        except Exception:
            all_gumps = []

        if expected_gump_id and expected_gump_id in all_gumps and _is_event_detail_gump(expected_gump_id):
            detail_gump_id = expected_gump_id
            debug_message(f"    [MATCHED] Found expected event detail gump serial {hex(expected_gump_id)} for {event_name}", COLORS['ok'])
        else:
            # Strict: only accept gumps that actually look like an event detail page
            detail_gump_id = _wait_for_event_detail_gump(before_gumps, expected_gump_id, WAIT_GUMP_MS)
            if detail_gump_id:
                if expected_gump_id and detail_gump_id != expected_gump_id:
                    debug_message(f"    [WARN] Event detail gump serial mismatch for {event_name}: expected {hex(expected_gump_id)} but found {hex(detail_gump_id)}", COLORS['warn'])
                else:
                    debug_message(f"    Found event detail gump serial {hex(detail_gump_id)} for {event_name}", COLORS['ok'])
        
        if not detail_gump_id:
            debug_message(f"    [ERROR] No event detail gump found for button {button_id} (refusing to read unrelated gumps)", COLORS['bad'])
            return 'no_gump'

        # Defensive: ensure we never parse an unrelated gump
        if not _is_event_detail_gump(detail_gump_id):
            debug_message(f"    [ERROR] Selected gump {hex(detail_gump_id)} does not look like an event detail page; aborting read", COLORS['bad'])
            return 'invalid_data'
        
        # CRITICAL: Read event data using the specific detail_gump_id serial
        # This ensures we're reading from the correct gump and not a different one
        debug_message(f"    [READING] Using gump serial {hex(detail_gump_id)} for {event_name}", COLORS['info'])
        lines = snap_text_lines(detail_gump_id, event_name)
        
        # Only process and add event data if we actually got lines
        if lines and len(lines) > 0:
            # Check if we got meaningful data (at least one non-empty line)
            non_empty_lines = [clean_html_tags(ln) for ln in lines if clean_html_tags(ln)]
            
            if len(non_empty_lines) > 0:
                debug_message(f"    [READING] Got {len(non_empty_lines)} lines of data for {event_name}", COLORS['info'])
                # Pass the gump serial to parse function for better error reporting
                event_data = parse_event_detail(lines, event_name, detail_gump_id)
                
                # Store button and gump IDs for claiming
                event_data['event_button_id'] = button_id
                event_data['detail_gump_id'] = detail_gump_id
                
                # CRITICAL: Only accept data if it's valid (has event points pattern)
                if event_data.get('data_valid', False):
                    debug_message(f"    [SUCCESS] Valid event data found for {event_name}", COLORS['ok'])
                    all_events_data.append(event_data)
                    
                    # Store raw gump data
                    raw_gump_data[event_name] = {
                        "gump_id": hex(detail_gump_id),
                        "button_id": button_id,
                        "lines": non_empty_lines
                    }
                    
                    # Use button 0 (back button) to close detail gump and reveal events list
                    debug_message(f"    Data captured for {event_name}, pressing back button", COLORS['ok'])
                    try:
                        Gumps.SendAction(detail_gump_id, BUTTON_BACK)  # Button 0 = back
                        Misc.Pause(150)
                        server_sync_delay()
                    except Exception as e:
                        debug_message(f"    [WARN] Error pressing back button: {e}", COLORS['warn'])
                    
                    return 'success'
                else:
                    debug_message(f"    [FAILED] Invalid data - no event points pattern found", COLORS['bad'])
                    debug_message(f"    [RETRY] This indicates wrong gump was read, will retry", COLORS['warn'])
                    return 'invalid_data'  # Return error code to trigger retry
            else:
                debug_message(f"    [ERROR] No meaningful data extracted for button {button_id}", COLORS['bad'])
                return 'no_data'  # Return error code
        else:
            debug_message(f"    [ERROR] Failed to read any lines for button {button_id}", COLORS['bad'])
            return 'no_lines'  # Return error code
        
        _close_open_event_detail_gumps()
        
        return 'read_failed'
        
    except Exception as e:
        debug_message(f"    [ERROR] Error processing button {button_id}: {e}", COLORS['bad'])
        return 'exception'

def collect_all_events_data():
    """Collect data from all global events across all pages.
    
    Returns:
        Tuple of (events_data_list, claimed_events_list)
    """
    debug_message("\n" + "#"*60, COLORS['title'])
    debug_message("#  STARTING GLOBAL EVENTS DATA COLLECTION", COLORS['title'])
    debug_message("#"*60 + "\n", COLORS['title'])
    
    # Close any existing gumps first
    close_all_event_gumps()
    server_sync_delay()
    
    # Open events list gump directly with [event command
    if not open_events_list_gump():
        debug_message("[ABORT] Failed to open events list gump", COLORS['bad'])
        return [], []
    
    # CRITICAL: Read events list gump to detect claimed events
    # The events list gump shows "COMPLETED" or "VIEW REWARDS" for each event
    claimed_events = read_events_list_for_claimed_status()
    
    # Read the events list gump content (only once at start)
    events_list_lines = read_events_list_gump(skip_read=False)
    
    all_events_data = []
    raw_gump_data = {
        "events_list_gump": {
            "gump_id": hex(EVENTS_LIST_GUMP_ID),
            "lines": events_list_lines
        }
    }
    
    total_pages = len(EVENT_PAGE_BUTTONS)
    current_page = 0
    
    # Visit each event page
    for button_id in EVENT_PAGE_BUTTONS:
        current_page += 1
        
        # Skip seasonal events if flag is enabled
        if SKIP_SEASONAL_EVENTS and button_id in SEASONAL_EVENTS:
            event_name = SEASONAL_EVENTS[button_id]
            debug_message(f"\n[PAGE {current_page}/{total_pages}] Skipping seasonal event: {event_name} (button {button_id})", COLORS['warn'])
            continue
        
        # Verify events list is still open before processing
        if not Gumps.HasGump(EVENTS_LIST_GUMP_ID):
            debug_message(f"\n[PAGE {current_page}/{total_pages}] Events list gump closed, reopening...", COLORS['warn'])
            close_all_event_gumps()
            server_sync_delay()
            
            if not open_events_list_gump():
                debug_message(f"    [ERROR] Failed to reopen events list, aborting", COLORS['bad'])
                break
        
        # Process this event page with retry logic
        result = process_event_page(button_id, all_events_data, raw_gump_data, current_page, total_pages, retry_count=0)
        
        # Retry if failed
        if result != 'success':
            for retry_attempt in range(1, MAX_EVENT_READ_RETRIES + 1):
                debug_message(f"    [RETRY] Attempting retry {retry_attempt}/{MAX_EVENT_READ_RETRIES} for button {button_id}...", COLORS['warn'])
                
                # CRITICAL: After 2 failed attempts with 'no_gump' error, do full menu reset
                if retry_attempt >= 2 and result == 'no_gump':
                    debug_message(f"    [RECOVERY] Detail gump failed to open after {retry_attempt} attempts", COLORS['warn'])
                    debug_message(f"    [RECOVERY] Performing full menu reset...", COLORS['info'])
                    
                    # Close ALL gumps
                    close_all_event_gumps()
                    server_sync_delay()
                    
                    # Reopen events list
                    if not open_events_list_gump():
                        debug_message(f"    [ERROR] Failed to reopen events list during recovery", COLORS['bad'])
                        break
                    
                    debug_message(f"    [RECOVERY] Menu reset complete, retrying button {button_id}...", COLORS['ok'])
                else:
                    # Normal retry: ONLY close verified event detail gumps
                    _close_open_event_detail_gumps()
                    server_sync_delay()
                
                # Brief pause before retry
                Misc.Pause(200)
                
                # Retry processing
                result = process_event_page(button_id, all_events_data, raw_gump_data, current_page, total_pages, retry_count=retry_attempt)
                
                if result == 'success':
                    break
            
            # If still failed after retries, add error entry
            if result != 'success':
                event_name = KNOWN_EVENTS_BUTTON_ID.get(button_id, f"Event_Button_{button_id}")
                error_msg = {
                    'no_gump': 'Detail gump did not open',
                    'no_data': 'No meaningful data extracted',
                    'no_lines': 'Failed to read gump lines',
                    'read_failed': 'Read operation failed',
                    'exception': 'Exception occurred',
                    'invalid_data': 'Wrong gump read - no event points pattern found'
                }.get(result, 'Unknown error')
                
                debug_message(f"    [FAILED] {event_name} failed after {MAX_EVENT_READ_RETRIES} retries: {error_msg}", COLORS['bad'])
                
                # Add error entry to results
                error_entry = create_error_event_entry(event_name, button_id, error_msg)
                all_events_data.append(error_entry)
                
                # Store error in raw data
                raw_gump_data[event_name] = {
                    "gump_id": "ERROR",
                    "button_id": button_id,
                    "lines": [],
                    "error": error_msg
                }
        
        _close_open_event_detail_gumps()
        
        # Brief pause before next event
        Misc.Pause(100)
        server_sync_delay()  # Sync between pages
    
    debug_message(f"\n" + "#"*60, COLORS['title'])
    debug_message(f"#  COLLECTION COMPLETE: {len(all_events_data)} events processed from {total_pages} pages", COLORS['ok'])
    debug_message("#"*60 + "\n", COLORS['title'])
    
    # Report discovered events
    discovered_events = [e for e in all_events_data if e.get('discovered_name', False)]
    if discovered_events:
        debug_message("\n" + "="*60, COLORS['info'])
        debug_message("DISCOVERED EVENTS REPORT", COLORS['ok'])
        debug_message("="*60, COLORS['info'])
        debug_message(f"Found {len(discovered_events)} event(s) with names discovered from gump text:", COLORS['info'])
        
        for event in discovered_events:
            event_name = event['name']
            points = event['points']
            # Try to find the button ID from raw_gump_data
            button_id = None
            for key, value in raw_gump_data.items():
                if key == event_name and isinstance(value, dict):
                    button_id = value.get('button_id')
                    break
            
            if button_id:
                debug_message(f"  - '{event_name}' (button {button_id}, {points} points)", COLORS['ok'])
            else:
                debug_message(f"  - '{event_name}' ({points} points)", COLORS['ok'])
        
        # Suggest additions to KNOWN_EVENTS
        unknown_events = [e for e in discovered_events if e['name'].startswith('Event_Button_') or e['name'] not in KNOWN_EVENTS_BUTTON_ID.values()]
        if unknown_events:
            debug_message("\n" + "-"*60, COLORS['info'])
            debug_message("SUGGESTED ADDITIONS TO KNOWN_EVENTS:", COLORS['warn'])
            debug_message("-"*60, COLORS['info'])
            for event in unknown_events:
                event_name = event['name']
                button_id = None
                for key, value in raw_gump_data.items():
                    if key == event_name and isinstance(value, dict):
                        button_id = value.get('button_id')
                        break
                
                if button_id and not event_name.startswith('Event_Button_'):
                    debug_message(f"{button_id}: '{event_name}',", COLORS['warn'])
        
        debug_message("="*60 + "\n", COLORS['info'])
    
    # Save to JSON if enabled
    if EXPORT_TO_JSON:
        save_events_to_json(all_events_data, raw_gump_data)
    
    # Close all event gumps now that collection is complete
    debug_message("\nClosing all event gumps...", COLORS['info'])
    close_all_event_gumps()
    debug_message("Event gumps closed\n", COLORS['ok'])
    
    return all_events_data, claimed_events

# ===== Claim Functions =====

def should_auto_claim_event(event_name, points):
    """Check if an event should be auto-claimed based on AUTO_CLAIM_CONFIG.
    
    Args:
        event_name: Name of the event
        points: Current points for the event
    
    Returns:
        True if event should be auto-claimed, False otherwise
    """
    if not AUTO_CLAIM_CONFIG:
        return False
    
    # Check if event is in auto-claim config
    if event_name not in AUTO_CLAIM_CONFIG:
        return False
    
    # Check if points meet threshold
    min_points = AUTO_CLAIM_CONFIG[event_name]
    if points >= min_points:
        debug_message(f"  [AUTO-CLAIM] {event_name} has {points} points (threshold: {min_points})", COLORS['info'])
        return True
    
    return False

def claim_event_points(event_name, event_button_id, detail_gump_id):
    """Claim points for a specific event.
    
    Args:
        event_name: Name of the event to claim
        event_button_id: Button ID on events list gump to open this event
        detail_gump_id: Gump ID of the event detail page
    
    Returns:
        True if claim successful, False otherwise
    """
    debug_message(f"\n{'='*60}", COLORS['title'])
    debug_message(f"CLAIMING: {event_name}", COLORS['title'])
    debug_message(f"{'='*60}", COLORS['title'])
    
    try:
        # Close any existing gumps
        close_all_event_gumps()
        server_sync_delay()
        
        # Open events list gump
        debug_message("Opening events list gump...", COLORS['info'])
        if not open_events_list_gump():
            debug_message("Failed to open events list for claiming", COLORS['bad'])
            return False
        
        # Open event detail page
        debug_message(f"Opening {event_name} detail page (button {event_button_id})...", COLORS['info'])
        if not open_event_detail(event_name, event_button_id, detail_gump_id):
            debug_message(f"Failed to open {event_name} detail for claiming", COLORS['bad'])
            return False
        
        # Click claim button (button ID 1 on detail gump)
        debug_message(f"Clicking CLAIM button (button 1) on {event_name} detail gump...", COLORS['info'])
        server_sync_delay()
        
        try:
            Gumps.SendAction(detail_gump_id, BUTTON_CLAIM)  # Button 1 = claim
            debug_message(f"  Sent claim action to gump {hex(detail_gump_id)}", COLORS['ok'])
        except Exception as e:
            debug_message(f"  [ERROR] Failed to send claim action: {e}", COLORS['bad'])
            return False
        
        # Wait for confirmation gump (0x11775c2e)
        debug_message(f"Waiting for confirmation gump ({hex(CLAIM_CONFIRM_GUMP_ID)})...", COLORS['info'])
        Misc.Pause(800)
        
        if wait_for_gump(CLAIM_CONFIRM_GUMP_ID, WAIT_GUMP_MS):
            debug_message(f"  Confirmation gump appeared!", COLORS['ok'])
            
            # Confirm claim (button 1 on confirmation gump)
            debug_message(f"Confirming claim (button 1)...", COLORS['info'])
            server_sync_delay()
            
            try:
                Gumps.SendAction(CLAIM_CONFIRM_GUMP_ID, BUTTON_CONFIRM_CLAIM)  # Button 1 = confirm
                debug_message(f"  Sent confirmation action", COLORS['ok'])
            except Exception as e:
                debug_message(f"  [ERROR] Failed to confirm: {e}", COLORS['bad'])
                return False
            
            # Wait for claim to process
            Misc.Pause(1500)
            server_sync_delay()
            
            debug_message(f"\n{'='*60}", COLORS['ok'])
            debug_message(f" Successfully claimed {event_name} points!", COLORS['ok'])
            debug_message(f"{'='*60}\n", COLORS['ok'])
            
            return True
        else:
            debug_message(f"  [WARN] Claim confirmation gump did not appear", COLORS['warn'])
            debug_message(f"  This may mean the event is not actually claimable", COLORS['warn'])
            return False
        
    except Exception as e:
        debug_message(f"[ERROR] Exception while claiming {event_name}: {e}", COLORS['bad'])
        return False
    finally:
        # Clean up gumps
        debug_message("Cleaning up gumps...", COLORS['info'])
        try:
            close_all_event_gumps()
            Misc.Pause(300)
        except Exception:
            pass

# ===== Display Functions =====

def build_events_display_data(events_data):
    """Build display data for events with button info.
    
    Returns:
        Dictionary with title and list of event display items
    """
    if not events_data:
        return {
            'title': 'GLOBAL EVENTS',
            'events': []
        }
    
    # Include ALL events (both valid and error events)
    all_events = events_data
    
    # Sort by points (highest first), with error events at the bottom
    sorted_events = sorted(all_events, key=lambda x: (x.get('data_valid', False), x['points']), reverse=True)
    
    return {
        'title': 'GLOBAL EVENTS',
        'events': sorted_events
    }

def add_text_with_outline(gump, x, y, width, height, html_content):
    """Add HTML text with black outline for better visibility."""
    if SHOW_TEXT_OUTLINE:
        # Generate outline offsets based on thickness
        outline_offsets = []
        for thickness in range(1, TEXT_OUTLINE_THICKNESS + 1):
            outline_offsets.extend([
                (-thickness, 0), (thickness, 0), (0, -thickness), (0, thickness),
                (-thickness, -thickness), (thickness, -thickness), (-thickness, thickness), (thickness, thickness)
            ])
        
        # Replace all color codes with pure black for outline
        html_outline = re.sub(r'#[0-9A-Fa-f]{6}', '#000000', html_content)
        
        # Draw black outline at all offset positions
        for dx, dy in outline_offsets:
            Gumps.AddHtml(gump, x + dx, y + dy, width, height, html_outline, False, False)
    
    # Draw main text on top
    Gumps.AddHtml(gump, x, y, width, height, html_content, False, False)

def add_centered_label_with_outline(gump, x, y, w, h, text, hue):
    """Draw a centered label with black outline for readability ."""
    try:
        approx_char_px = 6
        text_x = x + (w // 2) - max(0, len(text)) * approx_char_px // 2
        text_y = y + (h // 2) - 7
        outline_color = 0  # black
        
        # Two-ring outline for better visibility
        offsets_r1 = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
        offsets_r2 = [(-2, 0), (2, 0), (0, -2), (0, 2), (-2, -1), (-2, 1), (2, -1), (2, 1), (-1, -2), (1, -2), (-1, 2), (1, 2)]
        
        # Draw outer ring
        for dx, dy in offsets_r2:
            Gumps.AddLabel(gump, text_x + dx, text_y + dy, outline_color, text)
        # Draw inner ring
        for dx, dy in offsets_r1:
            Gumps.AddLabel(gump, text_x + dx, text_y + dy, outline_color, text)
        # Draw main text
        Gumps.AddLabel(gump, text_x, text_y, hue, text)
    except Exception:
        pass

def add_zone_status_border(gump, x, y, width, height, event_name, danger_zones=None, safe_zones=None, challenge_events=None):
    """Draw a single-pixel rectangular border behind text to indicate zone status.
    
    Args:
        gump: Gump object to add border to
        x: X position of border
        y: Y position of border
        width: Width of border rectangle
        height: Height of border rectangle
        event_name: Name of event to determine border color
        danger_zones: List of danger zone names (optional, uses global if not provided)
        safe_zones: List of safe zone names (optional, uses global if not provided)
        challenge_events: List of challenge event names (optional)
    
    Border colors:
        - Red (#FF0000): Danger zone events
        - Blue (#0066FF): Safe zone events
        - Orange (#FF8C00): Challenge events
        - Dual-color: Top/Left in one color, Bottom/Right in another (for events with multiple classifications)
        - No border: Unclassified events
    """
    if not SHOW_ZONE_STATUS_BORDER:
        return
    
    # Use provided lists or fall back to global static lists
    if danger_zones is None:
        danger_zones = DANGER_ZONE_EVENTS
    if safe_zones is None:
        safe_zones = SAFE_ZONE_EVENTS
    if challenge_events is None:
        challenge_events = []
    
    try:
        # Determine border color(s) based on zone classification
        # Check all classifications to support dual-color borders
        is_danger = event_name in danger_zones
        is_safe = event_name in safe_zones
        is_challenge = event_name in challenge_events
        
        # Define colors for each classification
        danger_color = '#FF0000'    # Red
        safe_color = '#0066FF'      # Blue
        challenge_color = '#FF8C00' # Orange
        
        # Determine border colors (may be dual-color)
        top_left_color = None
        bottom_right_color = None
        
        # DUAL-COLOR CASE: Both DANGER and CHALLENGE
        if is_danger and is_challenge:
            # Top/Left = Red (danger), Bottom/Right = Orange (challenge)
            top_left_color = danger_color
            bottom_right_color = challenge_color
        # DUAL-COLOR CASE: Both SAFE and CHALLENGE (less common but supported)
        elif is_safe and is_challenge:
            # Top/Left = Blue (safe), Bottom/Right = Orange (challenge)
            top_left_color = safe_color
            bottom_right_color = challenge_color
        # SINGLE-COLOR CASES: Only one classification
        elif is_challenge:
            top_left_color = challenge_color
            bottom_right_color = challenge_color
        elif is_danger:
            top_left_color = danger_color
            bottom_right_color = danger_color
        elif is_safe:
            top_left_color = safe_color
            bottom_right_color = safe_color
        
        # Only draw border if event is classified
        if top_left_color is not None:
            # Draw single-pixel border using HTML-based approach for colored borders
            # Create thin HTML elements for each border side
            
            # Border offset configuration - adjust these to fine-tune border positioning
            HORIZONTAL_LINE_REDUCTION = 10  # Reduce horizontal line length by this many characters
            HORIZONTAL_WIDTH_REDUCTION = 30  # Reduce HTML container width by this many pixels
            VERTICAL_LINE_HEIGHT_REDUCTION = 6  # Reduce vertical line height by this many pixels
            TOP_BORDER_OFFSET_Y = -7  # Vertical offset for top border
            BOTTOM_BORDER_OFFSET_Y = -5  # Vertical offset for bottom border
            LEFT_BORDER_OFFSET_X = -8  # Horizontal offset for left border
            RIGHT_BORDER_OFFSET_X = -49  # Horizontal offset for right border (negative = move left)
            VERTICAL_LINE_SPACING = 1  # Spacing between vertical line segments
            
            # Calculate adjusted dimensions
            horizontal_char_count = (width // 6) - HORIZONTAL_LINE_REDUCTION
            horizontal_container_width = width - HORIZONTAL_WIDTH_REDUCTION
            vertical_line_max_height = height - VERTICAL_LINE_HEIGHT_REDUCTION
            
            # Top border (horizontal line) - uses top_left_color
            top_html = f"<basefont color={top_left_color}>{'─' * horizontal_char_count}</basefont>"
            Gumps.AddHtml(gump, x, y + TOP_BORDER_OFFSET_Y, horizontal_container_width, 10, top_html, False, False)
            
            # Bottom border (horizontal line) - uses bottom_right_color
            bottom_html = f"<basefont color={bottom_right_color}>{'─' * horizontal_char_count}</basefont>"
            Gumps.AddHtml(gump, x, y + height + BOTTOM_BORDER_OFFSET_Y, horizontal_container_width, 10, bottom_html, False, False)
            
            # Left border (vertical line) - uses top_left_color
            for i in range(0, vertical_line_max_height, VERTICAL_LINE_SPACING):
                left_html = f"<basefont color={top_left_color}>│</basefont>"
                Gumps.AddHtml(gump, x + LEFT_BORDER_OFFSET_X, y + i, 10, 10, left_html, False, False)
            
            # Right border (vertical line) - uses bottom_right_color
            for i in range(0, vertical_line_max_height, VERTICAL_LINE_SPACING):
                right_html = f"<basefont color={bottom_right_color}>│</basefont>"
                Gumps.AddHtml(gump, x + width + RIGHT_BORDER_OFFSET_X, y + i, 10, 10, right_html, False, False)
            
    except Exception as e:
        debug_message(f"Error drawing zone status border: {e}", COLORS['warn'])

def show_global_events_gump(events_data, danger_zones=None, safe_zones=None, challenge_events=None, claimed_events=None):
    """Display global events in a custom gump with claim buttons.
    
    Args:
        events_data: List of event data dictionaries
        danger_zones: List of danger zone names (optional)
        safe_zones: List of safe zone names (optional)
        challenge_events: List of challenge event names (optional)
        claimed_events: List of claimed event names (optional)
    """
    debug_message("Building global events display gump", COLORS['info'])
    
    # Use provided zone lists or fall back to static lists
    if danger_zones is None:
        danger_zones = DANGER_ZONE_EVENTS
    if safe_zones is None:
        safe_zones = SAFE_ZONE_EVENTS
    if challenge_events is None:
        challenge_events = []
    if claimed_events is None:
        claimed_events = []
    
    # Build display data
    display_data = build_events_display_data(events_data)
    
    # Calculate gump height based on number of events
    num_events = len(display_data['events'])
    title_height = 50
    event_row_height = 35  # Increased for item icons
    padding = 20
    calculated_height = title_height + (num_events * event_row_height) + padding
    gump_height = max(150, min(calculated_height, DISPLAY_HEIGHT))
    
    # Create gump
    gump = Gumps.CreateGump(True, True, False, False)  # movable, closable
    Gumps.AddPage(gump, 0)
    
    # Background
    Gumps.AddBackground(gump, 0, 0, DISPLAY_WIDTH, gump_height, 30546)
    Gumps.AddAlphaRegion(gump, 0, 0, DISPLAY_WIDTH, gump_height)
    
    # Title
    current_y = 10
    title_html = f"<center><basefont color={HTML_COLORS['title']}>{display_data['title']}</basefont></center>"
    add_text_with_outline(gump, 10, current_y, DISPLAY_WIDTH - 20, 20, title_html)
    current_y += 30  # No subtitle, so just add spacing
    
    # Event rows with icons, names, points, and buttons
    # Button IDs are assigned only to claimable events (points >= 50)
    button_id = 1
    for event in display_data['events']:
        event_name = event['name']
        points = event['points']
        can_claim = event.get('can_claim', False)
        data_valid = event.get('data_valid', False)
        
        # Get display config for this event
        config = EVENT_DISPLAY_CONFIG.get(event_name, {
            'display_name': event_name.upper(),
            'color': '#CCCCCC',
            'main_icon': {'item_id': 0x0E76, 'hue': 0, 'offset_x': 0, 'offset_y': 0},
            'reward_icon': {'item_id': 0x0E76, 'hue': 0, 'offset_x': 0, 'offset_y': 0}
        })
        
        # Column 1: Main event icon (with offset from config)
        main_icon = config.get('main_icon', {'item_id': 0x0E76, 'hue': 0, 'offset_x': 0, 'offset_y': 0})
        icon_x = COL_ICON_X + main_icon.get('offset_x', 0)
        icon_y = current_y + main_icon.get('offset_y', 0)
        Gumps.AddItem(gump, icon_x, icon_y, main_icon['item_id'], main_icon['hue'])
        
        # Column 2: Event name with zone status border and custom color
        # Add zone status border behind event name (red=danger, blue=safe, orange=challenge)
        add_zone_status_border(gump, COL_NAME_X - 2, current_y + 3, 124, 22, event_name, danger_zones, safe_zones, challenge_events)
        
        if not data_valid:
            # Error state - red color
            name_html = f"<basefont color=#FF0000>{config['display_name']}</basefont>"
        else:
            name_html = f"<basefont color={config['color']}>{config['display_name']}</basefont>"
        
        add_text_with_outline(gump, COL_NAME_X, current_y + 5, 120, 25, name_html)
        
        # Column 2.5: Reward item icon (right side of event name, with offset from config)
        if 'reward_icon' in config:
            reward_icon = config['reward_icon']
            reward_x = COL_REWARD_X + reward_icon.get('offset_x', 0)
            reward_y = current_y + reward_icon.get('offset_y', 0)
            Gumps.AddItem(gump, reward_x, reward_y, reward_icon['item_id'], reward_icon['hue'])
        
        # Column 3: Points (right-aligned before button)
        if data_valid:
            if can_claim and points > 0:
                points_color = HTML_COLORS['points_high']
            else:
                points_color = HTML_COLORS['points_low']
            points_html = f"<basefont color={points_color}>{points}</basefont>"
        else:
            # Show error status
            points_html = f"<basefont color=#FF0000>ERROR</basefont>"
        
        add_text_with_outline(gump, COL_POINTS_X, current_y + 5, 60, 25, points_html)
        
        # Column 4: Claim button OR "COMPLETED" status
        # Check if event has been claimed (from main menu)
        is_claimed = event_name in claimed_events
        
        if is_claimed:
            # Show "COMPLETED" in medium gray instead of claim button
            completed_html = f"<basefont color=#888888>COMPLETED</basefont>"
            add_text_with_outline(gump, COL_BUTTON_X + 5, current_y + 8, 80, 25, completed_html)
        elif points >= 50 and data_valid:
            # Show claim button - only if points >= 50 and NOT claimed
            # Small black button
            Gumps.AddButton(gump, COL_BUTTON_X, current_y + 6, CUSTOM_BUTTON_ART_ID, CUSTOM_BUTTON_ART_ID_PRESSED, button_id, 1, 0)
            
            # Add sliver overlay for solid black appearance 
            try:
                Gumps.AddImageTiled(gump, COL_BUTTON_X, current_y + 6, CUSTOM_BUTTON_WIDTH, CUSTOM_BUTTON_HEIGHT, SLIVER_OVERLAY_TILE_ART_ID)
            except Exception:
                pass
            
            # Centered label with outline directly on button (green text)
            add_centered_label_with_outline(gump, COL_BUTTON_X, current_y + 6, CUSTOM_BUTTON_WIDTH, CUSTOM_BUTTON_HEIGHT, "CLAIM", 63)  # Hue 63 = bright green
            
            button_id += 1
        
        current_y += event_row_height
    
    # Send gump
    Gumps.SendGump(DISPLAY_GUMP_ID, Player.Serial, DISPLAY_X, DISPLAY_Y, gump.gumpDefinition, gump.gumpStrings)
    debug_message("Global events gump displayed with claim buttons", COLORS['ok'])
    
    # Close event gumps
    try:
        Gumps.CloseGump(EVENTS_LIST_GUMP_ID)
        debug_message("Closed events list gump", COLORS['info'])
    except Exception as e:
        debug_message(f"Error closing gump: {e}", COLORS['warn'])
    
    # Return events data for button handling
    return display_data['events']

# ===== Main Function =====

def handle_claim_button(clicked_button_id, events_list):
    """Handle claim button click by navigating to event and claiming.
    
    Args:
        clicked_button_id: The button ID that was clicked on the display gump
        events_list: List of all events with their data
    
    Returns:
        True if claim successful, False otherwise
    """
    try:
        # Get claimable events only (points >= 50)
        claimable_events = [e for e in events_list if e.get('points', 0) >= 50 and e.get('data_valid', False)]
        
        if not claimable_events:
            debug_message("No claimable events found", COLORS['warn'])
            return False
        
        # Button IDs start at 1
        event_index = clicked_button_id - 1
        
        if event_index < 0 or event_index >= len(claimable_events):
            debug_message(f"Invalid button ID: {clicked_button_id} (expected 1-{len(claimable_events)})", COLORS['bad'])
            return False
        
        event = claimable_events[event_index]
        event_name = event['name']
        event_button_id = event.get('event_button_id')
        detail_gump_id = event.get('detail_gump_id')
        
        debug_message(f"\nClaim button clicked for: {event_name}", COLORS['info'])
        debug_message(f"  Event button ID: {event_button_id}", COLORS['info'])
        debug_message(f"  Detail gump ID: {hex(detail_gump_id) if detail_gump_id else 'Unknown'}", COLORS['info'])
        
        if not event_button_id or not detail_gump_id:
            debug_message(f"[ERROR] Missing button or gump ID for {event_name}", COLORS['bad'])
            return False
        
        # Close display gump
        try:
            Gumps.CloseGump(DISPLAY_GUMP_ID)
        except Exception:
            pass
        
        # Claim the event
        success = claim_event_points(event_name, event_button_id, detail_gump_id)
        
        return success
        
    except Exception as e:
        debug_message(f"Error handling claim button: {e}", COLORS['bad'])
        return False

def main():
    """ collect events data and display results."""
    try:
        # STEP 1: Collect all events data FIRST (this opens many gumps)
        # Returns tuple: (events_data, claimed_events)
        events_data, claimed_events = collect_all_events_data()
        
        # STEP 2: After event collection, read zone status gumps (with retries)
        danger_zones = DANGER_ZONE_EVENTS
        safe_zones = SAFE_ZONE_EVENTS
        challenge_events = []
        
        if USE_DYNAMIC_ZONE_STATUS:
            # Add delay before reading status gumps to avoid "too many commands"
            debug_message("\nWaiting before reading zone status gumps...", COLORS['info'])
            Misc.Pause(2000)  # 2 second delay
            danger_zones, safe_zones, challenge_events = get_dynamic_zone_status()
        
        # Auto-claim events if enabled and configured
        if AUTO_CLAIM_ENABLED and AUTO_CLAIM_CONFIG:
            debug_message("\n" + "="*60, COLORS['title'])
            debug_message("CHECKING AUTO-CLAIM CONFIGURATION", COLORS['title'])
            debug_message("="*60, COLORS['title'])
            
            auto_claim_count = 0
            for event in events_data:
                event_name = event.get('name')
                points = event.get('points', 0)
                data_valid = event.get('data_valid', False)
                event_button_id = event.get('event_button_id')
                detail_gump_id = event.get('detail_gump_id')
                
                # Only process valid events with required data
                if not data_valid or not event_button_id or not detail_gump_id:
                    continue
                
                # Check if event should be auto-claimed
                if should_auto_claim_event(event_name, points):
                    debug_message(f"\n[AUTO-CLAIM] Attempting to claim {event_name}...", COLORS['info'])
                    
                    success = claim_event_points(event_name, event_button_id, detail_gump_id)
                    
                    if success:
                        auto_claim_count += 1
                        debug_message(f"[AUTO-CLAIM] Successfully claimed {event_name}", COLORS['ok'])
                        # Update event data to reflect claim
                        event['points'] = 0  # Reset points after claim
                        event['can_claim'] = False
                    else:
                        debug_message(f"[AUTO-CLAIM] Failed to claim {event_name}", COLORS['warn'])
                    
                    # Pause between claims to avoid overwhelming server
                    Misc.Pause(1000)
            
            if auto_claim_count > 0:
                debug_message(f"\n[AUTO-CLAIM] Claimed {auto_claim_count} event(s)", COLORS['ok'])
            else:
                debug_message(f"\n[AUTO-CLAIM] No events met auto-claim criteria", COLORS['info'])
            
            debug_message("="*60 + "\n", COLORS['title'])
        
        # Display results with interactive buttons (pass zone lists and claimed events)
        events_list = show_global_events_gump(events_data, danger_zones, safe_zones, challenge_events, claimed_events)
        
        # Wait for gump response
        gump_response = Gumps.WaitForGump(DISPLAY_GUMP_ID, 300000)  # 5 minute timeout
        
        if gump_response:
            gump_data = Gumps.GetGumpData(DISPLAY_GUMP_ID)
            if gump_data and hasattr(gump_data, 'buttonid'):
                button_id = gump_data.buttonid
                
                if button_id > 0:  # 0 = closed/cancelled
                    debug_message(f"Button {button_id} clicked", COLORS['info'])
                    
                    # Handle claim button
                    if handle_claim_button(button_id, events_list):
                        debug_message("Claim successful, refreshing display...", COLORS['ok'])
                        Misc.Pause(2000)
                        # Recursively call main to refresh display
                        main()
                    else:
                        debug_message("Claim failed or cancelled", COLORS['warn'])
        
    except Exception as e:
        debug_message(f"Error in main: {e}", COLORS['bad'])
        try:
            Misc.SendMessage(f"Global Events Error: {e}", COLORS['bad'])
        except Exception:
            print(f"Global Events Error: {e}")

if __name__ == "__main__":
    main()