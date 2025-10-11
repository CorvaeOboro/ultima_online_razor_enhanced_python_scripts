"""
SPELL Death Self - a Razor Enhanced Python script for Ultima Online

Casts a sequence of offensive spells targeting self , making a dramatic exit
Curse > Poison > Energy Bolt > Flamestrike > Lightning > Explosion > Explosion > Explosion

VERSION::20250904
"""

DEBUG_MODE = False  # Set to True for detailed debug output

# Optional dialog and emote configuration
ENABLE_DIALOG = True         # Set to True to enable dialog
ENABLE_EMOTES = True         # Set to True to enable emote commands

# Spell sequence for death
SPELL_SEQUENCE = ["Curse", "Poison", "Energy Bolt", "Flamestrike", "Lightning", "Explosion", "Explosion", "Explosion"]

# Dialog messages for each phase
RITUAL_DEATH_DIALOG = {
    "start": "there is one last thing ...",
    "Energy Bolt": "ㄱㄴ XEN CORP AN LOR メフ",
    "Explosion": "fare well",
}

RITUAL_DEATH_EMOTES = {
    "Flamestrike": "[emote giggle",
}

# Timing configuration (milliseconds)
CAST_DELAY_BASE = 800        # Base delay after each spell cast
CAST_DELAY_CURSE = 1000       # Curse cast delay
CAST_DELAY_POISON = 800      # Poison cast delay  
CAST_DELAY_EXPLOSION = 1000   # Explosion cast delay 
CAST_DELAY_FLAMESTRIKE = 1000 # Flamestrike cast delay (longest)
CAST_DELAY_LIGHTNING = 800   # Lightning bolt cast delay
WAITFORTARGET_MAX = 5000     # Maximum wait for target cursor
DIALOG_DELAY = 1200          # Delay after dialog messages (ms)

# Poison tick timing configuration
# poison is useful to cast on self to prevent healign , however we must avoid getting interrupted
POISON_TICK_INTERVAL = 5000  # Poison damage occurs every 5 seconds
POISON_SAFETY_BUFFER = 1500  # Buffer time before/after poison tick (ms)
POST_POISON_DELAY = 1500     # Extra delay after casting poison to sync timing

# Spell definitions with mana costs and reagent requirements
MAGERY_SPELLS = {
    "Curse": {
        "mana": 11,
        "reagents": {
            0xF88: 1,  # Nightshade
            0xF8C: 1   # Sulfurous Ash
        },
        "delay": CAST_DELAY_CURSE
    },
    "Poison": {
        "mana": 9,
        "reagents": {
            0xF88: 1   # Nightshade
        },
        "delay": CAST_DELAY_POISON
    },
    "Explosion": {
        "mana": 20,
        "reagents": {
            0xF7A: 1,  # Black Pearl
            0xF86: 1,  # Mandrake Root
            0xF8C: 1   # Sulfurous Ash
        },
        "delay": CAST_DELAY_EXPLOSION
    },
    "Flamestrike": {
        "mana": 40,
        "reagents": {
            0xF7A: 1,  # Black Pearl
            0xF85: 1,  # Ginseng
            0xF86: 1,  # Mandrake Root
            0xF8C: 1   # Sulfurous Ash
        },
        "delay": CAST_DELAY_FLAMESTRIKE
    },
    "Lightning": {
        "mana": 15,
        "reagents": {
            0xF7A: 1,  # Black Pearl
            0xF8C: 1   # Sulfurous Ash
        },
        "delay": CAST_DELAY_LIGHTNING
    },
    "Energy Bolt": {
        "mana": 20,
        "reagents": {
            0xF7A: 1,  # Black Pearl
            0xF88: 1   # Nightshade
        },
        "delay": CAST_DELAY_BASE
    }
}

#//===============  Utility Functions =======================

# Global variables to track poison timing and dialog history
poison_start_time = None
dialog_said = set()  # Track which dialog messages have been said

def get_current_time_ms():
    """Get current time in milliseconds."""
    import time
    return int(time.time() * 1000)

def debug_message(msg, color=68):
    """Send debug message if DEBUG_MODE is enabled."""
    if DEBUG_MODE:
        Misc.SendMessage(f"[DEATH_SELF] {msg}", color)

def say_dialog(message):
    """Say dialog message in-game if enabled."""
    if not ENABLE_DIALOG:
        return
    try:
        if hasattr(Player, 'ChatSay'):
            Player.ChatSay(message)
            debug_message(f"Dialog: {message}")
        else:
            debug_message(f"Dialog (fallback): {message}")
        Misc.Pause(DIALOG_DELAY)
    except Exception as e:
        debug_message(f"Error saying dialog: {str(e)}", 33)

