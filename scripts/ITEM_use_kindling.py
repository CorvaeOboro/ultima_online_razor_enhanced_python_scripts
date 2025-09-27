"""
ITEM use kindling - a Razor Enhanced Python Script for Ultima Online

use kindling in backpack.
Repeatedly tries to use kindling until amount decreases

TODO: dont camp if already near campfire

HOTKEY:: Z
VERSION::20250923
"""

DEBUG_MODE = False  # Set to False to suppress debug output
KINDLING_ID = 0x0DE1  #  kindling ItemID

def debug_message(msg, color=67):
    if DEBUG_MODE:
        Misc.SendMessage(f"[ITEM_use_kindling] {msg}", color)

class KindlingUser:
    def __init__(self):
        self.debug_color = 67  # Light blue for messages
        self.error_color = 33  # Red for errors
        self.success_color = 68  # Green for success
        self.use_delay = 1000  # 1 second between use attempts
        self.max_attempts = 10  # Maximum attempts to prevent infinite loops
        
        # Clear journal at start
        Journal.Clear()
        
    def debug_message(self, msg, color=None):
        if not DEBUG_MODE:
            return
        if color is None:
            color = self.debug_color
        Misc.SendMessage(f"[ITEM_use_kindling] {msg}", color)

    def count_kindling_in_backpack(self):
        """Count total amount of kindling in backpack"""
        total_count = 0
        
        self.debug_message(f"Searching for kindling (ID: {hex(KINDLING_ID)}) in backpack {hex(Player.Backpack.Serial)}")
        kindling_items = Items.FindByID(KINDLING_ID, -1, Player.Backpack.Serial)
        
        if kindling_items:
            if not isinstance(kindling_items, list):
                kindling_items = [kindling_items]
            
            for kindling in kindling_items:
                amount = kindling.Amount if hasattr(kindling, 'Amount') else 1
                total_count += amount
                self.debug_message(f"  Found kindling stack: {amount} items (Serial: {hex(kindling.Serial)})")
        else:
            self.debug_message("  No kindling found in backpack")
            
        self.debug_message(f"Total kindling count: {total_count}")
        return total_count

    def find_kindling_to_use(self):
        """Find the first available kindling item to use"""
        self.debug_message(f"Looking for kindling to use...")
        kindling_items = Items.FindByID(KINDLING_ID, -1, Player.Backpack.Serial)
        
        if kindling_items:
            if not isinstance(kindling_items, list):
                return kindling_items
            elif len(kindling_items) > 0:
                return kindling_items[0]
        
        return None

    def use_kindling_item(self, kindling_item):
        """Attempt to use a kindling item"""
        try:
            self.debug_message(f"Attempting to use kindling (Serial: {hex(kindling_item.Serial)})")
            
            # Use the kindling item
            Items.UseItem(kindling_item)
            Misc.Pause(self.use_delay)
            
            # Check for success/failure messages in journal
            success_messages = [
                "You place some kindling",
                "You add some kindling",
                "The kindling catches fire",
                "You successfully use the kindling"
            ]
            
            failure_messages = [
                "You cannot use that here",
                "You must be closer",
                "That is too far away",
                "You cannot reach that"
            ]
            
            # Check for success messages
            for msg in success_messages:
                if Journal.Search(msg):
                    self.debug_message(f"Success message detected: '{msg}'", self.success_color)
                    return True
                    
            # Check for failure messages
            for msg in failure_messages:
                if Journal.Search(msg):
                    self.debug_message(f"Failure message detected: '{msg}'", self.error_color)
                    return False
            
            # If no specific message found, assume it worked
            self.debug_message("No specific success/failure message found, assuming success")
            return True
            
        except Exception as e:
            self.debug_message(f"Error using kindling: {str(e)}", self.error_color)
            return False

    def use_kindling_until_consumed(self):
        """Main function to use kindling until amount decreases"""
        self.debug_message("Starting kindling usage...")
        
        # Check initial kindling count
        initial_count = self.count_kindling_in_backpack()
        
        if initial_count == 0:
            self.debug_message("No kindling found in backpack!", self.error_color)
            return False
            
        self.debug_message(f"Initial kindling count: {initial_count}", self.success_color)
        
        attempts = 0
        current_count = initial_count
        
        while current_count >= initial_count and attempts < self.max_attempts and Player.Connected:
            attempts += 1
            self.debug_message(f"Attempt {attempts} of {self.max_attempts}")
            
            # Find kindling to use
            kindling_to_use = self.find_kindling_to_use()
            
            if not kindling_to_use:
                self.debug_message("No kindling available to use!", self.error_color)
                break
                
            # Try to use the kindling
            use_result = self.use_kindling_item(kindling_to_use)
            
            # Wait a moment then check count again
            Misc.Pause(500)
            current_count = self.count_kindling_in_backpack()
            
            if current_count < initial_count:
                self.debug_message(f"Success! Kindling count decreased from {initial_count} to {current_count}", self.success_color)
                self.debug_message(f"Kindling successfully used after {attempts} attempts", self.success_color)
                return True
            else:
                self.debug_message(f"Kindling count unchanged: {current_count} (attempt {attempts})")
                
            # Clear journal for next attempt
            Journal.Clear()
            
        # If we get here, we either hit max attempts or something went wrong
        if attempts >= self.max_attempts:
            self.debug_message(f"Reached maximum attempts ({self.max_attempts}) without success", self.error_color)
        else:
            self.debug_message("Stopped due to connection loss or other issue", self.error_color)
            
        return False

def main():
    try:
        debug_message("Starting Kindling User...")
        user = KindlingUser()
        success = user.use_kindling_until_consumed()
        
        if success:
            debug_message("Kindling usage completed successfully!", 68)
        else:
            debug_message("Kindling usage failed or incomplete", 33)
            
    except Exception as e:
        debug_message(f"Error in Kindling User: {str(e)}", 33)

if __name__ == "__main__":
    main()
