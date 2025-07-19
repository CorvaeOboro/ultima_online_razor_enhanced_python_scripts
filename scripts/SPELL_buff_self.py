"""
 SPELL buff self - a Razor Enhanced Python Script for Ultima Online
 
 Casts Magic Reflection, Arch Protection, and Bless on self
 checks buffs if server allows , if not already active
 Buff order: Magic Reflection -> Arch Protection -> Bless

HOTKEY:: T
VERSION::20250718
"""

DEBUG_MODE = False

# CONFIGURABLE: Pause between casts (ms)
CAST_PAUSE = 600

# Buff names as they appear in Razor Enhanced (case-insensitive)
BUFFS = [
    ('Magic Reflection', 'Magic Reflection'),
    ('Arch Protection', 'Arch Protection'),
    ('Bless', 'Bless')
]

# Corresponding spell names for casting
SPELLS = [
    'Magic Reflection',
    'Arch Protection',
    'Bless'
]

def debug_message(msg, color=68):
    if DEBUG_MODE:
        Misc.SendMessage(f'[BuffSelf] {msg}', color)

# Helper: Check if buff is active (case-insensitive)
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

# Helper: Cast spell by name and target self if needed
def cast_spell(spell_name):
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
        Misc.Pause(CAST_PAUSE)
    except Exception as e:
       debug_message('Error casting {}: {}'.format(spell_name, e), 33)

# Main logic: Cast buffs in order if not present
def main():
    for idx, (buff, spell) in enumerate(zip([b[0] for b in BUFFS], SPELLS)):
        if not has_buff(buff):
            debug_message('Casting {}...'.format(spell), 68)
            cast_spell(spell)
            # Wait and recheck
            Misc.Pause(CAST_PAUSE)
            if has_buff(buff):
                debug_message('{} buff applied.'.format(buff), 68)
            else:
                debug_message('Could not confirm {} buff.'.format(buff), 33)
        else:
            debug_message('{} already active.'.format(buff), 44)

if __name__ == '__main__':
    main()
