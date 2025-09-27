"""
UI gump layout preset - a Razor Enhanced Python Script for Ultima Online

Moves ui gumps to specified layout positions

CURRENT LAYOUT =  ui areas on right side and lower side 
Gameplay Window Size = 1509 x 758 
spell icons , counters , and character status info under the gameplay 
right side is map , character , and skills , with backpack just to the left of skills at the bot

Notes : Razor Enhanced API of ClassicUO MoveGump = CUO.MoveGump(serial,x,y)
# 0xFFFFFFF = 4294967295 # max int , make sure gump ids are under this
# in razor enhanced we can use Inspect Gump then close or open the gump in game to get the gump id serial

TODO: 
- core game gumps were not detected , maybe through the gumps.xml we can reference them
- restore closed gumps , the buff icon gump was not detected , an in game macro ToggleBuffIconGump can open it maybe we can send that macro , but its a toggle and we cant detect it
- use check gump open so that we dont need to delay between gump moves if the gump is not open
Check Gump Open = Syntax	Gumps.HasGump( )
- converter function for the hexidecimal , we want to make sure not overlapping existing ids , inspected gumps are hexidecimal 

HOTKEY:: P
VERSION:: 20250924
"""

DEBUG_MODE = False
MOVE_GUMPS = True

GUMP_LAYOUT = {
    # Custom Shard Gumps (Unchained)
    0xafb24ef0: {"name": "Unchained Toolbar", "x": 400, "y": 825},
    0x431beab3: {"name": "Dungeon Progress", "x": 255, "y": 815},
    0x39d3bcad: {"name": "Wilderness Progress", "x": 255, "y": 850},
    0x7d050c60: {"name": "Expedition Progress", "x": 255, "y": 850},
    0x4a3bd2b1: {"name": "chat", "x": 0, "y": 920},
    0xbacf07e2: {"name": "spell proc bar", "x": 400, "y": 645},
    0x7da9a7ba: {"name": "emotes", "x": 400, "y": 645},
    0xdbae5952: {"name": "nature mastery forms", "x": 400, "y": 645},
    0xbf26ed43: {"name": "death mastery rage", "x": 400, "y": 645},
    0xb8108206: {"name": "summoner ritual dark lantern", "x": 400, "y": 645},
    # custom UI gumps 
    0xc671ea51: {"name": "Progress Tracker", "x": 0, "y": 755},
    3411114321: {"name": "Health Bar", "x": 465, "y": 715},
    3229191321: {"name": "Summon Monitor", "x": 790, "y": 720},
    0xc0798c99: {"name": "Summon Monitor", "x": 790, "y": 720},
    0x7a11a12: {"name": "Item Info WAILA", "x": 350, "y": 760},
    3135545776: {"name": "Local Chat", "x": 1500, "y": -20},
    4191917191: {"name": "Action Buttons", "x": 1520, "y": 185},
    0x75A11E6: {"name": "Loot", "x": 350, "y": 810},
    3636346736: {"name": "Durability", "x": 465, "y": 715},
    4191917201: {"name": "Command", "x": 465, "y": 715},
}

RESTORE_CLOSED_GUMPS = False # not working currently
DELAY_MS = 100
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
        return list(GUMP_LAYOUT.keys())
    
    def move_gump_to_preset(self, gump_id):
        """Move a specific gump to its preset location"""
        try:
            layout = GUMP_LAYOUT
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
        layout = GUMP_LAYOUT
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
    
    for gump_id, preset in GUMP_LAYOUT.items():
        manager.debug_message(f"{hex(gump_id)}: {preset['name']} -> ({preset['x']}, {preset['y']})")
    
    manager.debug_message(f"Total configured gumps: {len(GUMP_LAYOUT)}")

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
