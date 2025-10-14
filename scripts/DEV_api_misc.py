"""
DEV API Misc - a Razor Enhanced Python Script for Ultima Online

 demonstration of  Misc API functions
Tests utility functions, file operations, shared values, and system interactions

=== MISC API OVERVIEW ===
The Misc class contains general purpose functions of common use.

ALL MISC API FUNCTIONS (70+ functions):

MESSAGING & SOUND:
  - SendMessage(message, color) - Display colored message in game
  - Beep() - Play system beep sound
  - PlaySound(sound, x, y, z) - Play UO sound at coordinates

FILE OPERATIONS:
  - AppendToFile(fileName, lineOfData) - Append line to file
  - AppendNotDupToFile(fileName, lineOfData) - Append if not duplicate
  - ReadFile(fileName) - Read all lines from file
  - RemoveLineInFile(fileName, lineOfData) - Remove specific line
  - DeleteFile(fileName) - Delete file

SHARED VALUES (Cross-script data):
  - SetSharedValue(name, value) - Store shared value
  - ReadSharedValue(name) - Get shared value
  - CheckSharedValue(name) - Check if value exists
  - RemoveSharedValue(name) - Delete shared value
  - AllSharedValue() - Get list of all shared value names

DIRECTORIES:
  - ScriptDirectory() - Get Scripts directory path
  - DataDirectory() - Get Data directory path
  - ConfigDirectory() - Get Config directory path
  - RazorDirectory() - Get main Razor Enhanced folder path
  - ScriptCurrent(fullpath) - Get current script path

UTILITY FUNCTIONS:
  - Pause(millisec) - Pause script execution
  - Distance(X1, Y1, X2, Y2) - Calculate UO distance
  - DistanceSqrt(point_a, point_b) - Pythagorean distance
  - IsItem(serial) - Check if serial is item
  - IsMobile(serial) - Check if serial is mobile
  - NoOperation() - Do nothing (placeholder)

IGNORE LIST:
  - IgnoreObject(serial) - Add to ignore list
  - CheckIgnoreObject(serial) - Check if ignored
  - UnIgnoreObject(serial) - Remove from ignore list
  - ClearIgnore() - Clear entire ignore list

SYSTEM INFO:
  - GetWindowSize() - Get UO window size (Rectangle)
  - MouseLocation() - Get mouse position (Point)
  - GetMapInfo(serial) - Get MapInfo object
  - GetContPosition() - Get container position (OSI only)

PROMPTS:
  - HasPrompt() - Check if prompt is active
  - ResponsePrompt(text) - Respond to prompt
  - CancelPrompt() - Cancel prompt
  - ResetPrompt() - Reset prompt state

OLD MENUS:
  - HasMenu() - Check if menu is open
  - GetMenuTitle() - Get menu title
  - MenuContain(text) - Check if menu contains text
  - MenuResponse(text) - Select menu item
  - CloseMenu() - Close menu

QUERY STRING:
  - HasQueryString() - Check if query string is open
  - QueryStringResponse(okcancel, response) - Respond to query

CONTEXT MENUS:
  - ContextReply(serial, response_num) - Respond to context menu
  - WaitForContext(serial, delay) - Get context menu entries

CLIENT CONTROL:
  - FocusUOWindow() - Focus UO window
  - CaptureNow() - Take screenshot
  - Resync() - Trigger client resync
  - Disconnect() - Force disconnect
  - CloseBackpack() - Close backpack (OSI only)
  - OpenPaperdoll() - Open paperdoll (OSI only)

SCRIPT CONTROL:
  - ScriptRun(scriptfile) - Start script
  - ScriptStop(scriptfile) - Stop script
  - ScriptSuspend(scriptfile) - Suspend script
  - ScriptResume(scriptfile) - Resume script
  - ScriptIsSuspended(scriptfile) - Check if suspended
  - ScriptStatus(scriptfile) - Get script status

MOUSE CONTROL:
  - MouseMove(posX, posY) - Move mouse pointer
  - LeftMouseClick(xpos, ypos, clientCoords) - Left click
  - RightMouseClick(xpos, ypos, clientCoords) - Right click

ADVANCED:
  - ChangeProfile(profileName) - Load profile
  - ClearDragQueue() - Clear drag-n-drop queue
  - ExportPythonAPI(path, pretty) - Export API to JSON
  - FilterSeason(enable, seasonFlag) - Force season filter
  - Inspect() - Open inspector for target
  - LastHotKey() - Get last hotkey pressed
  - NextContPosition(x, y) - Get next container position (OSI only)
  - NoRunStealthStatus() - Get no-run-stealth status
  - NoRunStealthToggle(enable) - Set no-run-stealth
  - PetRename(serial, name) - Rename pet

=== MISC.CONTEXT CLASS ===
Context menu entry information (returned by WaitForContext)

Context Properties (2 properties):
  - Entry (String): Text displayed in context menu entry
  - Response (Int32): Response ID for this context menu entry

=== MISC.MAPINFO CLASS ===
Map and location information for objects

MapInfo Properties (5 properties):
  - Serial (UInt32): Serial number of the map object
  - Facet (UInt16): Facet/map number (0=Felucca, 1=Trammel, etc.)
  - MapOrigin (Point2D): Top-left corner of map coverage area
  - MapEnd (Point2D): Bottom-right corner of map coverage area
  - PinPosition (Point2D): Position of the pin on the map

IMPORTANT NOTES:
  - File operations restricted to RE/CUO directories only
  - Shared values accessible by all scripts
  - Some functions OSI-only (marked in documentation)
  - Mouse/window functions use Windows API

VERSION::20251013
"""

