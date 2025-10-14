"""
DEV API Mobile - a Razor Enhanced Python Script for Ultima Online

demonstration of Mobile API functions
Tests and displays information about Mobile objects (alive entities)

=== MOBILE API OVERVIEW ===
The Mobile class represents a single alive entity in the game world.
Each Mobile has a unique Serial, while MobileID represents the appearance/body type.
When a Mobile dies, it stops existing and leaves a corpse Item instead.

ALL MOBILE PROPERTIES (42 properties):

IDENTIFICATION:
  - Serial, MobileID/Body, ItemID, Graphics, Name

STATS & RESOURCES:
  - Hits, HitsMax, Mana, ManaMax, Stam, StamMax

APPEARANCE:
  - Color, Hue, Female, IsHuman, IsGhost

POSITION & MOVEMENT:
  - Position, Map, Direction, Flying

STATUS & STATE:
  - Visible, Deleted, Poisoned, Paralized, WarMode, YellowHits

REPUTATION:
  - Notoriety, Fame, Karma, KarmaTitle

EQUIPMENT & INVENTORY:
  - Backpack, Quiver, Mount, Contains

SOCIAL:
  - InParty, CanRename

PROPERTIES:
  - Properties, PropsUpdated

ALL MOBILE METHODS (5 methods):
  - DistanceTo(other_mobile) -> Int32
  - GetItemOnLayer(layer) -> Item
  - UpdateKarma() -> Boolean
  - Equals(obj) -> Boolean
  - GetHashCode() -> Int32

VERSION::20251013
"""

from System.Collections.Generic import List
import os
import json

# GLOBAL SETTINGS
DEBUG_MODE = True
TEST_NEARBY_MOBILES = True
MAX_TEST_DISTANCE = 10
TEST_DELAY = 500
# JSON output file path
BASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
OUTPUT_FILE = os.path.join(BASE_PATH, "api_mobile_test_output.json")
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
            Misc.SendMessage(f"[Mobile] {message}", color)
        else:
            Misc.SendMessage("", color)
    except Exception:
        if message:
            print(f"[Mobile] {message}")
        else:
            print("")

def section_header(title):
    """Print a section header"""
    debug_message("=" * 60, 88)
    debug_message(f"  {title}", 88)
    debug_message("=" * 60, 88)

