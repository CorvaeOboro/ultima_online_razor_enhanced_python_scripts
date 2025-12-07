"""
SPELL PureMage Selection - a Razor Enhanced Python Script for Ultima Online

Cast spells at enemy based on currently empowered spell from PureMage system.
Reads the current "empowered" spell from gump image IDs and casts it

STATUS::working
HOTKEY:: Q 
VERSION::20251206
"""

from System.Collections.Generic import List
from Scripts.glossary.enemies import GetEnemyNotorieties, GetEnemies
from Scripts.utilities.mobiles import GetEmptyMobileList
import re

# GLOBAL SETTINGS
DEBUG_MODE = False

USE_GUMP_READING = True # If True, read spell from gump image ID instead of journal
ATTACK_ON = True # Attack target before casting pet builds may want to send them first
EQUIP_SPELLBOOK = False # equip a spellbook from backpack if none is equipped. If False, requires you to have it equipped already. we are using staff currently
RETURN_TO_PEACE_AFTER_CAST = False # this is cool for rp walking ,When enabled, automatically switch to peace mode (warmode off) after each successful spell cast

ENEMY_SEARCH_RANGE = 12 # Enemy search range

PUREMAGE_GUMP_ID = 3134130146 # Gump ID for PureMage spell selection interface
PUREMAGE_STATUS_GUMP_ID = 0xbacf07e2 # Status gump ID that shows current empowered spell
PUREMAGE_BUTTON_ID = 1 # Button ID to press on the gump ( with gump reading the image id we dont need to press the button to spam journal )
GUMP_RESPONSE_DELAY = 100 # Delay after sending gump response (ms)
CAST_DELAY = 50 # Delay after casting spell (ms)

DEFAULT_SPELL = "Lightning" # Default spell to cast when no spell is selected or when excluded spell is recommended
# List of spells to ignore from PureMage recommendations (will cast DEFAULT_SPELL instead)
# TODO: add override for GREEN empowered summon effect , we will cast any spells if they have it 
EXCLUDED_SPELLS = [
    #"Flamestrike",  # Too slow , however new system we cant skip
]

# SPELL DATABASE - Single source of truth for all spell IDs
# Each spell has hex and decimal (int) representations of the same item art ID , note these arent the gump image ids , its the items art
SPELL_DATABASE = {
    "Magic Arrow": {
        "item_art_hex": 0x2084,      # Hex format
        "item_art_int": 8324,        # Decimal format (same value)
    },
    "Harm": {
        "item_art_hex": 0x208B,
        "item_art_int": 8331,
    },
    "Fireball": {
        "item_art_hex": 0x2091,
        "item_art_int": 8337,
    },
    "Lightning": {
        "item_art_hex": 0x209D,
        "item_art_int": 8349,
    },
    "Mind Blast": {
        "item_art_hex": 0x20A4,
        "item_art_int": 8356,        # Verified in gump 0xbacf07e2
    },
    "Explosion": {
        "item_art_hex": 0x20AA,
        "item_art_int": 8362,
    },
    "Flamestrike": {
        "item_art_hex": 0x20B2,
        "item_art_int": 8370,
    },
    "Energy Bolt": {
        "item_art_hex": 0x20A9,
        "item_art_int": 8361,
    },
}

# Build reverse lookup dictionaries from SPELL_DATABASE
def _build_spell_lookups():
    """Build reverse lookup dictionaries from the spell database"""
    lookups = {}
    for spell_name, ids in SPELL_DATABASE.items():
        for id_type, id_value in ids.items():
            if id_value not in lookups:
                lookups[id_value] = spell_name
    return lookups

SPELL_ID_LOOKUP = _build_spell_lookups()
#======================================================================

def debug_message(message, color=67):
    if not DEBUG_MODE:
        return
    try:
        Misc.SendMessage(f"[SPELL_PureMage] {message}", color)
    except Exception:
        print(f"[SPELL_PureMage] {message}")

