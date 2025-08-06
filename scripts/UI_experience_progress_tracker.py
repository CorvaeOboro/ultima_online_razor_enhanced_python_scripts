"""
UI Experience Progress Tracker - a Razor Enhanced Python Script for Ultima Online

Tracks progression systems by parsing journal and visualizes in a custom Gump UI
EXAMPLES TO MATCH = 'Label: 123 / 456', '[Label: 123 / 456]',
percentage first , colorize by category , display as bar 

change the ULTIMA_CLIENT_LOG_FOLDERPATH to match your client location JournalLogs
currently tuned for UOUnchained progression ( Mastery , Weekly Quests , Dungeons )

STATUS:: working
HOTKEY:: StartUp
VERSION::20250802
"""
import re
import time
import string
import threading
from datetime import datetime
import os

ULTIMA_CLIENT_LOG_FOLDERPATH = r'D:\ULTIMA\UO_Unchained\Data\Client\JournalLogs'

DEBUG_MODE = False  # Set to True to enable in-game debug messages

# gump ID= 4294967295  = the max value , randomly select a high number less then max
GUMP_ID =  3329354321

GUMP_X = 700
GUMP_Y = 600  
UPDATE_INTERVAL = 300  # ms
JOURNAL_SCAN_INTERVAL = 100  # ms
BAR_WIDTH = 260  
BAR_HEIGHT = 16  
BAR_SPACING = 6  

FONT_COLORS = {
    'red': 0x0020,         # red
    'dark red': 0x0024,    # dark red
    'maroon': 0x0021,      # maroon 
    'pink': 0x0028,        # pink 
    'orange': 0x0030,      # orange 
    'yellow': 0x0099,      # yellow
    'gold': 0x08A5,        # gold 
    'beige': 0x002D,       # beige 
    'brown': 0x01BB,       # light brown
    'green': 0x0044,       # green 
    'dark green': 0x0042,  # dark green
    'lime': 0x0040,        # lime
    'teal': 0x0058,        # teal
    'aqua': 0x005F,        # aqua
    'light blue': 0x005A,  # light blue
    'blue': 0x0056,        # blue 
    'dark blue': 0x0001,   # dark blue 
    'purple': 0x01A2,      # purple
    'white': 0x0384,       # white
    'gray': 0x0385,        # gray 
    'dark gray': 0x07AF,   # dark gray
    'black': 0x0000        # black
}

GUMP_HUE_COLORS = {
    'background': FONT_COLORS['black'],
    'bar': FONT_COLORS['green'],
    'bar2': FONT_COLORS['blue'],
    'bar3': FONT_COLORS['orange'],
    'text': FONT_COLORS['white'],
    'outline': FONT_COLORS['black'],
    'exp': FONT_COLORS['red'],
    'quest': FONT_COLORS['gold'],
    'mastery': FONT_COLORS['blue'],
    'summons': FONT_COLORS['teal'],
}

CATEGORY_COLORS = {
    'weekly quest': FONT_COLORS['gold'],
    'mastery': FONT_COLORS['blue'],
    'dungeon': FONT_COLORS['gold'],
    'spellsong': FONT_COLORS['green'],
    'holy': FONT_COLORS['blue'],
    'elemental': FONT_COLORS['purple'],
    'summons': FONT_COLORS['teal'],
    'default': FONT_COLORS['white']
}

# Exclude certain progress types that are not quests (e.g., XP, Max Stones)
EXCLUDED_PROGRESS_KEYS = ["Xp", "Max Stones"]

# --- JOURNAL PROGRESS PATTERN ---
# Matches any line containing "<current>/<max>" and uses text before as the title
# EXAMPLES TO MATCH = 'Label: 123 / 456', '[Label: 123 / 456]',
# Matches lines like 'Label: 123 / 456', '[Label: 123 / 456]', 'Weekly Quest: ... (126/222)'
PROGRESS_PATTERN = re.compile(r'([A-Za-z \[\]\:]+):\s*(\d+)\s*/\s*(\d+)')
PROGRESS_PARENS_PATTERN = re.compile(r'([A-Za-z \[\]\:]+)\s*\((\d+)\s*/\s*(\d+)\)')

# --- CONFIGURATION ---
LOG_FILE_PATH = 'experience_progress_tracker.log'  # Output log file path

