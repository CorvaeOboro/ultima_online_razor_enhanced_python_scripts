"""
SPELL Create Food - a Razor Enhanced Python script for Ultima Online

cast the Create Food spell to summon a mana restorative item
Finds and equips a basic spellbook from backpack , as we dont want to waste durability on our good spellbook
Casts Create Food repeatedly until 20 items are created

common to custom shards create food will produce mana restoring items if cast while holding a spellbook

TODO: this maybe could be merged with ready check script , if not enough mana restorative then create it

HOTKEY:: None 
VERSION::20250918
"""

import re

DEBUG_MODE = False  # Controls whether debug_message outputs to the client

EQUIP_BASE_SPELLBOOK = True # When True, will ensure a basic (no modifiers) spellbook is equipped before casting
REQUIRE_BLESSED_FOR_BASE = True # When True, a base spellbook must explicitly have the 'Blessed' property
REQUIRE_SPELLBOOK_NAME = True # When True, require the item name/properties to indicate 'Spellbook' to avoid runebooks

# Mana-restorative items produced by Create Food on custom shards while equipped a spellbook
# Using IDs consistent with prior scripts (grapes, dates, peach)
MANA_RESTORATIVE_ITEM_IDS = [
    0x09D1,  # Grapes
    0x1727,  # Dates
    0x09D2,  # Peach
]

# Casting and item targets
MAX_CASTS = 20
MAX_MANA_RESTORATIVE_TOTAL = 20  # Stop when this many restorative items exist in backpack

