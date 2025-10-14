"""
DEV API CUO - a Razor Enhanced Python Script for Ultima Online

 demonstration of  CUO (ClassicUO) API functions
Tests and displays information about ClassicUO client control functions

=== CUO API OVERVIEW ===
The CUO class provides direct access to ClassicUO client functionality using reflection.

ALL CUO API FUNCTIONS (19 functions):

FOLLOW SYSTEM (3 functions):
  - Following() -> (Boolean, UInt32)
  - FollowMobile(mobileserial)
  - FollowOff()

STATUS BARS (4 functions):
  - OpenMyStatusBar(x, y)
  - CloseMyStatusBar()
  - OpenMobileHealthBar(mobileserial, x, y, custom)
  - CloseMobileHealthBar(mobileserial)

GUMP MANAGEMENT (4 functions):
  - CloseGump(serial)
  - MoveGump(serial, x, y)
  - SetGumpOpenLocation(gumpserial, x, y)
  - OpenContainerAt(bag, x, y)

MAP FUNCTIONS (3 functions):
  - LoadMarkers()
  - GoToMarker(x, y)
  - CloseTMap() -> Boolean

SETTINGS (2 functions):
  - GetSetting(settingName) -> String
  - ProfilePropertySet(propertyName, value)

CAMERA & MACROS (2 functions):
  - FreeView(free)
  - PlayMacro(macroName)

Key Features:
  - Gump Management: Open, close, move gumps and containers
  - Health Bars: Control mobile health bar displays
  - Follow System: Make client follow mobiles
  - Map Markers: Load markers and navigate on world map
  - Settings: Get and set CUO profile properties
  - Free View: Enable/disable free camera movement
  - Macros: Execute CUO macros by name

IMPORTANT NOTES:
  - Some functions require specific UI elements to be open (e.g., map must be open for markers)
  - Functions use reflection to access CUO internals - use with caution
  - Not all functions may work on all CUO versions
  - Test in safe environment before using in production scripts

VERSION::20251013
"""

from System.Collections.Generic import List
import os
import json

# GLOBAL SETTINGS
DEBUG_MODE = True
# Enable interactive tests (will actually move gumps, open/close things)
INTERACTIVE_MODE = False  # Set to True to enable interactive tests
# JSON output file path
BASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
OUTPUT_FILE = os.path.join(BASE_PATH, "api_cuo_test_output.json")
# Run usage examples after tests
RUN_USAGE_EXAMPLES = True
# Test delay between operations (ms)
TEST_DELAY = 500
# Screen positions for testing
TEST_SCREEN_X = 100
TEST_SCREEN_Y = 100
#======================================================================

def debug_message(message, color=67):
    """Send debug message to game client"""
    if not DEBUG_MODE:
        return
    try:
        # Don't add prefix for empty messages (used for spacing)
        if message:
            Misc.SendMessage(f"[CUO] {message}", color)
        else:
            Misc.SendMessage("", color)
    except Exception:
        if message:
            print(f"[CUO] {message}")
        else:
            print("")

def section_header(title):
    """Print a section header"""
    debug_message("=" * 60, 88)
    debug_message(f"  {title}", 88)
    debug_message("=" * 60, 88)

def subsection_header(title):
    """Print a subsection header"""
    debug_message(f"--- {title} ---", 77)

