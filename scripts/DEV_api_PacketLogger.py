"""
DEV API PacketLogger - a Razor Enhanced Python Script for Ultima Online

demonstration of PacketLogger API functions
Tests and displays information about packet logging functionality

=== PACKETLOGGER API OVERVIEW ===
The PacketLogger class provides functions to log, filter, and send UO network packets.
Useful for debugging, and creating preview client side only objects in game .

ALL PACKETLOGGER FUNCTIONS (13 functions):

LOGGING CONTROL (3 functions):
  - Start(outputpath, appendLogs) -> String
  - Stop() -> String
  - Reset()

FILTERING (5 functions):
  - AddWhitelist(packetID)
  - AddBlacklist(packetID)
  - DiscardAll(discardAll)
  - DiscardShowHeader(showHeader)
  - ListenPacketPath(packetPath, active) -> String[]

TEMPLATES (2 functions):
  - AddTemplate(packetTemplate)
  - RemoveTemplate(packetID)

PACKET SENDING (2 functions):
  - SendToClient(packetData)
  - SendToServer(packetData)

CONFIGURATION (1 function):
  - SetOutputPath(outputpath) -> String

PROPERTIES (2 properties):
  - PathToString (Dictionary)
  - StringToPath (Dictionary)

=== FIELDTEMPLATE CLASS ===
Represents fields inside a packet template.

FIELDTEMPLATE PROPERTIES (5 properties):
  - name (String) - Display name of the field
  - length (Int32) - Length in bytes
  - type (String) - Field type (see FieldType)
  - fields (List[FieldTemplate]) - List of subfields
  - subpacket (PacketTemplate) - Subpacket definition

=== FIELDTYPE CLASS ===
Available field types for packet templates.

ALL FIELD TYPES (14 types):
  - PACKETID - Packet ID (1 byte, fixed)
  - SERIAL - Serial number (4 bytes, hex display)
  - MODELID - Model/Item/Body ID (2 bytes, hex display)
  - INT - Signed integer (1-4 bytes)
  - UINT - Unsigned integer (1-4 bytes)
  - HEX - Hex display integer (1-4 bytes)
  - BOOL - Boolean (1 byte, fixed)
  - TEXT - ASCII text (length required)
  - UTF8 - UTF8 text (length required)
  - SKIP - Skip bytes (length required)
  - DUMP - Raw hex dump (length required)
  - FIELDS - Struct with subfields
  - FIELDSFOR - Loop over fields
  - SUBPACKET - Nested packet structure

FIELDTYPE METHODS (1 method):
  - IsValid(typename) -> Boolean

Key Features:
  - Log packets to file with custom paths
  - Filter packets with whitelist/blacklist
  - Add custom packet templates
  - Send custom packets to client/server
  - Control packet paths (ClientToServer, ServerToClient)

VERSION::20251013
"""

from System.Collections.Generic import List
import os
import json

# GLOBAL SETTINGS
DEBUG_MODE = True
TEST_DELAY = 500
LOG_OUTPUT_PATH = "D:\\ULTIMA\\SCRIPTS\\RazorEnhanced_Python\\data\\test_packets.log"
# JSON output file path
BASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
OUTPUT_FILE = os.path.join(BASE_PATH, "api_packetlogger_test_output.json")
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
            Misc.SendMessage(f"[PacketLogger] {message}", color)
        else:
            Misc.SendMessage("", color)
    except Exception:
        if message:
            print(f"[PacketLogger] {message}")
        else:
            print("")

def section_header(title):
    """Print a section header"""
    debug_message("=" * 60, 88)
    debug_message(f"  {title}", 88)
    debug_message("=" * 60, 88)

