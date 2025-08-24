"""
Development Quest Gump Crawler - a Razor Enhanced Python Script for Ultima Online

Goal: Open a quest gump and extract organized data to JSON.
this may be used to populate the wiki , or useful info for other scripts

Flow per run:
1) Ensure a clean gump state.
2) Use the Mobile Quest humanoid to open the quest gump.
3) Snapshot base gump content
4) Probes button actions in an offset range to discover 
   - a category change, then an item's info panel; or
   - directly an item's info panel.
5) When an info/detail-like gump is detected, record it, then stop .

Notes:
- Button IDs and layout vary by tool/shard. We implement a small discovery scan with safety caps.
- You can configure TOOL_ITEM_IDS 
- later provide explicit CATEGORY_BUTTONS and ITEM_INFO_BUTTONS.

#//===============================================
Gump text lines vary so we map a few known example to categories
then handle each troublesome item mapping 


STATUS:: in progress , tuned for daily quests
VERSION = 20250818
"""
import time
import os
import random
import json
import codecs


# ===== Settings =====
DEBUG_MODE = True  # set True to enable verbose logging and faster pauses
DEBUG_LEVEL = 1     # 1=normal, 2=verbose
DEBUG_TO_INGAME_MESSAGE = True
DEBUG_TO_JSON = True
# Extraction cap (test mode)
MAX_ITEMS_TO_EXTRACT = 999

# Output shaping toggles
# - OUTPUT_BASE: include session/base gump and category scaffolding
# - OUTPUT_ITEM: include items parsed
# If only OUTPUT_ITEM is True, saved JSON will be a flat list of parsed items
OUTPUT_BASE = False
OUTPUT_ITEM = True
RUN_DETAIL_SCAN = True           # set True to also scan detail gumps per page

# Discovery probe (general)
BUTTON_ID_MIN = 1
BUTTON_ID_MAX = 999           # keep small to be safe for broad probing
 
# DELAYS
LOOP_PAUSE_MS = 100
JITTER_MS = 100
ITEM_BUTTON_CLICK_PAUSE_MS = 500  # slower wait for item info panels to render reliably
BUTTON_CLICK_PAUSE_MS = 100   # delay after clicking a button

# Detection thresholds to avoid endless loops when item info panels
# do not update or when probing beyond available items
MAX_MISSING_IN_ROW = 3  # consecutive non-info or unchanged info panels before skipping category

# ===== Quest Gump Config (self-contained) =====
# Buttons and gump IDs observed may vary per shard; these are hints/safe defaults.
QUEST_GIVER_SERIAL = 0x000000D4  # set to your quest NPC serial
BASE_GUMP_ID_HINT = 0xDA2ACF13   # hint only; used in waits if available

BUTTON_PREV = 1
BUTTON_NEXT = 2
BUTTON_AVAILABLE = 10

# Probe only higher indices to avoid nav/accept traps on low indices
PROBE_BUTTON_MIN = 100
PROBE_BUTTON_MAX = 200
ITEMS_PER_PAGE = 5  # number of quests per page

CONFIRM_GUMP_IDS = {0xEB54B301}
CONFIRM_TEXT_HINTS = ["accept", "are you sure", "confirm", "abandon", "cancel"]
DETAIL_TEXT_HINTS = [
    "description:",
    "objectives",
    "rewards",
    "reward:",
    "kill",
    "collect",
    "deliver",
]

WAIT_GUMP_MS = 10000
CLICK_PAUSE_MS = 400
PAGE_RESET_PAUSE_MS = 500
MAX_PAGES = 200
HOLD_DETAIL_MS = 800  # hold time on detail gump to ensure content fully renders before leaving

# Detail capture configuration (optional/advanced)
DETAIL_CAPTURE_MODE = "screenshot"     # "lines" or "screenshot"
DETAIL_SCREENSHOT_DELAY_MS = 900  # if using screenshots, delay before capture
DETAIL_OUTPUT_SUFFIX = "detail"   # used when saving separate detail files

