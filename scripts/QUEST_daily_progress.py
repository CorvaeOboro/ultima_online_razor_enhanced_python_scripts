"""
QUEST daily progress - a Razor Enhanced Python Script for Ultima Online

display quest progress combined , sorted by reward then tinted by difficulty , 
for each a corresponding image of the approximate objective and "preferred" reward . 

Navigates the quest gump that displays the status and progress of daily quests,
reads the information to present a combined list.

this script is buggy has some difficulty with reading the gump , 
where it may accidentally close the gump , so tries to recover but is sometimes slow .
intended to be used at begining of play session to plan out a few destinations

TROUBLESHOOTING:
- if "import" errors , download iron python 3.4.2 and copy the files in its "Lib" folder into your RazorEnhanced "Lib" folder 

STATUS:: WIP , working but sometimes buggy reading the gump may take several attempts
VERSION:: 20251010
"""

import re # regex , regular expressions to parse the quest info

DEBUG_MODE = False
SHOW_REWARD_ICONS = True  # Show reward item icons next to quest progress
SORT_BY_DIFFICULTY = True  # Sort quests within each category by difficulty (Easy->Medium->Hard)
SHOW_TEXT_OUTLINE = True  # Add black outline around all text 
TEXT_OUTLINE_THICKNESS = 2  # black Outline thickness in pixels
USE_BURNT_COLOR_SCHEME = False  # Use burnt brown/orange color scheme instead of green/blue/red

# is_mastery_orb is derived from preferred_reward containing "Random Mastery Orb"
QUEST_DATA_DIFFICULTY_REWARD = {
    # Easy Quests
    "Graveyard Cleanup": {"difficulty": "Easy", "preferred_reward": "2,500 Gold"},
    "The Exiled Ones": {"difficulty": "Easy", "preferred_reward": "2,000 Gold"},
    "City Cleanup": {"difficulty": "Easy", "preferred_reward": "Runebook (Unblessed)"},
    "Simply Gross": {"difficulty": "Easy", "preferred_reward": "2,500 Gold"},
    "Vermin to the North": {"difficulty": "Easy", "preferred_reward": "Random Mastery Orb"},
    "The Ogre Threat": {"difficulty": "Easy", "preferred_reward": "Random Mastery Orb"},
    "Ghost Hunt": {"difficulty": "Easy", "preferred_reward": "2,500 Gold"},
    
    # Medium Quests
    "Dragon's Essence": {"difficulty": "Medium", "preferred_reward": "Random Mastery Orb"},
    "Viscosity": {"difficulty": "Medium", "preferred_reward": "Random Mastery Orb"},
    "Daemon's Remains": {"difficulty": "Medium", "preferred_reward": "Random Mastery Orb"},
    "Lack of Proof": {"difficulty": "Medium", "preferred_reward": "Random Mastery Orb"},
    "Corrupted Blood": {"difficulty": "Medium", "preferred_reward": "Random Mastery Orb"},
    "Stolen Artifacts": {"difficulty": "Medium", "preferred_reward": "Random Mastery Orb"},
    "Land of the Dead": {"difficulty": "Medium", "preferred_reward": "100 Arcane Dust"},
    "Scary Affiliation": {"difficulty": "Medium", "preferred_reward": "Random Bulk Resource"},
    "Petrified": {"difficulty": "Medium", "preferred_reward": "Random Bulk Resource"},
    "Adamantium Hunt": {"difficulty": "Medium", "preferred_reward": "Random Bulk Resource"},
    "Shoes of a Giant": {"difficulty": "Medium", "preferred_reward": "Random Mastery Orb"},
    "Behorn the Infidels": {"difficulty": "Medium", "preferred_reward": "Random Mastery Orb"},
    "Sky is the Limit": {"difficulty": "Medium", "preferred_reward": "Random Runic Component"},
    "Desert Cleanup": {"difficulty": "Medium", "preferred_reward": "Random Mastery Orb"},
    "Frozen Cleansing": {"difficulty": "Medium", "preferred_reward": "Random Mastery Orb"},
    "Lava Cleansing": {"difficulty": "Medium", "preferred_reward": "Hellclap War Hammer"},
    "Contamination": {"difficulty": "Medium", "preferred_reward": "Random Mastery Orb"},
    "Toxic Flora": {"difficulty": "Medium", "preferred_reward": "Random Mastery Orb"},
    "Unwanted Colonizers": {"difficulty": "Medium", "preferred_reward": "Random Mastery Orb"},
    
    # Hard Quests
    "All Aboard!": {"difficulty": "Hard", "preferred_reward": "3,500 Gold"},
    "Tailoring Hell": {"difficulty": "Hard", "preferred_reward": "Random Mastery Orb"},
    "Gigantic!": {"difficulty": "Hard", "preferred_reward": "Random Mastery Orb"},
    "Evil Within": {"difficulty": "Hard", "preferred_reward": "Random Mastery Orb"},
    "Death Wings": {"difficulty": "Hard", "preferred_reward": "Random Runic Component"},
    "Ancient Sanctuary": {"difficulty": "Hard", "preferred_reward": "Random Mastery Orb"},
}

REWARD_ITEM_GRAPHICS = {
    # Gold rewards
    "1,500 Gold": {"item_id": 0x0EEF, "hue": 0},  # Gold pile
    "2,000 Gold": {"item_id": 0x0EEF, "hue": 0},
    "2,500 Gold": {"item_id": 0x0EEF, "hue": 0},
    "3,000 Gold": {"item_id": 0x0EEF, "hue": 0},
    "3,500 Gold": {"item_id": 0x0EEF, "hue": 0},
    "4,500 Gold": {"item_id": 0x0EEF, "hue": 0},
    "5,000 Gold": {"item_id": 0x0EEF, "hue": 0},
    
    # Mastery Orbs - random hue from list (all possible mastery orb types)
    "Random Mastery Orb": {"item_id": 0x573E, "hue": "random", "hue_list": [
        2388,  # Druidic Orb
        2048,  # Blood Orb (0x0800)
        0x081A,  # Shadow Orb
        0x0B3A,  # Death Orb
        0x0801,  # Poison Orb
        0x04A8,  # Artisan Orb
        0x0489,  # Fira Orb
        0x0B54,  # Earth Orb
        0x0B73,  # Fortune Orb
        0x093A,  # Lyrical Orb
        0x0954,  # Druidic Orb (alt)
        0x0BA7,  # Doom Orb
        0x0AD3,  # Bulwark Orb
        0x09C3,  # Aero Orb
        0x09A4,  # Holy Orb
    ]},
    
    # Arcane Dust
    "50 Arcane Dust": {"item_id": 0x26B8, "hue": 0},  # Powder of translocation
    "60 Arcane Dust": {"item_id": 0x26B8, "hue": 0},
    "75 Arcane Dust": {"item_id": 0x26B8, "hue": 0},
    "75 Arcane dust": {"item_id": 0x26B8, "hue": 0},  # lowercase variant
    "100 Arcane Dust": {"item_id": 0x26B8, "hue": 0},
    
    # Cloth
    "Random Rare Cloth": {"item_id": 0x175D, "hue": 1161},  # Cloth bolt
    
    # Resources
    "Random Bulk Resource": {"item_id": 0x1BF2, "hue": 0},  # Ingots
    "Random Runic Component": {"item_id": 0x5738, "hue": 1161},  # crystal shard
    
    # Maps and Books
    "Treasure Map": {"item_id": 0x14EC, "hue": 0},  # Treasure map
    "Runebook (Unblessed)": {"item_id": 0x0EFA, "hue": 0x0461},  # Runebook
    
    # Food and Supplies
    "Food Supply Crate": {"item_id": 0x09D0, "hue": 0},  # apple
    "Magical Rose": {"item_id": 0x0C3B, "hue": 33},  # Rose
    
    # Weapons
    "Twin's Rage Axe": {"item_id": 0x0F49, "hue": 33},  # Axe
    "Titan's Fall Axe": {"item_id": 0x0F49, "hue": 1161},
    "The Berserker's Maul": {"item_id": 0x143B, "hue": 33},  # Maul
    "Hellclap War Hammer": {"item_id": 0x143D, "hue": 1358},  # War hammer
    
    # Tools
    "Magical Pickaxe (double yield)": {"item_id": 0x0E86, "hue": 1161},  # Pickaxe
    
    # Special
    "Page of Insight": {"item_id": 0x0E34, "hue": 1161},  # Scroll
}

# Mastery Orb hue colors to indicate random orb graphics  
MASTERY_ORB_HUES = [
    2388,    # Druidic Orb
    2048,    # Blood Orb
    0x081A,  # Shadow Orb
    0x0B3A,  # Death Orb
    0x0801,  # Poison Orb
    0x04A8,  # Artisan Orb
    0x0489,  # Fira Orb
    0x0B54,  # Earth Orb
    0x0B73,  # Fortune Orb
    0x093A,  # Lyrical Orb
    0x0954,  # Druidic Orb (alt)
    0x0BA7,  # Doom Orb
    0x0AD3,  # Bulwark Orb
    0x09C3,  # Aero Orb
    0x09A4,  # Holy Orb
]

