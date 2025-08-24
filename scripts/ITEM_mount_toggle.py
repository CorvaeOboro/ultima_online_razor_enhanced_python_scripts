"""
Mount Toggle Script - a Razor Enhanced Python Script for Ultima Online

Toggles mounting/dismounting of an ethereal horse:
1. If not mounted: Searches backpack for ethereal horse and uses it
2. If mounted: Uses client action to dismount
3. Reports status via system messages if SHOW_DEBUG_INFO is True

Requirements:
Item: Ethereal Horse Statuette (0x20DD)

HOTKEY:: MiddleMouseButton
VERSION::20250823
"""

# Mount item ID for Ethereal Horse Statuette
MOUNT_ID = 0x20DD

SHOW_DEBUG_INFO = True

def debug_msg(msg, color=67):
    if SHOW_DEBUG_INFO:
        Misc.SendMessage(msg, color)

def is_mounted():
    """Check if the player is currently mounted."""
    mounted = Player.Mount is not None
    debug_msg(f"Mount status check - Is Mounted: {mounted}", 67)
    if mounted:
        try:
            debug_msg(f"Current Mount Info:", 67)
            debug_msg(f"- Serial: {hex(Player.Mount.Serial)}", 67)
            debug_msg(f"- ID: {hex(Player.Mount.ItemID)}", 67)
        except Exception as e:
            debug_msg(f"Error getting mount details: {str(e)}", 33)
    return mounted

def find_mount():
    """Search for mount item in backpack."""
    mount = Items.FindByID(MOUNT_ID, -1, Player.Backpack.Serial)
    if mount:
        try:
            # Verify the mount is actually in our backpack
            if mount.Container != Player.Backpack.Serial:
                debug_msg("Mount item found but not in backpack!", 33)
                return None
                
            debug_msg(f"Found mount item:", 67)
            debug_msg(f"- Serial: {hex(mount.Serial)}", 67)
            debug_msg(f"- ID: {hex(mount.ItemID)}", 67)
            debug_msg(f"- Container: {hex(mount.Container)}", 67)
        except Exception as e:
            debug_msg(f"Error getting mount item details: {str(e)}", 33)
            return None
    else:
        debug_msg("No mount item found in backpack", 33)
    return mount

def try_mount():
    """Attempt to mount using the ethereal mount item."""
    mount = find_mount()
    if not mount:
        debug_msg("No ethereal mount found in backpack!", 33)
        return False
        
    debug_msg(f"Attempting to mount using item serial: {hex(mount.Serial)}", 67)
    try:
        Items.UseItem(mount)
        
        # Wait and check state with retry
        for _ in range(3):  # Try up to 3 times
            Misc.Pause(300)  # Wait between checks
            if is_mounted():
                debug_msg("Successfully mounted!", 67)
                return True
        
        debug_msg("Failed to mount - not mounted after attempt", 33)
        return False
    except Exception as e:
        debug_msg(f"Error during mounting: {str(e)}", 33)
        return False

def try_dismount():
    """Attempt to dismount from the current mount."""
    if not is_mounted():
        debug_msg("Not currently mounted!", 33)
        return False
        
    debug_msg("Attempting to dismount...", 67)
    try:
        mount = Player.Mount
        if not mount:
            debug_msg("Could not access mount object!", 33)
            return False
            
        # Preferred: double-click the ethereal statuette in backpack (toggles dismount)
        eth_item = find_mount()
        if eth_item:
            debug_msg(f"Attempting dismount by using statuette: {hex(eth_item.Serial)}", 67)
            Items.UseItem(eth_item)
        else:
            debug_msg("Ethereal statuette not found in backpack; skipping to fallback.", 33)
        
        # Wait and check state with retry
        for _ in range(3):  # Try up to 3 times
            Misc.Pause(300)  # Wait between checks
            if not is_mounted():
                debug_msg("Successfully dismounted!", 67)
                return True
            
        # Fallback: try to use the current mount object directly
        debug_msg("First attempt failed, trying fallback by using mount object...", 33)
        debug_msg(f"Attempting to use mount object: serial {hex(mount.Serial)}", 67)
        Misc.UseObject(mount.Serial)
        Misc.Pause(300)
        
        if not is_mounted():
            debug_msg("Successfully dismounted!", 67)
            return True
            
        # Last resort - attempt another statuette use in case of laggy first attempt
        if eth_item:
            debug_msg("Trying final method: re-use statuette...", 33)
            Items.UseItem(eth_item)
            Misc.Pause(300)
            if not is_mounted():
                debug_msg("Successfully dismounted!", 67)
                return True
        
        debug_msg("Failed to dismount after all attempts", 33)
        return False
    except Exception as e:
        debug_msg(f"Error during dismounting: {str(e)}", 33)
        return False

def toggle_mount():
    """Toggle between mounted and dismounted state."""
    if is_mounted():
        try_dismount()
    else:
        try_mount()

# Run the toggle
if __name__ == "__main__":
    debug_msg("Starting mount toggle script...", 67)
    toggle_mount()