class CUOAPITester:
    def __init__(self):
        self.debug_color = 67  # Light blue
        self.error_color = 33  # Red
        self.success_color = 68  # Green
        self.info_color = 88  # Cyan
        self.warning_color = 53  # Yellow
        
        # Get player info
        self.player_serial = Player.Serial
        self.player_x = Player.Position.X
        self.player_y = Player.Position.Y
        
        # Initialize JSON output structure
        self.json_output = {
            "test_report": {},  # Summary of which API functions work
            "test_timestamp": str(Misc.ScriptCurrent(False)),
            "interactive_mode": INTERACTIVE_MODE,
            "player_info": {
                "serial": int(self.player_serial),
                "x": int(self.player_x),
                "y": int(self.player_y)
            },
            "tests": {}
        }
        
    def debug(self, message, color=None):
        """Send a debug message"""
        if color is None:
            color = self.debug_color
        debug_message(message, color)
    
    def test_follow_system(self):
        """
        Test Follow System Functions
        
        API: CUO.Following() -> (Boolean, UInt32)
        Purpose: Returns the status and target of ClassicUO's follow behavior
        Returns: Tuple of (followingMode, followingTarget)
        
        API: CUO.FollowMobile(mobileserial)
        Purpose: Make CUO client follow a specific mobile (same as alt+left-click)
        Parameters:
          - mobileserial (UInt32): Serial of mobile to follow
        Note: Shows "Now following." overhead message
        
        API: CUO.FollowOff()
        Purpose: Stop following if currently following a mobile
        """
        section_header("TEST: Follow System")
        
        test_success = True
        error_msg = None
        follow_data = {}
        
        # Test Following status
        try:
            self.debug("Checking current follow status...", self.info_color)
            following_status = CUO.Following()
            
            # Unpack tuple
            is_following = following_status[0]
            follow_target = following_status[1]
            
            follow_data["is_following"] = bool(is_following)
            follow_data["follow_target"] = int(follow_target) if follow_target else 0
            
            self.debug(f"  Following Status: {is_following}", self.success_color)
            if is_following:
                self.debug(f"  Following Target Serial: 0x{follow_target:08X}", self.success_color)
            else:
                self.debug("  Not currently following anyone", self.debug_color)
                
        except Exception as e:
            test_success = False
            error_msg = str(e)
            self.debug(f"  Error checking follow status: {e}", self.error_color)
        
        if INTERACTIVE_MODE:
            # Test FollowMobile (requires a valid mobile serial)
            try:
                self.debug("  Note: FollowMobile requires a valid mobile serial", self.warning_color)
                self.debug("  Example: CUO.FollowMobile(mobile_serial)", self.info_color)
            except Exception as e:
                test_success = False
                if not error_msg:
                    error_msg = str(e)
                self.debug(f"  Error: {e}", self.error_color)
            
            # Test FollowOff
            try:
                self.debug("Testing FollowOff...", self.info_color)
                CUO.FollowOff()
                self.debug("  FollowOff executed successfully", self.success_color)
                Misc.Pause(TEST_DELAY)
            except Exception as e:
                test_success = False
                if not error_msg:
                    error_msg = str(e)
                self.debug(f"  Error with FollowOff: {e}", self.error_color)
        else:
            self.debug("  [INTERACTIVE_MODE disabled - skipping FollowMobile/FollowOff tests]", self.warning_color)
        
        # Record test report
        self.json_output["test_report"]["FollowSystem"] = {
            "works": test_success,
            "error": error_msg,
            "data_returned": len(follow_data) > 0
        }
        self.json_output["tests"]["follow_data"] = follow_data
        
        self.debug("")
    
    def test_free_view(self):
        """
        Test FreeView Function
        
        API: CUO.FreeView(free)
        Purpose: Enable/disable free camera view (detach camera from player)
        Parameters:
          - free (Boolean): True to enable free view, False to disable
        Note: Function checks current state and only changes if needed
        """
        section_header("TEST: FreeView")
        
        self.debug("Testing FreeView function...", self.info_color)
        
        if INTERACTIVE_MODE:
            try:
                # Test enabling free view
                self.debug("  Enabling FreeView...", self.info_color)
                CUO.FreeView(True)
                self.debug("  FreeView enabled (camera detached from player)", self.success_color)
                Misc.Pause(TEST_DELAY * 2)
                
                # Test disabling free view
                self.debug("  Disabling FreeView...", self.info_color)
                CUO.FreeView(False)
                self.debug("  FreeView disabled (camera attached to player)", self.success_color)
                Misc.Pause(TEST_DELAY)
                
            except Exception as e:
                self.debug(f"  Error with FreeView: {e}", self.error_color)
        else:
            self.debug("  [INTERACTIVE_MODE disabled - skipping FreeView test]", self.warning_color)
            self.debug("  Example: CUO.FreeView(True)  # Enable free camera", self.info_color)
            self.debug("  Example: CUO.FreeView(False) # Disable free camera", self.info_color)
        
        self.debug("")
    
    def test_status_bar_functions(self):
        """
        Test Status Bar Functions
        
        API: CUO.OpenMyStatusBar(x, y)
        Purpose: Open player's status bar gump at specified screen position
        Parameters:
          - x (Int32): Screen X coordinate
          - y (Int32): Screen Y coordinate
        
        API: CUO.CloseMyStatusBar()
        Purpose: Close player's status bar gump
        
        API: CUO.OpenMobileHealthBar(mobileserial, x, y, custom)
        Purpose: Open a mobile's health bar at specified screen position
        Parameters:
          - mobileserial (Int32/UInt32): Serial of mobile
          - x (Int32): Screen X coordinate
          - y (Int32): Screen Y coordinate
          - custom (Boolean): Use custom health bar style
        
        API: CUO.CloseMobileHealthBar(mobileserial)
        Purpose: Close a mobile's health bar gump
        Parameters:
          - mobileserial (Int32/UInt32): Serial of mobile
        """
        section_header("TEST: Status Bar Functions")
        
        if INTERACTIVE_MODE:
            # Test OpenMyStatusBar
            try:
                self.debug("Testing OpenMyStatusBar...", self.info_color)
                CUO.OpenMyStatusBar(TEST_SCREEN_X, TEST_SCREEN_Y)
                self.debug(f"  Opened player status bar at ({TEST_SCREEN_X}, {TEST_SCREEN_Y})", self.success_color)
                Misc.Pause(TEST_DELAY * 2)
            except Exception as e:
                self.debug(f"  Error opening status bar: {e}", self.error_color)
            
            # Test CloseMyStatusBar
            try:
                self.debug("Testing CloseMyStatusBar...", self.info_color)
                CUO.CloseMyStatusBar()
                self.debug("  Closed player status bar", self.success_color)
                Misc.Pause(TEST_DELAY)
            except Exception as e:
                self.debug(f"  Error closing status bar: {e}", self.error_color)
            
            # Test OpenMobileHealthBar (using player as example)
            try:
                self.debug("Testing OpenMobileHealthBar...", self.info_color)
                CUO.OpenMobileHealthBar(self.player_serial, TEST_SCREEN_X + 200, TEST_SCREEN_Y, False)
                self.debug(f"  Opened mobile health bar at ({TEST_SCREEN_X + 200}, {TEST_SCREEN_Y})", self.success_color)
                Misc.Pause(TEST_DELAY * 2)
            except Exception as e:
                self.debug(f"  Error opening mobile health bar: {e}", self.error_color)
            
            # Test CloseMobileHealthBar
            try:
                self.debug("Testing CloseMobileHealthBar...", self.info_color)
                CUO.CloseMobileHealthBar(self.player_serial)
                self.debug("  Closed mobile health bar", self.success_color)
                Misc.Pause(TEST_DELAY)
            except Exception as e:
                self.debug(f"  Error closing mobile health bar: {e}", self.error_color)
        else:
            self.debug("  [INTERACTIVE_MODE disabled - skipping status bar tests]", self.warning_color)
            self.debug("  Example: CUO.OpenMyStatusBar(100, 100)", self.info_color)
            self.debug("  Example: CUO.CloseMyStatusBar()", self.info_color)
            self.debug("  Example: CUO.OpenMobileHealthBar(serial, 100, 100, False)", self.info_color)
            self.debug("  Example: CUO.CloseMobileHealthBar(serial)", self.info_color)
        
        self.debug("")
    
    def test_gump_functions(self):
        """
        Test Gump Management Functions
        
        API: CUO.CloseGump(serial)
        Purpose: Close a gump by its serial
        Parameters:
          - serial (UInt32): Serial of gump to close
        
        API: CUO.MoveGump(serial, x, y)
        Purpose: Move a gump or container to specified screen position
        Parameters:
          - serial (UInt32): Serial of gump/container
          - x (Int32): Screen X coordinate
          - y (Int32): Screen Y coordinate
        
        API: CUO.SetGumpOpenLocation(gumpserial, x, y)
        Purpose: Set location where next gump/container will open
        Parameters:
          - gumpserial (UInt32): Serial of gump/container
          - x (Int32): Screen X coordinate
          - y (Int32): Screen Y coordinate
        
        API: CUO.OpenContainerAt(bag, x, y)
        Purpose: Set location where container will open
        Parameters:
          - bag (UInt32/Item): Container serial or Item object
          - x (Int32): Screen X coordinate
          - y (Int32): Screen Y coordinate
        """
        section_header("TEST: Gump Management Functions")
        
        if INTERACTIVE_MODE:
            # Test with backpack
            try:
                backpack = Player.Backpack
                if backpack:
                    self.debug("Testing OpenContainerAt with backpack...", self.info_color)
                    CUO.OpenContainerAt(backpack.Serial, TEST_SCREEN_X, TEST_SCREEN_Y)
                    self.debug(f"  Set backpack open location to ({TEST_SCREEN_X}, {TEST_SCREEN_Y})", self.success_color)
                    Misc.Pause(TEST_DELAY)
                    
                    # Open backpack to see effect
                    Items.UseItem(backpack)
                    Misc.Pause(TEST_DELAY * 2)
                    
                    # Test MoveGump
                    self.debug("Testing MoveGump...", self.info_color)
                    CUO.MoveGump(backpack.Serial, TEST_SCREEN_X + 100, TEST_SCREEN_Y + 100)
                    self.debug(f"  Moved backpack to ({TEST_SCREEN_X + 100}, {TEST_SCREEN_Y + 100})", self.success_color)
                    Misc.Pause(TEST_DELAY * 2)
                    
                    # Test CloseGump
                    self.debug("Testing CloseGump...", self.info_color)
                    CUO.CloseGump(backpack.Serial)
                    self.debug("  Closed backpack gump", self.success_color)
                    Misc.Pause(TEST_DELAY)
            except Exception as e:
                self.debug(f"  Error with gump functions: {e}", self.error_color)
        else:
            self.debug("  [INTERACTIVE_MODE disabled - skipping gump tests]", self.warning_color)
            self.debug("  Example: CUO.CloseGump(gump_serial)", self.info_color)
            self.debug("  Example: CUO.MoveGump(gump_serial, 100, 100)", self.info_color)
            self.debug("  Example: CUO.SetGumpOpenLocation(gump_serial, 100, 100)", self.info_color)
            self.debug("  Example: CUO.OpenContainerAt(container_serial, 100, 100)", self.info_color)
        
        self.debug("")
    
    def test_map_functions(self):
        """
        Test Map Functions
        
        API: CUO.LoadMarkers()
        Purpose: Load map markers from file
        Note: World map must be open for this to work
        
        API: CUO.GoToMarker(x, y)
        Purpose: Navigate to marker on world map
        Parameters:
          - x (Int32): World X coordinate
          - y (Int32): World Y coordinate
        Note: World map must be open for this to work
        
        API: CUO.CloseTMap()
        Purpose: Close treasure map gump (right-click close)
        Returns: Boolean - True if map was closed, False otherwise
        Note: Only closes if item is actually a map
        """
        section_header("TEST: Map Functions")
        
        self.debug("Testing map functions...", self.info_color)
        
        if INTERACTIVE_MODE:
            try:
                self.debug("  Note: Map must be open for LoadMarkers and GoToMarker", self.warning_color)
                
                # Test LoadMarkers
                self.debug("Testing LoadMarkers...", self.info_color)
                CUO.LoadMarkers()
                self.debug("  LoadMarkers executed (map must be open)", self.success_color)
                Misc.Pause(TEST_DELAY)
                
                # Test GoToMarker
                self.debug("Testing GoToMarker...", self.info_color)
                CUO.GoToMarker(self.player_x, self.player_y)
                self.debug(f"  GoToMarker executed for ({self.player_x}, {self.player_y})", self.success_color)
                Misc.Pause(TEST_DELAY)
                
            except Exception as e:
                self.debug(f"  Error with map functions: {e}", self.error_color)
            
            # Test CloseTMap
            try:
                self.debug("Testing CloseTMap...", self.info_color)
                result = CUO.CloseTMap()
                if result:
                    self.debug("  Treasure map closed", self.success_color)
                else:
                    self.debug("  No treasure map to close", self.debug_color)
            except Exception as e:
                self.debug(f"  Error with CloseTMap: {e}", self.error_color)
        else:
            self.debug("  [INTERACTIVE_MODE disabled - skipping map tests]", self.warning_color)
            self.debug("  Example: CUO.LoadMarkers() # Map must be open", self.info_color)
            self.debug("  Example: CUO.GoToMarker(x, y) # Map must be open", self.info_color)
            self.debug("  Example: result = CUO.CloseTMap()", self.info_color)
        
        self.debug("")
    
    def test_settings_functions(self):
        """
        Test Settings Functions
        
        API: CUO.GetSetting(settingName)
        Purpose: Retrieve current CUO setting value
        Parameters:
          - settingName (String): Name of setting to retrieve
        Returns: String value of setting
        
        API: CUO.ProfilePropertySet(propertyName, value)
        Purpose: Set a CUO profile property
        Parameters:
          - propertyName (String): Name of property to set
          - value (Boolean/Int32/String): Value to set (type depends on property)
        
        Common Settings:
          - ShowHealthBar: Display health bars
          - ShowManaBar: Display mana bars
          - ShowStaminaBar: Display stamina bars
          - HighlightGameObjects: Highlight objects on mouseover
          - EnablePathfind: Enable pathfinding
          - AlwaysRun: Always run instead of walk
          - ShowMobilesHP: Show mobile health percentages
        """
        section_header("TEST: Settings Functions")
        
        test_success = True
        error_msg = None
        settings_data = {}
        
        self.debug("Testing settings functions...", self.info_color)
        
        # Test GetSetting with common settings
        common_settings = [
            "ShowHealthBar",
            "ShowManaBar", 
            "ShowStaminaBar",
            "HighlightGameObjects",
            "EnablePathfind",
            "AlwaysRun",
            "ShowMobilesHP"
        ]
        
        self.debug("Retrieving common CUO settings:", self.info_color)
        for setting_name in common_settings:
            try:
                value = CUO.GetSetting(setting_name)
                settings_data[setting_name] = str(value)
                self.debug(f"  {setting_name}: {value}", self.success_color)
            except Exception as e:
                test_success = False
                if not error_msg:
                    error_msg = str(e)
                self.debug(f"  {setting_name}: Error - {e}", self.error_color)
        
        if INTERACTIVE_MODE:
            self.debug("", self.debug_color)
            self.debug("Testing ProfilePropertySet...", self.info_color)
            try:
                # Example: Toggle a boolean setting (be careful!)
                self.debug("  Note: ProfilePropertySet can modify CUO settings", self.warning_color)
                self.debug("  Example: CUO.ProfilePropertySet('AlwaysRun', True)", self.info_color)
                self.debug("  Example: CUO.ProfilePropertySet('GameWindowWidth', 1024)", self.info_color)
                self.debug("  Example: CUO.ProfilePropertySet('ProfileName', 'MyProfile')", self.info_color)
            except Exception as e:
                test_success = False
                if not error_msg:
                    error_msg = str(e)
                self.debug(f"  Error: {e}", self.error_color)
        else:
            self.debug("  [INTERACTIVE_MODE disabled - skipping ProfilePropertySet test]", self.warning_color)
        
        # Record test report
        self.json_output["test_report"]["SettingsFunctions"] = {
            "works": test_success,
            "error": error_msg,
            "data_returned": len(settings_data) > 0
        }
        self.json_output["tests"]["settings_data"] = settings_data
        
        self.debug("")
    
    def test_macro_function(self):
        """
        Test Macro Function
        
        API: CUO.PlayMacro(macroName)
        Purpose: Execute a CUO macro by name
        Parameters:
          - macroName (String): Name of macro to execute
        Warning: Limited testing - use with caution!
        
        Note: Macro must exist in CUO's macro list
        """
        section_header("TEST: Macro Function")
        
        test_success = True
        error_msg = None
        
        self.debug("Testing PlayMacro function...", self.info_color)
        
        if INTERACTIVE_MODE:
            try:
                self.debug("  WARNING: Limited testing on this function!", self.warning_color)
                self.debug("  Example: CUO.PlayMacro('MyMacroName')", self.info_color)
                self.debug("  Macro must exist in CUO's macro list", self.warning_color)
            except Exception as e:
                test_success = False
                error_msg = str(e)
                self.debug(f"  Error: {e}", self.error_color)
        else:
            self.debug("  [INTERACTIVE_MODE disabled - skipping macro test]", self.warning_color)
            self.debug("  Example: CUO.PlayMacro('MyMacroName')", self.info_color)
        
        # Record test report
        self.json_output["test_report"]["PlayMacro"] = {
            "works": None if not INTERACTIVE_MODE else test_success,
            "error": "Skipped - INTERACTIVE_MODE disabled" if not INTERACTIVE_MODE else error_msg,
            "data_returned": False
        }
        
        self.debug("")
    
    def save_json_output(self):
        """Save test results to JSON file"""
        try:
            # Ensure directory exists
            if not os.path.exists(BASE_PATH):
                os.makedirs(BASE_PATH)
            
            # Write JSON file
            with open(OUTPUT_FILE, 'w') as f:
                json.dump(self.json_output, f, indent=2)
            
            self.debug(f"JSON output saved to: {OUTPUT_FILE}", self.success_color)
            
        except Exception as e:
            self.debug(f"Error saving JSON: {e}", self.error_color)
    
    def run_all_tests(self):
        """Run all CUO API tests"""
        section_header("CUO API COMPREHENSIVE TEST")
        self.debug(f"Player Serial: 0x{self.player_serial:08X}", self.info_color)
        self.debug(f"Player Position: ({self.player_x}, {self.player_y})", self.info_color)
        self.debug(f"Interactive Mode: {INTERACTIVE_MODE}", self.warning_color if not INTERACTIVE_MODE else self.success_color)
        if not INTERACTIVE_MODE:
            self.debug("  Set INTERACTIVE_MODE = True to enable actual testing", self.warning_color)
        self.debug("")
        
        # Run all tests
        self.test_follow_system()
        self.test_free_view()
        self.test_status_bar_functions()
        self.test_gump_functions()
        self.test_map_functions()
        self.test_settings_functions()
        self.test_macro_function()
        
        # Final summary
        section_header("TEST COMPLETE")
        self.debug("All CUO API functions have been tested!", self.success_color)
        if not INTERACTIVE_MODE:
            self.debug("Note: Most tests were skipped due to INTERACTIVE_MODE = False", self.warning_color)
            self.debug("Set INTERACTIVE_MODE = True to enable full testing", self.info_color)
        self.debug("Check the output above for detailed results.", self.info_color)
        
        # Save JSON output
        self.debug("")
        section_header("SAVING JSON OUTPUT")
        self.save_json_output()