# EXAMPLE OF GUMP RAW TEXT_LINES
# here is an example of the RAW BASE HUMP text_lines
"""
"49315",
"49315",
"49315",
"49315",
"49315",
"49315",
"49315",
"49315",
"49315",
"49315",
"49315",
"49315",
"49298",
"49302",
"Available Quests",
"Active Quests",
"Completed Quests",
"Quest Name", # start of columns
"Region",
"Type",
"Difficulty",
"Status", # end of columns
"Graveyard Cleanup", # 1 quest name
"Britain Graveyard", #1 region
"Kill", #1 type
"Easy", #1 difficulty
"Available", #1 status
"Description: Give rest to the ancients living in the Graveyard", # 1 quest  description
"Accept",
"The Exiled Ones", #2 quest name
"Exile", #2 region
"Collect", #2 type
"Easy", #2 difficulty
"Available", #2 status
"Description: Destroy the armament barrels found in Exile to prevent a revolution", # 2 quest description
"Accept",
"City Cleanup",
"Britain",
"Kill",
"Easy",
"Available",
"Description: Kill giant rat vermins roaming Britain city, it stinks!",
"Accept",
"Simply Gross",
"Humility",
"Kill",
"Easy",
"Available",
"Description: Slay the bog things contaminating the swamp of Humility Shrine",
"Accept",
"Vermin to the North",
"Gnoll Island",
"Kill",
"Easy",
"Available",
"Description: Exterminate the creatures living on the island north of Britain",
"Accept",
"Next Page"
"""
# ===== Utilities =====

def pause_ms(ms):
    Misc.Pause(int(ms + random.randint(0, JITTER_MS)))

def to_json(obj, indent=4, _level=0):
    sp = ' ' * (indent * _level)
    if isinstance(obj, dict):
        items = []
        for k, v in obj.items():
            items.append(f'{sp}    "{str(k)}": {to_json(v, indent, _level+1)}')
        return '{\n' + ',\n'.join(items) + f'\n{sp}' + '}'
    elif isinstance(obj, list):
        items = [to_json(i, indent, _level+1) for i in obj]
        return '[\n' + ',\n'.join(' ' * (indent * (_level+1)) + i for i in items) + f'\n{sp}]'
    elif isinstance(obj, str):
        return '"' + obj.replace('"', '\\"') + '"'
    elif obj is True:
        return 'true'
    elif obj is False:
        return 'false'
    elif obj is None:
        return 'null'
    else:
        return str(obj)

def debug_message(msg, color=68):
    if DEBUG_TO_INGAME_MESSAGE:
        try:
            Misc.SendMessage(f"[CraftCrawler] {msg}", color)
        except Exception:
            print(f"[CraftCrawler] {msg}")

def log_debug(msg, level=1):
    if DEBUG_MODE and level <= DEBUG_LEVEL:
        try:
            Misc.SendMessage("[DEBUG] " + str(msg), 115)
        except Exception:
            try:
                print("[DEBUG] " + str(msg))
            except Exception:
                pass

def adj_pause(ms):
    try:
        ms = int(ms)
    except Exception:
        return 100
    if DEBUG_MODE:
        return max(50, int(ms * 0.6))
    return ms

def jitter_ms(a, b):
    try:
        import random as _r
        return _r.randint(a, b)
    except Exception:
        return 0

def send_action_and_wait(gid, btn, wait_ms=CLICK_PAUSE_MS):
    log_debug("SendAction gid {} btn {}".format(hex(gid) if gid else gid, btn), 2)
    try:
        Gumps.SendAction(gid, btn)
    except Exception:
        return gid
    pause_ms(adj_pause(wait_ms) + jitter_ms(25, 60))
    try:
        ng = Gumps.CurrentGump()
    except Exception:
        ng = 0
    log_debug("After SendAction: new gid {}".format(hex(ng) if ng else ng), 2)
    return ng or gid

def navigate_to_available_page_index(target_index):
    """Open the Available page and navigate to the exact target page index by clicking NEXT target_index times.
    Returns the current gump id or 0 if navigation failed.
    """
    gid = go_to_available_page()
    if gid == 0:
        return 0
    if target_index <= 0:
        return gid
    for _ in range(target_index):
        gid = send_action_and_wait(gid, BUTTON_NEXT)
        if gid == 0:
            return 0
        pause_ms(adj_pause(PAGE_RESET_PAUSE_MS))
    return gid

def snap_text_lines():
    try:
        lines = Gumps.LastGumpGetLineList()
        if not lines:
            return []
        out = []
        for ln in lines:
            try:
                t = str(ln)
            except Exception:
                t = ""
            out.append(t.strip())
        return out
    except Exception:
        return []

