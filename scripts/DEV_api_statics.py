"""
DEV API Statics - a Razor Enhanced Python Script for Ultima Online

 demonstration of  Statics API functions
Tests and displays information about Land tiles and Static tiles (trees, decorations, etc.)

=== STATICS API OVERVIEW ===
The Statics class provides access to map information at the tile level.
Important distinction:
  - LAND: For any (X,Y,map) there is exactly 1 Land tile with 1 Z coordinate (the ground)
  - TILE: For any (X,Y,map) there can be multiple Tile items (trees, rocks, decorations, etc.)

=== STATICS.TILEINFO CLASS ===
TileInfo objects hold values representing Tile or Land items for a given (X,Y) coordinate.

TileInfo Properties (actual available properties):
  - StaticID (Int32): The item ID of the static/land tile (use for lookups)
  - ID (UInt16): Alternative item ID property (unsigned 16-bit)
  - StaticHue (Int32): The color/hue of the tile (0 = default color)
  - Hue (Int32): Alternative hue property
  - Z (Int32): Z coordinate (elevation/height) of the tile

Note: TileInfo objects do NOT contain X/Y coordinates. The X/Y position is the parameter
      you pass to GetStaticsLandInfo() or GetStaticsTileInfo(), not a property of the result.
      Only StaticID, StaticHue/Hue, and Z are available in the returned TileInfo objects.

VERSION::20251013
"""

from System.Collections.Generic import List
import os
import json

# GLOBAL SETTINGS
DEBUG_MODE = True
# Test radius around player (in tiles)
TEST_RADIUS = 5
# Map ID (0=Felucca, 1=Trammel, 2=Ilshenar, 3=Malas, 4=Tokuno, 5=TerMur)
TEST_MAP = Player.Map
# JSON output file path
BASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
OUTPUT_FILE = os.path.join(BASE_PATH, "api_statics_test_output.json")
# Run usage examples after tests
RUN_USAGE_EXAMPLES = True
# Sample Static IDs to test (trees, rocks, etc.)
SAMPLE_STATIC_IDS = [
    0x0CCA,  # Tree
    0x0CCE,  # Tree
    0x0CD0,  # Tree
    0x1363,  # Rock
    0x1364,  # Rock
    0x176C,  # Rock
    0x0B41,  # Forge
    0x0FAC,  # Anvil
]
# Sample Land IDs to test
SAMPLE_LAND_IDS = [
    0x0003,  # Grass
    0x0150,  # Dirt
    0x015A,  # Sand
    0x00A8,  # Water
]
# All available flags to test for both Land and Tile items
# These flags determine tile properties like walkability, transparency, etc.
ALL_FLAGS = [
    "None",         # No special flags
    "Translucent",  # Can see through (windows, glass)
    "Wall",         # Acts as a wall (blocks movement)
    "Damaging",     # Causes damage when stepped on (lava, fire)
    "Impassable",   # Cannot walk through
    "Surface",      # Can place items on it (tables, ground)
    "Bridge",       # Acts as a bridge (can walk over)
    "Window",       # Window tile
    "NoShoot",      # Cannot shoot projectiles through
    "Foliage",      # Tree/plant foliage (can walk through but blocks line of sight)
    "HoverOver",    # Can hover over in client
    "Roof",         # Roof tile
    "Door",         # Door tile
    "Wet"           # Water/wet surface
]
#======================================================================

def debug_message(message, color=67):
    """Send debug message to game client"""
    if not DEBUG_MODE:
        return
    try:
        # Don't add prefix for empty messages (used for spacing)
        if message:
            Misc.SendMessage(f"[STATICS] {message}", color)
        else:
            Misc.SendMessage("", color)
    except Exception:
        if message:
            print(f"[STATICS] {message}")
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