QUEST_OBJECTIVE_GRAPHICS = {
    # Easy Quests
    "Graveyard Cleanup": {"item_id": 0x20F8, "hue": 0},  # liche
    "The Exiled Ones": {"item_id": 0x0E77, "hue": 0},  # Barrel (Sturdy Armament Barrel)
    "City Cleanup": {"item_id": 0x20D0, "hue": 0},  # Rat mini
    "Simply Gross": {"item_id": 0x212A, "hue": 0},  # terathan green mini  (bog thing mob)
    "Vermin to the North": {"item_id":  0x20E3, "hue": 0},  # ratman mini
    "The Ogre Threat": {"item_id": 0x20DF, "hue": 0},  # ogre mini
    "Ghost Hunt": {"item_id": 0x2109, "hue": 0},  # ghoul mini ( deceased knight)
    
    # Medium Quests
    "Dragon's Essence": {"item_id": 0xB8B1, "hue": 0x093D},  # Moltendust 
    "Viscosity": {"item_id": 0x0E24, "hue": 0x09AF},  # Vermin Blood 
    "Daemon's Remains": {"item_id": 0x0F7E, "hue": 0x0B20},  # Daemon Bone 
    "Lack of Proof": {"item_id": 0x20E9, "hue": 0},  # troll mini ( yeti) 
    "Corrupted Blood": {"item_id": 0x0F7D, "hue": 33},  # using daemon blood here , Vial of diseased blood
    "Stolen Artifacts": {"item_id": 0x241E, "hue": 0},  # vase (elfic artifact)
    "Land of the Dead": {"item_id": 0x20F8, "hue": 0},  # grey lich mini (restless soul)
    "Scary Affiliation": {"item_id": 0x20E0, "hue": 0},  # orc mini  (mountain giant)
    "Petrified": {"item_id": 0x20D9, "hue": 0},  # gargoyle mini  (stone castle mobs)
    "Adamantium Hunt": {"item_id": 0x1BF2, "hue": 0},  # Ingot (adamantium ingot)
    "Shoes of a Giant": {"item_id": 0x212D, "hue": 0},  # cyclops min cyclops head
    "Behorn the Infidels": {"item_id": 0x2DB7, "hue": 0},  # horn (minotaur chief)
    "Sky is the Limit": {"item_id": 0x5737, "hue": 0},  # Feather (robust harpy feathers)
    "Desert Cleanup": {"item_id": 0x20ED, "hue": 0},  # air ele min (greater sand vortex)
    "Frozen Cleansing": {"item_id": 0x20E1, "hue": 0},  # polar bear mini (frozen isle mobs)
    "Lava Cleansing": {"item_id": 0x572D, "hue": 0},  # lava serpent crust (lava hill mobs)
    "Contamination": {"item_id": 0x0C67, "hue": 0},  # acid sac (venemous larvaes)
    "Toxic Flora": {"item_id": 0x20D2, "hue": 0},  # corpser mini
    
    # Hard Quests
    "All Aboard!": {"item_id": 0x210C, "hue": 0},  # human male mini (bilgewater captain)
    "Tailoring Hell": {"item_id": 0x1079, "hue": 0},  # Leather (infernal hide)
    "Gigantic!": {"item_id": 0x26B4, "hue": 0},  # Scales (lizardman scales)
    "Evil Within": {"item_id": 0x20D3, "hue": 0},  # demon mini  (pit fiend)
    "Death Wings": {"item_id": 0x20DC, "hue": 33},  # harpy mini (harpy prince)
    "Ancient Sanctuary": {"item_id": 0x20FA, "hue": 0},  # reaper tree mini (feywind guardian)
}

DEBUG_LEVEL = 1  # 1=normal, 2=verbose
SHOW_MASTERY_ORB_HEADER = False  # Show "Mastery Orb Quests" header line , this is inferred by the reward graphic

QUEST_NAME_MAX_LENGTH = 35  # Max character length for quest names 
PROGRESS_MAX_LENGTH = 25  # Max character length for progress text 
COLUMN_SEPARATOR_SPACES = 2  # Number of spaces between quest name and progress columns
# Icon positioning (offset from right edge of gump)
OBJECTIVE_ICON_OFFSET = 206  # Objective icon offset from right edge (larger = more left)
REWARD_ICON_OFFSET = 50  # Reward icon offset from right edge (larger = more left)

# Daily Quest gump configuration
QUEST_GUMP_ID = 0xFBCC3FF  # Daily quest status gump ID
BUTTON_NEXT = 2  # Next page button
BUTTON_PREV = 1  # Previous page button

# Retry
MAX_CONSECUTIVE_FAILURES = 20  # Keep trying navigation
MAX_NAVIGATION_ATTEMPTS = 100  # dont give up if we have missing pages
MAX_PAGE_1_RETRIES = 5  # Maximum times to retry page 1

# Timing 
WAIT_GUMP_MS = 3000
LOOP_PAUSE_MS = 100
JITTER_MS = 50
GUMP_WAIT_AFTER_BUTTON = 3000  # Wait for gump to update after button click using WaitForGump
COMMAND_DELAY = 1200  # Delay before sending button command 

# Custom gump output results 
# example max  =  4294967295 #  a high pseudo-random gump id to avoid other existing gump ids
DISPLAY_GUMP_ID = 4145545746
DISPLAY_X = 100
DISPLAY_Y = 100
DISPLAY_WIDTH = 402
DISPLAY_HEIGHT = 700

MAX_PAGES = 15  # Set higher than expected 11 pages for future quests added

# Colors for gump display
COLORS = {
    'title': 68,       # blue
    'label': 1153,     # light gray
    'ok': 63,          # green
    'warn': 53,        # yellow
    'bad': 33,         # red
    'info': 90,        # cyan
}

# HTML colors for text display , GREEN < BLUE < RED color scheme
HTML_COLORS = {
    'completed': '#335544',    # dark gray
    'active': '#3FA9FF',       # blue
    'available': '#FFB84D',    # orange
    'failed': '#FF6B6B',       # red
    'header': '#CCCCCC',       # light gray (default text)
    'progress': '#888888',     # medium gray
    'title': '#555555',        # dark gray
    'separator': '#555555',    # dark gray
    'stats': '#333333',        # very dark gray - for page/quest counts
    'mastery_orb': '#FFD700',  # gold - for mastery orb quests
    'difficulty_easy': '#90EE90',    # light green 90EE90 darker e6ffee
    'difficulty_medium': '#6B9BD1',  # muted blue 6B9BD1 darker 3399ff
    'difficulty_hard': '#FF6B6B',    # red FF6B6B redorange ff3300
}

# HTML colors for text display , alternate variation burnt brown and orange 
HTML_COLORS_BURNT = {
    'completed': '#5C3317',    # darker desaturated brown (burnt brown for completed)
    'active': '#3FA9FF',       # blue (unchanged)
    'available': '#FFB84D',    # orange (unchanged)
    'failed': '#FF6B6B',       # red (unchanged)
    'header': '#CCCCCC',       # light gray (unchanged)
    'progress': '#888888',     # medium gray (unchanged)
    'title': '#555555',        # dark gray (unchanged)
    'separator': '#555555',    # dark gray (unchanged)
    'stats': '#333333',        # very dark gray (unchanged)
    'mastery_orb': '#FFD700',  # gold (unchanged) A0724F
    'difficulty_easy': '#A0724F',    # darker desaturated brown (burnt orange-brown for easy)
    'difficulty_medium': '#8B5A2B',  # darker desaturated orange-brown (medium)
    'difficulty_hard': '#CC3300',    # darker desaturated red-orange (burnt red-orange for hard)
}

# NOTES:
"""
say = "[quest" , a command to open the daily quest gump 
daily quest gump id =  0xfbcc3ff
gump button id 2 = Next 
"""
# example of the daily quest gump readlines output=
"""
[0] '<CENTER><BASEFONT COLOR=WHITE>Page 1 of 11</CENTER>'
[1] '<CENTER><BASEFONT COLOR=ORANGE>City Cleanup (Britain)</CENTER>'
[2] '<CENTER><BASEFONT COLOR=WHITE>Kill giant rat vermins roaming Britain city, it stinks!</CENTER>'
[3] '<CENTER><BASEFONT COLOR=WHITE>Kills: 7/20</CENTER>'
[4] '<CENTER><BASEFONT COLOR=LIME>The Ogre Threat (Ogre Valley)</CENTER>'
[5] '<CENTER><BASEFONT COLOR=RED>In Cooldown (22h 39m)</CENTER>'
[6] '6160'
[7] '<CENTER><BASEFONT COLOR=ORANGE>Viscosity (Shame)</CENTER>'
[8] '<CENTER><BASEFONT COLOR=WHITE>Collect poison from the bugs within Shame, you will need an empty vial kit!</CENTER>'
[9] '<CENTER><BASEFONT COLOR=WHITE>Collected: 11/15</CENTER>'
[10] '<BASEFONT COLOR=WHITE>Next'
"""

# ===== ========================================= =====

def get_active_colors():
    """Return the active HTML color scheme based on USE_BURNT_COLOR_SCHEME setting."""
    return HTML_COLORS_BURNT if USE_BURNT_COLOR_SCHEME else HTML_COLORS

def debug_message(msg, color=68, level=1):
    """Send debug message to game client."""
    if DEBUG_MODE and level <= DEBUG_LEVEL:
        try:
            prefix = "[QuestStatus]" if level == 1 else "[DEBUG]"
            Misc.SendMessage(f"{prefix} {msg}", color)
        except Exception:
            print(f"[QuestStatus] {msg}")

def pause_ms(ms):
    """Pause for specified milliseconds."""
    try:
        Misc.Pause(int(ms))
    except Exception:
        Misc.Pause(int(ms))

