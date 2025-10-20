"""
Development Crafting Gump Crawler - a Razor Enhanced Python Script for Ultima Online

explore a crafting gump to learn recipes , ingredients and skill requirements 
Open a crafting tool gump and extract organized data to JSON.
useful to populate the wiki information , or info for other scripts

Use a crafting tool from backpack to open the crafting gump.
read gump content
try button actions in an offset range to discover 
   - a category change, then an item's info panel; or
   - directly an item's info panel.
When an info/detail-like gump is detected, record it, 
explore all permutations  

Notes:
- Button IDs and layout vary by tool/shard. 
- later provide exact CATEGORY_BUTTONS and ITEM_INFO_BUTTONS , from recording or gump inspection
- Gump text lines numbers vary in this cooking example so we map a few known example to categories
then handle each troublesome item mapping 

STATUS:: in progress , only tuned for cooking , needs verification ( DEV_crafting_tester.py )
VERSION = 20251016
"""
import time
import os
import random
from collections import OrderedDict


DEBUG_TO_INGAME_MESSAGE = True
DEBUG_TO_JSON = True

MAX_ITEMS_TO_EXTRACT = 999 # Extraction cap
USE_ALCHEMY_SETTINGS = True # Set to True for Alchemy (Mortar and Pestle), False for Cooking (Skillet)
ALCHEMY_TOOL_ITEM_IDS = [0x0E9B] # 0x0E9B = Mortar and Pestle (Alchemy)
COOKING_TOOL_ITEM_IDS = [0x097F] # 0x097F = Skillet / Frying Pan (Cooking)
TOOL_ITEM_IDS = ALCHEMY_TOOL_ITEM_IDS if USE_ALCHEMY_SETTINGS else COOKING_TOOL_ITEM_IDS

# initially may want to output the base to to get the category names , after we just want to output items
# If only OUTPUT_ITEM is True, saved JSON will be a flat list of parsed items
OUTPUT_BASE = False # - OUTPUT_BASE: include session/base gump and category scaffolding
OUTPUT_ITEM = True # - OUTPUT_ITEM: include items parsed
INCLUDE_PERCENTS = False  # success/exceptional percents are included in item JSON

DEBUG_TOKEN_STRIPE = True
DEBUG_TOKEN_STRIPE_CATEGORIES = { 'ingredients', 'preparations', 'baking' }
DEBUG_TOKEN_COLOR_A = 68
DEBUG_TOKEN_COLOR_B = 38


# Pattern continues by +7 up to 43: 1,8,15,22,29,36,43
CATEGORY_BUTTONS = list(range(1, 44, 7)) # Known category buttons for Skillet crafting gump (right side columns)

# Cooking (Skillet) category names mapped to their button IDs (right column)
# this was extracted by using the OUTPUT_BASE to scan the gump 
COOKING_CATEGORIES = {
    "Magical Foods": 1,
    "Ingredients": 8,
    "Preparations": 15,
    "Baking": 22,
    "Barbecue": 29,
    "Chocolatiering": 36,
    "Meals": 43,
}

ALCHEMY_CATEGORIES = {
    "Healing and Curative": 1,
    "Enhancement": 8,
    "Misc Potions": 15,
    "Toxic": 22,
    "Explosive": 29,
    "Strange Brew": 36,
}

# Active discipline-derived config
DISCIPLINE_NAME = 'Alchemy' if USE_ALCHEMY_SETTINGS else 'Cooking'
DISCIPLINE_NAME_LOWER = DISCIPLINE_NAME.lower()
CRAFTING_TYPE = DISCIPLINE_NAME
CRAFTING_TYPE_KEY = DISCIPLINE_NAME_LOWER
DISCIPLINE_MENU_LABELS_LOWER = [f"<center>{DISCIPLINE_NAME.lower()} menu</center>", f"{DISCIPLINE_NAME.lower()} menu"]

# Troublesome items per discipline
COOKING_TROUBLESOME_ITEMS = {
    # Example entries; adjust item_info values after confirming in-game
    "Magical Foods":    {"category_button": COOKING_CATEGORIES["Magical Foods"],    "item_info": 3},
    "Ingredients":      {"category_button": COOKING_CATEGORIES["Ingredients"],      "item_info": 3},
    "Preparations":     {"category_button": COOKING_CATEGORIES["Preparations"],     "item_info": 3},
    "Baking":           {"category_button": COOKING_CATEGORIES["Baking"],           "item_info": 3},
    "Barbecue":         {"category_button": COOKING_CATEGORIES["Barbecue"],         "item_info": 3},
    "Chocolatiering":   {"category_button": COOKING_CATEGORIES["Chocolatiering"],   "item_info": 3},
    "Meals":            {"category_button": COOKING_CATEGORIES["Meals"],            "item_info": 94}, # vegetable pizza Example C
}

def _build_alchemy_troublesome():
    try:
        return { name: {"category_button": btn, "item_info": 3} for name, btn in ALCHEMY_CATEGORIES.items() }
    except Exception:
        return {}

ALCHEMY_TROUBLESOME_ITEMS = _build_alchemy_troublesome()

# Active mappings selected by toggle
ACTIVE_CATEGORIES = ALCHEMY_CATEGORIES if USE_ALCHEMY_SETTINGS else COOKING_CATEGORIES
TROUBLESOME_ITEMS = ALCHEMY_TROUBLESOME_ITEMS if USE_ALCHEMY_SETTINGS else COOKING_TROUBLESOME_ITEMS

# Troublesome items (one per category): use to target specific panels quickly in tests
# Fill 'item_info' with a known button id when available. If None, tests will auto-detect.
 

# Discovery probe (general)
BUTTON_ID_MIN = 1
BUTTON_ID_MAX = 120           # keep small to be safe for broad probing

# Item info button scan parameters (left column follows +7 pattern: 3,10,17,...)
# Some shards paginate but continue the numbering (e.g., last on page: 66, next page starts at 73).
# We intentionally scan beyond the visible page without pressing Next.
ITEM_BUTTON_START = 3
ITEM_BUTTON_STEP = 7
ITEM_BUTTON_MAX = 120         # higher than general BUTTON_ID_MAX to catch next-page items

# Left-side item info buttons pattern (Skillet): start at 3, then 10, 17, ... (+7)
ITEM_INFO_BUTTONS = []  # will be derived once using ITEM_BUTTON_* settings

# Exit button id on crafting gumps
EXIT_BUTTON_ID = 0

# DELAYS
LOOP_PAUSE_MS = 100
JITTER_MS = 100
ITEM_BUTTON_CLICK_PAUSE_MS = 300  # slower wait for item info panels to render reliably
BUTTON_CLICK_PAUSE_MS = 100   # delay after clicking a button

# Detection thresholds to avoid endless loops when item info panels
# do not update or when probing beyond available items
MAX_MISSING_IN_ROW = 3  # consecutive non-info or unchanged info panels before skipping category

UI_TOKENS_IGNORE = set([
    'ITEM', 'MAKE NOW', 'MAKE NUMBER', 'MAKE MAX', 'BACK',
    DISCIPLINE_NAME.upper(), f'{DISCIPLINE_NAME.upper()} MENU', 'MATERIALS', 'OTHER',
    'SUCCESS CHANCE:', 'EXCEPTIONAL CHANCE:',
    "THIS ITEM MAY HOLD ITS MAKER'S MARK",
    "GLOBAL CHAT HISTORY - SAY [C <DESIRED MESSAGE> TO CHAT!"
])
_GLOBAL_CHAT_LINE_LOWER = 'global chat history - say [c <desired message> to chat!'

# Tokens that can appear in Baking/other categories that are NOT materials and should be skipped
NON_MATERIAL_PHRASES = {
    'makes as many as possible at once',
}

def _is_non_material_token(s: str) -> bool:
    try:
        return (s or '').strip().lower() in NON_MATERIAL_PHRASES
    except Exception:
        return False

# ===== Layout presets (ORDER_TYPES) =====
# Each ORDER_TYPE returns a suggested ordered token list from the raw text_lines for parsing.
ORDER_TYPES = {
    # Classic layout: name, graphic, skill, success, exceptional, then materials name/qty pairs
    'classic': 'heuristic',
    # Name appears very early (before "Cooking"), materials may be interleaved; use anchors
    'name_first': 'anchors',
    # Materials heavily interleaved (e.g., Meals); rely on anchors heavily
    'materials_interleaved': 'anchors',
}

# Specific troublesome items: map (category, name_substring) -> forced order_type
# Keep keys lowercase; match if both category and name substring match (case-insensitive).
TROUBLESOME_OVERRIDES = {
    ('preparations', 'empty bottle'): 'name_first',
    ('preparations', 'dough'): 'name_first',
    ('meals', 'fish steak'): 'materials_interleaved',
    ('meals', 'cooked bird'): 'materials_interleaved',
    ('meals', 'vegetable pizza'): 'materials_interleaved',
    ('chocolateering', 'cocoa butter'): 'name_first',
    ('baking', 'cake batter'): 'name_first',
}

# EXAMPLE OUTPUT A = most common standardized format found for newer items 
# ITEM Example = Pear Salad ,  Skill Required = 50.0 , Materials = Pear , 1 , Lettuce , 1
"""
ITEM
<CENTER>MATERIALS</CENTER>
<CENTER>OTHER</CENTER>
<CENTER>COOKING MENU</CENTER>
MAKE NOW
MAKE NUMBER
MAKE MAX
BACK
This item may hold its maker's mark
Cooking
Success Chance:
Exceptional Chance:
Pear Salad                 <- name
28855                      <- graphic_id (art id)
50.0                       <- skill_required
100.0%                     <- success_percent
49.3%                      <- exceptional_percent
Pear                       <- material name #1
1                          <- material qty #1
Lettuce                    <- material name #2
1                          <- material qty #2
"""