class PacketLoggerAPITester:
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
            "log_output_path": LOG_OUTPUT_PATH,
            "tests": {}
        }
        
    def debug(self, message, color=None):
        if color is None:
            color = self.debug_color
        debug_message(message, color)
    
    def test_start_stop(self):
        """
        Test Start and Stop Functions
        
        API: PacketLogger.Start(outputpath, appendLogs) -> String
        API: PacketLogger.Stop() -> String
        Purpose: Start/stop packet logging to file
        """
        section_header("TEST: Start/Stop Logging")
        
        test_success = True
        error_msg = None
        start_stop_data = {}
        
        try:
            # Start logging
            self.debug("Starting packet logger...", self.info_color)
            log_path = PacketLogger.Start(LOG_OUTPUT_PATH, False)
            start_stop_data["start_path"] = str(log_path)
            self.debug(f"  Started: {log_path}", self.success_color)
            
            Misc.Pause(TEST_DELAY)
            
            # Stop logging
            self.debug("Stopping packet logger...", self.info_color)
            final_path = PacketLogger.Stop()
            start_stop_data["stop_path"] = str(final_path)
            self.debug(f"  Stopped: {final_path}", self.success_color)
            
        except Exception as e:
            test_success = False
            error_msg = str(e)
            self.debug(f"  Error: {e}", self.error_color)
        
        self.json_output["test_report"]["StartStop"] = {
            "works": test_success,
            "error": error_msg,
            "data_returned": len(start_stop_data) > 0
        }
        self.json_output["tests"]["start_stop"] = start_stop_data
        self.debug("")
    
    def test_whitelist_blacklist(self):
        """
        Test Whitelist/Blacklist Functions
        
        API: PacketLogger.AddWhitelist(packetID)
        API: PacketLogger.AddBlacklist(packetID)
        API: PacketLogger.DiscardAll(discardAll)
        Purpose: Filter which packets to log
        """
        section_header("TEST: Whitelist/Blacklist")
        
        test_success = True
        error_msg = None
        filter_data = {}
        
        try:
            # Reset first
            PacketLogger.Reset()
            self.debug("Reset packet logger", self.info_color)
            
            # Add to whitelist (common packets)
            self.debug("Adding packets to whitelist...", self.info_color)
            PacketLogger.AddWhitelist(0x0B)  # Damage
            PacketLogger.AddWhitelist(0x1C)  # ASCII Speech
            PacketLogger.AddWhitelist(0x25)  # Single Click
            filter_data["whitelist"] = ["0x0B", "0x1C", "0x25"]
            self.debug("  Added: 0x0B (Damage), 0x1C (Speech), 0x25 (Click)", self.success_color)
            
            # Add to blacklist (spam packets)
            self.debug("Adding packets to blacklist...", self.info_color)
            PacketLogger.AddBlacklist(0x73)  # Ping
            PacketLogger.AddBlacklist(0x77)  # Mobile Moving
            filter_data["blacklist"] = ["0x73", "0x77"]
            self.debug("  Added: 0x73 (Ping), 0x77 (Moving)", self.success_color)
            
            # Enable discard all (only whitelist will be logged)
            self.debug("Enabling DiscardAll mode...", self.info_color)
            PacketLogger.DiscardAll(True)
            filter_data["discard_all_enabled"] = True
            self.debug("  Only whitelisted packets will be logged", self.success_color)
            
        except Exception as e:
            test_success = False
            error_msg = str(e)
            self.debug(f"  Error: {e}", self.error_color)
        
        self.json_output["test_report"]["WhitelistBlacklist"] = {
            "works": test_success,
            "error": error_msg,
            "data_returned": len(filter_data) > 0
        }
        self.json_output["tests"]["whitelist_blacklist"] = filter_data
        self.debug("")
    
    def test_packet_paths(self):
        """
        Test ListenPacketPath Function
        
        API: PacketLogger.ListenPacketPath(packetPath, active) -> String[]
        Purpose: Control which packet directions to log
        Paths: ClientToServer, ServerToClient
        """
        section_header("TEST: Packet Paths")
        
        try:
            # Get current active paths
            self.debug("Getting current packet paths...", self.info_color)
            active_paths = PacketLogger.ListenPacketPath("", True)
            if active_paths:
                self.debug(f"  Active paths: {len(active_paths)}", self.success_color)
            
            # Enable ClientToServer
            self.debug("Enabling ClientToServer path...", self.info_color)
            PacketLogger.ListenPacketPath("ClientToServer", True)
            self.debug("  ClientToServer enabled", self.success_color)
            
            # Enable ServerToClient
            self.debug("Enabling ServerToClient path...", self.info_color)
            PacketLogger.ListenPacketPath("ServerToClient", True)
            self.debug("  ServerToClient enabled", self.success_color)
            
        except Exception as e:
            self.debug(f"  Error: {e}", self.error_color)
        
        self.debug("")
    
    def test_templates(self):
        """
        Test AddTemplate and RemoveTemplate Functions
        
        API: PacketLogger.AddTemplate(packetTemplate)
        API: PacketLogger.RemoveTemplate(packetID)
        Purpose: Add custom packet parsing templates
        """
        section_header("TEST: Packet Templates")
        
        try:
            # Example template for Damage packet (0x0B)
            damage_template = """{
                'packetID': 11,
                'name': 'Damage 0x0B',
                'showHexDump': true,
                'fields':[
                    { 'name':'packetID', 'length':1, 'type':'packetID'},
                    { 'name':'Serial', 'length':4, 'type':'serial'},
                    { 'name':'Damage', 'length':2, 'type':'int'}
                ]
            }"""
            
            self.debug("Adding custom Damage packet template...", self.info_color)
            PacketLogger.AddTemplate(damage_template)
            self.debug("  Template added for packet 0x0B", self.success_color)
            
            # Remove template
            self.debug("Removing template...", self.info_color)
            PacketLogger.RemoveTemplate(0x0B)
            self.debug("  Template removed for packet 0x0B", self.success_color)
            
        except Exception as e:
            self.debug(f"  Error: {e}", self.error_color)
        
        self.debug("")
    
    def test_output_path(self):
        """
        Test SetOutputPath Function
        
        API: PacketLogger.SetOutputPath(outputpath) -> String
        Purpose: Set custom output path for logs
        """
        section_header("TEST: Output Path")
        
        try:
            # Set custom path
            self.debug("Setting custom output path...", self.info_color)
            path = PacketLogger.SetOutputPath(LOG_OUTPUT_PATH)
            self.debug(f"  Path set: {path}", self.success_color)
            
            # Reset to default
            self.debug("Resetting to default path...", self.info_color)
            default_path = PacketLogger.SetOutputPath("")
            self.debug(f"  Default path: {default_path}", self.success_color)
            
        except Exception as e:
            self.debug(f"  Error: {e}", self.error_color)
        
        self.debug("")
    
    def test_discard_show_header(self):
        """
        Test DiscardShowHeader Function
        
        API: PacketLogger.DiscardShowHeader(showHeader)
        Purpose: Show headers of discarded packets
        """
        section_header("TEST: Discard Show Header")
        
        try:
            self.debug("Enabling header display for discarded packets...", self.info_color)
            PacketLogger.DiscardShowHeader(True)
            self.debug("  Headers will be shown", self.success_color)
            
            self.debug("Disabling header display...", self.info_color)
            PacketLogger.DiscardShowHeader(False)
            self.debug("  Headers will be hidden", self.success_color)
            
        except Exception as e:
            self.debug(f"  Error: {e}", self.error_color)
        
        self.debug("")
    
    def test_reset(self):
        """
        Test Reset Function
        
        API: PacketLogger.Reset()
        Purpose: Reset packet logger to defaults
        """
        section_header("TEST: Reset")
        
        try:
            self.debug("Resetting packet logger to defaults...", self.info_color)
            PacketLogger.Reset()
            self.debug("  Reset complete", self.success_color)
            
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
        """Run all PacketLogger API tests"""
        section_header("PACKETLOGGER API TEST")
        self.debug("Testing PacketLogger functions", self.info_color)
        self.debug("WARNING: This will briefly start/stop packet logging", self.warning_color)
        self.debug("")
        
        self.test_output_path()
        self.test_whitelist_blacklist()
        self.test_packet_paths()
        self.test_discard_show_header()
        self.test_templates()
        self.test_start_stop()
        self.test_reset()
        
        section_header("TEST COMPLETE")
        self.debug("All PacketLogger functions tested!", self.success_color)
        
        # Save JSON output
        self.debug("")
        section_header("SAVING JSON OUTPUT")
        self.save_json_output()

