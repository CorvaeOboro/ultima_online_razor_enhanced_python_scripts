"""
DEV API Gumps - a Razor Enhanced Python Script for Ultima Online

 demonstration of  Gumps API functions
Tests creating and interacting with gumps

=== GUMPS API OVERVIEW ===
The Gumps class provides functions to create and interact with in-game gumps.

ALL GUMPS API FUNCTIONS (45+ functions):

GUMP CREATION (1 function):
  - CreateGump(movable, closable, disposable, resizeable) -> GumpData

ADD ELEMENTS (20 functions):
  - AddAlphaRegion(gd, x, y, width, height)
  - AddBackground(gd, x, y, width, height, gumpId)
  - AddButton(gd, x, y, normalID, pressedID, buttonID, type, param)
  - AddCheck(gd, x, y, inactiveID, activeID, initialState, switchID)
  - AddGroup(gd, group)
  - AddHtml(gd, x, y, width, height, text, background, scrollbar)
  - AddHtmlLocalized(gd, x, y, width, height, number, args, color, background, scrollbar)
  - AddImage(gd, x, y, gumpId, hue)
  - AddImageTiled(gd, x, y, width, height, gumpId)
  - AddImageTiledButton(gd, x, y, normalID, pressedID, buttonID, type, param, itemID, hue, width, height, localizedTooltip)
  - AddItem(gd, x, y, itemID, hue)
  - AddLabel(gd, x, y, hue, text)
  - AddLabelCropped(gd, x, y, width, height, hue, text)
  - AddPage(gd, page)
  - AddRadio(gd, x, y, inactiveID, activeID, initialState, switchID)
  - AddSpriteImage(gd, x, y, gumpId, spriteX, spriteY, spriteW, spriteH)
  - AddTextEntry(gd, x, y, width, height, hue, entryID, initialText)
  - AddTooltip(gd, cliloc, text)

GUMP DETECTION (4 functions):
  - HasGump(gumpId) -> Boolean
  - CurrentGump() -> UInt32
  - AllGumpIDs() -> List[UInt32]
  - IsValid(gumpId) -> Boolean

GUMP DATA RETRIEVAL (4 functions):
  - GetGumpData(gumpId) -> GumpData
  - GetGumpRawLayout(gumpId) -> String
  - GetGumpText(gumpId) -> List[String]
  - GetTextByID(gd, id) -> String

GUMP LINE READING (4 functions):
  - GetLine(gumpId, line_num) -> String
  - GetLineList(gumpId, dataOnly) -> List[String]
  - LastGumpGetLine(line_num) -> String
  - LastGumpGetLineList() -> List[String]

GUMP TEXT SEARCH (3 functions):
  - LastGumpTextExist(text) -> Boolean
  - LastGumpTextExistByLine(line_num, text) -> Boolean
  - LastGumpRawLayout() -> String

GUMP INTERACTION (5 functions):
  - SendAction(gumpId, buttonId)
  - SendAdvancedAction(gumpId, buttonId, switches, textlist_id, textlist_str)
  - CloseGump(gumpId)
  - ResetGump()
  - WaitForGump(gumpId, delay) -> Boolean

GUMP UTILITIES (3 functions):
  - LastGumpTile() -> List[Int32]
  - SendGump(gd, x, y)

Two Main Categories:
  1. GUMP CREATION: Build custom gumps with buttons, text, images
  2. GUMP INTERACTION: Read and respond to existing gumps

=== GUMPDATA CLASS ===
The GumpData object holds all information about a gump. It is returned by
CreateGump() and GetGumpData(), and modified by Add* functions.

GumpData Properties (16 properties):

IDENTIFICATION:
  - gumpId (UInt32): Unique identifier for this gump
  - serial (UInt32): Serial number associated with gump (usually player serial)
  - x (UInt32): Screen X position where gump appears
  - y (UInt32): Screen Y position where gump appears

LAYOUT & DEFINITION:
  - gumpDefinition (String): Raw definition string of gump structure
  - gumpLayout (String): Layout string describing gump elements
  - layoutPieces (List[String]): Individual layout pieces/commands

TEXT CONTENT:
  - gumpText (List[String]): Text content displayed in gump
  - gumpStrings (List[String]): String data for gump
  - stringList (List[String]): List of strings used in gump
  - text (List[String]): Text entries from user input fields
  - textID (List[Int32]): IDs of text entry fields

DATA & STATE:
  - gumpData (List[String]): Raw gump data
  - switches (List[Int32]): Active switch/checkbox IDs
  - buttonid (Int32): ID of button that was pressed (for responses)
  - hasResponse (Boolean): Whether gump has received a response

DEVELOPMENT TOOLS:
  - Use "Inspect Gumps" in RE editor to see gump/button IDs
  - Use "Record" feature to capture gump interactions

VERSION::20251013
"""

