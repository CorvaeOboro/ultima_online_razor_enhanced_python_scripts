"""
Development Crafting Tester — a Razor Enhanced Python Script for Ultima Online

test crafting recipes in game , verify the data written by DEV_crafting_gump_crawler.py
because the text_list is unsorted the data may have errors , this script attempts to check

Overview:
- Parse the latest crafting gump crawl JSON from `data/gump_crafting_*.json`.
- Build a proposed test plan per recipe (Target Item, Category, Item Graphic ID, Skill, Materials,
  and the json info for the gump Category button ID and the Target Item's Make/Info button IDs).
- Test verification in-game to attempt crafting eligible recipes, then write
  VERIFIED and FAILURE results into `data/` JSON files.

Modes:
1) Plan-only (default outside UO/Razor Enhanced):
   - Generates `data/crafting_test_plan_<timestamp>.json` and exits.
2) Live test (only if running in Razor Enhanced):
   - Navigates the Cooking crafting gump, attempts MAKE NOW, and records results.

Cooking gump assumptions (shard-agnostic defaults):
- Tool: Skillet `0x097F` in backpack opens the Cooking gump.
- Category buttons: mapped for Cooking (e.g., Magical Foods, Ingredients, ...).
- Item info buttons: left list index pattern `3, 10, 17, ...` (start=3, step=7).
- MAKE NOW candidate button IDs: `[4, 5, 6]` (tries in order; varies by shard).

Skip previously verified:
- `SKIP_VERIFIED`: if True, recipes that were already VERIFIED are skipped.
- `VERIFIED_JSON_PATH`: optional explicit path to a VERIFIED JSON; if empty, the script
  auto-picks the latest `data/crafting_verified_*.json` when `SKIP_VERIFIED` is enabled.

Outputs:
- Plan: `data/crafting_test_plan_<timestamp>.json`
- Live verified: `data/crafting_verified_<timestamp>.json`
- Live failures: `data/crafting_failures_<timestamp>.json`

VERSION::20250819
"""
import json
import os
import sys
import time
from collections import defaultdict
import re

DEBUG_MODE = True # - DEBUG_MODE: controls whether debug_message prints to in-game/console
# Skip recipes already verified in an external VERIFIED json
SKIP_VERIFIED = True
RAZOR_MODE = True # Manual toggle: set True when running inside Razor Enhanced (in-game)
DRY_RUN = False # navigate but do not press MAKE 
MAX_TESTS = 5 # safety cap for live attempts per run
# Controls whether to show debug logs for SKIPPED recipes (materials/backpack comparisons)
SHOW_SKIPPED_DEBUG = False

# One-time backpack snapshot used during planning/live checks to avoid repeated scans
BACKPACK_SNAPSHOT = {
    'by_name': defaultdict(int),  # normalized name -> count
    'by_id': defaultdict(int),    # graphic id (int) -> total amount
    'by_name_fuzzy': defaultdict(int),  # fuzzy key -> total amount
    'built': False,
}

VERIFIED_JSON_PATH = ""  # optional override; if empty and SKIP_VERIFIED, auto-pick latest crafting_verified_*.json in data/

# Borrow patterns from DEV_crafting_gump_crawler.py
# Category buttons pattern for Cooking (Skillet)
COOKING_CATEGORIES = {
    "Magical Foods": 1,
    "Ingredients": 8,
    "Preparations": 15,
    "Baking": 22,
    "Barbecue": 29,
    "Chocolatiering": 36,
    "Meals": 43,
}

# Left-side item info buttons: start at 3, step by 7
ITEM_BUTTON_START = 3
ITEM_BUTTON_STEP = 7
ITEM_BUTTON_MAX = 120

# Exit/cancel button id
EXIT_BUTTON_ID = 0

# Tool IDs: default to Skillet for Cooking
TOOL_ITEM_IDS = [0x097F]

# Delays (ms)
LOOP_PAUSE_MS = 150
BUTTON_CLICK_PAUSE_MS = 300
ITEM_INFO_RENDER_PAUSE_MS = 600
POST_MAKE_WAIT_MS = 1500
# Delay between separate craft attempts during the live loop
BETWEEN_CRAFTS_MS = 1000
# Name lookup tuning
NAME_LOOP_THROTTLE_MS = 40

def debug_message(message, color=90):
    try:
        if DEBUG_MODE:
            # Prefix to distinguish tester logs
            Misc.SendMessage(f"[DEV_CRAFT_TEST] {message}", color)
    except Exception:
        # Fallback to stdout
        print(f"[DEV_CRAFT_TEST] {message}")

# Material name remapping: recipe short names -> actual backpack normalized names
MATERIAL_NAME_REMAP = {
    'flour': 'open sack of flour',
    'raw ribs': 'cut of raw ribs',
    'sack of flour': 'open sack of flour',
    'bag of flour': 'open sack of flour',
    'flour sack': 'open sack of flour',
    'water': 'pitcher of water',
    'water pitcher': 'pitcher of water',
    'pitcher water': 'pitcher of water',
    'ball of dough': 'dough',
    'dough ball': 'dough',
    'honey': 'jar of honey',
    'jar honey': 'jar of honey',
    'honey jar': 'jar of honey',
    'jar of honey': 'jar of honey',
    'raw fish steaks': 'raw fish steak',
    'raw fish steak': 'raw fish steak',
}

# Fuzzy normalization helpers for food/raw items
_STOPWORDS = set([
    'a','an','the','of','cut','slab','portion','piece','pieces','pack','stack',
    'uncooked', 'unbaked', 'unprepared',
    # containers/forms that shouldn't affect fuzzy intent
    'ball','pitcher','jug','bottle','mug','cup','sack','bag'
])
_PRESERVE = set(['raw','cooked','fish','steak','ribs','rib','chicken','leg','legs','bacon','sausage'])

def _singularize(word: str) -> str:
    w = word
    if len(w) > 3 and w.endswith('s'):
        return w[:-1]
    return w

