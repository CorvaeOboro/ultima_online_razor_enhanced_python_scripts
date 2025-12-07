"""
ITEM Transfer Container to Backpack - a Razor Enhanced Python Script for Ultima Online

- Target a container to move items from
- Moves all items from container to player's backpack
- Uses server sync method for reliable timing (with fallback to hardcoded delay)
- Implements round-robin retry logic for failed items
- Re-fetches items after each move to verify success

HOTKEY:: CTRL + P
VERSION::20251024
"""

# === CONFIGURATION ===
USE_SERVER_SYNC = True  # Use server sync method for delays (recommended)
FALLBACK_DELAY = 600  # Fallback delay if server sync fails (in milliseconds)
MAX_RETRY_COUNT = 3  # Number of times to retry moving an item

DEBUG_MODE = False  # Set to True to enable debug/info messages

def debug_message(msg, color=68):
    if DEBUG_MODE:
        Misc.SendMessage(f"[ContainerXfer] {msg}", color)

def server_sync_delay():
    """Synchronize with server using backpack label check.
    This provides a natural server-synced delay that matches server response time.
    More reliable than arbitrary Misc.Pause() delays.
    Falls back to FALLBACK_DELAY if GetLabel fails.
    """
    try:
        # GetLabel forces client to wait for server response
        # This naturally syncs with server tick rate
        Items.GetLabel(Player.Backpack.Serial)
        debug_message("Server sync successful", 68)
    except Exception as e:
        # Fallback to configured delay if GetLabel fails
        debug_message(f"Server sync failed ({e}), using fallback delay: {FALLBACK_DELAY}ms", 53)
        Misc.Pause(FALLBACK_DELAY)

def get_container():
    """Prompt user to select a container and return it"""
    debug_message("Target the container to move items from...", 66)
    container = Target.PromptTarget()
    
    if container == -1:
        debug_message("Invalid container selection!", 33)
        return None
        
    container_item = Items.FindBySerial(container)
    if not container_item:
        debug_message("Container not found!", 33)
        return None
        
    return container_item

def verify_backpack():
    """Verify player has a backpack"""
    if not Player.Backpack:
        debug_message("No backpack found!", 33)
        return False
    return True

def move_items(container):
    """Move all items from container to backpack using round-robin retry logic.
    Each item is attempted once per round, skipping failed items until all are tried,
    then retries up to MAX_RETRY_COUNT rounds.
    """
    attempt = 0
    moved_items = 0
    total_items = 0
    failed_serials = set()
    
    while attempt < MAX_RETRY_COUNT:
        # Always re-fetch the current item list from the container at the start of each round
        container_obj = Items.FindBySerial(container.Serial)
        if not container_obj or not hasattr(container_obj, 'Contains') or not container_obj.Contains:
            if attempt == 0:
                debug_message("Container is empty!", 33)
            break
            
        items = list(container_obj.Contains)
        
        if attempt == 0:
            total_items = len(items)
            failed_serials = set([item.Serial for item in items])
            debug_message(f"Moving {total_items} items to backpack...", 66)
        else:
            # Only try to move items that failed in previous rounds
            items = [item for item in items if item.Serial in failed_serials]
            
        if not items:
            break
            
        debug_message(f"Round {attempt+1}: Attempting to move {len(items)} items...", 66)
        next_failed_serials = set()
        
        for item in items:
            # Re-fetch item object in case container changed or item was moved externally
            item_obj = Items.FindBySerial(item.Serial)
            if not item_obj or not hasattr(item_obj, 'Container') or item_obj.Container != container.Serial:
                debug_message(f"Item {item.Serial:X} not found in container, skipping.", 68)
                continue  # Already moved or gone
                
            # Attempt to move item to backpack
            if attempt_move_item_to_backpack(item_obj):
                moved_items += 1
                if moved_items % 5 == 0:  # Show progress every 5 items
                    debug_message(f"Moved {moved_items}/{total_items} items...", 66)
            else:
                next_failed_serials.add(item_obj.Serial)
                
        failed_serials = next_failed_serials
        attempt += 1
        
    if failed_serials:
        debug_message(f"Failed to move {len(failed_serials)} items after {MAX_RETRY_COUNT} rounds!", 33)
        
    debug_message(f"Finished moving items! Successfully moved {moved_items}/{total_items} items.", 67)

def attempt_move_item_to_backpack(item):
    """Attempt to move the given item to the player's backpack.
    Returns True on success, False otherwise.
    Re-fetches item after move to verify success.
    """
    try:
        # Store initial container before move
        initial_container = item.Container
        
        Items.Move(item, Player.Backpack, 0)
        if USE_SERVER_SYNC:
            server_sync_delay()
        else:
            Misc.Pause(FALLBACK_DELAY)
        
        # Re-fetch the item to get updated state
        moved_item = Items.FindBySerial(item.Serial)
        if not moved_item:
            # Item no longer exists (stacked or deleted) - consider success
            return True
        
        # Check if item is now in backpack
        if moved_item.Container == Player.Backpack.Serial:
            return True
        
        # Check if container changed at all (might have moved somewhere)
        if moved_item.Container != initial_container:
            debug_message(f"Item {item.Serial:X} moved but not to backpack (container changed)", 68)
            return True
            
    except Exception as e:
        debug_message(f"Error moving item {item.Serial:X}: {e}", 33)
        pass
        
    return False

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