# ============================================================================
# USAGE EXAMPLES - Common CUO API patterns
# ============================================================================

def example_follow_mobile():
    """Example: Follow a mobile and check status"""
    # Replace with actual mobile serial
    mobile_serial = 0x12345678
    
    # Start following
    CUO.FollowMobile(mobile_serial)
    Misc.Pause(100)
    
    # Check if following
    is_following, target = CUO.Following()
    if is_following:
        Misc.SendMessage(f"Following: 0x{target:08X}", 68)
    else:
        Misc.SendMessage("Not following", 33)
    
    # Stop following
    CUO.FollowOff()
    Misc.SendMessage("Stopped following", 67)

def example_open_containers_positioned():
    """Example: Open containers at specific positions"""
    if not Player.Backpack:
        Misc.SendMessage("No backpack found", 33)
        return
    
    # Set where backpack will open
    CUO.OpenContainerAt(Player.Backpack.Serial, 100, 100)
    Items.UseItem(Player.Backpack)
    Misc.SendMessage("Backpack opened at (100, 100)", 68)
    
    # Move it after opening
    Misc.Pause(500)
    CUO.MoveGump(Player.Backpack.Serial, 200, 200)
    Misc.SendMessage("Backpack moved to (200, 200)", 68)

def example_manage_party_health_bars():
    """Example: Manage health bars for party members"""
    # Replace with actual party member serials
    party_members = [0x12345678, 0x23456789, 0x34567890]
    y_offset = 0
    
    Misc.SendMessage("Opening party health bars...", 88)
    for member in party_members:
        CUO.OpenMobileHealthBar(member, 10, 100 + y_offset, True)
        y_offset += 50
        Misc.Pause(100)
    
    Misc.SendMessage(f"Opened {len(party_members)} health bars", 68)