# ============================================================================
# USAGE EXAMPLES
# ============================================================================

def example_log_specific_packets():
    """Example: Log only specific packet types"""
    # Reset to clean state
    PacketLogger.Reset()
    
    # Set custom output path
    output_path = "D:\\ULTIMA\\SCRIPTS\\RazorEnhanced_Python\\data\\combat_packets.log"
    PacketLogger.SetOutputPath(output_path)
    
    # Enable discard all mode
    PacketLogger.DiscardAll(True)
    
    # Whitelist only combat-related packets
    PacketLogger.AddWhitelist(0x0B)  # Damage
    PacketLogger.AddWhitelist(0x2C)  # Resurrection Menu
    PacketLogger.AddWhitelist(0xBF)  # General Information (includes combat)
    
    # Start logging
    Misc.SendMessage("Starting combat packet logging...", 68)
    PacketLogger.Start(output_path, False)
    
    # Log for 30 seconds
    Misc.SendMessage("Logging for 30 seconds...", 67)
    Misc.Pause(30000)
    
    # Stop logging
    final_path = PacketLogger.Stop()
    Misc.SendMessage(f"Logging stopped: {final_path}", 68)

def example_log_all_except_spam():
    """Example: Log everything except spam packets"""
    # Reset to clean state
    PacketLogger.Reset()
    
    # Disable discard all (log everything by default)
    PacketLogger.DiscardAll(False)
    
    # Blacklist spam packets
    PacketLogger.AddBlacklist(0x73)  # Ping
    PacketLogger.AddBlacklist(0x77)  # Mobile Moving
    PacketLogger.AddBlacklist(0x22)  # Character Move ACK
    PacketLogger.AddBlacklist(0x20)  # Draw Object
    
    # Start logging
    Misc.SendMessage("Logging all packets except spam...", 68)
    PacketLogger.Start("", False)  # Use default path
    
    Misc.Pause(10000)
    
    PacketLogger.Stop()
    Misc.SendMessage("Logging stopped", 68)