def wait_for_quest_gump(timeout_ms=WAIT_GUMP_MS):
    """Wait for the specific quest gump ID to appear using WaitForGump."""
    try:
        # Use Gumps.WaitForGump to wait for the specific quest gump
        result = Gumps.WaitForGump(QUEST_GUMP_ID, timeout_ms)
        if result:
            pause_ms(200)  # Small stabilization delay
            return True
        return False
    except Exception as e:
        debug_message(f"wait_for_quest_gump error: {e}", COLORS['bad'], 2)
        return False

def ensure_gump_open(allow_reopen=True):
    """Check if quest gump is open, optionally reopen if closed.
    allow_reopen: If True, reopens gump when closed. If False, just checks.
    Returns:        True if gump is open (or was successfully reopened), False otherwise
    """
    try:
        if Gumps.HasGump():
            return True
        
        if not allow_reopen:
            return False
        
        debug_message("Quest gump closed unexpectedly, reopening...", COLORS['warn'])
        pause_ms(400)  # was 800ms 
        return open_quest_gump()
    except Exception as e:
        debug_message(f"ensure_gump_open error: {e}", COLORS['bad'], 2)
        return False

def skip_to_page(target_page, current_page=1, max_attempts=20):
    """Quickly skip ahead to a target page by pressing NEXT multiple times.
    BLIND NAVIGATION - just presses NEXT repeatedly without reading pages.
    use minimal API calls.
    Returns:
        True if completed button presses, False if gump closed
    """
    if target_page <= current_page:
        return True  # Already at or past target
    
    pages_to_skip = target_page - current_page
    debug_message(f"Skip ahead: BLIND navigation to page {target_page} from {current_page} ({pages_to_skip} NEXT presses)", COLORS['info'])
    
    # Press NEXT button the required number of times using reliable pattern
    for i in range(min(pages_to_skip, max_attempts)):
        try:
            # Simple pattern: SendAction -> WaitForGump with long timeout 
            Gumps.SendAction(QUEST_GUMP_ID, BUTTON_NEXT)
            if not Gumps.WaitForGump(QUEST_GUMP_ID, 10000):
                debug_message(f"Gump closed during skip ahead at press {i+1}", COLORS['bad'])
                return False
        except Exception as e:
            debug_message(f"Error during skip ahead at press {i+1}: {e}", COLORS['bad'])
            return False
    
    debug_message(f"Skip ahead complete: pressed NEXT {pages_to_skip} times", COLORS['ok'])
    return True

def snap_text_lines():
    """Capture text lines from the quest gump using GetLineList with specific gump ID.
    Uses Gumps.GetLineList(gumpId, dataOnly) to read from the SPECIFIC quest gump ID.
    """
    try:
        debug_message(f"snap_text_lines: Reading from quest gump {hex(QUEST_GUMP_ID)}", 115, 2)
        
        # Use GetLineList with the specific quest gump ID
        # dataOnly=False to get all text including labels
        try:
            lines = Gumps.GetLineList(QUEST_GUMP_ID, False)
            debug_message(f"  Gumps.GetLineList({hex(QUEST_GUMP_ID)}, False) returned {len(lines) if lines else 0} lines", 115, 2)
            if lines:
                result = [str(ln).strip() for ln in lines]
                debug_message(f"  Successfully extracted {len(result)} text lines", 115, 2)
                return result
            else:
                debug_message("  GetLineList returned empty/None", 115, 2)
        except Exception as e:
            debug_message(f"  ERROR: Gumps.GetLineList() failed: {e}", COLORS['bad'], 1)
        
        return []
    except Exception as e:
        debug_message(f"snap_text_lines: Outer exception: {e}", COLORS['bad'], 1)
        return []

def open_quest_gump():
    """Open the quest status gump using the [quest command.
    The quest gump has ID 0xFBCC3FF 
    """
    debug_message(f"Opening quest gump (ID: {hex(QUEST_GUMP_ID)})", COLORS['info'])
    try:
        # Close any existing gumps
        try:
            Gumps.ResetGump()
        except Exception:
            pass
        
        # CRITICAL: Wait before sending command to avoid "wait a moment" message
        pause_ms(1000)
        
        # Send the [quest command
        Player.ChatSay(0, "[quest")
        
        # Wait for the SPECIFIC quest gump to appear
        if not wait_for_quest_gump(WAIT_GUMP_MS):
            debug_message(f"Quest gump {hex(QUEST_GUMP_ID)} did not appear", COLORS['bad'])
            return False
        
        debug_message(f"Quest gump {hex(QUEST_GUMP_ID)} opened successfully", COLORS['ok'])
        
        # CRITICAL: Longer initial wait for gump to fully load
        pause_ms(800)
        
        # Wait and verify we can read lines (retry up to 8 times with longer delays)
        for retry in range(8):
            pause_ms(600)  # Increased from 400ms
            lines = snap_text_lines()
            if lines:
                debug_message(f"Gump data ready: {len(lines)} lines captured", COLORS['ok'])
                # Extra stabilization after successful read
                pause_ms(400)
                return True
            debug_message(f"Retry {retry + 1}/8: waiting for gump data...", COLORS['warn'])
        
        debug_message("Failed to capture gump data after retries", COLORS['bad'])
        return False
    except Exception as e:
        debug_message(f"Error opening quest gump: {e}", COLORS['bad'])
        return False

def clean_html_tags(text):
    """Remove HTML tags from text."""
    if not text:
        return ''
    # Remove HTML tags like <CENTER>, <BASEFONT COLOR=WHITE>, etc.
    cleaned = re.sub(r'<[^>]+>', '', text)
    return cleaned.strip()

def extract_page_info(lines):
    """Extract page number info from lines like 'Page 1 of 11'.
    Returns tuple: (current_page, total_pages) or (None, None) if not found.
    """
    if not lines:
        return None, None
    
    for line in lines:
        cleaned = clean_html_tags(line)
        # Look for "Page X of Y" pattern
        match = re.search(r'page\s+(\d+)\s+of\s+(\d+)', cleaned, re.IGNORECASE)
        if match:
            try:
                current = int(match.group(1))
                total = int(match.group(2))
                return current, total
            except Exception:
                pass
    
    return None, None

def should_skip_line(line):
    """Check if a line should be skipped (pagination, navigation, etc.)."""
    if not line:
        return True
    
    # Clean HTML tags for checking
    cleaned = clean_html_tags(line)
    if not cleaned:
        return True
    
    cleaned_lower = cleaned.lower()
    
    # Skip pagination info (e.g., "Page 2 of 11")
    if re.search(r'page\s+\d+\s+of\s+\d+', cleaned_lower):
        return True
    
    # Skip navigation buttons
    if cleaned_lower in ['quest log', 'quests', 'page', 'next', 'previous', 'back', 'close']:
        return True
    
    # Skip pure numbers (like "6160")
    if re.match(r'^\d+$', cleaned):
        return True
    
    return False

def parse_quest_page(lines):
    """Parse quest information from gump text lines.
    
    Quest format from debug:
    - Line 0: Page info (skip)
    - Line 1: Quest name (ORANGE color)
    - Line 2: Quest description
    - Line 3: Progress (Kills: 7/20 or Collected: 11/15) OR Status (In Cooldown)
    - Line 4: Next quest name...
    """
    if not lines:
        return []
    
    # Debug: show all lines being analyzed
    debug_message("=== Analyzing Gump Lines ===", 1)
    for idx, line in enumerate(lines):
        debug_message(f"  [{idx}] {repr(line)}", 1)
    debug_message("=== End Gump Lines ===", 1)
    
    quests = []
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        cleaned = clean_html_tags(line)
        
        # Skip lines that should be ignored
        if should_skip_line(line):
            debug_message(f"Skipping line [{i}]: {repr(cleaned)}", 2)
            i += 1
            continue
        
        # Check if this is a quest name (ORANGE or LIME colored)
        if 'COLOR=ORANGE' in line or 'COLOR=LIME' in line:
            quest_name = cleaned
            is_lime = 'COLOR=LIME' in line  # LIME = completed quest
            
            quest_data = {
                'name': quest_name,
                'description': '',
                'progress': '',
                'status': '',
                'raw_lines': [quest_name]
            }
            
            debug_message(f"Found quest name [{i}]: {repr(quest_name)} (LIME={is_lime})", 1)
            i += 1
            
            # If LIME colored, next line is likely "Completed!" or cooldown - handle specially
            if is_lime and i < len(lines):
                next_line = lines[i].strip()
                next_cleaned = clean_html_tags(next_line)
                
                # Check if next line is "Completed!" or cooldown message
                if next_cleaned and ('completed' in next_cleaned.lower() or 'cooldown' in next_cleaned.lower()):
                    quest_data['status'] = 'Completed'
                    quest_data['progress'] = next_cleaned
                    quest_data['raw_lines'].append(next_cleaned)
                    debug_message(f"  Completed status [{i}]: {repr(next_cleaned)}", 2)
                    i += 1  # Skip this line, move to next
                # Otherwise treat as normal description
                else:
                    quest_data['description'] = next_cleaned
                    quest_data['status'] = 'Completed'  # LIME means completed
                    quest_data['raw_lines'].append(next_cleaned)
                    debug_message(f"  Description [{i}]: {repr(next_cleaned)}", 2)
                    i += 1
            # ORANGE colored - normal active quest
            elif i < len(lines):
                desc_line = lines[i].strip()
                desc_cleaned = clean_html_tags(desc_line)
                if desc_cleaned and not should_skip_line(desc_line):
                    quest_data['description'] = desc_cleaned
                    quest_data['raw_lines'].append(desc_cleaned)
                    debug_message(f"  Description [{i}]: {repr(desc_cleaned)}", 2)
                    i += 1
                
                # Next line should be progress or status
                if i < len(lines):
                    status_line = lines[i].strip()
                    status_cleaned = clean_html_tags(status_line)
                    
                    if status_cleaned and not should_skip_line(status_line):
                        # Check for cooldown
                        if 'cooldown' in status_cleaned.lower():
                            quest_data['status'] = 'Completed (Cooldown)'
                            quest_data['progress'] = status_cleaned
                            debug_message(f"  Cooldown [{i}]: {repr(status_cleaned)}", 2)
                        # Check for progress patterns (Kills: X/Y, Collected: X/Y)
                        elif re.search(r'(kills|collected|gathered|delivered):\s*\d+/\d+', status_cleaned, re.IGNORECASE):
                            # Check if quest is completed (X/Y where X == Y)
                            match = re.search(r'(\d+)/(\d+)', status_cleaned)
                            if match:
                                current = int(match.group(1))
                                total = int(match.group(2))
                                if current >= total:
                                    quest_data['status'] = 'Completed'
                                    quest_data['progress'] = status_cleaned
                                    debug_message(f"  Completed [{i}]: {repr(status_cleaned)}", 2)
                                else:
                                    quest_data['status'] = 'Active'
                                    quest_data['progress'] = status_cleaned
                                    debug_message(f"  Progress [{i}]: {repr(status_cleaned)}", 2)
                            else:
                                quest_data['status'] = 'Active'
                                quest_data['progress'] = status_cleaned
                                debug_message(f"  Progress [{i}]: {repr(status_cleaned)}", 2)
                        else:
                            quest_data['status'] = status_cleaned
                            debug_message(f"  Status [{i}]: {repr(status_cleaned)}", 2)
                        
                        quest_data['raw_lines'].append(status_cleaned)
                        i += 1
            
            # Add quest if we have valid data
            if quest_data['name']:
                quests.append(quest_data)
                debug_message(f"Added quest: {quest_data['name']} | Status: {quest_data['status']} | Progress: {quest_data['progress']}", 1)
        else:
            # Not a quest name, skip
            debug_message(f"Skipping non-quest line [{i}]: {repr(cleaned)}", 2)
            i += 1
    
    return quests

