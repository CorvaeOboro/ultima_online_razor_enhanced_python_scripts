"""
ITEM Use Flowers - a Razor Enhanced Python Script for Ultima Online

Finds flowers (ItemID 0x234D) in a targeted chest, transfers them to backpack,
then uses each flower by double-clicking it , then transfer all flowers and petals back

HOTKEY:: 
VERSION::20251205
"""

from System.Collections.Generic import List
from System import Int32

# === CONFIGURATION ===
DEBUG_MODE = False  # Set to False to suppress debug output
USE_SERVER_SYNC = True  # Use server sync method for delays
FALLBACK_DELAY = 600  # Fallback delay if server sync fails (in milliseconds)
FLOWER_ITEM_ID = 0x234D  # Flower ItemID
FLOWER_ITEM_ID_VARIANT = 0xB12E
MOVE_FLOWERS_TO_BACKPACK = True
RETURN_PETALS_TO_CONTAINER = True
PETAL_ITEM_ID = 0x1021
USE_DELAY_MS = 800  # Delay between using flowers
MAX_RETRY_COUNT = 3  # Number of times to retry moving an item

def server_sync_delay():
    """Synchronize with server by checking backpack serial.
    This provides a natural server-synced delay that matches server response time.
    Falls back to FALLBACK_DELAY if check fails.
    """
    try:
        # Simple check that forces server sync
        _ = Player.Backpack.Serial
        Misc.Pause(FALLBACK_DELAY)
    except Exception as e:
        if DEBUG_MODE:
            debug_message(f"Server sync failed ({e}), using fallback delay: {FALLBACK_DELAY}ms", 53)
        Misc.Pause(FALLBACK_DELAY)

def debug_message(msg, color=68):
    """Send a debug message to the game client."""
    if DEBUG_MODE:
        Misc.SendMessage(f"[Flowers] {msg}", color)

def prompt_for_container():
    """Prompt the user to target a container and return its serial or None."""
    debug_message("Target the container with flowers...", 65)
    Misc.SendMessage("Target the container with flowers...", 65)
    try:
        serial = Target.PromptTarget()
    except:
        return None
    if not serial:
        return None
    cont = Items.FindBySerial(serial)
    if not cont:
        debug_message("Invalid target.", 33)
        return None
    # Open to ensure contents loaded
    Items.UseItem(cont.Serial)
    if USE_SERVER_SYNC:
        server_sync_delay()
    else:
        Misc.Pause(FALLBACK_DELAY)
    return cont.Serial

def get_container_flowers(container_serial):
    """Return list of flowers from targeted container."""
    flowers = []
    cont = Items.FindBySerial(container_serial)
    if not cont:
        return flowers

    # Ensure fresh contents
    Items.UseItem(cont.Serial)
    if USE_SERVER_SYNC:
        server_sync_delay()
    else:
        Misc.Pause(300)

    # Re-fetch container to get updated contents
    cont = Items.FindBySerial(container_serial)
    if not cont or not hasattr(cont, 'Contains') or not cont.Contains:
        debug_message("Container is empty or has no contents!", 33)
        return flowers

    items = cont.Contains
    for item in items:
        if item.ItemID == FLOWER_ITEM_ID or item.ItemID == FLOWER_ITEM_ID_VARIANT:
            flowers.append(item)

    return flowers

def get_backpack_flowers():
    """Find all flowers in backpack."""
    flowers = []
    bp = Items.FindBySerial(Player.Backpack.Serial)
    if not bp or not hasattr(bp, 'Contains') or not bp.Contains:
        return flowers
    
    items = bp.Contains
    for item in items:
        if item.ItemID == FLOWER_ITEM_ID or item.ItemID == FLOWER_ITEM_ID_VARIANT:
            flowers.append(item)
    
    return flowers