def example_log_client_to_server_only():
    """Example: Log only client-to-server packets"""
    PacketLogger.Reset()
    
    # Enable only ClientToServer path
    PacketLogger.ListenPacketPath("ClientToServer", True)
    PacketLogger.ListenPacketPath("ServerToClient", False)
    
    Misc.SendMessage("Logging client-to-server packets only...", 68)
    PacketLogger.Start("", False)
    
    Misc.Pause(10000)
    
    PacketLogger.Stop()
    Misc.SendMessage("Logging stopped", 68)

def example_send_custom_packet_to_server():
    """Example: Send custom packet to server (Single Click)"""
    # Single Click packet (0x09)
    # Format: [PacketID(1)] [Serial(4)]
    
    target_serial = Player.Serial
    
    packet = [
        0x09,  # Packet ID
        (target_serial >> 24) & 0xFF,  # Serial byte 1
        (target_serial >> 16) & 0xFF,  # Serial byte 2
        (target_serial >> 8) & 0xFF,   # Serial byte 3
        target_serial & 0xFF            # Serial byte 4
    ]
    
    Misc.SendMessage(f"Sending single click packet for 0x{target_serial:08X}", 67)
    PacketLogger.SendToServer(packet)

def example_log_with_custom_template():
    """Example: Add custom template and log packets"""
    PacketLogger.Reset()
    
    # Custom template for ASCII Speech (0x1C)
    speech_template = """{
        'packetID': 28,
        'name': 'ASCII Speech 0x1C',
        'showHexDump': true,
        'fields':[
            { 'name':'packetID', 'length':1, 'type':'packetID'},
            { 'name':'Serial', 'length':4, 'type':'serial'},
            { 'name':'Body', 'length':2, 'type':'int'},
            { 'name':'Type', 'length':1, 'type':'int'},
            { 'name':'Hue', 'length':2, 'type':'int'},
            { 'name':'Font', 'length':2, 'type':'int'},
            { 'name':'Name', 'length':30, 'type':'string'},
            { 'name':'Text', 'length':-1, 'type':'string'}
        ]
    }"""
    
    # Add template
    PacketLogger.AddTemplate(speech_template)
    Misc.SendMessage("Added custom speech template", 68)
    
    # Whitelist speech packets
    PacketLogger.DiscardAll(True)
    PacketLogger.AddWhitelist(0x1C)
    
    # Start logging
    PacketLogger.Start("", False)
    Misc.SendMessage("Logging speech packets with custom template...", 67)
    
    Misc.Pause(10000)
    
    PacketLogger.Stop()
    Misc.SendMessage("Logging stopped", 68)

