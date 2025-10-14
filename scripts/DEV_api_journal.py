"""
DEV API Journal - a Razor Enhanced Python Script for Ultima Online

 demonstration of  Journal API functions
Tests searching, filtering, and reading journal messages

=== JOURNAL API OVERVIEW ===
The Journal class provides access to the in-game message journal (chat log).

ALL JOURNAL API FUNCTIONS (16 functions):

SEARCH FUNCTIONS (case-sensitive):
  - Search(text) -> Boolean
  - SearchByName(text, name) -> Boolean
  - SearchByColor(text, color) -> Boolean
  - SearchByType(text, type) -> Boolean

RETRIEVE FUNCTIONS:
  - GetJournalEntry(afterTimestamp) -> List[JournalEntry]
  - GetLineText(text, addname) -> String
  - GetTextByName(name, addname) -> List[String]
  - GetTextByColor(color, addname) -> List[String]
  - GetTextBySerial(serial, addname) -> List[String]
  - GetTextByType(type, addname) -> List[String]
  - GetSpeechName() -> List[String]

FILTER FUNCTIONS (case-insensitive):
  - FilterText(text) -> Void
  - RemoveFilterText(text) -> Void

WAIT FUNCTIONS (case-sensitive):
  - WaitJournal(text, delay) -> Boolean/String
  - WaitByName(name, delay) -> Boolean

CLEAR FUNCTIONS:
  - Clear() -> Void
  - Clear(toBeRemoved) -> Void

Message Types:
  Regular, System, Emote, Label, Focus, Whisper, Yell, Spell,
  Guild, Alliance, Party, Encoded, Special

=== JOURNALENTRY CLASS ===
The JournalEntry class represents a single line in the journal with full details.

JournalEntry Properties (6 properties):
  - Text (String): The actual message content
  - Name (String): Name of the source (Mobile or Item name)
  - Serial (Int32): Serial number of the source (Mobile or Item)
  - Color (Int32): Color/hue of the message text
  - Type (String): Message type (Regular, System, Emote, etc.)
  - Timestamp (Double): Unix timestamp (seconds since Jan 1, 1970)

JournalEntry Methods:
  - Copy() -> JournalEntry: Create a copy of the entry

Usage: Get entries via Journal.GetJournalEntry(afterTimestamp)
       Can filter by timestamp or previous JournalEntry object

IMPORTANT NOTES:
  - Most search functions are case-sensitive
  - Filter functions are case-insensitive
  - Journal has limited history (older messages are lost)
  - Use Clear() before waiting for new messages

VERSION::20251013
"""

from System.Collections.Generic import List
import os
import json

# GLOBAL SETTINGS
DEBUG_MODE = True
# Enable interactive tests (will wait for journal messages)
INTERACTIVE_MODE = False  # Set True to enable wait tests
# Test delay (ms)
TEST_DELAY = 500
# JSON output file path
BASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
OUTPUT_FILE = os.path.join(BASE_PATH, "api_journal_test_output.json")
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
            Misc.SendMessage(f"[JOURNAL] {message}", color)
        else:
            Misc.SendMessage("", color)
    except Exception:
        if message:
            print(f"[JOURNAL] {message}")
        else:
            print("")

def section_header(title):
    """Print a section header"""
    debug_message("=" * 60, 88)
    debug_message(f"  {title}", 88)
    debug_message("=" * 60, 88)