def wait_for_lines_change(prev_lines, timeout_ms=3500):
    """Poll gump text lines until they differ from prev_lines or timeout.
    Returns tuple: (changed, new_lines)
    """
    start = int(time.time() * 1000)
    prev = prev_lines or []
    while int(time.time() * 1000) - start < timeout_ms:
        cur = snap_text_lines()
        if cur and cur != prev:
            return True, cur
        pause_ms(LOOP_PAUSE_MS)
    return False, snap_text_lines()

def wait_for_stable_lines(initial_lines, settle_ms=600, max_wait_ms=2000):
    """After a change is detected, wait until the lines stabilize for settle_ms or until max_wait_ms is reached."""
    start = int(time.time() * 1000)
    last = initial_lines or []
    stable_start = None
    while int(time.time() * 1000) - start < max_wait_ms:
        cur = snap_text_lines()
        if cur == last:
            if stable_start is None:
                stable_start = int(time.time() * 1000)
            if int(time.time() * 1000) - stable_start >= settle_ms:
                return cur
        else:
            last = cur
            stable_start = None
        pause_ms(LOOP_PAUSE_MS)
    return snap_text_lines()

def click_probe_and_collect(gid, btn, baseline_lines):
    """Click a probe button and wait for either gump id or text lines to change.
    Returns (new_gid, detail_lines or None).
    """
    log_debug(f"Probing button {btn} from gid {hex(gid) if gid else gid}", 2)
    try:
        Gumps.SendAction(gid, btn)
    except Exception:
        return gid, None
    # Initial small pause
    pause_ms(adj_pause(ITEM_BUTTON_CLICK_PAUSE_MS))
    # Poll for either gid change or line change, whichever comes first
    poll_start = int(time.time() * 1000)
    ng = gid
    changed = False
    new_lines = None
    while int(time.time() * 1000) - poll_start < adj_pause(6500):
        try:
            cur_gid = Gumps.CurrentGump()
        except Exception:
            cur_gid = 0
        cur_lines = snap_text_lines()
        if cur_gid and cur_gid != gid:
            ng = cur_gid
            new_lines = cur_lines
            changed = True
            break
        # Treat line changes or presence of detail anchors as a change
        low_join = " ".join([x.lower() for x in (cur_lines or [])])
        has_detail_hint = any(tok in low_join for tok in DETAIL_TEXT_HINTS)
        if cur_lines and (cur_lines != (baseline_lines or []) or has_detail_hint):
            ng = cur_gid or gid
            new_lines = cur_lines
            changed = True
            break
        pause_ms(LOOP_PAUSE_MS)
    # If changed, let the content stabilize a bit before returning
    if changed:
        new_lines = wait_for_stable_lines(new_lines, settle_ms=900, max_wait_ms=2500)
        # Briefly hold the detail gump open to avoid racing back too quickly
        pause_ms(adj_pause(HOLD_DETAIL_MS))
    else:
        # Fallback: one more longer wait cycle in case shard/UI is slow
        changed2, new_lines2 = wait_for_lines_change(baseline_lines, timeout_ms=adj_pause(4500))
        if changed2:
            new_lines = wait_for_stable_lines(new_lines2, settle_ms=900, max_wait_ms=2500)
            changed = True
            pause_ms(adj_pause(HOLD_DETAIL_MS))
    log_debug(
        f"After probe btn {btn}: gid {hex(ng) if ng else ng}, changed={changed}, lines={len(new_lines or [])}",
        1,
    )
    # Emit a small preview of lines for debugging
    if DEBUG_MODE and (new_lines or []):
        preview = ", ".join((new_lines[:5] if len(new_lines) > 5 else new_lines))
        log_debug(f"Detail preview (btn {btn}): {preview}", 2)
    return (ng or gid), (new_lines if changed else None)

def is_confirm_gump(gid, lines=None):
    if gid in CONFIRM_GUMP_IDS:
        return True
    try:
        arr = lines or snap_text_lines()
        low = " ".join([x.lower() for x in arr])
        return any(tok in low for tok in CONFIRM_TEXT_HINTS)
    except Exception:
        return False

def cancel_confirmation_if_present(gid):
    if gid == 0:
        return False
    if not is_confirm_gump(gid):
        return False
    log_debug("Confirmation detected on gid {}; attempting cancel".format(hex(gid)))
    try:
        try:
            Gumps.SendAdvancedAction(gid, 0, [0], [], [])
        except Exception:
            pass
        pause_ms(adj_pause(150))
        try:
            Gumps.SendAdvancedAction(gid, 0, [2], [], [])
        except Exception:
            pass
        pause_ms(adj_pause(200))
    except Exception:
        pass
    return True