def example_log_with_headers_only():
    """Example: Log with headers but discard packet bodies"""
    PacketLogger.Reset()
    
    # Enable header display for discarded packets
    PacketLogger.DiscardShowHeader(True)
    
    # Discard all packets (but show headers)
    PacketLogger.DiscardAll(True)
    
    Misc.SendMessage("Logging packet headers only...", 68)
    PacketLogger.Start("", False)
    
    Misc.Pause(5000)
    
    PacketLogger.Stop()
    Misc.SendMessage("Logging stopped", 68)

def example_append_to_existing_log():
    """Example: Append to existing log file"""
    log_path = "D:\\ULTIMA\\SCRIPTS\\RazorEnhanced_Python\\data\\session_packets.log"
    
    # Start logging with append mode
    Misc.SendMessage("Appending to existing log...", 68)
    PacketLogger.Start(log_path, True)  # True = append
    
    Misc.Pause(5000)
    
    PacketLogger.Stop()
    Misc.SendMessage("Session appended to log", 68)

def example_debug_specific_interaction():
    """Example: Debug specific game interaction"""
    PacketLogger.Reset()
    
    # Whitelist packets related to item interaction
    PacketLogger.DiscardAll(True)
    PacketLogger.AddWhitelist(0x06)  # Double Click
    PacketLogger.AddWhitelist(0x07)  # Pick Up Item
    PacketLogger.AddWhitelist(0x08)  # Drop Item
    PacketLogger.AddWhitelist(0x13)  # Equip Item
    PacketLogger.AddWhitelist(0x3A)  # Skills
    PacketLogger.AddWhitelist(0x3C)  # Container Contents
    
    Misc.SendMessage("=== Debug Mode: Item Interactions ===", 88)
    Misc.SendMessage("Logging item-related packets...", 67)
    
    PacketLogger.Start("", False)
    
    # Perform your interaction here
    Misc.SendMessage("Perform item interactions now...", 53)
    Misc.Pause(15000)
    
    final_path = PacketLogger.Stop()
    Misc.SendMessage(f"Debug log saved: {final_path}", 68)