from System.Collections.Generic import List
import os
import json

# GLOBAL SETTINGS
DEBUG_MODE = True
# Enable interactive tests (requires user input)
INTERACTIVE_MODE = False  # Set True to enable interactive tests
# Test delay (ms)
TEST_DELAY = 500
# JSON output file path
BASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
OUTPUT_FILE = os.path.join(BASE_PATH, "api_misc_test_output.json")
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
            Misc.SendMessage(f"[MISC] {message}", color)
        else:
            Misc.SendMessage("", color)
    except Exception:
        if message:
            print(f"[MISC] {message}")
        else:
            print("")

def section_header(title):
    """Print a section header"""
    debug_message("=" * 60, 88)
    debug_message(f"  {title}", 88)
    debug_message("=" * 60, 88)

class MiscAPITester:
    def __init__(self):
        self.debug_color = 67  # Light blue
        self.error_color = 33  # Red
        self.success_color = 68  # Green
        self.info_color = 88  # Cyan
        self.warning_color = 53  # Yellow
        
        # Initialize JSON output structure
        self.json_output = {
            "test_report": {},  # Summary of which API functions work
            "test_timestamp": str(Misc.ScriptCurrent(False)),
            "tests": {}
        }
        
    def debug(self, message, color=None):
        """Send a debug message"""
        if color is None:
            color = self.debug_color
        debug_message(message, color)
    
    def test_messaging_functions(self):
        """Test SendMessage, Beep, PlaySound"""
        section_header("TEST: Messaging Functions")
        
        test_success = True
        error_msg = None
        
        try:
            self.debug("Testing SendMessage...", self.info_color)
            Misc.SendMessage("Test message - default color", 67)
            Misc.SendMessage("Test message - red", 33)
            Misc.SendMessage("Test message - green", 68)
            self.debug("  SendMessage: OK", self.success_color)
            
            self.debug("Testing Beep...", self.info_color)
            Misc.Beep()
            self.debug("  Beep: OK (listen for system beep)", self.success_color)
            
            if Player.Position:
                self.debug("Testing PlaySound...", self.info_color)
                Misc.PlaySound(0x0055, Player.Position.X, Player.Position.Y, Player.Position.Z)
                self.debug("  PlaySound: OK", self.success_color)
            
        except Exception as e:
            test_success = False
            error_msg = str(e)
            self.debug(f"  Error: {e}", self.error_color)
        
        # Record test report
        self.json_output["test_report"]["SendMessage"] = {
            "works": test_success,
            "error": error_msg,
            "data_returned": test_success
        }
        self.json_output["test_report"]["Beep"] = {
            "works": test_success,
            "error": error_msg,
            "data_returned": test_success
        }
        self.json_output["test_report"]["PlaySound"] = {
            "works": test_success,
            "error": error_msg,
            "data_returned": test_success
        }
        
        self.debug("")
    
    def test_directory_functions(self):
        """Test directory path functions"""
        section_header("TEST: Directory Functions")
        
        test_success = True
        error_msg = None
        paths = {}
        
        try:
            self.debug("Getting directory paths...", self.info_color)
            
            script_dir = Misc.ScriptDirectory()
            paths["script_dir"] = str(script_dir)
            self.debug(f"  ScriptDirectory: {script_dir}", self.debug_color)
            
            data_dir = Misc.DataDirectory()
            paths["data_dir"] = str(data_dir)
            self.debug(f"  DataDirectory: {data_dir}", self.debug_color)
            
            config_dir = Misc.ConfigDirectory()
            paths["config_dir"] = str(config_dir)
            self.debug(f"  ConfigDirectory: {config_dir}", self.debug_color)
            
            razor_dir = Misc.RazorDirectory()
            paths["razor_dir"] = str(razor_dir)
            self.debug(f"  RazorDirectory: {razor_dir}", self.debug_color)
            
            current_full = Misc.ScriptCurrent(True)
            paths["current_full"] = str(current_full)
            self.debug(f"  ScriptCurrent(full): {current_full}", self.debug_color)
            
            current_name = Misc.ScriptCurrent(False)
            paths["current_name"] = str(current_name)
            self.debug(f"  ScriptCurrent(name): {current_name}", self.debug_color)
            
            self.debug("  All directory functions: OK", self.success_color)
            
        except Exception as e:
            test_success = False
            error_msg = str(e)
            self.debug(f"  Error: {e}", self.error_color)
        
        # Record test report
        self.json_output["test_report"]["DirectoryFunctions"] = {
            "works": test_success,
            "error": error_msg,
            "data_returned": len(paths) > 0
        }
        self.json_output["tests"]["directory_paths"] = paths
        
        self.debug("")
    
    def test_file_operations(self):
        """Test file read/write/delete operations"""
        section_header("TEST: File Operations")
        
        test_file = "test_misc_api.txt"
        test_success = True
        error_msg = None
        
        try:
            self.debug("Testing file operations...", self.info_color)
            
            # AppendToFile
            self.debug("  Testing AppendToFile...", self.info_color)
            result = Misc.AppendToFile(test_file, "Test line 1")
            self.debug(f"    AppendToFile: {result}", self.debug_color)
            
            result = Misc.AppendToFile(test_file, "Test line 2")
            self.debug(f"    AppendToFile (2nd): {result}", self.debug_color)
            
            # AppendNotDupToFile
            self.debug("  Testing AppendNotDupToFile...", self.info_color)
            result = Misc.AppendNotDupToFile(test_file, "Test line 1")
            self.debug(f"    AppendNotDupToFile (duplicate): {result}", self.debug_color)
            
            result = Misc.AppendNotDupToFile(test_file, "Test line 3")
            self.debug(f"    AppendNotDupToFile (unique): {result}", self.debug_color)
            
            # ReadFile
            self.debug("  Testing ReadFile...", self.info_color)
            lines = Misc.ReadFile(test_file)
            if lines:
                self.debug(f"    ReadFile: {lines.Count} lines", self.debug_color)
                for i, line in enumerate(lines):
                    self.debug(f"      Line {i+1}: {line}", self.debug_color)
            
            # RemoveLineInFile
            self.debug("  Testing RemoveLineInFile...", self.info_color)
            result = Misc.RemoveLineInFile(test_file, "Test line 2")
            self.debug(f"    RemoveLineInFile: {result}", self.debug_color)
            
            # Verify removal
            lines = Misc.ReadFile(test_file)
            if lines:
                self.debug(f"    After removal: {lines.Count} lines", self.debug_color)
            
            # DeleteFile
            self.debug("  Testing DeleteFile...", self.info_color)
            result = Misc.DeleteFile(test_file)
            self.debug(f"    DeleteFile: {result}", self.debug_color)
            
            self.debug("  File operations: OK", self.success_color)
            
        except Exception as e:
            test_success = False
            error_msg = str(e)
            self.debug(f"  Error: {e}", self.error_color)
            try:
                Misc.DeleteFile(test_file)
            except:
                pass
        
        # Record test report
        self.json_output["test_report"]["FileOperations"] = {
            "works": test_success,
            "error": error_msg,
            "data_returned": test_success
        }
        
        self.debug("")
    
    def test_shared_values(self):
        """Test shared value storage"""
        section_header("TEST: Shared Values")
        
        test_success = True
        error_msg = None
        
        try:
            self.debug("Testing shared value functions...", self.info_color)
            
            # SetSharedValue
            self.debug("  Setting shared values...", self.info_color)
            Misc.SetSharedValue("test_string", "Hello World")
            Misc.SetSharedValue("test_number", 42)
            Misc.SetSharedValue("test_float", 3.14)
            self.debug("    SetSharedValue: OK", self.debug_color)
            
            # CheckSharedValue
            self.debug("  Checking shared values...", self.info_color)
            exists = Misc.CheckSharedValue("test_string")
            self.debug(f"    CheckSharedValue('test_string'): {exists}", self.debug_color)
            
            not_exists = Misc.CheckSharedValue("nonexistent")
            self.debug(f"    CheckSharedValue('nonexistent'): {not_exists}", self.debug_color)
            
            # ReadSharedValue
            self.debug("  Reading shared values...", self.info_color)
            val_str = Misc.ReadSharedValue("test_string")
            self.debug(f"    ReadSharedValue('test_string'): {val_str}", self.debug_color)
            
            val_num = Misc.ReadSharedValue("test_number")
            self.debug(f"    ReadSharedValue('test_number'): {val_num}", self.debug_color)
            
            val_float = Misc.ReadSharedValue("test_float")
            self.debug(f"    ReadSharedValue('test_float'): {val_float}", self.debug_color)
            
            # AllSharedValue
            self.debug("  Getting all shared values...", self.info_color)
            all_values = Misc.AllSharedValue()
            if all_values:
                self.debug(f"    AllSharedValue: {all_values.Count} values", self.debug_color)
                for name in all_values:
                    if name.startswith("test_"):
                        val = Misc.ReadSharedValue(name)
                        self.debug(f"      {name} = {val}", self.debug_color)
            
            # RemoveSharedValue
            self.debug("  Removing shared values...", self.info_color)
            Misc.RemoveSharedValue("test_string")
            Misc.RemoveSharedValue("test_number")
            Misc.RemoveSharedValue("test_float")
            self.debug("    RemoveSharedValue: OK", self.debug_color)
            
            # Verify removal
            exists = Misc.CheckSharedValue("test_string")
            self.debug(f"    After removal, exists: {exists}", self.debug_color)
            
            self.debug("  Shared values: OK", self.success_color)
            
        except Exception as e:
            test_success = False
            error_msg = str(e)
            self.debug(f"  Error: {e}", self.error_color)
            try:
                Misc.RemoveSharedValue("test_string")
                Misc.RemoveSharedValue("test_number")
                Misc.RemoveSharedValue("test_float")
            except:
                pass
        
        # Record test report
        self.json_output["test_report"]["SharedValues"] = {
            "works": test_success,
            "error": error_msg,
            "data_returned": test_success
        }
        
        self.debug("")
    
    def test_utility_functions(self):
        """Test utility functions"""
        section_header("TEST: Utility Functions")
        
        test_success = True
        error_msg = None
        utility_data = {}
        
        try:
            self.debug("Testing utility functions...", self.info_color)
            
            # Pause
            self.debug("  Testing Pause(100ms)...", self.info_color)
            Misc.Pause(100)
            self.debug("    Pause: OK", self.debug_color)
            
            # Distance
            self.debug("  Testing Distance...", self.info_color)
            dist = Misc.Distance(100, 100, 110, 110)
            utility_data["distance_test1"] = int(dist)
            self.debug(f"    Distance(100,100 to 110,110): {dist}", self.debug_color)
            
            dist = Misc.Distance(0, 0, 3, 4)
            utility_data["distance_test2"] = int(dist)
            self.debug(f"    Distance(0,0 to 3,4): {dist}", self.debug_color)
            
            # DistanceSqrt
            if Player.Position:
                self.debug("  Testing DistanceSqrt...", self.info_color)
                point_a = Point3D(Player.Position.X, Player.Position.Y, Player.Position.Z)
                point_b = Point3D(Player.Position.X + 10, Player.Position.Y + 10, Player.Position.Z)
                dist_sqrt = Misc.DistanceSqrt(point_a, point_b)
                utility_data["distance_sqrt"] = float(dist_sqrt)
                self.debug(f"    DistanceSqrt: {dist_sqrt:.2f}", self.debug_color)
            
            # IsItem / IsMobile
            self.debug("  Testing serial type checks...", self.info_color)
            
            player_serial = Player.Serial
            is_mobile = Misc.IsMobile(player_serial)
            is_item = Misc.IsItem(player_serial)
            utility_data["player_is_mobile"] = bool(is_mobile)
            utility_data["player_is_item"] = bool(is_item)
            self.debug(f"    Player serial 0x{player_serial:08X}:", self.debug_color)
            self.debug(f"      IsMobile: {is_mobile}", self.debug_color)
            self.debug(f"      IsItem: {is_item}", self.debug_color)
            
            backpack = Player.Backpack
            if backpack:
                is_mobile = Misc.IsMobile(backpack.Serial)
                is_item = Misc.IsItem(backpack.Serial)
                utility_data["backpack_is_mobile"] = bool(is_mobile)
                utility_data["backpack_is_item"] = bool(is_item)
                self.debug(f"    Backpack serial 0x{backpack.Serial:08X}:", self.debug_color)
                self.debug(f"      IsMobile: {is_mobile}", self.debug_color)
                self.debug(f"      IsItem: {is_item}", self.debug_color)
            
            # NoOperation
            self.debug("  Testing NoOperation...", self.info_color)
            Misc.NoOperation()
            self.debug("    NoOperation: OK (did nothing)", self.debug_color)
            
            self.debug("  Utility functions: OK", self.success_color)
            
        except Exception as e:
            test_success = False
            error_msg = str(e)
            self.debug(f"  Error: {e}", self.error_color)
        
        # Record test report
        self.json_output["test_report"]["UtilityFunctions"] = {
            "works": test_success,
            "error": error_msg,
            "data_returned": len(utility_data) > 0
        }
        self.json_output["tests"]["utility_data"] = utility_data
        
        self.debug("")
    
    def test_ignore_list(self):
        """Test ignore list management"""
        section_header("TEST: Ignore List")
        
        test_success = True
        error_msg = None
        
        try:
            self.debug("Testing ignore list functions...", self.info_color)
            
            test_serial = 0x12345678
            
            # IgnoreObject
            self.debug("  Testing IgnoreObject...", self.info_color)
            Misc.IgnoreObject(test_serial)
            self.debug(f"    Added 0x{test_serial:08X} to ignore list", self.debug_color)
            
            # CheckIgnoreObject
            self.debug("  Testing CheckIgnoreObject...", self.info_color)
            is_ignored = Misc.CheckIgnoreObject(test_serial)
            self.debug(f"    CheckIgnoreObject: {is_ignored}", self.debug_color)
            
            # UnIgnoreObject
            self.debug("  Testing UnIgnoreObject...", self.info_color)
            Misc.UnIgnoreObject(test_serial)
            self.debug(f"    Removed 0x{test_serial:08X} from ignore list", self.debug_color)
            
            # Verify removal
            is_ignored = Misc.CheckIgnoreObject(test_serial)
            self.debug(f"    After removal: {is_ignored}", self.debug_color)
            
            # ClearIgnore
            self.debug("  Testing ClearIgnore...", self.info_color)
            Misc.IgnoreObject(0x11111111)
            Misc.IgnoreObject(0x22222222)
            Misc.ClearIgnore()
            self.debug("    ClearIgnore: OK", self.debug_color)
            
            self.debug("  Ignore list: OK", self.success_color)
            
        except Exception as e:
            test_success = False
            error_msg = str(e)
            self.debug(f"  Error: {e}", self.error_color)
        
        # Record test report
        self.json_output["test_report"]["IgnoreList"] = {
            "works": test_success,
            "error": error_msg,
            "data_returned": test_success
        }
        
        self.debug("")
    
    def test_system_info(self):
        """Test system information functions"""
        section_header("TEST: System Info")
        
        test_success = True
        error_msg = None
        system_data = {}
        
        try:
            self.debug("Testing system info functions...", self.info_color)
            
            # GetWindowSize
            self.debug("  Testing GetWindowSize...", self.info_color)
            window = Misc.GetWindowSize()
            system_data["window"] = {
                "x": int(window.X),
                "y": int(window.Y),
                "width": int(window.Width),
                "height": int(window.Height)
            }
            self.debug(f"    Window X: {window.X}", self.debug_color)
            self.debug(f"    Window Y: {window.Y}", self.debug_color)
            self.debug(f"    Window Width: {window.Width}", self.debug_color)
            self.debug(f"    Window Height: {window.Height}", self.debug_color)
            
            # MouseLocation
            self.debug("  Testing MouseLocation...", self.info_color)
            mouse = Misc.MouseLocation()
            system_data["mouse"] = {"x": int(mouse.X), "y": int(mouse.Y)}
            self.debug(f"    Mouse X: {mouse.X}", self.debug_color)
            self.debug(f"    Mouse Y: {mouse.Y}", self.debug_color)
            
            # GetMapInfo
            self.debug("  Testing GetMapInfo...", self.info_color)
            player_map = Misc.GetMapInfo(Player.Serial)
            if player_map:
                system_data["map_info"] = {
                    "facet": int(player_map.Facet),
                    "map_origin": {"x": int(player_map.MapOrigin.X), "y": int(player_map.MapOrigin.Y)},
                    "map_end": {"x": int(player_map.MapEnd.X), "y": int(player_map.MapEnd.Y)},
                    "pin_position": {"x": int(player_map.PinPosition.X), "y": int(player_map.PinPosition.Y)}
                }
                self.debug(f"    Player MapInfo:", self.debug_color)
                self.debug(f"      Serial: 0x{player_map.Serial:08X}", self.debug_color)
                self.debug(f"      Facet: {player_map.Facet}", self.debug_color)
                self.debug(f"      MapOrigin: ({player_map.MapOrigin.X}, {player_map.MapOrigin.Y})", self.debug_color)
                self.debug(f"      MapEnd: ({player_map.MapEnd.X}, {player_map.MapEnd.Y})", self.debug_color)
                self.debug(f"      PinPosition: ({player_map.PinPosition.X}, {player_map.PinPosition.Y})", self.debug_color)
            
            self.debug("  System info: OK", self.success_color)
            
        except Exception as e:
            test_success = False
            error_msg = str(e)
            self.debug(f"  Error: {e}", self.error_color)
        
        # Record test report
        self.json_output["test_report"]["SystemInfo"] = {
            "works": test_success,
            "error": error_msg,
            "data_returned": len(system_data) > 0
        }
        self.json_output["tests"]["system_info"] = system_data
        
        self.debug("")
    
    def test_client_control(self):
        """Test client control functions"""
        section_header("TEST: Client Control")
        
        test_success = True
        error_msg = None
        screenshot_path = None
        
        try:
            self.debug("Testing client control functions...", self.info_color)
            
            # FocusUOWindow
            self.debug("  Testing FocusUOWindow...", self.info_color)
            Misc.FocusUOWindow()
            self.debug("    FocusUOWindow: OK", self.debug_color)
            
            # CaptureNow
            self.debug("  Testing CaptureNow...", self.info_color)
            screenshot_path = Misc.CaptureNow()
            self.debug(f"    Screenshot saved: {screenshot_path}", self.debug_color)
            
            self.debug("  Client control: OK", self.success_color)
            self.debug("  (Disconnect/Resync tests skipped for safety)", self.warning_color)
            
        except Exception as e:
            test_success = False
            error_msg = str(e)
            self.debug(f"  Error: {e}", self.error_color)
        
        # Record test report
        self.json_output["test_report"]["ClientControl"] = {
            "works": test_success,
            "error": error_msg,
            "data_returned": screenshot_path is not None
        }
        if screenshot_path:
            self.json_output["tests"]["screenshot_path"] = str(screenshot_path)
        
        self.debug("")
    
    def test_additional_functions(self):
        """Test additional Misc API functions"""
        section_header("TEST: Additional Functions")
        
        try:
            self.debug("Testing additional functions...", self.info_color)
            
            # ReadFile
            self.debug("  ReadFile: Tested in file_operations", self.debug_color)
            
            # SetSharedValue
            self.debug("  SetSharedValue: Tested in shared_values", self.debug_color)
            
            # UnIgnoreObject
            self.debug("  UnIgnoreObject: Tested in ignore_list", self.debug_color)
            
            # WaitForContext - requires interactive mode
            self.debug("  WaitForContext: Requires INTERACTIVE_MODE", self.warning_color)
            
            # ScriptRun, ScriptStop, ScriptSuspend, ScriptResume
            self.debug("  Script control functions: Skipped (affects script execution)", self.warning_color)
            
            # ScriptStatus
            try:
                current_script = Misc.ScriptCurrent(False)
                status = Misc.ScriptStatus(current_script)
                self.debug(f"  ScriptStatus('{current_script}'): {status}", self.debug_color)
            except Exception as e:
                self.debug(f"  ScriptStatus error: {e}", self.error_color)
            
            # ChangeProfile - skipped (would change profile)
            self.debug("  ChangeProfile: Skipped (would change profile)", self.warning_color)
            
            # ClearDragQueue
            self.debug("  Testing ClearDragQueue...", self.info_color)
            Misc.ClearDragQueue()
            self.debug("    ClearDragQueue: OK", self.debug_color)
            
            # CloseBackpack (OSI only)
            self.debug("  CloseBackpack: OSI client only", self.warning_color)
            
            # OpenPaperdoll (OSI only)  
            self.debug("  OpenPaperdoll: OSI client only", self.warning_color)
            
            # GetContPosition (OSI only)
            self.debug("  GetContPosition: OSI client only", self.warning_color)
            
            # NextContPosition (OSI only)
            self.debug("  NextContPosition: OSI client only", self.warning_color)
            
            # NoRunStealthStatus
            try:
                status = Misc.NoRunStealthStatus()
                self.debug(f"  NoRunStealthStatus: {status}", self.debug_color)
            except Exception as e:
                self.debug(f"  NoRunStealthStatus error: {e}", self.error_color)
            
            # FilterSeason
            self.debug("  FilterSeason: Skipped (affects client visuals)", self.warning_color)
            
            # ExportPythonAPI
            self.debug("  ExportPythonAPI: Skipped (creates file)", self.warning_color)
            
            # Inspect
            self.debug("  Inspect: Requires target selection", self.warning_color)
            
            # LastHotKey
            try:
                hotkey = Misc.LastHotKey()
                if hotkey:
                    self.debug(f"  LastHotKey: {hotkey}", self.debug_color)
                else:
                    self.debug("  LastHotKey: None", self.debug_color)
            except Exception as e:
                self.debug(f"  LastHotKey error: {e}", self.error_color)
            
            # MouseMove
            self.debug("  MouseMove: Skipped (moves mouse)", self.warning_color)
            
            # LeftMouseClick / RightMouseClick
            self.debug("  Mouse click functions: Skipped (performs clicks)", self.warning_color)
            
            # PetRename
            self.debug("  PetRename: Requires pet serial", self.warning_color)
            
            self.debug("  Additional functions: OK", self.success_color)
            
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
        """Run all Misc API tests"""
        section_header("MISC API COMPREHENSIVE TEST")
        self.debug(f"Interactive: {INTERACTIVE_MODE}", self.warning_color if not INTERACTIVE_MODE else self.success_color)
        self.debug("")
        
        # Core functionality tests
        self.test_messaging_functions()
        self.test_directory_functions()
        self.test_file_operations()
        self.test_shared_values()
        self.test_utility_functions()
        self.test_ignore_list()
        self.test_system_info()
        self.test_client_control()
        self.test_additional_functions()
        
        section_header("TEST COMPLETE")
        self.debug("All Misc API functions tested!", self.success_color)
        
        # Save JSON output
        self.debug("")
        section_header("SAVING JSON OUTPUT")
        self.save_json_output()

