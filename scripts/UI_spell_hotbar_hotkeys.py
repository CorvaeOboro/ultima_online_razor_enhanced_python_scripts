"""
UI Spell Hotbar Hotkeys - a Razor Enhanced Python Script for Ultima Online

Creates a gump of spell icons, a modern hotbar with cooldown and hotkey symbols.
This is a copy of the example spell hotbar in the razor enhanced docs with some modifications.

STATUS:: working
VERSION::20251015
"""
from System.Collections.Generic import List
from System import Byte
DEBUG_MODE = True

# Hotbar spell order - customize which spells appear and in what order, reference SPELL_CATALOG below for full list
HOTBAR_SPELLS = [
    'Energy Bolt',
    'Invisibility',
    'Greater Heal',
    'Water Elemental',
    'Poison',
    'Magic Trap',
    'Teleport',
    'Cure',
    'Arch Cure'
]

# Hotkey labels for each spell button position
HOTKEY_LABELS = {
    1: 'Q',
    2: 'W',
    3: 'E',
    4: 'R',
    5: 'S',
    6: 'D',
    7: 'F',
    8: 'G',
    9: 'H',
    10: '0'
}

# Global flag and position
HOTBAR_ACTIVE = True
HOTBAR_X = 600
HOTBAR_Y = 600

# GUMP ID LIMIT = 0xFFFFFFF = 4294967295 # max int , make sure gump ids are under this but high so unique 
GUMP_ID = 4123467115

# Assumed dimensions for each spell button
BUTTON_WIDTH = 44
BUTTON_HEIGHT = 44

# ===== SPELL DEFINITIONS =====

