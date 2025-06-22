"""
UI Player Status Bars - a Razor Enhanced Python Script for Ultima Online

Creates a custom gump showing health, mana, and stamina in a ARPG-style horizontal bar layout.
Features:
- Horizontal progress bars for health, mana, 
- Dynamic color intensity based on current values

TODO:
bandage duration 

VERSION :: 20250621
"""

import time
import re
from System.Collections.Generic import List

# gump ID= 4294967295  = the max value , randomly select a high number gump so its unique
GUMP_ID =  3411114321

# Art IDs for gump elements
GUMP_ART = {
    "BACKGROUND": 3500,  # Standard gump background
    "BAR": 5210,        # 12x16 pixel bar segment
    "SMALL_BAR": 9350,  # Smaller bar for stamina
}

# Bar segment dimensions
SEGMENT_DIMENSIONS = {
    "LARGE": {
        "WIDTH": 12,   # Pixels wide
        "HEIGHT": 16,  # Pixels tall
    },
    "SMALL": {
        "WIDTH": 4,    # Pixels wide for stamina
        "HEIGHT": 8,   # Pixels tall for stamina
    }
}

# Status effect configurations
STATUS_EFFECTS = {
    "bandage": {
        "duration": 7000,  # 7 seconds in ms
        "color": 168,     # Green
        "flash_color": 53, # Yellow
        "pattern": r"You begin applying the bandages",
    },
    "poison": {
        "duration": 30000,  # 30 seconds in ms
        "color": 63,       # Purple
        "pattern": r"You have been poisoned",
    },
    "bleed": {
        "duration": 15000,  # 15 seconds in ms
        "color": 33,       # Red
        "pattern": r"You are bleeding",
    }
}