def example_monitor_combat_damage():
    """Example: Monitor only damage packets during combat"""
    PacketLogger.Reset()
    
    # Whitelist only damage packet
    PacketLogger.DiscardAll(True)
    PacketLogger.AddWhitelist(0x0B)  # Damage packet
    
    # Add custom damage template
    damage_template = """{
        'packetID': 11,
        'name': 'Damage 0x0B',
        'showHexDump': false,
        'fields':[
            { 'name':'packetID', 'length':1, 'type':'packetID'},
            { 'name':'Target Serial', 'length':4, 'type':'serial'},
            { 'name':'Damage Amount', 'length':2, 'type':'int'}
        ]
    }"""
    
    PacketLogger.AddTemplate(damage_template)
    
    Misc.SendMessage("=== Combat Damage Monitor ===", 88)
    Misc.SendMessage("Logging damage packets...", 67)
    
    PacketLogger.Start("", False)
    
    # Monitor for 60 seconds
    Misc.Pause(60000)
    
    PacketLogger.Stop()
    Misc.SendMessage("Damage monitoring complete", 68)

def example_template_all_field_types():
    """Example: Template demonstrating all field types"""
    
    # Comprehensive template showing all field types
    comprehensive_template = """{
        'packetID': 255,
        'name': 'Comprehensive Field Types Demo',
        'showHexDump': true,
        'fields':[
            { 'name':'Packet ID', 'type':'packetID'},
            { 'name':'Target Serial', 'type':'serial'},
            { 'name':'Item Model', 'type':'modelID'},
            { 'name':'Signed Value', 'type':'int', 'length':2},
            { 'name':'Unsigned Value', 'type':'uint', 'length':2},
            { 'name':'Hex Value', 'type':'hex', 'length':2},
            { 'name':'Is Active', 'type':'bool'},
            { 'name':'Player Name', 'type':'text', 'length':30},
            { 'name':'UTF8 Text', 'type':'utf8', 'length':20},
            { 'name':'Skip Unused', 'type':'skip', 'length':10},
            { 'name':'Raw Data', 'type':'dump', 'length':8},
            { 'name':'Position', 'type':'fields',
                'fields':[
                    {'name':'X', 'type':'uint', 'length':2},
                    {'name':'Y', 'type':'uint', 'length':2},
                    {'name':'Z', 'type':'int', 'length':1}
                ]
            }
        ]
    }"""
    
    Misc.SendMessage("=== Field Types Demo ===", 88)
    Misc.SendMessage("Template shows all available field types:", 67)
    Misc.SendMessage("  PACKETID, SERIAL, MODELID", 67)
    Misc.SendMessage("  INT, UINT, HEX, BOOL", 67)
    Misc.SendMessage("  TEXT, UTF8, SKIP, DUMP", 67)
    Misc.SendMessage("  FIELDS (nested struct)", 67)

def example_template_with_subpacket():
    """Example: Template with subpacket structure"""
    
    # Template demonstrating subpacket usage
    subpacket_template = """{
        'packetID': 191,
        'name': 'General Information 0xBF',
        'showHexDump': true,
        'fields':[
            { 'name':'packetID', 'type':'packetID'},
            { 'name':'Packet Length', 'type':'uint', 'length':2},
            { 'name':'Subcommand', 'type':'hex', 'length':2},
            { 'name':'Subpacket Data', 'type':'subpacket',
                'subpacket':{
                    'name':'Subcommand Data',
                    'fields':[
                        {'name':'Data1', 'type':'uint', 'length':4},
                        {'name':'Data2', 'type':'uint', 'length':4}
                    ]
                }
            }
        ]
    }"""
    
    Misc.SendMessage("=== Subpacket Template ===", 88)
    Misc.SendMessage("Demonstrates nested packet structures", 67)

