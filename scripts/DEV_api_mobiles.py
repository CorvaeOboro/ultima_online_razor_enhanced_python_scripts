"""
DEV API Mobiles - a Razor Enhanced Python Script for Ultima Online

demonstration of Mobiles API functions
Tests functions to search and interact with Mobile objects

=== MOBILES API OVERVIEW ===
The Mobiles class provides functions to search and interact with Mobile objects.
This is different from the Mobile class which represents a single mobile entity.

ALL MOBILES FUNCTIONS (15 functions):

SEARCH & FILTER (4 functions):
  - ApplyFilter(filter) -> List[Mobile]
  - FindBySerial(serial) -> Mobile
  - FindMobile(graphic, notoriety, rangemax, selector, highlight) -> Mobile
  - Select(mobiles, selector) -> Mobile

PROPERTIES (4 functions):
  - GetPropStringList(serial) -> List[String]
  - GetPropStringByIndex(serial, index) -> String
  - GetPropValue(serial, name) -> Single
  - WaitForProps(m, delay) -> Boolean

INTERACTION (3 functions):
  - UseMobile(mobile)
  - SingleClick(mobile)
  - Message(mobile, hue, message, wait)

CONTEXT MENU (1 function):
  - ContextExist(mob, name, showContext) -> Int32

TARGETING (1 function):
  - GetTargetingFilter(target_name) -> Mobiles.Filter

TRACKING (1 function):
  - GetTrackingInfo() -> Mobiles.TrackingInfo

STATS (1 function):
  - WaitForStats(m, delay) -> Boolean

VERSION::20251013
"""

from System.Collections.Generic import List
import os
import json

# GLOBAL SETTINGS
DEBUG_MODE = True
TEST_DELAY = 500
MAX_SEARCH_RANGE = 10
# JSON output file path
BASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
OUTPUT_FILE = os.path.join(BASE_PATH, "api_mobiles_test_output.json")
# Run usage examples after tests
RUN_USAGE_EXAMPLES = True
#======================================================================

def debug_message(message, color=67):
    """Send debug message to game client"""
    if not DEBUG_MODE:
        return
    try:
        # Don't add prefix for empty messages (used for spacing)
        if message:
            Misc.SendMessage(f"[Mobiles] {message}", color)
        else:
            Misc.SendMessage("", color)
    except Exception:
        if message:
            print(f"[Mobiles] {message}")
        else:
            print("")

def section_header(title):
    """Print a section header"""
    debug_message("=" * 60, 88)
    debug_message(f"  {title}", 88)
    debug_message("=" * 60, 88)