def name_to_fuzzy_key(name: str) -> str:
    try:
        n = (name or '').strip().lower()
        if not n or n == 'unknown':
            return ''
        # remove punctuation
        n = re.sub(r"[^a-z0-9\s]", " ", n)
        toks = [t for t in n.split() if t]
        out = []
        for t in toks:
            # drop numeric-only tokens
            if t.isdigit():
                continue
            if t in _STOPWORDS:
                continue
            # keep 'raw' and 'cooked' tokens, singularize common nouns
            if t not in ('raw','cooked'):
                t = _singularize(t)
            out.append(t)
        if not out:
            return ''
        out.sort()
        return ' '.join(out)
    except Exception:
        return ''

# Small helpers
def fmt_hex4(v: int) -> str:
    try:
        return f"0x{int(v)&0xFFFF:04X}"
    except Exception:
        return "0x0000"
    
def _to_int_id(v):
    """Parse an id that may be int, decimal string, or hex string like '0x1083'.
    Returns int or None on failure.
    """
    try:
        if v is None:
            return None
        if isinstance(v, int):
            return v
        s = str(v).strip()
        if s.lower().startswith('0x'):
            return int(s, 16)
        return int(s)
    except Exception:
        return None

# ---------- Inventory auditing helpers ----------

def _name_norm(n: str) -> str:
    return (n or '').strip().lower()

def _normalize_material_name_global(nm: str) -> str:
    n = _name_norm(nm)
    if not n:
        return n
    return MATERIAL_NAME_REMAP.get(n, n)

def _collect_backpack_counts_by_key():
    """Return a dict keyed by (id, hue, name_norm) -> qty for current backpack."""
    counts = defaultdict(int)
    try:
        items = iter_player_backpack_items()
        for it in (items or []):
            try:
                iid = int(it.ItemID)
                try:
                    hue = int(it.Hue)
                except Exception:
                    try:
                        hue = int(it.Color)
                    except Exception:
                        hue = 0
                # Normalize using inspector-style naming to strip quantity prefixes
                raw_name = get_item_name(it, amount_hint=getattr(it, 'Amount', 1))
                name = _name_norm(MATERIAL_NAME_REMAP.get((raw_name or '').strip().lower(), (raw_name or '').strip().lower()))
                qty = int(getattr(it, 'Amount', 1) or 1)
                counts[(iid, hue, name)] += max(1, qty)
            except Exception:
                continue
    except Exception:
        pass
    return counts

def _diff_inventory(before: dict, after: dict) -> dict:
    """Compute delta map (id,hue,name)->(after-before)."""
    keys = set(before.keys()) | set(after.keys())
    delta = {}
    for k in keys:
        delta[k] = int(after.get(k, 0)) - int(before.get(k, 0))
    return delta

def _counts_to_list(counts: dict) -> list:
    """Serialize inventory count map (id,hue,name)->qty into a stable list of dicts.
    Each element: {name, id_hex, hue_hex, qty}
    """
    out = []
    try:
        for (iid, hue, name), qty in (counts or {}).items():
            out.append({
                'name': name,
                'id_hex': fmt_hex4(int(iid)),
                'hue_hex': fmt_hex4(int(hue)),
                'qty': int(qty),
            })
        # Stable ordering for readability
        out.sort(key=lambda r: (r.get('name') or '', r.get('id_hex') or '', r.get('hue_hex') or ''))
    except Exception:
        pass
    return out

def _sort_change_list(arr: list) -> list:
    """Return a stably sorted copy of a change list by name, id, hue."""
    try:
        return sorted(arr or [], key=lambda r: (
            (r.get('name') or ''),
            (r.get('id_hex') or ''),
            (r.get('hue_hex') or ''),
        ))
    except Exception:
        return arr or []

def _filter_deltas_for_materials(delta: dict, materials: list) -> list:
    """Return list of consumed entries matching materials with qty<0.
    Each entry: {name,id_hex,hue_hex,qty,name_key}
    """
    out = []
    # Build material matchers
    mat_ids = set()
    mat_names = set()
    mat_fuzzy = set()
    for m in (materials or []):
        mid = m.get('id')
        if mid is not None:
            try:
                mid_i = int(mid, 16) if isinstance(mid, str) and mid.startswith('0x') else int(mid)
                mat_ids.add(mid_i)
            except Exception:
                pass
        nm = _normalize_material_name_global(m.get('name'))
        if nm:
            mat_names.add(nm)
            fk = name_to_fuzzy_key(nm)
            if fk:
                mat_fuzzy.add(fk)
    for (iid, hue, name), q in delta.items():
        if q >= 0:
            continue
        if (iid in mat_ids) or (name in mat_names):
            out.append({
                'name': name,
                'id_hex': fmt_hex4(iid),
                'hue_hex': fmt_hex4(hue),
                'qty': q,  # negative
            })
            continue
        # Fuzzy fallback on names in delta to catch variants/containers
        try:
            fk = name_to_fuzzy_key(name)
            if fk and fk in mat_fuzzy:
                out.append({
                    'name': name,
                    'id_hex': fmt_hex4(iid),
                    'hue_hex': fmt_hex4(hue),
                    'qty': q,  # negative
                })
        except Exception:
            pass
    return out

def _filter_deltas_for_product(delta: dict, product_id: int) -> list:
    out = []
    for (iid, hue, name), q in delta.items():
        if q <= 0:
            continue
        if int(iid) == int(product_id):
            out.append({
                'name': name,
                'id_hex': fmt_hex4(iid),
                'hue_hex': fmt_hex4(hue),
                'qty': q,  # positive
            })
    return out

def _all_negative_deltas(delta: dict) -> list:
    """Return all negative deltas as {name,id_hex,hue_hex,qty} without recipe filtering."""
    out = []
    try:
        for (iid, hue, name), q in (delta or {}).items():
            if int(q) < 0:
                out.append({
                    'name': name,
                    'id_hex': fmt_hex4(int(iid)),
                    'hue_hex': fmt_hex4(int(hue)),
                    'qty': int(q),
                })
    except Exception:
        pass
    return out
        
# ---------- Razor Enhanced object access helpers ----------

def iter_player_backpack_items() -> list:
    """Return list of items in the backpack using the inspector's approach."""
    try:
        bp = Player.Backpack
        if not bp:
            return []
        items = bp.Contains
        return list(items) if items else []
    except Exception:
        return []