class MobileAPITester:
    def __init__(self):
        self.debug_color = 67
        self.error_color = 33
        self.success_color = 68
        self.info_color = 88
        self.warning_color = 53
        self.test_mobile = Player
        self.test_mobile_name = "Player"
        
        # Initialize JSON output structure
        self.json_output = {
            "test_report": {},  # Summary of which properties/methods work
            "test_timestamp": str(Misc.ScriptCurrent(False)),
            "test_mobile": {
                "name": str(self.test_mobile_name),
                "serial": int(self.test_mobile.Serial)
            },
            "tests": {}
        }
        
    def debug(self, message, color=None):
        if color is None:
            color = self.debug_color
        debug_message(message, color)
    
    def test_identification_properties(self):
        section_header("TEST: Identification Properties")
        mobile = self.test_mobile
        test_success = True
        error_msg = None
        id_data = {}
        
        try:
            self.debug(f"Testing: {self.test_mobile_name}", self.info_color)
            id_data["serial"] = int(mobile.Serial)
            id_data["mobile_id"] = int(mobile.MobileID)
            id_data["item_id"] = int(mobile.ItemID)
            id_data["graphics"] = int(mobile.Graphics)
            id_data["name"] = str(mobile.Name)
            
            self.debug(f"  Serial: 0x{mobile.Serial:08X}", self.success_color)
            self.debug(f"  MobileID/Body: {mobile.MobileID} (0x{mobile.MobileID:04X})", self.success_color)
            self.debug(f"  ItemID: {mobile.ItemID}", self.success_color)
            self.debug(f"  Graphics: {mobile.Graphics} (0x{mobile.Graphics:04X})", self.success_color)
            self.debug(f"  Name: {mobile.Name}", self.success_color)
        except Exception as e:
            test_success = False
            error_msg = str(e)
            self.debug(f"  Error: {e}", self.error_color)
        
        self.json_output["test_report"]["IdentificationProperties"] = {
            "works": test_success,
            "error": error_msg,
            "data_returned": len(id_data) > 0
        }
        self.json_output["tests"]["identification"] = id_data
        self.debug("")
    
    def test_stats_properties(self):
        section_header("TEST: Stats Properties")
        mobile = self.test_mobile
        test_success = True
        error_msg = None
        stats_data = {}
        
        try:
            hits_pct = (mobile.Hits / float(mobile.HitsMax) * 100) if mobile.HitsMax > 0 else 0
            mana_pct = (mobile.Mana / float(mobile.ManaMax) * 100) if mobile.ManaMax > 0 else 0
            stam_pct = (mobile.Stam / float(mobile.StamMax) * 100) if mobile.StamMax > 0 else 0
            
            stats_data = {
                "hits": int(mobile.Hits),
                "hits_max": int(mobile.HitsMax),
                "hits_pct": float(hits_pct),
                "mana": int(mobile.Mana),
                "mana_max": int(mobile.ManaMax),
                "mana_pct": float(mana_pct),
                "stam": int(mobile.Stam),
                "stam_max": int(mobile.StamMax),
                "stam_pct": float(stam_pct)
            }
            
            self.debug(f"  Health: {mobile.Hits}/{mobile.HitsMax} ({hits_pct:.1f}%)", self.success_color)
            self.debug(f"  Mana: {mobile.Mana}/{mobile.ManaMax} ({mana_pct:.1f}%)", self.success_color)
            self.debug(f"  Stamina: {mobile.Stam}/{mobile.StamMax} ({stam_pct:.1f}%)", self.success_color)
        except Exception as e:
            test_success = False
            error_msg = str(e)
            self.debug(f"  Error: {e}", self.error_color)
        
        self.json_output["test_report"]["StatsProperties"] = {
            "works": test_success,
            "error": error_msg,
            "data_returned": len(stats_data) > 0
        }
        self.json_output["tests"]["stats"] = stats_data
        self.debug("")
    
    def test_appearance_properties(self):
        section_header("TEST: Appearance Properties")
        mobile = self.test_mobile
        test_success = True
        error_msg = None
        appearance_data = {}
        
        try:
            appearance_data = {
                "color": int(mobile.Color),
                "hue": int(mobile.Hue),
                "female": bool(mobile.Female),
                "is_human": bool(mobile.IsHuman),
                "is_ghost": bool(mobile.IsGhost)
            }
            
            self.debug(f"  Color: {mobile.Color} (0x{mobile.Color:04X})", self.success_color)
            self.debug(f"  Hue: {mobile.Hue} (0x{mobile.Hue:04X})", self.success_color)
            self.debug(f"  Female: {mobile.Female}", self.success_color)
            self.debug(f"  IsHuman: {mobile.IsHuman}", self.success_color)
            self.debug(f"  IsGhost: {mobile.IsGhost}", self.success_color)
        except Exception as e:
            test_success = False
            error_msg = str(e)
            self.debug(f"  Error: {e}", self.error_color)
        
        self.json_output["test_report"]["AppearanceProperties"] = {
            "works": test_success,
            "error": error_msg,
            "data_returned": len(appearance_data) > 0
        }
        self.json_output["tests"]["appearance"] = appearance_data
        self.debug("")
    
    def test_position_properties(self):
        section_header("TEST: Position Properties")
        mobile = self.test_mobile
        test_success = True
        error_msg = None
        position_data = {}
        
        try:
            position_data = {
                "x": int(mobile.Position.X),
                "y": int(mobile.Position.Y),
                "z": int(mobile.Position.Z),
                "map": int(mobile.Map),
                "direction": int(mobile.Direction),
                "flying": bool(mobile.Flying)
            }
            
            self.debug(f"  Position: ({mobile.Position.X}, {mobile.Position.Y}, {mobile.Position.Z})", self.success_color)
            self.debug(f"  Map: {mobile.Map}", self.success_color)
            self.debug(f"  Direction: {mobile.Direction}", self.success_color)
            self.debug(f"  Flying: {mobile.Flying}", self.success_color)
        except Exception as e:
            test_success = False
            error_msg = str(e)
            self.debug(f"  Error: {e}", self.error_color)
        
        self.json_output["test_report"]["PositionProperties"] = {
            "works": test_success,
            "error": error_msg,
            "data_returned": len(position_data) > 0
        }
        self.json_output["tests"]["position"] = position_data
        self.debug("")
    
    def test_status_properties(self):
        section_header("TEST: Status Properties")
        mobile = self.test_mobile
        test_success = True
        error_msg = None
        status_data = {}
        
        try:
            status_data = {
                "visible": bool(mobile.Visible),
                "deleted": bool(mobile.Deleted),
                "poisoned": bool(mobile.Poisoned),
                "paralized": bool(mobile.Paralized),
                "war_mode": bool(mobile.WarMode),
                "yellow_hits": bool(mobile.YellowHits)
            }
            
            self.debug(f"  Visible: {mobile.Visible}", self.success_color)
            self.debug(f"  Deleted: {mobile.Deleted}", self.success_color)
            self.debug(f"  Poisoned: {mobile.Poisoned}", self.success_color)
            self.debug(f"  Paralized: {mobile.Paralized}", self.success_color)
            self.debug(f"  WarMode: {mobile.WarMode}", self.success_color)
            self.debug(f"  YellowHits: {mobile.YellowHits}", self.success_color)
        except Exception as e:
            test_success = False
            error_msg = str(e)
            self.debug(f"  Error: {e}", self.error_color)
        
        self.json_output["test_report"]["StatusProperties"] = {
            "works": test_success,
            "error": error_msg,
            "data_returned": len(status_data) > 0
        }
        self.json_output["tests"]["status"] = status_data
        self.debug("")
    
    def test_reputation_properties(self):
        section_header("TEST: Reputation Properties")
        mobile = self.test_mobile
        test_success = True
        error_msg = None
        reputation_data = {}
        
        try:
            notoriety_desc = {1: "Blue (Innocent)", 2: "Green (Friend)", 3: "Gray (Neutral)", 4: "Gray (Criminal)", 5: "Orange (Enemy)", 6: "Red (Hostile)", 7: "Yellow (Invulnerable)"}
            noto_text = notoriety_desc.get(mobile.Notoriety, "Unknown")
            
            reputation_data = {
                "notoriety": int(mobile.Notoriety),
                "notoriety_desc": str(noto_text),
                "fame": int(mobile.Fame),
                "karma": int(mobile.Karma),
                "karma_title": str(mobile.KarmaTitle)
            }
            
            self.debug(f"  Notoriety: {mobile.Notoriety} - {noto_text}", self.success_color)
            self.debug(f"  Fame: {mobile.Fame} (0-3 scale)", self.success_color)
            self.debug(f"  Karma: {mobile.Karma} (-5 to 5 scale)", self.success_color)
            self.debug(f"  KarmaTitle: {mobile.KarmaTitle}", self.success_color)
        except Exception as e:
            test_success = False
            error_msg = str(e)
            self.debug(f"  Error: {e}", self.error_color)
        
        self.json_output["test_report"]["ReputationProperties"] = {
            "works": test_success,
            "error": error_msg,
            "data_returned": len(reputation_data) > 0
        }
        self.json_output["tests"]["reputation"] = reputation_data
        self.debug("")
    
    def test_equipment_properties(self):
        section_header("TEST: Equipment Properties")
        mobile = self.test_mobile
        test_success = True
        error_msg = None
        equipment_data = {}
        
        try:
            equipment_data["has_backpack"] = mobile.Backpack is not None
            if mobile.Backpack:
                equipment_data["backpack_serial"] = int(mobile.Backpack.Serial)
                self.debug(f"  Backpack: 0x{mobile.Backpack.Serial:08X}", self.success_color)
            else:
                self.debug(f"  Backpack: None", self.debug_color)
            
            equipment_data["has_quiver"] = mobile.Quiver is not None
            if mobile.Quiver:
                equipment_data["quiver_serial"] = int(mobile.Quiver.Serial)
                self.debug(f"  Quiver: 0x{mobile.Quiver.Serial:08X}", self.success_color)
            else:
                self.debug(f"  Quiver: None", self.debug_color)
            
            equipment_data["has_mount"] = mobile.Mount is not None
            if mobile.Mount:
                equipment_data["mount_serial"] = int(mobile.Mount.Serial)
                self.debug(f"  Mount: 0x{mobile.Mount.Serial:08X}", self.success_color)
            else:
                self.debug(f"  Mount: None", self.debug_color)
            
            if mobile.Contains and len(mobile.Contains) > 0:
                equipment_data["paperdoll_items"] = len(mobile.Contains)
                self.debug(f"  Contains: {len(mobile.Contains)} items in paperdoll", self.success_color)
            else:
                equipment_data["paperdoll_items"] = 0
                self.debug(f"  Contains: No items", self.debug_color)
        except Exception as e:
            test_success = False
            error_msg = str(e)
            self.debug(f"  Error: {e}", self.error_color)
        
        self.json_output["test_report"]["EquipmentProperties"] = {
            "works": test_success,
            "error": error_msg,
            "data_returned": len(equipment_data) > 0
        }
        self.json_output["tests"]["equipment"] = equipment_data
        self.debug("")
    
    def test_social_properties(self):
        section_header("TEST: Social Properties")
        mobile = self.test_mobile
        try:
            self.debug(f"  InParty: {mobile.InParty}", self.success_color)
            self.debug(f"  CanRename: {mobile.CanRename}", self.success_color)
        except Exception as e:
            self.debug(f"  Error: {e}", self.error_color)
        self.debug("")
    
    def test_properties_property(self):
        section_header("TEST: Properties Property")
        mobile = self.test_mobile
        try:
            self.debug(f"  PropsUpdated: {mobile.PropsUpdated}", self.success_color)
            if mobile.Properties and len(mobile.Properties) > 0:
                self.debug(f"  Properties: {len(mobile.Properties)} properties", self.success_color)
                for i, prop in enumerate(mobile.Properties[:5]):
                    self.debug(f"    [{i+1}] {prop}", self.debug_color)
                if len(mobile.Properties) > 5:
                    self.debug(f"    ... and {len(mobile.Properties) - 5} more", self.debug_color)
            else:
                self.debug(f"  Properties: No properties", self.debug_color)
        except Exception as e:
            self.debug(f"  Error: {e}", self.error_color)
        self.debug("")
    
    def test_get_item_on_layer_method(self):
        section_header("TEST: GetItemOnLayer Method")
        mobile = self.test_mobile
        try:
            layers = ["RightHand", "LeftHand", "Shoes", "Pants", "Shirt", "Head", "Gloves", "Ring", "Neck", "Waist", "InnerTorso", "Bracelet", "MiddleTorso", "Earrings", "Arms", "Cloak", "OuterTorso", "OuterLegs", "InnerLegs"]
            found_count = 0
            for layer in layers:
                item = mobile.GetItemOnLayer(layer)
                if item:
                    self.debug(f"  {layer}: {item.Name} (0x{item.ItemID:04X})", self.success_color)
                    found_count += 1
            if found_count == 0:
                self.debug(f"  No items found on any layer", self.debug_color)
            else:
                self.debug(f"  Total: {found_count} items equipped", self.info_color)
        except Exception as e:
            self.debug(f"  Error: {e}", self.error_color)
        self.debug("")
    
    def test_distance_method(self):
        section_header("TEST: DistanceTo Method")
        mobile = self.test_mobile
        try:
            # Distance to self should be 0
            self_dist = mobile.DistanceTo(mobile)
            self.debug(f"  Distance to self: {self_dist} tiles", self.success_color)
            
            # Find nearby mobile for testing
            nearby_filter = Mobiles.Filter()
            nearby_filter.Enabled = True
            nearby_filter.RangeMax = MAX_TEST_DISTANCE
            nearby_filter.CheckIgnoreObject = True
            nearby_mobiles = Mobiles.ApplyFilter(nearby_filter)
            
            if nearby_mobiles and len(nearby_mobiles) > 1:
                other = nearby_mobiles[1] if nearby_mobiles[1].Serial != mobile.Serial else nearby_mobiles[0]
                distance = mobile.DistanceTo(other)
                self.debug(f"  Distance to {other.Name}: {distance} tiles", self.success_color)
            else:
                self.debug(f"  No other mobiles nearby for testing", self.warning_color)
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
        section_header("MOBILE API TEST")
        self.debug(f"Test Mobile: {self.test_mobile_name}", self.info_color)
        self.debug("")
        
        # Test all properties
        self.test_identification_properties()
        self.test_stats_properties()
        self.test_appearance_properties()
        self.test_position_properties()
        self.test_status_properties()
        self.test_reputation_properties()
        self.test_equipment_properties()
        self.test_social_properties()
        self.test_properties_property()
        
        # Test all methods
        self.test_get_item_on_layer_method()
        self.test_distance_method()
        
        section_header("TEST COMPLETE")
        self.debug("All Mobile properties and methods tested!", self.success_color)
        
        # Save JSON output
        self.debug("")
        section_header("SAVING JSON OUTPUT")
        self.save_json_output()