def get_backpack_petals():
    petals = []
    bp = Items.FindBySerial(Player.Backpack.Serial)
    if not bp or not hasattr(bp, 'Contains') or not bp.Contains:
        return petals

    items = bp.Contains
    for item in items:
        if item.ItemID == PETAL_ITEM_ID:
            petals.append(item)

    return petals

def move_item_to_backpack(item):
    """Attempt to move the given item to the player's backpack.
    Returns True on success, False otherwise.
    """
    retry_count = 0
    while retry_count < MAX_RETRY_COUNT:
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
                if retry_count > 0:
                    debug_message(f"Moved flower {item.Serial:X} after {retry_count+1} attempts.")
                return True
            
            # Check if container changed at all (might have moved somewhere)
            if moved_item.Container != initial_container:
                debug_message(f"Flower {item.Serial:X} moved but not to backpack (container changed)")
                return True
                
        except Exception as e:
            debug_message(f"Error moving flower {item.Serial:X}: {e}", 33)
            pass
        
        retry_count += 1
    
    return False

def transfer_flowers_to_backpack(container_serial):
    """Transfer all flowers from container to backpack.
    Returns count of successfully moved flowers.
    """
    moved_count = 0
    attempt = 0
    failed_serials = set()
    
    while attempt < MAX_RETRY_COUNT:
        flowers = get_container_flowers(container_serial)
        
        if attempt == 0:
            if not flowers:
                debug_message("No flowers found in container!", 33)
                return 0
            debug_message(f"Found {len(flowers)} flower(s) in container.", 90)
            failed_serials = set([flower.Serial for flower in flowers])
        else:
            # Only try to move flowers that failed in previous rounds
            flowers = [f for f in flowers if f.Serial in failed_serials]
        
        if not flowers:
            break
        
        debug_message(f"Transfer round {attempt+1}: Attempting to move {len(flowers)} flower(s)...")
        next_failed_serials = set()
        
        for flower in flowers:
            # Re-fetch flower object in case container changed
            flower_obj = Items.FindBySerial(flower.Serial)
            if not flower_obj or not hasattr(flower_obj, 'Container') or flower_obj.Container != container_serial:
                debug_message(f"Flower {flower.Serial:X} not found in container, skipping.", 68)
                continue  # Already moved or gone
            
            if move_item_to_backpack(flower_obj):
                moved_count += 1
                debug_message(f"Moved flower {flower_obj.Serial:X} to backpack ({moved_count} total)", 68)
            else:
                next_failed_serials.add(flower_obj.Serial)
        
        failed_serials = next_failed_serials
        attempt += 1
    
    if failed_serials:
        debug_message(f"Failed to move {len(failed_serials)} flower(s) after {MAX_RETRY_COUNT} rounds!", 33)
    
    debug_message(f"Transfer complete! Moved {moved_count} flower(s) to backpack.", 90)
    return moved_count

def use_flower(flower):
    """Use (double-click) a flower item.
    Returns True if the use was attempted, False otherwise.
    """
    try:
        debug_message(f"Using flower {flower.Serial:X} (hue: {flower.Hue})", 68)
        Items.UseItem(flower.Serial)
        Misc.Pause(USE_DELAY_MS)
        return True
    except Exception as e:
        debug_message(f"Error using flower {flower.Serial:X}: {e}", 33)
        return False

def use_all_backpack_flowers():
    """Use all flowers in backpack by double-clicking each one exactly once.
    Flowers are not consumed, they just lose petals, so we track serials.
    Returns count of flowers used.
    """
    used_serials = set()  # Track which flowers we've already used
    used_count = 0
    
    # Get all flowers in backpack
    flowers = get_backpack_flowers()
    
    if not flowers:
        debug_message("No flowers found in backpack!", 33)
        return 0
    
    debug_message(f"Found {len(flowers)} flower(s) in backpack.", 90)
    
    # Use each unique flower once
    for flower in flowers:
        if flower.Serial not in used_serials:
            if use_flower(flower):
                used_serials.add(flower.Serial)
                used_count += 1
                debug_message(f"Used flower {used_count} out of {len(flowers)}", 68)
            else:
                debug_message(f"Failed to use flower {flower.Serial:X}, skipping...", 33)
    
    debug_message(f"Complete! Used {used_count} flower(s).", 90)
    return used_count

