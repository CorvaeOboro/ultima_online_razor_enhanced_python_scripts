"""
SPELL SELF CURE + HEAL - A Razor Enhanced Python Script for Ultima Online

Healing and curing logic with explicit conditionals and thresholds:

- If poisoned:
    - Always cast Arch Cure first (if possible)
    - After a successful cure, if missing HP >= MEDIUM_HP_THRESHOLD (40), cast Greater Heal (unless mana is very low, then use Heal)
- If not poisoned:
    - If HP% at or below CRITICAL_HP_PERCENT (40%), cast Heal (fast emergency heal)
    - If HP% above CRITICAL_HP_PERCENT but not full:
        - If mana >= LOW_MANA_THRESHOLD (15), cast Greater Heal
        - If mana < LOW_MANA_THRESHOLD, cast Heal instead of Greater Heal (with warning)
    - If HP is full, do nothing
- Always warn if not enough mana for a spell, but still attempt to cast (to allow for mana cost reduction gear)

Threshold constants:
    CRITICAL_HP_PERCENT = 0.4   # 40% HP or less triggers Heal
    MEDIUM_HP_THRESHOLD = 40    # If missing HP >= 40 after cure, try Greater Heal
    GREATER_HEAL_MIN_MANA = 20  # Minimum mana for Greater Heal
    HEAL_MIN_MANA = 11          # Minimum mana for Heal
    LOW_MANA_THRESHOLD = 15     # If below this, use Heal instead of Greater Heal

TODO:
If not poisoned and not missing health, then try to heal nearby based on a global parameter boolean HEAL_OTHERS

HOTKEY:: E
VERSION::20250713
"""

DEBUG_MODE = False  # Set to False to suppress debug message output
# Spell Names
SPELL_ARCH_CURE = "Arch Cure"
SPELL_HEAL = "Heal"
SPELL_GREATER_HEAL = "Greater Heal"

# Thresholds
CRITICAL_HP_PERCENT = 0.4           # If HP% at or below this, use fast Heal (e.g., 0.4 = 40%)
MEDIUM_HP_THRESHOLD = 40            # If missing HP >= this after cure, use Greater Heal
GREATER_HEAL_MIN_MISSING_HP = 30    # (Legacy, not used in percent logic)
GREATER_HEAL_MIN_MANA = 20          # Minimum mana for Greater Heal
HEAL_MIN_MANA = 11                  # Minimum mana for Heal
LOW_MANA_THRESHOLD = 19             # If below this, use Heal instead of Greater Heal

#//============================================================
def is_poisoned():
    return Player.Poisoned

def missing_health():
    return Player.HitsMax - Player.Hits

def can_cast(spell, mana_cost):
    return Player.Mana >= mana_cost


def debug_message(msg, color=68):
    if DEBUG_MODE:
        Misc.SendMessage(f"[CUREHEAL] {msg}", color)


def cast_spell(spell):
    debug_message(f"Casting: {spell}", 68)
    Spells.Cast(spell)
    # Wait for target cursor (up to 2 seconds)
    if Target.WaitForTarget(2000):
        Target.Self()
        debug_message("Targeted self.", 68)
    else:
        debug_message("No target cursor appeared!", 33)
    Misc.Pause(600)  # Wait for cast

def main():
    # 1. Always cure poison first if poisoned
    if is_poisoned():
        if can_cast(SPELL_ARCH_CURE, 11):
            was_poisoned = Player.Poisoned
            cast_spell(SPELL_ARCH_CURE)
            Misc.Pause(200)  # Give time for status update
            if was_poisoned and not Player.Poisoned:
                debug_message("Successfully cured poison with Arch Cure.", 68)
                hp_missing = missing_health()
                # If HP still missing above medium, cast Greater Heal
                if hp_missing >= MEDIUM_HP_THRESHOLD:
                    if Player.Mana < LOW_MANA_THRESHOLD:
                        debug_message(f"Mana critically low ({Player.Mana}), using Heal instead of Greater Heal after cure.", 33)
                        cast_spell(SPELL_HEAL)
                    else:
                        if can_cast(SPELL_GREATER_HEAL, GREATER_HEAL_MIN_MANA):
                            debug_message(f"After cure, HP missing {hp_missing}, casting Greater Heal.")
                        else:
                            debug_message(f"Not enough mana for Greater Heal after cure, trying anyway in case of mana reduction.", 33)
                        cast_spell(SPELL_GREATER_HEAL)
            return
        else:
            debug_message("Not enough mana for Arch Cure!", 33)
            return
    # 2. Only heal if not poisoned
    hp_missing = missing_health()
    hp_percent = Player.Hits / float(Player.HitsMax) if Player.HitsMax > 0 else 1.0
    if hp_percent <= CRITICAL_HP_PERCENT and hp_missing > 0:
        if can_cast(SPELL_HEAL, HEAL_MIN_MANA):
            debug_message(f"Critical HP ({Player.Hits}/{Player.HitsMax}, {int(hp_percent*100)}%), casting fast Heal.")
        else:
            debug_message(f"Not enough mana for Heal, trying anyway in case of mana reduction.", 33)
        cast_spell(SPELL_HEAL)
    elif hp_percent > CRITICAL_HP_PERCENT and hp_percent < 1.0:
        if Player.Mana < LOW_MANA_THRESHOLD:
            debug_message(f"Mana critically low ({Player.Mana}), using Heal instead of Greater Heal.", 33)
            cast_spell(SPELL_HEAL)
        else:
            if can_cast(SPELL_GREATER_HEAL, GREATER_HEAL_MIN_MANA):
                debug_message(f"HP above critical ({Player.Hits}/{Player.HitsMax}, {int(hp_percent*100)}%), casting Greater Heal.")
            else:
                debug_message(f"Not enough mana for Greater Heal, trying anyway in case of mana reduction.", 33)
            cast_spell(SPELL_GREATER_HEAL)
    else:
        debug_message("No healing needed or not enough mana.", 33)

if __name__ == '__main__':
    main()
