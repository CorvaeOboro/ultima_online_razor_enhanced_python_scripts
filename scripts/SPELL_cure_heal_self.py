"""
SPELL cure and heal self - a Razor Enhanced Python Script for Ultima Online

heal self , cure if poisoned , when low on health prioritize small fast heal , greater heals when above 40% 

- If poisoned:
    - Always cast Arch Cure first (if possible)
    - After a successful cure, if missing HP >= MEDIUM_HP_THRESHOLD (40), cast Greater Heal (unless mana is very low, then use Heal)
- If not poisoned:
    - If HP% at or below CRITICAL_HP_PERCENT (40%), cast Heal (fast emergency heal)
    - If HP% above CRITICAL_HP_PERCENT but not full:
        - If mana >= LOW_MANA_THRESHOLD (15), cast Greater Heal
        - If mana < LOW_MANA_THRESHOLD, cast Heal instead of Greater Heal (with warning)
warn if not enough mana for a spell, tho still attempt to cast ( to allow for mana cost reduction gear )

TODO: maybe get nearby humanoids ,  use the blue noteriety to heal others , dont heal monsters , dont heal criminals 

HOTKEY:: E
VERSION::20250924
"""

DEBUG_MODE = False  # Set to False to suppress debug message output
HEAL_OTHERS = True   # Set to True to enable healing others
HEAL_OTHERS_RANGE = 5  # Range to search for injured innocent players

# Emergency mana threshold - use restoratives if mana drops below this
EMERGENCY_MANA_THRESHOLD = 10

# Thresholds
CRITICAL_HP_PERCENT = 0.4           # If HP% at or below this, use fast Heal (e.g., 0.4 = 40%)
MEDIUM_HP_THRESHOLD = 40            # If missing HP >= this after cure, use Greater Heal
GREATER_HEAL_MIN_MISSING_HP = 30    # (Legacy, not used in percent logic)
GREATER_HEAL_MIN_MANA = 20          # Minimum mana for Greater Heal
HEAL_MIN_MANA = 11                  # Minimum mana for Heal
LOW_MANA_THRESHOLD = 20             # If below this, use Heal instead of Greater Heal

WAITFORTARGET_MAX = 10000 # 2000 works however consider lag or world save 

# Spell Names
SPELL_CURE = "Cure"
SPELL_ARCH_CURE = "Arch Cure"
SPELL_HEAL = "Heal"
SPELL_GREATER_HEAL = "Greater Heal"

# Spell definitions: mana cost and reagent requirements
SPELLS = {
    "Cure": {
        "mana": 6,
        "reagents": {"Garlic": 1, "Ginseng": 1}
    },
    "Arch Cure": {
        "mana": 11,
        "reagents": {"Garlic": 1, "Ginseng": 1, "Mandrake Root": 1}
    },
    "Heal": {
        "mana": 11,
        "reagents": {"Ginseng": 1, "Garlic": 1, "Spider's Silk": 1}
    },
    "Greater Heal": {
        "mana": 20,
        "reagents": {"Ginseng": 1, "Garlic": 1, "Spider's Silk": 1, "Mandrake Root": 1}
    }
}

# Mana Restorative Items for Emergency Use
MANA_RESTORATIVES = {
    "Greater Mana Potion": 0x0F0D      # Greater Mana Potion
}

#//===============  Player Status Functions =======================
def is_poisoned():
    poisoned = Player.Poisoned
    debug_message(f"Player poisoned status: {poisoned}")
    return poisoned

def missing_health():
    missing = Player.HitsMax - Player.Hits
    debug_message(f"Player missing health: {missing} (Current: {Player.Hits}/{Player.HitsMax})")
    return missing

def get_health_percent():
    percent = Player.Hits / float(Player.HitsMax) if Player.HitsMax > 0 else 1.0
    debug_message(f"Player health percent: {int(percent*100)}%")
    return percent

def can_cast(spell, mana_cost):
    can_cast_spell = Player.Mana >= mana_cost
    debug_message(f"Can cast {spell} (cost: {mana_cost}): {can_cast_spell} (Current mana: {Player.Mana})")
    return can_cast_spell