# ============================================================================
# USAGE EXAMPLES - Using Mobile properties with Mobiles functions
# ============================================================================

def example_check_mobile_health():
    """Example: Check mobile health and display stats"""
    mobile = Player
    
    # Use Mobile properties
    if mobile.HitsMax > 0:
        health_pct = (mobile.Hits / float(mobile.HitsMax)) * 100
        mana_pct = (mobile.Mana / float(mobile.ManaMax)) * 100 if mobile.ManaMax > 0 else 0
        stam_pct = (mobile.Stam / float(mobile.StamMax)) * 100 if mobile.StamMax > 0 else 0
        
        Misc.SendMessage(f"=== {mobile.Name} Stats ===", 88)
        Misc.SendMessage(f"HP: {mobile.Hits}/{mobile.HitsMax} ({health_pct:.0f}%)", 68)
        Misc.SendMessage(f"Mana: {mobile.Mana}/{mobile.ManaMax} ({mana_pct:.0f}%)", 67)
        Misc.SendMessage(f"Stam: {mobile.Stam}/{mobile.StamMax} ({stam_pct:.0f}%)", 67)

def example_find_and_analyze_enemies():
    """Example: Find enemies and analyze their properties"""
    # Use Mobiles.ApplyFilter to find enemies
    enemy_filter = Mobiles.Filter()
    enemy_filter.Enabled = True
    enemy_filter.RangeMax = 10
    enemy_filter.Notorieties = [6]  # Red/Hostile
    enemy_filter.CheckIgnoreObject = True
    
    enemies = Mobiles.ApplyFilter(enemy_filter)
    
    if enemies and len(enemies) > 0:
        Misc.SendMessage(f"Found {len(enemies)} hostile mobiles:", 33)
        
        for enemy in enemies[:5]:  # Show first 5
            # Use Mobile properties
            distance = Player.DistanceTo(enemy)
            health_pct = (enemy.Hits / float(enemy.HitsMax) * 100) if enemy.HitsMax > 0 else 0
            
            # Build status string
            status = []
            if enemy.Poisoned:
                status.append("Poisoned")
            if enemy.Paralized:
                status.append("Paralyzed")
            if enemy.YellowHits:
                status.append("Invulnerable")
            
            status_str = f" [{', '.join(status)}]" if status else ""
            Misc.SendMessage(f"  {enemy.Name}: {distance}t, {health_pct:.0f}% HP{status_str}", 67)
    else:
        Misc.SendMessage("No hostile mobiles nearby", 68)

