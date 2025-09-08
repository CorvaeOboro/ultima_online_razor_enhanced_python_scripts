"""
UI Journal Filtered - a Razor Enhanced Python Script for Ultima Online

a minimal journal gump focused on local said messages , persistent display with quest notifications 
using multiple filters to reduce to player and npc spoken words without "command words"
names are colorized consistently by deterministic seed to visually separate
only "Quest" related system messages are whitelisted 

filters=
common command words "bank" , "All guard me" , 
repeating messages
known npcs are filtered out

STATUS:: working
VERSION::20250907
"""

import time # timestamps , and for timing the mouse lock for moving gump ( considering removing )
import re # regex parsing the text

DEBUG_MODE = False

SHOW_SYSTEM = True
SHOW_REGULAR = True
SHOW_PARTY = True
SHOW_GUILD = True
SHOW_ALLIANCE = True

SHOW_EMOTE = False
SHOW_LABEL = False
SHOW_FOCUS = False
SHOW_SPELL = False

ADDITIONAL_FILTERS = {
    "Player": True,
    "Spam": True,
    "StatusEffects": False, # Default to HIDE status effects 
    "BondedPets": False,
}

# System global messages ("System : PlayerName : message") or ("System : <General> PlayerName : message") 
SHOW_SYSTEM_GLOBAL_MESSAGES = True # If False, they are filtered out completely. If True, they are shown but reformatted.
ONLY_ALLOW_SYSTEM_QUESTS = True # Only allow non-global System messages that contain the word "quest"
FILTER_OPTIONAL_NPC_ENABLED = True # Toggle: when True, also filter out names listed in FILTER_SPEAKER_OPTIONAL_NPC

SHOW_TIMESTAMP = False  # Show [HH:MM:SS] prefix; default off per user preference
DEDUPLICATE_BY_TEXT = True # De-duplicate by text content (case-insensitive, whitespace-normalized)
CHAT_ORDER_TOP_NEW = True  # True=newest at top; False=oldest at top , new entries appear at bottom

#//==== GUMP ===================
# example=4294967295 #  a high pseudo-random gump id to avoid other existing gump ids
GUMP_ID = 3135545776

# Default gump position and sizing
DEFAULT_GUMP_X = 100
DEFAULT_GUMP_Y = 0
DEFAULT_GUMP_WIDTH = 420
DEFAULT_GUMP_HEIGHT = 500

# TIMING
UPDATE_INTERVAL_MS = 200

# UI SHAPE
FILTER_PANEL_WIDTH = 115
JOURNAL_START_X = 20
JOURNAL_START_Y = 25
FILTER_SPACING_Y = 30
JOURNAL_ENTRY_HEIGHT = 20

# Chat COLORS
CHAT_BG_DARK = True
CHAT_TEXT_COLOR = "#C0C0C0"  # light grey
QUEST_TEXT_COLOR = "#76D7C4" # Muted gold for quest lines ( other options gold = #C2A14A , teal = #76D7C4)
CHAT_BG_IMAGE_ID = None  # e.g., 2624 if you have a known black tile; None = no image # Leave as None to avoid any image (fully transparent via alpha region only).

# Move-lock sensitivity
MOVE_LOCK_ENABLE = True           # set False if move-lock interferes with updates
MOVE_LOCK_THRESHOLD_PX = 20       # total dx+dy considered a movement spike (start lock)
MOVE_LOCK_DURATION_MS = 500       # initial duration to pause updates after movement spike
MOVE_LOCK_QUIET_MS = 150          # extend lock on small movements; require this much quiet before resuming

