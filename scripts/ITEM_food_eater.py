"""
ITEM Food Eater - a Razor Enhanced Python Script for Ultima Online

eat food items until full
- prioritize least amount first
- excludes specific hued items that share food item ids ( mana restorative foods )

HOTKEY:: Y
VERSION::20250925
"""

import time

DEBUG_MODE = False  # Set to False to suppress debug output
PRIORITIZE_LEAST_AMOUNT_FIRST = True  #  eat food with least amount first

# Food Categories with ID
FOOD_ITEMS = {
    "FRUITS": {
        "items": [
            {"name": "Peach", "id": 0x09D2},
            {"name": "Apple", "id": 0x09D0},
            {"name": "Grapes", "id": 0x09D1},
            {"name": "Pear", "id": 0x0994},
            {"name": "Banana", "id": 0x171F},
            {"name": "Pumpkin", "id": 0x0C6A},
            {"name": "Onion", "id": 0x09EC},
            {"name": "Carrot", "id": 0x0C78},
            {"name": "Squash", "id": 0x0C6C},
        ]
    },
    "BAKED_GOODS": {
        "items": [
            {"name": "Muffins", "id": 0x09EB},
            {"name": "Bread Loaf", "id": 0x103B}
        ]
    },
    "MEATS": {
        "items": [
            {"name": "Cheese", "id": 0x097D},
            {"name": "Sausage", "id": 0x09C0},
            {"name": "Cooked Bird", "id": 0x09B7},
            {"name": "Cut of Ribs", "id": 0x09F2},
            {"name": "Ham", "id": 0x09C9},
            {"name": "Leg of Lamb", "id": 0x160A},
            {"name": "Chicken Leg", "id": 0x1608},
            {"name": "Fish Steak", "id": 0x097A},
            {"name": "Fish Steak 2", "id": 0x097B},
            {"name": "Bacon", "id": 0x097E}
        ]
    }
}

# Format: {(ItemID, Hue)} where both are hexidecimal
EXCLUDED_HUED_ITEMS = {
    (0x097B, 0x0825),  # Blue mana fish steak is a mana restorative
    # Apple variants to exclude: Arcane Berries and Tribal Berries
    (0x09D0, 0x0480),  # Arcane Berries (Apple ItemID with hue 0x0480)
    (0x09D0, 0x0006),  # Tribal Berries (Apple ItemID with hue 0x0006)
}

def debug_message(msg, color=67):
    if DEBUG_MODE:
        Misc.SendMessage(f"[FoodEater] {msg}", color)
        