# Complete spell catalog with icon IDs, circle, and classification
# Classifications: 'attack' (offensive/damage), 'defend' (protection/healing), 'utility' (other)
SPELL_CATALOG = {
    # Circle 1
    'Clumsy': {'icon_id': 2190, 'circle': 1, 'type': 'attack'},
    'Create Food': {'icon_id': 2241, 'circle': 1, 'type': 'utility'},
    'Feeblemind': {'icon_id': 2242, 'circle': 1, 'type': 'attack'},
    'Heal': {'icon_id': 2243, 'circle': 1, 'type': 'defend'},
    'Magic Arrow': {'icon_id': 2244, 'circle': 1, 'type': 'attack'},
    'Night Sight': {'icon_id': 2245, 'circle': 1, 'type': 'utility'},
    'Reactive Armor': {'icon_id': 2246, 'circle': 1, 'type': 'defend'},
    'Weaken': {'icon_id': 2247, 'circle': 1, 'type': 'attack'},
    
    # Circle 2
    'Agility': {'icon_id': 2248, 'circle': 2, 'type': 'defend'},
    'Cunning': {'icon_id': 2249, 'circle': 2, 'type': 'defend'},
    'Cure': {'icon_id': 2250, 'circle': 2, 'type': 'defend'},
    'Harm': {'icon_id': 2251, 'circle': 2, 'type': 'attack'},
    'Magic Trap': {'icon_id': 2252, 'circle': 2, 'type': 'utility'},
    'Magic Untrap': {'icon_id': 2253, 'circle': 2, 'type': 'utility'},
    'Protection': {'icon_id': 2254, 'circle': 2, 'type': 'defend'},
    'Strength': {'icon_id': 2255, 'circle': 2, 'type': 'defend'},
    
    # Circle 3
    'Bless': {'icon_id': 2256, 'circle': 3, 'type': 'defend'},
    'Fireball': {'icon_id': 2257, 'circle': 3, 'type': 'attack'},
    'Magic Lock': {'icon_id': 2258, 'circle': 3, 'type': 'utility'},
    'Poison': {'icon_id': 2259, 'circle': 3, 'type': 'attack'},
    'Telekinesis': {'icon_id': 2260, 'circle': 3, 'type': 'utility'},
    'Teleport': {'icon_id': 2261, 'circle': 3, 'type': 'utility'},
    'Unlock': {'icon_id': 2262, 'circle': 3, 'type': 'utility'},
    'Wall of Stone': {'icon_id': 2263, 'circle': 3, 'type': 'utility'},
    
    # Circle 4
    'Arch Cure': {'icon_id': 2264, 'circle': 4, 'type': 'defend'},
    'Arch Protection': {'icon_id': 2265, 'circle': 4, 'type': 'defend'},
    'Curse': {'icon_id': 2266, 'circle': 4, 'type': 'attack'},
    'Fire Field': {'icon_id': 2267, 'circle': 4, 'type': 'attack'},
    'Greater Heal': {'icon_id': 2268, 'circle': 4, 'type': 'defend'},
    'Lightning': {'icon_id': 2269, 'circle': 4, 'type': 'attack'},
    'Mana Drain': {'icon_id': 2270, 'circle': 4, 'type': 'attack'},
    'Recall': {'icon_id': 2271, 'circle': 4, 'type': 'utility'},
    
    # Circle 5
    'Blade Spirits': {'icon_id': 2272, 'circle': 5, 'type': 'attack'},
    'Dispel Field': {'icon_id': 2273, 'circle': 5, 'type': 'utility'},
    'Incognito': {'icon_id': 2274, 'circle': 5, 'type': 'utility'},
    'Magic Reflection': {'icon_id': 2275, 'circle': 5, 'type': 'defend'},
    'Mind Blast': {'icon_id': 2276, 'circle': 5, 'type': 'attack'},
    'Paralyze': {'icon_id': 2277, 'circle': 5, 'type': 'attack'},
    'Poison Field': {'icon_id': 2278, 'circle': 5, 'type': 'attack'},
    'Summon Creature': {'icon_id': 2279, 'circle': 5, 'type': 'utility'},
    
    # Circle 6
    'Dispel': {'icon_id': 2280, 'circle': 6, 'type': 'attack'},
    'Energy Bolt': {'icon_id': 2281, 'circle': 6, 'type': 'attack'},
    'Explosion': {'icon_id': 2282, 'circle': 6, 'type': 'attack'},
    'Invisibility': {'icon_id': 2283, 'circle': 6, 'type': 'utility'},
    'Mark': {'icon_id': 2284, 'circle': 6, 'type': 'utility'},
    'Mass Curse': {'icon_id': 2285, 'circle': 6, 'type': 'attack'},
    'Paralyze Field': {'icon_id': 2286, 'circle': 6, 'type': 'attack'},
    'Reveal': {'icon_id': 2287, 'circle': 6, 'type': 'utility'},
    
    # Circle 7
    'Chain Lightning': {'icon_id': 2288, 'circle': 7, 'type': 'attack'},
    'Energy Field': {'icon_id': 2289, 'circle': 7, 'type': 'attack'},
    'Flamestrike': {'icon_id': 2290, 'circle': 7, 'type': 'attack'},
    'Gate Travel': {'icon_id': 2291, 'circle': 7, 'type': 'utility'},
    'Mana Vampire': {'icon_id': 2292, 'circle': 7, 'type': 'attack'},
    'Mass Dispel': {'icon_id': 2293, 'circle': 7, 'type': 'attack'},
    'Meteor Swarm': {'icon_id': 2294, 'circle': 7, 'type': 'attack'},
    'Polymorph': {'icon_id': 2295, 'circle': 7, 'type': 'utility'},
    
    # Circle 8
    'Earthquake': {'icon_id': 2296, 'circle': 8, 'type': 'attack'},
    'Energy Vortex': {'icon_id': 2297, 'circle': 8, 'type': 'attack'},
    'Resurrection': {'icon_id': 2298, 'circle': 8, 'type': 'defend'},
    'Air Elemental': {'icon_id': 2299, 'circle': 8, 'type': 'utility'},
    'Summon Daemon': {'icon_id': 2300, 'circle': 8, 'type': 'attack'},
    'Earth Elemental': {'icon_id': 2301, 'circle': 8, 'type': 'utility'},
    'Fire Elemental': {'icon_id': 2302, 'circle': 8, 'type': 'utility'},
    'Water Elemental': {'icon_id': 2303, 'circle': 8, 'type': 'utility'},
}

# ===== COLORS =====

COLORS = {
    'info': 68,    # blue
    'ok': 63,      # green
    'warn': 53,    # yellow
    'bad': 33,     # red
}

# ===== HELPER FUNCTIONS =====