def crawl_all_quest_pages(max_pages=MAX_PAGES, retry_attempt=0):
    """Crawl all pages of the quest gump and collect quest data.
    
    Returns dict with:
    - quests: list of all quest dictionaries
    - pages_scanned: number of pages processed
    - timestamp: when the scan was performed
    """
    if retry_attempt > 0:
        debug_message(f"Starting quest page crawl (Retry {retry_attempt})", COLORS['warn'])
    else:
        debug_message("Starting quest page crawl", COLORS['info'])
    
    if not open_quest_gump():
        return {
            'quests': [],
            'pages_scanned': 0,
            'timestamp': 'N/A',
            'error': 'Failed to open quest gump'
        }
    
    all_quests = []
    seen_page_numbers = set()  # Track which page numbers we've collected
    pages_with_quests = {}  # Track quest count per page: {page_num: quest_count}
    pages_scanned = 0
    expected_total_pages = None
    consecutive_failures = 0
    navigation_attempts = 0  # Track how many times we've tried navigating
    last_page_seen = None  # Track last page number to detect overshooting
    stuck_counter = 0  # Track if we're stuck on unreadable pages
    unstick_attempts = 0  # Track consecutive unstick NEXT attempts
    page_1_retry_count = 0  # Track retries for page 1
    
    # Give initial gump time to stabilize (already waited in open_quest_gump)
    pause_ms(1000)  # Increased from 600ms for extra safety the first gump open is slow 
    
    # Keep trying until we get all pages - repeat if we have missing pages
    while pages_scanned < max_pages:
        # Only check navigation attempts if we have all expected pages
        if expected_total_pages and len(seen_page_numbers) >= expected_total_pages:
            debug_message(f"Have all {expected_total_pages} pages, stopping", COLORS['ok'])
            break
        
        # If we've tried too many times but still missing pages, use skip ahead
        if navigation_attempts >= MAX_NAVIGATION_ATTEMPTS:
            if expected_total_pages and len(seen_page_numbers) < expected_total_pages:
                missing = set(range(1, expected_total_pages + 1)) - seen_page_numbers
                debug_message(f"Hit max attempts but still missing {len(missing)} pages. Using skip ahead recovery...", COLORS['warn'])
                
                # Try to recover missing pages with skip ahead
                for missing_page in sorted(missing):
                    if not ensure_gump_open(allow_reopen=True):
                        break
                    
                    if skip_to_page(missing_page, current_page=1):
                        pause_ms(1200)  # Extra time after skip-ahead to let gump refresh
                        lines = snap_text_lines()
                        if lines:
                            current_page, _ = extract_page_info(lines)
                            if current_page == missing_page and current_page not in seen_page_numbers:
                                page_quests = parse_quest_page(lines)
                                all_quests.extend(page_quests)
                                seen_page_numbers.add(current_page)
                                debug_message(f"Recovered missing page {current_page}!", COLORS['ok'])
                
                # Check if we got everything
                if len(seen_page_numbers) >= expected_total_pages:
                    debug_message(f"SUCCESS: Recovered all pages!", COLORS['ok'])
                    break
                else:
                    debug_message(f"Still missing pages after recovery, continuing...", COLORS['warn'])
                    navigation_attempts = 0  # Reset and try again
            else:
                debug_message(f"Hit max navigation attempts, stopping", COLORS['warn'])
                break
        navigation_attempts += 1
        
        # Get current page text from the quest gump
        lines = snap_text_lines()
        
        if not lines:
            consecutive_failures += 1
            stuck_counter += 1
            unstick_attempts += 1
            debug_message(f"Can't read page (failures: {consecutive_failures}, stuck: {stuck_counter}, unstick: {unstick_attempts})", COLORS['warn'])
            
            # Check if gump is closed early - reopen immediately instead of retrying
            has_gump = Gumps.HasGump()
            if not has_gump:
                debug_message("Gump closed detected, reopening immediately...", COLORS['warn'])
                pause_ms(300)
                if open_quest_gump():
                    debug_message("Gump reopened successfully", COLORS['ok'])
                    # Skip to next missing page if we have any
                    if expected_total_pages and len(seen_page_numbers) > 0:
                        missing = set(range(1, expected_total_pages + 1)) - seen_page_numbers
                        if missing:
                            next_missing = min(missing)
                            debug_message(f"Skipping to missing page {next_missing}", COLORS['info'])
                            pause_ms(400)
                            skip_to_page(next_missing, current_page=1)
                            pause_ms(1200)
                    unstick_attempts = 0
                    consecutive_failures = 0
                    stuck_counter = 0
                    continue
                else:
                    debug_message("Failed to reopen gump", COLORS['bad'])
                    break
            
            # SPECIAL PAGE 1 FAILURE PROTOCOL: If we haven't read ANY pages yet , force gump reset
            if len(seen_page_numbers) == 0 and page_1_retry_count < MAX_PAGE_1_RETRIES:
                page_1_retry_count += 1
                debug_message(f"PAGE 1 FAILURE PROTOCOL: Retry {page_1_retry_count}/{MAX_PAGE_1_RETRIES} - Closing and reopening gump", COLORS['warn'])
                
                # Close the gump explicitly
                try:
                    Gumps.CloseGump(QUEST_GUMP_ID)
                    debug_message("Closed gump by ID", COLORS['info'])
                except Exception as e:
                    debug_message(f"Error closing gump: {e}", COLORS['warn'])
                
                pause_ms(500)  # Reduced from 1000ms for faster recovery
                
                # Reopen fresh
                if open_quest_gump():
                    debug_message("Gump reopened, retrying page 1", COLORS['ok'])
                    pause_ms(800)  # was  1200ms , but using the waitfor gump sped up read times and we can just try skipahead , so ok if we accidentally reset sometimes
                    consecutive_failures = 0
                    stuck_counter = 0
                    unstick_attempts = 0
                    navigation_attempts = 0  # Reset navigation counter
                    continue
                else:
                    debug_message("Failed to reopen gump for page 1 retry", COLORS['bad'])
                    if page_1_retry_count >= MAX_PAGE_1_RETRIES:
                        debug_message(f"Exhausted {MAX_PAGE_1_RETRIES} page 1 retries, giving up", COLORS['bad'])
                        break
                    continue
            
            # After 1 unstick attempt (reduced from 2), try reopening
            if unstick_attempts >= 1:
                debug_message("Quick reopen after unstick attempt...", COLORS['warn'])
                pause_ms(300)
                if open_quest_gump():
                    # Skip to next missing page if we have any
                    if expected_total_pages and len(seen_page_numbers) > 0:
                        missing = set(range(1, expected_total_pages + 1)) - seen_page_numbers
                        if missing:
                            next_missing = min(missing)
                            debug_message(f"After reopen, skipping to page {next_missing}", COLORS['info'])
                            pause_ms(400)
                            skip_to_page(next_missing, current_page=1)
                            pause_ms(1200)
                    unstick_attempts = 0
                    consecutive_failures = 0
                    stuck_counter = 0
                    continue
                else:
                    debug_message("Failed to reopen gump", COLORS['bad'])
                    unstick_attempts = 0
                    continue
            
            # Simple recovery: use NEXT (only if gump is still open)
            debug_message(f"Trying NEXT to unstick (attempt {unstick_attempts}/1)...", COLORS['info'])
            try:
                Gumps.SendAction(QUEST_GUMP_ID, BUTTON_NEXT)
                if not Gumps.WaitForGump(QUEST_GUMP_ID, 5000):  # Reduced timeout from 10s to 5s
                    debug_message("Gump closed during unstick", COLORS['bad'])
                continue
            except Exception as e:
                debug_message(f"Error: {e}", COLORS['bad'])
            
            # After many failures, check if gump closed
            if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                # Check if gump is actually closed
                has_gump = Gumps.HasGump()
                debug_message(f"[DEBUG] After {MAX_CONSECUTIVE_FAILURES} failures, HasGump() = {has_gump}", COLORS['warn'], 1)
                if not has_gump:
                    # DON'T reopen if we have missing pages - we'll lose progress
                    if expected_total_pages and len(seen_page_numbers) < expected_total_pages:
                        missing = set(range(1, expected_total_pages + 1)) - seen_page_numbers
                        next_missing = min(missing) if missing else None
                        
                        if next_missing:
                            debug_message(f"Gump closed but we have missing pages. Reopening and skipping to page {next_missing}...", COLORS['warn'])
                            pause_ms(400)
                            if not open_quest_gump():
                                debug_message("Failed to reopen, stopping", COLORS['bad'])
                                break
                            pause_ms(400)
                            
                            # Skip ahead to the next missing page
                            if skip_to_page(next_missing, current_page=1):
                                pause_ms(1200)  # Extra time after skip-ahead to let gump refresh
                                consecutive_failures = 0
                                stuck_counter = 0
                                continue
                            else:
                                debug_message("Skip ahead failed, stopping", COLORS['bad'])
                                break
                    else:
                        debug_message("Gump closed, reopening...", COLORS['warn'])
                        pause_ms(400)
                        if not open_quest_gump():
                            debug_message("Failed to reopen, stopping", COLORS['bad'])
                            break
                        pause_ms(400)
                        consecutive_failures = 0
                        stuck_counter = 0
                        continue
                else:
                    # Gump exists - reset and keep exploring
                    debug_message("Resetting counters, continuing exploration...", COLORS['info'])
                    consecutive_failures = 0
                    # Don't reset stuck_counter - let it keep trying different patterns
                    continue
            continue
        
        # Reset failure counters on success
        consecutive_failures = 0
        stuck_counter = 0  # Reset stuck counter when we successfully read a page
        unstick_attempts = 0  # Reset unstick counter on successful read
        
        # Extract page info from gump
        current_page, total_pages = extract_page_info(lines)
        
        if current_page and total_pages:
            debug_message(f"Reading Page {current_page} of {total_pages}", COLORS['info'])
            
            # Store expected total on first successful read
            if expected_total_pages is None:
                expected_total_pages = total_pages
                debug_message(f"Expected total pages: {expected_total_pages}", COLORS['ok'])
            
            # Check if we overshot (jumped too far forward)
            if last_page_seen and current_page > last_page_seen + 1:
                missing_page = last_page_seen + 1
                if missing_page not in seen_page_numbers:
                    debug_message(f"Overshot! Jumped from page {last_page_seen} to {current_page}, missing page {missing_page}", COLORS['warn'])
                    # Instead, mark this for recovery at the end
                    debug_message(f"Will recover page {missing_page} later", COLORS['info'])
            
            # Check if we already have this page
            if current_page in seen_page_numbers:
                debug_message(f"Already have page {current_page}, skipping", COLORS['info'])
                
                # If we keep seeing the same page, we're stuck - use skip-ahead
                if expected_total_pages:
                    missing = set(range(1, expected_total_pages + 1)) - seen_page_numbers
                    if missing:
                        next_missing = min(missing)
                        debug_message(f"Stuck on duplicate page {current_page}, using skip-ahead to page {next_missing}", COLORS['warn'])
                        if skip_to_page(next_missing, current_page=current_page):
                            pause_ms(1200)  # Extra time after skip-ahead to let gump refresh
                            continue
                        else:
                            debug_message("Skip-ahead failed, trying normal NEXT", COLORS['warn'])
                
                # Normal skip forward
                try:
                    debug_message(f"Clicking NEXT to skip duplicate page {current_page}...", COLORS['info'])
                    Gumps.SendAction(QUEST_GUMP_ID, BUTTON_NEXT)
                    if not Gumps.WaitForGump(QUEST_GUMP_ID, 10000):
                        debug_message("Gump closed during duplicate skip", COLORS['bad'])
                        break
                except Exception:
                    break
                continue
            
            # Mark this page as seen
            seen_page_numbers.add(current_page)
            last_page_seen = current_page  # Update last seen page
        else:
            debug_message(f"Could not determine page number, processing anyway", COLORS['warn'])
        
        # Parse quests from this page
        page_quests = parse_quest_page(lines)
        quest_count_on_page = len(page_quests)
        debug_message(f"Page {current_page or '?'}: found {quest_count_on_page} quests", COLORS['ok'])
        
        # Track quest count per page (0 quests is iregular and needs recovery)
        if current_page:
            pages_with_quests[current_page] = quest_count_on_page
            if quest_count_on_page == 0:
                debug_message(f"WARNING: Page {current_page} returned 0 quests - marking for recovery", COLORS['warn'])
        
        all_quests.extend(page_quests)
        pages_scanned += 1
        
        # Check if we have all expected pages
        if expected_total_pages and len(seen_page_numbers) >= expected_total_pages:
            debug_message(f"Collected all {expected_total_pages} pages!", COLORS['ok'])
            break
        
        #  Don't click NEXT if we're on the last page OR close to it 
        if expected_total_pages and current_page:
            if current_page >= expected_total_pages:
                debug_message(f"Already on last page {current_page}, stopping", COLORS['info'])
                break
            # Also check if we're near the end and have all remaining pages
            remaining_pages = set(range(current_page + 1, expected_total_pages + 1))
            if remaining_pages.issubset(seen_page_numbers):
                debug_message(f"All remaining pages already collected, stopping", COLORS['info'])
                break
        
        # CRITICAL: Wait after reading data before clicking NEXT
        pause_ms(600)  # Give time between read and button press
        
        # Try to go to next page
        try:
            # DON'T check HasGump() here - if we just read the page, gump is open
            # HasGump() seems to return false positives after reading ( maybe too many commands ) , causing unnecessary reopens
            
            debug_message(f"Clicking NEXT to advance from page {current_page or '?'}...", COLORS['info'])
            Gumps.SendAction(QUEST_GUMP_ID, BUTTON_NEXT)
            
            # Wait for gump to update using WaitForGump with long timeout
            if not Gumps.WaitForGump(QUEST_GUMP_ID, 10000):
                debug_message("Gump did not update after NEXT, will retry on next loop...", COLORS['warn'])
                # Don't check HasGump() here - it gives false negatives
                # If gump really closed, we'll detect it when we try to read next page
        except Exception as e:
            debug_message(f"Error clicking NEXT: {e}", COLORS['bad'])
            break
    
    debug_message(f"Initial crawl: {len(all_quests)} quests from {len(seen_page_numbers)} pages", COLORS['ok'])
    
    # Identify pages that returned 0 quests (empty data)
    empty_pages = [page for page, count in pages_with_quests.items() if count == 0]
    if empty_pages:
        debug_message(f"Found {len(empty_pages)} pages with 0 quests: {sorted(empty_pages)}", COLORS['warn'])
    
    # Missing page recovery - try up to 50 attempts
    recovery_attempts = 0
    MAX_RECOVERY_ATTEMPTS = 50
    
    while recovery_attempts < MAX_RECOVERY_ATTEMPTS:
        recovery_attempts += 1
        
        if not expected_total_pages:
            break
        
        # Find missing pages AND pages with 0 quests
        missing = set(range(1, expected_total_pages + 1)) - seen_page_numbers
        empty_pages_to_retry = [page for page, count in pages_with_quests.items() if count == 0]
        pages_to_recover = sorted(set(list(missing) + empty_pages_to_retry))
        
        if not pages_to_recover:
            debug_message("All pages collected with quest data", COLORS['ok'])
            break
        
        debug_message(f"Recovery attempt {recovery_attempts}/{MAX_RECOVERY_ATTEMPTS}: {len(pages_to_recover)} pages to recover: {pages_to_recover}", COLORS['warn'])
        
        # Try skip ahead to each page that needs recovery
        for target_page in pages_to_recover:
            # Ensure gump is open
            if not ensure_gump_open(allow_reopen=True):
                debug_message("Cannot ensure gump open, trying to reopen...", COLORS['warn'])
                pause_ms(400)  # 1000ms 
                if not open_quest_gump():
                    pause_ms(600)  # 1500ms
                    continue
            
            pause_ms(400)  #  600ms 
            
            # Skip to the target page 
            debug_message(f"Attempting to recover page {target_page}...", COLORS['info'])
            if skip_to_page(target_page, current_page=1):
                pause_ms(1500)  # Extra time after skip-ahead to let gump refresh at target page
                lines = snap_text_lines()
                if lines:
                    current_page, _ = extract_page_info(lines)
                    if current_page == target_page:
                        page_quests = parse_quest_page(lines)
                        quest_count = len(page_quests)
                        
                        # Update quest count for this page
                        pages_with_quests[current_page] = quest_count
                        
                        if quest_count > 0:
                            # Remove old quests from this page if retrying
                            if current_page in seen_page_numbers:
                                # Filter out quests from this page and re-add
                                debug_message(f"Re-reading page {current_page} (had 0 quests before)", COLORS['info'])
                            all_quests.extend(page_quests)
                            seen_page_numbers.add(current_page)
                            debug_message(f"Recovered page {current_page} with {quest_count} quests!", COLORS['ok'])
                        else:
                            debug_message(f"Page {current_page} still has 0 quests after recovery", COLORS['warn'])
                            seen_page_numbers.add(current_page)  # Mark as seen to avoid infinite retry
                    else:
                        debug_message(f"Skip ahead landed on page {current_page}, wanted {target_page}", COLORS['warn'])
            
            # Check if all pages have quest data
            empty_check = [p for p, c in pages_with_quests.items() if c == 0]
            if len(seen_page_numbers) >= expected_total_pages and len(empty_check) == 0:
                debug_message(f"SUCCESS: All {expected_total_pages} pages with quest data!", COLORS['ok'])
                break
        
        # If we got all pages, break outer loop
        if len(seen_page_numbers) >= expected_total_pages:
            break
        
        # Still missing pages, try random navigation
        if len(seen_page_numbers) < expected_total_pages:
            debug_message("Trying random navigation to find remaining pages...", COLORS['info'])
            for _ in range(5):
                if not ensure_gump_open(allow_reopen=True):
                    break
                
                Gumps.SendAction(QUEST_GUMP_ID, BUTTON_NEXT)
                if Gumps.WaitForGump(QUEST_GUMP_ID, 10000):
                    lines = snap_text_lines()
                    if lines:
                        current_page, _ = extract_page_info(lines)
                        if current_page and current_page not in seen_page_numbers:
                            page_quests = parse_quest_page(lines)
                            if page_quests:
                                all_quests.extend(page_quests)
                                seen_page_numbers.add(current_page)
                                debug_message(f"Found page {current_page} via navigation!", COLORS['ok'])
    
    # Final validation - check pages and identify empty pages
    quest_count = len(all_quests)
    pages_collected = len(seen_page_numbers)
    empty_pages_final = [page for page, count in pages_with_quests.items() if count == 0]
    
    if expected_total_pages:
        missing_pages = set(range(1, expected_total_pages + 1)) - seen_page_numbers
        pages_ok = pages_collected >= expected_total_pages
        has_empty_pages = len(empty_pages_final) > 0
        
        if pages_ok and not has_empty_pages:
            debug_message(f"SUCCESS: {pages_collected}/{expected_total_pages} pages, {quest_count} quests", COLORS['ok'])
        elif pages_ok and has_empty_pages:
            # Got all pages but some returned 0 quests
            debug_message(f"WARNING: Got all {pages_collected} pages but {len(empty_pages_final)} pages have 0 quests: {sorted(empty_pages_final)}", COLORS['warn'])
            debug_message(f"Total: {quest_count} quests - results may be incomplete", COLORS['warn'])
        elif not pages_ok:
            debug_message(f"INCOMPLETE: Got {pages_collected}/{expected_total_pages} pages, {quest_count} quests", COLORS['bad'])
            debug_message(f"Missing pages: {sorted(missing_pages)}", COLORS['bad'])
            if has_empty_pages:
                debug_message(f"Empty pages: {sorted(empty_pages_final)}", COLORS['bad'])
    else:
        # No expected page count
        debug_message(f"Collected {pages_collected} pages, {quest_count} quests", COLORS['ok'])
        if empty_pages_final:
            debug_message(f"Pages with 0 quests: {sorted(empty_pages_final)}", COLORS['warn'])
    
    # CRITICAL: If we have NO quests at all, return error instead of empty data
    if quest_count == 0:
        debug_message("CRITICAL: No quests collected! Cannot display empty results.", COLORS['bad'])
        return {
            'quests': [],
            'pages_scanned': 0,
            'expected_pages': expected_total_pages,
            'timestamp': 'N/A',
            'error': 'Failed to read any quest data'
        }
    
    return {
        'quests': all_quests,
        'pages_scanned': pages_collected,
        'expected_pages': expected_total_pages,
        'timestamp': 'N/A',
        'quest_count': quest_count,
        'empty_pages': empty_pages_final,  # List of pages that returned 0 quests
        'is_complete': len(empty_pages_final) == 0 and (not expected_total_pages or pages_collected >= expected_total_pages)
    }

