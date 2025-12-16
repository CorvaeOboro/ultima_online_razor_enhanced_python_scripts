""" 
ITEM Runebook Reorder Runes - a Razor Enhanced Python script for Ultima Online

Process:
1) Open the runebook (ItemID 0x0EFA)
2) Remove all runes out of the runebook by repeatedly:
   - opening the runebook
   - pressing the "Remove from Runebook" gump button
   - closing the runebook gump
3) Inspect the properties of backpack runes (ItemID 0x1F14)
4) Order runes by preferred fuzzy-name matching (substring/contains)
5) Close the runebook gump (required before moving items onto the book)
6) Move runes back into the runebook in the final order

UOR mapping :
- Runebook gump id: 0x59
- Remove from Runebook button: 200

VERSION::20251215
"""

DEBUG_MODE = True

# priority fuzzy matching (case-insensitive substring match).
PREFERRED_RUNE_PATTERNS = {
    "Bank": ["bank"],
    "Home": ["home", "house"],
    "OgreValley": ["ogre", "ogrevalley"],
    "Gnoll": ["gnoll"],
    "StygianKeep": ["stygian"],
    "WhiteStoneCastle": ["white"],
    "FrozenIsle": ["frozen"],
}

# IMPORTANT: Razor Enhanced commonly runs IronPython, where dict key iteration order is NOT guaranteed.
# This list defines the priority order used by matching + ordering.
PREFERRED_BUCKET_ORDER = [
    "Bank",
    "Home",
    "OgreValley",
    "Gnoll",
    "StygianKeep",
    "WhiteStoneCastle",
    "FrozenIsle",
]

# Controls
CLOSE_AND_REOPEN_AFTER_EACH_REMOVE = True
ONLY_READD_RUNES_REMOVED_FROM_BOOK = False
ADD_UNMATCHED_RUNES_AT_END = False

RUNEBOOK_ID = 0x0EFA
RUNEBOOK_NAME = "Runebook"
RUNE_ITEM_ID = 0x1F14
RUNEBOOK_GUMP_ID = 0x59 # UOR runebook
MAX_RUNES_IN_BOOK = 16
REMOVE_FROM_RUNEBOOK_BUTTON_ID = 200 # "Drop Rune" button on the second page
RUNEBOOK_GUMP_IDS = [RUNEBOOK_GUMP_ID, 1431013363] # gump ids from UOR or AOS
BUTTON_GOTO_REMOVE_PAGE = None

# Timing
USE_RUNEBOOK_DELAY_MS = 250
GUMP_WAIT_TIMEOUT_MS = 5000
AFTER_GUMP_ACTION_DELAY_MS = 600
REMOVE_FROM_RUNEBOOK_DELAY_MS = 900
MOVE_RUNE_DELAY_MS = 600

# =====================================================================

def debug_message(msg, color=68):
    if DEBUG_MODE:
        try:
            Misc.SendMessage(f"[RUNEBOOK-REORDER] {msg}", color)
        except Exception:
            pass


def _to_str(v):
    try:
        return str(v) if v is not None else ""
    except Exception:
        return ""


def _norm(s):
    s = _to_str(s).strip().lower()
    s = " ".join(s.split())
    return s


def find_runebook():
    if not Player.Backpack:
        return None

    books = Items.FindAllByID(RUNEBOOK_ID, -1, Player.Backpack.Serial, -1)
    for b in books:
        try:
            if getattr(b, "Name", None) == RUNEBOOK_NAME:
                return b
        except Exception:
            pass

    return books[0] if books and len(books) > 0 else None


def _looks_like_runebook_gump(lines):
    if not lines:
        return False
    for needle in ["Drop rune", "Set default", "Charges:", "Max Charges:"]:
        try:
            if needle in lines:
                return True
        except Exception:
            pass
    return False


def _scan_for_runebook_gump_id():
    try:
        gids = Gumps.AllGumpIDs()
    except Exception:
        gids = None

    if not gids:
        return None

    for gid in gids:
        try:
            gid_int = int(gid)
        except Exception:
            continue

        try:
            if not Gumps.WaitForGump(gid_int, 50):
                continue
        except Exception:
            continue

        lines = _get_runebook_lines(gid_int)
        if _looks_like_runebook_gump(lines):
            return gid_int

    return None