# --- DIAGNOSTIC KEYWORDS ---
JOURNAL_DIAGNOSTIC_KEYWORDS = {
    'system_types': ['System'],
    'system_names': ['System', 'Username'],
    'search_terms': [
        'Mastery',
        'Weekly Quest',
        'Spellsong',
        'Holy',
        'Elemental',
        'Dungeon',
        'Enhanced Summons'
    ]
}


def log(message):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_FILE_PATH, 'a', encoding='utf-8') as f:
        f.write(f'[{timestamp}] {message}\n')

def debug(message):
    if DEBUG_MODE:
        try:
            Misc.SendMessage(str(message))
        except Exception:
            pass  # In case Misc isn't available at import time
    log(str(message))

def debug_module_info():
    try:
        debug('--- DEBUG: Journal ---')
        debug('type(Journal): ' + str(type(Journal)))
        attrs = dir(Journal)
        debug('dir(Journal): ' + str(attrs))
        for attr in attrs:
            try:
                value = getattr(Journal, attr)
                debug(f'Journal.{attr} = {value}')
                if isinstance(value, int):
                    debug(f'Journal.{attr} (int) = {value}')
            except Exception as e:
                debug(f'Error accessing Journal.{attr}: {e}')
        # Try GetLineText at various indices
        for idx in [0, 1, -1, 100]:
            try:
                result = Journal.GetLineText(idx)
                debug(f'Journal.GetLineText({idx}) = {result}')
            except Exception as e:
                debug(f'Journal.GetLineText({idx}) error: {e}')
        # Try GetJournalEntry(0)
        try:
            result = Journal.GetJournalEntry(0)
            debug(f'Journal.GetJournalEntry(0) = {result}')
            if result and hasattr(result, '__getitem__'):
                entry = result[0]
                attrs = dir(entry)
                debug(f'First JournalEntry attributes: {attrs}')
                for attr in attrs:
                    try:
                        value = getattr(entry, attr)
                        debug(f'JournalEntry.{attr} = {value}')
                    except Exception as e:
                        debug(f'Error accessing JournalEntry.{attr}: {e}')
        except Exception as e:
            debug(f'Journal.GetJournalEntry(0) error: {e}')
    except Exception as e:
        debug('DEBUG ERROR: ' + str(e))

debug_module_info()

