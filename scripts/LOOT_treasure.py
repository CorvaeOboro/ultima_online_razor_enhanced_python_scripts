"""
LOOT Treasure Chest Lockpick - a Razor Enhanced Python script for Ultima Online

- Uses lockpicks to unlock nearby chests
- Opens chests (no disarm) and extracts items
- moving them from container to player backpack

TODO: 
- add navigation attempts when cant see target ( on a hill ) just randomly move around the chest until message gone

HOTKEY:: K
VERSION::20250802
"""

from System.Collections.Generic import List
from System import Int32

# If True, drop resource items on ground. If False, move to backpack. drop ground logic issues
DROP_RESOURCES_GROUND = False
# If False, suppress all Misc.SendMessage output
DEBUG_MODE = False
# Global move delay between item moves (in ms)
MOVE_DELAY = 600
# IDs for different treasure chest types 
CHEST_TYPES = [0x0E40, 0x0E41, 0x0E42, 0x0E43, 0xB061, 0xB05D, 0xB060, 0xB051, 0xC056, 0xC057, 0xB05C]  
# Lockpick item type 
LOCKPICK_TYPE = 0x14FC

# Item IDs for resources (leather, ingots, boards, cut cloth leather, etc.) we throw these on the ground if overweight
RESOURCE_IDS = [
    # Leather & hides
    0x1078,  # Leather
    0x1079,  # Spined Leather
    0x107A,  # Horned Leather
    0x107B,  # Barbed Leather
    0x107C,  # Regular Hide
    0x107D,  # Spined Hide
    0x107E,  # Horned Hide
    0x107F,  # Barbed Hide
    # Ingots
    0x1BF2,  # Iron Ingot
    0x1BEF,  # Dull Copper Ingot
    0x1BEF,  # Shadow Iron Ingot (same as dull copper in some shards)
    0x1BEF,  # Copper Ingot
    0x1BEF,  # Bronze Ingot
    0x1BEF,  # Gold Ingot
    0x1BEF,  # Agapite Ingot
    0x1BEF,  # Verite Ingot
    0x1BEF,  # Valorite Ingot
    # Boards
    0x1BD7,  # Boards
    0x1BDD,  # Oak Board
    0x1BDE,  # Ash Board
    0x1BDF,  # Yew Board
    0x1BE0,  # Heartwood Board
    0x1BE1,  # Bloodwood Board
    0x1BE2,  # Frostwood Board
    # Cut resources (new)
    0x1766,  # Cut Cloth
    0x1081,  # Cut Leather
]