def debug_message(msg, color=68):
    if DEBUG_MODE:
        Misc.SendMessage(f"[SPELL_CUREHEAL] {msg}", color)


def cast_spell_on_self(spell):
    debug_message(f"Casting: {spell} on self", 68)
    Spells.Cast(spell)
    # Wait for target cursor (up to 2 seconds)
    if Target.WaitForTarget(WAITFORTARGET_MAX):
        Target.Self()
        debug_message("Targeted self.", 68)
    else:
        debug_message("No target cursor appeared!", 33)
    Misc.Pause(600)  # Wait for cast

def cast_spell_on_target(spell, target):
    debug_message(f"Casting: {spell} on target {target.Serial}", 68)
    Spells.Cast(spell)
    # Wait for target cursor (up to 2 seconds)
    if Target.WaitForTarget(WAITFORTARGET_MAX):
        Target.TargetExecute(target)
        debug_message(f"Targeted player: {target.Name}", 68)
    else:
        debug_message("No target cursor appeared!", 33)
    Misc.Pause(600)  # Wait for cast

#//===============  Core Healing Logic Functions =======================
def handle_poison_cure():
    """Handle poison curing logic."""
    debug_message("=== POISON CURE PHASE ===")
    
    if not can_cast(SPELL_ARCH_CURE, 11):
        debug_message("Not enough mana for Arch Cure!", 33)
        return False
    
    was_poisoned = Player.Poisoned
    cast_spell_on_self(SPELL_ARCH_CURE)
    Misc.Pause(200)  # Give time for status update
    
    if was_poisoned and not Player.Poisoned:
        debug_message("Successfully cured poison with Arch Cure.", 68)
        return True
    return False

def handle_post_cure_healing():
    """Handle healing after successful poison cure."""
    debug_message("=== POST-CURE HEALING PHASE ===")
    
    hp_missing = missing_health()
    if hp_missing >= MEDIUM_HP_THRESHOLD:
        if Player.Mana < LOW_MANA_THRESHOLD:
            debug_message(f"Mana critically low ({Player.Mana}), using Heal instead of Greater Heal after cure.", 33)
            cast_spell_on_self(SPELL_HEAL)
        else:
            if can_cast(SPELL_GREATER_HEAL, GREATER_HEAL_MIN_MANA):
                debug_message(f"After cure, HP missing {hp_missing}, casting Greater Heal.")
            else:
                debug_message(f"Not enough mana for Greater Heal after cure, trying anyway in case of mana reduction.", 33)
            cast_spell_on_self(SPELL_GREATER_HEAL)

def handle_critical_healing():
    """Handle critical health situations."""
    debug_message("=== CRITICAL HEALING PHASE ===")
    
    if can_cast(SPELL_HEAL, HEAL_MIN_MANA):
        hp_percent = get_health_percent()
        debug_message(f"Critical HP ({Player.Hits}/{Player.HitsMax}, {int(hp_percent*100)}%), casting fast Heal.")
    else:
        debug_message(f"Not enough mana for Heal, trying anyway in case of mana reduction.", 33)
    cast_spell_on_self(SPELL_HEAL)

def handle_normal_healing():
    """Handle normal health situations."""
    debug_message("=== NORMAL HEALING PHASE ===")
    
    if Player.Mana < LOW_MANA_THRESHOLD:
        debug_message(f"Mana critically low ({Player.Mana}), using Heal instead of Greater Heal.", 33)
        cast_spell_on_self(SPELL_HEAL)
    else:
        if can_cast(SPELL_GREATER_HEAL, GREATER_HEAL_MIN_MANA):
            hp_percent = get_health_percent()
            debug_message(f"HP above critical ({Player.Hits}/{Player.HitsMax}, {int(hp_percent*100)}%), casting Greater Heal.")
        else:
            debug_message(f"Not enough mana for Greater Heal, trying anyway in case of mana reduction.", 33)
        cast_spell_on_self(SPELL_GREATER_HEAL)