# ===== Quest Data Enrichment Functions =====

def extract_quest_base_name(quest_name):
    """Extract the base quest name without location suffix.
    Args:
        quest_name: Full quest name like "City Cleanup (Britain)" or "Viscosity (Shame)"
    Returns:
        Base name like "City Cleanup" or "Viscosity"
    """
    # Remove location suffix in parentheses
    match = re.match(r'^(.+?)\s*\([^)]+\)\s*$', quest_name)
    if match:
        return match.group(1).strip()
    return quest_name.strip()

def get_quest_details(quest_name):
    """Get quest details from QUEST_DATA_DIFFICULTY_REWARD dictionary.
    Args:
        quest_name: Quest name to lookup (with or without location suffix)
    Returns:
        Dictionary with quest details (difficulty, preferred_reward) or None if not found
    
    Expected QUEST_DATA_DIFFICULTY_REWARD format:
        {
            "Quest Name": {
                "difficulty": "Easy|Medium|Hard",
                "preferred_reward": "Reward name",
            }
        }
    """
    # Extract base quest name (remove location suffix)
    base_name = extract_quest_base_name(quest_name)
    
    # Try exact match first
    if base_name in QUEST_DATA_DIFFICULTY_REWARD:
        return QUEST_DATA_DIFFICULTY_REWARD[base_name]
    
    # Try case-insensitive match
    for key in QUEST_DATA_DIFFICULTY_REWARD:
        if key.lower() == base_name.lower():
            return QUEST_DATA_DIFFICULTY_REWARD[key]
    
    return None

