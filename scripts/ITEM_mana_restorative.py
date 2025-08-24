"""
ITEM mana restorative - a Razor Enhanced Python script for Ultima Online

Consumes a mana restorative item , based on missing mana:
1) Blue Mana Food ( fish steak or mushroom ) (by hue) if missing >= 10 (+10)
2) Greater Mana Potion if current mana < 50 and missing >= 27 (+27)

Optional Emote after consuming

HOTKEY:: W
VERSION:: 20250822
"""

DEBUG_MODE = False # Prints messages if true
EMOTE_GIGGLE_ON_POTION = True # Toggle to say an emote when a mana potion is used
EMOTE_COMMAND = "[emote giggle"

# Known base item IDs
MANA_FOOD_ID = [0x097A, 0x097B] # fishsteaks , mushrooms
# Candidate hues for "blue"  , Colors are stored as hexidecimal IDs 
BLUE_HUES = [0x0825,0x0005, 0x0008, 0x051E, 0x0492]  # some blue-ish hues

# Shard-specific mana potion configuration
# Greater Mana potion (example): ItemID 0x0F0D, Hue 0x0387
MANA_POTION_IDS = [0x0F0D]
MANA_POTION_HUES = [0x0387]

# Restoration amounts (tune per shard if needed)
MANA_FOOD_RESTORE = 10
MANA_POTION_RESTORE = 27

# Policy: only use big potion when current mana is below this threshold
BIG_POTION_MIN_MANA = 50

# Delays
BASE_DELAY_MS = 700
COOLDOWN_MS = 2500   # minimal time between successful consumes
TIMEOUT_MS = 4000    # max wait after use to consider it processed

def debug_message(msg, color=67):
    if DEBUG_MODE:
        try:
            Misc.SendMessage(f"[ITEM_MANA_RESTORE] {msg}", color)
        except Exception:
            print(f"[ITEM_MANA_RESTORE] {msg}")

def pause_ms(ms):
    # Fixed delay; no jitter per user preference
    Misc.Pause(int(ms))

def find_item(ids, hues=None):
    """Return first matching item in backpack for any id, optionally filtering by hue list."""
    if not ids:
        return None
    for id_ in ids:
        try:
            itm = Items.FindByID(id_, -1, Player.Backpack.Serial)
        except Exception:
            itm = None
        if not itm:
            continue
        # Items.FindByID may return a single item or a list depending on RE version
        candidates = itm if isinstance(itm, list) else [itm]
        for c in candidates:
            try:
                if hues is None or int(c.Hue) in hues:
                    return c
            except Exception:
                continue
    return None

def get_mana_values():
    try:
        cur = int(Player.Mana)
        mx = int(Player.ManaMax)
        return max(cur, 0), max(mx, 0)
    except Exception:
        return 0, 0

def consume_mana_priority():
    cur, mx = get_mana_values()
    if mx <= 0:
        debug_message("Mana values unavailable.", 33)
        return

    label, item = choose_item_to_consume(cur, mx)
    if not item:
        # Optional: log why nothing chosen
        missing = max(0, mx - cur)
        if missing < MANA_FOOD_RESTORE:
            debug_message(f"Missing mana ({missing}) is below smallest restore amount; skipping.", 53)
        else:
            debug_message("No eligible mana restorative found (avoiding overcap or none present).", 33)
        return

    if use_item_and_wait(item, label, cur):
        if EMOTE_GIGGLE_ON_POTION and label == "Mana Potion":
            say_emote()
        return
    else:
        pause_ms(BASE_DELAY_MS)
        debug_message(f"Failed to use {label}.", 33)

def choose_item_to_consume(cur_mana, max_mana):
    """Return a tuple (label, item) or (None, None) following rules:
    - Use mana food (+10) if missing >= 10 and available
    - Use big mana potion (+27) only if cur_mana < 50 and missing >= 27
    - Never use an item if it would exceed max mana
    - Fallback: if big potion not allowed/available, use fish if eligible
    """
    missing = max(0, max_mana - cur_mana)
    if missing <= 0:
        return None, None

    # Try fish steak when it won't overcap
    manafood_ok = missing >= MANA_FOOD_RESTORE
    manafood_item = find_item(MANA_FOOD_ID, BLUE_HUES) if manafood_ok else None

    # Try big mana potion only if under threshold and won't overcap
    potion_allowed = cur_mana < BIG_POTION_MIN_MANA and missing >= MANA_POTION_RESTORE
    potion_item = find_item(MANA_POTION_IDS, MANA_POTION_HUES) if potion_allowed else None

    # Prefer potion when allowed (for larger deficits), else fish
    if potion_item:
        return "Mana Potion", potion_item
    if manafood_item:
        return "Blue Fish Steak", manafood_item

    # No eligible items without overcapping
    return None, None

def use_item_and_wait(item, label, pre_mana):
    """Use the item, pause briefly, and confirm by mana increase > 9."""
    if item is None:
        return False
    try:
        debug_message(f"Using {label} (ID=0x{item.ItemID:X}, Hue=0x{getattr(item, 'Hue', 0):X})", 68)
    except Exception:
        debug_message(f"Using {label}", 68)
    try:
        Items.UseItem(item)
    except Exception as e:
        debug_message(f"UseItem error: {e}", 33)
        return False

    # Pause once and verify mana gain
    pause_ms(BASE_DELAY_MS)
    try:
        cur_after = int(Player.Mana)
    except Exception:
        cur_after = pre_mana
    return (cur_after - pre_mana) > 9

def say_emote():
    """Says the in-game emote command if available."""
    try:
        # Prefer in-game speech so the command is executed server-side
        if hasattr(Player, 'ChatSay'):
            try:
                Player.ChatSay(EMOTE_COMMAND)
                return
            except Exception:
                pass
    except Exception:
        try:
            print("[MANA] emote command: ", EMOTE_COMMAND)
        except Exception:
            pass

def main():
    consume_mana_priority()

if __name__ == "__main__":
    main()
