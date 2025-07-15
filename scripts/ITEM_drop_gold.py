"""
Drop All Gold Script - a Razor Enhanced Python Script for Ultima Online

Drops all gold (item ID 0x0EED) in the player's backpack to the ground using safe, walkable tiles.
this is useful to instantly reduce weight in critical situations

HOTKEY:: V
VERSION::20250714
"""

GOLD_ID = 0x0EED

# Options: 'move_on_ground', 'nearby_tiles'
DROP_METHOD = 'move_on_ground'

DEBUG_MODE = False

def debug_message(msg):
    if DEBUG_MODE:
        Misc.SendMessage(f"[DropGold] {msg}", 67)

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

def drop_gold_stack_nearby_tiles(gold_item, amount, player_pos):
    debug_message(f"Trying to drop gold on nearby tiles (MoveOnGround)...")
    for x_offset, y_offset in get_nearby_tiles():
        x, y, z = find_ground_tile(x_offset, y_offset, player_pos)
        debug_message(f"Attempting drop: {amount} gold to ({x}, {y}, {z}) using MoveOnGround")
        Items.MoveOnGround(gold_item.Serial, amount, x, y, z)
        Misc.Pause(300)
        # Check if any gold remains
        gold_left = Items.FindBySerial(gold_item.Serial)
        if not gold_left or gold_left.Amount < amount:
            debug_message("Drop successful on nearby tile.")
            break

def drop_gold_stack_on_ground(gold_item, amount, player_pos):
    x, y, z = player_pos['x'], player_pos['y'], player_pos['z']
    debug_message(f"Trying to drop gold at player position: ({x}, {y}, {z}) using MoveOnGround")
    Items.MoveOnGround(gold_item.Serial, amount, x, y, z)
    Misc.Pause(300)


def drop_all_gold():
    player_pos = get_player_position()
    gold_items = Items.FindByID(GOLD_ID, -1, Player.Backpack.Serial)
    if not gold_items:
        debug_message("No gold found in backpack.")
        return
    if not isinstance(gold_items, list):
        gold_items = [gold_items]
    for gold_item in gold_items:
        amount = gold_item.Amount
        debug_message(f"Found gold stack: {amount} at serial {hex(gold_item.Serial)}")
        if DROP_METHOD == 'move_on_ground':
            drop_gold_stack_on_ground(gold_item, amount, player_pos)
        elif DROP_METHOD == 'nearby_tiles':
            drop_gold_stack_nearby_tiles(gold_item, amount, player_pos)
        else:
            debug_message(f"Unknown DROP_METHOD: {DROP_METHOD}")

if __name__ == "__main__":
    drop_all_gold()