def handle_example_A(lines: list) -> list:
    """Explicit classic layout parser returning a suggested ordered token list.
    Suitable when: name near skill/percents; materials appear as adjacent name-qty pairs.
    """
    toks = [_strip_tags(x) for x in (lines or []) if _strip_tags(x)]
    # filter out UI labels for signal extraction but keep originals for materials pass if needed
    sig = [t for t in toks if t.upper() not in UI_TOKENS_IGNORE]
    name = None
    gid = None
    skill = None
    percs = []
    # find graphic id (first int >=1000)
    for t in sig:
        ival = _to_int_or_none(t)
        if ival is not None and ival >= 1000:
            gid = ival
            break
    # name = last non-numeric before gid if present, else first non-numeric
    if gid is not None:
        try:
            idx = sig.index(str(gid))
        except Exception:
            idx = -1
        if idx > 0:
            for j in range(idx - 1, -1, -1):
                s = sig[j]
                if _to_int_or_none(s) is None and not _is_percent(s):
                    if s.upper() not in UI_TOKENS_IGNORE and s.lower() != _GLOBAL_CHAT_LINE_LOWER:
                        name = s
                        break
    if not name:
        for s in sig:
            if _to_int_or_none(s) is None and not _is_percent(s):
                if s.upper() not in UI_TOKENS_IGNORE and s.lower() != _GLOBAL_CHAT_LINE_LOWER:
                    name = s
                    break
    # skill and percents
    for s in sig:
        if _is_percent(s):
            v = _percent_to_float(s)
            if v is not None:
                percs.append(v)
            continue
        fv = _to_float_or_none(s)
        if fv is not None and not s.endswith('%') and 0.0 <= fv <= 150.0:
            if skill is None:
                skill = fv
    # materials as adjacent name-qty over all tokens (preserve order)
    mats = []
    i = 0
    while i < len(sig) - 1:
        a = sig[i]
        b = sig[i + 1]
        # Skip non-material phrases
        if _is_non_material_token(a):
            i += 1
            continue
        if (not _is_percent(a)) and (_to_float_or_none(b) is not None) and abs(_to_float_or_none(b) - int(_to_float_or_none(b))) < 1e-6:
            # avoid pairing if a equals item name
            if name and a.strip().lower() == str(name).strip().lower():
                i += 1
                continue
            q = int(_to_float_or_none(b))
            if 0 < q <= 500:
                mats.extend([a, str(q)])
                i += 2
                continue
        i += 1
    out = []
    if name: out.append(name)
    if gid is not None: out.append(str(gid))
    if skill is not None: out.append(str(skill))
    if len(percs) >= 1: out.append(f"{percs[0]}%")
    if len(percs) >= 2: out.append(f"{percs[1]}%")
    out.extend(mats)
    return out


 # EXAMPLE OUTPUT B = Preparations - UNbaked quiche , Material = 1 Dough and 1 Egg , 0.0 skill , 69.6% success , 9.6% exceptional , 

"""
ITEM
<CENTER>MATERIALS</CENTER>
<CENTER>OTHER</CENTER>
<CENTER>COOKING MENU</CENTER>
MAKE NOW
MAKE NUMBER
MAKE MAX
BACK
unbaked quiche             <- name appears EARLY (before 'Cooking' header),
                differs from Example 1 where name was at 12
Cooking                    <- header appears AFTER name here (order differs)
Success Chance:
Exceptional Chance:
Dough                      <- material name #1 appears BEFORE graphic/skill/percents
Eggs                       <- material name #2 contiguous with name #1
4162                       <- graphic_id appears AFTER materials 
0.0                        <- skill_required appears AFTER graphic_id 
69.6%                      <- success_percent
9.6%                       <- exceptional_percent
1                          <- material qty #1 (for 'Dough') appears LATE (after percents)
1                          <- material qty #2 (for 'Eggs') appears LATE (after percents)
"""
def handle_example_B(lines: list) -> list:
    """Name-first with early material names and late quantities (e.g., unbaked quiche).
    Strategy:
    - name = first non-anchor token before 'Cooking'.
    - collect material names appearing before first graphic id/skill/percents block.
    - quantities = integer-like tokens after percents (scan tail).
    - output: name, gid, skill, percents, then interleave names with qtys in order.
    """
    toks = [_strip_tags(x) for x in (lines or []) if _strip_tags(x)]
    low = [t.lower() for t in toks]
    # name before 'cooking'
    name = None
    try:
        idx_c = low.index(DISCIPLINE_NAME_LOWER)
    except Exception:
        idx_c = -1
    search_upto = idx_c if idx_c > 0 else len(toks)
    for t in toks[:search_upto]:
        if t.upper() in UI_TOKENS_IGNORE or _is_percent(t) or _to_float_or_none(t) is not None:
            continue
        name = t
        break
    # find first gid
    gid = None
    for t in toks:
        ival = _to_int_or_none(t)
        if ival is not None and ival >= 1000:
            gid = ival
            break
    # skill and percents
    percs = []
    skill = None
    for t in toks:
        if _is_percent(t):
            v = _percent_to_float(t)
            if v is not None:
                percs.append(v)
            continue
        fv = _to_float_or_none(t)
        if fv is not None and not t.endswith('%') and 0.0 <= fv <= 150.0:
            if skill is None:
                skill = fv
    # material names: from after name up to first percent or gid/skill
    names = []
    started = False
    for t in toks:
        if not started:
            if name and t == name:
                started = True
            continue
        if t.upper() in UI_TOKENS_IGNORE or t.lower() == DISCIPLINE_NAME_LOWER:
            continue
        if _is_non_material_token(t):
            continue
        if _is_percent(t):
            break
        if _to_int_or_none(t) is not None:
            # stop on gid or qty-like int appearing early
            break
        if _to_float_or_none(t) is not None:
            break
        if name and t.strip().lower() == name.strip().lower():
            continue
        names.append(t)
        if len(names) >= 10:
            break
    # qtys: scan from end collect as many ints as names
    qtys = []
    for t in reversed(toks):
        if len(qtys) >= len(names):
            break
        if _is_percent(t):
            continue
        fv = _to_float_or_none(t)
        if fv is not None and abs(fv - int(fv)) < 1e-6:
            iv = int(fv)
            if 0 < iv <= 500:
                qtys.append(iv)
    qtys = list(reversed(qtys))
    out = []
    if name: out.append(name)
    if gid is not None: out.append(str(gid))
    if skill is not None: out.append(str(skill))
    if len(percs) >= 1: out.append(f"{percs[0]}%")
    if len(percs) >= 2: out.append(f"{percs[1]}%")
    for i, nm in enumerate(names):
        out.append(nm)
        if i < len(qtys):
            out.append(str(qtys[i]))
    return out

# EXMAPLE C = Meals - Vegetable Pizza , Material = 2 Carrots , 1 dough , 1 onion , 1 cheese . Require 90.0 skill , graphic id = 4160
# most Meals are good , like example A , but this one is troublesome
"""
"ITEM",
"<CENTER>MATERIALS</CENTER>",
"<CENTER>OTHER</CENTER>",
"<CENTER>COOKING MENU</CENTER>",
"MAKE NOW",
"MAKE NUMBER",
"MAKE MAX",
"BACK",
"This item may hold its maker's mark",
"Cooking",
"Success Chance:",
"Exceptional Chance:",
"dough",
"onion",
"Cheese",
"Vegetable Pizza",
"4160",
"90.0",
"0.0%",
"0.0%",
"Carrots",
"2",
"1",
"1",
"1"
"""

# function to handle EXAMPLE C = Vegetable Pizza , Materials = 2 Carrots , 1 Dough , 1 Onion , 1 Cheese , Require 90.0 skill 
def handle_example_C(lines: list) -> list:
    """Vegetable Pizza-like interleaved layout with mixed early/late names and trailing qtys.
    Explicitly pairs trailing integers to the nearest preceding material names, preserving observed order.
    """
    tokens = [_strip_tags(x) for x in (lines or []) if _strip_tags(x)]
    # Guess name and graphic id
    name_guess, gid_guess, _ = _guess_item_name_and_graphic(tokens)
    # Helpers
    anchors = {'item', 'materials', 'other', 'menu', 'make', 'back', 'chance', DISCIPLINE_NAME_LOWER}
    def is_name_candidate(s: str) -> bool:
        if not s:
            return False
        low = s.lower()
        if low.startswith('<center>') or low.endswith('</center>'):
            return False
        if any(a in low for a in anchors):
            return False
        if _is_non_material_token(s):
            return False
        if s == name_guess:
            return False
        if _to_int_or_none(s) is not None or s.endswith('%'):
            return False
        if low.startswith('0x'):
            return False
        return True

    # Extract percents and skill + remember last percent index
    percents = []
    skill_val = None
    last_percent_idx = -1
    skipped_skill = False
    for i, s in enumerate(tokens):
        if s.endswith('%'):
            pv = _to_float_or_none(s)
            if pv is not None:
                percents.append(pv)
            last_percent_idx = i
            continue
        fv = _to_float_or_none(s)
        if fv is not None and not skipped_skill and 0.0 <= fv <= 120.0:
            skipped_skill = True
            skill_val = fv

    # Names that appear before the percent section (early names): e.g., dough, onion, Cheese
    names_pre = []
    for s in tokens[: max(0, last_percent_idx + 1)]:
        if is_name_candidate(s):
            names_pre.append(s)

    # Pairing logic after percents: use a LIFO stack seeded with early names, but new names encountered
    # after percents (e.g., Carrots) should be assigned first.
    stack = list(names_pre)  # LIFO; the right end is the top
    qty_map = {nm: None for nm in names_pre}
    names_post = []  # maintain encounter order for final output ordering
    for s in tokens[last_percent_idx + 1: ]:
        if is_name_candidate(s):
            names_post.append(s)
            # push to stack as most-recent unfilled name
            stack.append(s)
            qty_map.setdefault(s, None)
            continue
        ival = _to_int_or_none(s)
        if ival is None:
            continue
        if ival >= 1000:
            # graphic ids are > 1000; skip
            continue
        # assign this qty to the most recently encountered name without a qty
        # walk stack from the right to find first with None
        for k in range(len(stack) - 1, -1, -1):
            nm = stack[k]
            if qty_map.get(nm) is None:
                qty_map[nm] = ival
                break

    # Build output ordered pairs: prefer post-percent names in encounter order, then remaining pre names in original order
    ordered_names = list(names_post) + [nm for nm in names_pre if nm not in names_post]

    out = []
    if name_guess: out.append(name_guess)
    if gid_guess is not None: out.append(str(gid_guess))
    if skill_val is not None: out.append(str(skill_val))
    if len(percents) >= 1: out.append(f"{percents[0]}%")
    if len(percents) >= 2: out.append(f"{percents[1]}%")
    for nm in ordered_names:
        out.append(nm)
        q = qty_map.get(nm)
        if q is not None:
            out.append(str(q))
    return out