def wait_for_runebook_gump(timeout_ms):
    for gid in RUNEBOOK_GUMP_IDS:
        try:
            if Gumps.WaitForGump(gid, int(timeout_ms)):
                return gid
        except Exception:
            pass

    # Fallback: scan open gumps for one that looks like a runebook
    return _scan_for_runebook_gump_id()


def _get_runebook_lines(gump_id):
    try:
        Gumps.WaitForGump(gump_id, 200)
    except Exception:
        pass
    try:
        lines = Gumps.LastGumpGetLineList()
        return list(lines) if lines else []
    except Exception:
        return []


def close_runebook_gump():
    for gid in (RUNEBOOK_GUMP_IDS or []):
        try:
            Gumps.CloseGump(int(gid))
        except Exception:
            pass

    try:
        current = int(Gumps.CurrentGump())
        if current and current not in (RUNEBOOK_GUMP_IDS or []):
            Gumps.CloseGump(int(current))
    except Exception:
        pass


def _extract_rune_names_from_runebook_lines(lines):
    if not lines:
        return []

    if len(lines) <= 3:
        return []

    line_list = lines[3:]

    end_index = 0
    for i in range(0, len(line_list)):
        if line_list[i] == "Set default" or line_list[i] == "Drop rune":
            end_index += 1
        else:
            break

    end_index += 2

    rune_names = line_list[end_index : (end_index + MAX_RUNES_IN_BOOK)]
    rune_names = [n for n in rune_names if n and n != "Empty"]
    return rune_names


def get_rune_count_in_runebook(runebook):
    Items.UseItem(runebook)
    Misc.Pause(USE_RUNEBOOK_DELAY_MS)

    gid = wait_for_runebook_gump(GUMP_WAIT_TIMEOUT_MS)
    if not gid:
        debug_message("Runebook gump not found (too far / wrong gump id).", 33)
        return None

    lines = _get_runebook_lines(gid)
    rune_names = _extract_rune_names_from_runebook_lines(lines)

    try:
        Gumps.CloseGump(int(gid))
    except Exception:
        pass

    return len(rune_names)


