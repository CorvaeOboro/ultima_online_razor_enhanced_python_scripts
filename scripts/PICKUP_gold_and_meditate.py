"""
Pickup Gold and Meditate - Razor Enhanced Python Script for Ultima Online

- Uses Meditate skill if not already meditating
- Picks up all gold (0x0EED) on the ground within 1 tile of the player
- we drop all our gold often to free up weight to loot , once the loot is processed this quickly picks up those stacks

HOTKEY::Spacebar
VERSION::20250722
"""

import time
from System.Collections.Generic import List
from System import Int32

GOLD_ID = 0x0EED
PICKUP_RANGE = 2

DEBUG_MODE = False

def debug_print(msg):
    if DEBUG_MODE:
        print(msg)

def is_meditating():
    # Meditate status is shown in Journal
    for i in range(20):
        if Journal.Search("You enter a meditative trance."):
            return True
        if Journal.Search("You are already concentrating on your spiritual self."):
            return True
        time.sleep(0.05)
    return False

def pickup_gold_nearby():
    player_x = Player.Position.X
    player_y = Player.Position.Y
    player_z = Player.Position.Z

    # Diagnostic: Print ALL items in range
    debug_filter = Items.Filter()
    debug_filter.RangeMin = 0
    debug_filter.RangeMax = PICKUP_RANGE
    debug_items = Items.ApplyFilter(debug_filter)
    debug_print(f"[DEBUG] Found {len(debug_items) if debug_items else 0} items in range {PICKUP_RANGE}.")
    found_gold = False
    if debug_items:
        for item in debug_items:
            debug_print(f"[DEBUG] serial={item.Serial:X} name={item.Name} graphic={hex(item.ItemID)} cont={item.Container} pos=({item.Position.X},{item.Position.Y},{item.Position.Z})")
            if item.ItemID == GOLD_ID:
                debug_print(f"[DEBUG] GOLD DETECTED: serial={item.Serial:X} container={item.Container}")
                found_gold = True
    if not found_gold:
        debug_print("[DEBUG] No gold detected at all in item scan!")

    debug_print(f"[DEBUG] Player position: ({player_x},{player_y},{player_z})")
    # Now do actual gold pickup as before
    gold_filter = Items.Filter()
    gold_filter.Enabled = True
    gold_filter.OnGround = True
    gold_filter.RangeMin = 0
    gold_filter.RangeMax = PICKUP_RANGE
    gold_filter.Graphics = List[Int32]([Int32(GOLD_ID)])
    gold_items = Items.ApplyFilter(gold_filter)

    if not gold_items:
        debug_print("No gold found nearby (filter).")
        found_gold = False
        return
    count = 0
    count_failed = 0
    for gold in gold_items:
        # Pick up gold if it's on the ground (Container 0 or 0xFFFFFFFF)
        if gold.Container == 0 or gold.Container == 0xFFFFFFFF:
            debug_print(f"[DEBUG] Attempting to pick up gold: serial={gold.Serial:X} from pos=({gold.Position.X},{gold.Position.Y},{gold.Position.Z}) to backpack at ({player_x},{player_y},{player_z})")
            try:
                Items.Move(gold, Player.Backpack, 0)
                debug_print(f"[DEBUG] Called Items.Move({gold.Serial:X}, Player.Backpack, 0)")
                Misc.Pause(400)
                count += 1
            except Exception as e:
                debug_print(f"Failed to pick up gold {gold.Serial:X}: {e}")
                count_failed += 1
    debug_print(f"Picked up {count} gold stacks. Failed to pick up {count_failed} gold stacks.")

def log_player_buffs_and_status():
    debug_print("[DEBUG] Player Status:")
    try:
        debug_print(f"  Status: {Player.Status}")
    except Exception as e:
        debug_print(f"  Could not read Player.Status: {e}")
    debug_print("[DEBUG] Player Buffs:")
    try:
        buffs = Player.Buffs
        if buffs:
            for buff in buffs:
                debug_print(f"  Buff: {buff.Name if hasattr(buff, 'Name') else buff}")
        else:
            debug_print("  No buffs found.")
    except Exception as e:
        debug_print(f"  Could not read Player.Buffs: {e}")

def main():
    log_player_buffs_and_status()
    pickup_gold_nearby()
    if not is_meditating():
        Player.UseSkill("Meditation")
    # spam meditation regardless
    Player.UseSkill("Meditation")

if __name__ == '__main__':
    main()