def find_nearest_enemy():
    """Find the nearest valid enemy target.
    Returns the nearest enemy mobile or None if no enemies found.
    Filters out innocents (blue) and allies (green) for safety.
    """
    try:
        
        # Get all mobiles within range
        enemy_filter = Mobiles.Filter()
        enemy_filter.Enabled = True
        enemy_filter.RangeMax = 12
        
        # CRITICAL: Notorieties property requires List[Byte], not List[int]
        # Each integer MUST be explicitly cast to Byte type using Byte(value)
        # Notoriety values: 1=Blue(Innocent), 2=Green(Ally), 3=Grey(Criminal), 
        #                   4=Orange(Enemy), 5=Red(Murderer), 6=Yellow(Invulnerable)
        # We filter for hostile targets only (3,4,5,6) and exclude innocents/allies (1,2)
        enemy_filter.Notorieties = List[Byte]([Byte(3), Byte(4), Byte(5), Byte(6)])
        enemy_filter.CheckIgnoreObject = True
        
        enemies = Mobiles.ApplyFilter(enemy_filter)
        
        if not enemies or len(enemies) == 0:
            return None
        
        # Extra safety layer: Double-check notoriety to prevent accidental friendly fire
        # Even though the filter should exclude innocents/allies, we verify again
        # This prevents targeting blues (1) or greens (2) if filter fails or lags
        valid_enemies = []
        for enemy in enemies:
            try:
                noto = int(getattr(enemy, 'Notoriety', 0))
                if noto not in (1, 2):  # Not innocent or ally - safe to attack
                    valid_enemies.append(enemy)
            except Exception:
                continue
        
        if not valid_enemies:
            return None
        
        # Find nearest
        nearest = None
        min_distance = 999
        for enemy in valid_enemies:
            try:
                distance = Player.DistanceTo(enemy)
                if distance < min_distance:
                    min_distance = distance
                    nearest = enemy
            except Exception:
                continue
        
        return nearest
    except Exception as e:
        debug_message(f"Error finding enemy: {e}", COLORS['bad'])
        return None

def is_valid_enemy(mobile):
    """Check if a mobile is a valid enemy target.
    Returns True if the mobile is a valid enemy (not innocent/ally).
    """
    try:
        if mobile is None:
            return False
        # Notoriety: 1=Blue(Innocent), 2=Green(Ally), 3=Grey(Criminal), 4=Orange(Enemy), 5=Red(Murderer), 6=Yellow(Invul)
        noto = int(getattr(mobile, 'Notoriety', 0))
        if noto in (1, 2):
            return False
        return True
    except Exception:
        return False

def debug_message(msg, color=68):
    """Send debug message to game client."""
    if DEBUG_MODE:
        try:
            Misc.SendMessage(f"[SpellHotbar] {msg}", color)
        except Exception:
            print(f"[SpellHotbar] {msg}")

def server_sync_delay():
    """Synchronize with server using backpack label check.
    This provides a natural server-synced delay that matches server response time.
    More reliable than arbitrary Misc.Pause() delays.
    """
    try:
        # GetLabel forces client to wait for server response
        # This naturally syncs with server tick rate
        Items.GetLabel(Player.Backpack.Serial)
    except Exception:
        # Fallback to minimal pause if GetLabel fails
        Misc.Pause(100)

def cleanup_gumps():
    """Close any gumps created by this script."""
    try:
        Gumps.CloseGump(GUMP_ID)
    except Exception:
        pass

def build_spell_buttons():
    """Build spell button list from HOTBAR_SPELLS configuration.
    Returns list of tuples: (spell_name, icon_id, icon_id_pressed)
    """
    buttons = []
    for spell_name in HOTBAR_SPELLS:
        if spell_name in SPELL_CATALOG:
            icon_id = SPELL_CATALOG[spell_name]['icon_id']
            buttons.append((spell_name, icon_id, icon_id))
        else:
            debug_message(f"Warning: Spell '{spell_name}' not found in SPELL_CATALOG", COLORS['warn'])
    return buttons