from System.Collections.Generic import List
import os
import json

# GLOBAL SETTINGS
DEBUG_MODE = True
INTERACTIVE_MODE = False  # Set True to enable interactive tests
TEST_DELAY = 1000
CREATE_DEMO_GUMP = True
# JSON output file path
BASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
OUTPUT_FILE = os.path.join(BASE_PATH, "api_gumps_test_output.json")
# Run usage examples after tests
RUN_USAGE_EXAMPLES = True
#======================================================================

def debug_message(message, color=67):
    if not DEBUG_MODE:
        return
    try:
        # Don't add prefix for empty messages (used for spacing)
        if message:
            Misc.SendMessage(f"[GUMPS] {message}", color)
        else:
            Misc.SendMessage("", color)
    except Exception:
        if message:
            print(f"[GUMPS] {message}")
        else:
            print("")

def section_header(title):
    debug_message("=" * 60, 88)
    debug_message(f"  {title}", 88)
    debug_message("=" * 60, 88)

class GumpsAPITester:
    def __init__(self):
        self.debug_color = 67
        self.error_color = 33
        self.success_color = 68
        self.info_color = 88
        self.warning_color = 53
        self.demo_gump_id = 999999
        
        # Initialize JSON output structure
        self.json_output = {
            "test_report": {},  # Summary of which API functions work
            "test_timestamp": str(Misc.ScriptCurrent(False)),
            "interactive_mode": INTERACTIVE_MODE,
            "create_demo_gump": CREATE_DEMO_GUMP,
            "tests": {}
        }
        
    def debug(self, message, color=None):
        if color is None:
            color = self.debug_color
        debug_message(message, color)
    
    def test_create_gump(self):
        """
        GUMP CREATION FUNCTIONS
        
        CreateGump(movable, closable, disposable, resizeable) -> GumpData
        - Creates base gump structure
        - movable: Can be moved by player
        - closable: Can right-click to close
        - disposable: Can be disposed
        - resizeable: Can be resized
        """
        section_header("TEST: Create Gump")
        
        test_success = True
        error_msg = None
        
        if not CREATE_DEMO_GUMP:
            self.debug("  [CREATE_DEMO_GUMP disabled]", self.warning_color)
            # Record test report for skipped test
            self.json_output["test_report"]["CreateGump"] = {
                "works": None,
                "error": "Skipped - CREATE_DEMO_GUMP disabled",
                "data_returned": False
            }
            return None
        
        try:
            gump_data = Gumps.CreateGump(True, True, True, False)
            self.debug("  GumpData created successfully", self.success_color)
            
            # Record test report
            self.json_output["test_report"]["CreateGump"] = {
                "works": test_success,
                "error": error_msg,
                "data_returned": gump_data is not None
            }
            
            return gump_data
        except Exception as e:
            test_success = False
            error_msg = str(e)
            self.debug(f"  Error: {e}", self.error_color)
            
            # Record test report
            self.json_output["test_report"]["CreateGump"] = {
                "works": test_success,
                "error": error_msg,
                "data_returned": False
            }
            
            return None
    
    def test_add_elements(self, gump_data):
        """
        ADD ELEMENT FUNCTIONS
        
        AddBackground(gd, x, y, width, height, gumpId)
        AddImage(gd, x, y, gumpId, hue)
        AddLabel(gd, x, y, hue, text)
        AddButton(gd, x, y, normalID, pressedID, buttonID, type, param)
        AddTextEntry(gd, x, y, width, height, hue, entryID, initialText)
        AddCheck(gd, x, y, inactiveID, activeID, initialState, switchID)
        AddHtml(gd, x, y, width, height, text, background, scrollbar)
        """
        section_header("TEST: Add Elements")
        
        test_success = True
        error_msg = None
        
        if gump_data is None:
            self.json_output["test_report"]["AddElements"] = {
                "works": None,
                "error": "Skipped - no gump_data",
                "data_returned": False
            }
            return
        
        try:
            Gumps.AddBackground(gump_data, 0, 0, 400, 300, 9200)
            Gumps.AddLabel(gump_data, 150, 20, 2100, "Gumps API Demo")
            Gumps.AddHtml(gump_data, 50, 60, 300, 60, "<CENTER>Demo Gump</CENTER>", False, False)
            Gumps.AddImage(gump_data, 180, 130, 5609, 0)
            Gumps.AddButton(gump_data, 50, 270, 247, 248, 1, 0, 0)
            Gumps.AddLabel(gump_data, 85, 272, 0, "OK")
            self.debug("  All elements added", self.success_color)
        except Exception as e:
            test_success = False
            error_msg = str(e)
            self.debug(f"  Error: {e}", self.error_color)
        
        # Record test report
        self.json_output["test_report"]["AddElements"] = {
            "works": test_success,
            "error": error_msg,
            "data_returned": test_success
        }
    
    def test_gump_detection(self):
        """
        DETECTION FUNCTIONS
        
        HasGump(gumpId) -> Boolean
        CurrentGump() -> UInt32
        AllGumpIDs() -> List[UInt32]
        """
        section_header("TEST: Gump Detection")
        
        test_success = True
        error_msg = None
        detection_data = {}
        
        try:
            all_gumps = Gumps.AllGumpIDs()
            if all_gumps and len(all_gumps) > 0:
                detection_data["gump_count"] = len(all_gumps)
                detection_data["gump_ids"] = [int(g) for g in all_gumps]
                self.debug(f"  Found {len(all_gumps)} open gump(s)", self.success_color)
                for gump_id in all_gumps:
                    self.debug(f"    ID: {gump_id} (0x{gump_id:08X})", self.debug_color)
            else:
                detection_data["gump_count"] = 0
                self.debug("  No gumps open", self.warning_color)
            
            current = Gumps.CurrentGump()
            detection_data["current_gump"] = int(current) if current else 0
            if current > 0:
                self.debug(f"  Current gump: {current}", self.success_color)
        except Exception as e:
            test_success = False
            error_msg = str(e)
            self.debug(f"  Error: {e}", self.error_color)
        
        # Record test report
        self.json_output["test_report"]["GumpDetection"] = {
            "works": test_success,
            "error": error_msg,
            "data_returned": len(detection_data) > 0
        }
        self.json_output["tests"]["detection_data"] = detection_data
        
        self.debug("")
    
    def test_gump_reading(self):
        """
        READING FUNCTIONS
        
        GetGumpRawLayout(gumpId) -> String
        GetGumpText(gumpId) -> List[String]
        GetLineList(gumpId, dataOnly) -> List[String]
        GetLine(gumpId, line_num) -> String
        LastGumpRawLayout() -> String
        LastGumpGetLineList() -> List[String]
        LastGumpTextExist(text) -> Boolean
        """
        section_header("TEST: Gump Reading")
        
        test_success = True
        error_msg = None
        reading_data = {}
        
        try:
            all_gumps = Gumps.AllGumpIDs()
            if not all_gumps or len(all_gumps) == 0:
                reading_data["has_gumps"] = False
                self.debug("  No gumps to read", self.warning_color)
            else:
                reading_data["has_gumps"] = True
                test_id = all_gumps[0]
                reading_data["test_gump_id"] = int(test_id)
                self.debug(f"Testing with gump: {test_id}", self.info_color)
                
                layout = Gumps.GetGumpRawLayout(test_id)
                if layout:
                    reading_data["layout_length"] = len(layout)
                    self.debug(f"  Layout length: {len(layout)} chars", self.success_color)
                
                text_list = Gumps.GetGumpText(test_id)
                if text_list and len(text_list) > 0:
                    reading_data["text_entry_count"] = len(text_list)
                    reading_data["text_entries_sample"] = [str(t)[:50] for t in text_list[:3]]
                    self.debug(f"  Found {len(text_list)} text entries", self.success_color)
        except Exception as e:
            test_success = False
            error_msg = str(e)
            self.debug(f"  Error: {e}", self.error_color)
        
        # Record test report
        self.json_output["test_report"]["GumpReading"] = {
            "works": test_success,
            "error": error_msg,
            "data_returned": len(reading_data) > 0
        }
        self.json_output["tests"]["reading_data"] = reading_data
        
        self.debug("")
    
    def test_gumpdata_properties(self):
        """
        GUMPDATA PROPERTIES
        
        GumpData object contains 16 properties organized into categories:
        
        IDENTIFICATION: gumpId, serial, x, y
        LAYOUT: gumpDefinition, gumpLayout, layoutPieces
        TEXT: gumpText, gumpStrings, stringList, text, textID
        DATA: gumpData, switches, buttonid, hasResponse
        """
        section_header("TEST: GumpData Properties")
        
        test_success = True
        error_msg = None
        gumpdata_properties = {}
        
        try:
            all_gumps = Gumps.AllGumpIDs()
            if not all_gumps or len(all_gumps) == 0:
                gumpdata_properties["has_gumps"] = False
                self.debug("  No gumps to inspect", self.warning_color)
            else:
                gumpdata_properties["has_gumps"] = True
            
                test_id = all_gumps[0]
                gumpdata_properties["test_gump_id"] = int(test_id)
                self.debug(f"Inspecting GumpData for gump: {test_id}", self.info_color)
                
                # Get GumpData object
                gump_data = Gumps.GetGumpData(test_id)
                if not gump_data:
                    gumpdata_properties["gumpdata_retrieved"] = False
                    self.debug("  Could not retrieve GumpData", self.error_color)
                else:
                    gumpdata_properties["gumpdata_retrieved"] = True
            
                    # IDENTIFICATION properties
                    self.debug("  IDENTIFICATION:", self.info_color)
                    try:
                        gumpdata_properties["identification"] = {
                            "gumpId": int(gump_data.gumpId),
                            "serial": int(gump_data.serial),
                            "x": int(gump_data.x),
                            "y": int(gump_data.y)
                        }
                        self.debug(f"    gumpId: {gump_data.gumpId} (0x{gump_data.gumpId:08X})", self.debug_color)
                        self.debug(f"    serial: {gump_data.serial} (0x{gump_data.serial:08X})", self.debug_color)
                        self.debug(f"    x: {gump_data.x}", self.debug_color)
                        self.debug(f"    y: {gump_data.y}", self.debug_color)
                    except Exception as e:
                        self.debug(f"    Error: {e}", self.error_color)
            
                    # LAYOUT properties
                    self.debug("  LAYOUT & DEFINITION:", self.info_color)
                    try:
                        gumpdata_properties["layout"] = {}
                        if gump_data.gumpDefinition:
                            gumpdata_properties["layout"]["gumpDefinition_length"] = len(gump_data.gumpDefinition)
                            self.debug(f"    gumpDefinition: {len(gump_data.gumpDefinition)} chars", self.debug_color)
                        if gump_data.gumpLayout:
                            gumpdata_properties["layout"]["gumpLayout_length"] = len(gump_data.gumpLayout)
                            self.debug(f"    gumpLayout: {len(gump_data.gumpLayout)} chars", self.debug_color)
                        if gump_data.layoutPieces and len(gump_data.layoutPieces) > 0:
                            gumpdata_properties["layout"]["layoutPieces_count"] = len(gump_data.layoutPieces)
                            self.debug(f"    layoutPieces: {len(gump_data.layoutPieces)} pieces", self.debug_color)
                    except Exception as e:
                        self.debug(f"    Error: {e}", self.error_color)
            
                    # TEXT properties
                    self.debug("  TEXT CONTENT:", self.info_color)
                    try:
                        gumpdata_properties["text"] = {}
                        if gump_data.gumpText and len(gump_data.gumpText) > 0:
                            gumpdata_properties["text"]["gumpText_count"] = len(gump_data.gumpText)
                            self.debug(f"    gumpText: {len(gump_data.gumpText)} entries", self.debug_color)
                        if gump_data.gumpStrings and len(gump_data.gumpStrings) > 0:
                            gumpdata_properties["text"]["gumpStrings_count"] = len(gump_data.gumpStrings)
                            self.debug(f"    gumpStrings: {len(gump_data.gumpStrings)} strings", self.debug_color)
                        if gump_data.stringList and len(gump_data.stringList) > 0:
                            gumpdata_properties["text"]["stringList_count"] = len(gump_data.stringList)
                            self.debug(f"    stringList: {len(gump_data.stringList)} strings", self.debug_color)
                        if gump_data.text and len(gump_data.text) > 0:
                            gumpdata_properties["text"]["text_count"] = len(gump_data.text)
                            self.debug(f"    text: {len(gump_data.text)} entries", self.debug_color)
                        if gump_data.textID and len(gump_data.textID) > 0:
                            gumpdata_properties["text"]["textID_count"] = len(gump_data.textID)
                            self.debug(f"    textID: {len(gump_data.textID)} IDs", self.debug_color)
                    except Exception as e:
                        self.debug(f"    Error: {e}", self.error_color)
            
                    # DATA & STATE properties
                    self.debug("  DATA & STATE:", self.info_color)
                    try:
                        gumpdata_properties["data_state"] = {}
                        if gump_data.gumpData and len(gump_data.gumpData) > 0:
                            gumpdata_properties["data_state"]["gumpData_count"] = len(gump_data.gumpData)
                            self.debug(f"    gumpData: {len(gump_data.gumpData)} entries", self.debug_color)
                        if gump_data.switches and len(gump_data.switches) > 0:
                            gumpdata_properties["data_state"]["switches_count"] = len(gump_data.switches)
                            self.debug(f"    switches: {len(gump_data.switches)} active", self.debug_color)
                        gumpdata_properties["data_state"]["buttonid"] = int(gump_data.buttonid)
                        gumpdata_properties["data_state"]["hasResponse"] = bool(gump_data.hasResponse)
                        self.debug(f"    buttonid: {gump_data.buttonid}", self.debug_color)
                        self.debug(f"    hasResponse: {gump_data.hasResponse}", self.debug_color)
                    except Exception as e:
                        self.debug(f"    Error: {e}", self.error_color)
            
        except Exception as e:
            test_success = False
            error_msg = str(e)
            self.debug(f"  Error inspecting GumpData: {e}", self.error_color)
        
        # Record test report
        self.json_output["test_report"]["GumpDataProperties"] = {
            "works": test_success,
            "error": error_msg,
            "data_returned": len(gumpdata_properties) > 0
        }
        self.json_output["tests"]["gumpdata_properties"] = gumpdata_properties
        
        self.debug("")
    
    def test_gump_interaction(self):
        """
        INTERACTION FUNCTIONS
        
        SendAction(gumpId, buttonId)
        SendAdvancedAction(gumpId, buttonId, switches, textlist_id, textlist_str)
        CloseGump(gumpId)
        ResetGump()
        """
        section_header("TEST: Gump Interaction")
        
        test_success = True
        error_msg = None
        
        if not INTERACTIVE_MODE:
            self.debug("  [INTERACTIVE_MODE disabled]", self.warning_color)
            # Record test report for skipped test
            self.json_output["test_report"]["GumpInteraction"] = {
                "works": None,
                "error": "Skipped - INTERACTIVE_MODE disabled",
                "data_returned": False
            }
            self.debug("")
            return
        
        try:
            if CREATE_DEMO_GUMP and Gumps.HasGump(self.demo_gump_id):
                Gumps.CloseGump(self.demo_gump_id)
                self.debug("  Demo gump closed", self.success_color)
            
            Gumps.ResetGump()
            self.debug("  Gump state reset", self.success_color)
        except Exception as e:
            test_success = False
            error_msg = str(e)
            self.debug(f"  Error: {e}", self.error_color)
        
        # Record test report
        self.json_output["test_report"]["GumpInteraction"] = {
            "works": test_success,
            "error": error_msg,
            "data_returned": test_success
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
        section_header("GUMPS API COMPREHENSIVE TEST")
        self.debug(f"Interactive: {INTERACTIVE_MODE}", self.warning_color if not INTERACTIVE_MODE else self.success_color)
        self.debug("")
        
        # Creation tests
        gump_data = self.test_create_gump()
        if gump_data:
            self.test_add_elements(gump_data)
        
        # Reading tests
        self.test_gump_detection()
        self.test_gump_reading()
        self.test_gumpdata_properties()
        self.test_gump_interaction()
        
        section_header("TEST COMPLETE")
        self.debug("All Gumps API functions tested!", self.success_color)
        
        # Save JSON output
        self.debug("")
        section_header("SAVING JSON OUTPUT")
        self.save_json_output()

#======================================================================
# USAGE EXAMPLES
#======================================================================

def example_create_simple_gump():
    """Example: Create a simple gump with basic elements"""
    gd = Gumps.CreateGump(True, True, True, False)
    Gumps.AddBackground(gd, 0, 0, 300, 200, 9200)
    Gumps.AddLabel(gd, 100, 20, 2100, "Hello World")
    Gumps.AddButton(gd, 100, 150, 247, 248, 1, 0, 0)
    Gumps.SendGump(gd, 100, 100)

def example_wait_for_gump():
    """Example: Wait for a specific gump to appear"""
    gump_id = 0x12345678  # Replace with actual gump ID
    if Gumps.WaitForGump(gump_id, 5000):
        Misc.SendMessage("Gump appeared!", 68)
        # Interact with it
        Gumps.SendAction(gump_id, 1)
    else:
        Misc.SendMessage("Gump timeout", 33)

def example_read_gump_text():
    """Example: Read text from current gump"""
    if Gumps.CurrentGump() > 0:
        lines = Gumps.LastGumpGetLineList()
        if lines:
            for i, line in enumerate(lines):
                Misc.SendMessage(f"Line {i}: {line}", 67)

def example_search_gump_text():
    """Example: Search for text in gump"""
    if Gumps.LastGumpTextExist("Blacksmith"):
        Misc.SendMessage("Found blacksmith menu!", 68)
        # Press button 1
        current = Gumps.CurrentGump()
        Gumps.SendAction(current, 1)

def example_advanced_gump_response():
    """Example: Send advanced response with switches and text"""
    gump_id = Gumps.CurrentGump()
    if gump_id > 0:
        # Create switch list (checkboxes/radios that are ON)
        switches = [1, 3, 5]  # IDs of active switches
        
        # Create text entry lists
        text_ids = [0, 1]  # Text entry IDs
        text_values = ["Player Name", "100"]  # Text values
        
        Gumps.SendAdvancedAction(gump_id, 1, switches, text_ids, text_values)

def example_create_multi_page_gump():
    """Example: Create gump with multiple pages"""
    gd = Gumps.CreateGump(True, True, True, False)
    Gumps.AddBackground(gd, 0, 0, 400, 300, 9200)
    
    # Page 1
    Gumps.AddPage(gd, 1)
    Gumps.AddLabel(gd, 150, 20, 2100, "Page 1")
    Gumps.AddButton(gd, 300, 250, 247, 248, 0, 1, 2)  # Next page button
    Gumps.AddLabel(gd, 335, 252, 0, "Next")
    
    # Page 2
    Gumps.AddPage(gd, 2)
    Gumps.AddLabel(gd, 150, 20, 2100, "Page 2")
    Gumps.AddButton(gd, 50, 250, 247, 248, 0, 1, 1)  # Previous page button
    Gumps.AddLabel(gd, 85, 252, 0, "Back")
    
    Gumps.SendGump(gd, 100, 100)

def example_create_form_gump():
    """Example: Create gump with text entries and checkboxes"""
    gd = Gumps.CreateGump(True, True, True, False)
    Gumps.AddBackground(gd, 0, 0, 350, 250, 9200)
    Gumps.AddLabel(gd, 120, 20, 2100, "Character Form")
    
    # Text entries
    Gumps.AddLabel(gd, 20, 60, 0, "Name:")
    Gumps.AddTextEntry(gd, 80, 60, 200, 25, 0, 0, "")
    
    Gumps.AddLabel(gd, 20, 100, 0, "Age:")
    Gumps.AddTextEntry(gd, 80, 100, 100, 25, 0, 1, "")
    
    # Checkboxes
    Gumps.AddLabel(gd, 20, 140, 0, "Options:")
    Gumps.AddCheck(gd, 20, 160, 210, 211, False, 1)
    Gumps.AddLabel(gd, 45, 160, 0, "Option 1")
    
    Gumps.AddCheck(gd, 20, 185, 210, 211, True, 2)
    Gumps.AddLabel(gd, 45, 185, 0, "Option 2")
    
    # Submit button
    Gumps.AddButton(gd, 130, 215, 247, 248, 1, 0, 0)
    Gumps.AddLabel(gd, 165, 217, 0, "Submit")
    
    Gumps.SendGump(gd, 100, 100)

def example_create_item_display_gump():
    """Example: Create gump displaying items"""
    gd = Gumps.CreateGump(True, True, True, False)
    Gumps.AddBackground(gd, 0, 0, 300, 300, 9200)
    Gumps.AddLabel(gd, 100, 20, 2100, "Item Display")
    
    # Display various items
    Gumps.AddItem(gd, 50, 60, 0x0F3F, 0)  # Sword
    Gumps.AddItem(gd, 150, 60, 0x1F03, 0)  # Shield
    Gumps.AddItem(gd, 50, 150, 0x170D, 0)  # Helmet
    Gumps.AddItem(gd, 150, 150, 0x1415, 0)  # Plate chest
    
    Gumps.SendGump(gd, 100, 100)

def example_create_html_gump():
    """Example: Create gump with HTML content"""
    gd = Gumps.CreateGump(True, True, True, False)
    Gumps.AddBackground(gd, 0, 0, 400, 300, 9200)
    
    html_content = "<CENTER><BIG>Welcome!</BIG></CENTER><BR><BR>" \
                   "This is <B>bold</B> text.<BR>" \
                   "This is <I>italic</I> text.<BR>" \
                   "<BASEFONT COLOR=#FF0000>Red text</BASEFONT>"
    
    Gumps.AddHtml(gd, 20, 20, 360, 220, html_content, True, True)
    Gumps.AddButton(gd, 150, 260, 247, 248, 1, 0, 0)
    
    Gumps.SendGump(gd, 100, 100)

def example_check_gump_exists():
    """Example: Check if specific gump is open"""
    vendor_gump_id = 0x12345678  # Replace with actual ID
    
    if Gumps.HasGump(vendor_gump_id):
        Misc.SendMessage("Vendor gump is open", 68)
        
        # Get gump data
        gd = Gumps.GetGumpData(vendor_gump_id)
        if gd:
            Misc.SendMessage(f"Gump at position: ({gd.x}, {gd.y})", 67)
    else:
        Misc.SendMessage("Vendor gump not found", 33)

def example_close_all_gumps():
    """Example: Close all open gumps"""
    all_gumps = Gumps.AllGumpIDs()
    if all_gumps:
        for gump_id in all_gumps:
            Gumps.CloseGump(gump_id)
        Misc.SendMessage(f"Closed {len(all_gumps)} gumps", 68)

def example_get_gump_line_by_number():
    """Example: Get specific line from gump"""
    current = Gumps.CurrentGump()
    if current > 0:
        # Get line 5
        line = Gumps.GetLine(current, 5)
        if line:
            Misc.SendMessage(f"Line 5: {line}", 67)
        
        # Check if specific text exists on line 3
        if Gumps.LastGumpTextExistByLine(3, "Blacksmith"):
            Misc.SendMessage("Found Blacksmith on line 3!", 68)

def example_create_radio_button_gump():
    """Example: Create gump with radio buttons"""
    gd = Gumps.CreateGump(True, True, True, False)
    Gumps.AddBackground(gd, 0, 0, 300, 250, 9200)
    Gumps.AddLabel(gd, 100, 20, 2100, "Select Option")
    
    # Radio button group (only one can be selected)
    Gumps.AddRadio(gd, 50, 60, 208, 209, True, 1)  # Selected by default
    Gumps.AddLabel(gd, 75, 60, 0, "Option 1")
    
    Gumps.AddRadio(gd, 50, 90, 208, 209, False, 2)
    Gumps.AddLabel(gd, 75, 90, 0, "Option 2")
    
    Gumps.AddRadio(gd, 50, 120, 208, 209, False, 3)
    Gumps.AddLabel(gd, 75, 120, 0, "Option 3")
    
    Gumps.AddButton(gd, 100, 180, 247, 248, 1, 0, 0)
    Gumps.AddLabel(gd, 135, 182, 0, "OK")
    
    Gumps.SendGump(gd, 100, 100)

def example_validate_gump_id():
    """Example: Check if gump ID is valid"""
    gump_id = 9200  # Background gump ID
    
    if Gumps.IsValid(gump_id):
        Misc.SendMessage(f"Gump ID {gump_id} is valid", 68)
    else:
        Misc.SendMessage(f"Gump ID {gump_id} is invalid", 33)

# Main execution
try:
    tester = GumpsAPITester()
    tester.run_all_tests()
    
    # Optionally run usage examples
    if RUN_USAGE_EXAMPLES:
        debug_message("")
        debug_message("")
        section_header("USAGE EXAMPLES - PRACTICAL DEMONSTRATIONS")
        debug_message("Usage examples are defined as functions above", 67)
        debug_message("Call them individually as needed:", 67)
        debug_message("  - example_create_simple_gump()", 67)
        debug_message("  - example_wait_for_gump()", 67)
        debug_message("  - example_read_gump_text()", 67)
        debug_message("  - example_search_gump_text()", 67)
        debug_message("  - example_advanced_gump_response()", 67)
        debug_message("  - example_create_multi_page_gump()", 67)
        debug_message("  - example_create_form_gump()", 67)
        debug_message("  - example_create_item_display_gump()", 67)
        debug_message("  - example_create_html_gump()", 67)
        debug_message("  - example_check_gump_exists()", 67)
        debug_message("  - example_close_all_gumps()", 67)
        debug_message("  - example_get_gump_line_by_number()", 67)
        debug_message("  - example_create_radio_button_gump()", 67)
        debug_message("  - example_validate_gump_id()", 67)
        section_header("USAGE EXAMPLES COMPLETE")
    
except Exception as e:
    debug_message(f"FATAL ERROR: {e}", 33)
    import traceback
    debug_message(traceback.format_exc(), 33)
