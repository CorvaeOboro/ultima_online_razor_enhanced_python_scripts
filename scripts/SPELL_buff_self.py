"""
 SPELL buff self - a Razor Enhanced Python Script for Ultima Online

 Casts Magic Reflection, Arch Protection, and Bless on self
 if buff may be found will skip  

HOTKEY:: T
VERSION::20250924
"""

DEBUG_MODE = False

SPELL_SEQUENCE = [
    'Magic Reflection',
    'Arch Protection',
    'Bless',
    ]

SPELL_CONFIG = {
    'Magic Reflection': {'pause': 600},
    'Arch Protection': {'pause': 600},
    'Bless': {'pause': 600},
    }

ALREADY_IN_EFFECT_TEXT = "This spell is already in effect" # Journal text when a spell is already in effect
CAST_PAUSE = 600 # Default pause after casting if no per-spell override is provided

def debug_message(msg, color=68):
    if DEBUG_MODE:
        Misc.SendMessage(f'[BuffSelf] {msg}', color)

def has_buff(buff_name):
    try:
        for i in range(Buffs.GetBuffCount()):
            name = Buffs.GetBuffName(i)
            if name and buff_name.lower() in name.lower():
                return True
        return False
    except Exception as e:
        debug_message('Error checking buff: {}'.format(e), 33)
        return False

def cast_spell(spell_name, pause_ms=None, skip_final_pause=False):
    try:
        Spells.Cast(spell_name)
        # Wait up to 2s for target cursor to appear
        waited = 0
        while not Target.HasTarget() and waited < 20:
            Misc.Pause(100)
            waited += 1
        if Target.HasTarget():
            Target.TargetExecute(Player.Serial)
            # Fallback: spam self-target for up to 1.5s if still targeting
            for _ in range(15):
                Misc.Pause(100)
                if not Target.HasTarget():
                    break
                Target.TargetExecute(Player.Serial)
        else:
            debug_message('No target cursor appeared for {}!'.format(spell_name), 33)
        if not skip_final_pause:
            Misc.Pause(pause_ms if pause_ms is not None else CAST_PAUSE)
    except Exception as e:
       debug_message('Error casting {}: {}'.format(spell_name, e), 33)

def main():
    for spell in SPELL_SEQUENCE:
        buff_name = spell  # Buff name matches spell name
        per_spell_pause = SPELL_CONFIG.get(spell, {}).get('pause', CAST_PAUSE)

        if not has_buff(buff_name):
            # For Magic Reflection, clear journal first to detect "already in effect" quickly
            if spell == 'Magic Reflection':
                Journal.Clear()

            debug_message('Casting {}...'.format(spell), 68)
            # For Magic Reflection, don't pay the cast pause up-front; we'll decide after journal check
            skip_pause = (spell == 'Magic Reflection')
            cast_spell(spell, pause_ms=per_spell_pause, skip_final_pause=skip_pause)

            # If the server reports the spell is already active, skip to the next spell immediately (no extra waits)
            if spell == 'Magic Reflection' and Journal.Search(ALREADY_IN_EFFECT_TEXT):
                debug_message('Magic Reflection already in effect. Skipping to next buff.', 44)
                continue

            # Wait and recheck (only occurs if not already-in-effect, or for other spells)
            Misc.Pause(per_spell_pause)
            if has_buff(buff_name):
                debug_message('{} buff applied.'.format(buff_name), 68)
            else:
                debug_message('Could not confirm {} buff.'.format(buff_name), 33)
        else:
            debug_message('{} already active.'.format(buff_name), 44)

if __name__ == '__main__':
    main()