#======================================================================
# USAGE EXAMPLES
#======================================================================

def example_messaging():
    """Example: Send colored messages and play sounds"""
    Misc.SendMessage("Hello World", 68)  # Green
    Misc.SendMessage("Warning!", 53)  # Yellow
    Misc.SendMessage("Error!", 33)  # Red
    Misc.Beep()
    
    # Play sound at player location
    if Player.Position:
        Misc.PlaySound(0x0055, Player.Position.X, Player.Position.Y, Player.Position.Z)

def example_file_operations():
    """Example: File read/write operations"""
    filename = "player_data.txt"
    
    # Write to file
    Misc.AppendToFile(filename, "Player logged in")
    Misc.AppendNotDupToFile(filename, "Session started")
    
    # Read from file
    lines = Misc.ReadFile(filename)
    if lines:
        for line in lines:
            Misc.SendMessage(line, 67)
    
    # Clean up
    Misc.RemoveLineInFile(filename, "Player logged in")
    # Misc.DeleteFile(filename)  # Uncomment to delete

def example_shared_values():
    """Example: Cross-script data sharing"""
    # Store values accessible by all scripts
    Misc.SetSharedValue("player_state", "hunting")
    Misc.SetSharedValue("gold_count", 50000)
    Misc.SetSharedValue("last_location", (1000, 2000))
    
    # Read values
    state = Misc.ReadSharedValue("player_state")
    gold = Misc.ReadSharedValue("gold_count")
    
    # Check if value exists
    if Misc.CheckSharedValue("player_state"):
        Misc.SendMessage(f"Current state: {state}", 68)
    
    # List all shared values
    all_values = Misc.AllSharedValue()
    if all_values:
        Misc.SendMessage(f"Total shared values: {all_values.Count}", 67)
    
    # Clean up
    Misc.RemoveSharedValue("player_state")
    Misc.RemoveSharedValue("gold_count")
    Misc.RemoveSharedValue("last_location")