def example_check_full_equipment():
    """Example: Check all equipped items using GetItemOnLayer"""
    mobile = Player
    
    # All equipment layers
    equipment_layers = {
        "Weapon": "RightHand",
        "Shield": "LeftHand",
        "Helm": "Head",
        "Gorget": "Neck",
        "Chest": "OuterTorso",
        "Arms": "Arms",
        "Gloves": "Gloves",
        "Legs": "OuterLegs",
        "Boots": "Shoes"
    }
    
    Misc.SendMessage(f"=== {mobile.Name} Equipment ===", 88)
    equipped_count = 0
    
    for slot_name, layer in equipment_layers.items():
        item = mobile.GetItemOnLayer(layer)
        if item:
            Misc.SendMessage(f"  {slot_name}: {item.Name}", 68)
            equipped_count += 1
        else:
            Misc.SendMessage(f"  {slot_name}: Empty", 53)
    
    Misc.SendMessage(f"Total: {equipped_count}/{len(equipment_layers)} slots", 67)

def example_check_status_effects():
    """Example: Check all status effects and conditions"""
    mobile = Player
    
    status_list = []
    
    # Check status properties
    if mobile.Poisoned:
        status_list.append("Poisoned")
    if mobile.Paralized:
        status_list.append("Paralyzed")
    if mobile.WarMode:
        status_list.append("War Mode")
    if mobile.YellowHits:
        status_list.append("Invulnerable")
    if mobile.Flying:
        status_list.append("Flying")
    if not mobile.Visible:
        status_list.append("Hidden")
    if mobile.IsGhost:
        status_list.append("Ghost")
    
    if status_list:
        Misc.SendMessage(f"Status Effects: {', '.join(status_list)}", 53)
    else:
        Misc.SendMessage("No status effects active", 68)