# EXAMPLE D = Chocolateering - Sweet Cocoa Butter , Materal = 1 sack of sugar and 1 cocoa butter , 15.0 skill , 64.2% success , 4.2% exceptional , 1 quantity , 1 quantity
"""
"ITEM",
"<CENTER>MATERIALS</CENTER>",
"<CENTER>OTHER</CENTER>",
"<CENTER>COOKING MENU</CENTER>",
"MAKE NOW",
"MAKE NUMBER",
"MAKE MAX",
"BACK",
"Cooking",
"Success Chance:",
"Exceptional Chance:",
"sack of sugar",
"cocoa butter",
"15.0",
"64.2%",
"4.2%",
"1",
"1"
"""
def handle_example_D(lines: list) -> list:
    """Chocolatiering case with early material names, explicit skill then percents, and trailing qtys.
    Example shows NO explicit item name or graphic id in tokens; we focus on skill/percents and materials.
    Output order: [name?], [gid?], skill, success%, exceptional%, material name/qty pairs.
    """
    toks = [_strip_tags(x) for x in (lines or []) if _strip_tags(x)]
    # Try to infer a plausible name: last non-numeric token before skill if it doesn't look like a material block
    name = None
    # Skill and percents
    skill = None
    percs = []
    for t in toks:
        if _is_percent(t):
            v = _percent_to_float(t)
            if v is not None:
                percs.append(v)
            continue
        fv = _to_float_or_none(t)
        if fv is not None and not t.endswith('%') and 0.0 <= fv <= 150.0 and skill is None:
            skill = fv
    # Material names: scan from start until first number/percent
    names = []
    for t in toks:
        if t.upper() in UI_TOKENS_IGNORE or t.lower() == DISCIPLINE_NAME_LOWER:
            continue
        if _is_non_material_token(t):
            continue
        if _is_percent(t):
            break
        if _to_float_or_none(t) is not None:
            break
        if _to_int_or_none(t) is not None:
            break
        names.append(t)
        if len(names) >= 10:
            break
    # Quantities after percents (tail ints)
    qtys = []
    for t in reversed(toks):
        if len(qtys) >= len(names):
            break
        if _is_percent(t):
            continue
        fv = _to_float_or_none(t)
        if fv is not None and abs(fv - int(fv)) < 1e-6:
            iv = int(fv)
            if 0 < iv <= 500:
                qtys.append(iv)
    qtys = list(reversed(qtys))
    out = []
    # No graphic id expected; name often unavailable -> omit if not confidently identified
    if skill is not None: out.append(str(skill))
    if len(percs) >= 1: out.append(f"{percs[0]}%")
    if len(percs) >= 2: out.append(f"{percs[1]}%")
    for i, nm in enumerate(names):
        out.append(nm)
        if i < len(qtys):
            out.append(str(qtys[i]))
    return out

# EXAMPLE E =  BAKING - Bread Loaf , Material = 1 Dough , 0.0 skill , 69.6% success , 9.6% exceptional , graphic id = 4155
"""
"ITEM",
"<CENTER>MATERIALS</CENTER>",
"<CENTER>OTHER</CENTER>",
"<CENTER>COOKING MENU</CENTER>",
"MAKE NOW",
"MAKE NUMBER",
"MAKE MAX",
"BACK",
"bread loaf",
"This item may hold its maker's mark",
"Cooking",
"Success Chance:",
"Exceptional Chance:",
"Dough",
"4155",
"0.0",
"69.6%",
"9.6%",
"1"
"""
def handle_example_E(lines: list) -> list:
    """Baking case similar to name-first: name early, one material name early, graphic id present,
    then skill, percents, and trailing qty. Output as: name, gid, skill, success%, exceptional%, material pairs.
    """
    toks = [_strip_tags(x) for x in (lines or []) if _strip_tags(x)]
    low = [t.lower() for t in toks]
    # Name: first non-anchor token before discipline header
    name = None
    try:
        idx_c = low.index(DISCIPLINE_NAME_LOWER)
    except Exception:
        idx_c = -1
    search_upto = idx_c if idx_c > 0 else len(toks)
    for t in toks[:search_upto]:
        if t.upper() in UI_TOKENS_IGNORE or _is_percent(t) or _to_float_or_none(t) is not None:
            continue
        name = t
        break
    # Graphic id anywhere
    gid = None
    for t in toks:
        ival = _to_int_or_none(t)
        if ival is not None and ival >= 1000:
            gid = ival
            break
    # Skill and percents
    percs = []
    skill = None
    for t in toks:
        if _is_percent(t):
            v = _percent_to_float(t)
            if v is not None:
                percs.append(v)
            continue
        fv = _to_float_or_none(t)
        if fv is not None and not t.endswith('%') and 0.0 <= fv <= 150.0 and skill is None:
            skill = fv
    # Material name(s): tokens after name until percent/number/id
    names = []
    started = False
    for t in toks:
        if not started:
            if name and t == name:
                started = True
            continue
        if t.upper() in UI_TOKENS_IGNORE or t.lower() == 'cooking':
            continue
        if _is_non_material_token(t):
            continue
        if _is_percent(t) or _to_int_or_none(t) is not None or _to_float_or_none(t) is not None:
            break
        if name and t.strip().lower() == name.strip().lower():
            continue
        names.append(t)
        if len(names) >= 10:
            break
    # Quantities: trailing ints after percents
    qtys = []
    for t in reversed(toks):
        if len(qtys) >= len(names):
            break
        if _is_percent(t):
            continue
        fv = _to_float_or_none(t)
        if fv is not None and abs(fv - int(fv)) < 1e-6:
            iv = int(fv)
            if 0 < iv <= 500:
                qtys.append(iv)
    qtys = list(reversed(qtys))
    out = []
    if name: out.append(name)
    if gid is not None: out.append(str(gid))
    if skill is not None: out.append(str(skill))
    if len(percs) >= 1: out.append(f"{percs[0]}%")
    if len(percs) >= 2: out.append(f"{percs[1]}%")
    for i, nm in enumerate(names):
        out.append(nm)
        if i < len(qtys):
            out.append(str(qtys[i]))
    return out

# EXAMPLE F =  ALCHEMY - Total Mana Potion , Material = 8 Eye of Newt , 1 Empty Bottles , 90.0 skill , 83.3% success , 8% exceptional , graphic id = 3853
"""
"ITEM",
"<CENTER>MATERIALS</CENTER>",
"<CENTER>OTHER</CENTER>",
"<CENTER>ALCHEMY MENU</CENTER>",
"MAKE NOW",
"MAKE NUMBER",
"MAKE MAX",
"BACK",
"Alchemy",
"Success Chance:",
"Eye of Newt",
"Empty Bottles",
"Total Mana Potion",
"3853",
"90.0",
"83.3%",
"8",
"1"
"""
def handle_example_F(lines: list) -> list:
    # Parse an Alchemy item info panel similar to the example provided.
    # Output order: name, graphic_id, skill, success%, exceptional%, materials interleaved name,qty
    toks = [_strip_tags(x) for x in (lines or []) if _strip_tags(x)]
    if not toks:
        return []
    # Guess name and graphic id using shared helper
    name, gid, idx_gid = _guess_item_name_and_graphic(toks)
    # Skill: first float between 0..150 appearing after gid index
    skill = None
    start_idx = (idx_gid + 1) if idx_gid >= 0 else 0
    for t in toks[start_idx:]:
        v = _to_float_or_none(t.rstrip('%')) if isinstance(t, str) else None
        if v is None:
            continue
        if 0.0 <= v <= 150.0 and not t.endswith('%'):
            skill = v
            break
    # Percents: collect numeric percents (success, exceptional)
    percs = []
    for t in toks:
        if _is_percent(t):
            try:
                percs.append(float(str(t).rstrip('%')))
            except Exception:
                continue
    # Material names: take non-numeric, non-anchor tokens until we hit numbers/percents
    names = []
    for t in toks:
        s = (t or '').strip()
        if not s:
            continue
        if s.upper() in UI_TOKENS_IGNORE or s.lower() == DISCIPLINE_NAME_LOWER:
            continue
        if _is_non_material_token(s):
            continue
        if _is_percent(s):
            break
        if _to_float_or_none(s) is not None or _to_int_or_none(s) is not None:
            break
        names.append(s)
    # Quantities: trailing ints after percents; limit count to names length
    qtys = []
    for t in reversed(toks):
        if len(qtys) >= len(names):
            break
        if _is_percent(t):
            continue
        fv = _to_float_or_none(t)
        if fv is not None and abs(fv - int(fv)) < 1e-6:
            iv = int(fv)
            if 0 < iv <= 500:
                qtys.append(iv)
    qtys = list(reversed(qtys))
    # Build ordered output
    out = []
    if name:
        out.append(name)
    if gid is not None:
        out.append(str(gid))
    if skill is not None:
        out.append(str(skill))
    if len(percs) >= 1:
        out.append(f"{percs[0]}%")
    if len(percs) >= 2:
        out.append(f"{percs[1]}%")
    for i, nm in enumerate(names):
        out.append(nm)
        if i < len(qtys):
            out.append(str(qtys[i]))
    return out


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

def _extract_name_from_lines(lines: list) -> str:
    try:
        norm = normalize_text_by_anchors(lines or [])
        nm = norm.get('name')
        if isinstance(nm, str) and nm.strip():
            return nm.strip()
    except Exception:
        pass
    # fallback: first non-empty token that isn't an anchor keyword
    for t in (lines or [])[:5]:
        s = (t or '').strip()
        if not s:
            continue
        low = s.lower()
        if any(k in low for k in ['item', 'materials', 'other', 'menu', 'make', 'back', 'chance', DISCIPLINE_NAME_LOWER]):
            continue
        return s
    return ''

def identify_order_type(category: str, lines: list) -> str:
    """Decide which ORDER_TYPE fits based on category and token cues."""
    cat = (category or '').lower()
    # First: explicit troublesome overrides based on name
    name_guess = _extract_name_from_lines(lines or [])
    if name_guess:
        nlow = name_guess.lower()
        for (ocat, substr), ot in TROUBLESOME_OVERRIDES.items():
            if ocat == cat and substr in nlow:
                return ot
    # Category heuristics
    if cat in ('meals',):
        return 'materials_interleaved'
    if cat in ('preparations', 'baking'):
        return 'name_first'
    # Content heuristics
    # If name-like token appears before the word 'cooking', prefer name_first
    idx_cooking = _index_of(lines, [DISCIPLINE_NAME_LOWER])
    if idx_cooking > 0:
        # find first non-empty, non-anchor before idx_cooking
        for j in range(max(0, idx_cooking - 4), idx_cooking):
            t = (lines[j] or '').strip()
            if not t:
                continue
            low = t.lower()
            if any(key in low for key in ['item', 'materials', 'other', 'menu', 'make', 'back', 'chance']):
                continue
            # likely a name
            return 'name_first'
    # Default classic
    return 'classic'