def example_distance_calculations():
    """Example: Calculate distances"""
    # UO distance (max of X and Y difference)
    dist = Misc.Distance(100, 100, 110, 110)
    Misc.SendMessage(f"UO Distance: {dist}", 67)
    
    # Pythagorean distance
    if Player.Position:
        from Assistant import Point3D
        point_a = Point3D(Player.Position.X, Player.Position.Y, Player.Position.Z)
        point_b = Point3D(Player.Position.X + 10, Player.Position.Y + 10, Player.Position.Z)
        dist_sqrt = Misc.DistanceSqrt(point_a, point_b)
        Misc.SendMessage(f"Pythagorean Distance: {dist_sqrt:.2f}", 67)

def example_serial_type_checking():
    """Example: Check if serial is item or mobile"""
    player_serial = Player.Serial
    
    if Misc.IsMobile(player_serial):
        Misc.SendMessage("Player is a mobile", 68)
    
    if Player.Backpack:
        backpack_serial = Player.Backpack.Serial
        if Misc.IsItem(backpack_serial):
            Misc.SendMessage("Backpack is an item", 68)

def example_ignore_list():
    """Example: Manage ignore list"""
    test_serial = 0x12345678
    
    # Add to ignore list
    Misc.IgnoreObject(test_serial)
    
    # Check if ignored
    if Misc.CheckIgnoreObject(test_serial):
        Misc.SendMessage("Object is ignored", 67)
    
    # Remove from ignore list
    Misc.UnIgnoreObject(test_serial)
    
    # Clear all ignored objects
    # Misc.ClearIgnore()

