"""
UI Summon Health Monitor - a Razor Enhanced Python Script for Ultima Online

displays health bars for summoned creatures on a consistent custom gump

tracks and displays health bar for summoned creatures on a minimal custom gump
consistent follower healthbars , for temporary summons

HOTKEY:: StartUp
VERSION :: 20250802
"""
from datetime import datetime

DEBUG_MODE = False  # Set to False to disable debug messages
# gump ID= 4294967295  = the max value , randomly select a high number gump so its unique
GUMP_ID =  3229191321

# Global toggle for showing health numbers on the gump
SHOW_HEALTH_NUMBERS = False

class SummonMonitor:
    def __init__(self):
        self.summons = {}  # serial -> summon info
        self.gump_id = GUMP_ID  
        self.update_interval = 2000  
        self.last_update = None  # Set to None to force immediate first update
        self.gump_x = 700  # Gump X position
        self.gump_y = 700  # Gump Y position
        
        # Configuration
        self.summon_base_names = [
            "blood elemental",
            "greater air elemental",
            "greater earth elemental",
            "greater fire elemental",
            "greater water elemental",
            "daemon",
            "earth elemental",
            "fire elemental",
            "water elemental",
            "air elemental"
        ]
        
        # Status effect markers that might appear in names
        self.status_effects = [
            "*grows stronger*",
            "*regens*",
            "(summoned)"
        ]
        
        # Track out-of-range summons
        self.out_of_range_timeout = 3  # Number of missed scans before removal
        
        # Colors for health display
        self.colors = {
            'title': 0x0035,      # Bright gold
            'healthy': 0x0044,    # Green
            'damaged': 0x0021,    # Orange
            'critical': 0x0025,   # Red
            'background': 0x053,  # Dark gray
            'debug': 0x03B2,      # Light blue
            'text': 0x0481        # Bright white
        }
        if DEBUG_MODE:
            Misc.SendMessage("SummonMonitor initialized", self.colors['debug'])

    def debug_message(self, msg):
        """Send a debug message to the game client"""
        if DEBUG_MODE:
            Misc.SendMessage("[Debug] " + str(msg), self.colors['debug'])

    def clean_name(self, name):
        """Remove status effects and normalize name for comparison"""
        name = name.lower()
        # Remove "a " prefix if present
        if name.startswith("a "):
            name = name[2:]
        
        # Remove status effects from name
        for effect in self.status_effects:
            name = name.replace(effect.lower(), "").strip()
            
        return name.strip()

    def is_summon(self, mobile):
        """Check if a mobile is a summoned creature"""
        try:
            # First check the name for summon indicators
            if "(summoned)" in mobile.Name.lower():
                return True
                
            # Check properties for summon indicators
            if mobile.PropsUpdated:  # Only check if properties are up to date
                for prop in mobile.Properties:
                    prop_text = str(prop).lower()
                    if "(summoned)" in prop_text or "summoned creature" in prop_text:
                        return True
            
            # Check if name matches any base summon names
            cleaned_name = self.clean_name(mobile.Name)
            for base_name in self.summon_base_names:
                if base_name in cleaned_name:
                    return True
            
            return False
        except Exception as e:
            self.debug_message(f"Error checking summon status: {str(e)}")
            return False

    def find_summons(self):
        """Find all summoned creatures belonging to the player"""
        try:
            self.debug_message("Searching for summons...")
            
            # Check if player has any followers
            followers_count = Player.Followers
            followers_max = Player.FollowersMax
            self.debug_message(f"Player followers: {followers_count}/{followers_max}")
            
            if followers_count == 0:
                self.debug_message("No followers detected, skipping search")
                # Mark all tracked summons as out of range
                for serial in self.summons:
                    self.summons[serial]['out_of_range'] = True
                    self.summons[serial]['out_of_range_count'] = self.summons[serial].get('out_of_range_count', 0) + 1
                    self.summons[serial]['max_hits'] = 0
                return
            
            filter = Mobiles.Filter()
            filter.Enabled = True
            filter.RangeMax = 30  
            filter.CheckLineOfSight = False
            
            # Set notoriety to find friendly (2) creatures
            filter.Notorieties.Add(2)  # 2 = green/friend
            
            # Debug current player position
            self.debug_message(f"Player position: {Player.Position.X}, {Player.Position.Y}")
            
            # Look for creatures with specific names
            mobiles = Mobiles.ApplyFilter(filter)
            if mobiles:
                self.debug_message(f"Found {len(mobiles)} mobiles in range")
                # Debug each mobile found
                for mobile in mobiles:
                    if mobile:
                        # Calculate distance using Position property
                        player_pos = Player.Position
                        mobile_pos = mobile.Position
                        distance = max(abs(player_pos.X - mobile_pos.X), abs(player_pos.Y - mobile_pos.Y))
                        
                        self.debug_message(f"Mobile found - Name: {mobile.Name}, Distance: {distance}, Notoriety: {mobile.Notoriety}, Serial: {mobile.Serial}")
                        if mobile.PropsUpdated:
                            self.debug_message("Properties:")
                            for prop in mobile.Properties:
                                self.debug_message(f"  - {prop}")
            else:
                self.debug_message("No mobiles found in range")
            
            # Update summons dictionary
            current_serials = []
            found_count = 0
            
            if mobiles:
                for mobile in mobiles:
                    if mobile and mobile.Name:
                        if self.is_summon(mobile):
                            found_count += 1
                            current_serials.append(mobile.Serial)
                            if mobile.Serial not in self.summons:
                                self.debug_message(f"New summon found: {mobile.Name} (HP: {mobile.Hits}/{mobile.HitsMax})")
                                self.summons[mobile.Serial] = {
                                    'name': mobile.Name,
                                    'max_hits': mobile.HitsMax,
                                    'last_hits': mobile.Hits,
                                    'out_of_range': False,
                                    'out_of_range_count': 0
                                }
                            else:
                                # Update last hits and name (in case status changed)
                                self.summons[mobile.Serial]['last_hits'] = mobile.Hits
                                self.summons[mobile.Serial]['name'] = mobile.Name
                                self.summons[mobile.Serial]['max_hits'] = mobile.HitsMax
                                self.summons[mobile.Serial]['out_of_range'] = False
                                self.summons[mobile.Serial]['out_of_range_count'] = 0
                                self.debug_message(f"Updated summon: {mobile.Name} (HP: {mobile.Hits}/{mobile.HitsMax})")
            
            self.debug_message(f"Found {found_count} matching summons")
            
            # Mark summons that are out of range
            for serial in self.summons:
                if serial not in current_serials:
                    self.summons[serial]['out_of_range'] = True
                    self.summons[serial]['out_of_range_count'] = self.summons[serial].get('out_of_range_count', 0) + 1
                    self.summons[serial]['max_hits'] = 0
            
            # Remove summons that have been out of range for too long
            to_remove = []
            for serial, info in self.summons.items():
                if info.get('out_of_range', False) and info.get('out_of_range_count', 0) >= self.out_of_range_timeout:
                    to_remove.append(serial)
            for serial in to_remove:
                name = self.summons[serial]['name']
                self.debug_message(f"Removing disappeared summon: {name}")
                del self.summons[serial]
            
            if len(to_remove) > 0:
                self.debug_message(f"Removed {len(to_remove)} old summons")
            
            self.debug_message(f"Current active summons: {len(self.summons)}")
            
            # Close gump if we have no summons
            if len(self.summons) == 0:
                self.debug_message("No summons found, closing gump but will check again in 5 seconds")
                Gumps.CloseGump(self.gump_id)
        
        except Exception as e:
            Misc.SendMessage(f"Error in find_summons: {str(e)}", self.colors['critical'])

    def get_true_name(self, mobile):
        """Extract the true name from mobile properties"""
        try:
            if mobile.PropsUpdated:
                # First property is usually the true name
                for prop in mobile.Properties:
                    prop_text = str(prop).strip()
                    if prop_text.startswith('a ') or prop_text.startswith('an '):
                        return prop_text
            return mobile.Name
        except Exception as e:
            self.debug_message(f"Error getting true name: {str(e)}")
            return mobile.Name

    def get_health_color(self, current, maximum):
        """Get color based on health percentage"""
        try:
            if maximum <= 0:
                return self.colors['critical']
            
            percentage = (current * 100) / maximum
            if percentage > 75:
                return self.colors['healthy']
            elif percentage > 25:
                return self.colors['damaged']
            else:
                return self.colors['critical']
        except:
            return self.colors['critical']


    def create_gump(self):
        """Create a compact health bar gump with unified background and bars (single gump, like ARPG UI)"""
        try:
            width = 200
            ARPG_SEGMENT_HEIGHT = 16
            height = max(25, len(self.summons) * ARPG_SEGMENT_HEIGHT + 6)  # 2px top/bottom pad + 2px gap
            gd = Gumps.CreateGump(movable=True)
            Gumps.AddPage(gd, 0)
            Gumps.AddBackground(gd, 0, 0, width, height, 30546)
            Gumps.AddAlphaRegion(gd, 0, 0, width, height)
            ARPG_BAR_ART = 5210  # 12x16 pixel bar segment
            ARPG_SEGMENT_WIDTH = 12
            ARPG_SEGMENT_HEIGHT = 16
            ARPG_BAR_WIDTH = 60
            y_offset = 2
            for serial, summon in self.summons.items():
                # If out of range, display as 25/0 or 0/0
                if summon.get('out_of_range', False):
                    current_hits = summon['last_hits']
                    max_hits = 0
                    color = 38  # Bright red for out of range
                    true_name = summon['name'] + " (out of range)"
                else:
                    mobile = Mobiles.FindBySerial(serial)
                    if mobile:
                        true_name = self.get_true_name(mobile)
                    else:
                        true_name = summon['name']
                    current_hits = summon['last_hits']
                    max_hits = summon['max_hits']
                    # Color logic as before
                    health_percent = (current_hits / max_hits) if max_hits > 0 else 0
                    if health_percent >= 0.7:
                        color = 168  # Bright green
                    elif health_percent >= 0.4:
                        color = 53   # Yellow
                    elif health_percent >= 0.2:
                        color = 33   # Red
                    else:
                        color = 38   # Bright red
                num_segments = ARPG_BAR_WIDTH // ARPG_SEGMENT_WIDTH
                filled_segments = int((current_hits / max_hits) * num_segments) if max_hits > 0 else 0
                bar_x = 135
                bar_y = y_offset + 2
                for i in range(num_segments):
                    Gumps.AddImage(gd, bar_x + i * ARPG_SEGMENT_WIDTH, bar_y, ARPG_BAR_ART, 2999)
                for i in range(filled_segments):
                    Gumps.AddImage(gd, bar_x + i * ARPG_SEGMENT_WIDTH, bar_y, ARPG_BAR_ART, color)
                Gumps.AddLabel(gd, 5, y_offset + 2, color, true_name)
                if SHOW_HEALTH_NUMBERS:
                    health_text = f"{current_hits}/{max_hits}"
                    Gumps.AddLabel(gd, bar_x + ARPG_BAR_WIDTH + 8, bar_y, color, health_text)
                y_offset += ARPG_SEGMENT_HEIGHT
            Gumps.SendGump(self.gump_id, Player.Serial, self.gump_x, self.gump_y, gd.gumpDefinition, gd.gumpStrings)
            self.debug_message("Unified gump created and sent")
        except Exception as e:
            Misc.SendMessage(f"Error creating gump: {str(e)}", self.colors['critical'])

    def update(self):
        """Update the summon monitor"""
        try:
            current_time = datetime.now()
            if self.last_update is None:
                time_diff = self.update_interval + 1  # Force first update
            else:
                time_diff = (current_time - self.last_update).total_seconds() * 1000
            
            if time_diff >= self.update_interval:
                self.debug_message("Running update cycle...")
                self.find_summons()
                
                if len(self.summons) > 0:
                    self.create_gump()
                else:
                    self.debug_message("No summons found, skipping gump creation")
                    Gumps.CloseGump(self.gump_id)  # Close gump if no summons
                    
                self.last_update = current_time
                
        except Exception as e:
            Misc.SendMessage("Error in update: " + str(e), self.colors['critical'])

def main():
    try:
        Misc.SendMessage("Starting Summon Health Monitor...", 0x44)
        monitor = SummonMonitor()
        # Force immediate first update to show existing summons
        monitor.update()
        while True:
            monitor.update()
            # If no summons, wait 5 seconds; otherwise, 1 second
            pause_time = 5000 if len(monitor.summons) == 0 else 1000
            Misc.Pause(pause_time)
            
    except Exception as e:
        Misc.SendMessage("Error in main: " + str(e), 0x25)
        raise e

if __name__ == '__main__':
    main()