class ProgressTracker:
    def __init__(self):
        self.tasks = {}  # {task_name: {'current': int, 'max': int, 'last_gain': time}}
        self.last_journal_index = 0  # Parse all journal lines on first run
        self.last_update = 0
        self.gump_x = GUMP_X
        self.gump_y = GUMP_Y
        self.gump_open = True  # Track if gump should be open

    def handle_gump_response(self):
        # If the gump is no longer open, set flag to stop updating
        if not Gumps.HasGump(GUMP_ID):
            self.gump_open = False

    def parse_journal(self):
        entries = Journal.GetJournalEntry(0)
        line_count = len(entries)
        debug(f'[XP Tracker] Parsing journal: last_index={self.last_journal_index}, line_count={line_count}')

        # Diagnostics: Add filters for likely XP/progress keywords
        for keyword in JOURNAL_DIAGNOSTIC_KEYWORDS['search_terms']:
            try:
                Journal.FilterText(keyword)
                debug(f'[XP Tracker] [Diagnostics] Journal.FilterText({repr(keyword)}) applied.')
            except Exception as e:
                debug(f'[XP Tracker] [Diagnostics] Journal.FilterText({repr(keyword)}) error: {e}')

        # Diagnostics: Dump ALL journal lines for inspection
        all_entries = Journal.GetJournalEntry(0)
        debug(f'[XP Tracker] [Diagnostics] Dumping ALL journal entries ({len(all_entries)} total):')
        for idx, entry in enumerate(all_entries):
            debug(f'[XP Tracker] [ALL] idx={idx}, Type={repr(getattr(entry, "Type", None))}, Name={repr(getattr(entry, "Name", None))}, Text={repr(getattr(entry, "Text", None))}, Color={repr(getattr(entry, "Color", None))}')
            if getattr(entry, "Type", None) == "System":
                debug(f'[XP Tracker] [ALL][Type==System] idx={idx}, Text={repr(getattr(entry, "Text", None))}')
            if getattr(entry, "Name", None) == "System":
                debug(f'[XP Tracker] [ALL][Name==System] idx={idx}, Text={repr(getattr(entry, "Text", None))}')

        # Diagnostics: Brute-force Journal.GetLineText
        debug(f'[XP Tracker] [Diagnostics] Brute-force Journal.GetLineText(0..199):')
        for i in range(200):
            try:
                line = Journal.GetLineText(i)
                debug(f'[XP Tracker] [GetLineText] idx={i}, line={repr(line)}')
            except Exception as e:
                debug(f'[XP Tracker] [GetLineText] idx={i}, error={e}')
        # Diagnostics: Try other journal APIs using global diagnostic keywords
        for sys_type_val in JOURNAL_DIAGNOSTIC_KEYWORDS['system_types']:
            try:
                sys_type = Journal.GetTextByType(sys_type_val)
                debug(f'[XP Tracker] [Diagnostics] GetTextByType({repr(sys_type_val)}): {repr(sys_type)}')
            except Exception as e:
                debug(f'[XP Tracker] [Diagnostics] GetTextByType({repr(sys_type_val)}) error: {e}')
        for sys_name_val in JOURNAL_DIAGNOSTIC_KEYWORDS['system_names']:
            try:
                sys_name = Journal.GetTextByName(sys_name_val)
                debug(f'[XP Tracker] [Diagnostics] GetTextByName({repr(sys_name_val)}): {repr(sys_name)}')
            except Exception as e:
                debug(f'[XP Tracker] [Diagnostics] GetTextByName({repr(sys_name_val)}) error: {e}')
        for search_term in JOURNAL_DIAGNOSTIC_KEYWORDS['search_terms']:
            try:
                search_result = Journal.Search(search_term)
                debug(f'[XP Tracker] [Diagnostics] Search({repr(search_term)}): {repr(search_result)}')
            except Exception as e:
                debug(f'[XP Tracker] [Diagnostics] Search({repr(search_term)}) error: {e}')

        for i in range(self.last_journal_index, line_count):
            entry = entries[i]
            debug(f'[XP Tracker] [Journal Extract] idx={i}, Type={repr(getattr(entry, "Type", None))}, Name={repr(getattr(entry, "Name", None))}, Text={repr(getattr(entry, "Text", None))}, Color={repr(getattr(entry, "Color", None))}')
            if entry.Name and entry.Text:
                line = f'{entry.Name}: {entry.Text}'
            elif entry.Text:
                line = entry.Text
            else:
                line = ''
            debug(f'[XP Tracker] [Journal Line] idx={i}, line={repr(line)}')
            self._parse_line(line)
        self.last_journal_index = line_count

    
    def _parse_line(self, line):
        debug(f'[XP Tracker] [Parse Attempt] line={repr(line)}')
        if 'Max Stones' in line:
            debug('[XP Tracker] [Parse Ignore] Skipping Max Stones line')
            return False
        # Exclude lines with keys in exclusion list
        for excluded in EXCLUDED_PROGRESS_KEYS:
            if excluded in line:
                debug(f'[XP Tracker] [Parse Ignore] Skipping excluded key: {excluded}')
                return False
        m = PROGRESS_PATTERN.search(line)
        if m:
            debug(f'[XP Tracker] [Regex:slash] MATCHED: groups={m.groups()}')
            title = m.group(1).strip()
            if title.endswith(':'):
                title = title[:-1].strip()
            # Only use the last segment after splitting by colon, for clean Gump labels
            title_clean = title.split(':')[-1].strip() if ':' in title else title
            # Remove brackets from display name
            title_clean = title_clean.replace('[','').replace(']','').strip()
            cur = int(m.group(2))
            maxval = int(m.group(3))
            key = title_clean if title_clean else 'Progress'
            debug(f'[XP Tracker] [Parse Result] source=slash, key={repr(key)}, cur={cur}, max={maxval}')
            updated = False
            if key not in self.tasks or self.tasks[key]['current'] != cur or self.tasks[key]['max'] != maxval:
                self.tasks[key] = {'current': cur, 'max': maxval, 'last_gain': time.time()}
                updated = True
            else:
                self.tasks[key]['current'] = cur
                self.tasks[key]['max'] = maxval
                self.tasks[key]['last_gain'] = time.time()
            return updated
        m2 = PROGRESS_PARENS_PATTERN.search(line)
        if m2:
            debug(f'[XP Tracker] [Regex:parens] MATCHED: groups={m2.groups()}')
            title = m2.group(1).strip()
            if title.endswith(':'):
                title = title[:-1].strip()
            # Only use the last segment after splitting by colon, for clean Gump labels
            title_clean = title.split(':')[-1].strip() if ':' in title else title
            # Remove brackets from display name
            title_clean = title_clean.replace('[','').replace(']','').strip()
            cur = int(m2.group(2))
            maxval = int(m2.group(3))
            key = title_clean if title_clean else 'Progress'
            debug(f'[XP Tracker] [Parse Result] source=parens, key={repr(key)}, cur={cur}, max={maxval}')
            updated = False
            if key not in self.tasks or self.tasks[key]['current'] != cur or self.tasks[key]['max'] != maxval:
                self.tasks[key] = {'current': cur, 'max': maxval, 'last_gain': time.time()}
                updated = True
            else:
                self.tasks[key]['current'] = cur
                self.tasks[key]['max'] = maxval
                self.tasks[key]['last_gain'] = time.time()
            return updated
        debug(f'[XP Tracker] [Parse Result] NO MATCH: line={repr(line)}')
        return False

    def get_task_list(self):
        # Return sorted list of tracked tasks
        return sorted(self.tasks.keys())

    def get_progress(self, task):
        info = self.tasks[task]
        cur = info['current']
        maxval = info['max'] if info['max'] > 0 else max(cur, 1)
        pct = min(100, int(100 * cur / maxval))
        return cur, maxval, pct

    def update(self):
        if not self.gump_open:
            return
        self.parse_journal()
        self._draw_gump()

    def _draw_gump(self):
        debug('[XP Tracker] _draw_gump called')
        g = Gumps.CreateGump(movable=True)
        Gumps.AddPage(g, 0)
        # No background for a transparent/overlay look
        width = BAR_WIDTH + 28
        height = self._gump_height()
        Gumps.AddLabel(g, 12, 8, GUMP_HUE_COLORS['text'], "Progress Tracker")
        y = 28  # Slightly higher for compactness
        task_list = self.get_task_list()
        if not task_list:
            Gumps.AddLabel(g, 18, y + 1, GUMP_HUE_COLORS['text'], "No progress found.")
            y += BAR_HEIGHT + BAR_SPACING
        for idx, task in enumerate(task_list):
            cur, maxval, pct = self.get_progress(task)
            # Determine category color
            lower_task = task.lower()
            color = GUMP_HUE_COLORS['bar']  # Default
            for cat, cat_color in CATEGORY_COLORS.items():
                if cat != 'default' and cat in lower_task:
                    color = cat_color
                    break
            else:
                color = CATEGORY_COLORS['default']
            # Bar background
            Gumps.AddImageTiled(g, 12, y, BAR_WIDTH, BAR_HEIGHT, 2624)  # Black tiled bar
            # Progress bar
            fill_width = int(BAR_WIDTH * pct / 100)
            if fill_width > 0:
                Gumps.AddImageTiled(g, 12, y, fill_width, BAR_HEIGHT, 9304)  # Colored bar
                Gumps.AddAlphaRegion(g, 12, y, fill_width, BAR_HEIGHT)
            # Task label: percent, then name
            pct_str = f"{pct:02d}%"  # Always two digits
            # Shorten label if it contains 'Creature Killed In'
            # Remove both 'Creature Killed In' and 'Creature Killed in' (case-insensitive)
            import re
            short_task = re.sub(r'(?i)creature killed in', '', task).replace('  ', ' ').strip()
            # Remove brackets at display time
            short_task = short_task.replace('[','').replace(']','').strip()
            label_main = f"{pct_str}  {short_task.title()}: "
            label_nums = f"{cur}/{maxval}"
            # Draw main label (percent and name)
            # Estimate the width of the main label (percent + name + colon + 2 spaces)
            # Assume ~6 pixels per character for default font 
            main_label_width = 6 * len(label_main)
            Gumps.AddLabel(g, 18, y + 1, color, label_main)
            num_x = 18 + main_label_width + 4  # 4px gap width 
            # Draw numbers in smaller font or lighter color, offset to the right
            try:
                # Use HTML Gump for small font if supported (font size 8)
                html = f"<center><font size=8 color=gray>{label_nums}</font></center>"
                Gumps.AddHtmlGump(g, num_x, y + 1, 70, BAR_HEIGHT, html, False, False)
            except Exception:
                # Fallback: use a dimmer color for numbers
                Gumps.AddLabel(g, num_x, y + 1, 922, label_nums)  # 922 = grayish
            y += BAR_HEIGHT + BAR_SPACING
        Gumps.AddButton(g, BAR_WIDTH + 2, 4, 3600, 3601, 1, 0, 0)  # Close button, working convention
        debug(f'[XP Tracker] Sending Gump to serial {Player.Serial}')
        Gumps.SendGump(GUMP_ID, Player.Serial, self.gump_x, self.gump_y, g.gumpDefinition, g.gumpStrings)

    def _gump_height(self):
        n = max(1, len(self.tasks))
        return 36 + n * (BAR_HEIGHT + BAR_SPACING) + 12