class StaticsAPITester:
    def __init__(self):
        self.debug_color = 67  # Light blue
        self.error_color = 33  # Red
        self.success_color = 68  # Green
        self.info_color = 88  # Cyan
        self.warning_color = 53  # Yellow
        
        # Get player position
        self.player_x = Player.Position.X
        self.player_y = Player.Position.Y
        self.player_z = Player.Position.Z
        self.player_map = Player.Map
        
        # JSON output data structure
        self.json_output = {
            "test_report": {},  # Summary of which API functions work on this shard
            "player_position": {
                "x": int(self.player_x),
                "y": int(self.player_y),
                "z": int(self.player_z),
                "map": int(self.player_map)
            },
            "test_radius": TEST_RADIUS,
            "tests": {}
        }
        
    def debug(self, message, color=None):
        """Send a debug message"""
        if color is None:
            color = self.debug_color
        debug_message(message, color)
    
    def save_json_output(self):
        """Save the JSON output to file"""
        try:
            # Ensure directory exists
            directory = os.path.dirname(OUTPUT_FILE)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            
            # Write JSON file
            with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.json_output, f, indent=4)
            
            self.debug(f"JSON output saved to: {OUTPUT_FILE}", self.success_color)
            return True
        except Exception as e:
            self.debug(f"Error saving JSON output: {e}", self.error_color)
            return False
    
    def test_check_deed_house(self):
        """
        Test CheckDeedHouse function
        
        API: Statics.CheckDeedHouse(x, y) -> Boolean
        Purpose: Check if a tile is occupied by a private house
        Note: Must be within sight range (typically 18 tiles on most servers)
        Returns: True if tile is occupied by house, False otherwise
        """
        section_header("TEST: CheckDeedHouse")
        
        self.debug("Checking tiles around player for houses...", self.info_color)
        
        house_locations = []
        house_found = False
        test_success = True
        error_msg = None
        
        for dx in range(-TEST_RADIUS, TEST_RADIUS + 1):
            for dy in range(-TEST_RADIUS, TEST_RADIUS + 1):
                x = self.player_x + dx
                y = self.player_y + dy
                
                try:
                    is_house = Statics.CheckDeedHouse(x, y)
                    if is_house:
                        house_found = True
                        if len(house_locations) < 5:  # Limit to 5 locations
                            house_locations.append({"x": int(x), "y": int(y)})
                        self.debug(f"  HOUSE FOUND at ({x}, {y})", self.success_color)
                except Exception as e:
                    test_success = False
                    error_msg = str(e)
                    self.debug(f"  Error checking ({x}, {y}): {e}", self.error_color)
                    break
            if not test_success:
                break
        
        if not house_found and test_success:
            self.debug("  No houses found in test radius", self.warning_color)
        
        # Record test report
        self.json_output["test_report"]["CheckDeedHouse"] = {
            "works": test_success,
            "error": error_msg,
            "data_returned": house_found
        }
        
        # Record to JSON
        self.json_output["tests"]["CheckDeedHouse"] = {
            "house_found": house_found,
            "house_locations": house_locations,
            "total_houses_displayed": len(house_locations),
            "note": "Limited to first 5 house locations"
        }
        
        self.debug("")
    
    def test_get_land_id(self):
        """
        Test GetLandID function
        
        API: Statics.GetLandID(x, y, map) -> Int32
        Purpose: Get the StaticID of the Land tile at coordinates
        Parameters:
          - x (Int32): X coordinate
          - y (Int32): Y coordinate
          - map (Int32): Map ID (0=Felucca, 1=Trammel, 2=Ilshenar, 3=Malas, 4=Tokuno, 5=TerMur)
        Returns: StaticID of the land tile (the ground/terrain)
        """
        section_header("TEST: GetLandID")
        
        self.debug(f"Getting Land IDs around player position ({self.player_x}, {self.player_y})...", self.info_color)
        
        land_samples = []
        player_land_id = None
        test_success = True
        error_msg = None
        
        # Test player position
        try:
            land_id = Statics.GetLandID(self.player_x, self.player_y, self.player_map)
            player_land_id = int(land_id)
            self.debug(f"  Player position Land ID: 0x{land_id:04X} ({land_id})", self.success_color)
        except Exception as e:
            test_success = False
            error_msg = str(e)
            self.debug(f"  Error getting player Land ID: {e}", self.error_color)
        
        # Test surrounding tiles
        self.debug("  Sampling surrounding tiles:", self.info_color)
        sample_count = 0
        for dx in range(-2, 3, 2):
            for dy in range(-2, 3, 2):
                if dx == 0 and dy == 0:
                    continue
                x = self.player_x + dx
                y = self.player_y + dy
                try:
                    land_id = Statics.GetLandID(x, y, self.player_map)
                    land_samples.append({
                        "x": int(x),
                        "y": int(y),
                        "land_id": int(land_id),
                        "land_id_hex": f"0x{land_id:04X}"
                    })
                    self.debug(f"    ({x}, {y}): 0x{land_id:04X}", self.debug_color)
                    sample_count += 1
                    if sample_count >= 4:
                        break
                except Exception as e:
                    self.debug(f"    Error at ({x}, {y}): {e}", self.error_color)
            if sample_count >= 4:
                break
        
        # Record test report
        self.json_output["test_report"]["GetLandID"] = {
            "works": test_success,
            "error": error_msg,
            "data_returned": player_land_id is not None
        }
        
        # Record to JSON
        self.json_output["tests"]["GetLandID"] = {
            "player_land_id": player_land_id,
            "player_land_id_hex": f"0x{player_land_id:04X}" if player_land_id else None,
            "surrounding_samples": land_samples
        }
        
        self.debug("")
    
    def test_get_land_z(self):
        """
        Test GetLandZ function
        
        API: Statics.GetLandZ(x, y, map) -> Int32
        Purpose: Get the Z coordinate (elevation/height) of the Land tile
        Parameters:
          - x (Int32): X coordinate
          - y (Int32): Y coordinate
          - map (Int32): Map ID
        Returns: Z coordinate (height) of the land tile
        Note: Useful for pathfinding and determining elevation changes
        """
        section_header("TEST: GetLandZ")
        
        self.debug(f"Getting Land Z (height) around player...", self.info_color)
        
        test_success = True
        error_msg = None
        land_z = None
        
        # Test player position
        try:
            land_z = Statics.GetLandZ(self.player_x, self.player_y, self.player_map)
            self.debug(f"  Player position Land Z: {land_z} (Player Z: {self.player_z})", self.success_color)
        except Exception as e:
            test_success = False
            error_msg = str(e)
            self.debug(f"  Error getting player Land Z: {e}", self.error_color)
        
        # Test surrounding tiles to show elevation changes
        self.debug("  Elevation map (3x3 grid):", self.info_color)
        for dy in range(-1, 2):
            line = "    "
            for dx in range(-1, 2):
                x = self.player_x + dx
                y = self.player_y + dy
                try:
                    land_z = Statics.GetLandZ(x, y, self.player_map)
                    line += f"{land_z:4d} "
                except Exception:
                    line += " ERR "
            self.debug(line, self.debug_color)
        
        # Record test report
        self.json_output["test_report"]["GetLandZ"] = {
            "works": test_success,
            "error": error_msg,
            "data_returned": land_z is not None
        }
        
        self.debug("")
    
    def test_get_land_name(self):
        """
        Test GetLandName function
        
        API: Statics.GetLandName(StaticID) -> String
        Purpose: Get the name of a Land tile given its StaticID
        Parameters:
          - StaticID (Int32): The StaticID of a land tile
        Returns: Name of the land tile (e.g., "grass", "dirt", "sand", "water")
        """
        section_header("TEST: GetLandName")
        
        self.debug("Testing GetLandName with sample Land IDs...", self.info_color)
        
        test_success = True
        error_msg = None
        got_name = False
        
        # Test sample land IDs
        for land_id in SAMPLE_LAND_IDS:
            try:
                land_name = Statics.GetLandName(land_id)
                got_name = True
                self.debug(f"  Land ID 0x{land_id:04X}: '{land_name}'", self.success_color)
            except Exception as e:
                test_success = False
                error_msg = str(e)
                self.debug(f"  Error with Land ID 0x{land_id:04X}: {e}", self.error_color)
                break
        
        # Test actual land at player position
        if test_success:
            try:
                land_id = Statics.GetLandID(self.player_x, self.player_y, self.player_map)
                land_name = Statics.GetLandName(land_id)
                got_name = True
                self.debug(f"  Player standing on: '{land_name}' (0x{land_id:04X})", self.info_color)
            except Exception as e:
                test_success = False
                error_msg = str(e)
                self.debug(f"  Error getting player land name: {e}", self.error_color)
        
        # Record test report
        self.json_output["test_report"]["GetLandName"] = {
            "works": test_success,
            "error": error_msg,
            "data_returned": got_name
        }
        
        self.debug("")
    
    def test_get_land_flag(self):
        """
        Test GetLandFlag function
        
        API: Statics.GetLandFlag(staticID, flagname) -> Boolean
        Purpose: Check if a specific flag is active for a Land tile
        Parameters:
          - staticID (Int32): StaticID of the land tile
          - flagname (String): Flag name to check (see ALL_FLAGS list)
        Returns: True if flag is active, False otherwise
        
        Common Land Flags:
          - Surface: Can place items on it
          - Wet: Water/wet surface
          - Impassable: Cannot walk on it
        """
        section_header("TEST: GetLandFlag")
        
        self.debug("Testing GetLandFlag with player's current land...", self.info_color)
        
        try:
            land_id = Statics.GetLandID(self.player_x, self.player_y, self.player_map)
            land_name = Statics.GetLandName(land_id)
            self.debug(f"  Testing Land: '{land_name}' (0x{land_id:04X})", self.success_color)
            
            # Test all flags
            active_flags = []
            for flag in ALL_FLAGS:
                try:
                    is_active = Statics.GetLandFlag(land_id, flag)
                    if is_active:
                        active_flags.append(flag)
                        self.debug(f"    [{flag}]: TRUE", self.success_color)
                except Exception as e:
                    self.debug(f"    [{flag}]: Error - {e}", self.error_color)
            
            if not active_flags:
                self.debug("    No flags active", self.warning_color)
            else:
                self.debug(f"  Active flags: {', '.join(active_flags)}", self.info_color)
                
        except Exception as e:
            self.debug(f"  Error testing land flags: {e}", self.error_color)
        
        # Record test report
        test_success = True
        error_msg = None
        try:
            land_id = Statics.GetLandID(self.player_x, self.player_y, self.player_map)
            Statics.GetLandFlag(land_id, "Surface")
        except Exception as e:
            test_success = False
            error_msg = str(e)
        
        self.json_output["test_report"]["GetLandFlag"] = {
            "works": test_success,
            "error": error_msg,
            "data_returned": test_success
        }
        
        self.debug("")
    
    def test_get_statics_land_info(self):
        """
        Test GetStaticsLandInfo function
        
        API: Statics.GetStaticsLandInfo(x, y, map) -> Statics.TileInfo
        Purpose: Get a TileInfo object representing the Land tile at coordinates
        Parameters:
          - x (Int32): X coordinate
          - y (Int32): Y coordinate
          - map (Int32): Map ID
        Returns: Single TileInfo object with all land tile properties
        
        TileInfo contains: StaticID, StaticHue, Z (no X/Y - those are your input parameters)
        This is the most comprehensive way to get all land tile information at once
        """
        section_header("TEST: GetStaticsLandInfo")
        
        self.debug("Getting TileInfo for Land at player position...", self.info_color)
        
        try:
            tile_info = Statics.GetStaticsLandInfo(self.player_x, self.player_y, self.player_map)
            
            if tile_info:
                self.debug(f"  TileInfo retrieved successfully!", self.success_color)
                # StaticID (Int32): The item ID of the tile - use for lookups and identification
                self.debug(f"    StaticID: 0x{tile_info.StaticID:04X} ({tile_info.StaticID})", self.debug_color)
                # StaticHue (Int32): The color/hue of the tile (0 = default/natural color)
                self.debug(f"    StaticHue: {tile_info.StaticHue}", self.debug_color)
                # Z coordinate - GetStaticsLandInfo only returns StaticID, StaticHue, and Z (no X/Y)
                try:
                    self.debug(f"    Z: {tile_info.Z}", self.debug_color)
                except AttributeError:
                    pass
                
                # Try to get name
                try:
                    name = Statics.GetLandName(tile_info.StaticID)
                    self.debug(f"    Name: '{name}'", self.debug_color)
                except Exception:
                    pass
            else:
                self.debug("  No TileInfo returned", self.warning_color)
                
        except Exception as e:
            self.debug(f"  Error getting TileInfo: {e}", self.error_color)
        
        # Record test report
        test_success = True
        error_msg = None
        got_data = False
        try:
            test_tile = Statics.GetStaticsLandInfo(self.player_x, self.player_y, self.player_map)
            got_data = test_tile is not None
        except Exception as e:
            test_success = False
            error_msg = str(e)
        
        self.json_output["test_report"]["GetStaticsLandInfo"] = {
            "works": test_success,
            "error": error_msg,
            "data_returned": got_data
        }
        
        self.debug("")
    
    def test_get_statics_tile_info(self):
        """
        Test GetStaticsTileInfo function
        
        API: Statics.GetStaticsTileInfo(x, y, map) -> List[Statics.TileInfo]
        Purpose: Get a list of TileInfo objects for all Static tiles at coordinates
        Parameters:
          - x (Int32): X coordinate
          - y (Int32): Y coordinate
          - map (Int32): Map ID
        Returns: List of TileInfo objects (can be empty, or contain multiple statics)
        
        Note: Unlike Land (which is always singular), there can be multiple static tiles
              at the same (X,Y) coordinate (e.g., tree + rock + sign all at same spot)
        Use this to detect trees, rocks, buildings, decorations, etc.
        """
        section_header("TEST: GetStaticsTileInfo")
        
        self.debug("Getting Static Tiles around player...", self.info_color)
        
        player_tiles = []
        all_tiles = []
        
        # Test player position
        try:
            tile_list = Statics.GetStaticsTileInfo(self.player_x, self.player_y, self.player_map)
            
            if tile_list and len(tile_list) > 0:
                self.debug(f"  Found {len(tile_list)} static tile(s) at player position:", self.success_color)
                for i, tile in enumerate(tile_list):
                    self.debug(f"    Tile {i + 1}:", self.info_color)
                    # StaticID: The item ID of the static object (tree, rock, etc.)
                    self.debug(f"      StaticID: 0x{tile.StaticID:04X} ({tile.StaticID})", self.debug_color)
                    # Position: X, Y, Z coordinates - note multiple statics can share X,Y but differ in Z
                    # GetStaticsTileInfo returns tiles with StaticID, StaticHue, and Z only (no X/Y in object)
                    self.debug(f"      Z: {tile.Z}", self.debug_color)
                    # Hue: Color/hue of the static (0 = default color, >0 = custom color)
                    self.debug(f"      Hue: {tile.StaticHue}", self.debug_color)
                    
                    # Try to get name
                    tile_name = "Unknown"
                    try:
                        tile_name = Statics.GetTileName(tile.StaticID)
                        self.debug(f"      Name: '{tile_name}'", self.debug_color)
                    except Exception:
                        pass
                    
                    player_tiles.append({
                        "static_id": int(tile.StaticID),
                        "static_id_hex": f"0x{tile.StaticID:04X}",
                        "name": str(tile_name),
                        "x": int(self.player_x),
                        "y": int(self.player_y),
                        "z": int(tile.Z),
                        "hue": int(tile.StaticHue)
                    })
            else:
                self.debug("  No static tiles at player position", self.warning_color)
        except Exception as e:
            self.debug(f"  Error at player position: {e}", self.error_color)
        
        # Scan surrounding area for statics
        self.debug("  Scanning surrounding area for static tiles...", self.info_color)
        total_statics = 0
        for dx in range(-TEST_RADIUS, TEST_RADIUS + 1):
            for dy in range(-TEST_RADIUS, TEST_RADIUS + 1):
                x = self.player_x + dx
                y = self.player_y + dy
                
                try:
                    tile_list = Statics.GetStaticsTileInfo(x, y, self.player_map)
                    if tile_list and len(tile_list) > 0:
                        total_statics += len(tile_list)
                        for tile in tile_list:
                            tile_name = "Unknown"
                            try:
                                tile_name = Statics.GetTileName(tile.StaticID)
                                if total_statics <= 10:
                                    self.debug(f"    ({x}, {y}, {tile.StaticZ}): '{tile_name}' (0x{tile.StaticID:04X})", self.debug_color)
                            except Exception:
                                if total_statics <= 10:
                                    self.debug(f"    ({x}, {y}, {tile.StaticZ}): 0x{tile.StaticID:04X}", self.debug_color)
                            
                            all_tiles.append({
                                "static_id": int(tile.StaticID),
                                "static_id_hex": f"0x{tile.StaticID:04X}",
                                "name": str(tile_name),
                                "x": int(x),
                                "y": int(y),
                                "z": int(tile.Z),
                                "hue": int(tile.StaticHue)
                            })
                except Exception:
                    pass
        
        self.debug(f"  Total static tiles found in area: {total_statics}", self.info_color)
        
        # Record test report
        test_success = True
        try:
            # Test if the API call works at all
            test_tiles = Statics.GetStaticsTileInfo(self.player_x, self.player_y, self.player_map)
        except Exception as e:
            test_success = False
        
        self.json_output["test_report"]["GetStaticsTileInfo"] = {
            "works": test_success,
            "error": None,
            "data_returned": total_statics > 0
        }
        
        # Record to JSON
        self.json_output["tests"]["GetStaticsTileInfo"] = {
            "player_position_tiles": player_tiles,
            "player_position_tile_count": len(player_tiles),
            "surrounding_area_tiles": all_tiles[:50],  # Limit to first 50 for JSON size
            "total_tiles_found": total_statics
        }
        
        self.debug("")
    
    def test_get_tile_name(self):
        """
        Test GetTileName function
        
        API: Statics.GetTileName(StaticID) -> String
        Purpose: Get the name of a Static tile given its StaticID
        Parameters:
          - StaticID (Int32): The StaticID of a static tile
        Returns: Name of the static tile (e.g., "tree", "rock", "forge", "anvil")
        """
        section_header("TEST: GetTileName")
        
        self.debug("Testing GetTileName with sample Static IDs...", self.info_color)
        
        test_success = True
        error_msg = None
        got_name = False
        
        for static_id in SAMPLE_STATIC_IDS:
            try:
                tile_name = Statics.GetTileName(static_id)
                got_name = True
                self.debug(f"  Static ID 0x{static_id:04X}: '{tile_name}'", self.success_color)
            except Exception as e:
                test_success = False
                error_msg = str(e)
                self.debug(f"  Error with Static ID 0x{static_id:04X}: {e}", self.error_color)
                break
        
        # Record test report
        self.json_output["test_report"]["GetTileName"] = {
            "works": test_success,
            "error": error_msg,
            "data_returned": got_name
        }
        
        self.debug("")
    
    def test_get_tile_height(self):
        """
        Test GetTileHeight function
        
        API: Statics.GetTileHeight(StaticID) -> Int32
        Purpose: Get the height of a Static tile in Z coordinate units
        Parameters:
          - StaticID (Int32): The StaticID of a static tile
        Returns: Height of the tile (how tall it is, not its Z position)
        
        Note: This is the tile's HEIGHT (how tall the object is), not its Z position.
              For example, a tree might have height=20, meaning it's 20 units tall.
        """
        section_header("TEST: GetTileHeight")
        
        self.debug("Testing GetTileHeight with sample Static IDs...", self.info_color)
        
        test_success = True
        error_msg = None
        got_height = False
        
        for static_id in SAMPLE_STATIC_IDS:
            try:
                tile_height = Statics.GetTileHeight(static_id)
                tile_name = Statics.GetTileName(static_id)
                got_height = True
                self.debug(f"  '{tile_name}' (0x{static_id:04X}): Height = {tile_height}", self.success_color)
            except Exception as e:
                test_success = False
                error_msg = str(e)
                self.debug(f"  Error with Static ID 0x{static_id:04X}: {e}", self.error_color)
                break
        
        # Record test report
        self.json_output["test_report"]["GetTileHeight"] = {
            "works": test_success,
            "error": error_msg,
            "data_returned": got_height
        }
        
        self.debug("")
    
    def test_get_tile_flag(self):
        """
        Test GetTileFlag function
        
        API: Statics.GetTileFlag(StaticID, flagname) -> Boolean
        Purpose: Check if a specific flag is active for a Static tile
        Parameters:
          - StaticID (Int32): StaticID of the static tile
          - flagname (String): Flag name to check (see ALL_FLAGS list)
        Returns: True if flag is active, False otherwise
        
        Common Static Flags:
          - Impassable: Cannot walk through (walls, large rocks)
          - Wall: Acts as a wall
          - Foliage: Tree/plant foliage (blocks line of sight)
          - Surface: Can place items on it (tables, counters)
          - Door: Door tile
          - NoShoot: Cannot shoot projectiles through
        """
        section_header("TEST: GetTileFlag")
        
        self.debug("Testing GetTileFlag with sample Static IDs...", self.info_color)
        
        for static_id in SAMPLE_STATIC_IDS[:3]:  # Test first 3 to avoid spam
            try:
                tile_name = Statics.GetTileName(static_id)
                self.debug(f"  Testing Static: '{tile_name}' (0x{static_id:04X})", self.success_color)
                
                active_flags = []
                for flag in ALL_FLAGS:
                    try:
                        is_active = Statics.GetTileFlag(static_id, flag)
                        if is_active:
                            active_flags.append(flag)
                            self.debug(f"    [{flag}]: TRUE", self.success_color)
                    except Exception as e:
                        self.debug(f"    [{flag}]: Error - {e}", self.error_color)
                
                if not active_flags:
                    self.debug("    No flags active", self.warning_color)
                else:
                    self.debug(f"  Active flags: {', '.join(active_flags)}", self.info_color)
                    
            except Exception as e:
                self.debug(f"  Error with Static ID 0x{static_id:04X}: {e}", self.error_color)
        
        # Record test report
        test_success = True
        error_msg = None
        try:
            Statics.GetTileFlag(SAMPLE_STATIC_IDS[0], "Impassable")
        except Exception as e:
            test_success = False
            error_msg = str(e)
        
        self.json_output["test_report"]["GetTileFlag"] = {
            "works": test_success,
            "error": error_msg,
            "data_returned": test_success
        }
        
        self.debug("")
    
    def test_get_item_data(self):
        """
        Test GetItemData function
        
        API: Statics.GetItemData(StaticID) -> ItemData
        Purpose: Get detailed ItemData object for a Static tile
        Parameters:
          - StaticID (Int32): The StaticID of a static tile
        Returns: ItemData object with comprehensive tile information
        
        ItemData Properties (may include):
          - Name: Item name
          - Height: Item height
          - Weight: Item weight
          - Quality: Item quality
          - Quantity: Item quantity
          - Animation: Animation ID
          - Flags: Combined flags value
        
        Note: This provides more detailed information than other functions,
              including properties like weight, animation, and quality.
        """
        section_header("TEST: GetItemData")
        
        self.debug("Testing GetItemData with sample Static IDs...", self.info_color)
        
        for static_id in SAMPLE_STATIC_IDS[:5]:  # Test first 5
            try:
                item_data = Statics.GetItemData(static_id)
                
                if item_data:
                    tile_name = Statics.GetTileName(static_id)
                    self.debug(f"  '{tile_name}' (0x{static_id:04X}):", self.success_color)
                    
                    # Try to access ItemData properties
                    try:
                        self.debug(f"    Name: {item_data.Name}", self.debug_color)
                    except Exception:
                        pass
                    
                    try:
                        self.debug(f"    Height: {item_data.Height}", self.debug_color)
                    except Exception:
                        pass
                    
                    try:
                        self.debug(f"    Weight: {item_data.Weight}", self.debug_color)
                    except Exception:
                        pass
                    
                    try:
                        self.debug(f"    Quality: {item_data.Quality}", self.debug_color)
                    except Exception:
                        pass
                    
                    try:
                        self.debug(f"    Quantity: {item_data.Quantity}", self.debug_color)
                    except Exception:
                        pass
                    
                    try:
                        self.debug(f"    Animation: {item_data.Animation}", self.debug_color)
                    except Exception:
                        pass
                    
                    try:
                        self.debug(f"    Flags: {item_data.Flags}", self.debug_color)
                    except Exception:
                        pass
                else:
                    self.debug(f"  Static ID 0x{static_id:04X}: No ItemData returned", self.warning_color)
                    
            except Exception as e:
                self.debug(f"  Error with Static ID 0x{static_id:04X}: {e}", self.error_color)
        
        # Record test report
        test_success = True
        error_msg = None
        got_data = False
        try:
            test_data = Statics.GetItemData(SAMPLE_STATIC_IDS[0])
            got_data = test_data is not None
        except Exception as e:
            test_success = False
            error_msg = str(e)
        
        self.json_output["test_report"]["GetItemData"] = {
            "works": test_success,
            "error": error_msg,
            "data_returned": got_data
        }
        
        self.debug("")
    
    def run_all_tests(self):
        """Run all Statics API tests"""
        section_header("STATICS API COMPREHENSIVE TEST")
        self.debug(f"Player Position: ({self.player_x}, {self.player_y}, {self.player_z})", self.info_color)
        self.debug(f"Map: {self.player_map}", self.info_color)
        self.debug(f"Test Radius: {TEST_RADIUS} tiles", self.info_color)
        self.debug("")
        
        # Run all tests
        self.test_check_deed_house()
        self.test_get_land_id()
        self.test_get_land_z()
        self.test_get_land_name()
        self.test_get_land_flag()
        self.test_get_statics_land_info()
        self.test_get_statics_tile_info()
        self.test_get_tile_name()
        self.test_get_tile_height()
        self.test_get_tile_flag()
        self.test_get_item_data()
        
        # Final summary
        section_header("TEST COMPLETE")
        self.debug("All Statics API functions have been tested!", self.success_color)
        self.debug("Check the output above for detailed results.", self.info_color)
        
        # Save JSON output
        self.debug("")
        section_header("SAVING JSON OUTPUT")
        self.save_json_output()