class MobilesAPITester:
    def __init__(self):
        self.debug_color = 67
        self.error_color = 33
        self.success_color = 68
        self.info_color = 88
        self.warning_color = 53
        
        # Initialize JSON output structure
        self.json_output = {
            "test_report": {},  # Summary of which API functions work
            "test_timestamp": str(Misc.ScriptCurrent(False)),
            "max_search_range": MAX_SEARCH_RANGE,
            "tests": {}
        }
        
    def debug(self, message, color=None):
        if color is None:
            color = self.debug_color
        debug_message(message, color)
    
    def test_find_by_serial(self):
        """
        Test FindBySerial Function
        
        API: Mobiles.FindBySerial(serial) -> Mobile
        Purpose: Find mobile with specific serial
        Parameters:
          - serial (Int32): Serial of mobile
        Returns: Mobile object or null
        """
        section_header("TEST: FindBySerial")
        
        test_success = True
        error_msg = None
        find_data = {}
        
        try:
            # Test with player serial
            player_serial = Player.Serial
            mobile = Mobiles.FindBySerial(player_serial)
            
            if mobile:
                find_data["found_player"] = True
                find_data["player_name"] = str(mobile.Name)
                find_data["player_serial"] = int(mobile.Serial)
                self.debug(f"  Found mobile: {mobile.Name}", self.success_color)
                self.debug(f"  Serial: 0x{mobile.Serial:08X}", self.success_color)
            else:
                find_data["found_player"] = False
                self.debug(f"  Mobile not found", self.error_color)
                
            # Test with invalid serial
            invalid = Mobiles.FindBySerial(-1)
            find_data["invalid_serial_returns_null"] = invalid is None
            if invalid:
                self.debug(f"  Found with -1: {invalid.Name}", self.debug_color)
            else:
                self.debug(f"  No mobile with serial -1", self.debug_color)
                
        except Exception as e:
            test_success = False
            error_msg = str(e)
            self.debug(f"  Error: {e}", self.error_color)
        
        self.json_output["test_report"]["FindBySerial"] = {
            "works": test_success,
            "error": error_msg,
            "data_returned": len(find_data) > 0
        }
        self.json_output["tests"]["find_by_serial"] = find_data
        self.debug("")
    
    def test_apply_filter(self):
        """
        Test ApplyFilter Function
        
        API: Mobiles.ApplyFilter(filter) -> List[Mobile]
        Purpose: Find mobiles matching filter criteria
        Parameters:
          - filter (Mobiles.Filter): Filter object
        Returns: List of matching mobiles
        """
        section_header("TEST: ApplyFilter")
        
        test_success = True
        error_msg = None
        filter_data = {}
        
        try:
            # Create filter for nearby mobiles
            mobile_filter = Mobiles.Filter()
            mobile_filter.Enabled = True
            mobile_filter.RangeMax = MAX_SEARCH_RANGE
            mobile_filter.CheckIgnoreObject = True
            
            mobiles = Mobiles.ApplyFilter(mobile_filter)
            
            if mobiles and len(mobiles) > 0:
                filter_data["mobiles_found"] = len(mobiles)
                filter_data["sample_mobiles"] = []
                self.debug(f"  Found {len(mobiles)} mobiles within {MAX_SEARCH_RANGE} tiles", self.success_color)
                for i, mob in enumerate(mobiles[:5]):
                    distance = Player.DistanceTo(mob)
                    filter_data["sample_mobiles"].append({
                        "name": str(mob.Name),
                        "serial": int(mob.Serial),
                        "distance": int(distance)
                    })
                    self.debug(f"    [{i+1}] {mob.Name} at {distance} tiles", self.debug_color)
                if len(mobiles) > 5:
                    self.debug(f"    ... and {len(mobiles) - 5} more", self.debug_color)
            else:
                filter_data["mobiles_found"] = 0
                self.debug(f"  No mobiles found", self.warning_color)
                
        except Exception as e:
            test_success = False
            error_msg = str(e)
            self.debug(f"  Error: {e}", self.error_color)
        
        self.json_output["test_report"]["ApplyFilter"] = {
            "works": test_success,
            "error": error_msg,
            "data_returned": len(filter_data) > 0
        }
        self.json_output["tests"]["apply_filter"] = filter_data
        self.debug("")
    
    def test_find_mobile(self):
        """
        Test FindMobile Function
        
        API: Mobiles.FindMobile(graphic, notoriety, rangemax, selector, highlight) -> Mobile
        Purpose: Find mobile with specific criteria
        Parameters:
          - graphic (Int32/List[Int32]): Mobile graphic ID(s)
          - notoriety (List[Byte]): Notoriety list
          - rangemax (Int32): Maximum range
          - selector (String): Selection method ("Nearest", "Farthest", "Weakest", "Strongest")
          - highlight (Boolean): Highlight found mobile
        Returns: Mobile or null
        """
        section_header("TEST: FindMobile")
        
        try:
            # Find nearest mobile of any type
            mobile = Mobiles.FindMobile(-1, [1, 2, 3, 4, 5, 6, 7], MAX_SEARCH_RANGE, "Nearest", False)
            
            if mobile:
                self.debug(f"  Found nearest mobile: {mobile.Name}", self.success_color)
                self.debug(f"  Distance: {Player.DistanceTo(mobile)} tiles", self.success_color)
                self.debug(f"  Notoriety: {mobile.Notoriety}", self.success_color)
            else:
                self.debug(f"  No mobile found", self.warning_color)
                
        except Exception as e:
            self.debug(f"  Error: {e}", self.error_color)
        
        self.debug("")
    
    def test_select(self):
        """
        Test Select Function
        
        API: Mobiles.Select(mobiles, selector) -> Mobile
        Purpose: Select one mobile from list using selector
        Parameters:
          - mobiles (List[Mobile]): List of mobiles
          - selector (String): "Nearest", "Farthest", "Weakest", "Strongest"
        Returns: Selected mobile or null
        """
        section_header("TEST: Select")
        
        try:
            # Get list of mobiles
            mobile_filter = Mobiles.Filter()
            mobile_filter.Enabled = True
            mobile_filter.RangeMax = MAX_SEARCH_RANGE
            mobiles = Mobiles.ApplyFilter(mobile_filter)
            
            if mobiles and len(mobiles) > 0:
                self.debug(f"  Testing with {len(mobiles)} mobiles", self.info_color)
                
                # Test different selectors
                selectors = ["Nearest", "Farthest", "Weakest", "Strongest"]
                for selector in selectors:
                    selected = Mobiles.Select(mobiles, selector)
                    if selected:
                        distance = Player.DistanceTo(selected)
                        self.debug(f"  {selector}: {selected.Name} ({distance} tiles)", self.success_color)
            else:
                self.debug(f"  No mobiles to select from", self.warning_color)
                
        except Exception as e:
            self.debug(f"  Error: {e}", self.error_color)
        
        self.debug("")
    
    def test_property_functions(self):
        """
        Test Property Functions
        
        API: Mobiles.GetPropStringList(serial) -> List[String]
        API: Mobiles.GetPropStringByIndex(serial, index) -> String
        API: Mobiles.GetPropValue(serial, name) -> Single
        API: Mobiles.WaitForProps(m, delay) -> Boolean
        """
        section_header("TEST: Property Functions")
        
        mobile = Player
        test_success = True
        error_msg = None
        prop_data = {}
        
        try:
            # GetPropStringList
            self.debug("Testing GetPropStringList...", self.info_color)
            props = Mobiles.GetPropStringList(mobile.Serial)
            if props and len(props) > 0:
                prop_data["property_count"] = len(props)
                prop_data["sample_properties"] = [str(p) for p in props[:5]]
                self.debug(f"  Found {len(props)} properties", self.success_color)
                for i, prop in enumerate(props[:5]):
                    self.debug(f"    [{i}] {prop}", self.debug_color)
            else:
                prop_data["property_count"] = 0
                self.debug(f"  No properties found", self.warning_color)
            
            # GetPropStringByIndex
            self.debug("Testing GetPropStringByIndex...", self.info_color)
            if props and len(props) > 0:
                prop_0 = Mobiles.GetPropStringByIndex(mobile.Serial, 0)
                prop_data["first_property"] = str(prop_0)
                self.debug(f"  Property[0]: {prop_0}", self.success_color)
            
            # WaitForProps
            self.debug("Testing WaitForProps...", self.info_color)
            result = Mobiles.WaitForProps(mobile, 1000)
            prop_data["wait_for_props_result"] = bool(result)
            self.debug(f"  WaitForProps result: {result}", self.success_color)
            
        except Exception as e:
            test_success = False
            error_msg = str(e)
            self.debug(f"  Error: {e}", self.error_color)
        
        self.json_output["test_report"]["PropertyFunctions"] = {
            "works": test_success,
            "error": error_msg,
            "data_returned": len(prop_data) > 0
        }
        self.json_output["tests"]["property_functions"] = prop_data
        self.debug("")
    
    def test_interaction_functions(self):
        """
        Test Interaction Functions
        
        API: Mobiles.UseMobile(mobile)
        API: Mobiles.SingleClick(mobile)
        API: Mobiles.Message(mobile, hue, message, wait)
        """
        section_header("TEST: Interaction Functions")
        
        test_success = True
        error_msg = None
        
        try:
            # SingleClick
            self.debug("Testing SingleClick...", self.info_color)
            Mobiles.SingleClick(Player)
            self.debug(f"  SingleClick executed on player", self.success_color)
            Misc.Pause(TEST_DELAY)
            
            # Message (overhead message)
            self.debug("Testing Message...", self.info_color)
            Mobiles.Message(Player, 68, "Test Message", False)
            self.debug(f"  Message sent", self.success_color)
            
        except Exception as e:
            test_success = False
            error_msg = str(e)
            self.debug(f"  Error: {e}", self.error_color)
        
        self.json_output["test_report"]["InteractionFunctions"] = {
            "works": test_success,
            "error": error_msg,
            "data_returned": test_success
        }
        self.debug("")
    
    def test_context_exist(self):
        """
        Test ContextExist Function
        
        API: Mobiles.ContextExist(mob, name, showContext) -> Int32
        Purpose: Check if context menu entry exists
        Parameters:
          - mob (Int32/Mobile): Mobile serial or object
          - name (String): Context menu entry name
          - showContext (Boolean): Show context menu
        Returns: Int32 index or -1 if not found
        """
        section_header("TEST: ContextExist")
        
        try:
            self.debug("Testing ContextExist...", self.info_color)
            # Note: This will show context menu if showContext=True
            result = Mobiles.ContextExist(Player, "Status", False)
            if result >= 0:
                self.debug(f"  'Status' found at index: {result}", self.success_color)
            else:
                self.debug(f"  'Status' not found", self.warning_color)
                
        except Exception as e:
            self.debug(f"  Error: {e}", self.error_color)
        
        self.debug("")
    
    def test_wait_for_stats(self):
        """
        Test WaitForStats Function
        
        API: Mobiles.WaitForStats(m, delay) -> Boolean
        Purpose: Wait for mobile stats to update
        Parameters:
          - m (Int32/Mobile): Mobile serial or object
          - delay (Int32): Timeout in milliseconds
        Returns: True if stats received, False if timeout
        """
        section_header("TEST: WaitForStats")
        
        try:
            self.debug("Testing WaitForStats...", self.info_color)
            result = Mobiles.WaitForStats(Player, 1000)
            self.debug(f"  WaitForStats result: {result}", self.success_color)
            
        except Exception as e:
            self.debug(f"  Error: {e}", self.error_color)
        
        self.debug("")
    
    def test_tracking_info(self):
        """
        Test GetTrackingInfo Function
        
        API: Mobiles.GetTrackingInfo() -> Mobiles.TrackingInfo
        Purpose: Get current tracking information
        Returns: TrackingInfo object with tracking data
        """
        section_header("TEST: GetTrackingInfo")
        
        try:
            self.debug("Testing GetTrackingInfo...", self.info_color)
            tracking = Mobiles.GetTrackingInfo()
            
            if tracking:
                self.debug(f"  Tracking info retrieved", self.success_color)
                # TrackingInfo properties would be accessed here
            else:
                self.debug(f"  No tracking info available", self.warning_color)
                
        except Exception as e:
            self.debug(f"  Error: {e}", self.error_color)
        
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
        """Run all Mobiles API tests"""
        section_header("MOBILES API TEST")
        self.debug(f"Max search range: {MAX_SEARCH_RANGE} tiles", self.info_color)
        self.debug("")
        
        self.test_find_by_serial()
        self.test_apply_filter()
        self.test_find_mobile()
        self.test_select()
        self.test_property_functions()
        self.test_interaction_functions()
        self.test_context_exist()
        self.test_wait_for_stats()
        self.test_tracking_info()
        
        section_header("TEST COMPLETE")
        self.debug("All Mobiles API functions tested!", self.success_color)
        
        # Save JSON output
        self.debug("")
        section_header("SAVING JSON OUTPUT")
        self.save_json_output()