def use_all_container_flowers(container_serial):
    used_serials = set()
    used_count = 0

    flowers = get_container_flowers(container_serial)
    if not flowers:
        debug_message("No flowers found in container!", 33)
        return 0

    debug_message(f"Found {len(flowers)} flower(s) in container.", 90)

    for flower in flowers:
        if flower.Serial not in used_serials:
            if use_flower(flower):
                used_serials.add(flower.Serial)
                used_count += 1
                debug_message(f"Used flower {used_count} out of {len(flowers)}", 68)
            else:
                debug_message(f"Failed to use flower {flower.Serial:X}, skipping...", 33)

    debug_message(f"Complete! Used {used_count} flower(s).", 90)
    return used_count

def return_flowers_to_container(container_serial):
    """Return all flowers from backpack to the original container.
    Returns count of flowers returned.
    """
    returned_count = 0
    attempt = 0
    failed_serials = set()
    
    while attempt < MAX_RETRY_COUNT:
        flowers = get_backpack_flowers()
        
        if attempt == 0:
            if not flowers:
                debug_message("No flowers in backpack to return.", 68)
                return 0
            debug_message(f"Returning {len(flowers)} flower(s) to container...", 90)
            failed_serials = set([flower.Serial for flower in flowers])
        else:
            # Only try to move flowers that failed in previous rounds
            flowers = [f for f in flowers if f.Serial in failed_serials]
        
        if not flowers:
            break
        
        debug_message(f"Return round {attempt+1}: Attempting to move {len(flowers)} flower(s)...")
        next_failed_serials = set()
        
        for flower in flowers:
            # Re-fetch flower object in case it changed
            flower_obj = Items.FindBySerial(flower.Serial)
            if not flower_obj or not hasattr(flower_obj, 'Container') or flower_obj.Container != Player.Backpack.Serial:
                debug_message(f"Flower {flower.Serial:X} not in backpack, skipping.", 68)
                continue  # Already moved or gone
            
            if move_item_to_container(flower_obj, container_serial):
                returned_count += 1
                debug_message(f"Returned flower {flower_obj.Serial:X} to container ({returned_count} total)", 68)
            else:
                next_failed_serials.add(flower_obj.Serial)
        
        failed_serials = next_failed_serials
        attempt += 1
    
    if failed_serials:
        debug_message(f"Failed to return {len(failed_serials)} flower(s) after {MAX_RETRY_COUNT} rounds!", 33)
    
    debug_message(f"Return complete! Moved {returned_count} flower(s) back to container.", 90)
    return returned_count

def return_petals_to_container(container_serial):
    returned_count = 0
    attempt = 0
    failed_serials = set()

    while attempt < MAX_RETRY_COUNT:
        petals = get_backpack_petals()

        if attempt == 0:
            if not petals:
                debug_message("No petals in backpack to return.", 68)
                return 0
            debug_message(f"Returning {len(petals)} petal(s) to container...", 90)
            failed_serials = set([p.Serial for p in petals])
        else:
            petals = [p for p in petals if p.Serial in failed_serials]

        if not petals:
            break

        debug_message(f"Petal return round {attempt+1}: Attempting to move {len(petals)} petal(s)...")
        next_failed_serials = set()

        for petal in petals:
            petal_obj = Items.FindBySerial(petal.Serial)
            if not petal_obj or not hasattr(petal_obj, 'Container') or petal_obj.Container != Player.Backpack.Serial:
                debug_message(f"Petal {petal.Serial:X} not in backpack, skipping.", 68)
                continue

            if move_item_to_container(petal_obj, container_serial):
                returned_count += 1
                debug_message(f"Returned petal {petal_obj.Serial:X} to container ({returned_count} total)", 68)
            else:
                next_failed_serials.add(petal_obj.Serial)

        failed_serials = next_failed_serials
        attempt += 1

    if failed_serials:
        debug_message(f"Failed to return {len(failed_serials)} petal(s) after {MAX_RETRY_COUNT} rounds!", 33)

    debug_message(f"Petal return complete! Moved {returned_count} petal(s) back to container.", 90)
    return returned_count

