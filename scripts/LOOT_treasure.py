"""
LOOT Treasure Chest Lockpick - a Razor Enhanced Python script for Ultima Online

- Uses lockpicks to unlock nearby chests
- Opens chests ( no disarm ) and extracts items

TODO: 
drop resources on the ground near chest 
auto stop if cant pickup
if overweight drop gold on ground , then salvage , then pickup gold 

VERSION::20250713
"""

from System.Collections.Generic import List
from System import Int32

DROP_RESOURCES_GROUND = False  # If True, drop resource items on ground. If False, move to backpack.
DEBUG_MODE = True  # If False, suppress all Misc.SendMessage output

class TreasureManager:
    def is_overweight(self):
        """Returns True if player is overweight (checks weight and Journal)."""
        return self.journal_overweight() or self.weight_overweight()

    def journal_overweight(self):
        """Check the Journal for the overweight message."""
        return Journal.Search("That container cannot hold more weight.")

    def weight_overweight(self):
        try:
            return Player.Weight > Player.MaxWeight
        except:
            self.debug("Could not determine player weight.", self.error_color)
            return False

    def drop_all_gold_at_feet(self):
        """Drops all gold from backpack at (or near) player's feet. Splits large stacks if needed, with robust re-querying and debug."""
        # Gold coins: 0x0EED
        max_stack = 60000
        dropped = 0
        attempts = 0
        while True:
            gold_items = Items.FindByID(0x0EED, -1, Player.Backpack.Serial, -1)
            if not gold_items:
                break
            if not isinstance(gold_items, list):
                gold_items = [gold_items]
            dropped_this_pass = 0
            for gold in gold_items:
                if gold.Amount > max_stack:
                    self.debug(f"Splitting gold stack {gold.Serial:X} of {gold.Amount}", self.error_color)
                    try:
                        Items.Move(gold, Player.Backpack, max_stack)
                        Misc.Pause(self.move_delay)
                    except:
                        self.debug(f"Failed to split gold stack {gold.Serial:X}", self.error_color)
                    continue  # Will re-query and try again
                positions = self.get_nearby_drop_positions(Player.Position.X, Player.Position.Y, Player.Position.Z)
                success = False
                for (x, y, z) in positions:
                    self.debug(f"Trying to drop {gold.Amount} gold at ({x},{y},{z}) from stack {gold.Serial:X}", self.debug_color)
                    try:
                        Items.Move(gold, 0xFFFFFFFF, 0, x, y, z)
                        Misc.Pause(self.move_delay)
                        # Confirm gold is no longer in backpack
                        found = Items.FindBySerial(gold.Serial)
                        if found is None or found.Container != Player.Backpack.Serial:
                            dropped += 1
                            dropped_this_pass += 1
                            success = True
                            self.debug(f"Dropped {gold.Amount} gold at ({x},{y},{z}) from stack {gold.Serial:X}", self.success_color)
                            break
                    except Exception as e:
                        self.debug(f"Exception dropping gold: {e}", self.error_color)
                        continue
                if not success:
                    # Fallback: try dropping 1 coin at a time
                    if gold.Amount > 1:
                        self.debug(f"Trying fallback: splitting {gold.Amount} gold into 1 coin", self.error_color)
                        try:
                            Items.Move(gold, Player.Backpack, 1)
                            Misc.Pause(self.move_delay)
                        except:
                            self.debug(f"Failed to split 1 coin from stack {gold.Serial:X}", self.error_color)
                        continue  # Will re-query and try again
                    else:
                        self.debug(f"Failed to drop gold stack {gold.Serial:X} at any nearby position, even as single coin!", self.error_color)
            if dropped_this_pass == 0:
                break  # Prevent infinite loop if nothing was dropped
            attempts += 1
            if attempts > 50:
                self.debug("Too many attempts to drop gold, aborting to avoid infinite loop.", self.error_color)
                break
        self.debug(f"Dropped {dropped} gold stack(s)/coins at/near your feet.", self.success_color)

    def __init__(self):
        self.debug_color = 67  # Light blue for messages
        self.error_color = 33  # Red for errors
        self.success_color = 68  # Green for success
        
        # Item IDs
        self.chest_types = [0x0E40, 0x0E41, 0x0E42, 0x0E43, 0xB061, 0xB05D, 0xB060, 0xB051, 0xC056, 0xC057, 0xB05C]  # Different treasure chest types
        self.lockpick_type = 0x14FC
        
        # Timing configuration
        self.lockpick_delay = 1000    # 1 second between lockpick attempts
        self.open_delay = 1500        # 1.5 seconds after opening
        self.move_delay = 600         # 0.6 seconds between moving items
        self.retry_delay = 500        # 0.5 seconds before retrying
        
        # Search configuration
        self.search_range = 3         # Tiles to search for chests
        self.max_retry_count = 3      # Number of times to retry moving an item
        
    def debug(self, message, color=None):
        """Send a debug message to the game client (respects DEBUG_MESSAGES_ON global)"""
        if color is None:
            color = self.debug_color
        if DEBUG_MODE:
            Misc.SendMessage(f"[Treasure] {message}", color)
    
    def find_nearby_chest(self):
        """Find the nearest unopened treasure chest"""
        self.debug("Searching for treasure chests...")
        
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
                self.debug(f"Found chest at {chest.Position}", self.success_color)
                return chest
                
        self.debug("No chests found nearby", self.error_color)
        return None
    
    def find_lockpicks(self):
        """Find lockpicks in backpack"""
        lockpicks = Items.FindByID(self.lockpick_type, -1, Player.Backpack.Serial, -1)
        if not lockpicks:
            self.debug("No lockpicks found!", self.error_color)
            return None
        return lockpicks
    
    def unlock_chest(self, chest):
        """Attempt to unlock the chest"""
        self.debug("Attempting to unlock chest...")
        
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
        """Open the chest and wait for contents"""
        self.debug("Opening chest...")
        Items.UseItem(chest)
        Misc.Pause(self.open_delay)
        return True
    
    def is_resource_item(self, item):
        # Define resource item IDs (add more as needed)
        resource_ids = [
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
        ]
        return item.ItemID in resource_ids

    def get_nearby_drop_positions(self, center_x, center_y, center_z):
        # Spiral/adjacent pattern (center, N, E, S, W, diagonals, extended)
        offsets = [
            (0, 0), (0, 1), (1, 0), (0, -1), (-1, 0),
            (1, 1), (1, -1), (-1, -1), (-1, 1),
            (0, 2), (2, 0), (0, -2), (-2, 0)
        ]
        return [(center_x + dx, center_y + dy, center_z) for dx, dy in offsets]

    def try_drop_on_ground(self, item):
        # Drop item directly at player's feet (current position)
        x, y, z = Player.Position.X, Player.Position.Y, Player.Position.Z
        try:
            Items.Move(item, 0xFFFFFFFF, 0, x, y, z)  # 0xFFFFFFFF = ground
            Misc.Pause(self.move_delay)
            # Check if item is no longer in chest (moved)
            if Items.FindBySerial(item.Serial).Container != item.Container:
                self.debug(f"Dropped resource item {item.Serial:X} at ({x},{y})", self.success_color)
                return True
        except:
            pass
        self.debug(f"Failed to drop resource item {item.Serial:X} at player's feet!", self.error_color)
        return False

    def move_items(self, container):
        """Move all items from container to backpack or drop resources on ground. If overweight, drop all gold at feet."""
        items = Items.FindBySerial(container.Serial).Contains
        if not items:
            self.debug("Chest is empty!", self.error_color)
            return
        total_items = len(items)
        moved_items = 0
        self.debug(f"Moving {total_items} items to backpack/ground...")
        for item in items:
            retry_count = 0
            success = False
            if self.is_resource_item(item):
                if DROP_RESOURCES_GROUND:
                    # Try to drop on ground (original logic)
                    while retry_count < self.max_retry_count:
                        if self.try_drop_on_ground(item):
                            moved_items += 1
                            success = True
                            break
                        retry_count += 1
                    if not success:
                        self.debug(f"Failed to drop resource item {item.Serial:X} after {self.max_retry_count} attempts!", self.error_color)
                else:
                    # Move resource to backpack like other items
                    while retry_count < self.max_retry_count:
                        try:
                            Journal.Clear("That container cannot hold more weight.")
                            Items.Move(item, Player.Backpack, 0)
                            Misc.Pause(self.move_delay)
                            if Items.FindBySerial(item.Serial).Container == Player.Backpack.Serial:
                                moved_items += 1
                                success = True
                                if moved_items % 5 == 0:
                                    self.debug(f"Moved {moved_items}/{total_items} items...")
                                break
                            retry_count += 1
                            Misc.Pause(self.retry_delay)
                        except:
                            retry_count += 1
                            Misc.Pause(self.retry_delay)
                    if not success:
                        self.debug(f"Failed to move resource item {item.Serial:X} after {self.max_retry_count} attempts!", self.error_color)
            else:
                # Move to backpack as before
                while retry_count < self.max_retry_count:
                    try:
                        Journal.Clear("That container cannot hold more weight.")
                        Items.Move(item, Player.Backpack, 0)
                        Misc.Pause(self.move_delay)
                        if Items.FindBySerial(item.Serial).Container == Player.Backpack.Serial:
                            moved_items += 1
                            success = True
                            if moved_items % 5 == 0:
                                self.debug(f"Moved {moved_items}/{total_items} items...")
                            break
                        retry_count += 1
                        Misc.Pause(self.retry_delay)
                    except:
                        retry_count += 1
                        Misc.Pause(self.retry_delay)
                if not success:
                    self.debug(f"Failed to move item {item.Serial:X} after {self.max_retry_count} attempts!", self.error_color)

            # Check overweight after each move
            if self.journal_overweight():
                self.debug("Player is overweight! Dropping all gold at feet...", self.error_color)
                self.drop_all_gold_at_feet()
                Journal.Clear("That container cannot hold more weight.")

        self.debug(f"Finished moving items! Successfully moved {moved_items}/{total_items} items.", self.success_color)

        """Move all items from container to backpack or drop resources on ground"""
        items = Items.FindBySerial(container.Serial).Contains
        if not items:
            self.debug("Chest is empty!", self.error_color)
            return
        total_items = len(items)
        moved_items = 0
        self.debug(f"Moving {total_items} items to backpack/ground...")
        for item in items:
            retry_count = 0
            success = False
            if self.is_resource_item(item):
                if DROP_RESOURCES_GROUND:
                    # Try to drop on ground (original logic)
                    while retry_count < self.max_retry_count:
                        if self.try_drop_on_ground(item):
                            moved_items += 1
                            success = True
                            break
                        retry_count += 1
                    if not success:
                        self.debug(f"Failed to drop resource item {item.Serial:X} after {self.max_retry_count} attempts!", self.error_color)
                else:
                    # Move resource to backpack like other items
                    while retry_count < self.max_retry_count:
                        try:
                            Items.Move(item, Player.Backpack, 0)
                            Misc.Pause(self.move_delay)
                            if Items.FindBySerial(item.Serial).Container == Player.Backpack.Serial:
                                moved_items += 1
                                success = True
                                if moved_items % 5 == 0:
                                    self.debug(f"Moved {moved_items}/{total_items} items...")
                                break
                            retry_count += 1
                            Misc.Pause(self.retry_delay)
                        except:
                            retry_count += 1
                            Misc.Pause(self.retry_delay)
                    if not success:
                        self.debug(f"Failed to move resource item {item.Serial:X} after {self.max_retry_count} attempts!", self.error_color)
            else:
                # Move to backpack as before
                while retry_count < self.max_retry_count:
                    try:
                        Items.Move(item, Player.Backpack, 0)
                        Misc.Pause(self.move_delay)
                        if Items.FindBySerial(item.Serial).Container == Player.Backpack.Serial:
                            moved_items += 1
                            success = True
                            if moved_items % 5 == 0:
                                self.debug(f"Moved {moved_items}/{total_items} items...")
                            break
                        retry_count += 1
                        Misc.Pause(self.retry_delay)
                    except:
                        retry_count += 1
                        Misc.Pause(self.retry_delay)
                if not success:
                    self.debug(f"Failed to move item {item.Serial:X} after {self.max_retry_count} attempts!", self.error_color)
        self.debug(f"Finished moving items! Successfully moved {moved_items}/{total_items} items.", self.success_color)
    
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
        treasure_manager.debug("No backpack found!", treasure_manager.error_color)
        return
        
    # Try to loot chest
    if not treasure_manager.loot_chest():
        treasure_manager.debug("Failed to loot chest", treasure_manager.error_color)

# Start the script
if __name__ == '__main__':
    main()