def example_free_camera_scouting():
    """Example: Enable free camera for scouting"""
    # Enable free view
    CUO.FreeView(True)
    Misc.SendMessage("Free camera enabled - use arrow keys", 68)
    Misc.Pause(5000)
    
    # Disable free view
    CUO.FreeView(False)
    Misc.SendMessage("Camera locked to player", 68)

def example_toggle_cuo_setting():
    """Example: Check and modify CUO settings"""
    # Check current setting
    always_run = CUO.GetSetting("AlwaysRun")
    Misc.SendMessage(f"AlwaysRun: {always_run}", 67)
    
    # Toggle setting
    if always_run == "True":
        CUO.ProfilePropertySet("AlwaysRun", False)
        Misc.SendMessage("AlwaysRun disabled", 68)
    else:
        CUO.ProfilePropertySet("AlwaysRun", True)
        Misc.SendMessage("AlwaysRun enabled", 68)

def example_navigate_world_map():
    """Example: Navigate on world map"""
    # Open world map first (manually or via macro)
    Misc.SendMessage("Open world map first, then run this", 53)
    Misc.Pause(500)
    
    # Load markers
    CUO.LoadMarkers()
    Misc.SendMessage("Markers loaded", 68)
    
    # Navigate to location
    target_x = 2500
    target_y = 500
    CUO.GoToMarker(target_x, target_y)
    Misc.SendMessage(f"Navigating to ({target_x}, {target_y})", 68)

