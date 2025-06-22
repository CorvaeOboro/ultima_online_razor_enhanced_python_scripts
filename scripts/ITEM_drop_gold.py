"""
Drop All Gold Script - a Razor Enhanced Python Script for Ultima Online

Drops all gold (item ID 0x0EED) in the player's backpack to the ground using safe, walkable tiles.
this is useful to instantly reduce weight in critical situations

VERSION::20250621
"""

import sys
import time

GOLD_ID = 0x0EED

def get_nearby_tiles():
    offsets = [
        (0, 0), (0, 1), (1, 0), (0, -1), (-1, 0),
        (1, 1), (1, -1), (-1, -1), (-1, 1),
        (0, 2), (2, 0), (0, -2), (-2, 0),
    ]
    return offsets

def get_player_position():
    return {
        'x': Player.Position.X,
        'y': Player.Position.Y,
        'z': Player.Position.Z,
        'map': Player.Map
    }

def find_ground_tile(x_offset, y_offset, player_pos):
    x = player_pos['x'] + x_offset
    y = player_pos['y'] + y_offset
    z = player_pos['z']
    map_id = player_pos['map']
    statics = Statics.GetStaticsTileInfo(x, y, map_id)
    for tile in statics:
        # Some shards or Razor Enhanced versions may not have Flags attribute
        # Use hasattr to check safely
        if tile.StaticID < 0x4000:
            if hasattr(tile, 'Flags'):
                # 0x200 is walkable
                if tile.Flags & 0x200:
                    return (x, y, tile.Z)
            else:
                # No Flags attribute, just use StaticID and return first found
                return (x, y, tile.Z)
    return (x, y, z)

def drop_gold_stack(gold_item, amount, player_pos):
    for x_offset, y_offset in get_nearby_tiles():
        x, y, z = find_ground_tile(x_offset, y_offset, player_pos)
        Misc.MoveAmount = amount
        Items.Move(gold_item, 0, x, y, z)
        Misc.Pause(300)
        # Check if any gold remains
        gold_left = Items.FindBySerial(gold_item.Serial)
        if not gold_left or gold_left.Amount == 0:
            return
        # Try next tile if drop failed

def drop_all_gold():
    player_pos = get_player_position()
    gold_items = Items.FindByID(GOLD_ID, -1, Player.Backpack.Serial, -1)
    if not gold_items:
        Misc.SendMessage("No gold found in backpack.", 68)
        return
    if not isinstance(gold_items, list):
        gold_items = [gold_items]
    total = 0
    for gold in gold_items:
        total += gold.Amount
        drop_gold_stack(gold, gold.Amount, player_pos)
    Misc.SendMessage(f"Dropped {total} gold to the ground.", 68)

if __name__ == "__main__":
    drop_all_gold()