# ============================================================================
# USAGE EXAMPLES - Common Statics API patterns
# ============================================================================

def example_1_check_standing_on_water():
    """Example 1: Check if player is standing on water"""
    debug_message("=== Example 1: Check if standing on water ===", 88)
    try:
        land_id = Statics.GetLandID(Player.Position.X, Player.Position.Y, Player.Map)
        is_water = Statics.GetLandFlag(land_id, "Wet")
        if is_water:
            debug_message("You are standing on water!", 68)
        else:
            land_name = Statics.GetLandName(land_id)
            debug_message(f"You are standing on: {land_name} (not water)", 67)
        return is_water
    except Exception as e:
        debug_message(f"Error in example 1: {e}", 33)
        return False

def example_2_find_trees_near_player(radius=5):
    """Example 2: Find all trees near player"""
    debug_message(f"=== Example 2: Find trees within {radius} tiles ===", 88)
    tree_count = 0
    try:
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                x = Player.Position.X + dx
                y = Player.Position.Y + dy
                tiles = Statics.GetStaticsTileInfo(x, y, Player.Map)
                if tiles:
                    for tile in tiles:
                        name = Statics.GetTileName(tile.StaticID)
                        if "tree" in name.lower():
                            tree_count += 1
                            if tree_count <= 5:  # Show first 5
                                debug_message(f"  Tree at ({x}, {y}, {tile.StaticZ}): {name}", 68)
        debug_message(f"Total trees found: {tree_count}", 67)
        return tree_count
    except Exception as e:
        debug_message(f"Error in example 2: {e}", 33)
        return 0