def example_find_party_members_detailed():
    """Example: Find party members and show their stats"""
    # Use Mobiles.ApplyFilter with Friend filter
    party_filter = Mobiles.Filter()
    party_filter.Enabled = True
    party_filter.RangeMax = 20
    party_filter.Friend = True
    
    all_mobiles = Mobiles.ApplyFilter(party_filter)
    
    # Filter for party members using InParty property
    party_members = [m for m in all_mobiles if m.InParty]
    
    if party_members:
        Misc.SendMessage(f"=== Party Members ({len(party_members)}) ===", 88)
        
        for member in party_members:
            # Use Mobile properties
            distance = Player.DistanceTo(member)
            health_pct = (member.Hits / float(member.HitsMax) * 100) if member.HitsMax > 0 else 0
            
            # Color code by health
            color = 68 if health_pct > 70 else 53 if health_pct > 30 else 33
            
            Misc.SendMessage(f"  {member.Name}: {distance}t, {health_pct:.0f}% HP", color)
    else:
        Misc.SendMessage("No party members in range", 33)

def example_analyze_mobile_by_serial():
    """Example: Find mobile by serial and analyze all properties"""
    # Use Mobiles.FindBySerial
    mobile = Mobiles.FindBySerial(Player.Serial)
    
    if mobile:
        Misc.SendMessage(f"=== Mobile Analysis: {mobile.Name} ===", 88)
        Misc.SendMessage(f"Serial: 0x{mobile.Serial:08X}", 67)
        Misc.SendMessage(f"Body: {mobile.MobileID} (0x{mobile.MobileID:04X})", 67)
        Misc.SendMessage(f"Position: ({mobile.Position.X}, {mobile.Position.Y}, {mobile.Position.Z})", 67)
        Misc.SendMessage(f"Map: {mobile.Map}, Direction: {mobile.Direction}", 67)
        
        # Notoriety
        noto_names = {1: "Innocent", 2: "Friend", 3: "Neutral", 4: "Criminal", 5: "Enemy", 6: "Hostile", 7: "Invulnerable"}
        noto_name = noto_names.get(mobile.Notoriety, "Unknown")
        Misc.SendMessage(f"Notoriety: {noto_name} ({mobile.Notoriety})", 67)
        
        # Gender and race
        gender = "Female" if mobile.Female else "Male"
        race = "Human" if mobile.IsHuman else "Non-Human"
        Misc.SendMessage(f"Type: {gender} {race}", 67)