def remove_all_runes_from_runebook(runebook):
    def _scan_backpack_rune_serials():
        return set(int(r.Serial) for r in Items.FindAllByID(RUNE_ITEM_ID, -1, Player.Backpack.Serial, -1) or [])

    before_serials = set()
    if ONLY_READD_RUNES_REMOVED_FROM_BOOK:
        before_serials = _scan_backpack_rune_serials()

    safety = MAX_RUNES_IN_BOOK
    removed_any = False
    removed_serials = set()

    if CLOSE_AND_REOPEN_AFTER_EACH_REMOVE:
        for _ in range(safety):
            Items.UseItem(runebook)
            Misc.Pause(USE_RUNEBOOK_DELAY_MS)

            gid = wait_for_runebook_gump(GUMP_WAIT_TIMEOUT_MS)
            if not gid:
                debug_message("Runebook gump not found while removing runes.", 33)
                break

            lines = _get_runebook_lines(gid)
            if BUTTON_GOTO_REMOVE_PAGE is not None and ("Drop rune" not in lines):
                try:
                    Gumps.SendAction(int(gid), int(BUTTON_GOTO_REMOVE_PAGE))
                    Misc.Pause(AFTER_GUMP_ACTION_DELAY_MS)
                except Exception:
                    pass

            pre = _scan_backpack_rune_serials()
            try:
                Gumps.SendAction(int(gid), int(REMOVE_FROM_RUNEBOOK_BUTTON_ID))
            except Exception as e:
                debug_message(f"Failed to press Remove from Runebook (button {int(REMOVE_FROM_RUNEBOOK_BUTTON_ID)}): {e}", 33)
                close_runebook_gump()
                break

            Misc.Pause(REMOVE_FROM_RUNEBOOK_DELAY_MS)

            try:
                if Target.HasTarget():
                    Target.Cancel()
            except Exception:
                pass

            post = _scan_backpack_rune_serials()
            new_serials = post - pre
            if not new_serials:
                close_runebook_gump()
                debug_message("Runebook appears empty.", 67)
                break

            removed_any = True
            removed_serials |= new_serials

            close_runebook_gump()
            Misc.Pause(AFTER_GUMP_ACTION_DELAY_MS)
    else:
        Items.UseItem(runebook)
        Misc.Pause(USE_RUNEBOOK_DELAY_MS)

        gid = wait_for_runebook_gump(GUMP_WAIT_TIMEOUT_MS)
        if not gid:
            debug_message("Runebook gump not found while removing runes.", 33)
        else:
            lines = _get_runebook_lines(gid)
            if BUTTON_GOTO_REMOVE_PAGE is not None and ("Drop rune" not in lines):
                try:
                    Gumps.SendAction(int(gid), int(BUTTON_GOTO_REMOVE_PAGE))
                    Misc.Pause(AFTER_GUMP_ACTION_DELAY_MS)
                except Exception:
                    pass

            for _ in range(safety):
                pre = _scan_backpack_rune_serials()
                try:
                    Gumps.SendAction(int(gid), int(REMOVE_FROM_RUNEBOOK_BUTTON_ID))
                except Exception as e:
                    debug_message(f"Failed to press Remove from Runebook (button {int(REMOVE_FROM_RUNEBOOK_BUTTON_ID)}): {e}", 33)
                    break

                Misc.Pause(REMOVE_FROM_RUNEBOOK_DELAY_MS)

                try:
                    if Target.HasTarget():
                        Target.Cancel()
                except Exception:
                    pass

                post = _scan_backpack_rune_serials()
                new_serials = post - pre
                if not new_serials:
                    debug_message("Runebook appears empty.", 67)
                    break

                removed_any = True
                removed_serials |= new_serials

            close_runebook_gump()
            Misc.Pause(AFTER_GUMP_ACTION_DELAY_MS)

    after_serials = _scan_backpack_rune_serials()
    candidate_serials = removed_serials if ONLY_READD_RUNES_REMOVED_FROM_BOOK else after_serials

    if removed_any:
        debug_message(f"Remove complete. Candidate runes: {len(candidate_serials)}", 67)
    else:
        debug_message("No runes were removed (book may already be empty, or button ids differ).", 53)

    return candidate_serials


def get_rune_display_name(rune_item):
    try:
        Items.WaitForProps(rune_item, 1000)
    except Exception:
        pass

    try:
        props = Items.GetPropStringList(int(getattr(rune_item, "Serial", 0))) or []
    except Exception:
        props = []

    try:
        for p in (props or []):
            ps = _to_str(p)
            if not ps:
                continue
            low = ps.lower()
            needle = "a recall rune for "
            if needle in low:
                start = low.index(needle) + len(needle)
                loc = ps[start:]
                loc = loc.split(" (")[0].strip()
                if loc:
                    return loc
    except Exception:
        pass

    try:
        s = Items.GetPropStringByIndex(rune_item, 0)
        if s:
            return _to_str(s)
    except Exception:
        pass

    try:
        nm = getattr(rune_item, "Name", None)
        if nm:
            return _to_str(nm)
    except Exception:
        pass

    return "Recall Rune"


def build_rune_entries(serials):
    entries = []

    serials = list(serials) if serials else []
    for s in serials:
        item = Items.FindBySerial(int(s))
        if not item:
            continue
        if getattr(item, "ItemID", None) != RUNE_ITEM_ID:
            continue

        name = get_rune_display_name(item)
        props = []
        try:
            Items.WaitForProps(int(item.Serial), 1000)
        except Exception:
            pass
        try:
            props = Items.GetPropStringList(int(item.Serial)) or []
        except Exception:
            props = []

        match_text = " ".join([_to_str(name)] + [ _to_str(p) for p in (props or []) ])

        entries.append({
            "serial": int(item.Serial),
            "name": name,
            "name_norm": _norm(name),
            "props": [ _to_str(p) for p in (props or []) ],
            "match_text_norm": _norm(match_text),
        })

    return entries