def build_suggested_by_order_type(lines: list, order_type: str) -> list:
    """Produce a best-effort ordered token list for the given order_type."""
    norm = normalize_text_by_anchors(lines or [])
    if ORDER_TYPES.get(order_type) == 'anchors' and order_type != 'materials_interleaved':
        return norm.get('suggested_order') or list(lines or [])
    if order_type == 'materials_interleaved':
        # Special handling for cases like Vegetable Pizza where names and numbers are split
        tokens = list(lines or [])
        name_guess, gid_guess, idx_gid = _guess_item_name_and_graphic(tokens)
        # Collect candidate material names (exclude anchors and the item name)
        anchors = {'item', 'materials', 'other', 'menu', 'make', 'back', 'chance', DISCIPLINE_NAME_LOWER}
        names = []
        for t in tokens:
            s = (t or '').strip()
            if not s:
                continue
            low = s.lower()
            if low.startswith('<center>') or low.endswith('</center>'):
                continue
            if any(a in low for a in anchors):
                continue
            if s == name_guess:
                continue
            if _is_non_material_token(s):
                continue
            # Skip obvious numbers and percents
            if _to_int_or_none(s) is not None or s.endswith('%'):
                continue
            # Skip obvious ids like 0xNNNN
            if low.startswith('0x'):
                continue
            names.append(s)
        # Extract numeric tokens as candidate quantities, excluding graphic id and skill
        qtys_raw = []
        skipped_graphic = False
        skipped_skill = False
        skill_val = None
        percents = []  # collect as floats without %
        for t in tokens:
            s = (t or '').strip()
            if not s:
                continue
            if s.endswith('%'):
                pv = _to_float_or_none(s)
                if pv is not None:
                    percents.append(pv)
                continue
            if s == name_guess:
                continue
            ival = _to_int_or_none(s)
            if ival is not None:
                # Heuristics: first large int >= 1000 -> graphic id
                if not skipped_graphic and ival >= 1000:
                    skipped_graphic = True
                    continue
                # Integers 0/1/2 etc are qtys; accept
                qtys_raw.append(ival)
                continue
            fval = _to_float_or_none(s)
            if fval is not None:
                # Heuristic: first float 0-120 -> skill
                if not skipped_skill and 0.0 <= fval <= 120.0:
                    skipped_skill = True
                    skill_val = fval
                    continue
                continue
        # Build qtys by scanning from end: take exactly len(names) integers (skipping graphic id-sized ints)
        qtys_back = []
        for t in reversed(tokens):
            if len(qtys_back) >= len(names):
                break
            s = (t or '').strip()
            if not s or s.endswith('%'):
                continue
            ival = _to_int_or_none(s)
            if ival is None:
                continue
            # skip obvious graphic ids
            if ival >= 1000:
                continue
            qtys_back.append(ival)
        # Map quantities to materials from the end so the nearest number pairs with the last material
        pairs = []  # (index, name, qty)
        for i, mn in enumerate(names):
            # default qty None
            pairs.append([i, mn, None])
        for i, q in enumerate(qtys_back):
            idx_name = len(names) - 1 - i
            if 0 <= idx_name < len(pairs):
                pairs[idx_name][2] = q
        # Assemble classic order: name, graphic id, skill/success/exceptional, then materials pairs
        out = []
        if name_guess:
            out.append(name_guess)
        if gid_guess is not None:
            out.append(str(gid_guess))
        if skill_val is not None:
            out.append(str(skill_val))
        if len(percents) >= 1:
            out.append(f"{percents[0]}%")
        if len(percents) >= 2:
            out.append(f"{percents[1]}%")
        for i, mn, q in pairs:
            out.append(mn)
            if q is not None:
                out.append(str(q))
        return out if out else list(lines or [])
    # 'classic' -> try to enforce classic order using anchors but prioritizing expected flow
    out = []
    name = norm.get('name')
    if name:
        out.append(name)
    gid = norm.get('graphic_id')
    if gid is not None:
        out.append(str(gid))
    if norm.get('success_percent') is not None:
        out.append(f"{norm.get('success_percent')}%")
    if norm.get('exceptional_percent') is not None:
        out.append(f"{norm.get('exceptional_percent')}%")
    # materials pairs
    names = norm.get('materials_names') or []
    qtys = norm.get('materials_qtys') or []
    for i, mn in enumerate(names):
        out.append(mn)
        if i < len(qtys):
            out.append(str(qtys[i]))
    return out if out else list(lines or [])

def _to_int_or_none(s: str):
    try:
        if isinstance(s, str) and s.strip():
            if s.lower().startswith('0x'):
                return int(s, 16)
            return int(s)
    except Exception:
        return None
    return None

def _to_float_or_none(s: str):
    try:
        if isinstance(s, str) and s.strip():
            return float(s.rstrip('%'))
    except Exception:
        return None
    return None

def _guess_item_name_and_graphic(tokens: list):
    """Guess item name as the last non-anchor token before a large integer that looks like a graphic id.
    Returns: (name, graphic_id, index_of_graphic_id or -1)
    """
    anchors = {'item', 'materials', 'other', 'menu', 'make', 'back', 'chance', DISCIPLINE_NAME_LOWER}
    idx_gid = -1
    gid = None
    # find first large integer token
    for i, t in enumerate(tokens or []):
        ival = _to_int_or_none((t or '').strip())
        if ival is not None and ival >= 1000:
            gid = ival
            idx_gid = i
            break
    # guess name: walk backwards from idx_gid-1 to find first non-anchor text
    name = None
    if idx_gid > 0:
        for j in range(idx_gid - 1, -1, -1):
            s = (tokens[j] or '').strip()
            if not s:
                continue
            low = s.lower()
            if low.startswith('<center>') or low.endswith('</center>'):
                continue
            if any(a in low for a in anchors):
                continue
            # Skip numbers and percents
            if _to_int_or_none(s) is not None or s.endswith('%'):
                continue
            name = s
            break
    return name, gid, idx_gid

def _score_parsed(parsed: dict) -> tuple:
    """Score a parsed result. Higher is better. Tuple ordering ensures deterministic choice.
    Metrics:
    - has_name, has_graphic, has_skill, has_success, has_exceptional, materials_count
    - penalize if name looks numeric or empty
    """
    if not isinstance(parsed, dict):
        return (0, 0, 0, 0, 0, 0)
    name = parsed.get('name')
    def _is_numish(x):
        try:
            float(str(x).rstrip('%'))
            return True
        except Exception:
            return False
    has_name = 1 if (isinstance(name, str) and name.strip() and not _is_numish(name)) else 0
    has_graphic = 1 if (parsed.get('graphic_id') is not None) else 0
    has_skill = 1 if (parsed.get('skill_required') is not None) else 0
    has_success = 1 if (parsed.get('success_percent') is not None) else 0
    has_exceptional = 1 if (parsed.get('exceptional_percent') is not None) else 0
    mats = parsed.get('materials') or []
    mats_count = len(mats)
    # Weight materials_count to strongly prefer richer extractions
    return (has_name, has_graphic, has_skill, has_success, has_exceptional, mats_count * 10)

def _parse_with_lines(entry: dict, lines: list, category: str):
    tmp = dict(entry or {})
    tmp['text_lines'] = list(lines or [])
    return parse_item_info_gump(tmp, category)

# ===== Handler sequencing for troublesome items =====

def build_handler_candidates(category: str, entry: dict) -> list:
    """Return a list of (tag, ordered_tokens) candidates prioritized by category and example patterns.
    Includes original, normalization-based, order-type heuristic, and example handlers A-F.
    """
    lines = (entry or {}).get('text_lines') or []
    candidates = []
    # Original
    if lines:
        candidates.append(('original', list(lines)))
    # Normalized suggested order (computed locally; we don't persist it to entry)
    try:
        norm = normalize_text_by_anchors(lines)
        if isinstance(norm, dict):
            sug = norm.get('suggested_order') or []
            if sug:
                candidates.append(('normalized', sug))
    except Exception:
        pass
    # Category-specific example handlers (priority varies by category)
    cat = (category or '').lower()
    if cat == 'meals':
        # Prioritize Example C for Meals before generic order-type to better handle Vegetable Pizza layout
        example_funcs = [handle_example_C, handle_example_A, handle_example_B]
    elif cat == 'preparations':
        example_funcs = [handle_example_B, handle_example_A, handle_example_C]
    elif cat == 'baking':
        example_funcs = [handle_example_E, handle_example_B, handle_example_A]
    elif cat == 'chocolatiering':
        example_funcs = [handle_example_D, handle_example_A, handle_example_B]
    elif cat == 'misc potions' and DISCIPLINE_NAME_LOWER == 'alchemy':
        # Alchemy Misc Potions (e.g., mana potions) follow Example F; prioritize it
        example_funcs = [handle_example_F, handle_example_A, handle_example_B, handle_example_C, handle_example_D, handle_example_E]
    else:
        # Default: include Example F as a fallback candidate as well
        example_funcs = [handle_example_A, handle_example_B, handle_example_C, handle_example_D, handle_example_E, handle_example_F]
    for fn in example_funcs:
        try:
            seq = fn(lines) or []
            if seq:
                candidates.append((fn.__name__, seq))
        except Exception:
            continue

    # Order-type suggestion (for Meals, this now comes after example handlers to avoid tie overshadowing)
    try:
        ot = identify_order_type(category, lines)
        sug = build_suggested_by_order_type(lines, ot)
        if sug:
            candidates.append((f'order:{ot}', sug))
    except Exception:
        pass
    return candidates