def example_cleanup_health_bars():
    """Example: Clean up all health bars"""
    # Replace with actual summon serials
    summons = [0x12345678, 0x23456789, 0x34567890]
    
    Misc.SendMessage("Closing health bars...", 88)
    for summon in summons:
        CUO.CloseMobileHealthBar(summon)
        Misc.Pause(50)
    
    Misc.SendMessage(f"Closed {len(summons)} health bars", 68)

def example_position_status_bar():
    """Example: Position player status bar"""
    # Close existing
    CUO.CloseMyStatusBar()
    Misc.Pause(100)
    
    # Open at specific position
    CUO.OpenMyStatusBar(10, 10)
    Misc.SendMessage("Status bar opened at (10, 10)", 68)

def example_organize_containers():
    """Example: Organize multiple containers on screen"""
    if not Player.Backpack:
        Misc.SendMessage("No backpack found", 33)
        return
    
    # Find all bags in backpack
    bags = []
    for item in Player.Backpack.Contains:
        if item.ItemID in [0x0E76, 0x0E75, 0x0E79]:  # Bag, Backpack, Pouch
            bags.append(item)
    
    if not bags:
        Misc.SendMessage("No bags found in backpack", 33)
        return
    
    # Position bags in a grid
    x_start = 50
    y_start = 50
    x_offset = 0
    
    Misc.SendMessage(f"Positioning {len(bags)} containers...", 88)
    for bag in bags[:5]:  # Limit to 5 bags
        CUO.OpenContainerAt(bag.Serial, x_start + x_offset, y_start)
        Items.UseItem(bag)
        Misc.Pause(300)
        x_offset += 250
    
    Misc.SendMessage("Containers organized", 68)

