"""
ITEM Use Spell Scrolls All - a Razor Enhanced Python Script for Ultima Online

Finds and uses all Magery spell scrolls either in a targeted container
or in the player's backpack, and adds them to the equipped spellbook
via the scroll's context menu action "Add To Spellbook".

VERSION::20250918
"""

DEBUG_MODE = False  # Set to False to suppress debug output
SPELLBOOK_ID = 0x0EFA  # Default spellbook ItemID

USE_DELAY_MS = 800  # Delay in ms between using scrolls
TARGET_TIMEOUT_MS = 3000  # Wait up to 3 seconds for target cursor
BOOK_LAYER = "LeftHand"  # checks equiped for base blessed spell book , if not equipped checks backpack
JOURNAL_MSG_ALREADY = "That spell is already present in that spellbook."

# Magic Scrolls - All spell scrolls organized by circle
MAGIC_SCROLLS = [
    # Circle 1 Scrolls
    {"name": "1_Clumsy", "id": 0x1F2E, "hue": None},
    {"name": "1_CreateFood", "id": 0x1F2F, "hue": None},
    {"name": "1_Feeblemind", "id": 0x1F30, "hue": None},
    {"name": "1_Heal", "id": 0x1F31, "hue": None},
    {"name": "1_MagicArrow", "id": 0x1F32, "hue": None},
    {"name": "1_NightSight", "id": 0x1F33, "hue": None},
    {"name": "1_ReactiveArmor", "id": 0x1F2D, "hue": None},
    {"name": "1_Weaken", "id": 0x1F34, "hue": None},
    # Circle 2 Scrolls
    {"name": "2_Agility", "id": 0x1F35, "hue": None},
    {"name": "2_Cunning", "id": 0x1F36, "hue": None},
    {"name": "2_Cure", "id": 0x1F37, "hue": None},
    {"name": "2_Harm", "id": 0x1F38, "hue": None},
    {"name": "2_MagicTrap", "id": 0x1F39, "hue": None},
    {"name": "2_MagicUnTrap", "id": 0x1F3A, "hue": None},
    {"name": "2_Protection", "id": 0x1F3B, "hue": None},
    {"name": "2_Strength", "id": 0x1F3C, "hue": None},
    # Circle 3 Scrolls
    {"name": "3_Bless", "id": 0x1F3D, "hue": None},
    {"name": "3_Fireball", "id": 0x1F3E, "hue": None},
    {"name": "3_MagicLock", "id": 0x1F3F, "hue": None},
    {"name": "3_Poison", "id": 0x1F40, "hue": None},
    {"name": "3_Telekinisis", "id": 0x1F41, "hue": None},
    {"name": "3_Teleport", "id": 0x1F42, "hue": None},
    {"name": "3_Unlock", "id": 0x1F43, "hue": None},
    {"name": "3_WallOfStone", "id": 0x1F44, "hue": None},
    # Circle 4 Scrolls
    {"name": "4_ArchCure", "id": 0x1F45, "hue": None},
    {"name": "4_ArchProtection", "id": 0x1F46, "hue": None},
    {"name": "4_Curse", "id": 0x1F47, "hue": None},
    {"name": "4_FireField", "id": 0x1F48, "hue": None},
    {"name": "4_GreaterHeal", "id": 0x1F49, "hue": None},
    {"name": "4_Lightning", "id": 0x1F4A, "hue": None},
    {"name": "4_ManaDrain", "id": 0x1F4B, "hue": None},
    {"name": "4_Recall", "id": 0x1F4C, "hue": None},
    # Circle 5 Scrolls
    {"name": "5_BladeSpirits", "id": 0x1F4D, "hue": None},
    {"name": "5_DispelField", "id": 0x1F4E, "hue": None},
    {"name": "5_Incognito", "id": 0x1F4F, "hue": None},
    {"name": "5_MagicReflect", "id": 0x1F50, "hue": None},
    {"name": "5_MindBlast", "id": 0x1F51, "hue": None},
    {"name": "5_Paralyze", "id": 0x1F52, "hue": None},
    {"name": "5_PoisonField", "id": 0x1F53, "hue": None},
    {"name": "5_SummonCreature", "id": 0x1F54, "hue": None},
    # Circle 6 Scrolls
    {"name": "6_Dispel", "id": 0x1F55, "hue": None},
    {"name": "6_EnergyBolt", "id": 0x1F56, "hue": None},
    {"name": "6_Explosion", "id": 0x1F57, "hue": None},
    {"name": "6_Invisibility", "id": 0x1F58, "hue": None},
    {"name": "6_Mark", "id": 0x1F59, "hue": None},
    {"name": "6_MassCurse", "id": 0x1F5A, "hue": None},
    {"name": "6_ParalyzeField", "id": 0x1F5B, "hue": None},
    {"name": "6_Reveal", "id": 0x1F5C, "hue": None},
    # Circle 7 Scrolls
    {"name": "7_ChainLightning", "id": 0x1F5D, "hue": None},
    {"name": "7_EnergyField", "id": 0x1F5E, "hue": None},
    {"name": "7_Flamestrike", "id": 0x1F5F, "hue": None},
    {"name": "7_GateTravel", "id": 0x1F60, "hue": None},
    {"name": "7_ManaVampire", "id": 0x1F61, "hue": None},
    {"name": "7_MassDispel", "id": 0x1F62, "hue": None},
    {"name": "7_MeteorSwarm", "id": 0x1F63, "hue": None},
    {"name": "7_Polymorph", "id": 0x1F64, "hue": None},
    # Circle 8 Scrolls
    {"name": "8_Earthquake", "id": 0x1F65, "hue": None},
    {"name": "8_EnergyVortex", "id": 0x1F66, "hue": None},
    {"name": "8_Resurrection", "id": 0x1F67, "hue": None},
    {"name": "8_SummonAirElemental", "id": 0x1F68, "hue": None},
    {"name": "8_SummonDaemon", "id": 0x1F69, "hue": None},
    {"name": "8_SummonEarthElemental", "id": 0x1F6A, "hue": None},
    {"name": "8_SummonFireElemental", "id": 0x1F6B, "hue": None},
    {"name": "8_SummonWaterElemental", "id": 0x1F6C, "hue": None},
]