def is_mastery_orb_quest(quest_name):
    """Check if a quest rewards a Mastery Orb.
    Returns:
        True if quest's preferred_reward contains "Random Mastery Orb", False otherwise
    """
    base_name = extract_quest_base_name(quest_name)
    
    # Get quest data from QUEST_DATA_DIFFICULTY_REWARD
    quest_data = QUEST_DATA_DIFFICULTY_REWARD.get(base_name)
    if not quest_data:
        # Try case-insensitive match
        for key in QUEST_DATA_DIFFICULTY_REWARD:
            if key.lower() == base_name.lower():
                quest_data = QUEST_DATA_DIFFICULTY_REWARD[key]
                break
    
    if not quest_data:
        return False
    
    # Check if preferred_reward contains "Random Mastery Orb"
    preferred_reward = quest_data.get('preferred_reward', '')
    return 'Random Mastery Orb' in preferred_reward

def get_difficulty_color(difficulty):
    """Get HTML color for quest difficulty.
    Args:
        difficulty: Difficulty string ("Easy", "Medium", "Hard")
    Returns:
        HTML color code from active color scheme
    """
    colors = get_active_colors()
    if not difficulty:
        return colors['header']
    
    difficulty_lower = difficulty.lower()
    if difficulty_lower == 'easy':
        return colors['difficulty_easy']
    elif difficulty_lower == 'medium':
        return colors['difficulty_medium']
    elif difficulty_lower == 'hard':
        return colors['difficulty_hard']
    else:
        return colors['header']

# Global counter for cycling through mastery orb hues
_mastery_orb_hue_index = None

def get_reward_icon_info(quest_name):
    """Get reward icon information for a quest.
    Returns:
        Dictionary with 'item_id' and 'hue', or None if no reward icon found

    Uses QUEST_DATA_DIFFICULTY_REWARD to find preferred_reward, then REWARD_ITEM_GRAPHICS for icon.
    For Random Mastery Orb, cycles through MASTERY_ORB_HUES based on time seed to avoid duplicates.
    """
    global _mastery_orb_hue_index
    
    base_name = extract_quest_base_name(quest_name)
    
    # Get quest data to find preferred reward from QUEST_DATA_DIFFICULTY_REWARD
    quest_data = QUEST_DATA_DIFFICULTY_REWARD.get(base_name)
    if not quest_data:
        # Try case-insensitive match
        for key in QUEST_DATA_DIFFICULTY_REWARD:
            if key.lower() == base_name.lower():
                quest_data = QUEST_DATA_DIFFICULTY_REWARD[key]
                break
    
    if not quest_data:
        return None
    
    preferred_reward = quest_data.get('preferred_reward')
    if not preferred_reward:
        return None
    
    # Get reward graphics
    reward_graphic = REWARD_ITEM_GRAPHICS.get(preferred_reward)
    if not reward_graphic:
        return None
    
    # Special handling for Random Mastery Orb - cycle through hues to avoid duplicates
    if reward_graphic and reward_graphic.get('hue') == 'random':
        hue_list = reward_graphic.get('hue_list', MASTERY_ORB_HUES)
        
        # Initialize index based on player stats if not set
        if _mastery_orb_hue_index is None:
            # Use player position + stats for pseudo-random seed
            pos = Player.Position
            seed = pos.X + pos.Y + pos.Z + Player.AR + Player.Serial + Player.Gold + Player.Weight
            _mastery_orb_hue_index = seed % len(hue_list)
        
        # Get current hue and increment index for next call
        selected_hue = hue_list[_mastery_orb_hue_index]
        _mastery_orb_hue_index = (_mastery_orb_hue_index + 1) % len(hue_list)
        
        return {
            'item_id': reward_graphic['item_id'],
            'hue': selected_hue
        }
    
    return {
        'item_id': reward_graphic['item_id'],
        'hue': reward_graphic['hue']
    }