# Speaker colorization palette (bright, muted colors for readability)
PALETTE_GOOD_COLORS = [
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

# VIRTUES are referenced by in world shrines where events may occur 
VIRTUES = {
    "honesty", "compassion", "valor", "justice",
    "sacrifice", "honor", "spirituality", "humility"
}

# MASTERY_NAMES are referenced by golems in game , we use this to filter out their title messages 
MASTERY_NAMES = {
    "aero", "fira", "earth", "shadow", "blood", "doom", "fortune", "artisan", "bulwark", "poison", "lyric", "death", "druidic", "holy"
}

# Specific System lines to filter out entirely (case-insensitive, substring or regex)
FILTER_SYSTEM_SUBSTRINGS = [
    "[safe looting] you refuse to loot this corpse",
    "careful! you",  # e.g., "System : Careful! You ..."
    "enhanced summons",  # e.g., "System : [Enhanced Summons] ..."
    "enhanced sumons",  # common misspelling variant
    "a pixie is guarding you",
]

FILTER_SYSTEM_PATTERNS = [
    # Add regex patterns here if needed
]

# Generic text filters (apply to any speaker/type) , common NPC dialog , bank and vendor interactions
FILTER_GENERIC_SUBSTRINGS = [
    "you see nothing useful to carve from the corpse",
    "(summoned)",
    "the spell fizzles.",
    "You have accepted quest:",
    "bank container has ",
    "Take a look at my goods",
    "Thou hast withdrawn gold from thy account. ",
    "Thou canst not withdraw so much at one time! ",
    "There's not enough room in your bankbox",
    "the purchased items were placed in you bank box.",
    "The total of thy purchase is",
    "i am dead and cannot do that.",
    "emptying the trashcan!",
    "It appears to be locked.",
    "The trash is full!",
]

# exact matches , lowercase catches all
FILTER_GENERIC_EXACTS = [
    "1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16","17","18","19","20",
    "all guard me", "all guard",
    "all kill",
    "all follow me", "all follow",
    "all stay","all come",
    "bank","claim","stable",
    "bank guards",
    "guards open my bank","guards bank stable i ban thee",
    "vendor buy thee bank from thee guards!",
    "vendor buy thee bank from thee guards",
    "vendor buy guards bank",
    "banker bank",
    "vendor buy bank guards",
    "vendor buy bank","bank vendor buy",
    "vendor buy bank guards i ban thee",
    "bbbb",
    "bnak",
    "that is secure.","Locked down!","I can't reach that.",
    "vendor buy me a bank",
    "bank guards i ban thee",
    "bank guard room claim list i ban thee",
    "You cannot heal yourself in your current state.",
    "(tame)","(bonded)",
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

# Speaker-based filters
FILTER_SPEAKER_EXACTS = [
    "canute", # quest giver , we are letting other quest givers through but the weekly quest giver "Canute" spams unique messages for each quest some one takes
]

FILTER_SPEAKER_OPTIONAL_NPC = [
    "ogden", # quest givers in brit bank
    "luffy", # quest givers in brit bank
    "cigal", # quest givers in brit bank
    "mariel", # thief trainer givers in brit bank
    "forsythe", #banker
]

# Alert highlighting
ALERT_ATTACK_SUBSTRING = " is attacking you"
ALERT_ATTACK_COLOR = "#FF3333"

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

        # Toggles (only chat panel retained)
        self.show_chat_panel = True

        # Data
        # Static lists/sets used by filtering
        self.additional_type_names = list(ADDITIONAL_FILTERS.keys())

        # Precompiled patterns to detect status effects
        # Examples: "* PlayerName begins to spasm uncontrollably *"
        #           "* You begin to spasm uncontrollably *"
        #           Other status effect style asterisks-wrapped lines
        escaped_player = re.escape(Player.Name) if hasattr(Player, 'Name') else r"Player"
        self.status_effect_patterns = [
            re.compile(r"\*\s*(?:You|%s)\s+begins?\s+to\s+spasm\s+uncontrollably\s*\*" % escaped_player, re.IGNORECASE),
            # Generic asterisk-wrapped emotes that look like status effects
            re.compile(r"^\s*\*.+\*\s*$", re.IGNORECASE),
        ]
        # Robust System global chat pattern: captures name and message
        # Accepts variants with spaces around colons, optional channel tags like <General>, and both "System" and "Systems"
        # Examples:
        #   System : Player : hello
        #   Systems: <General> Player : hello
        #   System:<Trade>Player:hello
        self.system_global_capturing_pattern = re.compile(
            r"^\s*System[s]?\s*:?\s*(?:<[^>]+>\s*)?([^:]+?)\s*:\s*(.+)\s*$",
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

        # Move lock: when dragging the gump, pause updates to avoid interrupting the move
        self._move_lock_until_ms = 0
        self._last_mouse_x = None
        self._last_mouse_y = None
        self._last_button_id = None

        # Span cache to speed up wrapping calculations
        self._span_cache = {}
        self._span_cache_max = 2000

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
        # Example spot to apply a color tint or other remap in the future
        return SHOW_PARTY

    #//======= Data processing =====================
    def build_filtered_journal_entries(self):
        entries = Journal.GetJournalEntry(-1)
        # Ensure chronological order from oldest to newest
        entries = entries[::-1]
        debug_message(f" Processing {len(entries)} raw journal entries")
        new_count = 0
        for entry in entries:
            # Build a stable key for deduplication
            try:
                key = (entry.Timestamp, int(entry.Serial), str(entry.Text))
            except Exception:
                try:
                    key = (entry.Timestamp, entry.Serial, str(entry.Text))
                except Exception:
                    key = (entry.Timestamp, str(entry.Text))
            if key in self._seen_entry_keys:
                continue
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

            # System-specific handling: filters and global/quest message normalization
            if not hide_entry and entry.Type == 'System':
                try:
                    txt = entry.Text if isinstance(entry.Text, str) else str(entry.Text)
                    sys_handled = self._handle_system_message(txt)
                    if sys_handled.get('hide'):
                        hide_entry = True
                    elif sys_handled.get('is_quest'):
                        # Quest lines: convert to Quest type and replace speaker with [QUEST]
                        cleaned = txt
                        try:
                            cleaned = re.sub(r"^\s*System\s*:\s*", "", cleaned, flags=re.IGNORECASE)
                        except Exception:
                            pass
                        if sys_handled.get('is_global'):
                            cleaned = sys_handled.get('message', cleaned)
                        fixed_type = 'Quest'
                        entry = type('E', (), dict(Type=fixed_type, Color=entry.Color,
                                                     Name='[QUEST]',
                                                     Serial=entry.Serial,
                                                     Text=cleaned,
                                                     Timestamp=entry.Timestamp))
                    elif sys_handled.get('is_global') and SHOW_SYSTEM_GLOBAL_MESSAGES:
                        # Reformat: show speaker and message, mark as Global for special rendering
                        fixed_type = 'Global'
                        entry = type('E', (), dict(Type=fixed_type, Color=entry.Color,
                                                     Name=sys_handled.get('speaker', entry.Name),
                                                     Serial=entry.Serial,
                                                     Text=sys_handled.get('message', txt),
                                                     Timestamp=entry.Timestamp))
                    elif sys_handled.get('is_global') and not SHOW_SYSTEM_GLOBAL_MESSAGES:
                        hide_entry = True
                except Exception:
                    pass

            # Hide player messages if disabled
            if ADDITIONAL_FILTERS.get('Player', True) is False:
                if entry.Name == Player.Name:
                    hide_entry = True

            # Speaker-based filtering
            try:
                if not hide_entry and entry.Name and isinstance(entry.Name, str):
                    if entry.Name.strip().lower() in FILTER_SPEAKER_EXACTS:
                        hide_entry = True
                    elif FILTER_OPTIONAL_NPC_ENABLED and (entry.Name.strip().lower() in FILTER_SPEAKER_OPTIONAL_NPC):
                        hide_entry = True
            except Exception:
                pass

            # Hide duplicates when Spam filter is disabled
            base_row = [entry.Type, entry.Color, entry.Name, entry.Serial, entry.Text]
            if base_row in self.filtered_entries and ADDITIONAL_FILTERS.get('Spam', True) is False:
                hide_entry = True

            # Auctioneer filtering removed per request

            # Hide bonded pets (by name suffix) when disabled
            try:
                if ADDITIONAL_FILTERS.get('BondedPets', False) is False:
                    if entry.Name and isinstance(entry.Name, str):
                        lname = entry.Name.lower()
                        if ('{bonded}' in lname) or ('[bonded]' in lname) or ('(bonded)' in lname):
                            hide_entry = True
            except Exception:
                pass

            # Hide status effects when disabled (pattern-based)
            try:
                if ADDITIONAL_FILTERS.get('StatusEffects', False) is False:
                    text = entry.Text if isinstance(entry.Text, str) else str(entry.Text)
                    if self._is_status_effect_line(text):
                        hide_entry = True
            except Exception:
                pass

            # Hide bonded-only text (e.g., "[bonded]", "{bonded)") after colon content when bonded pets are disabled
            try:
                if ADDITIONAL_FILTERS.get('BondedPets', False) is False:
                    text = entry.Text if isinstance(entry.Text, str) else str(entry.Text)
                    if self._is_bonded_only_text(text):
                        hide_entry = True
            except Exception:
                pass

            # Generic content filters regardless of speaker/type
            try:
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
                # Filter pure withdraw commands like "withdraw 5,000"
                if not hide_entry:
                    try:
                        text_raw = str(entry.Text)
                        if (
                            WITHDRAW_ONLY_PATTERN.match(text_raw)
                            or DEPOSIT_ONLY_PATTERN.match(text_raw)
                            or CHECK_ONLY_PATTERN.match(text_raw)
                            or BALANCE_ONLY_PATTERN.match(text_raw)
                            or STATEMENT_ONLY_PATTERN.match(text_raw)
                        ):
                            hide_entry = True
                    except Exception:
                        pass
            except Exception:
                pass

            # Hide empty
            try:
                if len(entry.Text.strip()) == 0:
                    hide_entry = True
            except Exception:
                hide_entry = True

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
                if DEDUPLICATE_BY_TEXT and text_norm:
                    if text_norm in self._seen_text_norm:
                        # skip appending duplicate text
                        pass
                    else:
                        self._seen_text_norm.add(text_norm)
                        self.filtered_entries.append(row)
                        self.filtered_entries_with_time.append(row_with_time)
                else:
                    self.filtered_entries.append(row)
                    self.filtered_entries_with_time.append(row_with_time)
            # mark as seen regardless so we don't reprocess on the next tick
            self._seen_entry_keys.add(key)
            new_count += 1

        debug_message(f" Appended {new_count} entries; total filtered: {len(self.filtered_entries_with_time)}")

    def _is_status_effect_line(self, text):
        try:
            for pat in self.status_effect_patterns:
                if pat.search(text):
                    return True
        except Exception:
            pass
        return False

    # Parse and filter System messages
    # Returns a dict: { 'hide': bool, 'is_global': bool, 'speaker': str, 'message': str, 'is_quest': bool }
    def _handle_system_message(self, text):
        out = { 'hide': False, 'is_global': False, 'is_quest': False }
        try:
            s = str(text)
            low = s.lower()
            # Always-allow keywords even when ONLY_ALLOW_SYSTEM_QUESTS is True
            allow_keywords = ('danger zone' in low) or ('hellfire' in low)
            # Virtue alerts like "Spirituality is currently under attack!"
            virtue_alert = any(v in low for v in VIRTUES) and ('attack' in low)
            if allow_keywords or virtue_alert:
                # Mark as quest-allowed so it passes the quest gate
                out['is_quest'] = True
            # Specific substrings
            for sub in FILTER_SYSTEM_SUBSTRINGS:
                if sub in low:
                    out['hide'] = True
                    return out
            # Specific regex patterns
            for pat in FILTER_SYSTEM_PATTERNS:
                try:
                    if pat.search(s):
                        out['hide'] = True
                        return out
                except Exception:
                    continue
            # Global message detection with capture
            m = self.system_global_capturing_pattern.match(s)
            if m:
                speaker = m.group(1).strip()
                message = m.group(2).strip()
                out['is_global'] = True
                out['speaker'] = speaker
                out['message'] = message
                if 'quest' in low:
                    out['is_quest'] = True
                # If enforcing quest-only System lines, hide global unless it mentions quest
                # BUT if global messages are enabled, do not hide them
                if ONLY_ALLOW_SYSTEM_QUESTS and ('quest' not in low) and (out.get('is_quest') is not True) and not (SHOW_SYSTEM_GLOBAL_MESSAGES and out['is_global']):
                    out['hide'] = True
                return out
            # If enforcing quest-only System lines, hide anything that doesn't mention quest
            if ONLY_ALLOW_SYSTEM_QUESTS and ('quest' not in low) and (out.get('is_quest') is not True):
                out['hide'] = True
                return out
            if 'quest' in low:
                out['is_quest'] = True
        except Exception:
            pass
        return out

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
            idx = (h + int(COLOR_SEED_OFFSET)) % len(PALETTE_GOOD_COLORS)
            return PALETTE_GOOD_COLORS[idx]
        except Exception:
            return CHAT_TEXT_COLOR

    #//======= UI drawing =====================
    def draw_gump(self):
        gump_data = Gumps.CreateGump(True, True, False, False)
        Gumps.AddPage(gump_data, 0)

        # Chat section
        if self.show_chat_panel:
            # Title is rendered within the chat background area below

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
            # For newest-first display, keep order as collected (newest -> older)
            # If not reversing, flip to render oldest -> newest
            if not CHAT_ORDER_TOP_NEW:
                selected.reverse()

            # Compute dynamic background height based on total rendered lines
            total_render_lines = sum(span for _, span, _, _ in selected)
            # Reserve one line for the title
            total_render_height = (total_render_lines * JOURNAL_ENTRY_HEIGHT) + JOURNAL_ENTRY_HEIGHT

            # Add dark background region sized to content (safe-clamped)
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

            # Title: 'Local Chat' rendered inside background in grey
            title_html = "<BASEFONT COLOR=\"#333333\">      ________  L O C A L  C H A T  ________</BASEFONT>"
            tx, ty, tw, th = self._safe_rect(JOURNAL_START_X + 4, JOURNAL_START_Y + 2, self.resize_width - 35, JOURNAL_ENTRY_HEIGHT)
            Gumps.AddHtml(gump_data, tx, ty, tw, th, title_html, False, False)

            # Render with proper vertical spacing by allocating height per span, after the title
            current_y = JOURNAL_START_Y + JOURNAL_ENTRY_HEIGHT
            for _, span, html_text, _ in selected:
                height_px = span * JOURNAL_ENTRY_HEIGHT
                rx, ry, rw, rh = self._safe_rect(JOURNAL_START_X, current_y, self.resize_width - 25, height_px)
                Gumps.AddHtml(gump_data, rx, ry, rw, rh, html_text, False, False)
                current_y += height_px

        else:
            Gumps.AddLabel(gump_data, 130, 0, 0, "Chat Hidden")

        Gumps.CloseGump(self.gump_id)
        Gumps.SendGump(self.gump_id, Player.Serial, 0, 0, gump_data.gumpDefinition, gump_data.gumpStrings)

    #//======= Input handling =====================
    def handle_gump_response(self):
        gump_data = Gumps.GetGumpData(self.gump_id)
        if not gump_data:
            return
        debug_message(f" handle_gump_response buttonid={gump_data.buttonid}")

        # Track last mouse for movement checks
        self._last_mouse_x = Misc.MouseLocation().X
        self._last_mouse_y = Misc.MouseLocation().Y
        self._last_button_id = gump_data.buttonid

    def _is_move_locked(self):
        try:
            return int(time.time() * 1000) < self._move_lock_until_ms
        except Exception:
            return False

    def detect_move_activity(self):
        try:
            if not MOVE_LOCK_ENABLE:
                return False
            mx = Misc.MouseLocation().X
            my = Misc.MouseLocation().Y
            now_ms = int(time.time() * 1000)
            if self._last_mouse_x is not None and self._last_mouse_y is not None:
                dx = abs(mx - self._last_mouse_x)
                dy = abs(my - self._last_mouse_y)
                delta = dx + dy
                # Large movement spike -> start/refresh long lock
                if delta > MOVE_LOCK_THRESHOLD_PX:
                    self._move_lock_until_ms = now_ms + MOVE_LOCK_DURATION_MS
                # Any movement while locked extends a short quiet period
                elif delta > 0 and now_ms < self._move_lock_until_ms:
                    self._move_lock_until_ms = now_ms + MOVE_LOCK_QUIET_MS
            self._last_mouse_x = mx
            self._last_mouse_y = my
            return now_ms < self._move_lock_until_ms
        except Exception:
            return False
    
    def update(self):
        # Update loop tick: throttle, handle movement, then refresh and draw
        try:
            Misc.Pause(self.update_interval_ms)
        except Exception:
            pass
        # Skip updates during movement lock
        if self.detect_move_activity():
            return
        if self._is_move_locked():
            return
        # Refresh data and draw
        self.build_filtered_journal_entries()
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
                html_text = f"<BASEFONT COLOR=\"{CHAT_TEXT_COLOR}\">{ts_part}[{colored_name_html}] : {msg_part}</BASEFONT>"
                plain_text = display_text
            elif str(entry[0]) == 'Quest':
                display_text = f"{ts_part}[QUEST] {msg_part}"
                html_text = f"<BASEFONT COLOR=\"{QUEST_TEXT_COLOR}\">{display_text}</BASEFONT>"
                plain_text = display_text
            else:
                if colored_name_html:
                    display_text = f"{ts_part}{name_part} : {msg_part}"
                    html_text = f"<BASEFONT COLOR=\"{CHAT_TEXT_COLOR}\">{ts_part}{colored_name_html} : {msg_part}</BASEFONT>"
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
    ui.build_filtered_journal_entries()
    ui.draw_gump()
    while True:
        ui.update()

main()