class CreateFoodManager:
    def __init__(self):
        self.debug_color = 67  # Light blue for messages
        self.error_color = 33  # Red for errors
        self.success_color = 68  # Green for success
        
        # Timing configuration
        self.equip_delay = 1000  # 1 second after equipping
        self.cast_delay = 2000   # 2 seconds after casting
        self.dress_delay = 1500  # 1.5 seconds after dress macro
        
        # Spell configuration
        self.min_mana = 4  # Create Food requires 4 mana
        
        # Current spellbook tracking
        self.current_spellbook = None
        # Previously equipped (non-base) spellbook to restore after sequence
        self.previous_spellbook_serial = None

        # Spellbook detection configuration
        self.spellbook_item_id = 0x0EFA
        # Property keywords that indicate modifiers (i.e., NOT a base spellbook)
        self.modifier_keywords = [
            "Slayer",
            "Lower Reagent Cost",
            "Lower Mana Cost",
            "Faster Casting",
            "Faster Cast Recovery",
            "Spell Damage Increase",
            "Mana Regeneration",
            "Hit Chance Increase",
            "Defense Chance Increase",
            "Luck",
            "Durability",
            "Exceptional",
            "Charges",
        ]
        # Properties considered safe/neutral on a base spellbook
        self.neutral_properties = {"Blessed", "Insured", "Spellbook"}
        
    def debug_message(self, message, color=None):
        """Send a debug message to the game client (gated by DEBUG_MODE)."""
        if not DEBUG_MODE:
            return
        if color is None:
            color = self.debug_color
        Misc.SendMessage(f"[SPELL_create_food] {message}", color)

    def count_restorative_items(self):
        """Count total mana-restorative items in the player's backpack."""
        total = 0
        try:
            for item_id in MANA_RESTORATIVE_ITEM_IDS:
                found = Items.FindByID(item_id, -1, Player.Backpack.Serial)
                if not found:
                    continue
                if isinstance(found, list):
                    for itm in found:
                        total += max(1, int(getattr(itm, 'Amount', 1)))
                else:
                    total += max(1, int(getattr(found, 'Amount', 1)))
        except Exception:
            pass
        return total
        
    def find_spellbook(self):
        """Find a spellbook in backpack or equipped"""
        self.debug_message("Searching for spellbook...")
        
        # First check equipped items
        for layer in ['LeftHand', 'RightHand']:
            item = Player.GetItemOnLayer(layer)
            if item and item.ItemID == self.spellbook_item_id:  # Spellbook ID
                self.debug_message("Found equipped spellbook", self.success_color)
                return item
        
        # Then check backpack
        items = Items.FindByID(self.spellbook_item_id, -1, Player.Backpack.Serial)  # Spellbook ID
        if not items:
            return None
            
        if not isinstance(items, list):
            items = [items]
            
        if items:
            self.debug_message("Found spellbook in backpack", self.success_color)
            return items[0]
                
        return None
        
    def verify_spellbook(self):
        """Verify the spellbook exists and is accessible"""
        # Get or verify spellbook
        self.current_spellbook = self.find_spellbook()
        if not self.current_spellbook:
            self.debug_message("No spellbook found!", self.error_color)
            return False
            
        if self.current_spellbook.Container != Player.Backpack.Serial and not self.is_item_equipped(self.current_spellbook):
            self.debug_message("Spellbook must be in backpack or equipped!", self.error_color)
            return False
            
        return True
        
    def is_item_equipped(self, item):
        """Return True if the given item is equipped in either hand."""
        try:
            for layer in ['LeftHand', 'RightHand']:
                litem = Player.GetItemOnLayer(layer)
                if litem and litem.Serial == item.Serial:
                    return True
        except Exception:
            pass
        return False
        
    def equip_spellbook(self):
        """Equip the spellbook if not already equipped"""
        if not self.current_spellbook:
            return False
            
        # Check if already equipped
        if self.is_item_equipped(self.current_spellbook):
            return True
            
        # Equip the spellbook
        self.debug_message("Equipping spellbook...")
        Player.EquipItem(self.current_spellbook)
        Misc.Pause(self.equip_delay)
        
        # Verify it was equipped
        if self.is_item_equipped(self.current_spellbook):
            return True
            
        self.debug_message("Failed to equip spellbook!", self.error_color)
        return False
        
    def unequip_spellbook(self):
        """Unequip the spellbook if equipped"""
        if not self.current_spellbook:
            return True
            
        # Check if equipped
        if not self.is_item_equipped(self.current_spellbook):
            return True
            
        # Move back to backpack
        self.debug_message("Unequipping spellbook...")
        Items.Move(self.current_spellbook, Player.Backpack.Serial, 0)
        Misc.Pause(self.equip_delay)
        return True
        
    def has_enough_mana(self):
        """Check if we have enough mana to cast"""
        return Player.Mana >= self.min_mana
        
    def cast_create_food(self):
        """Cast the Create Food spell"""
        if not self.has_enough_mana():
            return False
            
        self.debug_message("Casting Create Food...")
        Spells.CastMagery("Create Food")
        Misc.Pause(self.cast_delay)
        return True
        
    def run_dress_macro(self):
        """Run the Razor Enhanced dress macro"""
        self.debug_message("Running dress macro...")
        Dress.ChangeList("Default")
        Dress.DressStatus()
        Misc.Pause(self.dress_delay)
        return True
        
    def get_item_properties(self, item):
        """Return a set of property strings for an item using multiple APIs.

        Uses serial-based queries to ensure consistent behavior.
        """
        props = set()
        try:
            serial = int(getattr(item, 'Serial', item))
        except Exception:
            serial = item
        # Try to wait for props to be available
        try:
            Items.WaitForProps(int(serial), 750)
        except Exception:
            pass
        # Method 1: full list
        try:
            lst = Items.GetPropStringList(int(serial))
            if lst:
                for p in lst:
                    if p:
                        props.add(str(p))
        except Exception:
            pass
        # Method 2: iterate indices
        try:
            for i in range(0, 64):
                try:
                    s = Items.GetPropStringByIndex(int(serial), i)
                except Exception:
                    s = None
                if not s:
                    break
                props.add(str(s))
        except Exception:
            pass
        return props

    def is_base_spellbook(self, item):
        """True if the spellbook has no modifiers.

        If REQUIRE_BLESSED_FOR_BASE is True, the book must explicitly contain
        the 'Blessed' property and have no modifier keywords.
        Otherwise, allows books with only neutral/no properties.
        """
        if not item or item.ItemID != self.spellbook_item_id:
            return False
        props = self.get_item_properties(item)
        # Verify the item is indeed a spellbook by name or properties
        if REQUIRE_SPELLBOOK_NAME:
            name_ok = False
            try:
                nm = getattr(item, 'Name', '')
                if nm and 'spellbook' in str(nm).lower():
                    name_ok = True
            except Exception:
                pass
            if not name_ok:
                # Check properties for 'Spellbook'
                if any('spellbook' in str(p).lower() for p in props):
                    name_ok = True
            if not name_ok:
                return False
        # If any Durability pattern is present, it's NOT a base book
        for p in list(props):
            if re.search(r"durability\s*\d+\s*/\s*\d+", str(p), re.IGNORECASE):
                return False
        if REQUIRE_BLESSED_FOR_BASE:
            # Must be Blessed and must not contain any modifier keyword
            has_blessed = any("blessed" in str(p).lower() for p in props)
            if not has_blessed:
                return False
            for p in props:
                ps = str(p)
                for kw in self.modifier_keywords:
                    if kw.lower() in ps.lower():
                        return False
            return True
        # Fallback mode: allow empty or only neutral properties
        if not props:
            return True
        all_neutral = True
        for p in list(props):
            ps = str(p)
            for kw in self.modifier_keywords:
                if kw.lower() in ps.lower():
                    return False
            if ps not in self.neutral_properties and ps.strip() != "":
                all_neutral = False
        return all_neutral

    def find_base_spellbook_in_backpack(self):
        """Find a base spellbook (no modifiers) in backpack. Prefer Blessed if multiple."""
        items = Items.FindByID(self.spellbook_item_id, -1, Player.Backpack.Serial)
        if not items:
            return None
        if not isinstance(items, list):
            items = [items]
        base_books = []
        for itm in items:
            if itm.Container != Player.Backpack.Serial:
                continue
            if self.is_base_spellbook(itm):
                base_books.append(itm)
        if not base_books:
            return None
        # Prefer Blessed if available
        for itm in base_books:
            props = self.get_item_properties(itm)
            if any("blessed" in str(p).lower() for p in props):
                return itm
        return base_books[0]

    def equip_basic_spellbook(self):
        """Ensure a base spellbook is equipped. Unequip non-base if necessary."""
        self.debug_message("Ensuring base spellbook is equipped...")
        # Check equipped book
        equipped_book = None
        for layer in ['LeftHand', 'RightHand']:
            item = Player.GetItemOnLayer(layer)
            if item and item.ItemID == self.spellbook_item_id:
                equipped_book = item
                break
        # If equipped and not base, unequip it
        if equipped_book and not self.is_base_spellbook(equipped_book):
            self.debug_message("Unequipping non-base spellbook from hands...")
            # Remember this equipped non-base spellbook to restore later
            try:
                self.previous_spellbook_serial = int(equipped_book.Serial)
            except Exception:
                self.previous_spellbook_serial = None
            try:
                Items.Move(equipped_book, Player.Backpack.Serial, 0)
                Misc.Pause(self.equip_delay)
            except Exception as e:
                self.debug_message(f"Error unequipping book: {e}", self.error_color)
                Misc.Pause(self.equip_delay)
        # If base already equipped, done
        for layer in ['LeftHand', 'RightHand']:
            item = Player.GetItemOnLayer(layer)
            if item and item.ItemID == self.spellbook_item_id and self.is_base_spellbook(item):
                self.current_spellbook = item
                self.debug_message("Base spellbook already equipped.")
                return True
        # Find base in backpack
        base_book = self.find_base_spellbook_in_backpack()
        if not base_book:
            self.debug_message("No base spellbook found in backpack.", self.error_color)
            return False
        self.debug_message("Equipping base spellbook from backpack...")
        try:
            Player.EquipItem(base_book)
            Misc.Pause(self.equip_delay)
        except Exception as e:
            self.debug_message(f"Error equipping base book: {e}", self.error_color)
            return False
        # Verify
        for layer in ['LeftHand', 'RightHand']:
            item = Player.GetItemOnLayer(layer)
            if item and item.Serial == base_book.Serial:
                self.current_spellbook = item
                return True
        self.debug_message("Failed to equip base spellbook!", self.error_color)
        return False

    def re_equip_previous_spellbook(self):
        """Try to re-equip the previously equipped non-base spellbook by serial."""
        if not self.previous_spellbook_serial:
            return False
        try:
            prev = Items.FindBySerial(int(self.previous_spellbook_serial))
        except Exception:
            prev = None
        if not prev:
            return False
        try:
            # Only re-equip if it's still a spellbook and not already equipped
            if getattr(prev, 'ItemID', None) == self.spellbook_item_id and not self.is_item_equipped(prev):
                Player.EquipItem(prev)
                Misc.Pause(self.equip_delay)
                # Verify
                for layer in ['LeftHand', 'RightHand']:
                    it = Player.GetItemOnLayer(layer)
                    if it and int(getattr(it, 'Serial', 0)) == int(self.previous_spellbook_serial):
                        return True
        except Exception:
            return False
        return False
        
    def create_food_sequence(self):
        """Run the complete Create Food sequence"""
        self.debug_message("Starting Create Food sequence...")

        # Optionally ensure we are using a base spellbook first
        if EQUIP_BASE_SPELLBOOK:
            if not self.equip_basic_spellbook():
                # If failed to equip base book, fall back to any spellbook
                self.debug_message("Falling back to any available spellbook...", self.error_color)
                if not self.verify_spellbook() or not self.equip_spellbook():
                    return False
        else:
            # Verify and equip any spellbook
            if not self.verify_spellbook() or not self.equip_spellbook():
                return False
            
        # Cast until out of mana, or caps reached
        casts = 0
        while self.has_enough_mana():
            # Stop if casts cap reached
            if casts >= MAX_CASTS:
                break
            # Stop if item cap reached
            current_total = self.count_restorative_items()
            if current_total >= MAX_MANA_RESTORATIVE_TOTAL:
                self.debug_message(f"Reached restorative item cap: {current_total}/{MAX_MANA_RESTORATIVE_TOTAL}", self.success_color)
                break
            if self.cast_create_food():
                casts += 1
                # Optionally re-check item count and stop early
                current_total = self.count_restorative_items()
                if current_total >= MAX_MANA_RESTORATIVE_TOTAL:
                    self.debug_message(f"Reached restorative item cap: {current_total}/{MAX_MANA_RESTORATIVE_TOTAL}", self.success_color)
                    break
                
        self.debug_message(f"Cast Create Food {casts} times")
        
        # Restore gear: re-equip previous non-base spellbook if we switched
        if not self.re_equip_previous_spellbook():
            # If we couldn't re-equip previous, at least unequip base and run dress macro
            self.unequip_spellbook()
            self.run_dress_macro()
        
        self.debug_message("Create Food sequence complete!", self.success_color)
        return True

def main():
    manager = CreateFoodManager()
    manager.create_food_sequence()

if __name__ == "__main__":
    main()