class FoodEater:
    def __init__(self):
        self.debug_color = 67  # Light blue for messages
        self.error_color = 33  # Red for errors
        self.success_color = 68  # Green for success
        self.last_eat_time = 0
        self.eat_delay = 1500  # 1.5 seconds between eating attempts
        
        # Hunger status tracking
        self.is_hungry = True
        self.last_hunger_check = 0
        self.hunger_check_delay = 20000  # Check hunger every 20 seconds
        
        # Fullness tracking
        self.quite_full_count = 0
        self.max_quite_full = 2  # Stop after this many "quite full" messages
        
        # Failure tracking
        self.consecutive_failures = 0
        self.max_failures = 3
        
        # Stats tracking
        self.items_eaten = {}
        
        # Clear journal at start
        Journal.Clear()
        
    def debug_message(self, msg, color=None):
        if not DEBUG_MODE:
            return
        if color is None:
            color = self.debug_color
        Misc.SendMessage(f"[FoodEater] {msg}", color)

    def find_food_in_backpack(self):
        """Find all food items in the backpack"""
        found_items = []
        
        for category, group in FOOD_ITEMS.items():
            for item in group["items"]:
                self.debug_message(f"Searching for {item['name']} (ID: {hex(item['id'])}) in backpack {hex(Player.Backpack.Serial)}")
                items = Items.FindByID(item["id"], -1, Player.Backpack.Serial)
                if items:
                    self.debug_message(f"  Found {item['name']}! ({items})")
                    if not isinstance(items, list):
                        items = [items]
                    for food in items:
                        # Skip exempted hued items
                        try:
                            item_id = int(food.ItemID)
                            hue_val = int(food.Hue)
                        except Exception:
                            # Fallback in case of unexpected types
                            item_id = food.ItemID
                            hue_val = food.Hue
                        if (item_id, hue_val) in EXCLUDED_HUED_ITEMS:
                            self.debug_message(f"  Skipping exempt item {item['name']} (ID {hex(item_id)}, Hue {hex(hue_val)})")
                            continue
                        found_items.append({
                            "item": food,
                            "name": item["name"],
                            "category": category
                        })
                else:
                    self.debug_message(f"  No {item['name']} found.")
        
        return found_items

    def can_eat_food(self):
        """Check if enough time has passed since last eat"""
        current_time = time.time() * 1000
        return (current_time - self.last_eat_time) >= self.eat_delay

    def check_hunger_status(self):
        """Check journal for hunger status"""
        current_time = time.time() * 1000
        if (current_time - self.last_hunger_check) >= self.hunger_check_delay:
            self.last_hunger_check = current_time
            
            # Check for satiated/full messages
            full_messages = [
                "You feel much less hungry",
                "You are simply too full to eat any more",
                "You do not feel hungry",
                "You feel full",
                "You are stuffed!",
                "You manage to eat the food, but you are stuffed!"
            ]
            
            # Check for "quite full" message
            if Journal.Search("You feel quite full after consuming the food"):
                self.quite_full_count += 1
                self.debug_message(f"Quite full count: {self.quite_full_count}/{self.max_quite_full}")
                if self.quite_full_count >= self.max_quite_full:
                    self.is_hungry = False
                    self.debug_message("Reached maximum fullness level!", self.success_color)
                    return False
            
            for msg in full_messages:
                if Journal.Search(msg):
                    self.is_hungry = False
                    self.debug_message("No longer hungry!", self.success_color)
                    return False
                
            # These messages indicate still hungry
            hunger_messages = [
                "You feel extremely hungry",
                "You feel hungry",
                "You could use a bite to eat",
                "Your stomach grumbles"
            ]
            
            for msg in hunger_messages:
                if Journal.Search(msg):
                    self.is_hungry = True
                    self.debug_message(f"Status: {msg}", self.debug_color)
                    Journal.Clear()  # Clear to prevent re-reading same message
                    return True
                    
        return self.is_hungry

    def eat_food_item(self, food_info):
        """Attempt to eat a food item"""
        try:
            if not self.can_eat_food():
                return False
                
            food = food_info["item"]
            name = food_info["name"]
            
            # Verify item is still in backpack
            if food.Container != Player.Backpack.Serial:
                return False
                
            # Use the item (eat it)
            Items.UseItem(food)
            self.last_eat_time = time.time() * 1000
            
            # Track statistics
            if name not in self.items_eaten:
                self.items_eaten[name] = 0
            self.items_eaten[name] += 1
            
            self.debug_message(f"Eating {name}", self.success_color)
            
            # Reset failure counter on successful eat
            self.consecutive_failures = 0
            return True
            
        except Exception as e:
            self.debug_message(f"Error eating {name}: {str(e)}", self.error_color)
            self.consecutive_failures += 1
            return False

    def eat_all_food(self):
        """Find and eat food items until no longer hungry"""
        self.debug_message("Starting auto-eat...")
        
        while self.is_hungry and Player.Connected:
            # Check hunger status
            if not self.check_hunger_status():
                break
                
            # Check failure threshold
            if self.consecutive_failures >= self.max_failures:
                self.debug_message("Too many consecutive failures, stopping", self.error_color)
                break
                
            # Find available food
            food_items = self.find_food_in_backpack()
            
            if not food_items:
                self.debug_message("No food found in backpack", self.error_color)
                self.consecutive_failures += 1
                break
                
            # Sort by least quantity if enabled, otherwise by category
            if PRIORITIZE_LEAST_AMOUNT_FIRST:
                # Count quantity of each food type in backpack
                for food in food_items:
                    # Find all items of this type
                    id_ = food["item"].ItemID
                    items_of_type = Items.FindByID(id_, -1, Player.Backpack.Serial)
                    if items_of_type:
                        if not isinstance(items_of_type, list):
                            items_of_type = [items_of_type]
                        # Count only non-exempt variants
                        qty = 0
                        for it in items_of_type:
                            try:
                                item_id = int(it.ItemID)
                                hue_val = int(it.Hue)
                            except Exception:
                                item_id = it.ItemID
                                hue_val = it.Hue
                            if (item_id, hue_val) in EXCLUDED_HUED_ITEMS:
                                continue
                            qty += 1
                        food["quantity"] = qty
                    else:
                        food["quantity"] = 0
                food_items.sort(key=lambda x: x.get("quantity", 0))
            else:
                food_items.sort(key=lambda x: list(FOOD_ITEMS.keys()).index(x["category"]))
            
            # Try to eat something
            ate_something = False
            for food_info in food_items:
                if self.eat_food_item(food_info):
                    # Check for any 'full' or 'not hungry' message immediately after eating
                    full_messages = [
                        "You feel much less hungry",
                        "You are simply too full to eat any more",
                        "You do not feel hungry",
                        "You feel full",
                        "You are stuffed!",
                        "You manage to eat the food, but you are stuffed!"
                    ]
                    found_full_message = None
                    for msg in full_messages:
                        if Journal.Search(msg):
                            found_full_message = msg
                            break
                    if found_full_message:
                        self.is_hungry = False
                        self.debug_message(f"Fullness message detected: '{found_full_message}' (stopping eating)", self.success_color)
                        Journal.Clear()
                        break
                    ate_something = True
                    Misc.Pause(1000)  # Pause between items
                    break
                    
            if not ate_something:
                self.debug_message("Failed to eat anything", self.error_color)
                self.consecutive_failures += 1
                
            Misc.Pause(500)  # Slow down loop
            
        # Show summary
        self.debug_message(f"Finished eating session", self.success_color)
        if self.items_eaten:
            self.debug_message("Items consumed:")
            for name, count in self.items_eaten.items():
                self.debug_message(f"- {name}: {count}")

def main():
    try:
        debug_message("Starting Food Eater...")
        eater = FoodEater()
        eater.eat_all_food()
    except Exception as e:
        debug_message(f"Error in Food Eater: {str(e)}", 33)

if __name__ == "__main__":
    main()