def find_newest_log_file(log_dir):
    files = [os.path.join(log_dir, f) for f in os.listdir(log_dir) if os.path.isfile(os.path.join(log_dir, f))]
    if not files:
        return None
    newest = max(files, key=os.path.getmtime)
    return newest

def tail_log_file(filepath, callback):
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        f.seek(0, 2)  # Always go to end of file on startup (never parse old lines)
        debug(f'[XP Tracker] [Log Tail] Started tailing {filepath} at EOF')
        while True:
            pos = f.tell()
            line = f.readline()
            if not line:
                time.sleep(0.1)
                continue
            # Only process complete lines
            if not line.endswith('\n'):
                f.seek(pos)  # Wait for the rest of the line
                time.sleep(0.05)
                continue
            # Clean up non-printable characters
            cleaned = ''.join(ch for ch in line if ch in string.printable)
            if '[XP Tracker]' in cleaned:
                # Skip own debug output to prevent infinite feedback loop
                continue
            if cleaned.strip() == '':
                # Optionally debug skipped lines
                continue
            try:
                debug(f'[XP Tracker] [Log Tail] Cleaned line: {cleaned.rstrip()}')
                callback(cleaned.rstrip('\n'))
            except Exception as e:
                debug(f'[XP Tracker] [Log Tail] Exception processing line: {e} | line={repr(cleaned)}')

