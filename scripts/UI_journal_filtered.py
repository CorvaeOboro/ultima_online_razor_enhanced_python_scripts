"""
UI Journal Filtered - a Razor Enhanced Python Script for Ultima Online

a minimal journal gump focused on locally spoken and quest events
filters command words , includes colorized speakers and events displayed persistently

using multiple filters to reduce to player and npc spoken words without "command words"
different names are colorized consistently by deterministic seed to visually separate
only "Quest" and "Event" related system messages are whitelisted 

global chat may be displayed as well , tho is turned off by default
many settings are toggleable for preference 

filters =
common command words "bank" , "All guard me" , housing
repeating messages
known npcs are filtered out

events =
events are colorized and condensed into a single line 
harvest and kill global quests , virtue shrine corruption , danger zone rotation  

TROUBLESHOOTING:
- if "import" errors , download iron python 3.4.2 and copy the files in its "Lib" folder into your RazorEnhanced "Lib" folder 

STATUS:: working
VERSION::20250909
"""

import time # timestamps and delays 
import random # jitter for desynchronize updates
import re # regex , regular expression for parsing the text

DEBUG_MODE = False

CHAT_ORDER_TOP_NEW = True  # True = newest at top; or  False = oldest at top 

SHOW_SYSTEM = True
SHOW_REGULAR = True
SHOW_PARTY = True
SHOW_GUILD = True
SHOW_ALLIANCE = True

SHOW_EMOTE = False
SHOW_LABEL = False
SHOW_FOCUS = False
SHOW_SPELL = False

SHOW_PLAYER_SELF_MESSAGES = True  # show or hide messages spoken by the local player
SHOW_OPTIONAL_NPC_ENABLED = False   # show or hide messages from optional NPC list (False = hide, replacing previous FILTER_OPTIONAL_NPC_ENABLED=True)
SHOW_MONSTER_NPC_ENABLED = False    # show or hide messages from monster NPC list (False = hide)

# System message  
SHOW_SYSTEM_QUEST_MESSAGES = True   # quest-related non-global chat System notifications
SHOW_SYSTEM_QUEST_PROGRESS = False   # quest progress lines like "Quest Progress - City Cleanup: 11/20"
SHOW_SYSTEM_WEEKLY_QUEST_MESSAGES = False  # Weekly Quest announcements (lines containing 'Weekly Quest:')
SHOW_SYSTEM_OTHER_MESSAGES = False  # other non-global System lines

# Global chat channels 
SHOW_SYSTEM_GLOBAL_MESSAGES = True  # global chat routed through System: "System <General> Player : msg"
SHOW_GLOBAL_CHAT_GENERAL = False  # System: <General> Speaker : message
SHOW_GLOBAL_CHAT_PVP = False      # System: <PVP> Speaker : message
SHOW_GLOBAL_CHAT_TRADE = False    # System: <Trade> Speaker : message

# Anti-spam  , filters hotkey spam , numeric only messages 
SHOW_NUMERIC_ONLY_MESSAGES = False   # messages that are only digits (e.g., accidental number spam)
SHOW_LONG_ALNUM_TOKENS = False       # messages that contain very long alphanumeric tokens (likely hotkey mash)
LONG_ALNUM_TOKEN_THRESHOLD = 20      # tokens longer than this (A-Za-z0-9 only, no spaces) are considered spam when SHOW_LONG_ALNUM_TOKENS is False
SHOW_PUNCT_NUM_ONLY_MESSAGES = False # messages that contain only punctuation/special characters and numbers (no letters)

SHOW_TIMESTAMP = False  # Show [HH:MM:SS] prefix; default off 
DEDUPLICATE_BY_TEXT = True # De-duplicate for simple anti spam
SHOW_ROW_DUPLICATES = False       # duplicate rows; False keeps spam suppressed 
SHOW_STATUS_EFFECT_LINES = False  # asterisk-wrapped status/emote-like lines
SHOW_BONDED_PET_LINES = False     # lines from bonded pets or lines that are only a bonded tag

"""
Offline preview settings: when enabled, reads a plain text journal file and produces an HTML preview
that simulates how this gump would render in-game after filtering.  this is for testing the colors and formatting
it is not representative of the actual gump because of the in game "channel" filtering , but lets us review how specific instances will be formatted 

not needed , you only need to change these if want to test local logs
"""
OFFLINE_JOURNAL_SIMULATE = False # setting this to true will read external journal log then exit for testing purposes .
OFFLINE_JOURNAL_INPUT_PATH = r"D:\ULTIMA\example\Data\Client\JournalLogs\2025_09_09_20_37_33_journal.txt"
OFFLINE_JOURNAL_OUTPUT_PATH = r"d:\ULTIMA\SCRIPTS\RazorEnhanced_Python\data\journal_preview.html"

#//==== GUMP ==================================================================
# example=4294967295 #  a high pseudo-random gump id to avoid other existing gump ids
GUMP_ID = 3135545776

# Default gump position and sizing
DEFAULT_GUMP_X = 200
DEFAULT_GUMP_Y = 0
DEFAULT_GUMP_WIDTH = 400
DEFAULT_GUMP_HEIGHT = 300

# TIMING
UPDATE_INTERVAL_MS = 750

# SAFETY LIMITS
MAX_HISTORY = 50           # Keep only the last N messages in memory and on-screen
MIN_RESEND_MS = 750        # throttling
ENABLE_JITTER = True # Optional jitter to desynchronize with other scripts
JITTER_MS_MAX = 100

# UI SHAPE
FILTER_PANEL_WIDTH = 115
JOURNAL_START_X = 20
JOURNAL_START_Y = 25
FILTER_SPACING_Y = 30
JOURNAL_ENTRY_HEIGHT = 20

# Chat COLORS =================================================================
CHAT_BG_DARK = True
CHAT_TEXT_COLOR = "#C0C0C0"  # light grey
QUEST_TEXT_COLOR = "#1E90FF" # Muted gold for quest lines ( other options gold = #C2A14A , teal = #76D7C4 , blue = #3FA9FF)
CHAT_BG_IMAGE_ID = None  # maybe could use 2624; # None = no image (fully transparent via alpha region only).

# Special event colors
VIRTUE_ALERT_COLOR = "#E84827"  # orange for shrine corruption/virtue attacks
DANGER_ZONE_LABEL_COLOR = "#FF3333"  # red for danger zone label

# Alert highlighting
ALERT_ATTACK_SUBSTRING = " is attacking you"
ALERT_ATTACK_COLOR = "#FF3333"

# Speaker colorization palette (bright, muted colors for readability)
PALETTE_SPEAKER_COLORS = [
    "#E6B422",  # mustard gold
    "#85C1E9",  # soft blue
    "#A3E4D7",  # mint
    "#F5B7B1",  # soft salmon
    "#D7BDE2",  # lavender
    "#F7DC6F",  # light yellow
    "#76D7C4",  # teal
    "#F8C471",  # orange tan
    "#BB8FCE",  # purple
    "#73C6B6",  # aqua
    "#F1948A",  # coral
    "#7FB3D5",  # steel blue
    "#82E0AA",  # green
    "#F0B27A",  # peach
    "#C39BD3",  # violet
]

# Optional global seed offset to bias speaker color selection (user-tunable)
COLOR_SEED_OFFSET = 0 # speaker name color is a deterministic seed based on name , use this offset if you want different colors

# VIRTUES are referenced by in world shrines where events may occur  , virtues + chaos
VIRTUES = {
    "honesty", "compassion", "valor", "justice",
    "sacrifice", "honor", "spirituality", "humility", "chaos"
}

# MASTERY_NAMES are referenced by golems in game , we use this to filter out their title messages 
# currently disabled ( not-filtered ) , as a player may actually just say the mastery name as a response 
MASTERY_NAMES = {
    "aero", "fira", "earth", "shadow", "blood", "doom", "fortune", "artisan", "bulwark", "poison", "lyric", "death", "druidic", "holy"
}

# Specific System lines to filter out entirely (case-insensitive, substring or regex)
FILTER_SYSTEM_SUBSTRINGS = [
    "[safe looting] you refuse to loot this corpse",
    "careful! you",  # e.g., "System : Careful! You ..."
    "enhanced summons",  # e.g., "System : [Enhanced Summons] ..."
    "enhanced sumons",  #  misspelling 
    "a pixie is guarding you",
]