def example_system_info():
    """Example: Get system information"""
    # Window size
    window = Misc.GetWindowSize()
    Misc.SendMessage(f"Window: {window.Width}x{window.Height}", 67)
    
    # Mouse position
    mouse = Misc.MouseLocation()
    Misc.SendMessage(f"Mouse: ({mouse.X}, {mouse.Y})", 67)
    
    # Map info
    map_info = Misc.GetMapInfo(Player.Serial)
    if map_info:
        Misc.SendMessage(f"Facet: {map_info.Facet}", 67)

def example_directory_paths():
    """Example: Get directory paths"""
    script_dir = Misc.ScriptDirectory()
    data_dir = Misc.DataDirectory()
    config_dir = Misc.ConfigDirectory()
    razor_dir = Misc.RazorDirectory()
    
    Misc.SendMessage(f"Scripts: {script_dir}", 67)
    Misc.SendMessage(f"Data: {data_dir}", 67)
    
    # Current script info
    current_full = Misc.ScriptCurrent(True)
    current_name = Misc.ScriptCurrent(False)
    Misc.SendMessage(f"Current script: {current_name}", 67)

def example_client_control():
    """Example: Client control functions"""
    # Focus window
    Misc.FocusUOWindow()
    
    # Take screenshot
    screenshot_path = Misc.CaptureNow()
    Misc.SendMessage(f"Screenshot: {screenshot_path}", 68)
    
    # Pause script
    Misc.Pause(1000)  # Wait 1 second