def enrich_quest_data(quest):
    """Enrich quest data with additional information from QUEST_DATA_DIFFICULTY_REWARD.
    
    Args:
        quest: Quest dictionary with at least 'name' key
    
    Returns:
        Enhanced quest dictionary with added fields:
        - 'difficulty': Easy|Medium|Hard
        - 'is_mastery_orb': bool
        - 'difficulty_color': HTML color code
        - 'quest_details': full details dict or None
        - 'reward_icon': dict with item_id and hue, or None
    
    Modifies the quest dictionary in place and returns it.
    """
    quest_name = quest.get('name', '')
    
    # Get quest details
    details = get_quest_details(quest_name)
    quest['quest_details'] = details
    
    # Extract difficulty
    if details:
        quest['difficulty'] = details.get('difficulty', '')
        quest['difficulty_color'] = get_difficulty_color(quest['difficulty'])
    else:
        quest['difficulty'] = ''
        quest['difficulty_color'] = get_active_colors()['header']
    
    # Check if mastery orb quest
    quest['is_mastery_orb'] = is_mastery_orb_quest(quest_name)
    
    # Get reward icon info
    quest['reward_icon'] = get_reward_icon_info(quest_name)
    
    # Get objective icon info (what you collect/kill)
    quest['objective_icon'] = get_quest_objective_icon(quest_name)
    
    return quest

# ===== Quest Categorization =====

def get_difficulty_sort_key(quest):
    """Get sort key for difficulty-based sorting.
    
    Args:
        quest: Quest dictionary with 'difficulty' field
    
    Returns:
        Integer sort key (0=Easy, 1=Medium, 2=Hard, 3=Unknown)
    """
    difficulty = quest.get('difficulty', '').lower()
    if difficulty == 'easy':
        return 0
    elif difficulty == 'medium':
        return 1
    elif difficulty == 'hard':
        return 2
    else:
        return 3  # Unknown difficulties sort last

def sort_quests_by_difficulty(quest_list):
    """Sort a list of quests by difficulty if SORT_BY_DIFFICULTY is enabled.
    
    Args:
        quest_list: List of quest dictionaries
    
    Returns:
        Sorted list (or original if SORT_BY_DIFFICULTY is False)
    """
    if not SORT_BY_DIFFICULTY:
        return quest_list
    
    return sorted(quest_list, key=get_difficulty_sort_key)

def categorize_quests(quests):
    """Categorize quests by status and priority.
    
    Args:
        quests: List of quest dictionaries
    
    Returns:
        Dictionary with keys:
        - 'mastery_orb_active': Active mastery orb quests (priority)
        - 'active': Other active quests
        - 'completed': Completed/cooldown quests
        - 'available': Available quests
        - 'other': Uncategorized quests
    
    Enriches each quest with additional data before categorizing.
    """
    categories = {
        'mastery_orb_active': [],
        'active': [],
        'completed': [],
        'available': [],
        'other': []
    }
    
    for quest in quests:
        # Enrich quest with difficulty, mastery orb status, etc.
        enrich_quest_data(quest)
        
        status_lower = quest.get('status', '').lower()
        progress_lower = quest.get('progress', '').lower()
        
        # Debug categorization
        debug_message(f"Categorizing: {quest.get('name')} | Status: '{quest.get('status')}' | Progress: '{quest.get('progress')}'", 2)
        
        # "In Cooldown" or "Completed" = completed (check both status and progress)
        if 'complet' in status_lower or 'cooldown' in status_lower or 'cooldown' in progress_lower:
            categories['completed'].append(quest)
            debug_message(f"  -> Completed category", 2)
        # "Active" or "In Progress" = active
        elif 'active' in status_lower or 'progress' in status_lower:
            # Prioritize mastery orb quests
            if quest.get('is_mastery_orb', False):
                categories['mastery_orb_active'].append(quest)
                debug_message(f"  -> Mastery Orb Active category", 2)
            else:
                categories['active'].append(quest)
                debug_message(f"  -> Active category", 2)
        # "Available" or "Ready" = available
        elif 'available' in status_lower or 'ready' in status_lower:
            categories['available'].append(quest)
            debug_message(f"  -> Available category", 2)
        else:
            categories['other'].append(quest)
            debug_message(f"  -> Other category (status_lower='{status_lower}')", 2)
    
    # Sort each category by difficulty if enabled
    for category_name in categories:
        categories[category_name] = sort_quests_by_difficulty(categories[category_name])
    
    return categories

def calculate_visual_length(text):
    """Calculate visual length of text accounting for narrow characters.

    Returns:
        Approximate visual width (narrow chars count as 0.6, normal as 1.0)
    Characters like '(', ')', '.', ',', ':', ';', '!', 'i', 'l', 'I' are narrower.
    """
    narrow_chars = set('().,;:!ilI\'\"')
    visual_length = 0.0
    
    for char in text:
        if char in narrow_chars:
            visual_length += 0.6  # Narrow characters
        else:
            visual_length += 1.0  # Normal characters
    
    return visual_length

def get_quest_objective_icon(quest_name):
    """Get objective icon information for a quest.
    Returns:
        Dictionary with 'item_id' and 'hue', or None if no icon found
    """
    base_name = extract_quest_base_name(quest_name)
    return QUEST_OBJECTIVE_GRAPHICS.get(base_name)

def calculate_progress_percentage(progress_text):
    """Calculate completion percentage from progress text like "Kills: 7/20" or "3/10".
    
    Args:
        progress_text: Progress string
    
    Returns:
        Float between 0.0 and 1.0 representing completion percentage
    """

    # Look for pattern like "7/20" or "3/10"
    match = re.search(r'(\d+)/(\d+)', progress_text)
    if match:
        current = int(match.group(1))
        total = int(match.group(2))
        if total > 0:
            return current / float(total)
    
    return 0.0

def get_progress_color(progress_text):
    """Get color for progress text based on completion percentage.
    
    Args:
        progress_text: Progress string like "Kills: 7/20"
    
    Returns:
        HTML color string
    
    0% = medium gray (#888888)
    90%+ = white (#FFFFFF)
    Interpolates between gray and white based on percentage
    """
    percentage = calculate_progress_percentage(progress_text)
    
    # Interpolate between medium gray (136, 136, 136) and white (255, 255, 255)
    gray_value = 136
    white_value = 255
    
    # Linear interpolation
    current_value = int(gray_value + (white_value - gray_value) * percentage)
    
    # Convert to hex
    hex_color = f"#{current_value:02X}{current_value:02X}{current_value:02X}"
    
    return hex_color

def format_quest_line(quest_name, progress, difficulty_color):
    """Format a quest line with proper column alignment using spaces.
    
    Args:
        quest_name: Quest name string
        progress: Progress string (e.g., "Kills: 7/20")
        difficulty_color: HTML color for quest name
    
    Returns:
        Formatted HTML string with aligned columns
    
    Pads quest name accounting for visual width of characters,
    then pads progress to PROGRESS_MAX_LENGTH for alignment.
    Progress color brightness based on completion percentage.
    """
    # Calculate visual length and pad accordingly
    visual_len = calculate_visual_length(quest_name)
    target_visual_len = QUEST_NAME_MAX_LENGTH
    
    # Add spaces to reach target visual length
    spaces_needed = int(target_visual_len - visual_len)
    if spaces_needed < 0:
        spaces_needed = 0
    
    padded_name = quest_name + (" " * spaces_needed)
    
    # Build the line
    line_parts = []
    line_parts.append(f"<basefont color={difficulty_color}>{padded_name}</basefont>")
    
    if progress:
        # Adjust separator spaces for "Collected" text (5 less spaces)
        # Check case-insensitive for "collected" keyword
        if 'collected' in progress.lower():
            separator = " " * max(0, COLUMN_SEPARATOR_SPACES - 5)
        else:
            separator = " " * COLUMN_SEPARATOR_SPACES
        line_parts.append(separator)
        
        # Get progress color based on completion percentage
        progress_color = get_progress_color(progress)
        
        # Pad progress to max length for alignment
        padded_progress = progress.ljust(PROGRESS_MAX_LENGTH)
        line_parts.append(f"<basefont color={progress_color}>{padded_progress}</basefont>")
    
    return ''.join(line_parts)

