"""
COMMAND Summon Pets - A Razor Enhanced Python Script for Ultima Online

Uses the player's context menu to invoke the "Summon Creature" action,
which recalls controlled/summoned creatures back to the player. 

Implementation:
- Misc.UseContextMenu(Player.Serial, "Summon Creature", 1000)

STATUS:: working
HOTKEY:: 7 ( 3-5 is other pet commands ) , 6 is retreat
VERSION::20251017
"""

DEBUG_MODE = False
WAIT_MS_AFTER_USE = 800 # How long to wait after using the context menu

# COLORS
CHAT_COLOR = 67  # light blue
ERROR_COLOR = 33  # orange
SUCCESS_COLOR = 68  # green

def debug_message(msg, color=CHAT_COLOR):
    if DEBUG_MODE:
        Misc.SendMessage(msg, color)

def try_context_menu_summon():
    """Invoke the "Summon Creature" entry on the player's context menu.
    Returns True if the context menu call was issued  False if an exception was raised.
    """
    try:
        Misc.UseContextMenu(Player.Serial, "Summon Creature", 1000)
        return True
    except Exception as e:
        Misc.SendMessage(f"Error using context menu: {e}", ERROR_COLOR)
        return False

def summon_pets():
    """Attempt to summon pets using the context menu once"""
    debug_message("Summoning pets via context menu...")
    ok = try_context_menu_summon()
    Misc.Pause(WAIT_MS_AFTER_USE)
    if ok:
        debug_message("Summon command issued via context menu.", SUCCESS_COLOR)
        return True
    else:
        debug_message("Failed to issue context menu summon.", ERROR_COLOR)
        return False

if __name__ == "__main__":
    debug_message("Starting Summon Pets Command script...")
    ok = summon_pets()
    if ok:
        debug_message("Done: Summon command issued via context menu.", SUCCESS_COLOR)
    else:
        debug_message("Done: Summon command failed to issue.", ERROR_COLOR)