def open_quest_gump():
    try:
        try:
            Gumps.ResetGump()
        except Exception:
            pass
        pause_ms(adj_pause(150))
        log_debug("Using quest giver serial {}".format(hex(QUEST_GIVER_SERIAL)))
        Mobiles.UseMobile(QUEST_GIVER_SERIAL)
        # Attempt wait by hint, fallback to current
        try:
            if Gumps.WaitForGump(BASE_GUMP_ID_HINT, WAIT_GUMP_MS):
                return BASE_GUMP_ID_HINT
        except Exception:
            pass
        try:
            g = Gumps.CurrentGump()
            return g or 0
        except Exception:
            return 0
    except Exception:
        return 0

def go_to_available_page():
    gid = wait_for_gump(1000)
    if gid == 0:
        gid = open_quest_gump()
        if gid == 0:
            return 0
    gid = send_action_and_wait(gid, BUTTON_AVAILABLE)
    log_debug("Navigated to Available page; gid {}".format(hex(gid) if gid else gid))
    return gid

# ===== Gump helpers =====

def wait_for_gump(timeout_ms=4000):
    start = int(time.time() * 1000)
    while int(time.time() * 1000) - start < timeout_ms:
        try:
            if Gumps.HasGump():
                gid = Gumps.CurrentGump()
                if gid != 0:
                    return gid
        except Exception:
            pass
        pause_ms(LOOP_PAUSE_MS)
    return 0

def snap_gump_to_entry(gid):
    entry = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
        'gump_id_decimal': gid,
        'gump_id_hex': hex(gid),
        'text_lines': []
    }

    # text
    try:
        tl = Gumps.LastGumpGetLineList()
        if tl:
            entry['text_lines'] = list(tl)
    except Exception:
        pass

    return entry



def extract_base_quests(lines):
    """Extract base quest info from the Available Quests page lines.
    Expected headers: Quest Name, Region, Type, Difficulty, Status
    Returns list of dicts: {name, region, type, difficulty, status, description}
    """
    if not lines:
        return []
    L = [str(x).strip() for x in lines]
    # Find header block indices
    header_keys = ["Quest Name", "Region", "Type", "Difficulty", "Status"]
    header_idx = -1
    for i in range(len(L) - len(header_keys) + 1):
        window = [L[i + k] for k in range(len(header_keys))]
        if all(window[k].lower() == header_keys[k].lower() for k in range(len(header_keys))):
            header_idx = i
            break
    if header_idx == -1:
        return []
    # Start reading after the Status header
    i = header_idx + len(header_keys)
    quests = []
    sentinel_terms = {"next page", "active quests", "completed quests"}
    while i < len(L):
        low = L[i].lower()
        if low in sentinel_terms:
            break
        # Need at least 5 fields for a quest row
        if i + 4 >= len(L):
            break
        name = L[i].strip(); region = L[i+1].strip(); qtype = L[i+2].strip(); diff = L[i+3].strip(); status = L[i+4].strip()
        rec = {
            "name": name,
            "region": region,
            "type": qtype,
            "difficulty": diff,
            "status": status,
        }
        i += 5
        # Optional description follows, starting with "Description:"; may be followed by an "Accept" token
        if i < len(L) and L[i].lower().startswith("description:"):
            rec["description"] = L[i]
            i += 1
        if i < len(L) and L[i].lower() == "accept":
            i += 1
        quests.append(rec)
    return quests