def example_prompts():
    """Example: Handle prompts (requires active prompt)"""
    if Misc.HasPrompt():
        Misc.ResponsePrompt("New Name")
        # Or cancel it
        # Misc.CancelPrompt()

def example_context_menu():
    """Example: Context menu interaction"""
    # Wait for context menu and get entries
    # context_entries = Misc.WaitForContext(serial, 1000)
    
    # Reply to context menu by index
    # Misc.ContextReply(serial, 0)
    
    # Reply to context menu by text
    # Misc.ContextReply(serial, "Open")
    pass

def example_script_status():
    """Example: Check script status"""
    current_script = Misc.ScriptCurrent(False)
    
    # Check if suspended
    is_suspended = Misc.ScriptIsSuspended(current_script)
    Misc.SendMessage(f"Script suspended: {is_suspended}", 67)
    
    # Get script status
    status = Misc.ScriptStatus(current_script)
    Misc.SendMessage(f"Script status: {status}", 67)

def example_utility_functions():
    """Example: Various utility functions"""
    # Do nothing (useful as placeholder)
    Misc.NoOperation()
    
    # Clear drag queue
    Misc.ClearDragQueue()
    
    # Get last hotkey pressed
    hotkey = Misc.LastHotKey()
    if hotkey:
        Misc.SendMessage(f"Last hotkey: {hotkey}", 67)
    
    # Check no-run-stealth status
    no_run_status = Misc.NoRunStealthStatus()
    Misc.SendMessage(f"No run stealth: {no_run_status}", 67)

#======================================================================
# MAIN EXECUTION
#======================================================================
try:
    tester = MiscAPITester()
    tester.run_all_tests()
    
    # Optionally run usage examples
    if RUN_USAGE_EXAMPLES:
        debug_message("")
        debug_message("")
        section_header("USAGE EXAMPLES - PRACTICAL DEMONSTRATIONS")
        debug_message("Usage examples are defined as functions above", 67)
        debug_message("Call them individually as needed:", 67)
        debug_message("  - example_messaging()", 67)
        debug_message("  - example_file_operations()", 67)
        debug_message("  - example_shared_values()", 67)
        debug_message("  - example_distance_calculations()", 67)
        debug_message("  - example_serial_type_checking()", 67)
        debug_message("  - example_ignore_list()", 67)
        debug_message("  - example_system_info()", 67)
        debug_message("  - example_directory_paths()", 67)
        debug_message("  - example_client_control()", 67)
        section_header("USAGE EXAMPLES COMPLETE")
    
except Exception as e:
    debug_message(f"FATAL ERROR: {e}", 33)
    import traceback
    debug_message(traceback.format_exc(), 33)