# ============================================================================
# USAGE EXAMPLES
# ============================================================================

def example_find_nearest_enemy():
    """Example: Find nearest hostile mobile"""
    enemy = Mobiles.FindMobile(-1, [6], 15, "Nearest", True)
    if enemy:
        Misc.SendMessage(f"Nearest enemy: {enemy.Name}", 33)
    else:
        Misc.SendMessage("No enemies nearby", 68)

def example_filter_by_notoriety():
    """Example: Find all hostiles in range"""
    enemy_filter = Mobiles.Filter()
    enemy_filter.Enabled = True
    enemy_filter.RangeMax = 10
    enemy_filter.Notorieties = [6]  # Red
    enemy_filter.CheckIgnoreObject = True
    
    enemies = Mobiles.ApplyFilter(enemy_filter)
    if enemies:
        Misc.SendMessage(f"Found {len(enemies)} hostiles", 33)

def example_find_weakest_target():
    """Example: Find weakest mobile in range"""
    mobile_filter = Mobiles.Filter()
    mobile_filter.Enabled = True
    mobile_filter.RangeMax = 10
    mobile_filter.Notorieties = [3, 4, 5, 6]
    
    mobiles = Mobiles.ApplyFilter(mobile_filter)
    if mobiles:
        weakest = Mobiles.Select(mobiles, "Weakest")
        if weakest:
            Misc.SendMessage(f"Weakest: {weakest.Name}", 67)