def build_backpack_snapshot(max_items: int = 1000):
    """Build a snapshot of backpack contents by normalized name and by graphic id.
    Uses direct access to Player.Backpack.Contains and get_item_name once at start.
    """
    BACKPACK_SNAPSHOT['by_name'].clear()
    BACKPACK_SNAPSHOT['by_id'].clear()
    BACKPACK_SNAPSHOT['by_name_fuzzy'].clear()
    BACKPACK_SNAPSHOT['built'] = False
    try:
        items = iter_player_backpack_items()
        n = 0
        for it in items:
            try:
                # by-id
                gid = int(it.ItemID)
                amt = int(it.Amount or 1)
                BACKPACK_SNAPSHOT['by_id'][gid] += max(1, amt)
                # by-name (normalized)
                nm = get_item_name(it, amount_hint=it.Amount)
                norm = (nm or '').strip().lower()
                if norm:
                    norm = MATERIAL_NAME_REMAP.get(norm, norm)
                if norm and norm != 'unknown':
                    BACKPACK_SNAPSHOT['by_name'][norm] += max(1, amt)
                    fkey = name_to_fuzzy_key(norm)
                    if fkey:
                        BACKPACK_SNAPSHOT['by_name_fuzzy'][fkey] += max(1, amt)
                n += 1
                if n >= max_items:
                    break
                _pause_ms(NAME_LOOP_THROTTLE_MS)
            except Exception:
                continue
        BACKPACK_SNAPSHOT['built'] = True
        debug_message(f"Built backpack snapshot: {len(BACKPACK_SNAPSHOT['by_id'])} ids, {len(BACKPACK_SNAPSHOT['by_name'])} names, {len(BACKPACK_SNAPSHOT['by_name_fuzzy'])} fuzzy")
    except Exception:
        pass

def _consume_materials_in_snapshot(materials):
    """Subtract material quantities from the global snapshot after a successful craft.
    Supports both id-based and name-based entries.
    """
    if not BACKPACK_SNAPSHOT.get('built'):
        return
    try:
        for m in (materials or []):
            q = int(m.get('qty') or 1)
            # Prefer id -> support either 'id' (int/hex) or 'id_hex'
            if m.get('id') is not None or m.get('id_hex') is not None:
                try:
                    raw_id = m.get('id') if m.get('id') is not None else m.get('id_hex')
                    mid = int(raw_id, 16) if isinstance(raw_id, str) and str(raw_id).startswith('0x') else int(raw_id)
                    BACKPACK_SNAPSHOT['by_id'][int(mid)] = max(0, int(BACKPACK_SNAPSHOT['by_id'].get(int(mid), 0)) - max(1, q))
                    continue
                except Exception:
                    pass
            # Name-based decrement (with remap and fuzzy key)
            nm = (m.get('name') or '').strip().lower()
            if nm:
                nm = MATERIAL_NAME_REMAP.get(nm, nm)
                BACKPACK_SNAPSHOT['by_name'][nm] = max(0, int(BACKPACK_SNAPSHOT['by_name'].get(nm, 0)) - max(1, q))
                fk = name_to_fuzzy_key(nm)
                if fk:
                    BACKPACK_SNAPSHOT['by_name_fuzzy'][fk] = max(0, int(BACKPACK_SNAPSHOT['by_name_fuzzy'].get(fk, 0)) - max(1, q))
    except Exception:
        pass

def _add_products_to_snapshot(produced: list):
    """Increase snapshot counts for produced items (list of {name,id_hex,qty}).
    Ensures by_id, by_name, and by_name_fuzzy are updated so follow-up recipes see them.
    """
    if not BACKPACK_SNAPSHOT.get('built'):
        return
    try:
        for p in (produced or []):
            q = int(p.get('qty') or 1)
            if q <= 0:
                continue
            # by id
            try:
                raw_id = p.get('id') if p.get('id') is not None else p.get('id_hex')
                if raw_id is not None:
                    pid = int(raw_id, 16) if isinstance(raw_id, str) and str(raw_id).startswith('0x') else int(raw_id)
                    BACKPACK_SNAPSHOT['by_id'][int(pid)] = int(BACKPACK_SNAPSHOT['by_id'].get(int(pid), 0)) + max(1, q)
            except Exception:
                pass
            # by name + fuzzy
            nm = (p.get('name') or '').strip().lower()
            if nm and nm != 'unknown':
                nm = MATERIAL_NAME_REMAP.get(nm, nm)
                BACKPACK_SNAPSHOT['by_name'][nm] = int(BACKPACK_SNAPSHOT['by_name'].get(nm, 0)) + max(1, q)
                fk = name_to_fuzzy_key(nm)
                if fk:
                    BACKPACK_SNAPSHOT['by_name_fuzzy'][fk] = int(BACKPACK_SNAPSHOT['by_name_fuzzy'].get(fk, 0)) + max(1, q)
    except Exception:
        pass

# ---------- Helpers for paths and IO ----------

def _script_root_paths():
    here = os.path.abspath(os.path.dirname(__file__))
    project_root = os.path.abspath(os.path.join(here, os.pardir))
    data_dir = os.path.join(project_root, 'data')
    return project_root, data_dir

def _find_latest_crafting_json(data_dir: str) -> str:
    if not os.path.isdir(data_dir):
        return None
    candidates = []
    for name in os.listdir(data_dir):
        if not name.lower().endswith('.json'):
            continue
        if not name.lower().startswith('gump_crafting'):
            continue
        full = os.path.join(data_dir, name)
        try:
            mtime = os.path.getmtime(full)
        except Exception:
            continue
        candidates.append((mtime, full))
    if not candidates:
        return None
    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]

def _read_json(path: str):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def _write_json(path: str, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)

def _ts():
    return time.strftime('%Y%m%d%H%M%S', time.localtime())

# ---------- VERIFIED imports (skip already verified) ----------

def _find_latest_verified_json(data_dir: str) -> str:
    if not os.path.isdir(data_dir):
        return None
    candidates = []
    for name in os.listdir(data_dir):
        if not name.lower().endswith('.json'):
            continue
        if not name.lower().startswith('crafting_verified_'):
            continue
        full = os.path.join(data_dir, name)
        try:
            mtime = os.path.getmtime(full)
        except Exception:
            continue
        candidates.append((mtime, full))
    if not candidates:
        return None
    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]

