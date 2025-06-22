"""
SPELL Create Food - a Razor Enhanced Python script for Ultima Online

Manages the casting of Create Food spell by:
1. Finding and equipping a spellbook from backpack
2. Casting Create Food repeatedly until out of mana

this is specific to custom servers that use mana restoring items like mana mushrooms or mana fish steaks
typically this variant is triggered by equipping a spell book when casting create food

Default make 10

VERSION::20250621
"""

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
        
    def debug(self, message, color=None):
        """Send a debug message to the game client"""
        if color is None:
            color = self.debug_color
        Misc.SendMessage(f"[Food] {message}", color)
        
    def find_spellbook(self):
        """Find a spellbook in backpack or equipped"""
        self.debug("Searching for spellbook...")
        
        # First check equipped items
        for layer in ['LeftHand', 'RightHand']:
            item = Player.GetItemOnLayer(layer)
            if item and item.ItemID == 0x0EFA:  # Spellbook ID
                self.debug("Found equipped spellbook", self.success_color)
                return item
        
        # Then check backpack
        items = Items.FindByID(0x0EFA, -1, Player.Backpack.Serial)  # Spellbook ID
        if not items:
            return None
            
        if not isinstance(items, list):
            items = [items]
            
        if items:
            self.debug("Found spellbook in backpack", self.success_color)
            return items[0]
                
        return None
        
    def verify_spellbook(self):
        """Verify the spellbook exists and is accessible"""
        # Get or verify spellbook
        self.current_spellbook = self.find_spellbook()
        if not self.current_spellbook:
            self.debug("No spellbook found!", self.error_color)
            return False
            
        if self.current_spellbook.Container != Player.Backpack.Serial and not Player.CheckLayer('LeftHand', self.current_spellbook.Serial) and not Player.CheckLayer('RightHand', self.current_spellbook.Serial):
            self.debug("Spellbook must be in backpack or equipped!", self.error_color)
            return False
            
        return True
        
    def equip_spellbook(self):
        """Equip the spellbook if not already equipped"""
        if not self.current_spellbook:
            return False
            
        # Check if already equipped
        if Player.CheckLayer('LeftHand', self.current_spellbook.Serial) or Player.CheckLayer('RightHand', self.current_spellbook.Serial):
            return True
            
        # Equip the spellbook
        self.debug("Equipping spellbook...")
        Player.EquipItem(self.current_spellbook)
        Misc.Pause(self.equip_delay)
        
        # Verify it was equipped
        if Player.CheckLayer('LeftHand', self.current_spellbook.Serial) or Player.CheckLayer('RightHand', self.current_spellbook.Serial):
            return True
            
        self.debug("Failed to equip spellbook!", self.error_color)
        return False
        
    def unequip_spellbook(self):
        """Unequip the spellbook if equipped"""
        if not self.current_spellbook:
            return True
            
        # Check if equipped
        if not Player.CheckLayer('LeftHand', self.current_spellbook.Serial) and not Player.CheckLayer('RightHand', self.current_spellbook.Serial):
            return True
            
        # Move back to backpack
        self.debug("Unequipping spellbook...")
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
            
        self.debug("Casting Create Food...")
        Spells.CastMagery("Create Food")
        Misc.Pause(self.cast_delay)
        return True
        
    def run_dress_macro(self):
        """Run the Razor Enhanced dress macro"""
        self.debug("Running dress macro...")
        Dress.ChangeList("Default")
        Dress.DressStatus()
        Misc.Pause(self.dress_delay)
        return True
        
    def create_food_sequence(self):
        """Run the complete Create Food sequence"""
        self.debug("Starting Create Food sequence...")
        
        # Verify and equip spellbook
        if not self.verify_spellbook() or not self.equip_spellbook():
            return False
            
        # Cast until out of mana
        casts = 0
        while self.has_enough_mana():
            if self.cast_create_food():
                casts += 1
                
        self.debug(f"Cast Create Food {casts} times")
        
        # Unequip and dress
        self.unequip_spellbook()
        self.run_dress_macro()
        
        self.debug("Create Food sequence complete!", self.success_color)
        return True

def main():
    # Create manager and run sequence
    manager = CreateFoodManager()
    manager.create_food_sequence()

if __name__ == "__main__":
    main()