def move_item_to_container(item, container_serial):
    """Attempt to move the given item to a specific container.
    Returns True on success, False otherwise.
    """
    retry_count = 0
    container = Items.FindBySerial(container_serial)
    
    if not container:
        debug_message(f"Container {container_serial:X} not found!", 33)
        return False
    
    while retry_count < MAX_RETRY_COUNT:
        try:
            # Store initial container before move
            initial_container = item.Container
            
            Items.Move(item, container, 0)
            if USE_SERVER_SYNC:
                server_sync_delay()
            else:
                Misc.Pause(FALLBACK_DELAY)
            
            # Re-fetch the item to get updated state
            moved_item = Items.FindBySerial(item.Serial)
            if not moved_item:
                # Item no longer exists (stacked or deleted) - consider success
                return True
            
            # Check if item is now in target container
            if moved_item.Container == container_serial:
                if retry_count > 0:
                    debug_message(f"Moved item {item.Serial:X} after {retry_count+1} attempts.")
                return True
            
            # Check if container changed at all (might have moved somewhere)
            if moved_item.Container != initial_container:
                debug_message(f"Item {item.Serial:X} moved but not to target container")
                return True
                
        except Exception as e:
            debug_message(f"Error moving item {item.Serial:X}: {e}", 33)
            pass
        
        retry_count += 1
    
    return False

def main():
    """Main script function"""
    # Verify backpack
    if not Player.Backpack:
        debug_message("No backpack found!", 33)
        return
    
    # Prompt for container
    container_serial = prompt_for_container()
    if not container_serial:
        debug_message("No container selected. Exiting.", 33)
        return
    
    moved_count = 0
    returned_count = 0

    if MOVE_FLOWERS_TO_BACKPACK:
        # Transfer flowers from container to backpack
        moved_count = transfer_flowers_to_backpack(container_serial)
        if moved_count == 0:
            debug_message("No flowers were transferred. Exiting.", 33)
            return

        # Use all flowers in backpack
        debug_message("Starting to use flowers...", 90)
        Misc.Pause(500)
        used_count = use_all_backpack_flowers()

        # Return flowers to original container
        debug_message("Returning flowers to container...", 90)
        Misc.Pause(500)
        returned_count = return_flowers_to_container(container_serial)
    else:
        flowers = get_container_flowers(container_serial)
        if not flowers:
            debug_message("No flowers found in container. Exiting.", 33)
            return

        debug_message("Starting to use flowers in container...", 90)
        Misc.Pause(500)
        used_count = use_all_container_flowers(container_serial)

    returned_petals_count = 0
    if RETURN_PETALS_TO_CONTAINER:
        debug_message("Returning petals to container...", 90)
        Misc.Pause(500)
        returned_petals_count = return_petals_to_container(container_serial)

    if MOVE_FLOWERS_TO_BACKPACK:
        if RETURN_PETALS_TO_CONTAINER:
            debug_message(f"Complete! Transferred {moved_count}, used {used_count}, returned {returned_count} flower(s), returned {returned_petals_count} petal(s).", 90)
        else:
            debug_message(f"Complete! Transferred {moved_count}, used {used_count}, returned {returned_count} flower(s).", 90)
    else:
        if RETURN_PETALS_TO_CONTAINER:
            debug_message(f"Complete! Used {used_count} flower(s) in container, returned {returned_petals_count} petal(s).", 90)
        else:
            debug_message(f"Complete! Used {used_count} flower(s) in container.", 90)

if __name__ == "__main__":
    main()