def test_extract_troublesome_recipes():
    """Merged extractor: iterate TROUBLESOME_ITEMS categories and capture a single targeted
    item info panel per category. Uses category-driven handler sequencing to parse best.
    Optionally records sampler diagnostics like test_extract_troublesome_set_with_sampler.
    """
    results = {
        'session_start': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
        'tool_item_ids': [hex(tool_item_id) for tool_item_id in TOOL_ITEM_IDS],
        'crafting_type': CRAFTING_TYPE,
        'crafting_type_key': CRAFTING_TYPE_KEY,
        'categories': {}
    }

    gid = open_crafting_gump()
    if gid == 0:
        debug_message('Could not open crafting gump', 33)
        return results

    for cat_name, meta in TROUBLESOME_ITEMS.items():
        cat_btn = int((meta or {}).get('category_button') or COOKING_CATEGORIES.get(cat_name) or 0)
        if cat_btn <= 0:
            debug_message(f"Skip unknown category button for {cat_name}", 33)
            continue
        gid = send_action_and_wait(gid, cat_btn)
        if gid == 0:
            debug_message(f"Failed to switch to {cat_name}", 33)
            break
        pause_ms(ITEM_BUTTON_CLICK_PAUSE_MS // 2)

        if cat_name not in results['categories']:
            results['categories'][cat_name] = { 'button': cat_btn, 'items': [] }

        series, gid = detect_item_button_series_for_category(gid, cat_btn)
        series_to_use = series if (series and len(series) > 0) else ITEM_INFO_BUTTONS
        if not series_to_use:
            debug_message(f'No item button series detected for {cat_name}', 33)
            continue

        explicit_btn = (meta or {}).get('item_info')
        probe_buttons = [explicit_btn] if (isinstance(explicit_btn, int) and explicit_btn > 0) else series_to_use[:5]

        picked = None
        for item_btn in probe_buttons:
            cur = send_action_and_wait(gid, item_btn, wait_ms=ITEM_BUTTON_CLICK_PAUSE_MS)
            if cur == 0:
                break
            entry = snap_gump_to_entry(cur)

            if looks_like_item_info(entry):
                try:
                    debug_tokens_striped(cat_name, entry.get('text_lines'))
                except Exception:
                    pass
                # Build handler candidates and score
                best_parsed = None
                best_score = None
                best_tag = None
                for tag, seq in build_handler_candidates(cat_name, entry):
                    try:
                        parsed = _parse_with_lines(entry, seq, cat_name)
                        score = _score_parsed(parsed)
                        if (best_parsed is None) or (score > best_score):
                            best_parsed, best_score, best_tag = parsed, score, tag
                    except Exception:
                        continue
                # Fallback
                if not best_parsed:
                    try:
                        best_parsed = parse_item_info_gump(entry, cat_name) or {}
                    except Exception:
                        best_parsed = {}
                best_parsed['category'] = cat_name
                # Attach category and item button ids
                try:
                    best_parsed['button_category'] = int(cat_btn)
                except Exception:
                    best_parsed['button_category'] = None
                best_parsed['button_info'] = int(item_btn)
                try:
                    best_parsed['button_make'] = int(item_btn) - 1
                except Exception:
                    best_parsed['button_make'] = None
                picked = {
                    'button': item_btn,
                    'detail': entry,
                    'parsed': best_parsed,
                    'parse_meta': {
                        'strategy': best_tag,
                        'score': best_score,
                    }
                }
                exit_gump(cur, retries=2)
                break
            # Return to category page if not info
            exit_gump(cur, retries=1)
            gid = open_crafting_gump()
            if gid == 0:
                break
            gid = send_action_and_wait(gid, cat_btn)
            if gid == 0:
                break
            pause_ms(ITEM_BUTTON_CLICK_PAUSE_MS // 2)

        results['categories'][cat_name]['items'] = [] if picked is None else [picked]

        exit_gump(gid, retries=2)
        gid = open_crafting_gump()
        if gid == 0:
            break

    save_results(results)
    return results

def exit_gump(gid, retries=3):
    """Attempt to close the current gump cleanly by clicking Exit (button 0) multiple times.
    Returns True if no gump remains open, False otherwise."""
    ok = False
    for _ in range(max(1, retries)):
        try:
            if gid:
                Gumps.SendAction(gid, EXIT_BUTTON_ID)
            else:
                # try generic close on current
                cur = Gumps.CurrentGump()
                if cur:
                    Gumps.SendAction(cur, EXIT_BUTTON_ID)
        except Exception:
            pass
        pause_ms(200)
        # check state
        cur = wait_for_gump(600)
        if cur == 0:
            ok = True
            break
    # hard reset as a fallback
    try:
        if not ok:
            Gumps.ResetGump()
            pause_ms(150)
            cur = wait_for_gump(400)
            ok = (cur == 0)
    except Exception:
        pass
    return ok

def looks_like_item_info(entry):
    """Heuristic: detect if a gump snapshot looks like an item detail/info panel."""
    lines = (entry.get('text_lines') or [])
    joined = ' '.join([l.lower() for l in lines])
    keywords = [
        'required', 'resources', 'materials', 'skill', 'success', 'exceptional',
        'make', 'mark item', 'tools', 'ingredients', 'weight', 'durability'
    ]
    return any(k in joined for k in keywords)

def debug_tokens_striped(category_key: str, text_lines: list):
    """Send a compact single-line of all tokens, then two alternating color lines
    (even/odd tokens) to improve visual separation in the game chat.
    Only runs for configured categories to avoid spam.
    """
    try:
        if not DEBUG_TOKEN_STRIPE:
            return
        cat_lower = (category_key or '').strip().lower()
        if cat_lower not in DEBUG_TOKEN_STRIPE_CATEGORIES:
            return
        # Build tokens (strip tags, drop empties) but do NOT filter UI labels; user wants to see everything
        tokens = [_strip_tags(x) for x in (text_lines or []) if _strip_tags(x)]
        if not tokens:
            return
        # Single long line with indexed tokens
        joined = ' | '.join([f"[{i}] {t}" for i, t in enumerate(tokens)])
        debug_message(joined, DEBUG_TOKEN_COLOR_A)
        # Even / Odd lines alternating colors
        even_line = ' | '.join([f"[{i}] {t}" for i, t in enumerate(tokens) if i % 2 == 0])
        odd_line = ' | '.join([f"[{i}] {t}" for i, t in enumerate(tokens) if i % 2 == 1])
        if even_line:
            debug_message(even_line, DEBUG_TOKEN_COLOR_A)
        if odd_line:
            debug_message(odd_line, DEBUG_TOKEN_COLOR_B)
    except Exception:
        pass

# ===== Item info parsing =====

def _strip_tags(s: str) -> str:
    s = s.strip()
    # remove <CENTER>...</CENTER> wrappers
    if s.upper().startswith('<CENTER>') and s.upper().endswith('</CENTER>'):
        s = s[8:-9]
    return s.strip()

def _is_percent(s: str) -> bool:
    return s.endswith('%') and _is_float(s[:-1])

def _percent_to_float(s: str):
    try:
        return float(s.replace('%', ''))
    except Exception:
        return None

def _is_float(s: str) -> bool:
    try:
        float(s)
        return True
    except Exception:
        return False

def format_graphic_id_hex(val) -> str:
    """Return 4-digit, zero-padded uppercase hex like '0x00F2' for an int input."""
    try:
        n = int(val)
        return f"0x{n:04X}"
    except Exception:
        return None

def is_sparse_parsed_item(parsed: dict) -> bool:
    """Heuristic to detect under-parsed items (too many null/empty fields).
    Returns True if the item is considered too sparse to keep.
    Criteria:
      - Missing name OR
      - Has <= 1 of these populated: graphic_id_hex, skill_required, success_percent,
        exceptional_percent, materials (non-empty)
    """
    if not parsed:
        return True
    if not parsed.get('name'):
        return True
    signals = 0
    if parsed.get('graphic_id_hex'): signals += 1
    if parsed.get('skill_required') is not None: signals += 1
    if parsed.get('success_percent') is not None: signals += 1
    if parsed.get('exceptional_percent') is not None: signals += 1
    mats = parsed.get('materials')
    if isinstance(mats, list) and len(mats) > 0:
        signals += 1
    return signals <= 1

def build_item_output(parsed: dict, include_percents: bool = None) -> dict:
    """Return an ordered, succinct dict for a parsed item.
    Order: category, name, id, skill_required, [success_percent, exceptional_percent], buttons, materials
    - id is the zero-padded uppercase hex graphic id (e.g., 0x00F2)
    - include_percents: override global toggle if provided
    """
    if include_percents is None:
        include_percents = INCLUDE_PERCENTS
    o = OrderedDict()
    # Append in strict order, skipping None/empty
    val = parsed.get('category')
    if val is not None:
        o['category'] = val
    val = parsed.get('name')
    if val is not None:
        o['name'] = val
    val = parsed.get('graphic_id_hex')
    if val is not None:
        o['id'] = val
    val = parsed.get('skill_required')
    if val is not None:
        o['skill_required'] = val
    if include_percents:
        val = parsed.get('success_percent')
        if val is not None:
            o['success_percent'] = val
        val = parsed.get('exceptional_percent')
        if val is not None:
            o['exceptional_percent'] = val
    # Include button ids (category/info/make) before materials, if present
    val = parsed.get('button_category')
    if val is not None:
        o['button_category'] = val
    val = parsed.get('button_info')
    if val is not None:
        o['button_info'] = val
    val = parsed.get('button_make')
    if val is not None:
        o['button_make'] = val
    mats = parsed.get('materials')
    if isinstance(mats, list) and len(mats) > 0:
        o['materials'] = mats
    return o

def parse_item_info_gump(entry: dict, category: str = None) -> dict:
    """Parse an item info gump snapshot into a structured dict.

    Strategy (based on observed Skillet pattern):
    - The list contains UI labels and section headers; we strip/ignore those.
    - We then extract:
      * name: first non-ignored, non-numeric, non-percent token.
      * graphic_id: first integer token > 1000 (heuristic to avoid material quantities).
      * skill_required: first float token (no %).
      * success: first percent token (as float).
      * exceptional: second percent token (as float).
      * materials: after both percents are seen, read pairs [name, qty] from remaining tokens.
    We also return a 'mapping' field documenting these heuristics.
    """
    lines = entry.get('text_lines') or []
    tokens_raw = [_strip_tags(x) for x in lines if _strip_tags(x)]
    # filtered tokens (ignore UI labels)
    tokens = [t for t in tokens_raw if t.upper() not in UI_TOKENS_IGNORE]

    name = None
    name_idx = None
    graphic_id = None
    graphic_idx = None
    skill_required = None
    skill_idx = None
    success = None
    exceptional = None
    materials = []

    # Extract percents and floats/ints
    percent_vals = []
    numeric_positions_consumed = set()
    # Track which token indices are consumed by components to later classify the rest
    used_indices = set()

    for idx, t in enumerate(tokens):
        if _is_percent(t):
            val = _percent_to_float(t)
            percent_vals.append((idx, val))
            continue

    # name: prefer the token immediately before the first large graphic_id if present,
    # otherwise fall back to the first non-numeric, non-percent token.
    prelim_name = None
    prelim_idx = None
    for idx, t in enumerate(tokens):
        if _is_percent(t) or _is_float(t):
            continue
        if t.upper() in UI_TOKENS_IGNORE:
            continue
        if "maker's mark" in t.lower():
            continue
        if t.strip().lower() == 'global chat history - say [c <desired message> to chat!':
            continue
        prelim_name = t
        prelim_idx = idx
        break

    # graphic id: first int > 1000
    for idx, t in enumerate(tokens):
        if t.isdigit():
            try:
                val = int(t)
                if val > 1000:
                    graphic_id = val
                    graphic_idx = idx
                    numeric_positions_consumed.add(idx)
                    used_indices.add(idx)
                    break
            except Exception:
                pass

    # skill_required: first float without percent
    for idx, t in enumerate(tokens):
        if _is_percent(t):
            continue
        if _is_float(t):
            try:
                if '.' in t or float(t) != int(float(t)):
                    skill_required = float(t)
                    skill_idx = idx
                    numeric_positions_consumed.add(idx)
                    used_indices.add(idx)
                    break
            except Exception:
                pass

    # success/exceptional
    if len(percent_vals) >= 1:
        success = percent_vals[0][1]
        numeric_positions_consumed.add(percent_vals[0][0])
        used_indices.add(percent_vals[0][0])
    if len(percent_vals) >= 2:
        exceptional = percent_vals[1][1]
        numeric_positions_consumed.add(percent_vals[1][0])
        used_indices.add(percent_vals[1][0])

    # Finalize name selection (prefer token immediately before graphic_id when available)
    if graphic_idx is not None:
        # search backwards from graphic_idx-1 for a suitable name token
        for b in range(graphic_idx - 1, -1, -1):
            tb = tokens[b]
            if _is_percent(tb) or _is_float(tb) or tb.upper() in UI_TOKENS_IGNORE:
                continue
            if "maker's mark" in tb.lower():
                continue
            if tb.strip().lower() == 'global chat history - say [c <desired message> to chat!':
                continue
            name = tb
            name_idx = b
            break
        if name is None and prelim_name is not None:
            name = prelim_name
            name_idx = prelim_idx
    else:
        # No graphic id found; use preliminary name if any
        name = prelim_name
        name_idx = prelim_idx

    # Before parsing materials, detect the first material pair anywhere in the token stream.
    # We'll use this as a boundary to ensure the item name is located BEFORE materials.
    def _first_material_pair_index(tokens_seq):
        QTY_MAX_TMP = 500
        z = 0
        while z < len(tokens_seq) - 1:
            a = tokens_seq[z]
            b = tokens_seq[z + 1]
            if _is_non_material_token(a):
                z += 1
                continue
            if (not _is_float(a)) and (_is_float(b) and abs(float(b) - int(float(b))) < 1e-6):
                qty_i = int(float(b))
                if 0 < qty_i <= QTY_MAX_TMP:
                    return z, a, qty_i
            z += 1
        return None, None, None

    first_mat_idx, first_mat_name, _first_mat_qty = _first_material_pair_index(tokens)

    # If current name is missing or equals the first material name, reselect
    # the name as the last non-numeric, non-percent token BEFORE the first material pair.
    if first_mat_idx is not None and (name is None or (first_mat_name and str(name).strip().lower() == str(first_mat_name).strip().lower())):
        for b in range(first_mat_idx - 1, -1, -1):
            tb = tokens[b]
            if _is_percent(tb) or _is_float(tb) or tb.upper() in UI_TOKENS_IGNORE:
                continue
            if "maker's mark" in tb.lower():
                continue
            if tb.strip().lower() == 'global chat history - say [c <desired message> to chat!':
                continue
            name = tb
            name_idx = b
            break

    # materials: robust parse of [name, qty] pairs.
    # Determine a safe starting index after all detected header fields.
    header_indices = []
    if name_idx is not None:
        header_indices.append(name_idx)
        used_indices.add(name_idx)
    if graphic_idx is not None:
        header_indices.append(graphic_idx)
    if skill_idx is not None:
        header_indices.append(skill_idx)
    header_indices.extend([p[0] for p in percent_vals])
    start_idx = (max(header_indices) + 1) if header_indices else 0

    QTY_MAX = 500  # heuristic upper bound to avoid treating art IDs as quantities
    j = max(0, start_idx)
    while j < len(tokens):
        # Skip ignored or percent tokens
        t = tokens[j]
        if t.upper() in UI_TOKENS_IGNORE or _is_percent(t):
            j += 1
            continue
        if _is_non_material_token(t):
            j += 1
            continue
        # Pair a non-numeric name with a following numeric quantity
        if (j + 1) < len(tokens):
            mat_name = tokens[j]
            mat_qty = tokens[j + 1]
            # Accept integer-only quantities (no dot)
            if (not _is_float(mat_name)) and (_to_int_or_none(mat_qty) is not None) and ('.' not in str(mat_qty)):
                qty_int = int(float(mat_qty))
                # Avoid pairing if the material name matches the item name
                if name and mat_name.strip().lower() == str(name).strip().lower():
                    j += 1
                    continue
                # Enforce upper bound
                if 0 < qty_int <= QTY_MAX:
                    materials.append({'name': mat_name, 'qty': qty_int})
                    # mark indices used for materials
                    used_indices.add(j)
                    used_indices.add(j + 1)
                j += 2
                continue
        j += 1

    # If not enough materials were detected via adjacent pairs, attempt a fallback using a Materials block.
    if not materials:
        # Try to locate a Materials section in tokens and pair names with integer-only qtys
        def _collect_materials_from_block(tok_list):
            # Find indices for MATERIALS and the next header boundary
            mat_idx = -1
            end_idx = len(tok_list)
            for idx, tk in enumerate(tok_list):
                if isinstance(tk, str) and tk.strip().upper() == 'MATERIALS':
                    mat_idx = idx
                    break
            if mat_idx >= 0:
                for idx in range(mat_idx + 1, len(tok_list)):
                    tku = (tok_list[idx] or '').strip().upper() if isinstance(tok_list[idx], str) else ''
                    if tku in {'OTHER', 'MENU', 'BACK'}:
                        end_idx = idx
                        break
            block = tok_list[mat_idx + 1:end_idx] if mat_idx >= 0 else []
            names_b = []
            qtys_b = []
            for tok in block:
                s = (tok or '').strip()
                if not s:
                    continue
                if _is_non_material_token(s):
                    continue
                # Integer-only quantities (no dot)
                iv = _to_int_or_none(s)
                if iv is not None and ('.' not in s) and 0 < iv <= QTY_MAX:
                    qtys_b.append(iv)
                    continue
                # Skip percents and floats and UI tokens
                if _is_percent(s) or _is_float(s) or s.upper() in UI_TOKENS_IGNORE:
                    continue
                # Skip obvious ids
                if s.lower().startswith('0x'):
                    continue
                # Skip if equals item name
                if name and s.strip().lower() == str(name).strip().lower():
                    continue
                names_b.append(s)
            return names_b, qtys_b

        nb, qb = _collect_materials_from_block(tokens)
        if nb:
            # Pair in order; missing qtys default to 1
            for idx, nm in enumerate(nb):
                qv = qb[idx] if idx < len(qb) else 1
                materials.append({'name': nm, 'qty': qv})

    # Category-based fallback for Example 2 ordering (names earlier, quantities later)
    # Only apply if no materials were captured by the adjacent-pair logic and the
    # category is not one of the Example 1 categories.
    try:
        cat = (category or '').strip().lower()
    except Exception:
        cat = ''
    EX1_CATEGORIES = {'magical foods', 'meals'}
    materials_name_candidates = []
    materials_qty_candidates = []
    if (not materials) and (cat not in EX1_CATEGORIES):
        # Heuristic: find a block of candidate material names immediately after the chosen name,
        # stopping at the first strong metadata signal (percent or clear numeric run with id/skill).
        name_block = []
        if name_idx is not None:
            k = name_idx + 1
            while k < len(tokens):
                tk = tokens[k]
                # Stop at percents
                if _is_percent(tk):
                    break
                # Stop at a likely metadata number (graphic id or skill float)
                if _is_float(tk):
                    # If >= 1000 treat as art id; stop
                    try:
                        v = float(tk)
                        if v >= 1000 or ('.' in tk):
                            break
                    except Exception:
                        break
                # Skip UI tokens and obvious non-material labels
                if tk.upper() in UI_TOKENS_IGNORE or tk.strip().lower() in {DISCIPLINE_NAME_LOWER}:
                    k += 1
                    continue
                if _is_non_material_token(tk):
                    k += 1
                    continue
                # Accept as a material name candidate (non-numeric)
                if not _is_float(tk):
                    # Avoid duplicating the item name
                    if not (name and tk.strip().lower() == str(name).strip().lower()):
                        name_block.append(tk)
                else:
                    break
                # Cap to reasonable number of materials to prevent runaway
                if len(name_block) >= 10:
                    break
                k += 1

        # Collect integer-like quantities after the last percent (they tend to appear late)
        qty_block = []
        last_percent_pos = max([p[0] for p in percent_vals], default=-1)
        m = max(start_idx, last_percent_pos + 1)
        while m < len(tokens) and len(qty_block) < len(name_block):
            tm = tokens[m]
            if _is_float(tm) and abs(float(tm) - int(float(tm))) < 1e-6:
                qv = int(float(tm))
                if 0 < qv <= QTY_MAX:
                    qty_block.append(qv)
            m += 1

        # Zip candidates if counts match
        # Save candidate blocks regardless of match for downstream visibility
        materials_name_candidates = name_block[:]
        materials_qty_candidates = qty_block[:]
        if name_block and len(name_block) == len(qty_block):
            materials = [{'name': nm, 'qty': qv} for nm, qv in zip(name_block, qty_block)]
            # We cannot back-map exact indices here reliably; leave used_indices as-is

    # Classify remaining tokens (non-ignored) that were not consumed into components
    unknown_numbers = []
    unknown_texts = []
    for idx, t in enumerate(tokens):
        if idx in used_indices:
            continue
        # Skip UI tokens again (defensive) and the preliminary name if unused_indices missed it
        if t.upper() in UI_TOKENS_IGNORE:
            continue
        if _is_float(t):
            # Avoid double-counting success/exceptional already added to used_indices
            # leftover numbers go here
            unknown_numbers.append(t)
        elif not _is_percent(t):
            unknown_texts.append(t)

    return {
        'name': name,
        'graphic_id': graphic_id,
        'graphic_id_hex': format_graphic_id_hex(graphic_id) if graphic_id is not None else None,
        'skill_required': skill_required,
        'success_percent': success,
        'exceptional_percent': exceptional,
        'materials': materials,
        'materials_name_candidates': materials_name_candidates if materials_name_candidates else None,
        'materials_qty_candidates': materials_qty_candidates if materials_qty_candidates else None,
        'unclassified': {
            'unknown_numbers': unknown_numbers if unknown_numbers else None,
            'unknown_texts': unknown_texts if unknown_texts else None
        }
    }

# ===== Tool handling =====

def find_tool_in_backpack():
    if not TOOL_ITEM_IDS:
        return None
    for id_ in TOOL_ITEM_IDS:
        try:
            itm = Items.FindByID(id_, -1, Player.Backpack.Serial)
        except Exception:
            itm = None
        if itm:
            return itm if isinstance(itm, list) else itm
    return None

def open_crafting_gump():
    # Reset state
    try:
        Gumps.ResetGump()
    except Exception:
        pass
    pause_ms(150)

    # Use tool
    tool = find_tool_in_backpack()
    if not tool:
        debug_message("No crafting tool found in backpack (configure TOOL_ITEM_IDS)", 33)
        return 0
    try:
        Items.UseItem(tool)
    except Exception as e:
        debug_message(f"UseItem tool error: {e}", 33)
        return 0

    gid = wait_for_gump(5000)
    if gid == 0:
        debug_message("No gump appeared after using tool", 33)
    else:
        debug_message(f"Opened crafting gump {hex(gid)}", 68)
    return gid

# ===== Main crawler =====

def send_action_and_wait(gid, btn, wait_ms=BUTTON_CLICK_PAUSE_MS):
    """Click a button on gid, wait, and return the current (possibly new) gump id.
    Reopens the tool if gump vanishes. Returns 0 if it cannot restore."""
    try:
        Gumps.SendAction(gid, btn)
    except Exception as e:
        debug_message(f"SendAction {btn} error: {e}", 53)
        return gid
    pause_ms(wait_ms)
    cur = wait_for_gump(2000)
    if cur == 0:
        # try to reopen once
        cur = open_crafting_gump()
    return cur

def _index_of(lines, token_substrs):
    """Return first index in lines containing any of the substrings (case-insensitive)."""
    if not lines:
        return -1
    subs = [s.lower() for s in (token_substrs or []) if isinstance(s, str)]
    for i, ln in enumerate(lines):
        low = (ln or '').lower()
        for s in subs:
            if s in low:
                return i
    return -1

def normalize_text_by_anchors(text_lines: list) -> dict:
    """Heuristic normalization: slice by anchor headers to stabilize meaning despite order.
    Returns a structure with identified fields and a suggested ordered list.
    """
    lines = list(text_lines or [])
    # Key anchors
    idx_mat = _index_of(lines, ['<center>materials</center>', 'materials'])
    idx_other = _index_of(lines, ['<center>other</center>', 'other'])
    idx_menu = _index_of(lines, DISCIPLINE_MENU_LABELS_LOWER)
    idx_skill = _index_of(lines, ['success chance:'])
    idx_exc = _index_of(lines, ['exceptional chance:'])

    # Name heuristic: choose the last non-empty line before skill header that is not an anchor label
    name = None
    if idx_skill > 0:
        for j in range(idx_skill - 1, -1, -1):
            t = (lines[j] or '').strip()
            if not t:
                continue
            low = t.lower()
            if 'item' == low:
                continue
            if DISCIPLINE_NAME_LOWER in low:
                continue
            if 'chance' in low or 'make' in low or 'back' == low or 'menu' in low:
                continue
            if 'materials' in low or 'other' in low:
                continue
            name = t
            break

    # Materials block: between idx_mat and idx_other (or menu/footer)
    mat_start = idx_mat + 1 if idx_mat >= 0 else -1
    mat_end = idx_other if idx_other >= 0 else (idx_menu if idx_menu >= 0 else len(lines))
    materials_block = lines[mat_start:mat_end] if (mat_start >= 0 and mat_start < mat_end) else []
    # Split names vs qty tokens
    material_names = []
    material_qtys = []
    for tok in materials_block:
        t = (tok or '').strip()
        if not t:
            continue
        if _is_non_material_token(t):
            continue
        # numeric? allow decimals but typical qty are ints
        is_num = True
        try:
            float(t)
        except Exception:
            is_num = False
        if is_num:
            # keep as int if possible
            try:
                material_qtys.append(int(float(t)))
            except Exception:
                material_qtys.append(t)
        else:
            material_names.append(t)

    # Graphic id: any standalone integer near name or inside block that looks like ArtID (200-40000 typical)
    graphic_id = None
    numeric_candidates = []
    for tok in lines:
        t = (tok or '').strip()
        try:
            v = int(float(t))
            numeric_candidates.append(v)
        except Exception:
            pass
    # Prefer a 4-digit range common in your samples (e.g., 2487, 4155, 4161, 4162)
    for v in numeric_candidates:
        if 200 <= v <= 50000:
            graphic_id = v
            break

    # Skill/percents
    skill_required = None
    success_percent = None
    exceptional_percent = None
    # Extract numbers following headers if available
    def _num_after(idx):
        if idx < 0:
            return None
        # look forward for the first numeric token
        for k in range(idx + 1, min(idx + 5, len(lines))):
            t = (lines[k] or '').strip().rstrip('%')
            try:
                return float(t)
            except Exception:
                continue
        return None
    success_percent = _num_after(idx_skill)
    exceptional_percent = _num_after(idx_exc)
    # Skill may appear as a plain number before percents; choose the first float not a percent before idx_skill
    if idx_skill >= 0:
        for j in range(max(0, idx_skill - 5), idx_skill):
            t = (lines[j] or '').strip().rstrip('%')
            try:
                val = float(t)
                # often whole number or one decimal; not an ID if very large
                if 0.0 <= val <= 150.0:
                    skill_required = val
                    break
            except Exception:
                pass

    # Compose a suggested order: [ITEM header], name, graphic, Cooking, Skill, Success/Exceptional, Materials header, interleaved name-qty pairs
    ordered = []
    # start with name if found
    if name:
        ordered.append(name)
    if graphic_id is not None:
        ordered.append(str(graphic_id))
    if success_percent is not None:
        ordered.append(f"{success_percent}%")
    if exceptional_percent is not None:
        ordered.append(f"{exceptional_percent}%")
    # interleave materials names with quantities (best-effort)
    mats = []
    for i, mname in enumerate(material_names):
        qty = material_qtys[i] if i < len(material_qtys) else None
        if qty is not None:
            mats.extend([mname, str(qty)])
        else:
            mats.append(mname)

    return {
        'name': name,
        'graphic_id': graphic_id,
        'skill_required': skill_required,
        'success_percent': success_percent,
        'exceptional_percent': exceptional_percent,
        'materials_names': material_names,
        'materials_qtys': material_qtys,
        'suggested_order': ordered + mats,
        'anchors': {
            'materials_idx': idx_mat,
            'other_idx': idx_other,
            'menu_idx': idx_menu,
            'skill_idx': idx_skill,
            'exceptional_idx': idx_exc,
        }
    }

def register_known(entry, results):
    """Store a lightweight record of a gump to build knowledge for future crawls."""
    try:
        if not entry or not isinstance(entry, dict):
            return
        key = entry.get('gump_id_hex') or str(entry.get('gump_id_decimal'))
        if not key:
            return
        if 'known_gumps' not in results:
            results['known_gumps'] = {}
        if key in results['known_gumps']:
            return
        results['known_gumps'][key] = {
            'text_lines': entry.get('text_lines', [])
        }
    except Exception:
        pass

def detect_item_button_series_for_category(current_gump_id: int, category_button_id: int):
    """Detect the correct left-column item button offset for this category by probing
    phases 0..ITEM_BUTTON_STEP-1 starting at ITEM_BUTTON_START. Returns a tuple
    (series_list, refreshed_gump_id). If detection fails, returns (None, current_gump_id).

    Strategy:
    - Try ITEM_BUTTON_START+phase for phase in [0..step-1].
    - If an item-info gump is detected, use that as the seed, then generate the
      full series: seed, seed+step, seed+2*step, ... up to ITEM_BUTTON_MAX.
    - After detection, re-select the category to return to the item list page.
    """
    try:
        step = max(1, int(ITEM_BUTTON_STEP))
        start = int(ITEM_BUTTON_START)
        maxb = int(ITEM_BUTTON_MAX)
    except Exception:
        step, start, maxb = 7, 3, 300

    detected_seed = None
    working_gump_id = current_gump_id
    for phase in range(0, step):
        probe_button_id = start + phase
        # Click and wait for potential item-info panel
        working_gump_id = send_action_and_wait(working_gump_id, probe_button_id, wait_ms=ITEM_BUTTON_CLICK_PAUSE_MS)
        if working_gump_id == 0:
            # Try to restore and reselect the category
            working_gump_id = open_crafting_gump()
            if working_gump_id == 0:
                debug_message(f"Failed to reopen gump during offset detection (phase {phase})", 33)
                return (None, 0)
            working_gump_id = send_action_and_wait(working_gump_id, category_button_id)
            pause_ms(ITEM_BUTTON_CLICK_PAUSE_MS // 2)
            continue
        probe_entry = snap_gump_to_entry(working_gump_id)
        if looks_like_item_info(probe_entry):
            detected_seed = probe_button_id
            debug_message(f"Detected item button seed {detected_seed} for category btn {category_button_id}", 63)
            break
    # Reselect category to return to list page before main iteration
    if working_gump_id != 0:
        working_gump_id = send_action_and_wait(working_gump_id, category_button_id)
        pause_ms(ITEM_BUTTON_CLICK_PAUSE_MS // 2)

    if detected_seed is None:
        return (None, working_gump_id)

    detected_series = [b for b in range(detected_seed, maxb + 1, step)]
    return (detected_series, working_gump_id)

def crawl_once(max_items=1):
    """Perform a single crawl session over the crafting gump and collect item details.

    max_items: the maximum number of item detail panels to capture across all categories.
    """
    crawl_results = {
        'session_start': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
        'tool_item_ids': [hex(tool_item_id) for tool_item_id in TOOL_ITEM_IDS],
        'crafting_type': CRAFTING_TYPE,
        'crafting_type_key': CRAFTING_TYPE_KEY,
        'base_gump': None,
        'categories': {},
        'known_gumps': {}
    }

    crafting_gump_id = open_crafting_gump()
    if crafting_gump_id == 0:
        return crawl_results

    # Take an initial snapshot of the base crafting gump
    base_gump_entry = snap_gump_to_entry(crafting_gump_id)
    crawl_results['base_gump'] = base_gump_entry
    register_known(base_gump_entry, crawl_results)

    # Initialize the list of item-info button identifiers (3, 10, 17, ...)
    global ITEM_INFO_BUTTONS
    if not ITEM_INFO_BUTTONS:
        try:
            item_button_start_value = int(ITEM_BUTTON_START)
            item_button_step_value = max(1, int(ITEM_BUTTON_STEP))
            item_button_maximum_value = int(ITEM_BUTTON_MAX)
        except Exception:
            item_button_start_value, item_button_step_value, item_button_maximum_value = 3, 7, 300
        ITEM_INFO_BUTTONS = [button_id for button_id in range(item_button_start_value, item_button_maximum_value + 1, item_button_step_value)]
        debug_message(f"Derived ITEM_INFO_BUTTONS up to {item_button_maximum_value} (count={len(ITEM_INFO_BUTTONS)})", 68)

    # Probe categories first, then iterate across all potential item-info buttons
    number_of_items_captured = 0
    categories_iteration_list = list(ACTIVE_CATEGORIES.items()) if ACTIVE_CATEGORIES else [(None, button_id) for button_id in CATEGORY_BUTTONS]
    for category_name, category_button_id in categories_iteration_list:
        # Ensure a gump is present before interacting
        if wait_for_gump(500) == 0:
            crafting_gump_id = open_crafting_gump()
            if crafting_gump_id == 0:
                debug_message("No gump present; cannot proceed with category selection", 33)
                break
        crafting_gump_id = send_action_and_wait(crafting_gump_id, category_button_id)
        if crafting_gump_id == 0:
            break
        # Allow the category page to render before probing item buttons
        pause_ms(ITEM_BUTTON_CLICK_PAUSE_MS // 2)
        # Ensure a results bucket exists for this category (prefer human-readable name)
        category_key = category_name if category_name else str(category_button_id)
        if category_key not in crawl_results['categories']:
            crawl_results['categories'][category_key] = { 'button': category_button_id, 'items': [] }
        # Detect per-category item-button series if offset differs; fallback to global series
        detected_series, crafting_gump_id = detect_item_button_series_for_category(crafting_gump_id, category_button_id)
        series_to_use = detected_series if (detected_series and len(detected_series) > 0) else ITEM_INFO_BUTTONS
        if not detected_series:
            debug_message(f"Using global item button series for category {category_key}", 47)
        # Iterate through all discovered item-info buttons
        consecutive_missing_or_noninfo = 0
        consecutive_unchanged_info = 0
        previous_info_text_lines = None
        for item_info_button_id in series_to_use:
            # Use a longer pause for item info panels; they render slower than category switches
            current_gump_id = send_action_and_wait(crafting_gump_id, item_info_button_id, wait_ms=ITEM_BUTTON_CLICK_PAUSE_MS)
            if current_gump_id == 0:
                break
            gump_snapshot_entry = snap_gump_to_entry(current_gump_id)
            if not looks_like_item_info(gump_snapshot_entry):
                # Retry once with a longer wait in case of slow render
                current_gump_id = send_action_and_wait(current_gump_id, item_info_button_id, wait_ms=ITEM_BUTTON_CLICK_PAUSE_MS + 150)
                if current_gump_id == 0:
                    break
                gump_snapshot_entry = snap_gump_to_entry(current_gump_id)
            if looks_like_item_info(gump_snapshot_entry):
                # Reset the non-info counter
                consecutive_missing_or_noninfo = 0
                # Detect unchanged info panels
                cur_lines = gump_snapshot_entry.get('text_lines') or []
                if previous_info_text_lines is not None and cur_lines == previous_info_text_lines:
                    consecutive_unchanged_info += 1
                else:
                    consecutive_unchanged_info = 0
                previous_info_text_lines = cur_lines
                if consecutive_unchanged_info >= MAX_MISSING_IN_ROW:
                    debug_message(f"Detected {consecutive_unchanged_info} unchanged info panels in a row in category {category_key}; skipping to next category", 53)
                    # Close and break out of this category
                    exit_gump(current_gump_id, retries=2)
                    break
                register_known(gump_snapshot_entry, crawl_results)
                # Debug: show token stream in alternating colors for tricky categories
                try:
                    debug_tokens_striped(category_key, gump_snapshot_entry.get('text_lines'))
                except Exception:
                    pass
                # Build handler candidates and score to select best parsing result
                best_parsed = None
                best_score = None
                best_tag = None
                for tag, seq in build_handler_candidates(category_key, gump_snapshot_entry):
                    try:
                        parsed = _parse_with_lines(gump_snapshot_entry, seq, category_key)
                        score = _score_parsed(parsed)
                        if (best_parsed is None) or (score > best_score):
                            best_parsed, best_score, best_tag = parsed, score, tag
                    except Exception:
                        continue
                # Fallback to baseline parser
                if not best_parsed:
                    try:
                        best_parsed = parse_item_info_gump(gump_snapshot_entry, category_key) or {}
                    except Exception:
                        best_parsed = {}
                # Attach originating category key for downstream consumers
                parsed_item_details = best_parsed if isinstance(best_parsed, dict) else {}
                parsed_item_details['category'] = category_key
                # Track which buttons led here
                try:
                    parsed_item_details['button_category'] = int(category_button_id)
                except Exception:
                    parsed_item_details['button_category'] = None
                parsed_item_details['button_info'] = int(item_info_button_id)
                try:
                    parsed_item_details['button_make'] = int(item_info_button_id) - 1
                except Exception:
                    parsed_item_details['button_make'] = None
                # Skip sparse/under-parsed items with a warning
                if is_sparse_parsed_item(parsed_item_details):
                    # Build a compact preview of found text to aid debugging
                    try:
                        preview_tokens = [_strip_tags(x) for x in (gump_snapshot_entry.get('text_lines') or []) if _strip_tags(x)]
                        preview = ', '.join(preview_tokens[:12])
                    except Exception:
                        preview = ''
                    debug_message(f"Skipped sparse item detail (btn {item_info_button_id}) in category {category_key}: too many null fields | found: {preview}", 53)
                    # Close the info gump to avoid getting stuck, then restore base and reselect
                    exit_gump(current_gump_id, retries=2)
                    crafting_gump_id = open_crafting_gump()
                    if crafting_gump_id == 0:
                        break
                    crafting_gump_id = send_action_and_wait(crafting_gump_id, category_button_id)
                    pause_ms(ITEM_BUTTON_CLICK_PAUSE_MS // 2)
                    # Continue scanning; treat as seen info so do not bump non-info counter
                    continue
                crawl_results['categories'][category_key]['items'].append({
                    'button': item_info_button_id,
                    'detail': gump_snapshot_entry,
                    'parsed': parsed_item_details,
                    'parse_meta': {
                        'strategy': best_tag,
                        'score': best_score,
                    }
                })
                debug_message(f"Captured item detail via cat {category_key} (btn {category_button_id}) item-btn {item_info_button_id}", 68)
                # Close the info gump to ensure we return to a clean state; double-exit for safety
                exit_gump(current_gump_id, retries=2)
                # Reopen base crafting gump and reselect current category before next item
                crafting_gump_id = open_crafting_gump()
                if crafting_gump_id == 0:
                    break
                crafting_gump_id = send_action_and_wait(crafting_gump_id, category_button_id)
                pause_ms(ITEM_BUTTON_CLICK_PAUSE_MS // 2)
                number_of_items_captured += 1
                if number_of_items_captured >= max_items:
                    break
            else:
                # Not an item info gump; log occasionally for visibility
                debug_message(f"Non-info gump for item-btn {item_info_button_id} in cat {category_key}", 47)
                consecutive_missing_or_noninfo += 1
                if consecutive_missing_or_noninfo >= MAX_MISSING_IN_ROW:
                    debug_message(f"Encountered {consecutive_missing_or_noninfo} non-info panels in a row in category {category_key}; skipping to next category", 53)
                    break
        # Attempt a clean exit/reset before moving to the next category
        exit_gump(crafting_gump_id, retries=3)
        # Re-open for next loop iteration if we continue
        if number_of_items_captured < max_items:
            crafting_gump_id = open_crafting_gump()
            if crafting_gump_id == 0:
                break
        if number_of_items_captured >= max_items:
            break

    # Final exit attempts to ensure reset state
    exit_gump(crafting_gump_id, retries=3)

    return crawl_results

def save_results(results):
    if not DEBUG_TO_JSON:
        return
    try:
        # Save under project's data/ directory next to scripts/
        scripts_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(scripts_dir)
        data_dir = os.path.join(project_root, 'data')
        try:
            os.makedirs(data_dir, exist_ok=True)
        except Exception:
            pass
        dt = time.strftime("%Y%m%d%H%M%S", time.localtime())
        # Prefer the crafting type from results for flexibility; fallback to current toggle
        ct_key = (results.get('crafting_type_key') if isinstance(results, dict) else None) or CRAFTING_TYPE_KEY
        filename = f"gump_crafting_{ct_key}_{dt}.json"
        file_path = os.path.join(data_dir, filename)

        # Shape the output according to toggles
        if OUTPUT_ITEM and not OUTPUT_BASE:
            # Flatten to a succinct list of parsed items (no gump/base data)
            items_only = []
            try:
                cats = results.get('categories', {})
                for _, cat_data in cats.items():
                    for it in (cat_data.get('items') or []):
                        parsed = (it or {}).get('parsed') or {}
                        if not parsed:
                            continue
                        nm = (parsed.get('name') or '').strip().lower()
                        if nm == _GLOBAL_CHAT_LINE_LOWER:
                            # Skip leaked system banner lines entirely
                            continue
                        items_only.append(build_item_output(parsed))
            except Exception:
                pass
            payload = {
                'crafting_type': results.get('crafting_type') or CRAFTING_TYPE,
                'crafting_type_key': results.get('crafting_type_key') or CRAFTING_TYPE_KEY,
                'items': items_only
            }
        elif OUTPUT_BASE and not OUTPUT_ITEM:
            # Include base/session and category scaffolding without items
            shaped = {
                'session_start': results.get('session_start'),
                'tool_item_ids': results.get('tool_item_ids'),
                'crafting_type': results.get('crafting_type') or CRAFTING_TYPE,
                'crafting_type_key': results.get('crafting_type_key') or CRAFTING_TYPE_KEY,
                'base_gump': results.get('base_gump'),
                'known_gumps': results.get('known_gumps', {})
            }
            # categories without items
            cats_out = {}
            for cat_key, cat_data in (results.get('categories') or {}).items():
                cats_out[cat_key] = {
                    'button': cat_data.get('button'),
                    'items': []
                }
            shaped['categories'] = cats_out
            payload = shaped
        else:
            # Default: include full structure
            payload = results

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(to_json(payload, indent=4))
        debug_message(f"Wrote crafting gump data to data/{filename}", 63)
    except Exception as e:
        debug_message(f"Failed to write crafting JSON: {e}", 33)

def main():
    # Default: run the focused troublesome-recipes extractor (single item per category)
    #results = test_extract_troublesome_recipes()
    results = crawl_once(MAX_ITEMS_TO_EXTRACT)
    save_results(results)

if __name__ == "__main__":
    main()