def match_priority_bucket(entry):
    match_text_norm = entry.get("match_text_norm", "") or entry.get("name_norm", "")
    if not match_text_norm:
        return None

    bucket_order = list(PREFERRED_BUCKET_ORDER or [])
    for k in (PREFERRED_RUNE_PATTERNS or {}).keys():
        if k not in bucket_order:
            bucket_order.append(k)

    for bucket_name in bucket_order:
        patterns = (PREFERRED_RUNE_PATTERNS or {}).get(bucket_name, [])
        for p in (patterns or []):
            p_norm = _norm(p)
            if p_norm and (p_norm in match_text_norm):
                return bucket_name

    return None


def order_runes(entries):
    used = set()
    ordered = []

    bucket_order = list(PREFERRED_BUCKET_ORDER or [])
    for k in (PREFERRED_RUNE_PATTERNS or {}).keys():
        if k not in bucket_order:
            bucket_order.append(k)

    bucketed = {k: [] for k in bucket_order}
    unmatched = []

    for e in entries:
        b = match_priority_bucket(e)
        if b is None:
            unmatched.append(e)
        else:
            bucketed[b].append(e)

    for bucket_name in bucket_order:
        group = bucketed.get(bucket_name, [])
        group.sort(key=lambda x: x.get("name_norm", ""))
        for e in group:
            if e["serial"] in used:
                continue
            used.add(e["serial"])
            ordered.append(e)

    if ADD_UNMATCHED_RUNES_AT_END:
        unmatched.sort(key=lambda x: x.get("name_norm", ""))
        for e in unmatched:
            if e["serial"] in used:
                continue
            used.add(e["serial"])
            ordered.append(e)

    return ordered


def move_runes_into_runebook(runebook, ordered_entries):
    moved = 0

    # Required: runebook gump must be closed before moving items onto the book.
    close_runebook_gump()

    for i, e in enumerate(ordered_entries, 1):
        close_runebook_gump()
        item = Items.FindBySerial(int(e["serial"]))
        if not item:
            continue

        try:
            Items.Move(item.Serial, runebook.Serial, 0)
            moved += 1
            debug_message(f"Moved rune into runebook {i} of {len(ordered_entries)}: {e.get('name','')} (0x{int(item.Serial):X})", 67)
            Misc.Pause(MOVE_RUNE_DELAY_MS)
        except Exception as ex:
            debug_message(f"Failed to move rune '{e.get('name','')}' into runebook: {ex}", 33)
            Misc.Pause(200)

    return moved


def main():
    runebook = find_runebook()
    if not runebook:
        debug_message("No runebook found in backpack.", 33)
        return

    debug_message(f"Using runebook: {_to_str(getattr(runebook,'Name', 'Runebook'))} (0x{int(runebook.Serial):X})", 67)

    candidate_serials = remove_all_runes_from_runebook(runebook)
    if not candidate_serials:
        debug_message("No runes available to move into runebook.", 33)
        return

    debug_message(f"Candidate rune serials: {len(list(candidate_serials))}", 67)

    entries = build_rune_entries(candidate_serials)
    if not entries:
        debug_message("No valid rune entries found after removing.", 33)
        return

    for e in entries:
        try:
            debug_message(f"Candidate rune: 0x{int(e.get('serial', 0)):X} | {e.get('name','')}", 67)
            for p in (e.get("props") or []):
                if p:
                    debug_message(f"  {p}", 67)
        except Exception:
            pass

    for e in entries:
        try:
            bucket = match_priority_bucket(e)
            e["bucket"] = bucket
            debug_message(f"Match: 0x{int(e.get('serial', 0)):X} | {e.get('name','')} -> {_to_str(bucket)}", 67)
        except Exception:
            pass

    ordered = order_runes(entries)

    if not ordered:
        debug_message("Final ordered list is empty. Likely no matches and ADD_UNMATCHED_RUNES_AT_END=False.", 33)
        return

    for i, e in enumerate(ordered, 1):
        try:
            debug_message(f"Order {i}: 0x{int(e.get('serial', 0)):X} | {e.get('name','')}", 67)
        except Exception:
            pass

    debug_message(f"Moving {len(ordered)} rune(s) into runebook...", 67)

    # Required before moving runes onto the runebook.
    close_runebook_gump()

    moved = move_runes_into_runebook(runebook, ordered)
    debug_message(f"Done. Moved {moved} rune(s).", 67)


if __name__ == "__main__":
    main()