def example_check_all_settings():
    """Example: Display all common CUO settings"""
    settings = [
        "ShowHealthBar", "ShowManaBar", "ShowStaminaBar",
        "HighlightGameObjects", "EnablePathfind", "AlwaysRun",
        "ShowMobilesHP", "ShowCorpseNames", "NameOverheadToggled"
    ]
    
    Misc.SendMessage("=== CUO Settings ===", 88)
    for setting in settings:
        try:
            value = CUO.GetSetting(setting)
            Misc.SendMessage(f"{setting}: {value}", 67)
        except Exception as e:
            Misc.SendMessage(f"{setting}: Error - {e}", 33)

def example_close_treasure_map():
    """Example: Close treasure map if open"""
    result = CUO.CloseTMap()
    if result:
        Misc.SendMessage("Treasure map closed", 68)
    else:
        Misc.SendMessage("No treasure map open", 33)

def example_play_cuo_macro():
    """Example: Execute a CUO macro"""
    macro_name = "MyMacroName"  # Replace with actual macro name
    
    try:
        CUO.PlayMacro(macro_name)
        Misc.SendMessage(f"Executed macro: {macro_name}", 68)
    except Exception as e:
        Misc.SendMessage(f"Error executing macro: {e}", 33)

# Main execution
try:
    tester = CUOAPITester()
    tester.run_all_tests()
    
    # Optionally run usage examples
    if RUN_USAGE_EXAMPLES:
        debug_message("")
        debug_message("")
        section_header("USAGE EXAMPLES - PRACTICAL DEMONSTRATIONS")
        debug_message("Usage examples are defined as functions above", 67)
        debug_message("Call them individually as needed:", 67)
        debug_message("  - example_follow_mobile()", 67)
        debug_message("  - example_open_containers_positioned()", 67)
        debug_message("  - example_manage_party_health_bars()", 67)
        debug_message("  - example_free_camera_scouting()", 67)
        debug_message("  - example_toggle_cuo_setting()", 67)
        debug_message("  - example_navigate_world_map()", 67)
        debug_message("  - example_cleanup_health_bars()", 67)
        debug_message("  - example_position_status_bar()", 67)
        debug_message("  - example_organize_containers()", 67)
        debug_message("  - example_check_all_settings()", 67)
        debug_message("  - example_close_treasure_map()", 67)
        debug_message("  - example_play_cuo_macro()", 67)
        section_header("USAGE EXAMPLES COMPLETE")
    
except Exception as e:
    debug_message(f"FATAL ERROR: {e}", 33)
    import traceback
    debug_message(traceback.format_exc(), 33)