def example_3_check_tile_walkable(x, y, map_id):
    """Example 3: Check if tile is walkable (no impassable statics)"""
    debug_message(f"=== Example 3: Check if tile ({x}, {y}) is walkable ===", 88)
    try:
        tiles = Statics.GetStaticsTileInfo(x, y, map_id)
        is_walkable = True
        if tiles:
            for tile in tiles:
                if Statics.GetTileFlag(tile.StaticID, "Impassable"):
                    tile_name = Statics.GetTileName(tile.StaticID)
                    debug_message(f"  Impassable tile found: {tile_name}", 33)
                    is_walkable = False
                    break
        
        if is_walkable:
            debug_message(f"  Tile is walkable", 68)
        else:
            debug_message(f"  Tile is NOT walkable", 33)
        return is_walkable
    except Exception as e:
        debug_message(f"Error in example 3: {e}", 33)
        return False

def example_4_get_elevation_map(radius=3):
    """Example 4: Get elevation map for pathfinding"""
    debug_message(f"=== Example 4: Get elevation map ({radius}x{radius}) ===", 88)
    elevation_map = {}
    try:
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                x = Player.Position.X + dx
                y = Player.Position.Y + dy
                z = Statics.GetLandZ(x, y, Player.Map)
                elevation_map[(x, y)] = z
        
        # Display elevation grid
        debug_message("  Elevation map:", 67)
        for dy in range(-radius, radius + 1):
            line = "    "
            for dx in range(-radius, radius + 1):
                x = Player.Position.X + dx
                y = Player.Position.Y + dy
                z = elevation_map.get((x, y), 0)
                line += f"{z:4d} "
            debug_message(line, 67)
        
        return elevation_map
    except Exception as e:
        debug_message(f"Error in example 4: {e}", 33)
        return {}

