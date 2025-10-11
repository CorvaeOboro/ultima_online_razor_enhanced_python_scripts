"""
ITEM Withdraw Hay From Pack Horse - a Razor Enhanced Python Script for Ultima Online

- Target a pack animal (horse/llama), then withdraw a specific number of hay items to your backpack
- Auto-detects the animal's pack container when possible; falls back to manual container target
- Robust retries, pacing, and progress reporting


Mobiles.UseMobile(0x0003931A)
Items.Move(0x416DE207, 0x40412C63, 1)

HOTKEY:: CTRL + SHIFT + H
VERSION::20250924
"""

# Configuration
HAY_ITEM_IDS = [
    0x0F36,  # Hay / sheaf of hay (adjust for your shard if different)
]
WITHDRAW_COUNT = 20          # Number of hay items to withdraw
MOVE_DELAY_MS = 400          # Delay between moves
VERIFY_RETRY_MS = 300        # Delay between verification retries
MAX_MOVE_RETRIES = 3         # Retries per item
MAX_VERIFY_RETRIES = 3       # Post-move verification retries
DEBUG_MODE = True            # Toggle debug messages


def debug_message(msg, color=68):
    if DEBUG_MODE:
        try:
            Misc.SendMessage(f"[HayWithdraw] {msg}", color)
        except Exception:
            print(f"[HayWithdraw] {msg}")


def prompt_pack_animal():
    debug_message("Target your pack animal (horse/llama)...", 66)
    target_serial = Target.PromptTarget()
    if target_serial == -1:
        debug_message("Invalid mobile target.", 33)
        return None
    mob = Mobiles.FindBySerial(target_serial)
    if not mob:
        debug_message("Could not find that mobile.", 33)
        return None
    # Debug: show basic mobile info
    try:
        debug_message(f"Mob selected: serial={hex(mob.Serial)} name='{mob.Name}' body={getattr(mob,'Body',None)} hue={getattr(mob,'Hue',None)}", 67)
    except Exception:
        pass
    return mob


def get_pack_container_from_mobile(mob):
    """Attempt to resolve the pack container serial from a pack animal mobile.
    Returns a container Item or None.
    """
    # 1) Try direct property
    try:
        pack_container = mob.Backpack if hasattr(mob, 'Backpack') else None
        if pack_container:
            # Debug: log what we think the backpack serial is
            try:
                pack_serial_dbg = pack_container.Serial if hasattr(pack_container, 'Serial') else pack_container
                debug_message(f"Direct Backpack ref present: serial={hex(int(pack_serial_dbg))}", 67)
            except Exception:
                pass
            pack_item = Items.FindBySerial(pack_container.Serial) if hasattr(pack_container, 'Serial') else Items.FindBySerial(pack_container)
            if pack_item:
                debug_message(f"Resolved pack container by direct property: serial={hex(pack_item.Serial)} contains={len(getattr(pack_item,'Contains',[]) or [])}", 67)
                return pack_item
    except Exception as e:
        debug_message(f"Direct pack resolve failed: {e}", 33)

    # 2) Actively open the pack's backpack (UseMobile), then re-check
    try:
        # Prefer Mobiles.UseMobile if available; otherwise fall back to Misc.UseObject
        try:
            Mobiles.UseMobile(mob.Serial)
        except Exception:
            try:
                Misc.UseObject(mob.Serial)
            except Exception:
                pass
        Misc.Pause(600)
        # Re-fetch mob and try Backpack again
        mob2 = Mobiles.FindBySerial(mob.Serial)
        if mob2 and hasattr(mob2, 'Backpack') and mob2.Backpack:
            try:
                debug_message(f"After UseMobile: mob2.Backpack serial={hex(mob2.Backpack.Serial) if hasattr(mob2.Backpack,'Serial') else mob2.Backpack}", 67)
            except Exception:
                pass
            pack_item2 = Items.FindBySerial(mob2.Backpack.Serial) if hasattr(mob2.Backpack, 'Serial') else Items.FindBySerial(mob2.Backpack)
            if pack_item2:
                debug_message(f"Resolved pack container after UseMobile: serial={hex(pack_item2.Serial)} contains={len(getattr(pack_item2,'Contains',[]) or [])}", 67)
                return pack_item2
    except Exception as e:
        debug_message(f"UseMobile open failed: {e}", 33)

    debug_message("Could not auto-detect pack container. Target the pack's backpack...", 66)
    cont_serial = Target.PromptTarget()
    if cont_serial == -1:
        debug_message("Invalid container target.", 33)
        return None
    cont_item = Items.FindBySerial(cont_serial)
    if not cont_item:
        debug_message("Container not found.", 33)
        return None
    debug_message(f"Using manually targeted pack container: serial={hex(cont_item.Serial)} contains={len(getattr(cont_item,'Contains',[]) or [])}", 67)
    return cont_item


