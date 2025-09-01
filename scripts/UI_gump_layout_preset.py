"""
UI gump layout preset - a Razor Enhanced Python Script for Ultima Online

Moves custom gumps to a specified layout location

Goal:
custom shard gumps and custom gumps from scripts dont automatically save their location into the settings or profile gumps.xml . 
custom gumps positioning is not stored by the settings like core gumps 
, and  while the player profile settings holds the positions there isnt a LOCK option
 so drit over time from small nudges accumulates . 
 therefore we want to store an external gump position settings file 
 and be able to conditionally arrange elements ( spells , custom gump locations ) 
 we will try to handle this in the custom gump scripts ( positioning themselves on start from a settings file ) , but this might be a good catch all 
 
Razor Enhanced API of ClassicUO MoveGump = CUO.MoveGump(serial,x,y)

TODO: 
- core game gumps were not detected , maybe through the gumps.xml we can reference them
- restore closed gumps , the buff icon gump was not detected , an in game macro ToggleBuffIconGump can open it maybe we can send that macro , but its a toggle and we cant detect it it

HOTKEY:: P
VERSION:: 20250901
"""
DEBUG_MODE = False

MOVE_GUMPS = True
RESTORE_CLOSED_GUMPS = False # not working currently
DELAY_MS = 100

# =============================================================================

GUMP_LOCATIONS = {
    # Custom Shard Gumps (Unchained)
    0xafb24ef0: {"name": "Unchained Toolbar", "x": 400, "y": 825},
    0x431beab3: {"name": "Wilderness Progress", "x": 255, "y": 800},
    0x39d3bcad: {"name": "Deceit Progress", "x": 255, "y": 850},
    0x4a3bd2b1: {"name": "chat", "x": 0, "y": 920},
    0xbacf07e2: {"name": "spell proc bar", "x": 400, "y": 645},
    # custom UI gumps 
    0xc671ea51: {"name": "Progress Tracker", "x": 0, "y": 755},
    3411114321: {"name": "Health Bar", "x": 465, "y": 715},
    3229191321: {"name": "Summon Monitor", "x": 790, "y": 720},
    0x7a11a12: {"name": "Walia Info", "x": 350, "y": 760},
    # other custom gumps
    0xbeefdade: {"name": "Durability percents", "x": 350, "y": 760},
}

# =============================================================================

class GumpLayoutManager:
    def __init__(self):
        self.moved_gumps = []
        self.failed_moves = []
        self.restored_gumps = []
        
    def debug_message(self, message, color=0x40):
        """Send debug message if debug mode is enabled"""
        if DEBUG_MODE:
            Misc.SendMessage(f"[Gump Layout] {message}", color)
    
    def get_all_configured_gumps(self):
        """Get list of all configured gumps"""
        return list(GUMP_LOCATIONS.keys())
    
    def move_gump_to_preset(self, gump_id):
        """Move a specific gump to its preset location"""
        try:
            layout = GUMP_LOCATIONS
            if gump_id not in layout:
                self.debug_message(f"No preset location for gump {hex(gump_id)}", 0x33)
                return False
            
            preset = layout[gump_id]
            target_x = preset["x"]
            target_y = preset["y"]
            gump_name = preset["name"]
            
            self.debug_message(f"Attempting to move {gump_name} ({hex(gump_id)}) to ({target_x}, {target_y})")
            
            # Try to move the gump
            try:
                CUO.MoveGump(gump_id, target_x, target_y)
                self.moved_gumps.append(gump_name)
                self.debug_message(f"Successfully moved {gump_name} to ({target_x}, {target_y})")
                
                Misc.Pause(DELAY_MS)
                return True
                
            except Exception as move_error:
                self.debug_message(f"CUO.MoveGump failed for {gump_name}: {move_error}", 0x25)
                return False
            
        except Exception as e:
            gump_name = layout.get(gump_id, {}).get("name", "Unknown")
            self.debug_message(f"Error moving gump {hex(gump_id)} ({gump_name}): {e}", 0x25)
            self.failed_moves.append(f"{gump_name}: {e}")
            return False
    
    def move_all_gumps(self):
        """Move all configured gumps to their preset locations (force attempt all)"""
        self.debug_message("Starting gump layout preset application...")
        
        all_gumps = self.get_all_configured_gumps()
        layout = GUMP_LOCATIONS
        moved_count = 0
        total_gumps = len(all_gumps)
        
        self.debug_message(f"Processing {total_gumps} configured gumps...")
        
        for i, gump_id in enumerate(all_gumps, 1):
            gump_name = layout[gump_id]["name"]
            self.debug_message(f"Step {i} of {total_gumps}: {gump_name} ({hex(gump_id)})")
            
            if self.move_gump_to_preset(gump_id):
                moved_count += 1
                self.debug_message(f"Step {i} completed successfully")
            else:
                self.debug_message(f"Step {i} failed", 0x25)
            
            if i < total_gumps:  # Don't pause after the last gump
                self.debug_message(f"Waiting before next gump...")
                Misc.Pause(DELAY_MS)
        
        self.debug_message(f"Layout complete: {moved_count} out of {total_gumps} gumps moved", 0x40)
    
    def apply_layout_preset(self):
        """Main function to apply the complete layout preset"""
        self.debug_message("=== Starting Gump Layout Preset ===", 0x44)
        
        # Clear previous results
        self.moved_gumps = []
        self.failed_moves = []
        self.restored_gumps = []
        
        # Move all configured gumps to preset positions
        if MOVE_GUMPS:
            self.move_all_gumps()
        
        # Step 3: Report results
        self.report_results()
    
    def report_results(self):
        """Report the results of the layout operation"""
        self.debug_message("=== Layout Preset Results ===", 0x44)
        
        if self.moved_gumps:
            self.debug_message(f"Successfully moved: {', '.join(self.moved_gumps)}", 0x40)
        
        if self.failed_moves:
            self.debug_message(f"Failed moves: {len(self.failed_moves)}", 0x25)
            for failure in self.failed_moves:
                self.debug_message(f"  - {failure}", 0x25)
        
        if not self.moved_gumps:
            self.debug_message("No gumps were moved", 0x33)

# =============================================================================

def list_configured_gumps():
    """List all configured gumps and their preset positions"""
    manager = GumpLayoutManager()
    manager.debug_message("=== Configured Gumps ===", 0x44)
    
    for gump_id, preset in GUMP_LOCATIONS.items():
        manager.debug_message(f"{hex(gump_id)}: {preset['name']} -> ({preset['x']}, {preset['y']})")
    
    manager.debug_message(f"Total configured gumps: {len(GUMP_LOCATIONS)}")

def reset_layout():
    """Reset all gumps to their preset positions"""
    manager = GumpLayoutManager()
    manager.apply_layout_preset()

# =============================================================================

def main():
    """Main execution function"""
    try:
        manager = GumpLayoutManager()
        manager.apply_layout_preset()
        
    except Exception as e:
        Misc.SendMessage(f"[Gump Layout] Critical error: {e}", 0x25)

if __name__ == "__main__":
    main()