def say_emote(emote_command):
    """Execute emote command in-game if enabled."""
    if not ENABLE_EMOTES:
        return
    try:
        if hasattr(Player, 'ChatSay'):
            Player.ChatSay(emote_command)
            debug_message(f"Emote: {emote_command}")
        else:
            debug_message(f"Emote (fallback): {emote_command}")
        Misc.Pause(600)  # Brief pause after emote
    except Exception as e:
        debug_message(f"Error executing emote: {str(e)}", 33)

def calculate_next_poison_tick(poison_time):
    """Calculate when the next poison tick will occur."""
    if poison_time is None:
        return None
    
    current_time = get_current_time_ms()
    elapsed = current_time - poison_time
    
    # Calculate how many ticks have passed
    ticks_passed = elapsed // POISON_TICK_INTERVAL
    
    # Calculate when the next tick will occur
    next_tick_time = poison_time + ((ticks_passed + 1) * POISON_TICK_INTERVAL)
    
    return next_tick_time

def is_safe_to_cast(spell_name):
    """Check if it's safe to cast a spell without poison interruption."""
    global poison_start_time
    
    if poison_start_time is None:
        return True  # No poison active, safe to cast
    
    current_time = get_current_time_ms()
    next_tick = calculate_next_poison_tick(poison_start_time)
    
    if next_tick is None:
        return True
    
    time_until_tick = next_tick - current_time
    spell_delay = MAGERY_SPELLS.get(spell_name, {}).get('delay', CAST_DELAY_BASE)
    
    # Check if we have enough time to cast before the next tick
    # Add buffer time to be safe
    safe_window = spell_delay + POISON_SAFETY_BUFFER
    
    is_safe = time_until_tick > safe_window or time_until_tick < -POISON_SAFETY_BUFFER
    
    debug_message(f"Poison safety check for {spell_name}: next tick in {time_until_tick}ms, need {safe_window}ms - {'SAFE' if is_safe else 'WAIT'}")
    
    return is_safe

def wait_for_safe_cast_window(spell_name):
    """Wait until it's safe to cast a spell without poison interruption."""
    global poison_start_time
    
    if poison_start_time is None:
        return  # No poison active
    
    max_wait_attempts = 10
    attempt = 0
    
    while not is_safe_to_cast(spell_name) and attempt < max_wait_attempts:
        current_time = get_current_time_ms()
        next_tick = calculate_next_poison_tick(poison_start_time)
        
        if next_tick:
            time_until_tick = next_tick - current_time
            
            if time_until_tick > 0 and time_until_tick < POISON_SAFETY_BUFFER:
                # Wait for the tick to pass, then add buffer
                wait_time = time_until_tick + POISON_SAFETY_BUFFER
                debug_message(f"Waiting {wait_time}ms for poison tick to pass before casting {spell_name}")
                Misc.Pause(int(wait_time))
        
        attempt += 1
    
    if attempt >= max_wait_attempts:
        debug_message(f"Max wait attempts reached for {spell_name}, proceeding anyway", 33)

def has_enough_mana(spell_name):
    """Check if player has enough mana for the spell."""
    spell = MAGERY_SPELLS.get(spell_name, {})
    mana_needed = spell.get('mana', 0)
    has_mana = Player.Mana >= mana_needed
    debug_message(f"Mana check for {spell_name}: need {mana_needed}, have {Player.Mana} - {'OK' if has_mana else 'INSUFFICIENT'}")
    return has_mana

def has_enough_reagents(spell_name):
    """Check if player has enough reagents for the spell."""
    spell = MAGERY_SPELLS.get(spell_name, {})
    reagents = spell.get('reagents', {})
    
    for reagent_id, qty_needed in reagents.items():
        qty_have = Items.BackpackCount(reagent_id)
        if qty_have < qty_needed:
            debug_message(f"Reagent check for {spell_name}: need {qty_needed} of 0x{reagent_id:X}, have {qty_have} - INSUFFICIENT", 33)
            return False
    
    debug_message(f"Reagent check for {spell_name}: OK")
    return True

def can_cast_spell(spell_name):
    """Check if spell can be cast (reagents only, ignore mana)."""
    return has_enough_reagents(spell_name)

def cast_spell_on_self(spell_name):
    """Cast the specified spell on self with error handling."""
    global poison_start_time
    
    debug_message(f"=== CASTING {spell_name.upper()} ===", 68)
    
    # Wait for safe casting window if poison is active
    if poison_start_time is not None:
        wait_for_safe_cast_window(spell_name)
    
    try:
        # Cast the spell
        Spells.Cast(spell_name)
        debug_message(f"Spell {spell_name} initiated")
        
        # Wait for target cursor
        if Target.WaitForTarget(WAITFORTARGET_MAX):
            Target.Self()
            debug_message(f"Targeted self for {spell_name}")
        else:
            debug_message(f"No target cursor appeared for {spell_name}!", 33)
        
        # Apply spell-specific delay
        spell_delay = MAGERY_SPELLS.get(spell_name, {}).get('delay', CAST_DELAY_BASE)
        Misc.Pause(spell_delay)
        
        # Special handling for poison spell
        if spell_name == "Poison":
            poison_start_time = get_current_time_ms()
            debug_message(f"Poison cast successful - tracking started at {poison_start_time}")
            debug_message(f"Adding post-poison delay of {POST_POISON_DELAY}ms to sync timing")
            Misc.Pause(POST_POISON_DELAY)
        
        debug_message(f"Completed {spell_name} (waited {spell_delay}ms)")
        
    except Exception as e:
        debug_message(f"Error casting {spell_name}: {str(e)}", 33)