def _test_key_from_entry(entry: dict):
    """Return a comparable key for a test entry identifying the recipe."""
    if not entry:
        return None
    tgt = str((entry.get('target_name') or '')).strip().lower()
    cat = str((entry.get('category') or '')).strip().lower()
    gid = _to_int_id(entry.get('id')) if entry.get('id') is not None else None
    return (cat, tgt, gid)

def _load_verified_keys_from_json(path: str) -> set:
    """Read an external VERIFIED json and return a set of test keys to skip.

    Supported formats:
    - List of records with {'entry': <plan_entry>, 'result': {...}, 'timestamp': ...}
    - Dict with {'tests': [...]} where each is a plan entry
    - Direct list of plan entries
    """
    keys = set()
    if not path:
        return keys
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        return keys
    # Case A: list of verified records
    if isinstance(data, list):
        for rec in data:
            ent = (rec or {}).get('entry') if isinstance(rec, dict) else None
            if ent:
                k = _test_key_from_entry(ent)
                if k:
                    keys.add(k)
                continue
            # New flattened format support: {target_name, category, product_id_hex, ...}
            if isinstance(rec, dict) and ('target_name' in rec or 'category' in rec):
                try:
                    pid_hex = rec.get('product_id_hex') or rec.get('expected_product_id_hex')
                    pid = int(pid_hex, 16) if isinstance(pid_hex, str) and pid_hex.startswith('0x') else _to_int_id(pid_hex)
                except Exception:
                    pid = None
                ent_like = {
                    'target_name': rec.get('target_name'),
                    'category': rec.get('category'),
                    'id': pid,
                }
                k = _test_key_from_entry(ent_like)
                if k:
                    keys.add(k)
                continue
            # Fallback: try treating record itself as an entry
            if isinstance(rec, dict):
                k = _test_key_from_entry(rec)
                if k:
                    keys.add(k)
        return keys
    # Case B: dict with tests
    if isinstance(data, dict):
        tests = data.get('tests') or []
        for ent in tests:
            k = _test_key_from_entry(ent)
            if k:
                keys.add(k)
    return keys

# ---------- Universal verified-by-name list (data/crafting_verified_universal.json) ----------

def _universal_verified_path(data_dir: str) -> str:
    return os.path.join(data_dir, 'crafting_verified_universal.json')

def _load_universal_verified_names(path: str) -> (list, set):
    """Return (names_list, names_lower_set). If file missing/invalid, return ([], set())."""
    try:
        if not os.path.exists(path):
            return [], set()
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if isinstance(data, list):
            names = [str((x or '')).strip() for x in data if str(x or '').strip()]
            lowers = set([n.lower() for n in names])
            return names, lowers
    except Exception:
        pass
    return [], set()

def _save_universal_verified_names(path: str, names: list):
    try:
        uniq = []
        seen = set()
        for n in (names or []):
            k = (n or '').strip()
            if not k:
                continue
            lk = k.lower()
            if lk in seen:
                continue
            seen.add(lk)
            uniq.append(k)
        uniq.sort(key=lambda s: s.lower())
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(uniq, f, ensure_ascii=False, indent=2)
    except Exception as e:
        debug_message(f"Failed saving universal verified list: {e}", 33)

def _report_verified_progress(plan: dict, data_dir: str, already_verified: set = None):
    """Minimal, non-intrusive progress summary: counts verified vs total.
    - universal_by_name: matches against data/crafting_verified_universal.json
    - external_verified_json: matches against latest VERIFIED json (or provided set)
    Output via debug_message only.
    """
    try:
        tests = plan.get('tests') or []
        total = len(tests)
        # Universal list
        uni_path = _universal_verified_path(data_dir)
        _, uni_lower = _load_universal_verified_names(uni_path)
        # External verified set
        ver_keys = already_verified
        if ver_keys is None:
            ver_keys = set()
            src_v = (VERIFIED_JSON_PATH or '').strip() or _find_latest_verified_json(data_dir)
            if src_v:
                ver_keys = _load_verified_keys_from_json(src_v)
        # Counts
        count_uni = 0
        count_ext = 0
        for ent in tests:
            tn = (ent.get('target_name') or '').strip().lower()
            if tn and tn in uni_lower:
                count_uni += 1
            if _test_key_from_entry(ent) in ver_keys:
                count_ext += 1
        debug_message(f"Verified progress: universal_by_name {count_uni}/{total}, external_verified_json {count_ext}/{total}", 68)
    except Exception:
        pass

# ---------- Gump and interaction helpers ----------

def _pause_ms(ms):
    try:
        Misc.Pause(int(ms))
    except Exception:
        time.sleep(ms / 1000.0)

def _wait_for_gump(timeout_ms=4000):
    start = int(time.time() * 1000)
    debug_message(f"Waiting for crafting gump up to {timeout_ms} ms...")
    while int(time.time() * 1000) - start < timeout_ms:
        try:
            if Gumps.HasGump():
                gid = Gumps.CurrentGump()
                if gid != 0:
                    debug_message(f"Gump detected: gid={gid}")
                    return gid
        except Exception:
            pass
        _pause_ms(LOOP_PAUSE_MS)
    debug_message("Timed out waiting for gump", 33)
    return 0

 

def _send_action(btn_id):
    try:
        gid = Gumps.CurrentGump()
        if gid:
            Gumps.SendAction(gid, int(btn_id))
            _pause_ms(BUTTON_CLICK_PAUSE_MS)
            debug_message(f"Sent gump action {btn_id}")
            return True
    except Exception:
        pass

    

def _ensure_gump_closed():
    try:
        if Gumps.HasGump():
            gid = Gumps.CurrentGump()
            if gid:
                Gumps.SendAction(gid, EXIT_BUTTON_ID)
                _pause_ms(200)
    except Exception:
        pass

def _use_crafting_tool():
    """Use a crafting tool from backpack (e.g., Skillet) to open the crafting gump."""
    try:
        items = iter_player_backpack_items()
        if not items:
            return False
        for it in items:
            try:
                if int(it.ItemID) in TOOL_ITEM_IDS:
                    debug_message(f"Using crafting tool ItemID=0x{int(it.ItemID):04X}")
                    Items.UseItem(it.Serial)
                    _pause_ms(250)
                    return True
            except Exception:
                continue
    except Exception:
        pass
    return False