def find_injured_innocents():
    """Find nearby innocent players who need healing."""
    debug_message("=== SEARCHING FOR INJURED INNOCENTS ===")
    
    injured_players = []
    # Retrieve nearby mobiles safely; avoid calling FindBySerial() without args
    try:
        mobiles = Mobiles.GetMobilesInRange(int(HEAL_OTHERS_RANGE))
    except Exception:
        try:
            flt = Mobiles.Filter()
            flt.Enabled = True
            flt.RangeMax = int(HEAL_OTHERS_RANGE)
            mobiles = Mobiles.ApplyFilter(flt)
        except Exception:
            mobiles = []
    
    for mobile in mobiles:
        if (mobile.Serial != Player.Serial and  # Not self
            mobile.Notoriety == 1 and           # Innocent (blue)
            mobile.Body in [0x0190, 0x0191] and # Human body types
            mobile.Hits < mobile.HitsMax and    # Missing health
            Player.DistanceTo(mobile) <= int(HEAL_OTHERS_RANGE)):
            
            injured_players.append(mobile)
            debug_message(f"Found injured innocent: {mobile.Name} ({mobile.Hits}/{mobile.HitsMax}) at distance {Player.DistanceTo(mobile)}")
    
    debug_message(f"Found {len(injured_players)} injured innocent players")
    return injured_players

def heal_others():
    """Heal nearby innocent players if enabled."""
    if not HEAL_OTHERS:
        return
    
    debug_message("=== HEAL OTHERS PHASE ===")
    
    injured_players = find_injured_innocents()
    if not injured_players:
        debug_message("No injured innocent players found nearby")
        return
    
    # Sort by most injured (lowest health percentage)
    injured_players.sort(key=lambda p: p.Hits / float(p.HitsMax) if p.HitsMax > 0 else 1.0)
    
    for player in injured_players:
        if Player.Mana < HEAL_MIN_MANA:
            debug_message(f"Not enough mana to heal others (Current: {Player.Mana})")
            break
        
        missing_hp = player.HitsMax - player.Hits
        hp_percent = player.Hits / float(player.HitsMax) if player.HitsMax > 0 else 1.0
        
        # Choose appropriate heal spell based on target's condition and our mana
        if hp_percent <= CRITICAL_HP_PERCENT or Player.Mana < GREATER_HEAL_MIN_MANA:
            if can_cast(SPELL_HEAL, HEAL_MIN_MANA):
                debug_message(f"Healing {player.Name} with Heal (HP: {int(hp_percent*100)}%)")
                cast_spell_on_target(SPELL_HEAL, player)
            else:
                debug_message(f"Not enough mana to heal {player.Name}")
                break
        else:
            if can_cast(SPELL_GREATER_HEAL, GREATER_HEAL_MIN_MANA):
                debug_message(f"Healing {player.Name} with Greater Heal (HP: {int(hp_percent*100)}%)")
                cast_spell_on_target(SPELL_GREATER_HEAL, player)
            else:
                debug_message(f"Not enough mana for Greater Heal on {player.Name}, using Heal instead")
                cast_spell_on_target(SPELL_HEAL, player)
        
        # Only heal one player per script execution to avoid spam
        break

def main():
    debug_message("=== SPELL CURE HEAL SELF STARTED ===")
    
    # 1. Always cure poison first if poisoned
    if is_poisoned():
        if handle_poison_cure():
            handle_post_cure_healing()
        return
    
    # 2. Handle self healing if not poisoned
    hp_missing = missing_health()
    hp_percent = get_health_percent()
    
    if hp_missing > 0:
        if hp_percent <= CRITICAL_HP_PERCENT:
            handle_critical_healing()
        else:
            handle_normal_healing()
    else:
        debug_message("Player at full health")
        # 3. If not poisoned and not missing health, try to heal others
        heal_others()
    
    debug_message("=== SPELL CURE HEAL SELF COMPLETED ===")

if __name__ == '__main__':
    main()