FILTER_SYSTEM_PATTERNS = [
    # universal regex patterns here , for now we are doing specific regex patterns after routing , like for global quests
]

# Generic text filters (apply to any speaker/type) , 
# common NPC dialog , bank and vendor interactions
FILTER_GENERIC_SUBSTRINGS = [
    "you see nothing useful to carve from the corpse",
    "(summoned)",
    "the spell fizzles.","you cannot heal that.","you sense ",
    "You have accepted quest:","You have accepted the quest:",
    "bank container has ",
    "Take a look at my goods",
    "Thou hast withdrawn gold from thy account. ",
    "Thou canst not withdraw so much at one time! ",
    "There's not enough room in your bankbox",
    "the purchased items were placed in you bank box.",
    "The total of thy purchase is",
    "i am dead and cannot do that.","I can't reach that.",
    "emptying the trashcan!",
    "It appears to be locked.","The lock quickly yields to your skill.",
    "The trash is full!",
]

# exact matches , lowercase catches all , 
# mostly command words and bank interactions
FILTER_GENERIC_EXACTS = [
    "1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16","17","18","19","20",
    "all guard me", "all guard", "locked down!",
    "all kill",
    "all follow me", "all follow",
    "all stay","all come","all stop",
    "bank","claim","stable","stable all","bank claim !","bank i ban thee","claim list",
    "bank guards","bank vendor buy guards i ban thee",
    "guards open my bank","guards bank stable i ban thee",
    "vendor buy thee bank from thee guards!",
    "vendor buy thee bank from thee guards",
    "vendor buy guards bank","bank claim stable i ban thee","bank guards stable i ban thee",
    "banker bank","bank box please","i ban thee",
    "vendor buy bank guards", "bank vendor buy guards", "bank buy guards",
    "vendor buy bank","bank vendor buy","vendor buy bank i ban thee",
    "vendor buy bank guards i ban thee","vendor buy","guards","claim g", 
    "bbbb",
    "bnak","bak","ban"
    "that is secure.","Locked down!","I can't reach that.",
    "vendor buy me a bank",
    "bank guards i ban thee","vendor buy bank i ban thee",
    "bank guard room claim list i ban thee",
    "You cannot heal yourself in your current state.","you cannot heal that target in their current state.",
    "(tame)","(bonded)",
    "i wish to lock this down","i wish to release this","i wish to secure this","(no longer locked down)",
]

FILTER_GENERIC_PREFIXES = [
    "insufficient mana.",
    "into your bank box i have placed",
]

# Player bank command lines (numbers only), e.g., "withdraw 1000"
WITHDRAW_ONLY_PATTERN = re.compile(r"^\s*withdraw\s+[\d,]+\s*$", re.IGNORECASE)
DEPOSIT_ONLY_PATTERN = re.compile(r"^\s*deposit\s+[\d,]+\s*$", re.IGNORECASE)
CHECK_ONLY_PATTERN   = re.compile(r"^\s*check\s+[\d,]+\s*$", re.IGNORECASE)
BALANCE_ONLY_PATTERN = re.compile(r"^\s*balance\s*$", re.IGNORECASE)
STATEMENT_ONLY_PATTERN = re.compile(r"^\s*statement\s*$", re.IGNORECASE)

# Speaker-based filters , adjust per shard
FILTER_SPEAKER_EXACTS = [
    "canute", # quest giver , we are letting other quest givers through but the daily quest giver "Canute" spams unique messages for each quest some one takes
]

# Town NPCs , adjust per shard
FILTER_SPEAKER_OPTIONAL_NPC = [
    "ogden", # quest givers in brit bank
    "luffy", # quest givers in brit bank
    "cigal", # quest givers in brit bank
    "mariel", # thief trainer givers in brit bank
    "forsythe", #banker
]

# talkative monsters like lizardmen are filtered from local chat by default
FILTER_SPEAKER_MONSTER_NPC = [
    "a lizardman berserker","a lizardman stoneguard",  
    "a mephite lizardman", 
    "a lizardman warlock", 
    "a molten lizardman","a mephitic lizardman", "a thornscale lizardman",  "a smoke lizardman",    
    "a lizardman berserker", 
    "a lizardman", 
    "a ratman","a ratman warrior","a ratman mage",
    "a gnoll","a gnoll warrior","a gnoll mage","a gnoll defender",
    "Tsycieth","Yslish" # lizardman name
]

#//==================================================================================

def debug_message(message):
    if DEBUG_MODE:
        try:
            Misc.SendMessage("[UI_journal_filtered] " + str(message))
        except Exception:
            pass