def build_quest_lines(quest_data):
    """Build list of quest line data for individual rendering.
    
    Args:
        quest_data: Dictionary with 'quests', 'pages_scanned', 'expected_pages'
    
    Returns:
        List of dictionaries, each containing:
        - 'html': HTML string for the line
        - 'quest': Quest dictionary (for icon rendering)
        - 'type': 'title', 'header', 'quest', 'completed', etc.
    
    Each line will be rendered separately with precise Y positioning.
    """
    quests = quest_data.get('quests', [])
    pages = quest_data.get('pages_scanned', 0)
    expected_pages = quest_data.get('expected_pages', 0)
    
    lines = []
    colors = get_active_colors()
    
    if not quests:
        lines.append({
            'html': f"<basefont color={colors['title']}>_______ Q U E S T S _______ - {pages} Pages, 0 Quests</basefont>",
            'type': 'title',
            'quest': None
        })
        lines.append({
            'html': f"<basefont color={colors['failed']}>No quests found.</basefont>",
            'type': 'error',
            'quest': None
        })
        return lines
    
    # Categorize quests (enriches them with difficulty , mastery orb status)
    categories = categorize_quests(quests)
    
    # Title with quest count validation
    page_info = f"{pages}/{expected_pages}" if expected_pages else str(pages)
    quest_count = len(quests)
    is_complete = quest_data.get('is_complete', True)
    empty_pages = quest_data.get('empty_pages', [])
    
    # Add warning indicator if incomplete or has empty pages
    if not is_complete or len(empty_pages) > 0:
        warning_text = f"WARNING: {page_info} Pages, {quest_count} Quests"
        if len(empty_pages) > 0:
            warning_text += f" (Empty: {sorted(empty_pages)})"
        else:
            warning_text += " (INCOMPLETE)"
        title_html = f"<basefont color={colors['title']}>_______ Q U E S T S _______</basefont> <basefont color={colors['failed']}>{warning_text}</basefont>"
    else:
        title_html = f"<basefont color={colors['title']}>_______ Q U E S T S _______</basefont> <basefont color={colors['stats']}>{page_info} Pages, {quest_count} Quests</basefont>"
    
    lines.append({
        'html': title_html,
        'type': 'title',
        'quest': None
    })
    
    # Mastery Orb header (optional)
    if categories.get('mastery_orb_active') and SHOW_MASTERY_ORB_HEADER:
        lines.append({
            'html': f"<basefont color={colors['mastery_orb']}><b>* Mastery Orb Quests ({len(categories['mastery_orb_active'])})</b></basefont>",
            'type': 'header',
            'quest': None
        })
    
    # Mastery Orb Active Quests
    for quest in categories.get('mastery_orb_active', []):
        formatted_line = format_quest_line(quest['name'], quest.get('progress', ''), quest.get('difficulty_color', colors['header']))
        lines.append({
            'html': formatted_line,
            'type': 'quest',
            'quest': quest
        })
    
    # Other Active Quests
    for quest in categories.get('active', []):
        formatted_line = format_quest_line(quest['name'], quest.get('progress', ''), quest.get('difficulty_color', colors['header']))
        lines.append({
            'html': formatted_line,
            'type': 'quest',
            'quest': quest
        })
    
    # Completed Quests - display with completed color including cooldown text
    for quest in categories.get('completed', []):
        progress = quest.get('progress', '')
        # Format completed quests similar to active quests but with completed color
        if progress:
            # Use format_quest_line but override the color to completed color
            quest_name = quest['name']
            # Build line manually to ensure both name and progress are in completed color
            html = f"<basefont color={colors['completed']}>{quest_name}  {progress}</basefont>"
        else:
            html = f"<basefont color={colors['completed']}>{quest['name']}</basefont>"
        lines.append({
            'html': html,
            'type': 'completed',
            'quest': quest
        })
    
    # Available Quests
    for quest in categories.get('available', []):
        lines.append({
            'html': f"<basefont color={colors['available']}>{quest['name']}</basefont>",
            'type': 'available',
            'quest': quest
        })
    
    # Other Quests - display in completed color
    for quest in categories.get('other', []):
        progress = quest.get('progress', '')
        if progress:
            html = f"<basefont color={colors['completed']}>{quest['name']}  {progress}</basefont>"
        else:
            html = f"<basefont color={colors['completed']}>{quest['name']}</basefont>"
        lines.append({
            'html': html,
            'type': 'other',
            'quest': quest
        })
    
    return lines

def add_quest_icons(gump, quests, start_y):
    """Add objective and reward item icons to the gump for each quest.
    
    Args:
        gump: Gump object to add items to
        quests: List of quest dictionaries with objective_icon and reward_icon info
        start_y: Starting Y position for first icon
    
    Returns:
        None (modifies gump in place)
    
    Adds objective icons (what you collect/kill) in middle column,
    and reward icons at right side of gump for each quest.
    """
    objective_icon_x = DISPLAY_WIDTH - OBJECTIVE_ICON_OFFSET  # Middle position (between name and progress)
    reward_icon_x = DISPLAY_WIDTH - REWARD_ICON_OFFSET  # Right side position
    current_y = start_y
    line_height = 20  # Approximate height per quest line
    
    for quest in quests:
        # Add objective icon (what you're collecting/killing)
        objective_icon = quest.get('objective_icon')
        if objective_icon:
            item_id = objective_icon.get('item_id')
            hue = objective_icon.get('hue', 0)
            if item_id:
                Gumps.AddItem(gump, objective_icon_x, current_y, item_id, hue)
        
        # Add reward icon (what you get for completing)
        if SHOW_REWARD_ICONS:
            reward_icon = quest.get('reward_icon')
            if reward_icon:
                item_id = reward_icon.get('item_id')
                hue = reward_icon.get('hue', 0)
                if item_id:
                    Gumps.AddItem(gump, reward_icon_x, current_y, item_id, hue)
        
        current_y += line_height

def show_quest_status_gump(quest_data):
    """Display the quest status in a custom gump.
    Each quest line rendered separately with 1-pixel spacing
    """
    debug_message("Building quest status display gump", COLORS['info'])
    
    # Create gump
    gump = Gumps.CreateGump(movable=True)
    Gumps.AddPage(gump, 0)
    
    # Simple borderless background 
    Gumps.AddBackground(gump, 0, 0, DISPLAY_WIDTH, DISPLAY_HEIGHT, 30546)
    Gumps.AddAlphaRegion(gump, 0, 0, DISPLAY_WIDTH, DISPLAY_HEIGHT)
    
    # Build quest lines for individual rendering
    quest_lines = build_quest_lines(quest_data)
    
    # Render each line separately with precise Y positioning
    current_y = 10
    line_height = 21  # 20px text + 1px spacing
    quest_row_counter = 0  # Track quest rows for alternating icon offset
    
    for line_data in quest_lines:
        html_content = line_data['html']
        
        # Add black outline if enabled
        if SHOW_TEXT_OUTLINE:
            # Generate outline offsets based on thickness
            outline_offsets = []
            for thickness in range(1, TEXT_OUTLINE_THICKNESS + 1):
                # 8-directional offsets for each thickness level
                outline_offsets.extend([
                    (-thickness, 0), (thickness, 0), (0, -thickness), (0, thickness),
                    (-thickness, -thickness), (thickness, -thickness), (-thickness, thickness), (thickness, thickness)
                ])
            
            # Replace all color codes with pure black (#000000) for outline
            html_outline = re.sub(r'#[0-9A-Fa-f]{6}', '#000000', html_content)
            
            # Draw black outline at all offset positions
            for dx, dy in outline_offsets:
                Gumps.AddHtml(
                    gump,
                    10 + dx,
                    current_y + dy,
                    DISPLAY_WIDTH - 60,
                    line_height,
                    html_outline,
                    False,
                    False
                )
        
        # Draw main colored HTML on top
        Gumps.AddHtml(
            gump,
            10,
            current_y,
            DISPLAY_WIDTH - 60,  # Leave room for icons
            line_height,
            html_content,
            False,  # no background
            False   # no scrollbar
        )
        
        # Add icons for quest lines
        quest = line_data.get('quest')
        if quest and line_data['type'] == 'quest':
            # Alternate X offset by +5 or -5 pixels to prevent vertical overlap
            x_offset = 5 if (quest_row_counter % 2 == 0) else -5
            quest_row_counter += 1
            
            # Add objective icon (middle) - use OBJECTIVE_ICON_OFFSET with vertical offset
            objective_icon = quest.get('objective_icon')
            if objective_icon:
                item_id = objective_icon.get('item_id')
                hue = objective_icon.get('hue', 0)
                if item_id:
                    # Offset 5 pixels up vertically + alternating horizontal offset
                    Gumps.AddItem(gump, DISPLAY_WIDTH - OBJECTIVE_ICON_OFFSET + x_offset, current_y - 5, item_id, hue)
            
            # Add reward icon (right) - use REWARD_ICON_OFFSET
            if SHOW_REWARD_ICONS:
                reward_icon = quest.get('reward_icon')
                if reward_icon:
                    item_id = reward_icon.get('item_id')
                    hue = reward_icon.get('hue', 0)
                    if item_id:
                        Gumps.AddItem(gump, DISPLAY_WIDTH - REWARD_ICON_OFFSET, current_y, item_id, hue)
        
        current_y += line_height
    
    # Send gump (right-click to close)
    Gumps.SendGump(DISPLAY_GUMP_ID, Player.Serial, DISPLAY_X, DISPLAY_Y, gump.gumpDefinition, gump.gumpStrings)
    debug_message("Quest status gump displayed", COLORS['ok'])
    
    # Close the daily quest gump now that we've displayed results
    try:
        Gumps.CloseGump(QUEST_GUMP_ID)
        debug_message("Closed daily quest gump", COLORS['info'])
    except Exception as e:
        debug_message(f"Error closing quest gump: {e}", COLORS['warn'])

# ============================ Main ================================

def main():
    """Main entry point - crawl quests and display results."""
    try:
        # Crawl all quest pages
        quest_data = crawl_all_quest_pages()
        
        # Display results in custom gump
        show_quest_status_gump(quest_data)
        
        
    except Exception as e:
        debug_message(f"Error in main: {e}", COLORS['bad'])
        try:
            Misc.SendMessage(f"Quest Status Error: {e}", COLORS['bad'])
        except Exception:
            print(f"Quest Status Error: {e}")

if __name__ == "__main__":
    main()