def _backpack_count_by_graphic(graphic_id: int) -> int:
    count = 0
    try:
        items = iter_player_backpack_items()
        if not items:
            return 0
        for it in items:
            try:
                if int(it.ItemID) == int(graphic_id):
                    count += int(it.Amount or 1)
            except Exception:
                continue
    except Exception:
        pass
    return count

# ---------- Name normalization (copied from DEV_item_inspector) ----------

def _clean_leading_amount(name: str, amount: int) -> str:
    """Remove leading quantity prefixes like '10 Iron Ingot', '(10) Iron Ingot', '10x Iron Ingot'."""
    try:
        amt = int(amount)
    except Exception:
        return name
    if not name:
        return name
    # Primary: exact amount-based prefix removal
    if amt > 1:
        pattern = r'^\s*(?:\(|\[)?\s*' + re.escape(str(amt)) + r'\s*(?:\)|\])?\s*(?:x|×|X)?\s*[:\-*]?\s*'
        cleaned = re.sub(pattern, '', name).strip()
        if cleaned != name:
            return cleaned
    # Fallback: remove any generic leading numeric prefix regardless of amt
    generic = re.sub(r'^\s*(?:\(|\[)?\s*\d+\s*(?:\)|\])?\s*(?:x|×|X)?\s*[:\-*]?\s*', '', name).strip()
    return generic

def get_item_name(item, amount_hint=None):
    """Best-effort item name using fast paths, then props as fallback (from inspector)."""
    try:
        nm = item.Name
        if nm:
            nm = str(nm)
            amt = amount_hint if amount_hint is not None else item.Amount
            return _clean_leading_amount(nm, amt)
    except Exception:
        pass
    try:
        # First attempt: quick wait
        Items.WaitForProps(item.Serial, 400)
        props = Items.GetPropStringList(item.Serial)
        if props and len(props) > 0:
            nm = str(props[0])
            amt = amount_hint if amount_hint is not None else item.Amount
            return _clean_leading_amount(nm, amt)
        # Second attempt: trigger tooltip via single click
        Items.SingleClick(item.Serial)
        Misc.Pause(150)
        Items.WaitForProps(item.Serial, 600)
        props = Items.GetPropStringList(item.Serial)
        if props and len(props) > 0:
            nm = str(props[0])
            amt = amount_hint if amount_hint is not None else item.Amount
            return _clean_leading_amount(nm, amt)
        # Fallback to GetPropValue index 0
        name0 = Items.GetPropValue(item.Serial, 0)
        if name0:
            nm = str(name0)
            amt = amount_hint if amount_hint is not None else item.Amount
            return _clean_leading_amount(nm, amt)
    except Exception:
        pass
    return "Unknown"

def _category_to_button_id(category: str):
    if not category:
        return None
    # direct match
    bid = COOKING_CATEGORIES.get(category)
    if bid:
        return bid
    # case-insensitive match
    cl = category.strip().lower()
    for k, v in COOKING_CATEGORIES.items():
        if k.lower() == cl:
            return v
    return None

 

# ---------- Normalize crawl items ----------

def _normalize_items(json_root):
    # Case 1: already a list of items
    if isinstance(json_root, list):
        return json_root
    # Case 2: full structure with categories
    items = []
    cats = (json_root or {}).get('categories', {})
    for cat_key, cat_data in cats.items():
        for it in (cat_data.get('items') or []):
            parsed = (it or {}).get('parsed') or {}
            if parsed:
                if 'category' not in parsed:
                    parsed['category'] = cat_key
                # Carry through button ids when available on raw item
                # Common keys in crawler output: button_info, button_make
                if 'button_info' in it and 'item_info_button_id' not in parsed:
                    parsed['item_info_button_id'] = it.get('button_info')
                if 'button_make' in it and 'item_make_button_id' not in parsed:
                    parsed['item_make_button_id'] = it.get('button_make')
                items.append(parsed)
    return items

# ---------- Test planning ----------

def build_test_plan(items):
    """Build a test plan dict from normalized items.

    Each test includes:
    - target_name, category, id, skill_required, materials
    - gump_category_button (optional placeholder)
    - gump_item_make_button (optional placeholder)
    """
    plan = []
    for it in items:
        # Compute category button from known mapping when possible
        cat = it.get('category')
        cat_btn = _category_to_button_id(cat) if cat else None
        entry = {
            'target_name': it.get('name'),
            'category': cat,
            'id': it.get('id'),
            'skill_required': it.get('skill_required'),
            'materials': it.get('materials') or [],
            # Placeholders, to be filled if/when we enrich with crawler raw data
            'gump_category_button': it.get('category_button_id') or cat_btn,
            'gump_item_info_button': it.get('item_info_button_id') or it.get('button_info') or None,
            'gump_item_make_button': it.get('item_make_button_id') or it.get('button_make') or None,
        }
        # Heuristic: if info button exists and make button missing, derive make = info - 1
        if not entry.get('gump_item_make_button') and entry.get('gump_item_info_button') is not None:
            try:
                info_btn = int(entry.get('gump_item_info_button'))
                entry['gump_item_make_button'] = info_btn - 1
            except Exception:
                pass
        plan.append(entry)
    return {
        'generated_at': _ts(),
        'total_items': len(items),
        'tests': plan,
    }

# ---------- Live test execution (optional) ----------

def _player_skill_meets(skill_required):
    """Return True if player's relevant skill meets/exceeds requirement.
    We infer skill by category name; fallback True if we cannot detect.
    """
    if not RAZOR_MODE:
        return False
    try:
        # Simple heuristic: cooking category -> Cooking skill
        # Extend as needed for other crafts
        sr = float(skill_required) if skill_required is not None else 0.0
    except Exception:
        sr = 0.0
    try:
        # Default to cooking for now; adapt later using category mapping
        val = Player.GetRealSkillValue('Cooking')
        return float(val) >= sr
    except Exception:
        return True  # Don't block if API not available

