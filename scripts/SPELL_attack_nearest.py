"""
Spell Attack Nearest Enemy - a Razor Enhanced Python Script for Ultima Online

Automatically attacks the nearest enemy with offensive spells:
1. Checks/equips spellbook if needed
2. Prioritize Energy Bolt first ( Ebolt > Explosion > Flamestrike > Lightning > Harm > Fireball > Magic Arrow )
3. casts other spells if reagents missing or mana low

TODO:
- add spellbook switching , search by property like Energy Bolt

HOTKEY:: Q
VERSION::20250707
"""

from System.Collections.Generic import List
from Scripts.glossary.enemies import GetEnemyNotorieties, GetEnemies
from Scripts.utilities.mobiles import GetEmptyMobileList

# GLOBAL SETTINGS
ATTACK_ON = True # default = true , set to false if not using pets 
MANA_REQUIRED = True # default = true , set to false if have "reduced mana cost"
REAGENT_REQUIRED = True # default = true , set to false if have "lower reagent cost" 
DEBUG_ON = False
#======================================================================

def debug_message(message, color=67):
    """Centralized debug logging gated by DEBUG_ON.

    All script messages should flow through this function so that toggling
    DEBUG_ON enables/disables output consistently.
    """
    if not DEBUG_ON:
        return
    try:
        Misc.SendMessage(f"[Attack] {message}", color)
    except Exception:
        # Fallback to print in case Misc is unavailable (e.g., offline testing)
        print(f"[Attack] {message}")