class JournalFilterUI:
    def __init__(self):
        # Window state
        self.gump_id = GUMP_ID
        self.gump_x = DEFAULT_GUMP_X
        self.gump_y = DEFAULT_GUMP_Y
        self.resize_width = DEFAULT_GUMP_WIDTH
        self.resize_height = DEFAULT_GUMP_HEIGHT

        # Toggles 
        self.show_chat_panel = True

        # REGEX patterns to detect status effects
        # Examples: "* PlayerName begins to spasm uncontrollably *"
        #           "* You begin to spasm uncontrollably *"
        #           Other status effect style asterisks-wrapped lines
        escaped_player = re.escape(Player.Name) if hasattr(Player, 'Name') else r"Player"
        self.status_effect_patterns = [
            re.compile(r"\*\s*(?:You|%s)\s+begins?\s+to\s+spasm\s+uncontrollably\s*\*" % escaped_player, re.IGNORECASE),
            # Generic asterisk-wrapped emotes that look like status effects
            re.compile(r"^\s*\*.+\*\s*$", re.IGNORECASE),
        ]

        # REGEX pattern with named groups and explicit channel detection.
        # Handles spacing around colons, optional channel tags, and both "System" and "Systems".
        # Examples of raw journal lines (all should match):
        #   "System: <General> PlayerName : hello world"
        #   "System <Trade> Alice: selling regs"
        #   "Systems: <Help> Bob : need a rez"
        #   "System: PlayerName : local system line"
        # Captures:
        #   channel -> text inside < > if present, else None
        #   speaker -> the token before the colon (player name)
        #   message -> text after the last colon
        self.system_global_capturing_pattern = re.compile(
            r"^\s*System[s]?\s*:??\s*(?:<(?P<channel>[^>]+)>\s*)?(?P<speaker>[^:]+?)\s*:\s*(?P<message>.+)\s*$",
            re.IGNORECASE,
        )

        # Processed journal cache
        self.filtered_entries = []  # [Type, Color, Name, Serial, Text]
        self.filtered_entries_with_time = []  # [Type, Color, Name, Serial, Text, Timestamp]
        self._seen_entry_keys = set()  # to deduplicate across updates
        self._seen_text_norm = set()    # for global text-based spam suppression

        # Timing
        self.update_interval_ms = UPDATE_INTERVAL_MS

        # Scrolling state (line-based)
        self.scroll_offset_lines = 0  # how many wrapped lines from the bottom we are offset
        self.stick_to_bottom = True  # auto-follow newest lines unless user scrolls up

        # Render/processing tracking
        self._last_processed_ts = 0           # process only entries newer than this timestamp
        self._last_render_signature = None    # signature of currently rendered visible content
        self._last_gump_send_ms = 0           # last time we sent the gump to the client

        # Span cache to speed up wrapping calculations
        self._span_cache = {}
        self._span_cache_max = 2000

        # Pending state for shrine corruption -> virtue under attack combo
        self._shrine_corruption_pending_until_ms = 0

        # Pending state for Danger Zones activation -> regions list combo
        self._danger_zones_pending_until_ms = 0

        # Pending state for Global Quest name/objective combiner
        self._globalquest_name = ''
        self._globalquest_pending_until_ms = 0
        self._globalquest_last_objective = ''
        self._globalquest_last_objective_until_ms = 0

    # Basic clamp helpers to keep gump textures sane
    def _clamp_int(self, val, lo, hi, fallback):
        try:
            v = int(val)
            if v < lo:
                return lo
            if v > hi:
                return hi
            return v
        except Exception:
            return int(fallback)

    def _safe_rect(self, x, y, w, h, max_w=1200, max_h=1200):
        # Clamp width/height to avoid 0/negatives and excessively large textures
        sx = self._clamp_int(x, 0, 4096, 0)
        sy = self._clamp_int(y, 0, 4096, 0)
        sw = self._clamp_int(w, 1, int(max_w), 1)
        sh = self._clamp_int(h, 1, int(max_h), 1)
        return sx, sy, sw, sh

    #//======= Type-specific visibility hooks =====================
    # These wrappers make it easy to add type-specific remapping, tinting, or extra filters later.
    def _allow_regular(self, entry):
        return SHOW_REGULAR

    def _allow_guild(self, entry):
        # maybe colorize guild chat words
        return SHOW_GUILD

    def _allow_alliance(self, entry):
        return SHOW_ALLIANCE

    def _allow_emote(self, entry):
        return SHOW_EMOTE

    def _allow_label(self, entry):
        return SHOW_LABEL

    def _allow_focus(self, entry):
        return SHOW_FOCUS

    def _allow_spell(self, entry):
        return SHOW_SPELL

    def _allow_party(self, entry):
        # maybe colorize party chat words
        return SHOW_PARTY

    #//======= Data processing =====================
    def build_filtered_journal_entries(self):
        entries = Journal.GetJournalEntry(-1)
        # Ensure chronological order from oldest to newest
        entries = entries[::-1]
        debug_message(f" Processing {len(entries)} raw journal entries")
        new_count = 0
        max_ts_seen = self._last_processed_ts
        for entry in entries:
            # Process only new entries by timestamp when possible
            try:
                if hasattr(entry, 'Timestamp') and entry.Timestamp is not None:
                    # Allow processing when timestamp == last boundary to avoid missing multi-line events (e.g., Quest begin + objective)
                    if float(entry.Timestamp) < float(self._last_processed_ts):
                        continue
            except Exception:
                pass
            did_append, ts_candidate = self._process_entry(entry)
            if did_append:
                new_count += 1
            try:
                if ts_candidate is not None and float(ts_candidate) > float(max_ts_seen):
                    max_ts_seen = float(ts_candidate)
            except Exception:
                pass

        # Update last processed timestamp if we saw newer entries
        if max_ts_seen > self._last_processed_ts:
            self._last_processed_ts = max_ts_seen

        # Prune history and dedupe memory to the last MAX_HISTORY (live mode only)
        if not OFFLINE_JOURNAL_SIMULATE:
            try:
                if len(self.filtered_entries_with_time) > MAX_HISTORY:
                    self.filtered_entries_with_time = self.filtered_entries_with_time[-MAX_HISTORY:]
                    self.filtered_entries = [e[:5] for e in self.filtered_entries_with_time]
                    # Rebuild seen cache conservatively from the retained segment
                    self._seen_entry_keys.clear()
                    for e in self.filtered_entries_with_time:
                        try:
                            ts = e[5]
                            ser = e[3]
                            key = (ts, ser, str(e[4]))
                            self._seen_entry_keys.add(key)
                        except Exception:
                            continue
            except Exception:
                pass

        debug_message(f" Appended {new_count} entries; total filtered: {len(self.filtered_entries_with_time)}")
        return new_count

    # Core processing for a single entry. Returns (did_append: bool, ts_candidate: float|None)
    def _process_entry(self, entry):
        # Build a stable key for deduplication across updates
        try:
            key = (entry.Timestamp, int(entry.Serial), str(entry.Text))
        except Exception:
            try:
                key = (entry.Timestamp, entry.Serial, str(entry.Text))
            except Exception:
                key = (entry.Timestamp, str(entry.Text))
        if key in self._seen_entry_keys:
            return False, getattr(entry, 'Timestamp', None)

        hide_entry = False
        fixed_type = None

        # Map speaking types into Regular and gate by per-type allow hooks
        if entry.Type in ('Yell', 'Whisper', 'Regular', 'Special', 'Encoded'):
            fixed_type = 'Regular'
            if not self._allow_regular(entry):
                hide_entry = True
        elif entry.Type == 'System':
            # handled in System block below
            pass
        elif entry.Type == 'Guild':
            if not self._allow_guild(entry):
                hide_entry = True
        elif entry.Type == 'Alliance':
            if not self._allow_alliance(entry):
                hide_entry = True
        elif entry.Type == 'Emote':
            if not self._allow_emote(entry):
                hide_entry = True
        elif entry.Type == 'Label':
            if not self._allow_label(entry):
                hide_entry = True
        elif entry.Type == 'Focus':
            if not self._allow_focus(entry):
                hide_entry = True
        elif entry.Type == 'Spell':
            if not self._allow_spell(entry):
                hide_entry = True
        elif entry.Type == 'Party':
            if not self._allow_party(entry):
                hide_entry = True

        # System-specific handling: centralized routing and display policy
        if not hide_entry and entry.Type == 'System':
            try:
                route_hide, new_entry = self._handle_system_entry(entry)
                if route_hide:
                    hide_entry = True
                elif new_entry is not None:
                    entry = new_entry
            except Exception:
                pass

        # Hide player messages if disabled
        if SHOW_PLAYER_SELF_MESSAGES is False:
            try:
                if entry.Name == Player.Name:
                    hide_entry = True
            except Exception:
                pass

        # Speaker-based filtering (skip for Global chat which is routed differently)
        try:
            if not hide_entry and (entry.Type != 'Global') and entry.Name and isinstance(entry.Name, str):
                if entry.Name.strip().lower() in FILTER_SPEAKER_EXACTS:
                    hide_entry = True
                elif (not SHOW_OPTIONAL_NPC_ENABLED) and (entry.Name.strip().lower() in FILTER_SPEAKER_OPTIONAL_NPC):
                    hide_entry = True
                elif (not SHOW_MONSTER_NPC_ENABLED) and (entry.Name.strip().lower() in FILTER_SPEAKER_MONSTER_NPC):
                    hide_entry = True
        except Exception:
            pass

        # Effective flags: in offline simulation, allow duplicates so the preview shows everything
        show_row_dupes = SHOW_ROW_DUPLICATES if not OFFLINE_JOURNAL_SIMULATE else True

        # Hide duplicates (exact row) when SHOW_ROW_DUPLICATES is False (suppress spam)
        base_row = [entry.Type, entry.Color, entry.Name, entry.Serial, entry.Text]
        if (not show_row_dupes) and (base_row in self.filtered_entries):
            hide_entry = True

        # Hide bonded pets (by name suffix) when SHOW_BONDED_PET_LINES is False (skip for Global)
        try:
            if SHOW_BONDED_PET_LINES is False and entry.Type != 'Global':
                if entry.Name and isinstance(entry.Name, str):
                    lname = entry.Name.lower()
                    if ('{bonded}' in lname) or ('[bonded]' in lname) or ('(bonded)' in lname):
                        hide_entry = True
        except Exception:
            pass

        # Hide status effects when SHOW_STATUS_EFFECT_LINES is False (pattern-based) (skip for Global)
        try:
            if SHOW_STATUS_EFFECT_LINES is False and entry.Type != 'Global':
                text = entry.Text if isinstance(entry.Text, str) else str(entry.Text)
                if self._is_status_effect_line(text):
                    hide_entry = True
        except Exception:
            pass

        # Hide bonded-only text when SHOW_BONDED_PET_LINES is False (skip for Global)
        try:
            if SHOW_BONDED_PET_LINES is False and entry.Type != 'Global':
                text = entry.Text if isinstance(entry.Text, str) else str(entry.Text)
                if self._is_bonded_only_text(text):
                    hide_entry = True
        except Exception:
            pass

        # Generic content filters regardless of speaker/type
        try:
            # Apply numeric-only, long-token, and punct+num anti-spam universally (includes Global)
            try:
                text_raw = str(entry.Text)
            except Exception:
                text_raw = ''
            if (not SHOW_NUMERIC_ONLY_MESSAGES) and self._is_numeric_only_message(text_raw):
                hide_entry = True
            if (not hide_entry) and (not SHOW_LONG_ALNUM_TOKENS) and self._has_long_alnum_token(text_raw):
                hide_entry = True
            if (not hide_entry) and (not SHOW_PUNCT_NUM_ONLY_MESSAGES) and self._is_punct_num_only_message(text_raw):
                hide_entry = True

            # Apply the rest only to non-Global
            if (not hide_entry) and entry.Type != 'Global':
                low = (entry.Text if isinstance(entry.Text, str) else str(entry.Text)).strip().lower()
                for sub in FILTER_GENERIC_SUBSTRINGS:
                    if str(sub).strip().lower() in low:
                        hide_entry = True
                        break
                if not hide_entry and low in FILTER_GENERIC_EXACTS:
                    hide_entry = True
                if not hide_entry:
                    for pre in FILTER_GENERIC_PREFIXES:
                        if low.startswith(str(pre).strip().lower()):
                            hide_entry = True
                            break
            # Filter pure withdraw commands like "withdraw 5,000" (non-Global)
            if not hide_entry and entry.Type != 'Global':
                try:
                    text_raw2 = str(entry.Text)
                    if (
                        WITHDRAW_ONLY_PATTERN.match(text_raw2)
                        or DEPOSIT_ONLY_PATTERN.match(text_raw2)
                        or CHECK_ONLY_PATTERN.match(text_raw2)
                        or BALANCE_ONLY_PATTERN.match(text_raw2)
                        or STATEMENT_ONLY_PATTERN.match(text_raw2)
                    ):
                        hide_entry = True
                except Exception:
                    pass
        except Exception:
            pass

        # Hide empty
        try:
            if len(str(entry.Text).strip()) == 0:
                hide_entry = True
        except Exception:
            hide_entry = True

        did_append = False
        if not hide_entry:
            row_type = fixed_type if fixed_type is not None else entry.Type
            row = [row_type, entry.Color, entry.Name, entry.Serial, entry.Text]
            row_with_time = row + [entry.Timestamp]
            # Global text-based dedupe
            try:
                text_val = entry.Text if isinstance(entry.Text, str) else str(entry.Text)
                text_norm = ' '.join(text_val.split()).strip().lower()
            except Exception:
                text_norm = None
            # Effective text-dedupe: disabled in offline simulation to keep full history in preview
            # and ALWAYS bypassed for Quest entries so repeated Quest lines are not suppressed.
            dedupe_by_text = DEDUPLICATE_BY_TEXT if not OFFLINE_JOURNAL_SIMULATE else False
            if (row_type == 'Quest'):
                # Always append Quest entries (no text-based dedupe suppression)
                self.filtered_entries.append(row)
                self.filtered_entries_with_time.append(row_with_time)
                did_append = True
            else:
                if dedupe_by_text and text_norm:
                    if text_norm not in self._seen_text_norm:
                        self._seen_text_norm.add(text_norm)
                        self.filtered_entries.append(row)
                        self.filtered_entries_with_time.append(row_with_time)
                        did_append = True
                else:
                    self.filtered_entries.append(row)
                    self.filtered_entries_with_time.append(row_with_time)
                    did_append = True

        # mark as seen regardless so we don't reprocess on the next tick
        try:
            self._seen_entry_keys.add(key)
        except Exception:
            pass

        return did_append, getattr(entry, 'Timestamp', None)

    def _is_status_effect_line(self, text):
        try:
            for pat in self.status_effect_patterns:
                if pat.search(text):
                    return True
        except Exception:
            pass
        return False

    # Convert deprecated <BASEFONT COLOR> tags to browser-friendly <span style="color:"> for the offline preview
    def _html_for_browser(self, html_text):
        try:
            s = str(html_text)
            # Replace opening BASEFONT with span style
            s = re.sub(r"<\s*BASEFONT\s+COLOR=\"([^\"]+)\"\s*>", r"<span style=\"color: \1\">", s, flags=re.IGNORECASE)
            # Replace closing BASEFONT with </span>
            s = re.sub(r"<\s*/\s*BASEFONT\s*>", "</span>", s, flags=re.IGNORECASE)
            # If an outer span with chat color wraps the whole line and inner spans exist, drop the outer wrapper
            m = re.match(r"^\s*<span\s+style=\"color:\s*([^\"]+)\">(.*)</span>\s*$", s, flags=re.IGNORECASE|re.DOTALL)
            if m:
                outer_color = m.group(1).strip()
                inner = m.group(2)
                if outer_color.lower() == str(CHAT_TEXT_COLOR).lower() and re.search(r"<span\s+style=\"color:", inner, flags=re.IGNORECASE):
                    # Let the container provide the chat color; keep inner colored spans intact
                    s = inner
            # Unescape any stray backslash-escaped quotes that may prevent style parsing in some viewers
            s = s.replace('\\"', '"').replace("\\'", "'")
            return s
        except Exception:
            return html_text

    # Remove simple HTML color tags from a string to produce a plain-text version for span calculation
    def _strip_html_tags(self, text):
        try:
            s = str(text)
            # Remove BASEFONT tags
            s = re.sub(r"<\s*BASEFONT\s+COLOR=\"[^\"]+\"\s*>", "", s, flags=re.IGNORECASE)
            s = re.sub(r"<\s*/\s*BASEFONT\s*>", "", s, flags=re.IGNORECASE)
            # Remove span color tags
            s = re.sub(r"<\s*span\s+style=\"color:\s*[^\"]+\"\s*>", "", s, flags=re.IGNORECASE)
            s = re.sub(r"<\s*/\s*span\s*>", "", s, flags=re.IGNORECASE)
            # Collapse excess whitespace
            s = re.sub(r"\s+", " ", s).strip()
            return s
        except Exception:
            return text

    # Remove leading timestamp like "[09/08/2025 22 : 09:18]" (with optional spaces and NBSP) from a raw log line
    def _strip_leading_timestamp(self, line):
        try:
            s = str(line)
            # Normalize non-breaking/zero-width spaces that often appear in exported logs
            s = s.replace('\u00A0', ' ').replace('\xa0', ' ').replace('\u200b', '')
            # Pattern: [MM/DD/YYYY HH : MM(:SS)?] with variable spacing and optional seconds
            s = re.sub(r"^\s*\[\s*\d{2}/\d{2}/\d{4}\s+\d{1,2}\s*:\s*\d{2}(?:\s*:\s*\d{2})?\s*\]\s*", "", s)
            return s
        except Exception:
            return line

    # Offline: simulate rendering from a text log file and write an HTML preview
    # Expected input lines examples:
    #   System: <Trade> Bokagsea : Book of Lost Knowledge
    #   System: The following regions are now DANGER ZONES: Stygian Keep, Minoc
    #   Alice : hello there
    #   Bob: missing space but still handled
    #   [emote] * You begin to spasm uncontrollably *
    def simulate_from_text_file(self, input_path, output_path):
        try:
            # Try UTF-8 first
            with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            # If content appears to be UTF-16 (embedded nulls), reopen with utf-16-le
            if '\x00' in content:
                with open(input_path, 'r', encoding='utf-16-le', errors='ignore') as f2:
                    content = f2.read()
            lines = content.splitlines()
        except Exception as e:
            try:
                # Fallback: direct utf-16-le
                with open(input_path, 'r', encoding='utf-16-le', errors='ignore') as f3:
                    lines = f3.read().splitlines()
            except Exception as e2:
                debug_message(f"Offline simulate: cannot read file: {e} / {e2}")
                return

        # Reset internal state for a clean run
        self.filtered_entries = []
        self.filtered_entries_with_time = []
        self._seen_entry_keys = set()
        self._seen_text_norm = set()

        ts = 1.0
        appended = 0
        sys_count = 0
        reg_count = 0
        for raw in lines:
            s = str(raw).rstrip('\n')
            # Normalize and strip any leading timestamp prefix from exported journal logs
            s = self._strip_leading_timestamp(s)
            if not s:
                continue
            # Build a minimal entry-like object
            etype = 'Regular'
            name = ''
            text = s
            # Heuristic: System lines
            if s.strip().lower().startswith('system'):
                etype = 'System'
                sys_count += 1
            else:
                # Try to split "Name : message" variants
                if ' : ' in s:
                    parts = s.split(' : ', 1)
                    name = parts[0].strip()
                    text = parts[1]
                elif ':' in s:
                    parts = s.split(':', 1)
                    # avoid time-like prefixes by preferring short names
                    if len(parts[0].strip()) <= 24:
                        name = parts[0].strip()
                        text = parts[1]
                reg_count += 1

            entry = type('E', (), dict(Type=etype,
                                       Color=CHAT_TEXT_COLOR,
                                       Name=name,
                                       Serial=0,
                                       Text=text,
                                       Timestamp=ts))
            ts += 1.0
            did_append, _ = self._process_entry(entry)
            if did_append:
                appended += 1

        # Write HTML preview using the same HTML snippets as gump
        try:
            out_lines = []
            out_lines.append("<!doctype html>")
            out_lines.append("<html><head><meta charset='utf-8'><meta http-equiv='X-UA-Compatible' content='IE=edge'><title>Journal Preview</title></head><body>")
            out_lines.append("<div style='font-family: Verdana, Arial, sans-serif; font-size: 12px; background:#111; padding:10px; width:700px;'>")
            out_lines.append("<div style='color:#888; margin-bottom:8px;'>______ JOURNAL PREVIEW ______</div>")
            out_lines.append(f"<div style='color:#888; margin-bottom:8px;'>Parsed: System={sys_count} Regular-like={reg_count} Appended={appended}</div>")
            for e in self.filtered_entries_with_time:
                html_text, plain_text = self._build_entry_texts(e)
                out_lines.append(f"<div style='margin:2px 0;'>{self._html_for_browser(html_text)}</div>")
            out_lines.append("</div></body></html>")
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(out_lines))
            debug_message(f"Offline simulate: wrote {appended} entries to {output_path}")
        except Exception as e:
            debug_message(f"Offline simulate: write error {e}")


    # True if the entire text (after trimming) is just digits
    def _is_numeric_only_message(self, text):
        try:
            s = str(text).strip()
            return True if re.match(r"^\d+$", s) else False
        except Exception:
            return False

    # True if any token has only A-Za-z0-9 and length > threshold
    def _has_long_alnum_token(self, text, threshold=None):
        try:
            s = str(text)
            th = int(threshold) if threshold is not None else int(LONG_ALNUM_TOKEN_THRESHOLD)
            # Split on whitespace and punctuation, preserve alnum chunks
            tokens = re.findall(r"[A-Za-z0-9]+", s)
            for t in tokens:
                if len(t) > th:
                    return True
        except Exception:
            pass
        return False

    # True if, after removing whitespace, the string has no letters A-Za-z
    # and contains at least one non-space character (i.e., only digits and punctuation/specials)
    def _is_punct_num_only_message(self, text):
        try:
            s = str(text)
            s_compact = re.sub(r"\s+", "", s)
            if len(s_compact) == 0:
                return False
            return re.search(r"[A-Za-z]", s_compact) is None
        except Exception:
            return False

    # Normalize Global Quest objective text by removing trailing qualifiers like 'worldwide'/'globally'
    # and collapsing redundant whitespace/punctuation. Examples:
    #  - "Kill 350 Dragons worldwide" -> "Kill 350 Dragons"
    #  - "Harvest 5000 Logs" -> unchanged
    def _normalize_globalquest_objective(self, obj_text):
        try:
            s = str(obj_text).strip()
            # Remove trailing qualifiers commonly seen in objectives
            s = re.sub(r"\s*(?:world\s*wide|worldwide|globally|across\s+the\s+realm|across\s+britannia)\s*$",
                       "", s, flags=re.IGNORECASE)
            # Compact internal whitespace
            s = re.sub(r"\s+", " ", s).strip()
            # If pattern is Kill/Harvest N Thing(s), keep it as-is after trimming
            m_kill = re.match(r"^Kill\s+(\d+)\s+(.+)$", s, re.IGNORECASE)
            if m_kill:
                n = m_kill.group(1)
                thing = m_kill.group(2).strip()
                return f"Kill {n} {thing}"
            m_harv = re.match(r"^Harvest\s+(\d+)\s+(.+)$", s, re.IGNORECASE)
            if m_harv:
                n = m_harv.group(1)
                thing = m_harv.group(2).strip()
                return f"Harvest {n} {thing}"
            return s
        except Exception:
            return obj_text

    # Decide if a non-global System line should be considered a quest notification
    def _is_quest_system_text(self, s_lower):
        try:
            if s_lower is None:
                return False
            # Keywords and shard events that we always allow as quest-like
            if ('danger zone' in s_lower) or ('hellfire' in s_lower):
                return True
            virtue_alert = any(v in s_lower for v in VIRTUES) and ('attack' in s_lower)
            if virtue_alert:
                return True
            # Use word boundaries so 'question' does not count as 'quest'
            if re.search(r"\bquests?\b", s_lower, re.IGNORECASE):
                return True
        except Exception:
            pass
        return False

    # Route one System journal entry according to SHOW_SYSTEM_* flags.
    # Returns (hide: bool, new_entry: entry-like object or None)
    #
    # Examples from raw log and expected classification:
    # - "System: <General> Playername : speaking in general chat"
    #     => Global (channel present), show if SHOW_SYSTEM_GLOBAL_MESSAGES is True; 
    # - "System: <Trade> Alice : WTS Valorite Ingots"
    #     => Global, show/hide per SHOW_SYSTEM_GLOBAL_MESSAGES.
    # - "System: Spirituality is currently under attack!"
    #     => Non-global Quest (virtue alert), show per SHOW_SYSTEM_QUEST_MESSAGES.
    # - "System: You have accepted quest: The Lost Map"
    #     => Non-global Quest (contains word 'quest'), show per SHOW_SYSTEM_QUEST_MESSAGES.
    # - "System: The trash is full!"
    #     => Non-global Other; hidden unless SHOW_SYSTEM_OTHER_MESSAGES is True (and may also be filtered earlier by generic filters).
    def _handle_system_entry(self, entry):
        try:
            txt = entry.Text if isinstance(entry.Text, str) else str(entry.Text)
            s = str(txt)
            low = s.lower()
            # Check for Global format first
            m = self.system_global_capturing_pattern.match(s)
            if m:
                # Only treat as Global if a channel like <General>/<Trade>/<PVP> is present
                try:
                    channel = (m.group('channel') or '').strip()
                except Exception:
                    channel = ''
                if channel:
                    if not SHOW_SYSTEM_GLOBAL_MESSAGES:
                        if DEBUG_MODE:
                            debug_message(f"Global suppressed by toggle: channel={channel}, speaker={m.group('speaker')}, msg={m.group('message')[:60] if m.group('message') else ''}")
                        return True, None
                    speaker = (m.group('speaker') or '').strip()
                    # Enforce per-channel visibility
                    ch_low = channel.lower()
                    if ch_low == 'general' and not SHOW_GLOBAL_CHAT_GENERAL:
                        return True, None
                    if ch_low == 'pvp' and not SHOW_GLOBAL_CHAT_PVP:
                        return True, None
                    if ch_low == 'trade' and not SHOW_GLOBAL_CHAT_TRADE:
                        return True, None
                    message = (m.group('message') or '').strip()
                    fixed_type = 'Global'
                    new_entry = type('E', (), dict(Type=fixed_type,
                                                   Color=entry.Color,
                                                   Name=speaker or entry.Name,
                                                   Serial=entry.Serial,
                                                   Text=message,
                                                   Timestamp=entry.Timestamp))
                    if DEBUG_MODE:
                        debug_message(f"Classified Global: channel={channel}, speaker={speaker}, msg={message[:80]}")
                    return False, new_entry
                # If no channel, fall through to non-global handling (Quest/Danger/etc.)
            # Non-global: specialized handling first (DANGER ZONES, Virtue Shrine events), then generic quest/other
            now_ms = int(time.time() * 1000)
            # Detect and hold the shrine corruption marker
            try:
                cleaned_marker = re.sub(r"^\s*System\s*:?:?\s*", "", s, flags=re.IGNORECASE).strip()
            except Exception:
                cleaned_marker = s.strip()

            # Weekly Quest announcements filter (non-global System lines that contain "Weekly Quest:")
            try:
                if (not SHOW_SYSTEM_WEEKLY_QUEST_MESSAGES) and re.search(r"\bweekly\s+quest\s*:\s*", cleaned_marker, re.IGNORECASE):
                    return True, None
            except Exception:
                pass

            # Fallback Global routing: if the cleaned text still looks like '<Channel> Speaker : Message', treat as Global
            try:
                ch_m = re.match(r"^\s*<\s*(?P<channel>[^>]+)\s*>\s*(?P<speaker>[^:<>]+?)\s*:\s*(?P<message>.+)$", cleaned_marker)
                if ch_m:
                    if not SHOW_SYSTEM_GLOBAL_MESSAGES:
                        return True, None
                    speaker = (ch_m.group('speaker') or '').strip()
                    channel = (ch_m.group('channel') or '').strip()
                    ch_low = channel.lower()
                    if ch_low == 'general' and not SHOW_GLOBAL_CHAT_GENERAL:
                        return True, None
                    if ch_low == 'pvp' and not SHOW_GLOBAL_CHAT_PVP:
                        return True, None
                    if ch_low == 'trade' and not SHOW_GLOBAL_CHAT_TRADE:
                        return True, None
                    message = (ch_m.group('message') or '').strip()
                    fixed_type = 'Global'
                    new_entry = type('E', (), dict(Type=fixed_type,
                                                   Color=entry.Color,
                                                   Name=speaker or entry.Name,
                                                   Serial=entry.Serial,
                                                   Text=message,
                                                   Timestamp=entry.Timestamp))
                    if DEBUG_MODE:
                        debug_message(f"Fallback Classified Global: channel={channel}, speaker={speaker}, msg={message[:80]}")
                    return False, new_entry
            except Exception:
                pass

            # Global Quest combiner: begin line + objective line to a single Quest message
            #
            # Expected inputs (non-channel System lines):
            #   System: A new global quest has begun: Lumber Crisis!
            #   System: Objective: Harvest 5000 Logs (Target: 5000)
            #   System: Say [globalquest to view details!
            # -> Output: [QUEST] Lumber Crisis! Harvest 5000 Logs
            #
            #   System: A new global quest has begun: Dragon Threat!
            #   System: Objective: Kill 350 Dragons worldwide (Target: 350)
            #   System: Say [globalquest to view details!
            # -> Output: [QUEST] Dragon Threat! Kill 350 Dragons
            #
            #   System: A new global quest has begun: Shame Purification!
            #   System: Objective: Kill 300 monsters in Shame (Target: 300)
            #   System: Say [globalquest to view details!
            # -> Output: [QUEST] Shame Purification! Kill 300 monsters in Shame
            #
            # Notes:
            # - We intentionally ignore the "Say [globalquest ..." helper line.
            # - Objective parser ignores the "(Target: NNN)" suffix and trims qualifiers like "worldwide/globally".
            # - Pending window must span both lines; prefer >= 6000 ms if timestamps may differ.
            try:
                # Examples: "A new global quest has begun: Lumber Crisis!"
                # Allow optional trailing punctuation variations and spacing
                begin_m = re.match(r"^\s*A\s+new\s+global\s+quest\s+has\s+begun\s*:\s*(?P<name>.+?)\s*[!\.]?\s*$", cleaned_marker, re.IGNORECASE)
                if begin_m:
                    # Hold quest name for a short time to await objective line
                    self._globalquest_name = (begin_m.group('name') or '').strip()
                    self._globalquest_pending_until_ms = now_ms + 3000
                    if DEBUG_MODE:
                        debug_message(f"Quest begin: name='{self._globalquest_name}' pending 3s")
                    # If we previously saw an objective first and it's still fresh, combine immediately
                    try:
                        if getattr(self, '_globalquest_last_objective_until_ms', 0) > now_ms and getattr(self, '_globalquest_last_objective', '').strip():
                            objective = self._normalize_globalquest_objective(self._globalquest_last_objective)
                            # Clear stored objective state and pending window
                            self._globalquest_last_objective = ''
                            self._globalquest_last_objective_until_ms = 0
                            self._globalquest_pending_until_ms = 0
                            quest_name = self._globalquest_name
                            self._globalquest_name = ''
                            if not SHOW_SYSTEM_QUEST_MESSAGES:
                                return True, None
                            combined_name = quest_name if quest_name.endswith('!') else f"{quest_name}!"
                            combined = f"{combined_name} {objective}"
                            fixed_type = 'Quest'
                            new_entry = type('E', (), dict(Type=fixed_type,
                                                           Color=entry.Color,
                                                           Name='[QUEST]',
                                                           Serial=entry.Serial,
                                                           Text=combined,
                                                           Timestamp=entry.Timestamp))
                            return False, new_entry
                    except Exception:
                        pass
                    return True, None  # hide the begin line itself
                # Examples: "Objective: Harvest 5000 Logs (Target: 5000)"
                obj_m = re.match(r"^\s*Objective\s*:\s*(?P<obj>.+?)(?:\s*\(\s*Target\s*:\s*[^\)]*\))?\s*$", cleaned_marker, re.IGNORECASE)
                if obj_m and getattr(self, '_globalquest_pending_until_ms', 0) > now_ms:
                    quest_name = getattr(self, '_globalquest_name', '').strip()
                    # Clear pending state
                    self._globalquest_pending_until_ms = 0
                    self._globalquest_name = ''
                    if quest_name:
                        if not SHOW_SYSTEM_QUEST_MESSAGES:
                            return True, None
                        objective = (obj_m.group('obj') or '').strip()
                        objective = self._normalize_globalquest_objective(objective)
                        # Ensure single trailing '!' after name and a single space before objective
                        combined_name = quest_name if quest_name.endswith('!') else f"{quest_name}!"
                        combined = f"{combined_name} {objective}"
                        fixed_type = 'Quest'
                        new_entry = type('E', (), dict(Type=fixed_type,
                                                       Color=entry.Color,
                                                       Name='[QUEST]',
                                                       Serial=entry.Serial,
                                                       Text=combined,
                                                       Timestamp=entry.Timestamp))
                        return False, new_entry
                # Defensive: if Objective appears before Begin (rare), hold it briefly and try to pair
                if obj_m and getattr(self, '_globalquest_pending_until_ms', 0) <= now_ms:
                    self._globalquest_last_objective = (obj_m.group('obj') or '').strip()
                    self._globalquest_last_objective_until_ms = now_ms + 3000
                    if DEBUG_MODE:
                        debug_message("Quest objective seen before begin; holding for 3s")
                    return True, None
            except Exception:
                pass

            # DANGER ZONES handling
            # Accept variations like: [DANGER ZONES ACTIVATED], [Danger Zones Active], etc.
            if re.match(r"^\s*\[\s*danger\s+zone[s]?\s+activ\w*\s*\]\s*$", cleaned_marker, re.IGNORECASE):
                # arm a short pending window to catch the next regions list line
                self._danger_zones_pending_until_ms = now_ms + 2000
                return True, None  # hide the marker itself
            # Unconditional combined list handling: convert directly to Danger entry regardless of pending state
            dz_list_match = re.match(r"^\s*the\s+following\s+regions\s+are\s+now\s+danger\s+zone[s]?\s*:\s*(?P<list>.+)\s*$", cleaned_marker, re.IGNORECASE)
            if dz_list_match:
                regions_raw = dz_list_match.group('list') or ''
                regions = [r.strip() for r in regions_raw.split(',') if r.strip()]
                colored = self._colorize_regions(regions)
                fixed_type = 'Danger'
                new_entry = type('E', (), dict(Type=fixed_type,
                                               Color=entry.Color,
                                               Name='[DANGER ZONE]',
                                               Serial=entry.Serial,
                                               Text=colored,
                                               Timestamp=entry.Timestamp))
                return False, new_entry
            # Fallback: if the line contains 'danger zone' and a colon-separated list, classify as Danger even without prior marker
            low_clean = cleaned_marker.lower()
            if ('danger zone' in low_clean) and (':' in cleaned_marker):
                try:
                    list_part = cleaned_marker.split(':', 1)[1]
                except Exception:
                    list_part = ''
                regions = [r.strip() for r in list_part.split(',') if r.strip()]
                if regions:
                    colored = self._colorize_regions(regions)
                    fixed_type = 'Danger'
                    new_entry = type('E', (), dict(Type=fixed_type,
                                                   Color=entry.Color,
                                                   Name='[DANGER ZONE]',
                                                   Serial=entry.Serial,
                                                   Text=colored,
                                                   Timestamp=entry.Timestamp))
                    return False, new_entry
            if re.match(r"^\s*\[\s*shrine\s+corruption\s*\]\s*$", cleaned_marker, re.IGNORECASE):
                # Hold for a short window so we can coalesce the next virtue attack line
                self._shrine_corruption_pending_until_ms = now_ms + 2000
                return True, None  # hide the marker itself

            # Hide Quest Progress lines if disabled
            try:
                if not SHOW_SYSTEM_QUEST_PROGRESS:
                    # Hide any variant that includes 'Quest Progress:' (e.g., 'Global Quest Progress: ...')
                    if re.search(r"\bquest\s+progress\s*:\s*", cleaned_marker, re.IGNORECASE):
                        return True, None
                    # Backward compatibility: also hide lines that start with 'Quest Progress' even without a colon
                    if re.match(r"^\s*quest\s+progress\b", cleaned_marker, re.IGNORECASE):
                        return True, None
            except Exception:
                pass

            # Virtue under attack line
            shrine_match = re.match(r"^\s*(?P<virtue>\w+)\s+is\s+currently\s+under\s+attack!\s*$", cleaned_marker, re.IGNORECASE)
            if shrine_match and (shrine_match.group('virtue') or '').strip().lower() in VIRTUES:
                virtue = shrine_match.group('virtue').strip()
                # If we recently saw the corruption marker, coalesce to a single shrine entry
                if now_ms < self._shrine_corruption_pending_until_ms:
                    self._shrine_corruption_pending_until_ms = 0
                # Show shrine alert as a unified entry regardless of pending marker
                fixed_type = 'Shrine'
                new_entry = type('E', (), dict(Type=fixed_type,
                                               Color=entry.Color,
                                               Name='[VIRTUE SHRINE]',
                                               Serial=entry.Serial,
                                               Text=f"{virtue} is under attack!",
                                               Timestamp=entry.Timestamp))
                return False, new_entry

            # Generic classification: quest vs other (ensure Danger preference)
            # If a line mentions danger zone(s), prefer Danger handling above; do not treat as Quest here.
            if 'danger zone' in low:
                return True, None  # already handled or will be ignored if unmatched
            is_quest = self._is_quest_system_text(low)
            try:
                cleaned = re.sub(r"^\s*System\s*:?:?\s*", "", s, flags=re.IGNORECASE).strip()
            except Exception:
                cleaned = s.strip()
            if is_quest:
                if not SHOW_SYSTEM_QUEST_MESSAGES:
                    return True, None
                fixed_type = 'Quest'
                new_entry = type('E', (), dict(Type=fixed_type,
                                               Color=entry.Color,
                                               Name='[QUEST]',
                                               Serial=entry.Serial,
                                               Text=cleaned,
                                               Timestamp=entry.Timestamp))
                return False, new_entry
            else:
                if not SHOW_SYSTEM_OTHER_MESSAGES:
                    return True, None
                fixed_type = 'System'
                new_entry = type('E', (), dict(Type=fixed_type,
                                               Color=entry.Color,
                                               Name='[SYSTEM]',
                                               Serial=entry.Serial,
                                               Text=cleaned,
                                               Timestamp=entry.Timestamp))
                return False, new_entry
        except Exception:
            return False, None

    # Colorize a list of region names with known colors or deterministic fallback
    def _colorize_regions(self, regions):
        try:
            out_parts = []
            for name in regions:
                color = self._color_for_region(name)
                safe = str(name)
                out_parts.append(f"<BASEFONT COLOR=\"{color}\">{safe}</BASEFONT>")
            return " , ".join(out_parts)
        except Exception:
            try:
                return " , ".join([str(x) for x in regions])
            except Exception:
                return ""

    def _color_for_region(self, name):
        # Known location colors; keys are lowercase
        KNOWN_LOCATION_COLORS = {
            'minoc': '#85C1E9',        # soft blue
            'stygian keep': '#C39BD3', # violet
            'deceit': '#BB8FCE',       # purple
            'eventide': '#76D7C4',     # teal
            'shadowkin camp': '#7FB3D5',
            'britain': '#F8C471',
            'yew': '#82E0AA',
            'vesper': '#73C6B6',
            'skara brae': '#F0B27A',
            'trinsic': '#F1948A',
        }
        try:
            key = (name or '').strip().lower()
            if key in KNOWN_LOCATION_COLORS:
                return KNOWN_LOCATION_COLORS[key]
            # Deterministic fallback using speaker color palette hash
            # Reuse the same FNV-1a approach to pick a readable color from PALETTE_GOOD_COLORS
            h = 0x811C9DC5
            for ch in key:
                h ^= ord(ch)
                h = (h * 0x01000193) & 0xFFFFFFFF
            idx = (h + int(COLOR_SEED_OFFSET)) % len(PALETTE_SPEAKER_COLORS)
            return PALETTE_SPEAKER_COLORS[idx]
        except Exception:
            return CHAT_TEXT_COLOR


    # Detect messages that are only a bonded tag like "[bonded]", "{bonded}", or even "{bonded)"
    def _is_bonded_only_text(self, text):
        try:
            if text is None:
                return False
            s = str(text).strip().lower()
            # Regex: optional single leading bracket/brace/paren, then bonded, then optional single trailing counterpart
            # Allows minor mismatches like {bonded) as requested
            if re.match(r"^\s*[\[\{\(]?\s*bonded\s*[\]\}\)]?\s*$", s, re.IGNORECASE):
                return True
        except Exception:
            pass
        return False

    # Deterministic color for a given speaker name using the preset palette
    def _color_for_speaker(self, name):
        try:
            if not name:
                return CHAT_TEXT_COLOR
            key = name.strip().lower()
            # FNV-1a 32-bit hash for deterministic index without hashlib
            h = 0x811C9DC5
            for ch in key:
                h ^= ord(ch)
                h = (h * 0x01000193) & 0xFFFFFFFF
            idx = (h + int(COLOR_SEED_OFFSET)) % len(PALETTE_SPEAKER_COLORS)
            return PALETTE_SPEAKER_COLORS[idx]
        except Exception:
            return CHAT_TEXT_COLOR

    #//======= UI drawing =====================
    def draw_gump(self):
        # Compute the lines to render and a signature for change detection
        # Compute paging using wrapped line spans
        usable_height = max(0, self.resize_height - JOURNAL_START_Y - JOURNAL_ENTRY_HEIGHT)
        available_lines = max(1, usable_height // JOURNAL_ENTRY_HEIGHT)

        # Auto-stick to bottom unless user scrolled up
        if self.stick_to_bottom:
            self.scroll_offset_lines = 0

        # Determine visible window from bottom using scroll_offset_lines
        start_line_from_bottom = self.scroll_offset_lines
        end_line_from_bottom = self.scroll_offset_lines + available_lines

        # Collect just enough entries backwards to fill the window
        selected = []  # (index, span, html, plain)
        acc = 0
        width = self.resize_width - 25
        for idx in range(len(self.filtered_entries_with_time) - 1, -1, -1):
            entry = self.filtered_entries_with_time[idx]
            html_text, plain_text = self._build_entry_texts(entry)
            span = self._get_span_for_entry(entry, plain_text, width)
            next_acc = acc + span
            if next_acc > start_line_from_bottom:
                selected.append((idx, span, html_text, plain_text))
            acc = next_acc
            if acc >= end_line_from_bottom:
                break
        if not CHAT_ORDER_TOP_NEW:
            selected.reverse()

        # Build a signature of visible content
        try:
            visible_plain = tuple(p for (_, _, _, p) in selected)
        except Exception:
            visible_plain = tuple()

        now_ms = int(time.time() * 1000)
        if (
            self._last_render_signature is not None
            and visible_plain == self._last_render_signature
            and (now_ms - self._last_gump_send_ms) < MIN_RESEND_MS
        ):
            # No change and resend window not elapsed; skip sending
            return

        # Proceed to build and send the gump
        gump_data = Gumps.CreateGump(True, True, False, False)
        Gumps.AddPage(gump_data, 0)

        if self.show_chat_panel:
            total_render_lines = sum(span for _, span, _, _ in selected)
            total_render_height = (total_render_lines * JOURNAL_ENTRY_HEIGHT) + JOURNAL_ENTRY_HEIGHT

            bg_x, bg_y, bg_w, bg_h = self._safe_rect(JOURNAL_START_X,
                                                     JOURNAL_START_Y,
                                                     self.resize_width - 25,
                                                     max(JOURNAL_ENTRY_HEIGHT, total_render_height))
            if CHAT_BG_DARK:
                try:
                    Gumps.AddAlphaRegion(gump_data, bg_x, bg_y, bg_w, bg_h)
                except Exception:
                    pass
            if CHAT_BG_IMAGE_ID is not None:
                try:
                    Gumps.AddImageTiled(gump_data, bg_x, bg_y, bg_w, bg_h, int(CHAT_BG_IMAGE_ID))
                except Exception:
                    pass

            title_html = "<BASEFONT COLOR=\"#333333\">     ________  L O C A L  C H A T  ________</BASEFONT>"
            tx, ty, tw, th = self._safe_rect(JOURNAL_START_X + 4, JOURNAL_START_Y + 2, self.resize_width - 35, JOURNAL_ENTRY_HEIGHT)
            Gumps.AddHtml(gump_data, tx, ty, tw, th, title_html, False, False)

            current_y = JOURNAL_START_Y + JOURNAL_ENTRY_HEIGHT
            for _, span, html_text, _ in selected:
                height_px = span * JOURNAL_ENTRY_HEIGHT
                rx, ry, rw, rh = self._safe_rect(JOURNAL_START_X, current_y, self.resize_width - 25, height_px)
                Gumps.AddHtml(gump_data, rx, ry, rw, rh, html_text, False, False)
                current_y += height_px
        else:
            Gumps.AddLabel(gump_data, 130, 0, 0, "Chat Hidden")

        try:
            Gumps.CloseGump(self.gump_id)
            Gumps.SendGump(self.gump_id, Player.Serial, 0, 0, gump_data.gumpDefinition, gump_data.gumpStrings)
            self._last_render_signature = visible_plain
            self._last_gump_send_ms = now_ms
        except Exception as e:
            # On failure, do not spam retries; wait until next update cycle
            debug_message(f" SendGump error: {e}")

    #//======= Input handling =====================
    def handle_gump_response(self):
        gump_data = Gumps.GetGumpData(self.gump_id)
        if not gump_data:
            return
        debug_message(f" handle_gump_response buttonid={gump_data.buttonid}")
    
    def update(self):
        # Update loop tick: throttle, then refresh and draw conditionally
        try:
            pause_ms = int(self.update_interval_ms)
            if ENABLE_JITTER:
                try:
                    pause_ms += int(random.randint(0, int(JITTER_MS_MAX)))
                except Exception:
                    pass
            Misc.Pause(pause_ms)
        except Exception:
            pass
        # Refresh data
        new_count = self.build_filtered_journal_entries()
        # Only redraw/send gump if something changed
        if new_count > 0:
            self.draw_gump()
    
    def _build_entry_texts(self, entry):
        # Build both HTML display text and plain text for measurement for an entry row
        try:
            name_part = str(entry[2]) if entry[2] is not None else ""
            msg_part = str(entry[4])
            ts_part = ""
            if SHOW_TIMESTAMP:
                tm_struct = time.localtime(entry[5])
                time_str = time.strftime('%H:%M:%S', tm_struct)
                ts_part = f"[{time_str}] "
            speaker_color = self._color_for_speaker(name_part)
            colored_name_html = f"<BASEFONT COLOR=\"{speaker_color}\">{name_part}</BASEFONT>" if name_part else ""
            if str(entry[0]) == 'Global' and colored_name_html:
                display_text = f"{ts_part}[{name_part}] : {msg_part}"
                # Color only specific segments to avoid nested outer span masking inner spans in browser preview
                html_text = (
                    f"<BASEFONT COLOR=\"{CHAT_TEXT_COLOR}\">{ts_part}[</BASEFONT>"
                    f"{colored_name_html}"
                    f"<BASEFONT COLOR=\"{CHAT_TEXT_COLOR}\">] : {msg_part}</BASEFONT>"
                )
                plain_text = display_text
            elif str(entry[0]) == 'Quest':
                display_text = f"{ts_part}[QUEST] {msg_part}"
                html_text = f"<BASEFONT COLOR=\"{QUEST_TEXT_COLOR}\">{display_text}</BASEFONT>"
                plain_text = display_text
            elif str(entry[0]) == 'Shrine':
                # Virtue shrine alerts use a unified orange color
                display_text = f"{ts_part}[VIRTUE SHRINE] {msg_part}"
                html_text = f"<BASEFONT COLOR=\"{VIRTUE_ALERT_COLOR}\">{display_text}</BASEFONT>"
                plain_text = display_text
            elif str(entry[0]) == 'Danger':
                # Danger zones: red label + pre-colored region list in message
                display_text = f"{ts_part}[DANGER ZONE] : {msg_part}"
                html_text = f"<BASEFONT COLOR=\"{DANGER_ZONE_LABEL_COLOR}\">{ts_part}[DANGER ZONE]</BASEFONT> : {msg_part}"
                plain_text = display_text
            else:
                if colored_name_html:
                    display_text = f"{ts_part}{name_part} : {msg_part}"
                    # Only emit a timestamp span if we actually show a timestamp
                    ts_html = f"<BASEFONT COLOR=\"{CHAT_TEXT_COLOR}\">{ts_part}</BASEFONT>" if ts_part else ""
                    # Speaker in own color; separator+message in base chat color
                    html_text = f"{ts_html}{colored_name_html}<BASEFONT COLOR=\"{CHAT_TEXT_COLOR}\"> : {msg_part}</BASEFONT>"
                    plain_text = display_text
                else:
                    display_text = f"{ts_part}{msg_part}"
                    html_text = f"<BASEFONT COLOR=\"{CHAT_TEXT_COLOR}\">{display_text}</BASEFONT>"
                    plain_text = display_text

            # Alert highlighting: if text contains " is attacking you", color entire message bright red
            try:
                if ALERT_ATTACK_SUBSTRING.lower() in plain_text.lower():
                    html_text = f"<BASEFONT COLOR=\"{ALERT_ATTACK_COLOR}\">{plain_text}</BASEFONT>"
            except Exception:
                pass
            # Ensure plain_text contains no HTML tags so span calculation is based on visible characters
            try:
                plain_text = self._strip_html_tags(plain_text)
            except Exception:
                pass
            return html_text, plain_text
        except Exception:
            s = str(entry)
            return f"<BASEFONT COLOR=\"{CHAT_TEXT_COLOR}\">{s}</BASEFONT>", s
    
    def _estimate_line_span(self, plain_text, width_px):
        # Rough estimate of how many wrapped lines a piece of text will occupy
        try:
            # Approximate average character width in pixels for the gump font
            avg_char_px = 7.0
            columns = max(1, int(width_px / avg_char_px))
            length = max(1, len(plain_text))
            # simple ceiling division
            span = (length + columns - 1) // columns
            return max(1, span)
        except Exception:
            return 1

    def _get_span_for_entry(self, entry, plain_text, width_px):
        try:
            key = (entry[5], entry[3], hash(plain_text), int(width_px))
        except Exception:
            key = (hash(str(entry)), int(width_px))
        cached = self._span_cache.get(key)
        if cached:
            return cached
        span = max(1, self._estimate_line_span(plain_text, width_px))
        # size-bound cache
        if len(self._span_cache) >= self._span_cache_max:
            try:
                self._span_cache.clear()
            except Exception:
                pass
        self._span_cache[key] = span
        return span

def main():
    debug_message(' Starting main()')
    ui = JournalFilterUI()
    if OFFLINE_JOURNAL_SIMULATE:
        # Run offline simulation and exit
        try:
            ui.simulate_from_text_file(OFFLINE_JOURNAL_INPUT_PATH, OFFLINE_JOURNAL_OUTPUT_PATH)
        except Exception as e:
            debug_message(f"Offline simulate failed: {e}")
        return
    # Live UI mode
    ui.build_filtered_journal_entries()
    ui.draw_gump()
    while True:
        ui.update()

main()