def capture_detail_screenshot(page_index, button_id, tag="quest_detail"):
    """Capture a 'screenshot' artifact for the current detail gump.

    Implementation note: If the client API doesn't expose a bitmap capture, we
    persist the stabilized gump text lines to a uniquely named file. This keeps a
    durable artifact per detail while honoring requested delays.
    Returns the relative file path of the saved artifact.
    """
    debug_message(f"[detail] Capture requested: page={page_index}, btn={button_id}, tag={tag}", 94)
    # Respect delay to allow UI to fully render
    pause_ms(adj_pause(DETAIL_SCREENSHOT_DELAY_MS))

    # Trigger real client screenshot via Razor Enhanced
    try:
        Misc.CaptureNow()
        debug_message("[detail] Misc.CaptureNow() invoked", 63)
    except Exception as e:
        debug_message(f"[detail] Misc.CaptureNow() failed: {e}", 33)

    # Snapshot lines as a fallback artifact
    lines = snap_text_lines()
    try:
        scripts_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(scripts_dir)
        data_dir = os.path.join(project_root, 'data')
        shots_dir = os.path.join(data_dir, 'screenshots')
        if not os.path.isdir(shots_dir):
            os.makedirs(shots_dir, exist_ok=True)
        ts = time.strftime('%Y%m%d%H%M%S', time.localtime())
        fname = f"{tag}_p{page_index}_b{button_id}_{ts}.txt"
        fpath = os.path.join(shots_dir, fname)
        with codecs.open(fpath, 'w', 'utf-8') as fh:
            for ln in (lines or []):
                try:
                    fh.write(str(ln) + "\n")
                except Exception:
                    fh.write("\n")
        # Return path relative to data/ for portability in logs
        rel_path = os.path.join('data', 'screenshots', fname)
        debug_message(f"[detail] Saved artifact to {rel_path}", 63)
        return rel_path
    except Exception as e:
        debug_message(f"[detail] Failed to save artifact: {e}", 33)
        return None