class SpellManager:
    def __init__(self):
        self.debug_color = 67  # Light blue for messages
        self.error_color = 33  # Red for errors
        self.success_color = 68  # Green for success
        
        # Timing configuration - optimized delays
        self.cast_delay = 1200   
        self.equip_delay = 800   
        self.target_delay = 400  
        self.attack_delay = 600  
        
        # Combat configuration
        self.min_mana = 4  # Minimum mana to even try casting
        self.min_hp_percent = 50  # Only cast if HP above this % , otherwise heal self
        
        # Spell configurations with required reagents
        self.spells = {
            "Energy Bolt": {
                "mana": 20,
                "reagents": {
                    0xF7A: 1,  # Black Pearl
                    0xF88: 1   # Nightshade
                },
                "range": 12
            },
            "Flamestrike": {
                "mana": 40,
                "reagents": {
                    0xF7A: 1,  # Black Pearl
                    0xF85: 1,  # Ginseng
                    0xF86: 1,  # Mandrake Root
                    0xF8C: 1   # Sulfurous Ash
                },
                "range": 12
            },
            "Lightning": {
                "mana": 15,
                "reagents": {
                    0xF7A: 1,  # Black Pearl
                    0xF8C: 1   # Sulfurous Ash
                },
                "range": 10
            },
            "Harm": {
                "mana": 6,
                "reagents": {
                    0xF88: 1,  # Nightshade
                    0xF8C: 1   # Sulfurous Ash
                },
                "range": 8
            },
            "Magic Arrow": {
                "mana": 4,
                "reagents": {
                    0xF8C: 1   # Sulfurous Ash
                },
                "range": 10
            }
        }

    def has_enough_mana(self, spell_name):
        if not MANA_REQUIRED:
            if DEBUG_ON:
                self.debug(f"Skipping mana check for {spell_name} (MANA_REQUIRED=False)", self.debug_color)
            return True
        spell = self.spells.get(spell_name, {})
        mana_needed = spell.get('mana', 0)
        if Player.Mana >= mana_needed:
            return True
        if DEBUG_ON:
            self.debug(f"Not enough mana for {spell_name}: needed {mana_needed}, have {Player.Mana}", self.error_color)
        return False

    def has_enough_reagents(self, spell_name):
        if not REAGENT_REQUIRED:
            if DEBUG_ON:
                self.debug(f"Skipping reagent check for {spell_name} (REAGENT_REQUIRED=False)", self.debug_color)
            return True
        spell = self.spells.get(spell_name, {})
        reagents = spell.get('reagents', {})
        for itemid, qty in reagents.items():
            if Items.BackpackCount(itemid) < qty:
                if DEBUG_ON:
                    self.debug(f"Not enough reagent 0x{itemid:X} for {spell_name}", self.error_color)
                return False
        return True

        # Track if target reticle is active
        self.target_active = False

    def debug(self, message, color=None):
        """Send a debug message to the game client"""
        if color is None:
            color = self.debug_color
        # Route all messages through the centralized function so DEBUG_ON controls output
        debug_message(message, color)
    
    def check_spellbook(self):
        """Check if spellbook is equipped, if not try to equip one"""
        # Check if already equipped
        for layer in ['LeftHand', 'RightHand']:
            item = Player.GetItemOnLayer(layer)
            if item and item.ItemID == 0x0EFA:  # Spellbook ID
                return True
        
        # Find spellbook in backpack
        spellbook = Items.FindByID(0x0EFA, -1, Player.Backpack.Serial, -1)
        if spellbook:
            self.debug("Equipping spellbook...")
            Player.EquipItem(spellbook)
            Misc.Pause(self.equip_delay)  # Only pause if we actually equipped
            return True
            
        self.debug("No spellbook found!", self.error_color)
        return False
    
    def check_combat_state(self):
        """Check if we're in a good state to cast spells"""
        # Check mana
        if Player.Mana < self.min_mana:
            self.debug("Low mana, skipping spells", self.error_color)
            return False
            

        return True
    
    def check_reagents(self, spell_name):
        """Check if we have enough reagents for the spell"""
        spell = self.spells[spell_name]
        for reagent_id, amount in spell["reagents"].items():
            items = Items.FindByID(reagent_id, -1, Player.Backpack.Serial, -1)
            if not items or items.Amount < amount:
                return False
        return True
    
    def check_mana(self, spell_name):
        """Check if we have enough mana for the spell"""
        required_mana = self.spells[spell_name]["mana"]
        return Player.Mana >= required_mana
    
    def in_range(self, enemy, spell_name):
        """Check if enemy is in range for the spell"""
        max_range = self.spells[spell_name]["range"]
        return Player.DistanceTo(enemy) <= max_range
    
    def attack_target(self, enemy):
        """Attack the target and wait a moment"""
        Player.Attack(enemy)
        Misc.Pause(self.attack_delay)
    
    def handle_target_reticle(self, enemy):
        """Handle any leftover target reticle by targeting the enemy"""
        if Target.HasTarget():
            self.debug("Found leftover target, targeting enemy...")
            Target.TargetExecute(enemy)
            Misc.Pause(self.target_delay)
            return True
        return False
    
    def cast_offensive_spell(self, enemy):
        """Try to cast the best offensive spell available"""
        # First check overall combat state
        if not self.check_combat_state():
            return False
            
        # Handle any leftover target reticle
        self.handle_target_reticle(enemy)
            
        # Then check spellbook
        if not self.check_spellbook():
            return False
            
        # Try spells in order of preference
        for spell_name in ["Energy Bolt", "Flamestrike", "Lightning", "Harm", "Magic Arrow"]:
            if (self.has_enough_mana(spell_name) and 
                self.has_enough_reagents(spell_name) and 
                self.in_range(enemy, spell_name)):
                
                self.debug(f"Casting {spell_name}")
                Spells.CastMagery(spell_name)
                Target.WaitForTarget(5000, False)  
                Target.TargetExecute(enemy)
                Misc.Pause(self.cast_delay)
                return True
                
        self.debug("No spells available")
        return False

def FindEnemy():
    """Returns the nearest enemy"""
    enemies = GetEnemies(Mobiles, 0, 12, GetEnemyNotorieties())
    
    if len(enemies) == 0:
        return None
    elif len(enemies) == 1:
        return enemies[0]
    else:
        enemiesInWarMode = GetEmptyMobileList(Mobiles)
        enemiesInWarMode.AddRange([enemy for enemy in enemies if enemy.WarMode])
        
        if len(enemiesInWarMode) == 0:
            return Mobiles.Select(enemies, 'Nearest')
        elif len(enemiesInWarMode) == 1:
            return enemiesInWarMode[0]
        else:
            return Mobiles.Select(enemiesInWarMode, 'Nearest')

# Main execution
spell_manager = SpellManager()

# Handle any leftover target reticle first
if Target.HasTarget():
    enemy = FindEnemy()
    if enemy:
        spell_manager.handle_target_reticle(enemy)
    else:
        Target.Cancel()
        spell_manager.debug("No enemies found for leftover target", spell_manager.error_color)
else:
    enemy = FindEnemy()
    if enemy:
        # Always attack first
        spell_manager.attack_target(enemy)
        
        # Then try to cast if conditions are good
        if spell_manager.check_combat_state():
            spell_manager.cast_offensive_spell(enemy)
    else:
        spell_manager.debug("No enemies found", spell_manager.error_color)
