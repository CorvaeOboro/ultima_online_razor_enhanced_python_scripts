"""
COMBAT Cancel Casting - a Razor Enhanced Python Script for Ultima Online

Interrupt current spell cast 
Razor Enhanced API: Spells.Interrupt() - Interrupts the casting of a spell by performing an equip/unequip.

CHANGELOG:: initially this script was trying to do the equip / unequip manually 
targeting a specific "least important" item layer , such that it didnt have stats ,
and whose visual change would be minimal ( apron , shoes , depending on the outfit ) 
however the api function is much cleaner and faster 

HOTKEY:: ESC
VERSION:: 20251014
"""
DEBUG_MODE = False  # Set True for verbose messages

def debug_message(msg, color=67):
    """Send debug message if DEBUG_MODE is enabled."""
    if DEBUG_MODE:
        try:
            Misc.SendMessage(f"[CANCEL_CAST] {msg}", color)
        except Exception:
            pass

def main():
    """Interrupt current spell casting using built-in API."""
    try:
        debug_message("Interrupting spell cast...", 67)
        Spells.Interrupt()
        debug_message("Spell cast interrupted.", 68)
    except Exception as e:
        debug_message(f"Error interrupting spell: {e}", 33)
        Misc.SendMessage(f"[CANCEL_CAST] Error: {e}", 33)

if __name__ == "__main__":
    main()