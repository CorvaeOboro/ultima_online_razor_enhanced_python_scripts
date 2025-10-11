"""
TRAIN Magery and Spiritspeak - a Razor Enhanced Python Script for Ultima Online

Training Magery and Spiritspeak skills by casting spells and meditating.
Mana Drain > Invisibility > Mana Vampire 
includes reagent checks, and includes mana regen like food management, and mana potions.

VERSION::20250925
"""
from collections import namedtuple

MEDITATION_COOLDOWN = 10000  # 10 seconds
SPIRIT_SPEAK_COOLDOWN = 2100  # 2.1 seconds
ADDITIONAL_SHARD_COOLDOWN = 500  # Extra delay 
REAGENT_CHECK_COOLDOWN = 30000  # Check reagents every 30 seconds
FOOD_CHECK_COOLDOWN = 60000  # Check food every 60 seconds
MANA_POTION_COOLDOWN = 100000  # Check mana potions every 100 seconds

DEBUG_MODE = True

# Create a namedtuple for spells
Spell = namedtuple('Spell', ['name', 'mana_cost', 'delay_ms', 'reagents'])

# Name , Mana Cost , Delay , Reagents
SPELLS = {
    'Mana Drain': Spell('Mana Drain', 6, 1500, ['Black Pearl', 'Mandrake Root', 'Spider Silk']),
    'Invisibility': Spell('Invisibility', 20, 1500, ['Bloodmoss', 'Nightshade']),
    'Mana Vampire': Spell('Mana Vampire', 40, 1750, ['Bloodmoss', 'Mandrake Root', 'Spider Silk'])
}

# Spell selection based on magery skill level
SKILL_SPELLS = {
    (0, 50.8): SPELLS['Mana Drain'],
    (50.8, 74.5): SPELLS['Invisibility'],
    (74.5, 120): SPELLS['Mana Vampire']
}

ITEM_IDS = {
    # Reagents
    'Black Pearl': 0x0F7A,
    'Bloodmoss': 0x0F7B,
    'Mandrake Root': 0x0F86,
    'Nightshade': 0x0F88,
    'Spider Silk': 0x0F8D,
    # Food
    'Fish Steak': 0x097A,
    'Ribs': 0x09F2,
    'Bird': 0x09B7,
    'Lamb': 0x160A,
    'Chicken': 0x09B7,
    # Mana Restore
    'Mana Potion': 0x0F0B,
    'Mana Fish Steak': 0x0F0B,
}

FOOD_ITEMS = ['Fish Steak', 'Ribs', 'Bird', 'Lamb', 'Chicken'] # Food priority (try these in order)
MANA_POTIONS = ['Mana Potion', 'Mana Fish Steak'] # Mana potion priority

class Colors:
    """ANSI color codes for messages"""
    RED = 33
    GREEN = 68
    YELLOW = 53

#//===========================================================

def debug_message(msg, color):
    if DEBUG_MODE:
        Misc.SendMessage(msg, color)

def find_item(item_names):
    """Find first available item from a list in backpack"""
    for name in item_names:
        item_id = ITEM_IDS.get(name)
        if not item_id:
            continue
        item = Items.FindByID(item_id, -1, Player.Backpack.Serial)
        if item:
            return item
    return None

def check_and_eat_food():
    """Check if we need food and eat if necessary"""
    if Timer.Check('food_timer'):
        return
        
    if Player.Hits >= Player.HitsMax:  # Already well fed
        Timer.Create('food_timer', FOOD_CHECK_COOLDOWN)
        return
        
    food = find_item(FOOD_ITEMS)
    if food:
        Items.UseItem(food)
        debug_message('Eating food to maintain mana regeneration', Colors.GREEN)
        Timer.Create('food_timer', FOOD_CHECK_COOLDOWN)
    else:
        debug_message('No food found in backpack!', Colors.YELLOW)

def use_mana_potion():
    """Use a mana potion if available and needed"""
    if Timer.Check('potion_timer'):
        return False
        
    if Player.Mana >= Player.ManaMax - 10:  # Don't waste potions
        return False
        
    potion = find_item(MANA_POTIONS)
    if potion:
        Items.UseItem(potion)
        debug_message('Using mana potion', Colors.GREEN)
        Timer.Create('potion_timer', MANA_POTION_COOLDOWN)
        return True
    return False

def get_reagent_count(reagent):
    """Get count of a specific reagent in backpack"""
    return Items.BackpackCount(ITEM_IDS.get(reagent, 0))

