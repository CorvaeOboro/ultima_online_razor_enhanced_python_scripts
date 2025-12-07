"""
SPELL Recall to Bank or Home- a Razor Enhanced Python script for Ultima Online

- Finds runebook named 'Runebook' in player's backpack
- Opens the runebook
- Uses the specific rune number
- Activates recall through the gump

FEATURE: Location-based switching - recalls to home when at bank, recalls to bank when away 

STATUS::working
HOTKEY:: B
VERSION::20251206
"""
DEBUG_MODE = False  # If False, suppress all Misc.SendMessage output

USE_FALLBACK_RUNE_SEARCH = True  # Search for individual runes with "Bank" in name/properties
BANK_RUNE_NUMBER = 1  # Rune number to use when not at bank (recall to bank)
HOME_RUNE_NUMBER = 2  # Rune number to use when at bank (recall to home)

# Location-based switching configuration
LOCATION_BASED_SWITCH = True  # Enable/disable location-based rune selection
BANK_COORDINATES = (1416, 1687)  # Bank location coordinates
BANK_RANGE = 20  # Range to consider "near" the bank

RUNEBOOK_ID = 0x0EFA  # Runebook itbem ID
RUNEBOOK_NAME = "Runebook"  # Name of the runebook to find
GUMP_ID = 89  # Runebook gump ID
RUNE_NUMBER = 1  # Default rune number (will be overridden by location logic if enabled)
RECALL_BUTTON_NUMBER = 49 # add this to the rune number for the button
GUMP_TIMEOUT = 10000  # Timeout for gump operations in milliseconds

# Rune item configuration
RUNE_ITEM_ID = 0x1F14  # Individual rune item ID
RECALL_SPELL_NAME = "Recall"  # Magery Recall spell name

#//==================================================================
def debug_message(msg, color=33):
    """Send a status/debug message if DEBUG_MODE is enabled."""
    if DEBUG_MODE:
        Misc.SendMessage(f"[RECALL] {msg}", color)

def is_near_bank():
    """Check if player is near the bank coordinates"""
    if not LOCATION_BASED_SWITCH:
        return False
        
    player_x = Player.Position.X
    player_y = Player.Position.Y
    bank_x, bank_y = BANK_COORDINATES
    
    # Calculate distance 
    distance = ((player_x - bank_x) ** 2 + (player_y - bank_y) ** 2) ** 0.5
    
    debug_message(f"Player position: ({player_x}, {player_y}), Bank: ({bank_x}, {bank_y}), Distance: {distance:.1f}", 66)
    
    return distance <= BANK_RANGE

def get_target_rune_number():
    """Determine which rune to use based on location"""
    if not LOCATION_BASED_SWITCH:
        return RUNE_NUMBER
        
    if is_near_bank():
        debug_message(f"Near bank - using HOME rune #{HOME_RUNE_NUMBER}", 67)
        return HOME_RUNE_NUMBER
    else:
        debug_message(f"Not near bank - using BANK rune #{BANK_RUNE_NUMBER}", 67)
        return BANK_RUNE_NUMBER

def find_runebook():
    """Find the named runebook in player's backpack"""
    if not Player.Backpack:
        debug_message("No backpack found!", 33)
        return None
        
    # Find all runebooks (adding color parameter -1 for any color)
    runebooks = Items.FindAllByID(RUNEBOOK_ID, -1, Player.Backpack.Serial, -1)
    
    # Look for the specifically named runebook
    for book in runebooks:
        if book.Name == RUNEBOOK_NAME:
            return book
            
    debug_message(f"No runebook named '{RUNEBOOK_NAME}' found in backpack!", 33)
    return None

def find_bank_rune():
    """Find an individual rune with 'Bank' in name or properties"""
    if not Player.Backpack:
        debug_message("No backpack found!", 33)
        return None
    
    # Find all runes in backpack
    runes = Items.FindAllByID(RUNE_ITEM_ID, -1, Player.Backpack.Serial, -1)
    
    debug_message(f"Found {len(runes)} rune(s) in backpack", 66)
    
    # Search for rune with "Bank" in name or properties
    for rune in runes:
        # Check name
        if rune.Name and "bank" in rune.Name.lower():
            debug_message(f"Found bank rune by name: {rune.Name} (Serial: 0x{rune.Serial:X})", 67)
            return rune
        
        # Check properties
        try:
            props = Items.GetPropStringList(rune)
            if props:
                for prop in props:
                    if "bank" in prop.lower():
                        debug_message(f"Found bank rune by property: {rune.Name} - {prop} (Serial: 0x{rune.Serial:X})", 67)
                        return rune
        except:
            pass
    
    debug_message("No rune with 'Bank' in name or properties found!", 33)
    return None

def cast_recall_on_rune(rune):
    """Cast Recall spell and target the specified rune"""
    try:
        debug_message(f"Casting Recall on rune: {rune.Name} (Serial: 0x{rune.Serial:X})", 66)
        
        # Cast Recall spell
        Spells.CastMagery(RECALL_SPELL_NAME)
        
        # Give spell time to cast before waiting for target
        Misc.Pause(1000)
        
        # Wait for target cursor (longer timeout)
        if not Target.WaitForTarget(5000, False):
            debug_message("Target cursor did not appear!", 33)
            return False
        
        debug_message("Target cursor ready, targeting rune...", 66)
        
        # Target the rune - try with serial directly first, then with int conversion
        try:
            Target.TargetExecute(rune.Serial)
        except:
            try:
                Target.TargetExecute(int(rune.Serial))
            except Exception as e2:
                debug_message(f"Failed to target rune: {str(e2)}", 33)
                return False
        
        debug_message("Target executed, waiting for recall...", 66)
        
        # Wait for recall to complete
        Misc.Pause(3000)
        
        debug_message("Recall cast successfully!", 67)
        return True
        
    except Exception as e:
        debug_message(f"Error casting recall: {str(e)}", 33)
        return False

def use_runebook():
    """Main function to use runebook and recall"""
    # Find runebook
    runebook = find_runebook()
    if not runebook:
        return False
        
    # Determine which rune to use based on location
    target_rune = get_target_rune_number()
    target_button = RECALL_BUTTON_NUMBER + target_rune
        
    # Use runebook
    Items.UseItem(runebook)
    
    # Wait for and handle gump
    if Gumps.WaitForGump(GUMP_ID, GUMP_TIMEOUT):
        debug_message(f"Activating recall for rune {target_rune} (button {target_button})...", 66)
        Gumps.SendAction(GUMP_ID, target_button)
        
        # Wait for recall to complete
        Misc.Pause(3000)
        return True
    else:
        debug_message("Runebook gump not found!", 33)
        return False

def main():
    """Main script function"""
    debug_message("[RECALL] Starting bank recall...", 66)
    
    # Try runebook first
    if use_runebook():
        debug_message("[RECALL] Successfully recalled to bank!", 67)
        return
    
    # If runebook failed and fallback is enabled, try individual rune
    if USE_FALLBACK_RUNE_SEARCH:
        debug_message("[RECALL] Runebook not found, searching for individual bank rune...", 66)
        bank_rune = find_bank_rune()
        
        if bank_rune:
            if cast_recall_on_rune(bank_rune):
                debug_message("[RECALL] Successfully recalled using individual rune!", 67)
                return
        
        debug_message("[RECALL] Failed to find or use bank rune!", 33)
    else:
        debug_message("[RECALL] Failed to recall to bank!", 33)

# Start the script
if __name__ == '__main__':
    main()