SCROLL_ITEM_IDS = [entry['id'] for entry in MAGIC_SCROLLS]

def debug_message(msg, color=68):
    if DEBUG_MODE:
        Misc.SendMessage(f"[SpellScrolls] {msg}", color)

def is_blessed_spellbook(item):
    """Return True if item is a blessed spellbook named 'Spellbook'."""
    try:
        if not item or item.ItemID != SPELLBOOK_ID:
            return False
        # Name check (fallback)
        name_ok = False
        try:
            name = getattr(item, 'Name', None)
            if name:
                name_ok = 'spellbook' in name.lower()
        except Exception:
            name_ok = False
        # Properties check for 'Blessed'
        blessed_ok = False
        try:
            props = Items.GetPropStringList(item)
            if props:
                blessed_ok = any('blessed' in p.lower() for p in props)
        except Exception:
            blessed_ok = False
        return name_ok and blessed_ok
    except Exception:
        return False

def find_best_spellbook():
    """Find the best spellbook to target: prefer blessed 'Spellbook' in hands, else in backpack, else any equipped spellbook."""
    candidates = []
    # Hands
    left = Player.GetItemOnLayer("LeftHand")
    right = Player.GetItemOnLayer("RightHand")
    for itm in [left, right]:
        if itm and itm.ItemID == SPELLBOOK_ID:
            candidates.append(itm)
    # Backpack
    try:
        bp = Items.FindBySerial(Player.Backpack.Serial)
        for itm in (bp.Contains if bp and bp.Contains else []):
            if itm and itm.ItemID == SPELLBOOK_ID:
                candidates.append(itm)
    except Exception:
        pass
    if not candidates:
        return None
    # Prefer blessed + named
    blessed_named = [it for it in candidates if is_blessed_spellbook(it)]
    if blessed_named:
        return blessed_named[0]
    # Else prefer any in hands
    for it in [left, right]:
        if it and it in candidates:
            return it
    # Else first found
    return candidates[0]


def get_backpack_scrolls():
    # Find all spell scrolls in backpack using authoritative list
    scrolls = []
    bp = Items.FindBySerial(Player.Backpack.Serial)
    items = bp.Contains if bp and bp.Contains else []
    for item in items:
        if item.ItemID in SCROLL_ITEM_IDS:
            scrolls.append(item)
    return scrolls

