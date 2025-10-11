"""
SPELL INVIS SELF - A Razor Enhanced Python Script for Ultima Online

Casts Invisibility and targets self.

TODO:
make mana check optional ( "lower mana cost" modifiers might make this fail when it could cast it )
deal with already casting or existing target 
errors on fail ( not invisible ) 

HOTKEY:: I ( for Invisible )
VERSION::20250925
"""

import time

DEBUG_MODE = False
SPELL_INVIS = "Invisibility"
INVIS_MANA_COST = 20

# Config: make mana check optional
CHECK_MANA = False  # Set to True to require minimum mana, False to always attempt cast

CAST_TIMEOUT = 3  # seconds
TARGET_TIMEOUT = 2  # seconds
REPEAT_UNTIL_INVIS = True  # Set to False to only try once
MAX_ATTEMPTS = 5  # Safety limit if repeat is enabled

#//============================================================

def can_cast_invis():
    if not CHECK_MANA:
        return True
    return Player.Mana >= INVIS_MANA_COST


def debug_message(msg, color=68):
    if DEBUG_MODE:
        Misc.SendMessage(f"[SPELL_INVIS] {msg}", color)


def cast_invis_self():
    attempts = 0
    while True:
        # Cancel any existing target cursor or spellcast before casting
        if Target.HasTarget():
            debug_message("Target cursor already up, cancelling first.", 33)
            Target.Cancel()
            Misc.Pause(100)
        # Check mana if enabled
        if not can_cast_invis():
            debug_message("Not enough mana to cast Invisibility!", 33)
            return
        debug_message(f"Casting Invisibility... (attempt {attempts+1})", 68)
        Spells.Cast(SPELL_INVIS)
        # Wait for target cursor
        start = time.time()
        while not Target.HasTarget() and (time.time() - start) < CAST_TIMEOUT:
            Misc.Pause(50)
        if Target.HasTarget():
            Target.Self()
            debug_message("Invisibility targeted on self.", 68)
        else:
            debug_message("No target cursor appeared!", 33)
        Misc.Pause(600)
        if Player.BuffsExist("Invisibility") or Player.Hidden:
            debug_message("Player is now invisible!", 67)
            break
        attempts += 1
        if not REPEAT_UNTIL_INVIS or attempts >= MAX_ATTEMPTS:
            debug_message("Failed to become invisible after attempts.", 33)
            break
        debug_message("Retrying invisibility...", 33)
        Misc.Pause(600)

if __name__ == '__main__':
    cast_invis_self()
