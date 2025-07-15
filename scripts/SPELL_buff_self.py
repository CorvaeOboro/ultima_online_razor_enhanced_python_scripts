"""
 SPELL buff self - a Razor Enhanced Python Script for Ultima Online
 
 Casts Magic Reflection, Arch Protection, and Bless on self if not already active
 Buff order: Magic Reflection -> Arch Protection -> Bless

HOTKEY:: T
VERSION::20250713
"""

DEBUG_MODE = True
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

# Helper: Check if buff is active (case-insensitive)
def has_buff(buff_name):
    try:
        for i in range(Buffs.GetBuffCount()):
            name = Buffs.GetBuffName(i)
            if name and buff_name.lower() in name.lower():
                return True
        return False
    except Exception as e:
        Misc.SendMessage('Error checking buff: {}'.format(e), 33)
        return False

# Helper: Cast spell by name
def cast_spell(spell_name):
    try:
        Spells.Cast(spell_name)
        Misc.Pause(CAST_PAUSE)
    except Exception as e:
        Misc.SendMessage('Error casting {}: {}'.format(spell_name, e), 33)

# Main logic: Cast buffs in order if not present
def main():
    for idx, (buff, spell) in enumerate(zip([b[0] for b in BUFFS], SPELLS)):
        if not has_buff(buff):
            Misc.SendMessage('Casting {}...'.format(spell), 68)
            cast_spell(spell)
            # Wait and recheck
            Misc.Pause(CAST_PAUSE)
            if has_buff(buff):
                Misc.SendMessage('{} buff applied.'.format(buff), 68)
            else:
                Misc.SendMessage('Could not confirm {} buff.'.format(buff), 33)
        else:
            Misc.SendMessage('{} already active.'.format(buff), 44)

if __name__ == '__main__':
    main()
