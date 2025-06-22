"""
Recall to Bank or Home- a Razor Enhanced Python script for Ultima Online

- Finds runebook named 'Runebook' in player's backpack
- Opens the runebook
- Uses the specific rune number
- Activates recall through the gump

VERSION::20250621
"""

RUNEBOOK_ID = 0x0EFA  # Runebook item ID
RUNEBOOK_NAME = "Runebook"  # Name of the runebook to find
GUMP_ID = 89  # Runebook gump ID
RUNE_NUMBER = 12  # Which rune in the runebook to recall to (1-based)
RECALL_BUTTON = 49 + RUNE_NUMBER
GUMP_TIMEOUT = 10000  # Timeout for gump operations in milliseconds
SHOW_DEBUG = True  # If False, suppress all Misc.SendMessage output

#//==================================================================
def debug_msg(msg, color=33):
    """Send a status/debug message if SHOW_DEBUG is enabled."""
    if SHOW_DEBUG:
        Misc.SendMessage(msg, color)

def find_runebook():
    """Find the named runebook in player's backpack"""
    if not Player.Backpack:
        debug_msg("No backpack found!", 33)
        return None
        
    # Find all runebooks (adding color parameter -1 for any color)
    runebooks = Items.FindAllByID(RUNEBOOK_ID, -1, Player.Backpack.Serial, -1)
    
    # Look for the specifically named runebook
    for book in runebooks:
        if book.Name == RUNEBOOK_NAME:
            return book
            
    debug_msg(f"No runebook named '{RUNEBOOK_NAME}' found in backpack!", 33)
    return None

def use_runebook():
    """Main function to use runebook and recall"""
    # Find runebook
    runebook = find_runebook()
    if not runebook:
        return False
        
    # Use runebook
    Items.UseItem(runebook)
    
    # Wait for and handle gump
    if Gumps.WaitForGump(GUMP_ID, GUMP_TIMEOUT):
        # Dynamically determine recall button based on RUNE_NUMBER
        gump_recall_button = RECALL_BUTTON
        debug_msg(f"Activating recall for rune {RUNE_NUMBER} (button {RECALL_BUTTON})...", 66)
        Gumps.SendAction(GUMP_ID, gump_recall_button)
        
        # Wait for recall to complete
        Misc.Pause(3000)
        return True
    else:
        debug_msg("Runebook gump not found!", 33)
        return False

def main():
    """Main script function"""
    Misc.SendMessage("Starting bank recall...", 66)
    
    # Try to recall
    if use_runebook():
        Misc.SendMessage("Successfully recalled to bank!", 67)
    else:
        Misc.SendMessage("Failed to recall to bank!", 33)

# Start the script
if __name__ == '__main__':
    main()