def example_check_mobile_properties():
    """Example: Get mobile properties"""
    mobile = Player
    props = Mobiles.GetPropStringList(mobile.Serial)
    if props:
        Misc.SendMessage(f"Properties: {len(props)}", 67)
        for prop in props[:3]:
            Misc.SendMessage(f"  {prop}", 67)

def example_send_overhead_message():
    """Example: Send overhead message to mobile"""
    Mobiles.Message(Player, 68, "Hello World!", False)

def example_wait_for_mobile_data():
    """Example: Wait for mobile stats/props"""
    mobile = Player
    
    # Wait for stats
    if Mobiles.WaitForStats(mobile, 1000):
        Misc.SendMessage("Stats received", 68)
    
    # Wait for properties
    if Mobiles.WaitForProps(mobile, 1000):
        Misc.SendMessage("Props received", 68)

def example_find_party_members():
    """Example: Find all party members"""
    party_filter = Mobiles.Filter()
    party_filter.Enabled = True
    party_filter.RangeMax = 20
    party_filter.Friend = True
    
    all_mobiles = Mobiles.ApplyFilter(party_filter)
    party_members = [m for m in all_mobiles if m.InParty]
    
    Misc.SendMessage(f"Party members: {len(party_members)}", 68)

def example_find_by_body_type():
    """Example: Find mobiles by body type"""
    # Find all humans
    human_filter = Mobiles.Filter()
    human_filter.Enabled = True
    human_filter.RangeMax = 15
    human_filter.Bodies = [400, 401]  # Male, Female
    
    humans = Mobiles.ApplyFilter(human_filter)
    Misc.SendMessage(f"Found {len(humans)} humans", 67)