def example_5_detect_houses_in_area(radius=10):
    """Example 5: Detect houses in area"""
    debug_message(f"=== Example 5: Detect houses within {radius} tiles ===", 88)
    house_count = 0
    try:
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                x = Player.Position.X + dx
                y = Player.Position.Y + dy
                if Statics.CheckDeedHouse(x, y):
                    house_count += 1
                    if house_count <= 3:  # Show first 3
                        debug_message(f"  House detected at ({x}, {y})", 68)
        
        if house_count > 0:
            debug_message(f"Total houses detected: {house_count}", 67)
        else:
            debug_message("No houses detected in area", 67)
        return house_count
    except Exception as e:
        debug_message(f"Error in example 5: {e}", 33)
        return 0

def example_6_get_complete_tile_info(x, y, map_id):
    """Example 6: Get complete tile information"""
    debug_message(f"=== Example 6: Complete tile info at ({x}, {y}) ===", 88)
    try:
        # For Land (ground)
        land_info = Statics.GetStaticsLandInfo(x, y, map_id)
        if land_info:
            land_name = Statics.GetLandName(land_info.StaticID)
            debug_message(f"  Land: {land_name} (0x{land_info.StaticID:04X}) at Z={land_info.Z}", 68)
        
        # For Statics (objects)
        static_tiles = Statics.GetStaticsTileInfo(x, y, map_id)
        if static_tiles and len(static_tiles) > 0:
            debug_message(f"  Static tiles: {len(static_tiles)}", 67)
            for i, tile in enumerate(static_tiles[:5]):  # Show first 5
                tile_name = Statics.GetTileName(tile.StaticID)
                debug_message(f"    {i+1}. {tile_name} (0x{tile.StaticID:04X}) at Z={tile.Z}", 67)
        else:
            debug_message("  No static tiles at this location", 67)
        
        return True
    except Exception as e:
        debug_message(f"Error in example 6: {e}", 33)
        return False

