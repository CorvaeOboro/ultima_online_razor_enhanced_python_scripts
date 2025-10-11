"""
SPELL Attack Nearest Enemy - a Razor Enhanced Python Script for Ultima Online

Cast Spells on Nearest Enemy based on mana , reagents , and priority
( Ebolt > Explosion > Flamestrike > Lightning > Harm > Fireball > Magic Arrow )

TODO: switching spellbooks per spell , by property like Energy Bolt

HOTKEY:: Q
VERSION::20250928
"""

from System.Collections.Generic import List
from Scripts.glossary.enemies import GetEnemyNotorieties, GetEnemies
from Scripts.utilities.mobiles import GetEmptyMobileList
import re

# GLOBAL SETTINGS
ATTACK_ON = True # default = true attacking target , set to false if not using pets as you dont want the reaction until your spell hits 
MANA_REQUIRED = True # default = true mana determines spell selection, set to false if have a lot of "reduced mana cost"
REAGENT_REQUIRED = True # default = true available reagents determine spell selection, set to false if have a lot of "lower reagent cost" 
# each one of these adds a slight processing delay to precast , so be careful 

DEBUG_MODE = False
# When enabled, automatically switch to peace mode (warmode off) after each successful spell cast
RETURN_TO_PEACE_AFTER_CAST = True
# equip a spellbook from backpack if none is equipped. If False, requires you to have it equipped already.
EQUIP_SPELLBOOK = True
#======================================================================

def debug_message(message, color=67):
    if not DEBUG_MODE:
        return
    try:
        Misc.SendMessage(f"[Attack] {message}", color)
    except Exception:
        print(f"[Attack] {message}")