def ensure_player_backpack():
    if not Player.Backpack:
        debug_message("No player backpack found.", 33)
        return False
    return True


def _open_pack_and_poll_contents(mob, container_serial, timeout_ms=2000):
    """Open the pack via UseMobile and poll for the container contents to populate."""
    try:
        try:
            Mobiles.UseMobile(mob.Serial)
        except Exception:
            try:
                Misc.UseObject(mob.Serial)
            except Exception:
                pass
    except Exception as e:
        debug_message(f"UseMobile during poll failed: {e}", 33)
    elapsed = 0
    step = 200
    while elapsed <= timeout_ms:
        Misc.Pause(step)
        elapsed += step
        try:
            cont = Items.FindBySerial(container_serial)
            if cont and getattr(cont, 'Contains', None):
                return cont.Contains
        except Exception:
            pass
    return []


def find_hay_items_in_container(container, mob=None):
    """Return a list of hay item objects located in the given container (non-recursive).
    If contents are empty and a mob is supplied, attempt to open the pack and poll until contents are available.
    """
    items = []
    try:
        contains = Items.FindBySerial(container.Serial).Contains
    except Exception:
        contains = None
    if not contains:
        debug_message(f"Container {hex(container.Serial)} has no enumerated contents.", 33)
        if mob is not None:
            debug_message("Attempting to open pack and refresh contents...", 66)
            contains = _open_pack_and_poll_contents(mob, container.Serial, timeout_ms=2500)
        if not contains:
            return items
    # Debug: preview first few contents
    try:
        dbg_preview = []
        for it in (contains or [])[:10]:
            dbg_preview.append(f"{hex(it.Serial)} id=0x{int(it.ItemID):04X} hue={getattr(it,'Hue',None)}")
        debug_message(f"Container {hex(container.Serial)} contents[{len(contains)}]: " + ", ".join(dbg_preview), 67)
    except Exception:
        pass
    for it in contains:
        try:
            if int(it.ItemID) in HAY_ITEM_IDS:
                items.append(it)
        except Exception:
            continue
    debug_message(f"Hay matches in {hex(container.Serial)}: {len(items)} (IDs={','.join([f'0x{hid:04X}' for hid in HAY_ITEM_IDS])})", 67)
    return items


def move_item_to_container(it, dest_container):
    """Move a single item to the destination container with retries and verification."""
    for attempt in range(1, MAX_MOVE_RETRIES + 1):
        try:
            Items.Move(it, dest_container, 0)
            Misc.Pause(MOVE_DELAY_MS)
        except Exception as e:
            debug_message(f"Move error (attempt {attempt}) for {it.Serial}: {e}", 33)
            Misc.Pause(VERIFY_RETRY_MS)
            continue
        # Verify
        for vtry in range(1, MAX_VERIFY_RETRIES + 1):
            try:
                moved_ref = Items.FindBySerial(it.Serial)
                if moved_ref and moved_ref.Container == dest_container.Serial:
                    return True
            except Exception:
                pass
            Misc.Pause(VERIFY_RETRY_MS)
    return False


def withdraw_hay_from_pack():
    if not ensure_player_backpack():
        return

    mob = prompt_pack_animal()
    if not mob:
        return

    pack_container = get_pack_container_from_mobile(mob)
    if not pack_container:
        return

    to_withdraw = int(WITHDRAW_COUNT)
    if to_withdraw <= 0:
        debug_message("WITHDRAW_COUNT must be > 0.", 33)
        return

    debug_message(f"Scanning pack container serial={hex(pack_container.Serial)} for hay...", 67)
    hay_items = find_hay_items_in_container(pack_container, mob)
    total_available = len(hay_items)
    if total_available <= 0:
        debug_message("No hay found in pack. See debug above for container contents and IDs.", 33)
        return

    debug_message(f"Requesting {to_withdraw} hay items from {mob.Name or 'pack animal'} (available {total_available})...", 66)
    moved = 0

    for it in list(hay_items):
        if moved >= to_withdraw:
            break
        ok = move_item_to_container(it, Player.Backpack)
        if ok:
            moved += 1
            if moved % 5 == 0 or moved == to_withdraw:
                debug_message(f"Withdrawn {moved}/{to_withdraw} hay items...", 67)
        else:
            debug_message(f"Failed to withdraw hay {it.Serial} after {MAX_MOVE_RETRIES} retries.", 33)

    debug_message(f"Done. Withdrawn {moved}/{to_withdraw} hay items.", 68 if moved == to_withdraw else 33)


def main():
    withdraw_hay_from_pack()


if __name__ == '__main__':
    main()