class MobaStatusBars:
    def __init__(self):
        # UI dimensions
        self.bar_width = 204  # Adjusted to be multiple of segment width (17 segments * 12 pixels)
        self.bar_height = 16  # Match large segment height
        self.stamina_height = 8  # Smaller height for stamina
        self.status_bar_height = 6  # Height for status effect bars
        self.spacing = 1  # Minimal spacing
        
        # Position (centered in lower screen)
        self.x = Player.Position.X - (self.bar_width // 2)  # Center horizontally
        self.y = 600  # Lower screen area
        
        # Gump ID (using unique range to avoid conflicts)
        self.gump_id = GUMP_ID
        
        # Update timing
        self.last_update = 0
        self.update_delay = 100  # 100ms for smooth updates
        self.last_journal_check = 0
        self.journal_check_delay = 1000  # Check journal every second
        self.active = False
        
        # Status effects tracking
        self.status_effects = {
            "bandage": {"active": False, "start_time": 0},
            "poison": {"active": False, "start_time": 0},
            "bleed": {"active": False, "start_time": 0}
        }
        
        # Art IDs from global config
        self.art = {
            "background": GUMP_ART["BACKGROUND"],
            "bar": {
                "large": GUMP_ART["BAR"],
                "small": GUMP_ART["SMALL_BAR"]
            }
        }
        
        # Color configurations for bars and text
        self.colors = {
            "health": {
                "high": 168,     # Bright Green
                "medium": 53,    # Yellow
                "low": 33,       # Red
                "critical": 38   # Bright Red
            },
            "mana": {
                "fill": 88,     # Light Blue
                "text": 88      # Light Blue
            },
            "stamina": {
                "fill": 2118,   # Desaturated orange
            },
            "text": 2000,        # White
            "text_border": 0     # Pure black
        }
        
        # Colors for segments
        self.segment_colors = {
            "filled": {
                "health": lambda pct: (
                    self.colors["health"]["high"] if pct >= 0.7 else
                    self.colors["health"]["medium"] if pct >= 0.4 else
                    self.colors["health"]["low"] if pct >= 0.2 else
                    self.colors["health"]["critical"]
                ),
                "mana": lambda _: self.colors["mana"]["fill"],
                "stamina": lambda _: self.colors["stamina"]["fill"]
            },
            "depleted": 2999,  # Very dark grey hue for unfilled segments
            "changed": 32  # Bright red for recently changed segments
        }
        
        # Track previous values for change detection (only health and mana)
        self.previous_values = {
            "health": 0,
            "mana": 0
        }
        
        # Track recently changed segments (only health and mana)
        self.changed_segments = {
            "health": [],
            "mana": []
        }
        self.change_time = 500  # Time in ms to show changed segments
        
        # Thresholds for health colors
        self.thresholds = {
            "critical": 0.2,  # 20% health
            "low": 0.4,       # 40% health
            "medium": 0.7     # 70% health
        }
        
    def debug(self, message, color=68):
        """Send debug message"""
        Misc.SendMessage(f"[MobaUI] {message}", color)
        
    def get_bar_color(self, current, maximum, resource_type):
        """Get color based on current value percentage"""
        percentage = current / maximum if maximum > 0 else 0
        colors = self.colors[resource_type]
        
        if resource_type == "health":
            if percentage <= self.thresholds["critical"]:
                return colors["critical"]
            elif percentage <= self.thresholds["low"]:
                return colors["low"]
            elif percentage <= self.thresholds["medium"]:
                return colors["medium"]
            else:
                return colors["high"]
                
        if resource_type == "exp":
            return colors[resource_type]  # Use specific exp type color
            
        return colors["fill"]
            
    def draw_segmented_bar(self, gump, x, y, width, height, current, maximum, bar_type):
        """Draw a bar made of individual segments that show resource level"""
        # Use appropriate art and dimensions
        is_small = bar_type == "stamina"
        art = self.art["bar"]["small"] if is_small else self.art["bar"]["large"]
        dims = SEGMENT_DIMENSIONS["SMALL"] if is_small else SEGMENT_DIMENSIONS["LARGE"]
        
        # Calculate segments
        num_segments = width // dims["WIDTH"]
        filled_segments = int((current / maximum) * num_segments) if maximum > 0 else 0
        
        # Get current time for change animation (only for health and mana)
        current_time = time.time() * 1000
        
        # Check for changes (only for health and mana)
        if bar_type in ["health", "mana"]:
            previous = self.previous_values[bar_type]
            if current != previous:
                if current < previous:  # Resource decreased
                    start_seg = filled_segments
                    end_seg = int((previous / maximum) * num_segments)
                    self.changed_segments[bar_type].extend([
                        {"segment": i, "time": current_time}
                        for i in range(start_seg, end_seg)
                    ])
                self.previous_values[bar_type] = current
            
            # Clean up old changed segments
            self.changed_segments[bar_type] = [
                change for change in self.changed_segments[bar_type]
                if current_time - change["time"] < self.change_time
            ]
        
        # Calculate percentage for health color
        percentage = current / maximum if maximum > 0 else 0
        
        # Draw segments
        for i in range(num_segments):
            segment_x = x + i * dims["WIDTH"]
            
            # Determine segment color
            if i < filled_segments:
                # For health, use the same color for all filled segments based on percentage
                if bar_type == "health":
                    color = self.segment_colors["filled"][bar_type](percentage)
                else:
                    color = self.segment_colors["filled"][bar_type](i / num_segments)
            else:
                # Check if this is a recently changed segment (only for health and mana)
                if bar_type in ["health", "mana"]:
                    is_changed = any(
                        change["segment"] == i 
                        for change in self.changed_segments[bar_type]
                    )
                    color = self.segment_colors["changed"] if is_changed else self.segment_colors["depleted"]
                else:
                    color = self.segment_colors["depleted"]
            
            # Draw segment
            Gumps.AddImage(gump, int(segment_x), int(y), art, color)
            
    def check_journal(self):
        """Check journal for status effect messages"""
        current_time = time.time() * 1000
        if (current_time - self.last_journal_check) < self.journal_check_delay:
            return
            
        self.last_journal_check = current_time
        
        # Get journal entries
        entries = Journal.GetTextByType("Regular")
        if not entries:
            return
            
        # Check for status effect triggers
        for entry in entries:
            for effect, config in STATUS_EFFECTS.items():
                if re.search(config["pattern"], entry, re.IGNORECASE):
                    self.status_effects[effect] = {
                        "active": True,
                        "start_time": current_time
                    }
                    
    def draw_status_bar(self, gump, x, y, width, height, effect_type):
        """Draw a status effect progress bar"""
        current_time = time.time() * 1000
        effect = self.status_effects[effect_type]
        config = STATUS_EFFECTS[effect_type]
        
        if not effect["active"]:
            return
            
        # Calculate progress
        elapsed = current_time - effect["start_time"]
        if elapsed >= config["duration"]:
            effect["active"] = False
            return
            
        progress = 1.0 - (elapsed / config["duration"])
        filled_width = int(width * progress)
        
        # For bandages, flash near completion
        color = config["color"]
        if effect_type == "bandage" and progress < 0.15:  # Flash in last 15%
            if int(current_time / 200) % 2:  # Flash every 200ms
                color = config["flash_color"]
        
        # Draw background (darker version of effect color)
        Gumps.AddImageTiled(gump, x, y, width, height, 
                           self.art["bar"]["small"], 
                           self.segment_colors["depleted"])
        
        # Draw filled portion
        if filled_width > 0:
            Gumps.AddImageTiled(gump, x, y, filled_width, height,
                               self.art["bar"]["small"], color)
            
    def create_gump(self):
        """Create the status bars gump"""
        try:
            # Create new gump with movable=True
            gump = Gumps.CreateGump(movable=True)
            
            # Add page
            Gumps.AddPage(gump, 0)
            
            # Calculate total dimensions including status bars
            total_width = self.bar_width + 4  # Minimal padding
            status_section_height = (len(STATUS_EFFECTS) * 
                                   (self.status_bar_height + self.spacing))
            total_height = (self.bar_height * 2 + 
                          self.stamina_height +
                          status_section_height +
                          self.spacing * 4 + 4)  # Minimal padding
            
            # Add background with pure black tint
            Gumps.AddBackground(gump, 0, 0, total_width, total_height, self.art["background"])
            Gumps.AddImage(gump, 0, 0, self.art["background"], 0)  # Pure black tint
            Gumps.AddAlphaRegion(gump, 0, 0, total_width, total_height)
            
            # Health bar
            y_pos = 5
            self.draw_segmented_bar(gump, 5, y_pos, self.bar_width, self.bar_height, 
                                  Player.Hits, Player.HitsMax, "health")
            # Health value with color based on percentage
            health_text = str(Player.Hits)
            text_x = (self.bar_width // 2) - (len(health_text) * 4)
            Gumps.AddLabel(gump, text_x + 1, y_pos + 2, 
                          self.colors["text_border"], health_text)
            Gumps.AddLabel(gump, text_x, y_pos + 1, 
                          self.get_bar_color(Player.Hits, Player.HitsMax, "health"), health_text)
            
            # Mana bar
            y_pos += self.bar_height + self.spacing
            self.draw_segmented_bar(gump, 5, y_pos, self.bar_width, self.bar_height,
                                  Player.Mana, Player.ManaMax, "mana")
            # Mana value in blue
            mana_text = str(Player.Mana)
            text_x = (self.bar_width // 2) - (len(mana_text) * 4)
            Gumps.AddLabel(gump, text_x + 1, y_pos + 2, 
                          self.colors["text_border"], mana_text)
            Gumps.AddLabel(gump, text_x, y_pos + 1, 
                          self.colors["mana"]["text"], mana_text)
            
            # Stamina bar (no text)
            y_pos += self.bar_height + self.spacing
            self.draw_segmented_bar(gump, 5, y_pos, self.bar_width, self.stamina_height,
                                  Player.Stam, Player.StamMax, "stamina")
            
            # Status effect bars
            y_pos += self.stamina_height + self.spacing
            for effect in STATUS_EFFECTS:
                self.draw_status_bar(gump, 5, y_pos, self.bar_width, 
                                   self.status_bar_height, effect)
                y_pos += self.status_bar_height + self.spacing
            
            # Send the gump
            Gumps.SendGump(self.gump_id, Player.Serial, self.x, self.y, 
                          gump.gumpDefinition, gump.gumpStrings)
            return True
            
        except Exception as e:
            self.debug(f"Error creating gump: {str(e)}")
            return False
            
    def update(self):
        """Update the gump display"""
        try:
            current_time = time.time() * 1000
            if (current_time - self.last_update) >= self.update_delay:
                self.check_journal()  # Check for status updates
                self.last_update = current_time
                self.create_gump()
                    
        except Exception as e:
            self.debug(f"Error updating: {str(e)}")
            
    def start(self):
        """Start the UI update loop"""
        try:
            self.debug("Starting MOBA-style status bars...")
            
            self.active = True
            
            while self.active and Player.Connected:
                self.update()
                Misc.Pause(50)  # Short pause for smooth updates
                
        except Exception as e:
            self.debug(f"Error in main loop: {str(e)}")
            self.stop()
            
    def stop(self):
        """Stop the UI and clean up"""
        self.active = False
        Gumps.CloseGump(self.gump_id)
        self.debug("Stopped MOBA-style status bars")

def main():
    ui = MobaStatusBars()
    ui.start()

if __name__ == "__main__":
    main()