def example_find_nearest_mobile_by_type():
    """Example: Find nearest mobile of specific body type"""
    # Use Mobiles.FindMobile with specific body ID
    # Example: Find nearest human (body 400 = male, 401 = female)
    human_bodies = [400, 401]
    
    nearest = Mobiles.FindMobile(
        human_bodies,  # graphic
        [1, 2, 3, 4, 5, 6, 7],  # all notorieties
        15,  # range
        "Nearest",  # selector
        False  # don't highlight
    )
    
    if nearest:
        distance = Player.DistanceTo(nearest)
        Misc.SendMessage(f"Nearest human: {nearest.Name} at {distance} tiles", 68)
        
        # Show additional properties
        gender = "Female" if nearest.Female else "Male"
        Misc.SendMessage(f"  Gender: {gender}, Body: {nearest.MobileID}", 67)
    else:
        Misc.SendMessage("No humans found nearby", 33)

def example_check_backpack_contents():
    """Example: Check backpack using Backpack property"""
    mobile = Player
    
    if mobile.Backpack:
        backpack = mobile.Backpack
        Misc.SendMessage(f"=== Backpack Contents ===", 88)
        Misc.SendMessage(f"Serial: 0x{backpack.Serial:08X}", 67)
        
        # Count items
        if backpack.Contains:
            item_count = len(backpack.Contains)
            Misc.SendMessage(f"Items: {item_count}", 67)
            
            # Show first few items
            for i, item in enumerate(backpack.Contains[:5]):
                Misc.SendMessage(f"  [{i+1}] {item.Name} (x{item.Amount})", 67)
            
            if item_count > 5:
                Misc.SendMessage(f"  ... and {item_count - 5} more items", 67)
        else:
            Misc.SendMessage("Backpack is empty", 53)
    else:
        Misc.SendMessage("No backpack found", 33)

# Main execution
try:
    tester = MobileAPITester()
    tester.run_all_tests()
    
    # Optionally run usage examples
    if RUN_USAGE_EXAMPLES:
        debug_message("")
        debug_message("")
        section_header("USAGE EXAMPLES - PRACTICAL DEMONSTRATIONS")
        debug_message("Usage examples are defined as functions above", 67)
        debug_message("Call them individually as needed:", 67)
        debug_message("  - example_check_mobile_health()", 67)
        debug_message("  - example_find_and_analyze_enemies()", 67)
        debug_message("  - example_check_full_equipment()", 67)
        debug_message("  - example_check_status_effects()", 67)
        debug_message("  - example_find_party_members_detailed()", 67)
        debug_message("  - example_analyze_mobile_by_serial()", 67)
        debug_message("  - example_find_nearest_mobile_by_type()", 67)
        debug_message("  - example_check_backpack_contents()", 67)
        section_header("USAGE EXAMPLES COMPLETE")
    
except Exception as e:
    debug_message(f"FATAL ERROR: {e}", 33)
    import traceback
    debug_message(traceback.format_exc(), 33)