def check_reagents(spell, min_count=5):  
    """Check if we have enough reagents for the spell"""
    if not Timer.Check('reagent_check'):
        # Only check and report reagents periodically
        Timer.Create('reagent_check', REAGENT_CHECK_COOLDOWN)
        counts = {r: get_reagent_count(r) for r in spell.reagents}
        low_reagents = [f"{r}: {c}" for r, c in counts.items() if c < min_count + 10]
        
        if low_reagents:
            debug_message(f"Low on reagents: {', '.join(low_reagents)}", Colors.YELLOW)
            if any(get_reagent_count(r) <= min_count for r in spell.reagents):
                debug_message(f"Stopping at minimum reagent count ({min_count})", Colors.RED)
                return False
    
    # Check if we have more than minimum count for all reagents
    return all(get_reagent_count(reagent) > min_count for reagent in spell.reagents)

def get_current_spell():
    """Get appropriate spell based on current magery skill"""
    magery = Player.GetSkillValue('Magery')
    for (min_skill, max_skill), spell in SKILL_SPELLS.items():
        if min_skill <= magery < max_skill:
            return spell
    return SPELLS['Mana Drain']  # Default to lowest spell

def should_use_spirit_speak():
    """Check if we should use Spirit Speak"""
    spirit_speak = Player.GetSkillValue('Spirit Speak')
    if spirit_speak >= 100:
        return False
    
    # Check if the skill is currently active
    # "you feel you contacts with the netherworld fade" means we need to wait
    return not Journal.Search("netherworld fade")

def meditate_to_full(target_mana):
    """Meditate until we reach target mana"""
    while Player.Mana < target_mana:
        # Check food and potions
        check_and_eat_food()
        if use_mana_potion():
            Misc.Pause(500)  # Wait for potion effect
            continue
            
        # Try Spirit Speak while meditating if needed
        if not Timer.Check('spirit_speak') and should_use_spirit_speak():
            Player.UseSkill('Spirit Speak')
            Timer.Create('spirit_speak', SPIRIT_SPEAK_COOLDOWN)
            
        if not Player.BuffsExist('Meditation') and not Timer.Check('meditation'):
            Player.UseSkill('Meditation')
            Timer.Create('meditation', MEDITATION_COOLDOWN)
        Misc.Pause(100)

def cast_spell(spell):
    """Cast a spell and handle targeting"""
    Spells.CastMagery(spell.name)
    Timer.Create('magery', spell.delay_ms + ADDITIONAL_SHARD_COOLDOWN)
    Target.WaitForTarget(2000, True)
    Target.TargetExecute(Player.Serial) # target self

def train_skills():
    """Main training loop for both Magery and Spirit Speak"""
    debug_message('Starting Magery and Spirit Speak training...', Colors.GREEN)
    
    # Initialize timers
    Timer.Create('spirit_speak', 1)
    Timer.Create('magery', 1)
    Timer.Create('reagent_check', 1)
    Timer.Create('food_timer', 1)
    Timer.Create('potion_timer', 1)
    
    # Clear journal for spirit speak checks
    Journal.Clear()
    
    current_spell = get_current_spell()
    debug_message(f"Training with spell: {current_spell.name}", Colors.GREEN)
    
    while not Player.IsGhost:
        # Check food status
        check_and_eat_food()
        
        # Try Spirit Speak first (fast cooldown) if needed
        if not Timer.Check('spirit_speak') and should_use_spirit_speak():
            Player.UseSkill('Spirit Speak')
            Timer.Create('spirit_speak', SPIRIT_SPEAK_COOLDOWN)
        
        # Check Magery (slower cooldown)
        if not Timer.Check('magery'):
            if not check_reagents(current_spell):
                debug_message(f'Out of reagents for {current_spell.name}!', Colors.RED)
                debug_message(f'Needed: {", ".join(current_spell.reagents)}', Colors.RED)
                break
            
            if Player.Mana >= current_spell.mana_cost:
                cast_spell(current_spell)
                # Update spell selection after cast
                new_spell = get_current_spell()
                if new_spell != current_spell:
                    current_spell = new_spell
                    debug_message(f"Switching to spell: {current_spell.name}", Colors.GREEN)
            else:
                meditate_to_full(current_spell.mana_cost)
        
        # Short pause to prevent CPU spike
        Misc.Pause(100)

if __name__ == '__main__':
    train_skills()