def crawl_detail_for_current_page(gid, page_index, baseline_lines):
    """Probe detail buttons for the current page and collect either text lines or request screenshots.
    Returns a list of {button, detail:{raw|screenshot}} entries.
    """
    details = []
    lines = list(baseline_lines or [])
    for btn in range(PROBE_BUTTON_MIN, PROBE_BUTTON_MAX + 1):
        if btn in (BUTTON_PREV, BUTTON_NEXT, BUTTON_AVAILABLE):
            continue
        # Determine which page this button likely belongs to (buttons increment across pages)
        try:
            target_page = max(0, int((btn - PROBE_BUTTON_MIN) // ITEMS_PER_PAGE))
        except Exception:
            target_page = page_index
        # Ensure we are positioned on the correct Available page before probing
        gid = navigate_to_available_page_index(target_page)
        if gid == 0:
            debug_message("[detail] Lost Available page; stopping detail scan for this page", 33)
            break
        # Click candidate button and see if we got a different gump with detail text
        new_gid = send_action_and_wait(gid, btn)
        detail_lines = None
        opened_detail = (new_gid != 0 and new_gid != gid)
        if opened_detail:
            pause_ms(adj_pause(HOLD_DETAIL_MS))
            try:
                detail_lines = Gumps.LastGumpGetLineList()
            except Exception:
                detail_lines = None
        if new_gid == 0:
            # Detail gump failed to open or the window closed; skip any capture
            debug_message(f"[detail] Button {btn} did not open a gump; skipping capture", 47)
            continue
        if DETAIL_CAPTURE_MODE == "lines":
            if opened_detail and detail_lines:
                details.append({"button": btn, "detail": {"raw": detail_lines}})
            elif opened_detail:
                pause_ms(adj_pause(HOLD_DETAIL_MS))
                snapshot_lines = snap_text_lines()
                details.append({"button": btn, "detail": {"raw": snapshot_lines}})
            # Return to the target page for subsequent probes
            gid = navigate_to_available_page_index(target_page)
            pause_ms(adj_pause(PAGE_RESET_PAUSE_MS))
        elif DETAIL_CAPTURE_MODE == "screenshot":
            if opened_detail:
                shot = capture_detail_screenshot(page_index, btn)
                details.append({"button": btn, "detail": {"screenshot": shot}})
            # Return to the target page for subsequent probes
            gid = navigate_to_available_page_index(target_page)
            pause_ms(adj_pause(PAGE_RESET_PAUSE_MS))
        else:
            gid = navigate_to_available_page_index(target_page)
            pause_ms(adj_pause(PAGE_RESET_PAUSE_MS))
    return details

def crawl_available_pages_with_details(max_pages=9):
    """Optional pass to collect detail info per page. Saves a separate JSON file with detail entries.
    Does not alter the base crawl JSON. Use RUN_DETAIL_SCAN to control execution.
    """
    gid = go_to_available_page()
    if gid == 0:
        debug_message("Failed to open Available page for detail scan", 33)
        return
    seen = set()
    all_details = {
        "session_start": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
        "mode": DETAIL_CAPTURE_MODE,
        "pages": []
    }
    page_index = 0
    for _ in range(MAX_PAGES):
        if page_index >= max_pages:
            break
        lines = snap_text_lines()
        sig = "|".join(lines)[:4096]
        if sig in seen:
            break
        seen.add(sig)
        page_details = crawl_detail_for_current_page(gid, page_index, lines)
        all_details["pages"].append({
            "index": page_index,
            "gump_id": hex(gid),
            "details": page_details,
        })
        gid = send_action_and_wait(gid, BUTTON_NEXT)
        if gid == 0:
            break
        page_index += 1
        pause_ms(adj_pause(PAGE_RESET_PAUSE_MS))
    # Save separate detail file
    try:
        scripts_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(scripts_dir)
        data_dir = os.path.join(project_root, 'data')
        if not os.path.isdir(data_dir):
            os.makedirs(data_dir, exist_ok=True)
        dt = time.strftime('%Y%m%d%H%M%S', time.localtime())
        filename = f"gump_daily_quests_{DETAIL_OUTPUT_SUFFIX}_{dt}.json"
        file_path = os.path.join(data_dir, filename)
        with codecs.open(file_path, 'w', 'utf-8') as fh:
            json.dump(all_details, fh, indent=2)
        debug_message(f"Wrote detail capture to data/{filename}", 63)
    except Exception as e:
        debug_message(f"Failed to save detail capture: {e}", 33)

def crawl_once(max_items=1):
    """Daily Quest crawl: scan Available pages and extract base info across paginated results.
    Detail probing is disabled in this mode; we only parse base rows using NEXT navigation.
    """
    results = {
        "session_start": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
        "quest_giver_serial": hex(QUEST_GIVER_SERIAL),
        "base_gump_hint": hex(BASE_GUMP_ID_HINT),
        "pages": [],
        "stats": {
            "button_clicks": 0,
            "confirm_canceled": 0,
            "detail_pages": 0,
            "pages_scanned": 0,
        }
    }

    gid = open_quest_gump()
    if gid == 0:
        debug_message("Failed to open quest giver gump", 33)
        return results

    gid = go_to_available_page()
    if gid == 0:
        debug_message("Failed to navigate to Available Quests", 33)
        return results

    seen_pages = []
    page_index = 0

    for _ in range(MAX_PAGES):
        if page_index >= max_items:
            break
        lines = snap_text_lines()
        page_sig = "|".join(lines)[:4096]
        if page_sig in seen_pages:
            debug_message("Detected repeated page; stopping page scan", 47)
            break
        seen_pages.append(page_sig)

        page_record = {
            "index": page_index,
            "gump_id": hex(gid),
            "quests": extract_base_quests(lines),
        }
        # Include raw list lines only when OUTPUT_BASE is True
        if OUTPUT_BASE:
            page_record["list"] = {"raw": lines}
        results["stats"]["pages_scanned"] += 1

        results["pages"].append(page_record)
        gid = send_action_and_wait(gid, BUTTON_NEXT)
        if gid == 0:
            break
        page_index += 1
        pause_ms(adj_pause(PAGE_RESET_PAUSE_MS))

    return results

def save_results(results):
    if not DEBUG_TO_JSON:
        return
    try:
        scripts_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(scripts_dir)
        data_dir = os.path.join(project_root, 'data')
        if not os.path.isdir(data_dir):
            try:
                os.makedirs(data_dir)
            except Exception:
                pass
        dt = time.strftime('%Y%m%d%H%M%S', time.localtime())
        filename = f"gump_daily_quests_{dt}.json"
        file_path = os.path.join(data_dir, filename)
        # Shape output: when OUTPUT_BASE is False and OUTPUT_ITEM is True,
        # save a flat list of quests only.
        out_obj = results
        if not OUTPUT_BASE and OUTPUT_ITEM:
            flat = []
            try:
                for pg in results.get("pages", []):
                    for q in pg.get("quests", []) or []:
                        flat.append(q)
            except Exception:
                pass
            out_obj = flat
        with codecs.open(file_path, 'w', 'utf-8') as fh:
            json.dump(out_obj, fh, indent=2)
        debug_message(f"Wrote daily quest data to data/{filename}", 63)
    except Exception as e:
        debug_message(f"Failed to save results: {e}", 33)

def main():
    results = crawl_once(MAX_ITEMS_TO_EXTRACT)
    save_results(results)
    # Optional pass: open each quest's extra info button per page and capture (screenshots by default)
    if RUN_DETAIL_SCAN:
        try:
            crawl_available_pages_with_details(max_pages=MAX_PAGES)
        except Exception as e:
            debug_message(f"Detail scan failed: {e}", 33)

if __name__ == "__main__":
    main()