def run_usage_examples():
    """Run all usage examples to demonstrate Statics API"""
    section_header("USAGE EXAMPLES - PRACTICAL DEMONSTRATIONS")
    
    # Example 1: Check if standing on water
    example_1_check_standing_on_water()
    debug_message("")
    
    # Example 2: Find trees near player
    example_2_find_trees_near_player(radius=5)
    debug_message("")
    
    # Example 3: Check if current tile is walkable
    example_3_check_tile_walkable(Player.Position.X, Player.Position.Y, Player.Map)
    debug_message("")
    
    # Example 4: Get elevation map
    example_4_get_elevation_map(radius=3)
    debug_message("")
    
    # Example 5: Detect houses
    example_5_detect_houses_in_area(radius=10)
    debug_message("")
    
    # Example 6: Complete tile information
    example_6_get_complete_tile_info(Player.Position.X, Player.Position.Y, Player.Map)
    debug_message("")
    
    section_header("USAGE EXAMPLES COMPLETE")

# Main execution
try:
    tester = StaticsAPITester()
    tester.run_all_tests()
    
    # Optionally run usage examples
    if RUN_USAGE_EXAMPLES:
        debug_message("")
        debug_message("")
        run_usage_examples()
    
except Exception as e:
    debug_message(f"FATAL ERROR: {e}", 33)
    import traceback
    debug_message(traceback.format_exc(), 33)