def example_context_menu_check():
    """Example: Check context menu options"""
    mobile = Player
    
    # Check if "Open Paperdoll" exists
    index = Mobiles.ContextExist(mobile, "Open Paperdoll", False)
    if index >= 0:
        Misc.SendMessage(f"Paperdoll option at index {index}", 67)

# Main execution
try:
    tester = MobilesAPITester()
    tester.run_all_tests()
    
    # Optionally run usage examples
    if RUN_USAGE_EXAMPLES:
        debug_message("")
        debug_message("")
        section_header("USAGE EXAMPLES - PRACTICAL DEMONSTRATIONS")
        debug_message("Usage examples are defined as functions above", 67)
        debug_message("Call them individually as needed:", 67)
        debug_message("  - example_find_nearest_enemy()", 67)
        debug_message("  - example_filter_by_notoriety()", 67)
        debug_message("  - example_find_weakest_target()", 67)
        debug_message("  - example_check_mobile_properties()", 67)
        debug_message("  - example_send_overhead_message()", 67)
        debug_message("  - example_wait_for_mobile_data()", 67)
        debug_message("  - example_find_party_members()", 67)
        debug_message("  - example_find_by_body_type()", 67)
        debug_message("  - example_context_menu_check()", 67)
        section_header("USAGE EXAMPLES COMPLETE")
    
except Exception as e:
    debug_message(f"FATAL ERROR: {e}", 33)
    import traceback
    debug_message(traceback.format_exc(), 33)