def display_spell_requirements():
    """Display total mana and reagent requirements for the death sequence."""
    if not DEBUG_MODE:
        return
        
    total_mana = sum(MAGERY_SPELLS[spell]['mana'] for spell in SPELL_SEQUENCE)
    debug_message(f"=== DEATH SEQUENCE REQUIREMENTS ===")
    debug_message(f"Total mana needed: {total_mana}")
    debug_message(f"Current mana: {Player.Mana}")
    
    # Aggregate reagent requirements
    reagent_totals = {}
    for spell in SPELL_SEQUENCE:
        reagents = MAGERY_SPELLS[spell].get('reagents', {})
        for reagent_id, qty in reagents.items():
            reagent_totals[reagent_id] = reagent_totals.get(reagent_id, 0) + qty
    
    debug_message("Reagent requirements:")
    reagent_names = {
        0xF7A: "Black Pearl",
        0xF85: "Ginseng", 
        0xF86: "Mandrake Root",
        0xF88: "Nightshade",
        0xF8C: "Sulfurous Ash"
    }
    
    for reagent_id, qty_needed in reagent_totals.items():
        qty_have = Items.BackpackCount(reagent_id)
        name = reagent_names.get(reagent_id, f"0x{reagent_id:X}")
        status = "OK" if qty_have >= qty_needed else "INSUFFICIENT"
        debug_message(f"  {name}: need {qty_needed}, have {qty_have} - {status}")

def execute_death_sequence():
    """Execute the complete death spell sequence with dialog and emotes."""
    global dialog_said
    
    debug_message("=== BEGINNING DEATH SEQUENCE ===", 68)
    
    # Opening dialog and emote 
    try:
        if "start" in RITUAL_DEATH_DIALOG and "start" not in dialog_said:
            say_dialog(RITUAL_DEATH_DIALOG["start"])
            dialog_said.add("start")
    except KeyError:
        debug_message("No start dialog defined", 33)
    
    try:
        if "start" in RITUAL_DEATH_EMOTES:
            say_emote(RITUAL_DEATH_EMOTES["start"])
    except KeyError:
        debug_message("No start emote defined", 33)
    
    successful_casts = 0
    failed_casts = 0
    
    for i, spell_name in enumerate(SPELL_SEQUENCE, 1):
        debug_message(f"--- Step {i} of {len(SPELL_SEQUENCE)}: {spell_name} ---")
        
        # Pre-spell dialog for certain phases (only say once per spell type)
        if spell_name in RITUAL_DEATH_DIALOG and spell_name not in dialog_said:
            say_dialog(RITUAL_DEATH_DIALOG[spell_name])
            dialog_said.add(spell_name)
        
        if can_cast_spell(spell_name):
            cast_spell_on_self(spell_name)
            successful_casts += 1
            debug_message(f"{spell_name} cast successfully", 68)
            
            # Post-spell emotes 
            if spell_name in RITUAL_DEATH_EMOTES:
                say_emote(RITUAL_DEATH_EMOTES[spell_name])
        else:
            debug_message(f"Cannot cast {spell_name} - insufficient resources", 33)
            failed_casts += 1
            # Still pause briefly 
            Misc.Pause(400)
    
    # Closing dialog and emote 
    try:
        if "end" in RITUAL_DEATH_DIALOG and "end" not in dialog_said:
            say_dialog(RITUAL_DEATH_DIALOG["end"])
            dialog_said.add("end")
    except KeyError:
        debug_message("No end dialog defined", 33)
    
    try:
        if "end" in RITUAL_DEATH_EMOTES:
            say_emote(RITUAL_DEATH_EMOTES["end"])
    except KeyError:
        debug_message("No end emote defined", 33)
    
    debug_message(f"=== DEATH SEQUENCE COMPLETE ===", 68)
    debug_message(f"Successful casts: {successful_casts}")
    debug_message(f"Failed casts: {failed_casts}")

#//===============  Main Execution =======================

def main():
    """Main function to execute the death spell sequence."""
    debug_message("=== SPELL DEATH SELF STARTED ===", 68)
    
    # Display requirements if in debug mode
    display_spell_requirements()
    
    # Execute the death sequence
    execute_death_sequence()
    
    debug_message("=== SPELL DEATH SELF COMPLETED ===", 68)

if __name__ == '__main__':
    main()