class PureMageSpellSelector:
    def __init__(self):
        self.debug_color = 67  # Light blue for messages
        self.error_color = 33  # Red for errors
        self.success_color = 68  # Green for success
        
        # Track currently preferred/equipped spellbook signature to re-equip correctly
        self.saved_spellbook_signature = None
        
        # Timing configuration
        self.equip_delay = 1
        self.gump_delay = GUMP_RESPONSE_DELAY
        self.cast_delay = CAST_DELAY
        self.target_delay = 1
        self.attack_delay = 1

    def debug(self, message, color=None):
        """Send a debug message to the game client"""
        if color is None:
            color = self.debug_color
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
            Misc.Pause(self.equip_delay)
            self.saved_spellbook_signature = self.make_item_signature(spellbook)
            return True
            
        self.debug("No spellbook found!", self.error_color)
        return False
    
    def is_valid_enemy(self, mobile):
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
    
    def attack_target(self, enemy):
        """Attack the target and wait a moment"""
        if ATTACK_ON:
            Player.Attack(enemy)
            Misc.Pause(self.attack_delay)
    
    def handle_target_reticle(self, enemy):
        """Handle any leftover target reticle by targeting the enemy"""
        if Target.HasTarget():
            # Validate target safety and liveness before firing
            if not self.is_valid_enemy(enemy):
                self.debug("Leftover target invalid/safe target detected", self.error_color)
                return False
            self.debug("Found leftover target, targeting enemy...")
            Target.TargetExecute(enemy)
            Misc.Pause(self.target_delay)
            return True
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
    
    def clear_system_messages(self):
        """Clear system messages to prepare for reading new ones"""
        try:
            Journal.Clear()
            self.debug("Cleared system messages")
        except Exception as e:
            self.debug(f"Error clearing system messages: {e}", self.error_color)
    
    def respond_to_gump(self):
        """Send gump response to PureMage spell selection interface"""
        try:
            Gumps.SendAction(PUREMAGE_GUMP_ID, PUREMAGE_BUTTON_ID)
            Misc.Pause(self.gump_delay)
            self.debug("Sent gump response")
            return True
        except Exception as e:
            self.debug(f"Error responding to gump: {e}", self.error_color)
            return False
    
    def get_backpack_label(self):
        """Get backpack label to trigger system message update (ping check)"""
        try:
            if Player.Backpack:
                # This triggers a label request which updates system messages
                label = Player.Backpack.Name
                Misc.Pause(50)  # Small delay for label to arrive
                self.debug(f"Got backpack label: {label}")
                return True
        except Exception as e:
            self.debug(f"Error getting backpack label: {e}", self.error_color)
        return False
    
    def read_spell_from_journal(self):
        """Read the selected spell from system messages"""
        try:
            # Check journal for spell names from SPELL_DATABASE
            for spell_name in SPELL_DATABASE.keys():
                if Journal.SearchByName(spell_name, "System"):
                    self.debug(f"Found spell in journal: {spell_name}", self.success_color)
                    return spell_name
                # Also check without name filter
                if Journal.Search(spell_name):
                    self.debug(f"Found spell in journal (no filter): {spell_name}", self.success_color)
                    return spell_name
            
            self.debug("No spell found in journal", self.error_color)
            return None
        except Exception as e:
            self.debug(f"Error reading journal: {e}", self.error_color)
            return None
    
    def read_spell_from_gump(self):
        """Read the current empowered spell directly from the status gump using GetLineList"""
        try:
            # Check if the status gump exists
            if not Gumps.HasGump(PUREMAGE_STATUS_GUMP_ID):
                self.debug("PureMage status gump not found", self.error_color)
                return None
            
            self.debug(f"Gump 0x{PUREMAGE_STATUS_GUMP_ID:X} found, reading lines...")
            
            # Use GetLineList to read gump text lines
            lines = Gumps.GetLineList(PUREMAGE_STATUS_GUMP_ID, True)
            
            if not lines or len(lines) == 0:
                self.debug("GetLineList returned no lines", self.error_color)
                return None
            
            self.debug(f"=== GUMP LINE DATA ({len(lines)} lines) ===")
            
            # Process each line
            for idx, line in enumerate(lines):
                line_str = str(line).strip()
                self.debug(f"  [{idx}] '{line_str}'")
                
                # Try to parse as integer and lookup in SPELL_ID_LOOKUP
                try:
                    line_id = int(line_str)
                    self.debug(f"    -> Parsed as int: {line_id} (0x{line_id:X})")
                    
                    if line_id in SPELL_ID_LOOKUP:
                        spell_name = SPELL_ID_LOOKUP[line_id]
                        self.debug(f"    -> MATCH! {line_id} (0x{line_id:X}) -> {spell_name}", self.success_color)
                        return spell_name
                    else:
                        self.debug(f"    -> Not in SPELL_ID_LOOKUP")
                except Exception as e:
                    self.debug(f"    -> Not an integer or parse error")
            
            # Show what's in SPELL_ID_LOOKUP for reference
            self.debug(f"=== SPELL_ID_LOOKUP contains {len(SPELL_ID_LOOKUP)} entries ===")
            for spell_id, spell_name in sorted(SPELL_ID_LOOKUP.items()):
                self.debug(f"  {spell_id} (0x{spell_id:X}) -> {spell_name}")
            
            self.debug("No spell ID found in gump lines", self.error_color)
            return None
            
        except Exception as e:
            self.debug(f"Error reading gump: {e}", self.error_color)
            import traceback
            self.debug(f"Traceback: {traceback.format_exc()}", self.error_color)
            return None
    
    def get_current_spell(self):
        """Get current empowered spell using configured method (gump or journal)"""
        if USE_GUMP_READING:
            self.debug("Reading spell from gump...")
            spell = self.read_spell_from_gump()
            if spell:
                return spell
            # Fallback to journal if gump reading fails
            self.debug("Gump reading failed, falling back to journal...")
            return self.read_spell_from_journal()
        else:
            self.debug("Reading spell from journal...")
            return self.read_spell_from_journal()
    
    def cast_spell(self, spell_name, enemy=None):
        """Cast the specified spell with optional target"""
        try:
            if spell_name not in SPELL_DATABASE:
                self.debug(f"Unknown spell: {spell_name}", self.error_color)
                Misc.SendMessage(f"Unknown spell: {spell_name}", 34)
                return False
            
            # Check spellbook before casting (only if EQUIP_SPELLBOOK is enabled)
            if EQUIP_SPELLBOOK:
                if not self.check_spellbook():
                    return False
            
            # Cast the spell (spell name is used directly)
            self.debug(f"Casting {spell_name}", self.success_color)
            Spells.CastMagery(spell_name)
            
            # If we have an enemy target, wait for target and execute
            if enemy:
                Target.WaitForTarget(3000, False)
                # Validate right before firing
                if not self.is_valid_enemy(enemy):
                    self.debug("Target invalid or dead before target execute.", self.error_color)
                    return False
                Target.TargetExecute(enemy)
            
            Misc.Pause(self.cast_delay)
            
            # Optional: return to peace mode after cast
            if RETURN_TO_PEACE_AFTER_CAST:
                try:
                    Player.WarMode = False
                except Exception:
                    pass
            
            return True
        except Exception as e:
            self.debug(f"Error casting spell: {e}", self.error_color)
            return False
    
    def execute_PureMage_selection(self, enemy=None):
        """Main execution flow for PureMage spell selection"""
        try:
            # Step 1: Get current spell (from gump or journal based on USE_GUMP_READING)
            if USE_GUMP_READING:
                # Read directly from gump - no need to press button or spam journal
                spell_name = self.get_current_spell()
            else:
                # Legacy method: Clear journal, press gump button, read from journal
                self.clear_system_messages()
                
                # Step 2: Respond to gump
                if not self.respond_to_gump():
                    return False
                
                # Step 3: Get backpack label (ping check)
                self.get_backpack_label()
                
                # Step 4: Read spell from journal
                spell_name = self.read_spell_from_journal()
            
            # Step 5: Check if spell is excluded or missing
            if not spell_name:
                self.debug(f"No spell selected, using default: {DEFAULT_SPELL}", self.success_color)
                spell_name = DEFAULT_SPELL
            elif spell_name in EXCLUDED_SPELLS:
                self.debug(f"Spell '{spell_name}' is excluded, using default: {DEFAULT_SPELL}", self.success_color)
                spell_name = DEFAULT_SPELL
            
            # Step 6: Cast the spell with target
            return self.cast_spell(spell_name, enemy)
            
        except Exception as e:
            self.debug(f"Error in PureMage selection: {e}", self.error_color)
            return False

def FindEnemy():
    """Returns the nearest enemy"""
    enemies = GetEnemies(Mobiles, 0, ENEMY_SEARCH_RANGE, GetEnemyNotorieties())
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
PureMage_selector = PureMageSpellSelector()

# Handle any leftover target reticle first
if Target.HasTarget():
    enemy = FindEnemy()
    if enemy:
        PureMage_selector.handle_target_reticle(enemy)
    else:
        PureMage_selector.debug("No enemies found for leftover target", PureMage_selector.error_color)
else:
    enemy = FindEnemy()
    if enemy:
        # Always attack first to set target
        PureMage_selector.attack_target(enemy)
        
        # Enter war mode if not already
        try:
            if not Player.WarMode:
                Player.WarMode = True
                Misc.Pause(50)
        except Exception as e:
            PureMage_selector.debug(f"Could not set war mode: {e}", PureMage_selector.error_color)
        
        # Then execute PureMage selection with target
        PureMage_selector.execute_PureMage_selection(enemy)
    else:
        PureMage_selector.debug("No enemies found", PureMage_selector.error_color)