def example_template_mobile_update():
    """Example: Complete mobile update packet template"""
    
    mobile_update_template = """{
        'packetID': 32,
        'name': 'Mobile Update 0x20',
        'showHexDump': false,
        'fields':[
            { 'name':'packetID', 'type':'packetID'},
            { 'name':'Serial', 'type':'serial'},
            { 'name':'Body', 'type':'modelID'},
            { 'name':'X', 'type':'uint', 'length':2},
            { 'name':'Y', 'type':'uint', 'length':2},
            { 'name':'Z', 'type':'int', 'length':1},
            { 'name':'Direction', 'type':'uint', 'length':1},
            { 'name':'Hue', 'type':'hex', 'length':2},
            { 'name':'Status', 'type':'hex', 'length':1},
            { 'name':'Notoriety', 'type':'uint', 'length':1}
        ]
    }"""
    
    PacketLogger.Reset()
    PacketLogger.AddTemplate(mobile_update_template)
    
    # Whitelist mobile update packets
    PacketLogger.DiscardAll(True)
    PacketLogger.AddWhitelist(0x20)
    
    Misc.SendMessage("=== Mobile Update Monitor ===", 88)
    Misc.SendMessage("Logging mobile movement with custom template...", 67)
    
    PacketLogger.Start("", False)
    Misc.Pause(10000)
    PacketLogger.Stop()
    
    Misc.SendMessage("Mobile update logging complete", 68)

def example_template_item_info():
    """Example: Item information packet template"""
    
    item_info_template = """{
        'packetID': 26,
        'name': 'Item Info 0x1A',
        'showHexDump': false,
        'fields':[
            { 'name':'packetID', 'type':'packetID'},
            { 'name':'Packet Length', 'type':'uint', 'length':2},
            { 'name':'Serial', 'type':'serial'},
            { 'name':'Item ID', 'type':'modelID'},
            { 'name':'Amount', 'type':'uint', 'length':2},
            { 'name':'Position', 'type':'fields',
                'fields':[
                    {'name':'X', 'type':'uint', 'length':2},
                    {'name':'Y', 'type':'uint', 'length':2},
                    {'name':'Z', 'type':'int', 'length':1}
                ]
            },
            { 'name':'Direction', 'type':'uint', 'length':1},
            { 'name':'Hue', 'type':'hex', 'length':2},
            { 'name':'Flags', 'type':'hex', 'length':1}
        ]
    }"""
    
    PacketLogger.Reset()
    PacketLogger.AddTemplate(item_info_template)
    
    PacketLogger.DiscardAll(True)
    PacketLogger.AddWhitelist(0x1A)
    
    Misc.SendMessage("=== Item Info Monitor ===", 88)
    Misc.SendMessage("Logging item updates...", 67)
    
    PacketLogger.Start("", False)
    Misc.Pause(10000)
    PacketLogger.Stop()
    
    Misc.SendMessage("Item logging complete", 68)

def example_validate_field_types():
    """Example: Validate field type names"""
    
    # Test field type validation
    test_types = [
        "packetID", "serial", "modelID",
        "int", "uint", "hex", "bool",
        "text", "utf8", "skip", "dump",
        "fields", "subpacket", "fieldsfor",
        "invalid_type"  # This should fail
    ]
    
    Misc.SendMessage("=== Field Type Validation ===", 88)
    
    for type_name in test_types:
        is_valid = PacketLogger.FieldType.IsValid(type_name)
        color = 68 if is_valid else 33
        status = "VALID" if is_valid else "INVALID"
        Misc.SendMessage(f"  {type_name}: {status}", color)

