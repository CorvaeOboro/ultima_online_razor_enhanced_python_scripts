"""
SPELL Create Food - a Razor Enhanced Python script for Ultima Online

cast the Create Food spell to summon a mana restorative item
Finds and equips a blessed base spellbook from backpack or hands
Casts Create Food repeatedly until 20 items are created

common to custom shards create food will produce mana restoring items if cast while holding a spellbook

TODO: this maybe could be merged with ready check script , if not enough mana restorative then create it

HOTKEY:: None 
VERSION::20250918
"""

DEBUG_MODE = False  # Controls whether debug_message outputs to the client

EQUIP_BASE_SPELLBOOK = True # When True, will ensure a blessed base spellbook is equipped before casting

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
        # Previously equipped (non-blessed) spellbook to restore after sequence
        self.previous_spellbook_serial = None

        # Spellbook detection configuration
        self.spellbook_item_id = 0x0EFA
        
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
        
    def is_blessed_spellbook(self, item):
        """Return True if item is a blessed spellbook named 'Spellbook'."""
        try:
            if not item or item.ItemID != self.spellbook_item_id:
                return False
            # Name check (fallback)
            name_ok = False
            try:
                name = getattr(item, 'Name', None)
                if name:
                    name_ok = 'spellbook' in name.lower()
            except Exception:
                name_ok = False
            # Properties check for 'Blessed'
            blessed_ok = False
            try:
                props = Items.GetPropStringList(item)
                if props:
                    blessed_ok = any('blessed' in p.lower() for p in props)
            except Exception:
                blessed_ok = False
            return name_ok and blessed_ok
        except Exception:
            return False

    def find_best_spellbook(self):
        """Find the best spellbook to use: prefer blessed 'Spellbook' in hands, else in backpack, else any equipped spellbook."""
        candidates = []
        # Hands
        left = Player.GetItemOnLayer("LeftHand")
        right = Player.GetItemOnLayer("RightHand")
        for itm in [left, right]:
            if itm and itm.ItemID == self.spellbook_item_id:
                candidates.append(itm)
        # Backpack
        try:
            bp = Items.FindBySerial(Player.Backpack.Serial)
            for itm in (bp.Contains if bp and bp.Contains else []):
                if itm and itm.ItemID == self.spellbook_item_id:
                    candidates.append(itm)
        except Exception:
            pass
        if not candidates:
            return None
        # Prefer blessed + named
        blessed_named = [it for it in candidates if self.is_blessed_spellbook(it)]
        if blessed_named:
            return blessed_named[0]
        # Else prefer any in hands
        for it in [left, right]:
            if it and it in candidates:
                return it
        # Else first found
        return candidates[0]

    def equip_basic_spellbook(self):
        """Ensure a blessed base spellbook is equipped. Unequip non-blessed if necessary."""
        self.debug_message("Ensuring blessed base spellbook is equipped...")
        # Check equipped book
        equipped_book = None
        for layer in ['LeftHand', 'RightHand']:
            item = Player.GetItemOnLayer(layer)
            if item and item.ItemID == self.spellbook_item_id:
                equipped_book = item
                break
        # If equipped and not blessed, unequip it
        if equipped_book and not self.is_blessed_spellbook(equipped_book):
            self.debug_message("Unequipping non-blessed spellbook from hands...")
            # Remember this equipped non-blessed spellbook to restore later
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
        # If blessed already equipped, done
        for layer in ['LeftHand', 'RightHand']:
            item = Player.GetItemOnLayer(layer)
            if item and item.ItemID == self.spellbook_item_id and self.is_blessed_spellbook(item):
                self.current_spellbook = item
                self.debug_message("Blessed base spellbook already equipped.")
                return True
        # Find blessed spellbook using find_best_spellbook
        blessed_book = self.find_best_spellbook()
        if not blessed_book:
            self.debug_message("No blessed spellbook found.", self.error_color)
            return False
        # If it's already equipped, we're done
        if self.is_item_equipped(blessed_book):
            self.current_spellbook = blessed_book
            return True
        # Otherwise equip it
        self.debug_message("Equipping blessed spellbook from backpack...")
        try:
            Player.EquipItem(blessed_book)
            Misc.Pause(self.equip_delay)
        except Exception as e:
            self.debug_message(f"Error equipping blessed book: {e}", self.error_color)
            return False
        # Verify
        for layer in ['LeftHand', 'RightHand']:
            item = Player.GetItemOnLayer(layer)
            if item and item.Serial == blessed_book.Serial:
                self.current_spellbook = item
                return True
        self.debug_message("Failed to equip blessed spellbook!", self.error_color)
        return False

    def re_equip_previous_spellbook(self):
        """Try to re-equip the previously equipped non-blessed spellbook by serial."""
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