def prompt_for_container():
    """Prompt the user to target a container and return its serial or None."""
    Misc.SendMessage("Target the container with spell scrolls (or press ESC to use backpack)", 65)
    try:
        serial = Target.PromptTarget()
    except:
        return None
    if not serial:
        return None
    cont = Items.FindBySerial(serial)
    if not cont:
        Misc.SendMessage("Invalid target.", 33)
        return None
    # Open to ensure contents loaded
    Items.UseItem(cont.Serial)
    Misc.Pause(600)
    return cont.Serial

def get_container_scrolls(container_serial):
    """Return scroll list from targeted container."""
    scrolls = []
    cont = Items.FindBySerial(container_serial)
    if not cont:
        return scrolls
    # ensure fresh contents
    Items.UseItem(cont.Serial)
    Misc.Pause(300)
    items = cont.Contains if cont.Contains else []
    for item in items:
        if item.ItemID in SCROLL_ITEM_IDS:
            scrolls.append(item)
    return scrolls

def use_context_menu_add_to_book(scroll, spellbook):
    """Use context menu on a scroll to add it to the equipped spellbook.
    Returns True if the call was issued (not necessarily learned), False otherwise.
    """
    try:
        # Important: pass primitive int for serial to avoid type mismatch
        serial_int = int(scroll.Serial)
        options = [
            "Add To Spellbook",
            "Add to Spellbook",
            "Add to spellbook",
        ]
        # Start fresh journal window for reliable detection
        try:
            Journal.Clear()
        except Exception:
            pass

        for opt in options:
            debug_message(f"UseContextMenu on scroll 0x{scroll.ItemID:X} (serial {serial_int}) -> '{opt}'")
            try:
                Misc.UseContextMenu(serial_int, opt, 1500)
                # After choosing the context menu entry, a target cursor should appear
                if Target.WaitForTarget(2000, False):
                    try:
                        sb_serial = int(spellbook.Serial)
                        debug_message(f"Targeting equipped spellbook serial {sb_serial:X}")
                        Target.TargetExecute(sb_serial)
                        Misc.Pause(USE_DELAY_MS)
                        # Detect 'already present' and report accordingly
                        try:
                            if Journal.Search(JOURNAL_MSG_ALREADY):
                                debug_message("Journal: spell already in spellbook; moving to next.", 68)
                                return "already"
                        except Exception:
                            pass
                        return "added"
                    except Exception as e_t:
                        debug_message(f"TargetExecute failed: {e_t}", 33)
                        Misc.Pause(200)
                        # Try next variant if any
                else:
                    debug_message("No target cursor appeared after context menu selection.", 53)
                    Misc.Pause(200)
                    # Try next variant
            except Exception as e_inner:
                # Try next variant
                debug_message(f"Variant '{opt}' failed: {e_inner}", 53)
                Misc.Pause(150)
        return "failed"
    except Exception as e:
        debug_message(f"UseContextMenu failed: {e}", 33)
        return "failed"

def main():
    spellbook = find_best_spellbook()
    if not spellbook:
        Misc.SendMessage("No valid Spellbook found. Equip or place a Blessed 'Spellbook' in your backpack and try again.", 33)
        return

    target_container = prompt_for_container()
    from_container = False
    if target_container:
        scrolls = get_container_scrolls(target_container)
        from_container = True
    else:
        scrolls = get_backpack_scrolls()

    if not scrolls:
        where = "container" if from_container else "backpack"
        Misc.SendMessage(f"No spell scrolls found in {where}!", 33)
        return

    Misc.SendMessage(f"Found {len(scrolls)} spell scroll(s) to use.", 90)
    used = 0
    start_count = len(scrolls)
    index = 0
    while True:
        # Refetch current list to avoid stale handles after each action
        if from_container:
            current = get_container_scrolls(target_container)
        else:
            current = get_backpack_scrolls()

        if index >= len(current):
            break

        scroll = current[index]
        result = use_context_menu_add_to_book(scroll, spellbook)
        if result == "added":
            used += 1
            # Item likely consumed; re-fetch and keep same index to process next item at this position
            Misc.Pause(250)
        elif result == "already" or result == "failed":
            # Move to next scroll on already-present or failure to avoid looping
            index += 1
            Misc.Pause(150)

    Misc.SendMessage(f"Done using spell scrolls. {used} attempted from {start_count} found.", 90)

if __name__ == "__main__":
    main()
