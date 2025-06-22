"""
ITEM Transfer Container to Backpack - a Razor Enhanced Python Script for Ultima Online

- Target a container to move items from
- Moves all items from container to player's backpack

VERSION::20250621
"""

from System.Collections.Generic import List

# Configuration
MOVE_DELAY = 600  # Delay between moving items (in milliseconds)
MAX_RETRY_COUNT = 3  # Number of times to retry moving an item

def get_container():
    """Prompt user to select a container and return it"""
    Misc.SendMessage("Target the container to move items from...", 66)
    container = Target.PromptTarget()
    
    if container == -1:
        Misc.SendMessage("Invalid container selection!", 33)
        return None
        
    container_item = Items.FindBySerial(container)
    if not container_item:
        Misc.SendMessage("Container not found!", 33)
        return None
        
    return container_item

def verify_backpack():
    """Verify player has a backpack"""
    if not Player.Backpack:
        Misc.SendMessage("No backpack found!", 33)
        return False
    return True

def move_items(container):
    """Move all items from container to backpack"""
    # Get list of items in container
    items = Items.FindBySerial(container.Serial).Contains
    if not items:
        Misc.SendMessage("Container is empty!", 33)
        return
        
    total_items = len(items)
    moved_items = 0
    
    Misc.SendMessage(f"Moving {total_items} items to backpack...", 66)
    
    for item in items:
        retry_count = 0
        while retry_count < MAX_RETRY_COUNT:
            try:
                # Move item to backpack
                Items.Move(item, Player.Backpack, 0)
                Misc.Pause(MOVE_DELAY)
                
                # Verify item was moved
                if Items.FindBySerial(item.Serial).Container == Player.Backpack.Serial:
                    moved_items += 1
                    if moved_items % 5 == 0:  # Show progress every 5 items
                        Misc.SendMessage(f"Moved {moved_items}/{total_items} items...", 66)
                    break
                    
                retry_count += 1
                Misc.Pause(500)  # Wait before retry
                
            except:
                retry_count += 1
                Misc.Pause(500)  # Wait before retry
                
        if retry_count == MAX_RETRY_COUNT:
            Misc.SendMessage(f"Failed to move item {item.Serial} after {MAX_RETRY_COUNT} attempts!", 33)
    
    # Show final results
    Misc.SendMessage(f"Finished moving items! Successfully moved {moved_items}/{total_items} items.", 67)

def main():
    """Main script function"""
    # Check for backpack
    if not verify_backpack():
        return
        
    # Get container from user
    container = get_container()
    if not container:
        return
        
    # Move items from container to backpack
    move_items(container)

# Start the script
if __name__ == '__main__':
    main()