def _debug_dump_backpack(max_items: int = 300):
    """Log a snapshot of backpack contents (name, id, amount)."""
    if not RAZOR_MODE:
        return
    try:
        # Mirror inspector: early guard (direct)
        try:
            _ = Player.Backpack
        except Exception:
            _ = None
        if not _:
            Misc.SendMessage("No backpack found!", 33)
            return
        items = iter_player_backpack_items()
        if not items:
            debug_message("Backpack empty or not accessible", 33)
            return
        arr = items
        debug_message(f"Backpack snapshot: {len(arr)} items (showing up to {max_items})")
        shown = 0
        for it in arr:
            try:
                name = (it.Name or '').strip()
                iid = int(it.ItemID)
                # Prefer Hue; fallback to Color
                try:
                    hue = int(it.Hue)
                except Exception:
                    try:
                        hue = int(it.Color)
                    except Exception:
                        hue = 0
                amt = int(it.Amount or 1)
                #debug_message(f" - {name} id={fmt_hex4(iid)} hue={fmt_hex4(hue)} amount={amt}")
            except Exception:
                continue
            shown += 1
            if shown >= max_items:
                break
    except Exception:
        pass

def _have_materials(materials) -> bool:
    """Check if backpack has required materials.
    Supports two modes per material entry:
    - By id (graphic) when 'id' present on material
    - Else by name (case-insensitive)
    Logs detailed diagnostics.
    """
    if not materials:
        return True

    # Build requirements
    req_by_name = defaultdict(int)
    req_by_name_fuzzy = defaultdict(int)
    req_by_id = defaultdict(int)
    def _normalize_material_name(nm: str) -> str:
        n = (nm or '').strip().lower()
        if not n:
            return n
        return MATERIAL_NAME_REMAP.get(n, n)

    for m in materials:
        q = int(m.get('qty') or 1)
        if 'id' in m and m.get('id') is not None:
            try:
                mid = int(m.get('id'), 16) if isinstance(m.get('id'), str) and m.get('id').startswith('0x') else int(m.get('id'))
                req_by_id[mid] += max(1, q)
                continue
            except Exception:
                pass
        nm = _normalize_material_name(m.get('name'))
        if nm:
            req_by_name[nm] += max(1, q)
            fk = name_to_fuzzy_key(nm)
            if fk:
                req_by_name_fuzzy[fk] += max(1, q)

    # Log requirements (only when opted in for skipped debug)
    if SHOW_SKIPPED_DEBUG:
        if req_by_id:
            debug_message(f"Req by id: {{" + ", ".join([f"0x{mid:04X}:{qty}" for mid, qty in req_by_id.items()]) + "}}")
        if req_by_name:
            debug_message(f"Req by name: {dict(req_by_name)}")

    # Ensure snapshot exists
    if not BACKPACK_SNAPSHOT.get('built'):
        build_backpack_snapshot()

    # Gather availability from snapshot (no repeated scans)
    have_by_name = {}
    if req_by_name:
        for k in req_by_name.keys():
            have_by_name[k] = int(BACKPACK_SNAPSHOT['by_name'].get(k, 0))
    have_by_name_fuzzy = {}
    if req_by_name_fuzzy:
        for k in req_by_name_fuzzy.keys():
            have_by_name_fuzzy[k] = int(BACKPACK_SNAPSHOT['by_name_fuzzy'].get(k, 0))
    have_by_id = {}
    if req_by_id:
        for k in req_by_id.keys():
            have_by_id[int(k)] = int(BACKPACK_SNAPSHOT['by_id'].get(int(k), 0))
    if SHOW_SKIPPED_DEBUG:
        if req_by_id:
            debug_message(f"Have by id: {{" + ", ".join([f"0x{mid:04X}:{qty}" for mid, qty in have_by_id.items()]) + "}}")
        if req_by_name:
            debug_message(f"Have by name: {dict(have_by_name)}")
        if req_by_name_fuzzy:
            debug_message(f"Have by fuzzy: {dict(have_by_name_fuzzy)}")

    # Evaluate
    for mid, q in req_by_id.items():
        if int(have_by_id.get(int(mid), 0)) < int(q):
            if SHOW_SKIPPED_DEBUG:
                debug_message(f"Missing by id: need 0x{int(mid):04X} x{q}, have {have_by_id.get(int(mid), 0)}", 33)
                _debug_dump_backpack()
            return False
    for nm, q in req_by_name.items():
        have_exact = int(have_by_name.get(nm, 0))
        if have_exact >= int(q):
            continue
        # Fuzzy fallback
        fk = name_to_fuzzy_key(nm)
        have_fuzzy = int(have_by_name_fuzzy.get(fk, 0)) if fk else 0
        if have_fuzzy >= int(q):
            if SHOW_SKIPPED_DEBUG:
                debug_message(f"Name exact shortfall for '{nm}' but fuzzy '{fk}' meets qty {q} (have {have_fuzzy})", 68)
            continue
        if SHOW_SKIPPED_DEBUG:
            debug_message(f"Missing material: name '{nm}' need x{q}, have exact {have_exact}, fuzzy '{fk}' {have_fuzzy}", 33)
            # Extra diagnostics: show normalized and fuzzy names detected in backpack
            try:
                dbg_counts = dict(BACKPACK_SNAPSHOT['by_name']) if BACKPACK_SNAPSHOT.get('built') else {}
                if dbg_counts:
                    names_list = sorted(list(dbg_counts.keys()))
                    preview = names_list[:40]
                    debug_message(f"Backpack normalized names ({len(names_list)}): {preview}")
                dbg_fz = dict(BACKPACK_SNAPSHOT['by_name_fuzzy']) if BACKPACK_SNAPSHOT.get('built') else {}
                if dbg_fz:
                    fz_list = sorted(list(dbg_fz.keys()))
                    fz_preview = fz_list[:40]
                    debug_message(f"Backpack fuzzy keys ({len(fz_list)}): {fz_preview}")
            except Exception:
                pass
            _debug_dump_backpack()
        return False
    return True