def send_static_gump():
    """Build and send the hotbar gump."""
    spell_buttons = build_spell_buttons()
    num_buttons = len(spell_buttons)
    
    # Calculate tight background dimensions
    # Width: left padding (10) + buttons (44 * num) + right padding (10)
    # Height: top padding (5) + button (44) + label space (15) + bottom padding (5)
    bg_width = 20 + (num_buttons * 44)
    bg_height = 69
    
    gd = Gumps.CreateGump(movable=True)
    Gumps.AddPage(gd, 0)
    Gumps.AddBackground(gd, 0, 0, bg_width, bg_height, 30546)
    Gumps.AddAlphaRegion(gd, 0, 0, bg_width, bg_height)
    
    # Spell buttons with hotkey labels
    x_offset = 10
    button_id = 1
    for spell, btn_unpressed, btn_pressed in spell_buttons:
        # Add spell button
        Gumps.AddButton(gd, x_offset, 5, btn_unpressed, btn_pressed, button_id, 1, 0)
        Gumps.AddTooltip(gd, r"{}".format(spell))
        # Add hotkey label below button
        hotkey = HOTKEY_LABELS.get(button_id, "")
        button_center = x_offset + (BUTTON_WIDTH // 2)
        label_x = button_center - (len(hotkey) * 4)
        Gumps.AddLabel(gd, label_x, 50, 1153, hotkey)
        x_offset += 44
        button_id += 1

    Gumps.SendGump(GUMP_ID, Player.Serial, HOTBAR_X, HOTBAR_Y, gd.gumpDefinition, gd.gumpStrings)


def cast_spell_with_targeting(spell_name):
    """Cast a spell and handle targeting for attack spells.
    For attack spells, automatically targets nearest enemy.
    For other spells, lets player target manually.
    """
    try:
        # Check if this is an attack spell
        spell_info = SPELL_CATALOG.get(spell_name)
        is_attack_spell = spell_info and spell_info.get('type') == 'attack'
        
        if is_attack_spell:
            # Find nearest enemy for attack spells
            enemy = find_nearest_enemy()
            if not enemy:
                debug_message(f"No valid enemy found for {spell_name}", COLORS['warn'])
                return False
            
            debug_message(f"Casting {spell_name} on nearest enemy", COLORS['ok'])
            
            # Server sync before casting
            server_sync_delay()
            
            # Cast the spell
            Spells.CastMagery(spell_name)
            
            # Wait for target cursor
            if Target.WaitForTarget(3000, False):
                # Validate target is still valid before executing
                if is_valid_enemy(enemy):
                    Target.TargetExecute(enemy)
                    debug_message(f"Targeted enemy with {spell_name}", COLORS['ok'])
                else:
                    debug_message("Enemy became invalid, canceling", COLORS['warn'])
                    Target.Cancel()
                    return False
            
            # Server sync after casting
            server_sync_delay()
            return True
        else:
            # Non-attack spells - cast without targeting
            debug_message(f"Casting {spell_name}", COLORS['ok'])
            
            # Server sync before casting
            server_sync_delay()
            
            Spells.CastMagery(spell_name)
            
            # Server sync after casting
            server_sync_delay()
            return True
    except Exception as e:
        debug_message(f"Error casting {spell_name}: {e}", COLORS['bad'])
        return False

def process_input():
    """Process input from the gump."""
    global HOTBAR_ACTIVE, HOTBAR_X, HOTBAR_Y
    spell_buttons = build_spell_buttons()
    
    Gumps.WaitForGump(GUMP_ID, 500)
    Gumps.CloseGump(GUMP_ID)
    gd = Gumps.GetGumpData(GUMP_ID)
    if not gd:
        return
    
    # Check if gump was right-clicked (buttonid 0 = right-click close)
    if gd.buttonid == 0:
        debug_message("Hotbar right-clicked, stopping script", COLORS['info'])
        HOTBAR_ACTIVE = False
        cleanup_gumps()
        # Stop the script by name
        try:
            Scripts.Stop('UI_spell_hotbar_hotkeys.py')
        except Exception:
            pass
        return

    # Handle spell button clicks
    if 1 <= gd.buttonid <= len(spell_buttons):
        spell_name = spell_buttons[gd.buttonid - 1][0]
        # Cast spell with appropriate targeting
        cast_spell_with_targeting(spell_name)
    
    send_static_gump()

# ===== MAIN EXECUTION =====

def main():
    """Main execution loop."""
    global HOTBAR_ACTIVE
    
    debug_message("Spell Hotbar starting...", COLORS['info'])
    
    # Initially send the gump
    send_static_gump()
    
    # Main loop: process input
    while Player.Connected and HOTBAR_ACTIVE:
        process_input()
        Misc.Pause(100)
    
    debug_message("Spell Hotbar stopped", COLORS['info'])
    cleanup_gumps()

# Run the script
if __name__ == '__main__':
    main()