def example_template_unicode_speech():
    """Example: Unicode speech packet with UTF8"""
    
    unicode_speech_template = """{
        'packetID': 174,
        'name': 'Unicode Speech 0xAE',
        'showHexDump': false,
        'fields':[
            { 'name':'packetID', 'type':'packetID'},
            { 'name':'Packet Length', 'type':'uint', 'length':2},
            { 'name':'Serial', 'type':'serial'},
            { 'name':'Body', 'type':'modelID'},
            { 'name':'Speech Type', 'type':'uint', 'length':1},
            { 'name':'Hue', 'type':'hex', 'length':2},
            { 'name':'Font', 'type':'uint', 'length':2},
            { 'name':'Language', 'type':'text', 'length':4},
            { 'name':'Name', 'type':'text', 'length':30},
            { 'name':'Text', 'type':'utf8', 'length':-1}
        ]
    }"""
    
    PacketLogger.Reset()
    PacketLogger.AddTemplate(unicode_speech_template)
    
    PacketLogger.DiscardAll(True)
    PacketLogger.AddWhitelist(0xAE)
    
    Misc.SendMessage("=== Unicode Speech Monitor ===", 88)
    Misc.SendMessage("Logging unicode speech with UTF8 support...", 67)
    
    PacketLogger.Start("", False)
    Misc.Pause(15000)
    PacketLogger.Stop()
    
    Misc.SendMessage("Speech logging complete", 68)

def example_template_container_contents():
    """Example: Container contents with repeating fields"""
    
    container_template = """{
        'packetID': 60,
        'name': 'Container Contents 0x3C',
        'showHexDump': false,
        'fields':[
            { 'name':'packetID', 'type':'packetID'},
            { 'name':'Packet Length', 'type':'uint', 'length':2},
            { 'name':'Item Count', 'type':'uint', 'length':2},
            { 'name':'Items', 'type':'fieldsfor',
                'fields':[
                    {'name':'Serial', 'type':'serial'},
                    {'name':'Item ID', 'type':'modelID'},
                    {'name':'Unknown', 'type':'skip', 'length':1},
                    {'name':'Amount', 'type':'uint', 'length':2},
                    {'name':'X', 'type':'uint', 'length':2},
                    {'name':'Y', 'type':'uint', 'length':2},
                    {'name':'Grid', 'type':'uint', 'length':1},
                    {'name':'Container', 'type':'serial'},
                    {'name':'Hue', 'type':'hex', 'length':2}
                ]
            }
        ]
    }"""
    
    PacketLogger.Reset()
    PacketLogger.AddTemplate(container_template)
    
    PacketLogger.DiscardAll(True)
    PacketLogger.AddWhitelist(0x3C)
    
    Misc.SendMessage("=== Container Contents Monitor ===", 88)
    Misc.SendMessage("Logging container updates...", 67)
    Misc.SendMessage("Open containers to see packet data", 53)
    
    PacketLogger.Start("", False)
    Misc.Pause(20000)
    PacketLogger.Stop()
    
    Misc.SendMessage("Container logging complete", 68)

# Main execution
try:
    tester = PacketLoggerAPITester()
    tester.run_all_tests()
    
    # Optionally run usage examples
    if RUN_USAGE_EXAMPLES:
        debug_message("")
        debug_message("")
        section_header("USAGE EXAMPLES - PRACTICAL DEMONSTRATIONS")
        debug_message("Usage examples are defined as functions above", 67)
        debug_message("Call them individually as needed:", 67)
        debug_message("  - example_log_specific_packets()", 67)
        debug_message("  - example_log_all_except_spam()", 67)
        debug_message("  - example_log_client_to_server_only()", 67)
        debug_message("  - example_send_custom_packet_to_server()", 67)
        debug_message("  - example_log_with_custom_template()", 67)
        debug_message("  - example_log_with_headers_only()", 67)
        debug_message("  - example_append_to_existing_log()", 67)
        debug_message("  - example_debug_specific_interaction()", 67)
        debug_message("  - example_monitor_combat_damage()", 67)
        debug_message("  - example_template_mobile_update()", 67)
        debug_message("  - example_template_item_info()", 67)
        debug_message("  - example_validate_field_types()", 67)
        debug_message("  - example_template_unicode_speech()", 67)
        debug_message("  - example_template_container_contents()", 67)
        section_header("USAGE EXAMPLES COMPLETE")
    
except Exception as e:
    debug_message(f"FATAL ERROR: {e}", 33)
    import traceback
    debug_message(traceback.format_exc(), 33)