def _attempt_craft(entry) -> dict:
    """Attempt to craft the item using the crafting gump.
    Strategy:
    - Ensure clean gump state, use crafting tool to open gump.
    - Click category button (from entry or mapping).
    - Open target item's info panel (use button id if provided, else scan 3,10,17,... and match name).
    - Click MAKE NOW (try candidate button ids) unless DRY_RUN.
    - Verify output item count increased (by graphic id) -> VERIFIED; else FAILURE.
    """
    if not RAZOR_MODE:
        return {
            'status': 'SKIPPED',
            'reason': 'RAZOR_MODE is False (not running in Razor Enhanced)'
        }

    target_name = (entry.get('target_name') or '').strip()
    category = (entry.get('category') or '').strip()
    graphic_id = _to_int_id(entry.get('id'))
    if graphic_id is None:
        return {'status': 'FAILURE', 'reason': 'Missing graphic id'}

    # Pre-count output items
    before_count = _backpack_count_by_graphic(int(graphic_id))
    debug_message(f"Attempting '{target_name}' (cat='{category}', id={fmt_hex4(graphic_id)}); before count={before_count}")

    # Ensure no stale gump
    _ensure_gump_closed()

    # Open crafting tool/gump
    if not _use_crafting_tool():
        # Maybe already open; wait for gump
        debug_message("Could not use tool; waiting for any existing crafting gump...", 33)
    gid = _wait_for_gump(4000)
    if gid == 0:
        debug_message("Crafting gump did not open after using tool/waiting", 33)
        return {'status': 'FAILURE', 'reason': 'Crafting gump did not open'}

    # Navigate to category
    bid = entry.get('gump_category_button') or _category_to_button_id(category)
    if bid:
        debug_message(f"Navigating to category '{category}' via button {bid}")
        _send_action(bid)
        _pause_ms(ITEM_INFO_RENDER_PAUSE_MS)
    else:
        debug_message(f"No category button id for '{category}', continuing without switching", 33)

    if DRY_RUN:
        debug_message("DRY_RUN enabled: skipping MAKE NOW click", 68)
        return {'status': 'SKIPPED', 'reason': 'DRY_RUN'}

    # Snapshot inventory before for auditing
    inv_before = _collect_backpack_counts_by_key()

    # Click MAKE using only the item-specific make button; do not use defaults
    preferred_make = entry.get('gump_item_make_button')
    # If make button missing, derive from info button when available (make = info - 1)
    if not preferred_make and entry.get('gump_item_info_button') is not None:
        try:
            info_btn = int(entry.get('gump_item_info_button'))
            preferred_make = info_btn - 1
            debug_message(f"Derived MAKE button {preferred_make} from info {info_btn}")
        except Exception:
            preferred_make = None
    if not preferred_make:
        debug_message("Missing item-specific make button id; skipping craft", 33)
        return {
            'status': 'FAILURE',
            'reason': 'No item-specific make button id provided',
            'audit': {
                'consumed': [],
                'produced': [],
                'expected_product_id_hex': fmt_hex4(int(graphic_id) if graphic_id is not None else 0),
                'expected_product_name': target_name,
                'backpack_before': _counts_to_list(inv_before),
                'backpack_after': _counts_to_list(inv_before),
            }
        }
    debug_message(f"Attempting: target='{target_name}' | cat_btn={bid} | make_btn={preferred_make}{' (derived)' if (entry.get('gump_item_make_button') is None and entry.get('gump_item_info_button') is not None) else ''}")
    debug_message(f"Click MAKE (item-specific) button {preferred_make}")
    _send_action(preferred_make)
    _pause_ms(POST_MAKE_WAIT_MS)
    after_count = _backpack_count_by_graphic(int(graphic_id))
    # Snapshot inventory after for auditing
    inv_after = _collect_backpack_counts_by_key()
    delta = _diff_inventory(inv_before, inv_after)
    consumed = _filter_deltas_for_materials(delta, entry.get('materials') or [])
    produced = _filter_deltas_for_product(delta, int(graphic_id))
    made = after_count > before_count
    if made:
        debug_message(f"Crafted '{target_name}' (+{after_count - before_count}) using MAKE button {preferred_make}", 68)

    if made:
        # Convert consumed (negative qty) to materials_used with positive qty
        # If recipe-filtered consumed is empty, fall back to all negative deltas
        if not consumed:
            fallback = _all_negative_deltas(delta)
            if fallback:
                debug_message("Consumed filter matched nothing; falling back to all negative deltas for audit")
                consumed = fallback
        materials_used = []
        try:
            for it in (consumed or []):
                materials_used.append({
                    'name': it.get('name'),
                    'id_hex': it.get('id_hex'),
                    'hue_hex': it.get('hue_hex'),
                    'qty': abs(int(it.get('qty') or 0)),
                })
        except Exception:
            materials_used = []
        # Update our cached snapshot so follow-up recipes see the new state
        try:
            _consume_materials_in_snapshot(materials_used)
            _add_products_to_snapshot(produced)
        except Exception:
            pass
        return {
            'status': 'VERIFIED',
            'audit': {
                'consumed': consumed,
                'produced': produced,
                'materials_used': materials_used,
            }
        }

    # No increase detected -> failure
    debug_message("No output count increase detected after MAKE attempts", 33)
    return {
        'status': 'FAILURE',
        'reason': 'MAKE NOW not effective or incorrect button ids',
        'audit': {
            'consumed': consumed,
            'produced': produced,
            'expected_product_id_hex': fmt_hex4(int(graphic_id)),
            'expected_product_name': target_name,
            'backpack_before': _counts_to_list(inv_before),
            'backpack_after': _counts_to_list(inv_after),
        }
    }

def _build_result_record(entry: dict, res: dict, when_ts: str) -> dict:
    """Build an ordered result record starting with target_name for stable JSON output.
    VERIFIED keys order:
      target_name, category, product_id_hex, status, materials_used, produced, consumed, entry, timestamp
    FAILURE keys order:
      target_name, category, expected_product_id_hex, status, reason, consumed, produced, backpack_before, backpack_after, entry, timestamp
    """
    target_name = (entry.get('target_name') or '').strip()
    category = (entry.get('category') or '').strip()
    product_id_hex = fmt_hex4(_to_int_id(entry.get('id')) or 0)
    status = (res or {}).get('status')
    record = {}
    if status == 'VERIFIED':
        audit = (res or {}).get('audit') or {}
        produced = _sort_change_list(audit.get('produced'))
        materials_used = _sort_change_list(audit.get('materials_used'))
        consumed = _sort_change_list(audit.get('consumed'))
        # ordered insertion: target_name first, status early
        record['target_name'] = target_name
        record['status'] = status
        record['category'] = category
        record['product_id_hex'] = product_id_hex
        record['produced'] = produced
        record['materials_used'] = materials_used
        record['consumed'] = consumed
        record['timestamp'] = when_ts
        record['entry'] = entry
        return record
    elif status == 'FAILURE':
        audit = (res or {}).get('audit') or {}
        produced = _sort_change_list(audit.get('produced'))
        consumed = _sort_change_list(audit.get('consumed'))
        record['target_name'] = target_name
        record['status'] = status
        record['category'] = category
        # Prefer audit expected_product_id_hex if present
        record['expected_product_id_hex'] = audit.get('expected_product_id_hex') or product_id_hex
        record['reason'] = (res or {}).get('reason')
        record['produced'] = produced
        record['consumed'] = consumed
        record['backpack_before'] = audit.get('backpack_before') or []
        record['backpack_after'] = audit.get('backpack_after') or []
        record['timestamp'] = when_ts
        record['entry'] = entry
        return record
    else:
        # Default ordering for other statuses
        record['target_name'] = target_name
        record['status'] = status
        record['category'] = category
        record['timestamp'] = when_ts
        record['entry'] = entry
        return record