class TreasureManager:
    def __init__(self):
        # Colors for debug messages
        self.debug_color = 67  # Light blue for messages
        self.error_color = 33  # Red for errors
        self.success_color = 68  # Green for success
        
        # List of item IDs for different treasure chest types
        self.chest_types = CHEST_TYPES
        self.lockpick_type = LOCKPICK_TYPE  # Lockpick item type
        
        # Timing configuration (in ms)
        self.lockpick_delay = 1000    # 1 second between lockpick attempts
        self.open_delay = 1500        # 1.5 seconds after opening
        self.move_delay = MOVE_DELAY  # Use global move delay
        self.retry_delay = 500        # 0.5 seconds before retrying
        
        # Search configuration
        self.search_range = 3         # Tiles to search for chests
        self.max_retry_count = 3      # Number of times to retry moving an item
        
    def is_overweight(self):
        """
        Returns True if player is overweight (checks both weight stat and Journal message).
        """
        return self.journal_overweight() or self.weight_overweight()

    def journal_overweight(self):
        """
        Check the Journal for the overweight message.
        """
        return Journal.Search("That container cannot hold more weight.")

    def weight_overweight(self):
        """
        Returns True if the player's weight stat exceeds the maximum allowed.
        """
        try:
            return Player.Weight > Player.MaxWeight
        except:
            self.debug_message("Could not determine player weight.", self.error_color)
            return False

    def get_player_position(self):
        """
        Returns the player's current position as (x, y, z, map).
        """
        return Player.Position.X, Player.Position.Y, Player.Position.Z, Player.Map

    def drop_all_gold_at_feet(self):
        """
        Drops all gold from backpack at (or near) player's feet using Items.MoveOnGround for reliability.
        """
        GOLD_ID = 0x0EED
        max_stack = 60000
        dropped = 0
        gold_items = Items.FindByID(GOLD_ID, -1, Player.Backpack.Serial, -1)
        if not gold_items:
            self.debug_message("No gold found in backpack.", self.error_color)
            return
        if not isinstance(gold_items, list):
            gold_items = [gold_items]
        x, y, z, _ = self.get_player_position()
        for gold in gold_items:
            amount = gold.Amount
            while amount > 0:
                drop_amount = min(amount, max_stack)
                try:
                    Items.MoveOnGround(gold.Serial, drop_amount, x, y, z)
                    Misc.Pause(self.move_delay)
                    dropped += drop_amount
                    self.debug_message(f"Dropped {drop_amount} gold at ({x},{y},{z}) from stack {gold.Serial:X}", self.success_color)
                except Exception as e:
                    self.debug_message(f"Exception dropping gold: {e}", self.error_color)
                    break
                # Refresh gold reference and amount
                gold = Items.FindBySerial(gold.Serial)
                if not gold:
                    break
                amount = gold.Amount
        self.debug_message(f"Dropped total of {dropped} gold at near your feet.", self.success_color)

    def debug_message(self, message, color=None):
        """
        Send a debug message to the game client (respects DEBUG_MODE global).
        """
        if color is None:
            color = self.debug_color
        if DEBUG_MODE:
            Misc.SendMessage(f"[Treasure] {message}", color)

    def find_nearby_chest(self):
        """
        Find the nearest unopened treasure chest within search_range tiles.
        Returns the chest item object or None if not found.
        """
        self.debug_message("Searching for treasure chests...")
        for chest_id in self.chest_types:
            chests = Items.Filter()
            chests.Enabled = True
            chests.OnGround = True
            chests.RangeMin = 0
            chests.RangeMax = self.search_range
            chests.Graphics = List[Int32]([Int32(chest_id)])
            chests.Movable = False
            found_chests = Items.ApplyFilter(chests)
            if found_chests:
                chest = Items.Select(found_chests, 'Nearest')
                self.debug_message(f"Found chest at {chest.Position}", self.success_color)
                return chest
        self.debug_message("No chests found nearby", self.error_color)
        return None

    def find_lockpicks(self):
        """
        Find lockpicks in the player's backpack.
        Returns the lockpick item object or None if not found.
        """
        lockpicks = Items.FindByID(self.lockpick_type, -1, Player.Backpack.Serial, -1)
        if not lockpicks:
            self.debug_message("No lockpicks found!", self.error_color)
            return None
        return lockpicks

    def unlock_chest(self, chest):
        """
        Attempt to unlock the given chest using lockpicks.
        Returns True if the attempt was made (does not guarantee success).
        """
        self.debug_message("Attempting to unlock chest...")
        lockpicks = self.find_lockpicks()
        if not lockpicks:
            return False
        # Use lockpick on chest
        Items.UseItem(lockpicks)
        Target.WaitForTarget(10000, False)
        Target.TargetExecute(chest)
        # Wait for unlock attempt
        Misc.Pause(self.lockpick_delay)
        return True

    def open_chest(self, chest):
        """
        Open the chest and wait for its contents to load.
        Returns True after opening.
        """
        self.debug_message("Opening chest...")
        Items.UseItem(chest)
        Misc.Pause(self.open_delay)
        return True

    def is_resource_item(self, item):
        """
        Returns True if the item is a resource (leather, ingot, board, etc.).
        """
        return item.ItemID in RESOURCE_IDS

    def get_nearby_drop_positions(self, center_x, center_y, center_z):
        """
        Returns a list of (x, y, z) positions near the given coordinates for item dropping.
        Spiral adjacent pattern (center, N, E, S, W, diagonals, extended).
        """
        offsets = [
            (0, 0), (0, 1), (1, 0), (0, -1), (-1, 0),
            (1, 1), (1, -1), (-1, -1), (-1, 1),
            (0, 2), (2, 0), (0, -2), (-2, 0)
        ]
        return [(center_x + dx, center_y + dy, center_z) for dx, dy in offsets]

    def try_drop_item_on_ground(self, item):
        """
        Attempt to drop the item directly at player's feet (current position).
        Returns True if successful, False otherwise.
        """
        x, y, z = Player.Position.X, Player.Position.Y, Player.Position.Z
        try:
            # Drop item on ground
            Items.Move(item, 0xFFFFFFFF, 0, x, y, z)  # 0xFFFFFFFF = ground
            Misc.Pause(self.move_delay)
            # Check if item is no longer in chest (moved)
            if Items.FindBySerial(item.Serial).Container != item.Container:
                self.debug_message(f"Dropped resource item {item.Serial:X} at ({x},{y})", self.success_color)
                return True
        except:
            pass
        self.debug_message(f"Failed to drop resource item {item.Serial:X} at player's feet!", self.error_color)
        return False

    def move_items(self, container):
        """
        Move all items from the given container (chest) to the backpack, or drop resources on the ground if configured.
        Implements round robin retry logic: each item is attempted once per round, skipping failed items until all are tried, then retries up to max_retry_count.
        If overweight at any point, drops resources at player's feet using spiral world coordinates.
        """
        # Always re-fetch the current item list from the container at the start of each round
        attempt = 0
        moved_items = 0
        total_items = 0
        failed_serials = set()
        while attempt < self.max_retry_count:
            container_obj = Items.FindBySerial(container.Serial)
            if not container_obj or not hasattr(container_obj, 'Contains') or not container_obj.Contains:
                if attempt == 0:
                    self.debug_message("Chest is empty!", self.error_color)
                break
            items = list(container_obj.Contains)
            if attempt == 0:
                total_items = len(items)
                failed_serials = set([item.Serial for item in items])
            else:
                # Only try to move items that failed in previous rounds
                items = [item for item in items if item.Serial in failed_serials]
            if not items:
                break
            self.debug_message(f"Round {attempt+1}: Attempting to move {len(items)} items...")
            next_failed_serials = set()
            for item in items:
                # If overweight, drop resources at feet
                if self.is_overweight():
                    self.debug_message("Overweight detected! Dropping resources at feet...", self.error_color)
                    self.drop_all_resources_at_feet()
                    Misc.Pause(500)
                # Re-fetch item object in case container changed or item was moved externally
                item_obj = Items.FindBySerial(item.Serial)
                if not item_obj or not hasattr(item_obj, 'Container') or item_obj.Container != container.Serial:
                    self.debug_message(f"Item {item.Serial:X} not found in chest, skipping.", self.debug_color)
                    continue  # Already moved or gone
                # Resource logic
                if self.is_resource_item(item_obj):
                    if DROP_RESOURCES_GROUND:
                        if self.attempt_drop_resource_on_ground(item_obj):
                            moved_items += 1
                        else:
                            next_failed_serials.add(item_obj.Serial)
                    else:
                        if self.attempt_move_item_to_backpack(item_obj):
                            moved_items += 1
                        else:
                            next_failed_serials.add(item_obj.Serial)
                else:
                    if self.attempt_move_item_to_backpack(item_obj):
                        moved_items += 1
                    else:
                        next_failed_serials.add(item_obj.Serial)
                Misc.Pause(self.move_delay)  # Always pause after move attempt for server sync
            failed_serials = next_failed_serials
            attempt += 1
            # Extra pause between rounds to avoid flooding
            Misc.Pause(300)
        if failed_serials:
            self.debug_message(f"Failed to move {len(failed_serials)} items after {self.max_retry_count} rounds!", self.error_color)
        self.debug_message(f"Finished moving items! Successfully moved {moved_items} out of {total_items} items.", self.success_color)

    def drop_all_resources_at_feet(self):
        """
        Drops all resource items in backpack at player's feet using world-space logic from ITEM_drop_gold.py.
        Tries spiral adjacent tiles using Statics.GetStaticsTileInfo for walkable ground, then falls back to player position.
        """
        resource_serials = [item.Serial for item in Player.Backpack.Contains if self.is_resource_item(item)]
        if not resource_serials:
            self.debug_message("No resources to drop!", self.error_color)
            return
        # Get player position
        x, y, z, map_id = self.get_player_position()
        player_pos = {'x': x, 'y': y, 'z': z, 'map': map_id}
        offsets = [  # Spiral adjacent pattern
            (0, 0), (0, 1), (1, 0), (0, -1), (-1, 0),
            (1, 1), (1, -1), (-1, -1), (-1, 1),
            (0, 2), (2, 0), (0, -2), (-2, 0),
        ]
        for serial in resource_serials:
            item = Items.FindBySerial(serial)
            if not item or item.Container != Player.Backpack.Serial:
                continue
            dropped = False
            for x_off, y_off in offsets:
                # Use gold drop logic: find walkable tile
                drop_x = player_pos['x'] + x_off
                drop_y = player_pos['y'] + y_off
                drop_z = player_pos['z']
                statics = Statics.GetStaticsTileInfo(drop_x, drop_y, player_pos['map'])
                found_tile = False
                if statics:
                    for tile in statics:
                        if hasattr(tile, 'Flags') and tile.Flags & 0x200:
                            drop_z = tile.Z
                            found_tile = True
                            break
                        elif not hasattr(tile, 'Flags'):
                            drop_z = tile.Z
                            found_tile = True
                            break
                # If found walkable, use that z, else fallback to player's z
                self.debug_message(f"Trying to drop resource {item.Serial:X} at ({drop_x},{drop_y},{drop_z})", self.debug_color)
                try:
                    Items.MoveOnGround(item.Serial, item.Amount if hasattr(item, 'Amount') else 1, drop_x, drop_y, drop_z)
                    Misc.Pause(self.move_delay)
                    # Confirm item is no longer in backpack
                    if not Items.FindBySerial(item.Serial) or Items.FindBySerial(item.Serial).Container != Player.Backpack.Serial:
                        self.debug_message(f"Dropped resource {item.Serial:X} at ({drop_x},{drop_y},{drop_z})", self.success_color)
                        dropped = True
                        break
                except Exception as e:
                    self.debug_message(f"Error dropping {item.Serial:X} at ({drop_x},{drop_y},{drop_z}): {e}", self.error_color)
            if not dropped:
                # Fallback: try player's current position
                try:
                    self.debug_message(f"Fallback: dropping {item.Serial:X} at player pos ({player_pos['x']},{player_pos['y']},{player_pos['z']})", self.debug_color)
                    Items.MoveOnGround(item.Serial, item.Amount if hasattr(item, 'Amount') else 1, player_pos['x'], player_pos['y'], player_pos['z'])
                    Misc.Pause(self.move_delay)
                    if not Items.FindBySerial(item.Serial) or Items.FindBySerial(item.Serial).Container != Player.Backpack.Serial:
                        self.debug_message(f"Dropped resource {item.Serial:X} at player position ({player_pos['x']},{player_pos['y']},{player_pos['z']})", self.success_color)
                        continue
                except Exception as e:
                    self.debug_message(f"Final drop failed for {item.Serial:X} at player pos: {e}", self.error_color)
                self.debug_message(f"Failed to drop resource {item.Serial:X} at any nearby location!", self.error_color)

    def attempt_move_item_to_backpack(self, item):
        """
        Attempt to move the given item to the player's backpack, with retry logic.
        Returns True on success, False otherwise.
        """
        retry_count = 0
        while retry_count < self.max_retry_count:
            try:
                Items.Move(item, Player.Backpack, 0)
                Misc.Pause(self.move_delay)
                # Check if item is now in backpack
                if Items.FindBySerial(item.Serial).Container == Player.Backpack.Serial:
                    if retry_count % 5 == 0 and retry_count > 0:
                        self.debug_message(f"Moved item {item.Serial:X} after {retry_count+1} attempts.")
                    return True
            except:
                pass
            retry_count += 1
            Misc.Pause(self.retry_delay)
        return False

    def attempt_drop_resource_on_ground(self, item):
        """
        Attempt to drop a resource item on the ground at player's feet, retrying if necessary.
        Returns True on success, False otherwise.
        """
        retry_count = 0
        while retry_count < self.max_retry_count:
            if self.try_drop_item_on_ground(item):
                return True
            retry_count += 1
            Misc.Pause(self.retry_delay)
        return False
    
    def loot_chest(self):
        """Main chest looting process"""
        # Find a chest
        chest = self.find_nearby_chest()
        if not chest:
            return False
        
        # Try to unlock it
        if not self.unlock_chest(chest):
            return False
            
        # Try to open it
        if not self.open_chest(chest):
            return False
            
        # Move all items
        self.move_items(chest)
        return True

def main():
    """Main script function"""
    treasure_manager = TreasureManager()
    
    # Verify backpack
    if not Player.Backpack:
        treasure_manager.debug_message("No backpack found!", treasure_manager.error_color)
        return
        
    # Try to loot chest
    if not treasure_manager.loot_chest():
        treasure_manager.debug_message("Failed to loot chest", treasure_manager.error_color)

# Start the script
if __name__ == '__main__':
    main()