class SpellManager:
    def __init__(self):
        self.debug_color = 67  # Light blue for messages
        self.error_color = 33  # Red for errors
        self.success_color = 68  # Green for success
        
        # Track currently preferred/equipped spellbook signature to re-equip correctly
        self.saved_spellbook_signature = None
        
        # Timing configuration - optimized delays
        self.cast_delay = 1200   
        # Reduce pre-cast delays to speed up time-to-cast
        self.equip_delay = 1   
        self.target_delay = 1  
        self.attack_delay = 1  
        
        # Combat configuration
        self.min_mana = 4  # Minimum mana to even try casting
        self.min_hp_percent = 5  # Only cast if HP above this % , otherwise heal self
        
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
                    0xF8C: 1,  # Sulfurous Ash
                    0xF8D: 1   # Spiders' Silk
                },
                "range": 12
            },
            "Lightning": {
                "mana": 15,
                "reagents": {
                    0xF8C: 1   # Sulfurous Ash
                },
                "range": 10
            },
            "Harm": {
                "mana": 6,
                "reagents": {
                    0xF88: 1   # Nightshade
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
            if DEBUG_MODE:
                self.debug(f"Skipping mana check for {spell_name} (MANA_REQUIRED=False)", self.debug_color)
            return True
        spell = self.spells.get(spell_name, {})
        mana_needed = spell.get('mana', 0)
        if Player.Mana >= mana_needed:
            return True
        if DEBUG_MODE:
            self.debug(f"Not enough mana for {spell_name}: needed {mana_needed}, have {Player.Mana}", self.error_color)
        return False

    def has_enough_reagents(self, spell_name):
        if not REAGENT_REQUIRED:
            if DEBUG_MODE:
                self.debug(f"Skipping reagent check for {spell_name} (REAGENT_REQUIRED=False)", self.debug_color)
            return True
        spell = self.spells.get(spell_name, {})
        reagents = spell.get('reagents', {})
        for itemid, qty in reagents.items():
            if Items.BackpackCount(itemid) < qty:
                if DEBUG_MODE:
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
                # Save signature of currently equipped spellbook so we can restore later
                self.saved_spellbook_signature = self.make_item_signature(item)
                return True
        
        # If auto-equip is disabled, do not attempt to pull from backpack
        if not EQUIP_SPELLBOOK:
            self.debug("Spellbook not equipped and EQUIP_SPELLBOOK is False; skipping auto-equip.", self.error_color)
            return False
        
        # Find spellbook in backpack
        spellbook = Items.FindByID(0x0EFA, -1, Player.Backpack.Serial, -1)
        if spellbook:
            self.debug("Equipping spellbook...")
            Player.EquipItem(spellbook)
            Misc.Pause(self.equip_delay)  # Only pause if we actually equipped
            self.saved_spellbook_signature = self.make_item_signature(spellbook)
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
            # Validate target safety and liveness before firing
            if not self.is_valid_enemy(enemy):
                self.debug("Leftover target invalid/safe target detected, canceling cast via dagger swap", self.error_color)
                self.cancel_spell_cast()
                return False
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
        if self.handle_target_reticle(enemy):
            return True
            
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
                # Optional: return to peace mode after a successful cast for RP/cosmetic reasons
                if RETURN_TO_PEACE_AFTER_CAST:
                    try:
                        Player.WarMode = False
                    except Exception:
                        pass
                Target.WaitForTarget(3000, False)  
                # Validate right before firing
                if not self.is_valid_enemy(enemy):
                    self.debug("Target invalid or dead before target execute. Canceling cast via dagger swap.", self.error_color)
                    self.cancel_spell_cast()
                    return False
                Target.TargetExecute(enemy)
                Misc.Pause(self.cast_delay)
                # Optional: return to peace mode after a successful cast for RP/cosmetic reasons
                if RETURN_TO_PEACE_AFTER_CAST:
                    try:
                        Player.WarMode = False
                    except Exception:
                        pass
                return True
                
        self.debug("No spells available")
        return False

    # ================== Safety and Equipment Helpers ==================
    def is_valid_enemy(self, mobile) -> bool:
        """Strict notoriety and sanity check to avoid blue/ally targets."""
        try:
            if mobile is None:
                return False
            # Notoriety: 1=Blue(Innocent), 2=Green(Ally/Guild), 3=Grey(Criminal), 4=Orange(Enemy), 5=Red(Murderer), 6=Yellow(Invul/Neutral)
            noto = int(getattr(mobile, 'Notoriety', 0))
            if noto in (1, 2):
                return False
            return True
        except Exception:
            return False

    def make_item_signature(self, item):
        """Create a signature for an item to re-identify it later: id, hue, name, durability, properties."""
        try:
            item_id = int(getattr(item, 'ItemID', 0))
            hue = int(getattr(item, 'Hue', -1)) if hasattr(item, 'Hue') else -1
            name = str(getattr(item, 'Name', '') or '')
            # Pull properties 
            props = []
            try:
                Items.WaitForProps(int(item.Serial), 750)
                prop_list = Items.GetPropStringList(int(item.Serial))
                if prop_list:
                    props.extend(prop_list)
                idx = 0
                while True:
                    p = Items.GetPropStringByIndex(int(item.Serial), idx)
                    if not p:
                        break
                    if p not in props:
                        props.append(p)
                    idx += 1
            except Exception:
                pass
            # Durability parse 
            cur_dura, max_dura = 0, 0
            try:
                for line in props:
                    m = re.search(r"durability\s+(\d+)\s*/\s*(\d+)", str(line).lower())
                    if m:
                        cur_dura, max_dura = int(m.group(1)), int(m.group(2))
                        break
            except Exception:
                pass
            return {
                'item_id': item_id,
                'hue': hue,
                'name': name,
                'durability': (cur_dura, max_dura),
                'props': set([str(x) for x in props])
            }
        except Exception:
            return None

    def find_matching_spellbook(self):
        """Search backpack for a spellbook matching the saved signature; fallback to any spellbook."""
        try:
            if not Player.Backpack:
                return None
            contains = Items.FindBySerial(Player.Backpack.Serial).Contains
            candidates = [it for it in contains if int(getattr(it, 'ItemID', 0)) == 0x0EFA]
            if not candidates:
                return None
            if not self.saved_spellbook_signature:
                return candidates[0]
            sig = self.saved_spellbook_signature
            # Try exact hue match + durability + props overlap
            best = None
            for it in candidates:
                itsig = self.make_item_signature(it)
                if not itsig:
                    continue
                score = 0
                if itsig['hue'] == sig['hue']:
                    score += 3
                if itsig['durability'] == sig['durability'] and itsig['durability'] != (0, 0):
                    score += 3
                # props overlap
                overlap = len(itsig['props'].intersection(sig['props']))
                score += min(3, overlap)
                # name heuristic
                if sig['name'] and itsig.get('name', '') == sig['name']:
                    score += 1
                if not best or score > best[0]:
                    best = (score, it)
            return best[1] if best else candidates[0]
        except Exception:
            return None

    def equip_dagger(self) -> bool:
        """Equip a dagger (0x0F52) to cancel current spell target cursor."""
        try:
            dagger = Items.FindByID(0x0F52, -1, Player.Backpack.Serial)
            if dagger:
                Player.EquipItem(dagger)
                Misc.Pause(self.equip_delay)
                return True
        except Exception:
            pass
        return False

    def re_equip_spellbook(self) -> bool:
        """Re-equip the correct spellbook based on saved signature, checking layers first."""
        try:
            # Already equipped?
            for layer in ['LeftHand', 'RightHand']:
                it = Player.GetItemOnLayer(layer)
                if it and int(getattr(it, 'ItemID', 0)) == 0x0EFA:
                    return True
            # Find matching in backpack
            match = self.find_matching_spellbook()
            if match:
                Player.EquipItem(match)
                Misc.Pause(self.equip_delay)
                return True
        except Exception:
            pass
        return False

    def cancel_spell_cast(self):
        """Cancel any active target cursor by swapping to dagger and restoring spellbook."""
        try:
            # Preserve current equipped spellbook signature if possible
            for layer in ['LeftHand', 'RightHand']:
                it = Player.GetItemOnLayer(layer)
                if it and int(getattr(it, 'ItemID', 0)) == 0x0EFA:
                    self.saved_spellbook_signature = self.make_item_signature(it)
                    break
            # Equip dagger to force-cancel target cursor
            equipped = self.equip_dagger()
            if not equipped:
                # As a fallback, try cancel directly
                if Target.HasTarget():
                    Target.Cancel()
                return False
            # Re-equip original spellbook
            self.re_equip_spellbook()
        except Exception:
            # Ensure target is canceled at minimum
            try:
                if Target.HasTarget():
                    Target.Cancel()
            except Exception:
                pass
        return

def FindEnemy():
    """Returns the nearest enemy"""
    enemies = GetEnemies(Mobiles, 0, 12, GetEnemyNotorieties())
    # Extra safety: filter out innocents (blue) and allies (green) explicitly
    def _safe(m):
        try:
            noto = int(getattr(m, 'Notoriety', 0))
            return noto not in (1, 2)
        except Exception:
            return False
    enemies = [e for e in enemies if _safe(e)]
    
    if len(enemies) == 0:
        return None
    elif len(enemies) == 1:
        return enemies[0]
    else:
        enemiesInWarMode = GetEmptyMobileList(Mobiles)
        enemiesInWarMode.AddRange([enemy for enemy in enemies if enemy.WarMode])
        
        # When using .NET typed lists, prefer .Count over len() for reliability
        if enemiesInWarMode.Count == 0:
            # Convert python list to .NET List[Mobile] before calling Mobiles.Select
            enemiesList = GetEmptyMobileList(Mobiles)
            enemiesList.AddRange(enemies)
            return Mobiles.Select(enemiesList, 'Nearest')
        elif enemiesInWarMode.Count == 1:
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
