"""
ITEM Transfer Hay to Pack Horse - a Razor Enhanced Python Script for Ultima Online

- Targets a pack animal (pack horse/llama) and transfers all hay from your backpack to its pack
- Supports auto-detecting the animal's pack container; falls back to manual container target if needed
- Robust retries, pacing, and progress reporting

HOTKEY:: CTRL + H
VERSION::20250924
"""

# Configuration
HAY_ITEM_IDS = [
    0x0F36,  # Hay / sheaf of hay (adjust for your shard if different)
]
MOVE_DELAY_MS = 400           # Delay between moves
VERIFY_RETRY_MS = 300         # Delay between verification retries
MAX_MOVE_RETRIES = 3          # Retries per item
MAX_VERIFY_RETRIES = 3        # Post-move verification retries
DEBUG_MODE = True             # Toggle debug messages


def debug_message(msg, color=68):
    if DEBUG_MODE:
        try:
            Misc.SendMessage(f"[HayXfer] {msg}", color)
        except Exception:
            print(f"[HayXfer] {msg}")


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
    return mob


def get_pack_container_from_mobile(mob):
    """Attempt to resolve the pack container serial from a pack animal mobile.
    Returns a container Item or None.
    """
    try:
        # Some shards expose an accessible backpack container on the mobile
        pack_container = mob.Backpack if hasattr(mob, 'Backpack') else None
        if pack_container:
            # Ensure it resolves to an Item
            pack_item = Items.FindBySerial(pack_container.Serial) if hasattr(pack_container, 'Serial') else Items.FindBySerial(pack_container)
            if pack_item:
                return pack_item
    except Exception as e:
        debug_message(f"Auto-detect pack container failed: {e}", 33)

    # Fallback: prompt user to target the pack container directly
    debug_message("Could not auto-detect pack container. Target the pack's backpack...", 66)
    cont_serial = Target.PromptTarget()
    if cont_serial == -1:
        debug_message("Invalid container target.", 33)
        return None
    cont_item = Items.FindBySerial(cont_serial)
    if not cont_item:
        debug_message("Container not found.", 33)
        return None
    return cont_item


def ensure_player_backpack():
    if not Player.Backpack:
        debug_message("No player backpack found.", 33)
        return False
    return True


def find_hay_items_in_backpack():
    """Return a list of hay item objects located in player's backpack (non-recursive)."""
    items = []
    try:
        contains = Items.FindBySerial(Player.Backpack.Serial).Contains
    except Exception:
        contains = None
    if not contains:
        return items
    for it in contains:
        try:
            if int(it.ItemID) in HAY_ITEM_IDS:
                items.append(it)
        except Exception:
            continue
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
        # if verification failed, retry move
    return False


def transfer_all_hay_to_pack():
    if not ensure_player_backpack():
        return

    mob = prompt_pack_animal()
    if not mob:
        return

    pack_container = get_pack_container_from_mobile(mob)
    if not pack_container:
        return

    hay_items = find_hay_items_in_backpack()
    total = len(hay_items)
    if total == 0:
        debug_message("No hay found in your backpack.", 33)
        return

    debug_message(f"Transferring {total} hay items to {mob.Name or 'pack animal'}...", 66)
    moved = 0

    for it in list(hay_items):
        ok = move_item_to_container(it, pack_container)
        if ok:
            moved += 1
            if moved % 5 == 0 or moved == total:
                debug_message(f"Moved {moved}/{total} hay items...", 67)
        else:
            debug_message(f"Failed to move hay {it.Serial} after {MAX_MOVE_RETRIES} retries.", 33)

    debug_message(f"Done. Moved {moved}/{total} hay items.", 68 if moved == total else 33)


def main():
    transfer_all_hay_to_pack()


if __name__ == '__main__':
    main()