def main():
    project_root, data_dir = _script_root_paths()
    debug_message(f"Starting DEV_crafting_tester: RAZOR_MODE={RAZOR_MODE}, DRY_RUN={DRY_RUN}, MAX_TESTS={MAX_TESTS}, SKIP_VERIFIED={SKIP_VERIFIED}")
    src_json = _find_latest_crafting_json(data_dir)
    if not src_json:
        print(f"No source crafting JSON found in {data_dir}")
        sys.exit(1)
    print(f"Using source: {src_json}")

    root = _read_json(src_json)
    items = _normalize_items(root)
    print(f"Loaded items: {len(items)}")

    # Build and write test plan
    plan = build_test_plan(items)
    plan_path = os.path.join(data_dir, f"crafting_test_plan_{_ts()}.json")
    _write_json(plan_path, plan)
    print(f"Wrote test plan: {plan_path}")
    debug_message(f"Plan contains {len(plan.get('tests', []))} tests; proceeding to live phase: {RAZOR_MODE}")

    # Live testing: iterate items we plausibly can test
    verified = []
    failures = []
    if RAZOR_MODE:
        # Inspector-style guard: require Player.Backpack before live actions
        try:
            _ = Player.Backpack
            if not _:
                Misc.SendMessage("No backpack found!", 33)
                debug_message(f"Run summary: VERIFIED={len(verified)}, FAILURES={len(failures)}")
                return
        except Exception:
            Misc.SendMessage("No backpack found!", 33)
            debug_message(f"Run summary: VERIFIED={len(verified)}, FAILURES={len(failures)}")
            return
        # Prepare skip set from external VERIFIED
        already_verified = set()
        if SKIP_VERIFIED:
            src_v = VERIFIED_JSON_PATH.strip() or _find_latest_verified_json(data_dir)
            if src_v:
                already_verified = _load_verified_keys_from_json(src_v)
                print(f"Loaded {len(already_verified)} already-verified recipes from: {src_v}")
            else:
                print("SKIP_VERIFIED is True but no VERIFIED json found.")
        # Load universal verified-by-name list
        uni_path = _universal_verified_path(data_dir)
        uni_names, uni_lower = _load_universal_verified_names(uni_path)
        # Minimal verified progress summary
        _report_verified_progress(plan, data_dir, already_verified)
        # Build one-time backpack snapshot for material checks
        build_backpack_snapshot()
        attempts = 0
        debug_message("Beginning live test pass...")
        _debug_dump_backpack()
        try:
            for entry in plan['tests']:
                # Skip if already verified
                if SKIP_VERIFIED and _test_key_from_entry(entry) in already_verified:
                    debug_message(f"Skip (already verified): {entry.get('target_name')} [{entry.get('category')}]", 58)
                    continue
                # Basic gating: skill and materials
                if not _player_skill_meets(entry.get('skill_required')):
                    debug_message(f"Skip (skill too low or undetected): {entry.get('target_name')}", 58)
                    continue
                # Skip by universal verified names if requested (no need to rescan)
                tname = (entry.get('target_name') or '').strip()
                if SKIP_VERIFIED and tname and tname.lower() in uni_lower:
                    debug_message(f"Skip (universal verified): {tname}", 58)
                    continue
                # Use existing snapshot to check materials; do not rescan if we will skip
                if not _have_materials(entry.get('materials') or []):
                    debug_message(f"Skip (missing materials): {entry.get('target_name')}", 58)
                    continue
                res = _attempt_craft(entry)
                ts_now = _ts()
                ordered_record = _build_result_record(entry, res, ts_now)
                if res.get('status') == 'VERIFIED':
                    verified.append(ordered_record)
                    # Refresh snapshot after actual craft so availability reflects changes
                    build_backpack_snapshot()
                    # Update universal verified names immediately
                    try:
                        if tname and tname.lower() not in uni_lower:
                            uni_names.append(tname)
                            uni_lower.add(tname.lower())
                            _save_universal_verified_names(uni_path, uni_names)
                    except Exception:
                        pass
                elif res.get('status') == 'FAILURE':
                    failures.append(ordered_record)
                else:
                    # skipped results are not stored in verified/failures; continue
                    pass
                # Throttle to be safe between crafts
                _pause_ms(BETWEEN_CRAFTS_MS)
                attempts += 1
                if attempts >= int(MAX_TESTS):
                    debug_message(f"Reached MAX_TESTS={MAX_TESTS} cap; stopping run", 38)
                    break
        except Exception as e:
            debug_message(f"Unhandled exception during live loop: {e}", 33)

    # Write outputs if any
    if verified:
        out_v = os.path.join(data_dir, f"crafting_verified_{_ts()}.json")
        _write_json(out_v, verified)
        print(f"Wrote VERIFIED: {out_v}")
    if failures:
        out_f = os.path.join(data_dir, f"crafting_failures_{_ts()}.json")
        _write_json(out_f, failures)
        print(f"Wrote FAILURES: {out_f}")

    debug_message(f"Run summary: VERIFIED={len(verified)}, FAILURES={len(failures)}")

    if not RAZOR_MODE:
        print("Plan-only mode completed (RAZOR_MODE is False).")

if __name__ == '__main__':
    main()