class JournalAPITester:
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
            "interactive_mode": INTERACTIVE_MODE,
            "tests": {}
        }
        
    def debug(self, message, color=None):
        """Send a debug message"""
        if color is None:
            color = self.debug_color
        debug_message(message, color)
    
    def test_search_functions(self):
        """
        SEARCH FUNCTIONS (case-sensitive)
        
        Search(text) -> Boolean
        - Search for text anywhere in journal
        - Returns True if found, False otherwise
        
        SearchByName(text, name) -> Boolean
        - Search for text from specific source name
        - Both text and name are case-sensitive
        
        SearchByColor(text, color) -> Boolean
        - Search for text with specific color
        - Color is Int32 hue value
        
        SearchByType(text, type) -> Boolean
        - Search for text of specific message type
        - Types: Regular, System, Emote, Label, Focus, Whisper, Yell,
                 Spell, Guild, Alliance, Party, Encoded, Special
        """
        section_header("TEST: Search Functions")
        
        test_success = True
        error_msg = None
        search_results = {}
        
        self.debug("Testing journal search functions...", self.info_color)
        
        # Test basic search
        try:
            # Search for common system messages
            test_searches = ["You", "the", "your", "System"]
            
            for search_text in test_searches:
                found = Journal.Search(search_text)
                search_results[f"search_{search_text}"] = bool(found)
                status = "FOUND" if found else "NOT FOUND"
                color = self.success_color if found else self.warning_color
                self.debug(f"  Search('{search_text}'): {status}", color)
                if found:
                    break  # Found one, move on
            
        except Exception as e:
            test_success = False
            error_msg = str(e)
            self.debug(f"  Error with Search: {e}", self.error_color)
        
        # Test SearchByName
        try:
            self.debug("  Testing SearchByName with 'System'...", self.info_color)
            found = Journal.SearchByName("", "System")
            search_results["search_by_name"] = bool(found)
            self.debug(f"    Messages from System: {found}", self.success_color if found else self.warning_color)
        except Exception as e:
            test_success = False
            if not error_msg:
                error_msg = str(e)
            self.debug(f"  Error with SearchByName: {e}", self.error_color)
        
        # Test SearchByType
        try:
            self.debug("  Testing SearchByType with 'System'...", self.info_color)
            found = Journal.SearchByType("", "System")
            search_results["search_by_type"] = bool(found)
            self.debug(f"    System type messages: {found}", self.success_color if found else self.warning_color)
        except Exception as e:
            test_success = False
            if not error_msg:
                error_msg = str(e)
            self.debug(f"  Error with SearchByType: {e}", self.error_color)
        
        # Record test report
        self.json_output["test_report"]["SearchFunctions"] = {
            "works": test_success,
            "error": error_msg,
            "data_returned": len(search_results) > 0
        }
        self.json_output["tests"]["search_results"] = search_results
        
        self.debug("")
    
    def test_retrieve_functions(self):
        """
        RETRIEVE FUNCTIONS
        
        GetLineText(text, addname) -> String
        - Get most recent line containing text
        - addname: Prepend source name (default False)
        - Returns empty string if not found
        
        GetTextByName(name, addname) -> List[String]
        - Get all lines from specific source
        
        GetTextByColor(color, addname) -> List[String]
        - Get all lines with specific color
        
        GetTextBySerial(serial, addname) -> List[String]
        - Get all lines from specific serial
        
        GetTextByType(type, addname) -> List[String]
        - Get all lines of specific type
        
        GetSpeechName() -> List[String]
        - Get list of all speakers in journal
        """
        section_header("TEST: Retrieve Functions")
        
        test_success = True
        error_msg = None
        retrieve_data = {}
        
        # Test GetSpeechName
        try:
            self.debug("Getting list of speakers...", self.info_color)
            speakers = Journal.GetSpeechName()
            if speakers and len(speakers) > 0:
                retrieve_data["speaker_count"] = len(speakers)
                retrieve_data["speakers"] = [str(s) for s in speakers[:10]]  # First 10
                self.debug(f"  Found {len(speakers)} speaker(s):", self.success_color)
                for i, speaker in enumerate(speakers[:5]):  # Show first 5
                    self.debug(f"    [{i}]: {speaker}", self.debug_color)
                if len(speakers) > 5:
                    self.debug(f"    ... and {len(speakers) - 5} more", self.debug_color)
            else:
                retrieve_data["speaker_count"] = 0
                self.debug("  No speakers found", self.warning_color)
        except Exception as e:
            test_success = False
            error_msg = str(e)
            self.debug(f"  Error with GetSpeechName: {e}", self.error_color)
        
        # Test GetTextByType
        try:
            self.debug("Getting System messages...", self.info_color)
            system_msgs = Journal.GetTextByType("System", False)
            if system_msgs and len(system_msgs) > 0:
                retrieve_data["system_message_count"] = len(system_msgs)
                retrieve_data["system_messages_sample"] = [str(m)[:60] for m in system_msgs[:3]]
                self.debug(f"  Found {len(system_msgs)} System message(s):", self.success_color)
                for i, msg in enumerate(system_msgs[:3]):  # Show first 3
                    self.debug(f"    {msg[:60]}...", self.debug_color)
            else:
                retrieve_data["system_message_count"] = 0
                self.debug("  No System messages", self.warning_color)
        except Exception as e:
            test_success = False
            if not error_msg:
                error_msg = str(e)
            self.debug(f"  Error with GetTextByType: {e}", self.error_color)
        
        # Test GetLineText
        try:
            self.debug("Getting line with common text...", self.info_color)
            line = Journal.GetLineText("you", False)
            if line:
                retrieve_data["line_text_found"] = True
                retrieve_data["line_text_sample"] = str(line)[:60]
                self.debug(f"  Found: {line[:60]}...", self.success_color)
            else:
                retrieve_data["line_text_found"] = False
                self.debug("  No line found", self.warning_color)
        except Exception as e:
            test_success = False
            if not error_msg:
                error_msg = str(e)
            self.debug(f"  Error with GetLineText: {e}", self.error_color)
        
        # Test GetTextBySerial
        try:
            self.debug("Testing GetTextBySerial with player serial...", self.info_color)
            player_msgs = Journal.GetTextBySerial(Player.Serial, False)
            if player_msgs and len(player_msgs) > 0:
                retrieve_data["player_message_count"] = len(player_msgs)
                self.debug(f"  Found {len(player_msgs)} message(s) from player:", self.success_color)
                for i, msg in enumerate(player_msgs[:3]):  # Show first 3
                    self.debug(f"    {msg[:60]}...", self.debug_color)
            else:
                retrieve_data["player_message_count"] = 0
                self.debug("  No messages from player serial", self.warning_color)
        except Exception as e:
            test_success = False
            if not error_msg:
                error_msg = str(e)
            self.debug(f"  Error with GetTextBySerial: {e}", self.error_color)
        
        # Record test report
        self.json_output["test_report"]["RetrieveFunctions"] = {
            "works": test_success,
            "error": error_msg,
            "data_returned": len(retrieve_data) > 0
        }
        self.json_output["tests"]["retrieve_data"] = retrieve_data
        
        self.debug("")
    
    def test_journal_entry(self):
        """
        JOURNAL ENTRY FUNCTIONS
        
        GetJournalEntry(afterTimestamp) -> List[JournalEntry]
        - Get all journal entries as JournalEntry objects
        - afterTimestamp: Unix time (seconds since 1970) or JournalEntry object
        - Returns list of JournalEntry objects with full details
        
        JournalEntry Properties (6 properties):
          - Text (String): The actual message content
          - Name (String): Name of the source (Mobile or Item)
          - Serial (Int32): Serial number of the source
          - Color (Int32): Color/hue of the message text
          - Type (String): Message type (Regular, System, Emote, etc.)
          - Timestamp (Double): Unix timestamp (seconds since Jan 1, 1970)
        
        JournalEntry Methods:
          - Copy() -> JournalEntry: Create a copy of the entry
        """
        section_header("TEST: Journal Entry")
        
        test_success = True
        error_msg = None
        entry_data = {}
        
        try:
            self.debug("Getting journal entries...", self.info_color)
            
            # Get all entries
            entries = Journal.GetJournalEntry(-1)
            
            if entries and len(entries) > 0:
                entry_data["total_entries"] = len(entries)
                entry_data["sample_entries"] = []
                self.debug(f"  Found {len(entries)} journal entry/entries:", self.success_color)
                
                # Show first few entries with all properties
                for i, entry in enumerate(entries[:5]):
                    self.debug(f"  Entry {i + 1}:", self.info_color)
                    try:
                        # Text (String): The actual message content
                        text_preview = entry.Text[:50] if len(entry.Text) > 50 else entry.Text
                        self.debug(f"    Text: {text_preview}{'...' if len(entry.Text) > 50 else ''}", self.debug_color)
                        
                        # Name (String): Name of the source (Mobile or Item)
                        self.debug(f"    Name: {entry.Name}", self.debug_color)
                        
                        # Serial (Int32): Serial number of the source
                        self.debug(f"    Serial: 0x{entry.Serial:08X} ({entry.Serial})", self.debug_color)
                        
                        # Color (Int32): Color/hue of the message text
                        self.debug(f"    Color: {entry.Color}", self.debug_color)
                        
                        # Type (String): Message type
                        self.debug(f"    Type: {entry.Type}", self.debug_color)
                        
                        # Timestamp (Double): Unix timestamp
                        self.debug(f"    Timestamp: {entry.Timestamp}", self.debug_color)
                        
                        # Store sample entry data
                        if i < 3:  # Store first 3
                            entry_data["sample_entries"].append({
                                "text": str(entry.Text)[:50],
                                "name": str(entry.Name),
                                "serial": int(entry.Serial),
                                "color": int(entry.Color),
                                "type": str(entry.Type),
                                "timestamp": float(entry.Timestamp)
                            })
                        
                        # Test Copy() method
                        try:
                            entry_copy = entry.Copy()
                            self.debug(f"    Copy() successful: {entry_copy.Text == entry.Text}", self.debug_color)
                        except Exception:
                            pass
                            
                    except Exception as e:
                        self.debug(f"    Error reading entry: {e}", self.error_color)
                
                if len(entries) > 5:
                    self.debug(f"  ... and {len(entries) - 5} more entries", self.debug_color)
                
                # Test filtering by timestamp
                if len(entries) > 0:
                    self.debug("  Testing timestamp filter...", self.info_color)
                    last_entry = entries[-1]
                    recent = Journal.GetJournalEntry(last_entry)
                    entry_data["entries_after_last"] = len(recent) if recent else 0
                    self.debug(f"    Entries after last: {len(recent) if recent else 0}", self.debug_color)
                    
                    # Test filtering by numeric timestamp
                    if len(entries) > 1:
                        mid_timestamp = entries[len(entries) // 2].Timestamp
                        filtered = Journal.GetJournalEntry(mid_timestamp)
                        entry_data["entries_after_midpoint"] = len(filtered) if filtered else 0
                        self.debug(f"    Entries after mid-point: {len(filtered) if filtered else 0}", self.debug_color)
            else:
                entry_data["total_entries"] = 0
                self.debug("  No journal entries found", self.warning_color)
                
        except Exception as e:
            test_success = False
            error_msg = str(e)
            self.debug(f"  Error with GetJournalEntry: {e}", self.error_color)
        
        # Record test report
        self.json_output["test_report"]["GetJournalEntry"] = {
            "works": test_success,
            "error": error_msg,
            "data_returned": len(entry_data) > 0
        }
        self.json_output["tests"]["journal_entries"] = entry_data
        
        self.debug("")
    
    def test_filter_functions(self):
        """
        FILTER FUNCTIONS (case-insensitive)
        
        FilterText(text)
        - Block messages containing text from appearing in journal
        - Case-insensitive matching
        - Useful for hiding spam
        
        RemoveFilterText(text)
        - Remove a previously added filter
        - Case-insensitive
        
        Note: Filters persist until removed or script ends
        """
        section_header("TEST: Filter Functions")
        
        test_success = True
        error_msg = None
        
        if not INTERACTIVE_MODE:
            self.debug("  [INTERACTIVE_MODE disabled - skipping filter tests]", self.warning_color)
            self.debug("  Example: Journal.FilterText('spam message')", self.info_color)
            self.debug("  Example: Journal.RemoveFilterText('spam message')", self.info_color)
            # Record test report for skipped test
            self.json_output["test_report"]["FilterFunctions"] = {
                "works": None,
                "error": "Skipped - INTERACTIVE_MODE disabled",
                "data_returned": False
            }
            self.debug("")
            return
        
        try:
            test_filter = "test_filter_123"
            
            self.debug(f"Adding filter for: '{test_filter}'...", self.info_color)
            Journal.FilterText(test_filter)
            self.debug("  Filter added", self.success_color)
            
            Misc.Pause(TEST_DELAY)
            
            self.debug(f"Removing filter for: '{test_filter}'...", self.info_color)
            Journal.RemoveFilterText(test_filter)
            self.debug("  Filter removed", self.success_color)
            
        except Exception as e:
            test_success = False
            error_msg = str(e)
            self.debug(f"  Error with filter functions: {e}", self.error_color)
        
        # Record test report
        self.json_output["test_report"]["FilterFunctions"] = {
            "works": test_success,
            "error": error_msg,
            "data_returned": test_success
        }
        
        self.debug("")
    
    def test_clear_functions(self):
        """
        CLEAR FUNCTIONS
        
        Clear()
        - Remove all entries from journal
        - Useful before waiting for new messages
        
        Clear(toBeRemoved)
        - Remove all entries matching text
        - Selective clearing
        """
        section_header("TEST: Clear Functions")
        
        test_success = True
        error_msg = None
        
        if not INTERACTIVE_MODE:
            self.debug("  [INTERACTIVE_MODE disabled - skipping clear test]", self.warning_color)
            self.debug("  Example: Journal.Clear()  # Clear all", self.info_color)
            self.debug("  Example: Journal.Clear('specific text')  # Clear matching", self.info_color)
            # Record test report for skipped test
            self.json_output["test_report"]["ClearFunctions"] = {
                "works": None,
                "error": "Skipped - INTERACTIVE_MODE disabled",
                "data_returned": False
            }
            self.debug("")
            return
        
        try:
            # Get count before
            entries_before = Journal.GetJournalEntry(-1)
            count_before = len(entries_before) if entries_before else 0
            self.debug(f"Journal entries before clear: {count_before}", self.info_color)
            
            # Clear all
            self.debug("Clearing all journal entries...", self.info_color)
            Journal.Clear()
            
            Misc.Pause(TEST_DELAY)
            
            # Get count after
            entries_after = Journal.GetJournalEntry(-1)
            count_after = len(entries_after) if entries_after else 0
            self.debug(f"Journal entries after clear: {count_after}", self.success_color)
            
        except Exception as e:
            test_success = False
            error_msg = str(e)
            self.debug(f"  Error with Clear: {e}", self.error_color)
        
        # Record test report
        self.json_output["test_report"]["ClearFunctions"] = {
            "works": test_success,
            "error": error_msg,
            "data_returned": test_success
        }
        
        self.debug("")
    
    def test_wait_functions(self):
        """
        WAIT FUNCTIONS (case-sensitive)
        
        WaitJournal(text, delay) -> Boolean/String
        - Pause script until text appears in journal
        - text: String or List[String] to wait for
        - delay: Maximum wait time in milliseconds
        - Returns True/text if found, False if timeout
        
        WaitByName(name, delay) -> Boolean
        - Pause until specific source speaks
        - name: Source name to wait for
        - delay: Maximum wait time in milliseconds
        
        Note: Clear journal before waiting for new messages!
        """
        section_header("TEST: Wait Functions")
        
        test_success = True
        error_msg = None
        
        if not INTERACTIVE_MODE:
            self.debug("  [INTERACTIVE_MODE disabled - skipping wait tests]", self.warning_color)
            self.debug("  Example: Journal.WaitJournal('text', 5000)", self.info_color)
            self.debug("  Example: Journal.WaitByName('System', 5000)", self.info_color)
            self.debug("  Note: Clear journal before waiting!", self.warning_color)
            # Record test report for skipped test
            self.json_output["test_report"]["WaitFunctions"] = {
                "works": None,
                "error": "Skipped - INTERACTIVE_MODE disabled",
                "data_returned": False
            }
            self.debug("")
            return
        
        try:
            self.debug("Testing WaitJournal...", self.info_color)
            self.debug("  Say something in chat to test!", self.warning_color)
            
            # Clear journal first
            Journal.Clear()
            
            # Wait for any text (short timeout for demo)
            result = Journal.WaitJournal("", 3000)
            
            if result:
                self.debug("  Message detected!", self.success_color)
            else:
                self.debug("  Timeout - no message", self.warning_color)
                
        except Exception as e:
            test_success = False
            error_msg = str(e)
            self.debug(f"  Error with WaitJournal: {e}", self.error_color)
        
        # Record test report
        self.json_output["test_report"]["WaitFunctions"] = {
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
        """Run all Journal API tests"""
        section_header("JOURNAL API COMPREHENSIVE TEST")
        self.debug(f"Interactive Mode: {INTERACTIVE_MODE}", self.warning_color if not INTERACTIVE_MODE else self.success_color)
        if not INTERACTIVE_MODE:
            self.debug("  Set INTERACTIVE_MODE = True for full testing", self.warning_color)
        self.debug("")
        
        # Run all tests
        self.test_search_functions()
        self.test_retrieve_functions()
        self.test_journal_entry()
        self.test_filter_functions()
        self.test_clear_functions()
        self.test_wait_functions()
        
        # Final summary
        section_header("TEST COMPLETE")
        self.debug("All Journal API functions have been tested!", self.success_color)
        if not INTERACTIVE_MODE:
            self.debug("Note: Some tests were skipped due to INTERACTIVE_MODE = False", self.warning_color)
        self.debug("Check the output above for detailed results.", self.info_color)
        
        # Save JSON output
        self.debug("")
        section_header("SAVING JSON OUTPUT")
        self.save_json_output()

# ============================================================================
# USAGE EXAMPLES - Common Journal API patterns
# ============================================================================

def example_wait_for_message():
    """Example: Wait for specific message"""
    Journal.Clear()
    if Journal.WaitJournal("You have gained", 5000):
        Misc.SendMessage("Skill gain detected!", 68)

def example_wait_multiple_texts():
    """Example: Search for multiple texts"""
    search_terms = ["gold", "treasure", "loot"]
    result = Journal.WaitJournal(search_terms, 10000)
    if result:
        Misc.SendMessage(f"Found: {result}", 68)

def example_filter_spam():
    """Example: Filter spam messages"""
    Journal.FilterText("spam message")
    Journal.FilterText("annoying text")
    # Messages containing these will be hidden
    Misc.SendMessage("Filters applied", 68)
    
    # Remove filters later
    # Journal.RemoveFilterText("spam message")
    # Journal.RemoveFilterText("annoying text")

def example_get_player_messages():
    """Example: Get all messages from a player"""
    player_name = "PlayerName"  # Replace with actual name
    messages = Journal.GetTextByName(player_name, True)
    if messages:
        Misc.SendMessage(f"Messages from {player_name}:", 67)
        for msg in messages[:5]:  # Show first 5
            Misc.SendMessage(msg, 67)

def example_monitor_system_messages():
    """Example: Monitor system messages"""
    Journal.Clear()
    Misc.Pause(5000)  # Do something
    system_msgs = Journal.GetTextByType("System", False)
    for msg in system_msgs:
        if "failed" in msg.lower():
            Misc.SendMessage("Action failed!", 33)
            break

def example_recent_entries_with_details():
    """Example: Get recent journal entries with details"""
    entries = Journal.GetJournalEntry(-1)
    if entries:
        Misc.SendMessage("Last 10 journal entries:", 88)
        for entry in entries[-10:]:  # Last 10 entries
            Misc.SendMessage(f"[{entry.Type}] {entry.Name}: {entry.Text[:50]}", entry.Color)

def example_wait_npc_response():
    """Example: Wait for NPC response"""
    vendor_name = "Vendor"  # Replace with actual vendor name
    Player.ChatSay("vendor buy")
    Journal.Clear()
    if Journal.WaitByName(vendor_name, 3000):
        Misc.SendMessage("Vendor responded!", 68)
        # Vendor responded, can now interact
    else:
        Misc.SendMessage("No vendor response", 33)

def example_check_combat_messages():
    """Example: Check for combat messages"""
    if Journal.SearchByType("hit", "Regular"):
        Misc.SendMessage("Combat detected!", 33)
    
    if Journal.Search("You hit"):
        Misc.SendMessage("You landed a hit!", 68)

def example_clear_specific_messages():
    """Example: Clear specific messages"""
    # Clear all "You see" messages
    Journal.Clear("You see")
    Misc.SendMessage("Cleared 'You see' messages", 67)

def example_get_all_speakers():
    """Example: Get all speakers"""
    speakers = Journal.GetSpeechName()
    if speakers:
        Misc.SendMessage(f"Active speakers ({len(speakers)}): {', '.join(speakers[:5])}", 67)

def example_search_by_color():
    """Example: Search by message color"""
    # System messages are often color 0x03B2
    if Journal.SearchByColor("", 0x03B2):
        Misc.SendMessage("Found system colored message", 67)
    
    # Get all messages of a specific color
    colored_msgs = Journal.GetTextByColor(0x03B2, False)
    if colored_msgs:
        Misc.SendMessage(f"Found {len(colored_msgs)} messages with color 0x03B2", 67)

def example_get_by_serial():
    """Example: Get messages by serial"""
    player_serial = Player.Serial
    player_msgs = Journal.GetTextBySerial(player_serial, True)
    if player_msgs:
        Misc.SendMessage(f"You said {len(player_msgs)} things:", 67)
        for msg in player_msgs[:3]:
            Misc.SendMessage(msg, 67)

def example_skill_gain_monitor():
    """Example: Complete skill gain monitoring system"""
    Journal.Clear()
    Misc.SendMessage("Monitoring for skill gains...", 88)
    
    # Wait for skill gain message
    if Journal.WaitJournal("You have gained", 30000):
        # Get the actual message
        line = Journal.GetLineText("You have gained", False)
        Misc.SendMessage(f"SKILL GAIN: {line}", 68)
        Misc.Beep()
    else:
        Misc.SendMessage("No skill gain in 30 seconds", 53)

# Main execution
try:
    tester = JournalAPITester()
    tester.run_all_tests()
    
    # Optionally run usage examples
    if RUN_USAGE_EXAMPLES:
        debug_message("")
        debug_message("")
        section_header("USAGE EXAMPLES - PRACTICAL DEMONSTRATIONS")
        debug_message("Usage examples are defined as functions above", 67)
        debug_message("Call them individually as needed:", 67)
        debug_message("  - example_wait_for_message()", 67)
        debug_message("  - example_wait_multiple_texts()", 67)
        debug_message("  - example_filter_spam()", 67)
        debug_message("  - example_get_player_messages()", 67)
        debug_message("  - example_monitor_system_messages()", 67)
        debug_message("  - example_recent_entries_with_details()", 67)
        debug_message("  - example_wait_npc_response()", 67)
        debug_message("  - example_check_combat_messages()", 67)
        debug_message("  - example_clear_specific_messages()", 67)
        debug_message("  - example_get_all_speakers()", 67)
        debug_message("  - example_search_by_color()", 67)
        debug_message("  - example_get_by_serial()", 67)
        debug_message("  - example_skill_gain_monitor()", 67)
        section_header("USAGE EXAMPLES COMPLETE")
    
except Exception as e:
    debug_message(f"FATAL ERROR: {e}", 33)
    import traceback
    debug_message(traceback.format_exc(), 33)