class LogFileProgressTracker(ProgressTracker):
    def __init__(self, log_path):
        super().__init__()
        self.log_path = log_path
        self.gump_open = True
        self.dirty = False  # Set to True when progress changes
        self.last_update = None
        self.update_interval = 2000  # ms, matches summon monitor
    def process_log_line(self, line):
        # Skip lines that are our own debug output or don't look like XP/progress messages
        if '[XP Tracker]' in line or not re.search(r'\w+:', line):
            return
        debug(f'[XP Tracker] [LogFile] {line}')
        updated = self._parse_line(line)
        if updated:
            self.dirty = True
    def update(self):
        now = datetime.now()
        if self.last_update is None:
            time_diff = self.update_interval + 1  # Force first update
        else:
            time_diff = (now - self.last_update).total_seconds() * 1000
        if time_diff >= self.update_interval:
            debug('[XP Tracker] Running update cycle...')
            if self.tasks:
                self._draw_gump()
            else:
                debug('[XP Tracker] No progress tasks, closing Gump.')
                Gumps.CloseGump(GUMP_ID)
            self.last_update = now

def main():
    debug('[XP Tracker] ENTERED MAIN()')
    try:
        debug('[XP Tracker] Main loop started')
        log_path = find_newest_log_file(ULTIMA_CLIENT_LOG_FOLDERPATH)
        if not log_path:
            debug(f'[XP Tracker] No log file found in {log_dir}')
            return
        debug(f'[XP Tracker] Using log file: {log_path}')
        tracker = LogFileProgressTracker(log_path)
        # Start log file tailer in a background thread
        t = threading.Thread(target=tail_log_file, args=(log_path, tracker.process_log_line), daemon=True)
        t.start()
        # Main loop: handle Gump drawing and response
        cycle = 0
        while True:
            debug(f'[XP Tracker] Main loop cycle {cycle}, dirty={tracker.dirty}')
            tracker.handle_gump_response()
            time.sleep(0.5)  # Sleep to be passive and non-blocking
            if tracker.dirty:
                debug('[XP Tracker] Main loop: dirty flag set, drawing Gump.')
                tracker._draw_gump()
                tracker.dirty = False
            time.sleep(0.5)
            cycle += 1
    except Exception as e:
        debug(f'[XP Tracker] EXCEPTION in main loop: {e}')

main()
