"""
VFX Mastery Ascension of Shadow Ritual - a Razor Enhanced Python Script for Ultima Online

Celebrate in the Ascension of your Shadow Mastery   
Timeline-based animation ritual for Shadow Mastery level advancement.
Client-side preview using packet injection - no actual item placement.

SHADOW RITUAL THEME:
- 8-12 shadow orb positions arranged in circle (radius 5, based on mastery level)
- Each orb position has:
  * Alchemical symbol at base (dark shadow hue 1)
  * Shadow orb (dark blue hue 0x081A) floating above with oscillation trail
  * Inner ring: 4 chaga mushrooms (dark hue 1)
  * Middle ring: 3 shadow oil pools (dark hue 1)
  * Outer ring: 5 footprint marks (dark hue 1)
- Nature tendrils VFX at each symbol (dark blue)
- Looping inward energy effect at center (3 loops)
- Late-stage wispy energy at center (dark blue hue 0x081A)
- Shockwave finale with dark blue hue (0x081A)
- Staggered vanishing sequence (decorations > orbs > symbols fade)

================================================================================
ANIMATION TIMELINE SCHEDULE 
================================================================================

TRACK TYPE              | START (ms) | END (ms)  | DURATION | LOOPS | NOTES
------------------------|------------|-----------|----------|-------|------------------
Symbol 1 Spawn          |      0     |  4645     |  Instant |   -   | Staggered spawn
Symbol 2 Spawn          |    100     |  4645     |  Instant |   -   | 100ms apart
Symbol 3 Spawn          |    200     |  4645     |  Instant |   -   | Shadow hue 1
Symbol 4 Spawn          |    300     |  4645     |  Instant |   -   | 
Symbol 5 Spawn          |    400     |  4645     |  Instant |   -   | 
Symbol 6 Spawn          |    500     |  4645     |  Instant |   -   | 
Symbol 7 Spawn          |    600     |  4645     |  Instant |   -   | 
Symbol 8 Spawn          |    700     |  4645     |  Instant |   -   | 
------------------------|------------|-----------|----------|-------|------------------
Orb 1 Spawn (Shadow)    |    200     |  4145     |  Oscillate|   -   | Dark blue 0x081A
Orb 2 Spawn (Shadow)    |    300     |  4145     |  Oscillate|   -   | 100ms apart
Orb 3 Spawn (Shadow)    |    400     |  4145     |  Oscillate|   -   | Trail effect
Orb 4 Spawn (Shadow)    |    500     |  4145     |  Oscillate|   -   | Z-axis movement
Orb 5 Spawn (Shadow)    |    600     |  4145     |  Oscillate|   -   | 
Orb 6 Spawn (Shadow)    |    700     |  4145     |  Oscillate|   -   | 
Orb 7 Spawn (Shadow)    |    800     |  4145     |  Oscillate|   -   | 
Orb 8 Spawn (Shadow)    |    900     |  4145     |  Oscillate|   -   | 
------------------------|------------|-----------|----------|-------|------------------
Decorations (Orb 1)     |    400     |  3645     |  Instant |   -   | 12 items total
Decorations (Orb 2)     |    500     |  3645     |  Instant |   -   | Inner: 4 mushrooms
Decorations (Orb 3)     |    600     |  3645     |  Instant |   -   | Middle: 3 oil pools
Decorations (Orb 4)     |    700     |  3645     |  Instant |   -   | Outer: 5 footprints
Decorations (Orb 5)     |    800     |  3645     |  Instant |   -   | 100ms per orb
Decorations (Orb 6)     |    900     |  3645     |  Instant |   -   | 130ms per item
Decorations (Orb 7)     |   1000     |  3645     |  Instant |   -   | 
Decorations (Orb 8)     |   1100     |  3645     |  Instant |   -   | 
------------------------|------------|-----------|----------|-------|------------------
Center Energy VFX       |    800     |  3510     |  ~900ms  |   3   | Dots inward
------------------------|------------|-----------|----------|-------|------------------
Nature Tendrils 1 VFX   |   1200     |  1540     |  ~340ms  |   2   | Dark blue hue 1
Nature Tendrils 2 VFX   |   1320     |  1660     |  ~340ms  |   2   | 120ms stagger
Nature Tendrils 3 VFX   |   1440     |  1780     |  ~340ms  |   2   | Creates cascade
Nature Tendrils 4 VFX   |   1560     |  1900     |  ~340ms  |   2   | Overlapping
Nature Tendrils 5 VFX   |   1680     |  2020     |  ~340ms  |   2   | Multiple visible
Nature Tendrils 6 VFX   |   1800     |  2140     |  ~340ms  |   2   | at same time
Nature Tendrils 7 VFX   |   1920     |  2260     |  ~340ms  |   2   | 
Nature Tendrils 8 VFX   |   2040     |  2380     |  ~340ms  |   2   | 
------------------------|------------|-----------|----------|-------|------------------
Wispy Energy VFX        |   3065     |  3665     |  ~600ms  |   2   | Late-stage center
------------------------|------------|-----------|----------|-------|------------------
Shockwave Finale        |   3365     |  3565     |  ~200ms  |   1   | Dark blue 0x081A
------------------------|------------|-----------|----------|-------|------------------
Decorations Vanish      |   3645     |  3645     |  Instant |   -   | Instant removal
Orbs Vanish             |   4145     |  4145     |  Instant |   -   | 500ms after decos
Symbols Fade Start      |   4645     |  6145     |  1500ms  |   -   | 5-step fade
                        |            |           |          |       | (shadow hue darken)

================================================================================
VISUAL TIMELINE (Time in seconds, each "=" represents ~100ms)
================================================================================

0.0s    1.0s    2.0s    3.0s    4.0s    5.0s    6.0s
|-------|-------|-------|-------|-------|-------|-------|

Symbol 1:   ████████████████████████████████████████████████  [0-6145ms fade]
Symbol 2:    ███████████████████████████████████████████████  [100-6145ms]
Symbol 3:     ██████████████████████████████████████████████  [200-6145ms]
Symbol 4:      █████████████████████████████████████████████  [300-6145ms]
Symbol 5:       ████████████████████████████████████████████  [400-6145ms]
Symbol 6:        ███████████████████████████████████████████  [500-6145ms]
Symbol 7:         ██████████████████████████████████████████  [600-6145ms]
Symbol 8:          █████████████████████████████████████████  [700-6145ms]

Orb 1:       ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~            [200-4145ms oscillating]
Orb 2:        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~            [300-4145ms oscillating]
Orb 3:         ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~            [400-4145ms oscillating]
Orb 4:          ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~            [500-4145ms oscillating]
Orb 5:           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~            [600-4145ms oscillating]
Orb 6:            ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~            [700-4145ms oscillating]
Orb 7:             ~~~~~~~~~~~~~~~~~~~~~~~~~~~~            [800-4145ms oscillating]
Orb 8:              ~~~~~~~~~~~~~~~~~~~~~~~~~~~            [900-4145ms oscillating]

Deco 1-8:       ████████████████████████████████            [400-3645ms]
                [Inner: mushrooms, Middle: oil pools, Outer: footprints]

Center VFX:         =========|=========|=========            [800-3510ms]
                    [loop 1] [loop 2] [loop 3]

Tendrils 1:              ████                              [1200-1540ms x2]
Tendrils 2:               ████                             [1320-1660ms x2]
Tendrils 3:                ████                            [1440-1780ms x2]
Tendrils 4:                 ████                           [1560-1900ms x2]
Tendrils 5:                  ████                          [1680-2020ms x2]
Tendrils 6:                   ████                         [1800-2140ms x2]
Tendrils 7:                    ████                        [1920-2260ms x2]
Tendrils 8:                     ████                       [2040-2380ms x2]

Wispy VFX:                                ██████              [3065-3665ms x2]
Shockwave:                              ██                    [3365-3565ms]

Vanish:                                     ▼                 [3645ms decorations]
Vanish:                                          ▼            [4145ms orbs]
Fade:                                                 █████   [4645-6145ms symbols]

================================================================================

CONFIGURATION:
- ELEMENT_COUNT: 8 (mastery level, configurable 1-12)
- CIRCLE_RADIUS: 5 tiles from center
- CIRCLE_ROTATION: 45 degrees offset
- COLOR_SCHEME: "blue" (shadow theme)
- SHADOW_HUE: 1 (dark blue/black for symbols & decorations)
- SHADOW_ORB_HUE: 0x081A (dark blue for orbs & VFX)
- NATURE_TENDRILS_STAGGER_DELAY_MS: 120ms between starts
- CENTER_ENERGY_LOOP_COUNT: 3 repetitions
- NATURE_TENDRILS_LOOP_COUNT: 2 repetitions per symbol
- MINIMUM_TICK_RATE_MS: 50ms (~20 FPS) with queue-based rate limiting
- MAX_UPDATES_PER_FRAME: 8 operations (strict enforcement)
- DECORATION_RINGS: 3 per orb (inner: mushrooms, middle: oil pools, outer: footprints)
- OSCILLATION: Shadow orbs float with Z-axis trail effect

VERSION::20251019
"""

import random
import time
import math

DEBUG_MODE = False
USE_MASTERY_LEVEL_FROM_GUMP = False # currently not implemented

RITUAL_CONFIG = {
    # Circle geometry
    "circle": {
        "radius": 5,              # Distance from center for symbol placement
        "element_count": 8,       # Number of elements in the circle ( mastery level )
        "rotation_degrees": 45,   # Base rotation offset
    },
    
    # Color scheme settings
    "color": {
        "scheme": "blue",                    # Shadow dark blue theme
        "enable_hue_cycling": False,         # Keep consistent dark theme
        "enable_brightness_variation": False, # No variation - stay dark
        "brightness_cycle_mode": "wave",     # Wave is sequential around circle
        "shadow_orb_hue": 0x081A,                 # Very dark blue hue
        "shadow_hue": 1,                     # Dark blue/black hue for all items
        "dark_blue_hue": 0x081A,                  # Dark blue hue for VFX effects
        "shockwave_hue": 0x081A,                  # Shockwave finale hue (dark blue)
    },
    
    # Phase 1: Alchemical symbols (base of each orb position)
    "phase_symbols": {
        "spawn_delay_ms": 100,     # Delay between placing each symbol
        "z_offset": 2,            # Ground level
        "use_shadow_hue": True,   # Use shadow hue (1) for symbols
    },
    
    # Phase 2: Shadow Orbs (floating above symbols)
    "phase_orbs": {
        "spawn_delay_ms": 100,     # Delay between placing orbs
        "start_offset_ms": 200,   # Delay after symbols start
        "z_offset": 10,            # Base Z height for orbs
        "item_id": 0x573E,        # Energy orb
        "use_shadow_hue": True,   # Use shadow orb hue
        "oscillate": True,        # Enable Z-axis oscillation with trail effect
        "z_amplitude": 8,        # Oscillate +/- 10 Z from base
        "oscillate_speed_ms": 150, # Update Z every 150ms
        "trail_length": 3,        # 2 trail items visible smooth effect
    },
    
    # Phase 3: Small decoration circles around each orb
    "phase_decorations": {
        "start_offset_ms": 400,   # Delay after orbs start
        "spawn_delay_per_orb_ms": 100,  # Delay between each orb's decorations
        "spawn_delay_per_item_ms": 130,  # Delay between items in same circle
        
        # Inner decoration ring (around each orb)
        "inner_ring": {
            "item_id": "mushroom_chaga",        # Daemon blood
            "radius": 1,              # 1 tile from orb center
            "points": 4,              # 4 items in circle
            "z_offset": 2,            # Ground level
            "hue": 1,            # Color (0x0000 = natural item color, or specify hue)
            "use_scheme_hue": False,   # If True, use color scheme; if False, use "hue" value
        },
        
        # Middle decoration ring (around each orb)
        "middle_ring": {
            "item_ids": "BLOOD_SPLATTERS",
            "radius": 2,              # 2 tiles from orb center
            "points": 3,              # 3 items in circle
            "z_offset": 2,            # Slightly elevated
            "random_selection": True, # Randomly pick from item_ids
            "hue": 0x0000,            # Color (0x0000 = natural item color, or specify hue)
            "use_scheme_hue": True,  # If True, use color scheme; if False, use "hue" value
        },
        
        # Outer decoration ring (around each orb) - black puddles
        "outer_ring": {
            "item_ids": "footsteps",  # Use BLOOD_SPLATTERS list (will be black puddles)
            "radius": 3,              # 3 tiles from orb center
            "points": 5,              # 5 items in circle
            "z_offset": 2,            # Ground level
            "random_selection": True, # Randomly pick from splatters
            "hue": 1,                 # Dark blue/black hue
            "use_scheme_hue": True,  # Use hue value (1)
        }
        
    },
    
    # Phase 3: Drifting Shadow Clouds
    "phase_drifting_clouds": {
        "enabled": False,          # Enable drifting shadow clouds
        "cloud_count": 5,         # Number of clouds to spawn
        "start_delay_ms": 500,    # Spawn after symbols
        "spawn_area_radius": 3,   # Radius around center to spawn clouds
        "min_distance": 1,        # Minimum distance between clouds (no overlap)
        "z_offset": 10,           # Base height of clouds (above orbs)
        "z_amplitude": 1,         # Random Z movement range (+/- 3)
        "drift_speed_ms": 300,    # Update Z position every 300ms
        "hue": 1,                 # Dark blue/black hue for clouds
        "vfx_frames": [0x5440, 0x5444],  # Cloud VFX frames (will cycle through)
        "frame_duration_ms": 110, # Time per frame for animation
        "camera_offset": True,    # Offset position to appear "in front" of player
        "offset_x": 3,            # X offset (east) - moves toward camera in isometric
        "offset_y": 3,            # Y offset (south) - moves toward camera in isometric
        # Note: In UO's isometric view, +X is east, +Y is south
        # Moving southeast (+X, +Y) brings objects toward the camera/front
    },
    
    # Phase 4: Center inward energy
    "phase_center_energy": {
        "vfx_effect": "dots_inward",
        "start_delay_ms": 800,    # When center energy starts
        "loop_count": 3,          # Number of times to loop
        "z_offset": 1,           # Height of center energy
        "hue": 0x0000,            # Color (0x0000 = use scheme)
        "camera_offset": True,    # Offset position to appear "in front" of player
        "offset_x": 2,            # X offset (east) - moves toward camera in isometric
        "offset_y": 2,            # Y offset (south) - moves toward camera in isometric
        # Note: In UO's isometric view, +X is east, +Y is south
        # Moving southeast (+X, +Y) brings objects toward the camera/front
    },
    
    # Phase 5: Symbol VFX (downward drops at each symbol)
    "phase_symbol_vfx": {
        "vfx_effect": "nature_tenrils",
        "start_offset_ms": 400,   # Delay after center energy starts
        "stagger_delay_ms": 120,  # Delay between each symbol VFX (overlapping)
        "loop_count": 2,          # Number of times to loop
        "z_offset": -15,           # Same height as center energy
        "hue": 1, 
        "use_shadow_hue": False,  # Use dark blue shadow hue for VFX
    },
    
    # Phase 5b: Late-stage wispy energy at center
    "phase_center_energy_late": {
        "vfx_effect": "wispy_lines_energy_around",
        "delay_after_symbol_vfx_ms": 100,  # Start shortly before finale
        "loop_count": 1,          # Number of times to loop
        "z_offset": 20,           # Height of center energy
        "hue": 0x081A,            # Color (0x0000 = use scheme)
        "camera_offset": True,    # Offset position to appear "in front" of player
        "offset_x": 1,            # X offset (east) - moves toward camera in isometric
        "offset_y": 1,            # Y offset (south) - moves toward camera in isometric
    },
    
    # Phase 6: Finale shockwave
    "phase_finale": {
        "vfx_effect": "shockwave",
        "delay_after_symbol_vfx_ms": 300,  # Delay after symbol VFX complete
        "loop_count": 1,          # Number of shockwave pulses
        "z_offset": 12,            # Ground level
        "use_shockwave_hue": True,  # Use shockwave hue 
        "camera_offset": True,    # Offset position to appear "in front" of player
        "offset_x": 2,            # X offset (east) - moves toward camera in isometric
        "offset_y": 2,    
    },
    
    # Phase 7: Fade out
    "phase_fade": {
        "delay_after_finale_ms": 100,  # When fade starts after finale
        "fade_steps": 4,               # Number of darkening steps
        "fade_step_delay_ms": 100,     # Delay per fade step
        "use_brightness_levels": True, # Use hue family brightness for fade
    },
    
    # Timeline system
    "timeline": {
        "minimum_tick_rate_ms": 20,  # ~6-7 FPS to prevent client overload
        "max_updates_per_frame": 18,   # Limit simultaneous updates per frame
    },
}

# UO HUE SYSTEM KNOWLEDGE:
# - Hues 1-906 organized in families of ~5 (brightness variations)
# - Within family: lower numbers = darker, higher = brighter
# - Example: 32-36 are red family (32=dark, 36=bright)

# Hue families organized by color with variations 
HUE_FAMILIES = {
    "blue": {
        "base_hues": [1, 1, 1, 1, 1],  # Shadow dark blue (consistent)
        "description": "Shadow dark blue,  darkness"
    },
}

# =============================================================================
# ALCHEMICAL SYMBOL ITEM IDs
# =============================================================================

# Alchemical symbols (base of each orb position)
ALCHEMICAL_SYMBOLS = [
    0x9BD1,0x9BD2,0x9BD3,0x9BD4,0x9BD5,0x9BD6,0x9BD7,0x9BD8,0x9BD9,0x9BDA,
    0x9BDB,0x9BDC,0x9BDD,0x9BDE,0x9BDF,0x9BE0,0x9BE1,0x9BE2,0x9BE3,0x9BE4,
    0x9BE5,0x9BE6,0x9BE7,0x9BE8,0x9BE9,0x9BEA,0x9BEB,0x9BEC,0x9BED,0x9BEE
]


# =============================================================================
# SHADOW RITUAL ITEM IDs
# =============================================================================

# Shadow ritual decoration items (circles around each orb)
SHADOW_ITEMS = {
    "mushroom_chaga": 0x5743,                 # Inner ring around orb (chaga mushroom)
    "footsteps": [0x1E03, 0x1E04, 0x1E05, 0x1E06],  # Footprint variants
    "void_essence": 0x4007,                   # Void essence item
    "shadow_orb": 0x573E,                     # Shadow orb (with dark blue hue)
}

# Shadow oil pools (dark puddles around orbs)
SHADOW_OIL_POOLS = [ 
    0x122A, 0x122B, 0x122C, 0x122D, 0x122E, 0x122F
]


# =============================================================================
# VFX EFFECT DEFINITIONS 
# =============================================================================

VFX_EFFECTS = {
    # Multi-frame animated VFX
    "dots_inward": {
        "frames": [0xAA80],  # Single static frame (use list literal)
        #"frames": list(range(0xAA80, 0xAA8A)),  # Dots converging inward (10 frames)
        "frame_duration": 150,  # Slower for better visibility 
    },
    "firepillar": {
        "frames": list(range(0xA437, 0xA44A)),  # Rising pillar (19 frames)
        "frame_duration": 85,
    },
    "shockwave": {
        "frames": [0xAAE5],  # Single static frame (use list literal)
        #"frames": list(range(0xAAE5, 0xAAF1)),  # Expanding shockwave (12 frames)
        "frame_duration": 100,
    },
    "wind_whirl": {
        "frames": list(range(0x6D60, 0x6D66)),  # 0x6D60 to 0x6D65 (6 frames)
        "frame_duration": 100,
    },
    "orrey_energy_sphere_rings": {
        "frames": list(range(0x6E10, 0x6E15)),  # 0x6E10 to 0x6E15 (5 frames)
        "frame_duration": 100,
    },
    "wispy_lines_energy_around": {
        "frames": [0x5480],  # Single static frame (use list literal)
        #"frames": list(range(0x5480, 0x5486)),  # 0x5480 to 0x5486 (6 frames)
        "frame_duration": 100,
    },
    "downward_drops": {
        "frames": list(range(0x549B, 0x549F)),  # 0x549B to 0x549F (4 frames)
        "frame_duration": 150,
    },
    "nature_tenrils": {
        "frames": [0x6D01],  # 0x6D01 to 0x6D0C (11 frames)
        "frame_duration": 150,
    },
    
    # Single-frame static VFX examples (use list for single frame)
    "static_cloud": {
        "frames": [0xA9D6],  # Single static frame (use list literal)
        # For animation: list(range(0xA9D6, 0xA9DF)) - multiple frames
        "frame_duration": 300,  # Time per frame (ignored for single frame)
    },
    "static_energy_sphere": {
        "frames": [0x6E10],  # Single static energy sphere
        "frame_duration": 100,  # Ignored for single frame
    },
    "static_wispy": {
        "frames": [0x5480],  # Single static wispy energy
        "frame_duration": 100,  # Ignored for single frame
    },
}

# Active effects for different phases
INWARD_ENERGY_EFFECT = "dots_inward"
SYMBOL_EFFECT = "nature_tenrils"  # Changed from firepillar to dots_inward
FINALE_EFFECT = "shockwave"

# =============================================================================
# GUMP CONFIGURATION 
# =============================================================================

# Gump configuration
GUMP_ID = 4121213728  # Unique gump ID 
GUMP_START_X = 350
GUMP_START_Y = 350
GUMP_WIDTH = 160
GUMP_HEIGHT = 220

# Button IDs
BUTTON_ASCEND = 1
BUTTON_LEVEL_BASE = 10  # Buttons 10-21 for levels 1-12

# Button styling
BUTTON_LARGE_ART = 1  # Large button art (80x40)
BUTTON_LARGE_WIDTH = 80
BUTTON_LARGE_HEIGHT = 40
BUTTON_SMALL_ART = 210  # Small square button art
BUTTON_SMALL_WIDTH = 30
BUTTON_SMALL_HEIGHT = 30
SLIVER_OVERLAY_TILE = 2624  # Dark tile overlay

# Global state
CURRENT_MASTERY_LEVEL = 8  # Default mastery level


# =============================================================================
# PACKET HANDLING FUNCTIONS
# =============================================================================

def debug_message(msg, color=67):
    """Send debug message to game client"""
    if not DEBUG_MODE:
        return
    try:
        Misc.SendMessage(f"[VFX_CIRCLE] {msg}", color)
    except Exception:
        print(f"[VFX_CIRCLE] {msg}")

def _convert_packet_to_bytes(packet_list):
    """Convert hex string list to byte array"""
    byte_list = []
    for value in packet_list:
        if value:
            byte_list.append(int(value, 16))
        else:
            byte_list.append(0)
    return byte_list

def _format_hex_4_with_space(value):
    """Format integer as 4-digit hex with space (e.g., '12 34')"""
    s = f"{int(value) & 0xFFFF:04X}"
    return s[:2] + " " + s[2:]

def _send_fake_item(item_x, item_y, item_z, item_id, hue=0x0000):
    """
    Send a client-only item render packet at specified location.
    
    Args:
        item_x: X coordinate
        item_y: Y coordinate
        item_z: Z coordinate
        item_id: Item ID to display
        hue: Optional hue/color override
    
    Returns:
        Serial number of the fake item (for later removal)
    """
    try:
        # Base packet template for item display
        packet = (
            "F3 00 01 00 48 FC BB 12 "
            + _format_hex_4_with_space(item_id)
            + " 00 00 01 00 01 05 88 06 88 0A 00 04 15 20 00 00"
        )
        packet_list = packet.split(" ")

        # Generate random serial for this fake item
        serial_hex = f"{random.randrange(0x40000000, 0x7FFFFFFF):08X}"

        # Convert coordinates to hex
        i_loc_x = f"{int(item_x):04X}"
        i_loc_y = f"{int(item_y):04X}"
        i_loc_z = f"{int(item_z):02X}"

        # Split hex values into bytes
        x1, x2 = i_loc_x[:2], i_loc_x[2:]
        y1, y2 = i_loc_y[:2], i_loc_y[2:]
        s1, s2, s3, s4 = serial_hex[0:2], serial_hex[2:4], serial_hex[4:6], serial_hex[6:8]

        # Format hue
        hue_hex = _format_hex_4_with_space(hue)
        hues = hue_hex.split(" ")

        # Inject values into packet
        packet_list[4] = s1
        packet_list[5] = s2
        packet_list[6] = s3
        packet_list[7] = s4
        packet_list[15] = x1
        packet_list[16] = x2
        packet_list[17] = y1
        packet_list[18] = y2
        packet_list[19] = i_loc_z
        packet_list[21] = hues[0]
        packet_list[22] = hues[1]

        # Convert to bytes and send
        byte_list = _convert_packet_to_bytes(packet_list)
        PacketLogger.SendToClient(byte_list)
        
        # Return serial as integer for tracking
        return int(serial_hex, 16)
        
    except Exception as e:
        debug_message(f"Failed to send item packet: {e}", 33)
        return None

def _remove_fake_item(serial):
    """
    Send packet to remove a client-side item by serial.
    
    Args:
        serial: Serial number of the item to remove
    """
    try:
        # Remove item packet (0x1D)
        serial_hex = f"{int(serial):08X}"
        packet = [
            0x1D,  # Packet ID
            int(serial_hex[0:2], 16),
            int(serial_hex[2:4], 16),
            int(serial_hex[4:6], 16),
            int(serial_hex[6:8], 16)
        ]
        
        PacketLogger.SendToClient(packet)
        
    except Exception as e:
        debug_message(f"Failed to remove item: {e}", 33)

# =============================================================================
# GEOMETRY FUNCTIONS
# =============================================================================

def generate_circle_points(center_x, center_y, radius, count, rotation=0):
    """
    Generate points in a circle around center.
    
    Args:
        center_x, center_y: Center coordinates
        radius: Circle radius
        count: Number of points
        rotation: Rotation offset in degrees
    
    Returns:
        List of (x, y) tuples
    """
    points = []
    angle_step = 360.0 / count
    
    for i in range(count):
        angle_deg = (i * angle_step + rotation) % 360
        angle_rad = math.radians(angle_deg)
        
        x = center_x + int(radius * math.cos(angle_rad))
        y = center_y + int(radius * math.sin(angle_rad))
        
        points.append((x, y))
    
    return points

def generate_line_points(start_x, start_y, end_x, end_y, steps):
    """
    Generate points along a line from start to end.
    
    Args:
        start_x, start_y: Starting coordinates
        end_x, end_y: Ending coordinates
        steps: Number of points along the line
    
    Returns:
        List of (x, y) tuples
    """
    points = []
    
    for i in range(steps + 1):
        t = i / float(steps) if steps > 0 else 0
        x = int(start_x + (end_x - start_x) * t)
        y = int(start_y + (end_y - start_y) * t)
        points.append((x, y))
    
    return points

# =============================================================================
# COLOR MANAGEMENT
# =============================================================================

def get_scheme_hue(brightness="brightest"):
    """
    Get a hue from the active color scheme.
    
    Args:
        brightness: "brightest", "darkest", or "middle"
    
    Returns:
        Hue value (integer)
    """
    scheme = RITUAL_CONFIG["color"]["scheme"]
    hue_family = HUE_FAMILIES.get(scheme, HUE_FAMILIES["blue"])
    base_hues = hue_family["base_hues"]
    
    if not base_hues:
        return 0x0000
    
    if brightness == "brightest":
        return base_hues[-1]  # Last hue is brightest
    elif brightness == "darkest":
        return base_hues[0]   # First hue is darkest
    else:  # middle
        return base_hues[len(base_hues) // 2]

def get_hue_for_element(element_index, total_elements):
    """
    Get hue for an element based on index and color scheme.
    Uses UO hue family system with brightness variations.
    
    Args:
        element_index: Index of the element (0-based)
        total_elements: Total number of elements
    
    Returns:
        Hue value (integer)
    """
    # Get the active hue family
    scheme = RITUAL_CONFIG["color"]["scheme"]
    hue_family = HUE_FAMILIES.get(scheme, HUE_FAMILIES["blue"])
    base_hues = hue_family["base_hues"]
    
    if not base_hues:
        return 0x0000
    
    if RITUAL_CONFIG["color"]["enable_hue_cycling"]:
        # Cycle through brightness levels based on mode
        if RITUAL_CONFIG["color"]["brightness_cycle_mode"] == "ascending":
            # Darkest to brightest as elements progress
            brightness_index = int((element_index / total_elements) * len(base_hues))
            brightness_index = min(brightness_index, len(base_hues) - 1)
            hue = base_hues[brightness_index]
            
        elif RITUAL_CONFIG["color"]["brightness_cycle_mode"] == "descending":
            # Brightest to darkest as elements progress
            brightness_index = int((element_index / total_elements) * len(base_hues))
            brightness_index = min(brightness_index, len(base_hues) - 1)
            hue = base_hues[-(brightness_index + 1)]
            
        elif RITUAL_CONFIG["color"]["brightness_cycle_mode"] == "wave":
            # Wave pattern: dark->bright->dark
            progress = (element_index / total_elements) * 2.0  # 0 to 2
            if progress <= 1.0:
                # First half: ascending
                brightness_index = int(progress * len(base_hues))
            else:
                # Second half: descending
                brightness_index = int((2.0 - progress) * len(base_hues))
            brightness_index = min(max(0, brightness_index), len(base_hues) - 1)
            hue = base_hues[brightness_index]
            
        elif RITUAL_CONFIG["color"]["brightness_cycle_mode"] == "random":
            # Random brightness for each element
            hue = random.choice(base_hues)
            
        else:
            # Default: cycle through all brightness levels
            brightness_index = element_index % len(base_hues)
            hue = base_hues[brightness_index]
    else:
        # Use middle brightness level (balanced)
        mid_index = len(base_hues) // 2
        hue = base_hues[mid_index]
    
    if RITUAL_CONFIG["color"]["enable_brightness_variation"]:
        # Add slight variation within brightness level (+/- 1 in hue family)
        variation = random.randint(-1, 1)
        hue = max(1, min(906, hue + variation))
    
    return hue

def darken_hue(hue, steps):
    """
    Darken a hue using UO hue family system.
    Special handling for doom hue (0x0916) to keep it dark.
    
    Args:
        hue: Original hue value
        steps: Number of darkening steps
    Returns:Darkened hue value
    """
    # Special handling for shadow hue - keep it consistently dark
    shadow_hue = RITUAL_CONFIG["color"].get("shadow_hue", 1)
    if hue == shadow_hue or hue == 1:
        # Shadow hue stays dark (already very dark blue/black)
        # Only fade to pure black on final steps
        if steps >= 4:
            return 0x0001  # Nearly black
        else:
            return shadow_hue  # Keep shadow hue
    
    if RITUAL_CONFIG["phase_fade"]["use_brightness_levels"]:
        # Find which family this hue belongs to
        hue_family = HUE_FAMILIES.get(RITUAL_CONFIG["color"]["scheme"], HUE_FAMILIES["blue"])
        base_hues = hue_family["base_hues"]
        
        # Find current brightness level in family
        try:
            current_index = base_hues.index(hue)
        except ValueError:
            # Hue not in family, find closest
            current_index = len(base_hues) - 1
            for i, family_hue in enumerate(base_hues):
                if abs(family_hue - hue) < abs(base_hues[current_index] - hue):
                    current_index = i
        
        # Move toward darker end of family
        target_index = max(0, current_index - steps)
        return base_hues[target_index]
    else:
        # Simple darkening by reducing hue value (fallback)
        darkened = max(1, hue - (5 * steps))  # 5 hue units per step
        return darkened

# =============================================================================
# TIMELINE ANIMATION SYSTEM 
# =============================================================================

class AnimationTrack:
    """Base class for timeline animation tracks."""
    
    def __init__(self, start_time_ms=0, duration_ms=None, loop=False, loop_count=None):
        self.start_time_ms = int(start_time_ms)
        self.duration_ms = int(duration_ms) if duration_ms is not None else None
        self.loop = loop
        self.loop_count = loop_count
        self.is_active = False
        self.is_complete = False
        self.current_loop_iteration = 0
        self.track_start_time_ms = 0
        
    def should_start(self, current_timeline_time_ms):
        if self.is_active or self.is_complete:
            return False
        return current_timeline_time_ms >= self.start_time_ms
    
    def get_local_time_ms(self, current_timeline_time_ms):
        if not self.is_active:
            return 0
        return current_timeline_time_ms - self.track_start_time_ms
    
    def check_completion(self, current_timeline_time_ms):
        if not self.is_active or self.is_complete:
            return self.is_complete
        if self.duration_ms is None:
            return True
        local_time = self.get_local_time_ms(current_timeline_time_ms)
        if local_time >= self.duration_ms:
            if self.loop:
                if self.loop_count is None:
                    self.restart_track(current_timeline_time_ms)
                    return False
                elif self.current_loop_iteration < self.loop_count - 1:
                    self.current_loop_iteration += 1
                    self.restart_track(current_timeline_time_ms)
                    return False
                else:
                    return True
            else:
                return True
        return False
    
    def restart_track(self, current_timeline_time_ms):
        self.track_start_time_ms = current_timeline_time_ms
    
    def start(self, current_timeline_time_ms):
        self.is_active = True
        self.track_start_time_ms = current_timeline_time_ms
        self.on_start()
    
    def update(self, current_timeline_time_ms):
        if not self.is_active or self.is_complete:
            return
        if self.check_completion(current_timeline_time_ms):
            self.is_complete = True
            self.on_complete()
            return
        local_time = self.get_local_time_ms(current_timeline_time_ms)
        self.on_update(local_time)
    
    def on_start(self):
        pass
    
    def on_update(self, local_time_ms):
        pass
    
    def on_complete(self):
        pass

class StaticItemTrack(AnimationTrack):
    """
    Spawns a static item that persists, optionally fades, then removes.
    Handles entire lifecycle: spawn -> persist -> [optional fade] -> remove
    """
    
    def __init__(self, start_time_ms, end_time_ms, item_id, position, hue=0x0000, 
                 fade_steps=0, fade_duration_ms=0):
        """
        Args:
            start_time_ms: When to spawn
            end_time_ms: When to remove (or start fading if fade_steps > 0)
            item_id: Item to display
            position: (x, y, z) tuple
            hue: Item hue
            fade_steps: Number of fade steps (0 = instant removal)
            fade_duration_ms: Total fade duration
        """
        total_duration = (end_time_ms - start_time_ms) + fade_duration_ms
        super().__init__(start_time_ms=start_time_ms, duration_ms=total_duration)
        self.end_time_ms = end_time_ms
        self.item_id = item_id
        self.position = position
        self.initial_hue = hue
        self.fade_steps = fade_steps
        self.fade_duration_ms = fade_duration_ms
        self.spawned_serial = None
        self.current_fade_step = -1
        self.fade_start_local_ms = end_time_ms - start_time_ms
        self.time_per_fade_step = fade_duration_ms / fade_steps if fade_steps > 0 else 0
    
    def on_start(self):
        """Spawn the item."""
        x, y, z = self.position
        self.spawned_serial = _send_fake_item(x, y, z, self.item_id, self.initial_hue)
    
    def on_update(self, local_time_ms):
        """Handle fading if configured."""
        if self.fade_steps == 0:
            return  # No fade, just persist until completion
        
        # Check if we're in fade period
        if local_time_ms >= self.fade_start_local_ms:
            fade_elapsed = local_time_ms - self.fade_start_local_ms
            target_fade_step = int(fade_elapsed / self.time_per_fade_step)
            
            if target_fade_step >= self.fade_steps:
                target_fade_step = self.fade_steps - 1
            
            # Update hue if fade step changed
            if target_fade_step != self.current_fade_step:
                if self.spawned_serial:
                    _remove_fake_item(self.spawned_serial)
                
                darkened_hue = darken_hue(self.initial_hue, target_fade_step + 1)
                x, y, z = self.position
                self.spawned_serial = _send_fake_item(x, y, z, self.item_id, darkened_hue)
                self.current_fade_step = target_fade_step
    
    def on_complete(self):
        """Remove the item."""
        if self.spawned_serial:
            _remove_fake_item(self.spawned_serial)

class OscillatingItemTrack(AnimationTrack):
    """
    Animates an item oscillating up and down in Z-axis with trail effect.
    Creates a "wave" effect when multiple items are staggered.
    Uses frame overlap system for smooth transitions without flicker.
    """
    
    def __init__(self, start_time_ms, end_time_ms, item_id, position, hue=0x0000, 
                 z_amplitude=10, update_interval_ms=100, z_direction=1, trail_length=2):
        """
        Args:
            start_time_ms: When to spawn and start oscillating
            end_time_ms: When to stop and clean up
            item_id: Item ID to display
            position: (x, y, z) base position
            hue: Color hue
            z_amplitude: How far to oscillate up/down
            update_interval_ms: Time between position updates
            z_direction: Initial direction (1=up, -1=down)
            trail_length: Number of trail items to keep visible (default 2 for smooth overlap)
        """
        total_duration = end_time_ms - start_time_ms
        super().__init__(start_time_ms=start_time_ms, duration_ms=total_duration)
        self.item_id = item_id
        self.base_position = position
        self.hue = hue
        self.z_amplitude = z_amplitude
        self.update_interval_ms = update_interval_ms
        self.z_direction = z_direction
        self.current_z_offset = 0
        
        # Frame overlap system - keep multiple frames visible for smooth transitions
        self.frame_trail = []  # List of (serial, spawn_time_ms) tuples
        self.trail_length = trail_length  # Number of frames to keep visible
        self.frame_overlap_ms = 100  # How long to keep old frames visible (overlap duration)
        
        self.last_update_time = 0
        self.last_overlap_cleanup_time = 0  # Track when we last cleaned up old frames
    
    def on_start(self):
        """Spawn the item at base position."""
        x, y, z = self.base_position
        serial = _send_fake_item(x, y, z, self.item_id, self.hue)
        if serial:
            self.frame_trail.append((serial, 0))  # Store with spawn time
        self.last_update_time = 0
        self.last_overlap_cleanup_time = 0
    
    def on_update(self, local_time_ms):
        """Update Z position to create oscillation with trail effect."""
        needs_update = False
        
        # Check if it's time to update position (skip if amplitude is 0 - static item)
        if self.z_amplitude > 0 and local_time_ms - self.last_update_time >= self.update_interval_ms:
            # Update Z offset
            self.current_z_offset += self.z_direction
            
            # Reverse direction at amplitude limits
            if self.current_z_offset >= self.z_amplitude:
                self.z_direction = -1
                self.current_z_offset = self.z_amplitude
            elif self.current_z_offset <= -self.z_amplitude:
                self.z_direction = 1
                self.current_z_offset = -self.z_amplitude
            
            needs_update = True
            self.last_update_time = local_time_ms
        
        # Spawn new frame if position changed
        if needs_update:
            x, y, base_z = self.base_position
            new_z = base_z + self.current_z_offset
            serial = _send_fake_item(x, y, new_z, self.item_id, self.hue)
            
            if serial:
                # Add new frame to trail with current time
                self.frame_trail.append((serial, local_time_ms))
                
                # Maintain fixed trail length - remove oldest frames when exceeding trail_length
                while len(self.frame_trail) > self.trail_length:
                    old_serial, old_time = self.frame_trail.pop(0)  # Remove oldest
                    _remove_fake_item(old_serial)
    
    def on_complete(self):
        """Remove all trail frames."""
        for serial, spawn_time in self.frame_trail:
            _remove_fake_item(serial)
        self.frame_trail.clear()

class VFXPlaybackTrack(AnimationTrack):
    """Plays through VFX frames in sequence with overlap for smooth transitions."""
    
    def __init__(self, start_time_ms, vfx_frames, frame_duration_ms, position, hue=0x0000, loop=False, loop_count=None):
        # Validate frames list is not empty
        if not vfx_frames or len(vfx_frames) == 0:
            raise ValueError("vfx_frames cannot be empty - must have at least one frame")
        
        # Calculate duration based on frames and loops
        single_loop_duration = len(vfx_frames) * frame_duration_ms
        if loop and loop_count is not None:
            # For looping VFX, multiply by loop count
            total_duration = single_loop_duration * loop_count
        else:
            total_duration = single_loop_duration
        
        super().__init__(start_time_ms=start_time_ms, duration_ms=total_duration, loop=loop, loop_count=loop_count)
        self.vfx_frames = vfx_frames
        self.frame_duration_ms = frame_duration_ms
        self.position = position
        self.hue = hue
        self.single_loop_duration = single_loop_duration
        self.is_single_frame = (len(vfx_frames) == 1)
        
        # Frame overlap system
        self.frame_trail = []  # List of (serial, spawn_time_ms) tuples
        self.frame_overlap_ms = 100  # Overlap duration
        self.current_frame_index = -1
        self.last_overlap_cleanup_time = 0
    
    def on_start(self):
        """Spawn initial frame (works for both single and multi-frame VFX)."""
        if not self.vfx_frames:
            return
        
        x, y, z = self.position
        frame_item_id = self.vfx_frames[0]  # Always start with first frame
        initial_serial = _send_fake_item(x, y, z, frame_item_id, self.hue)
        
        if initial_serial:
            self.frame_trail.append((initial_serial, 0))
            self.current_frame_index = 0
    
    def on_update(self, local_time_ms):
        if not self.vfx_frames:
            return
        
        # For single-frame VFX with looping, keep the frame visible throughout all loops
        # No need to respawn or update - just let it persist until on_complete()
        if self.is_single_frame:
            # Single frame stays visible, no updates needed
            return
        
        # Multi-frame VFX: cycle through frames
        if len(self.vfx_frames) > 1:
            target_frame_index = int(local_time_ms / self.frame_duration_ms)
            if target_frame_index >= len(self.vfx_frames):
                target_frame_index = len(self.vfx_frames) - 1
            
            if target_frame_index != self.current_frame_index:
                x, y, z = self.position
                frame_item_id = self.vfx_frames[target_frame_index]
                new_serial = _send_fake_item(x, y, z, frame_item_id, self.hue)
                
                if new_serial:
                    self.frame_trail.append((new_serial, local_time_ms))
                
                self.current_frame_index = target_frame_index
        
        # ALWAYS check for overlap cleanup (independent of frame changes)
        if len(self.frame_trail) > 1 and local_time_ms - self.last_overlap_cleanup_time >= 10:
            self.last_overlap_cleanup_time = local_time_ms
            
            # Remove old frames that have exceeded overlap time
            frames_to_remove = []
            for i, (serial, spawn_time) in enumerate(self.frame_trail[:-1]):  # Don't check newest frame
                age_ms = local_time_ms - spawn_time
                if age_ms > self.frame_overlap_ms:
                    frames_to_remove.append(i)
                    _remove_fake_item(serial)
            
            # Remove from trail list (in reverse to maintain indices)
            for i in reversed(frames_to_remove):
                self.frame_trail.pop(i)
    
    def on_complete(self):
        """Remove all trail frames."""
        for serial, spawn_time in self.frame_trail:
            _remove_fake_item(serial)
        self.frame_trail.clear()

class DriftingCloudTrack(AnimationTrack):
    """
    Animates a cloud VFX that floats/bobs vertically on the Z-axis.
    The cloud cycles through animation frames and randomly moves up/down.
    """
    
    def __init__(self, start_time_ms, end_time_ms, vfx_frames, frame_duration_ms, 
                 start_position, hue, drift_speed_ms=200, z_amplitude=3):
        """
        Args:
            start_time_ms: When to start the cloud
            end_time_ms: When to end the cloud
            vfx_frames: List of item IDs for cloud animation frames
            frame_duration_ms: Time per frame
            start_position: (x, y, z) starting position
            hue: Cloud hue
            drift_speed_ms: Time between Z position updates
            z_amplitude: Random Z offset range (+/- this value)
        """
        total_duration = end_time_ms - start_time_ms
        super().__init__(start_time_ms=start_time_ms, duration_ms=total_duration)
        self.vfx_frames = vfx_frames
        self.frame_duration_ms = frame_duration_ms
        self.start_position = start_position
        self.current_position = list(start_position)  # Mutable copy
        self.hue = hue
        self.drift_speed_ms = drift_speed_ms
        self.z_amplitude = z_amplitude
        self.z_direction = random.choice([-1, 1])  # Random initial direction
        
        # Frame overlap system - keep multiple frames visible for smooth transitions
        self.frame_trail = []  # List of (serial, spawn_time_ms) tuples
        self.trail_length = 2  # Max frames to keep visible
        self.frame_overlap_ms = 100  # How long to keep old frame visible (overlap duration)
        
        self.current_serial = None
        self.current_frame_index = 0
        self.last_frame_update_time = 0
        self.last_drift_update_time = 0
        self.last_overlap_cleanup_time = 0  # Track when we last cleaned up old frames
    
    def on_start(self):
        """Spawn initial cloud frame."""
        x, y, z = self.current_position
        frame_item_id = self.vfx_frames[self.current_frame_index]
        self.current_serial = _send_fake_item(x, y, z, frame_item_id, self.hue)
        if self.current_serial:
            self.frame_trail.append((self.current_serial, 0))
        self.last_frame_update_time = 0
        self.last_drift_update_time = 0
        self.last_overlap_cleanup_time = 0
    
    def on_update(self, local_time_ms):
        """Update cloud animation frame and position with overlap."""
        needs_update = False
        
        # Check if frame needs update (skip if only 1 frame - static VFX)
        if len(self.vfx_frames) > 1 and local_time_ms - self.last_frame_update_time >= self.frame_duration_ms:
            self.current_frame_index = (self.current_frame_index + 1) % len(self.vfx_frames)
            self.last_frame_update_time = local_time_ms
            needs_update = True
        
        # Check if Z position needs update (skip if amplitude is 0)
        if self.z_amplitude > 0 and local_time_ms - self.last_drift_update_time >= self.drift_speed_ms:
            # Update Z position randomly within amplitude range
            if random.random() < 0.3:  # 30% chance to change direction
                self.z_direction *= -1
            
            # Move Z position
            self.current_position[2] += self.z_direction
            
            # Clamp Z within amplitude range from start position
            base_z = self.start_position[2]
            if self.current_position[2] > base_z + self.z_amplitude:
                self.current_position[2] = base_z + self.z_amplitude
                self.z_direction = -1
            elif self.current_position[2] < base_z - self.z_amplitude:
                self.current_position[2] = base_z - self.z_amplitude
                self.z_direction = 1
            
            self.last_drift_update_time = local_time_ms
            needs_update = True
        
        # Only do ONE packet operation per update
        if needs_update:
            # Spawn new frame
            x, y, z = self.current_position
            frame_item_id = self.vfx_frames[self.current_frame_index]
            new_serial = _send_fake_item(x, y, z, frame_item_id, self.hue)
            
            if new_serial:
                # Add new frame to trail with current time
                self.frame_trail.append((new_serial, local_time_ms))
                self.current_serial = new_serial
        
        # ALWAYS check for overlap cleanup (independent of frame/drift updates)
        # This ensures old frames are removed even if no other updates are happening
        if len(self.frame_trail) > 1 and local_time_ms - self.last_overlap_cleanup_time >= 10:
            self.last_overlap_cleanup_time = local_time_ms
            
            # Remove old frames that have exceeded overlap time
            # Keep frames visible for frame_overlap_ms to prevent flicker
            frames_to_remove = []
            for i, (serial, spawn_time) in enumerate(self.frame_trail[:-1]):  # Don't check newest frame
                age_ms = local_time_ms - spawn_time
                # Only remove if older than overlap time
                if age_ms > self.frame_overlap_ms:
                    frames_to_remove.append(i)
                    _remove_fake_item(serial)
            
            # Remove from trail list (in reverse to maintain indices)
            for i in reversed(frames_to_remove):
                self.frame_trail.pop(i)
    
    def on_complete(self):
        """Remove cloud and all trail frames."""
        for serial, spawn_time in self.frame_trail:
            _remove_fake_item(serial)
        self.frame_trail.clear()


class AnimationTimeline:
    """Manages multiple animation tracks with scheduling and update queue."""
    
    def __init__(self, tick_rate_ms=60, max_updates_per_frame=8):
        self.tick_rate_ms = tick_rate_ms
        self.max_updates_per_frame = max_updates_per_frame
        self.tracks = []
        self.timeline_start_time_ms = 0
        self.is_playing = False
        self.operation_queue = []  # List of (queue_time_ms, operation_type, track, cost) tuples
    
    def add_track(self, track):
        self.tracks.append(track)
    
    def get_next_update_time_ms(self, current_timeline_time_ms):
        next_update_ms = self.tick_rate_ms
        for track in self.tracks:
            if track.is_complete:
                continue
            if not track.is_active:
                time_until_start = track.start_time_ms - current_timeline_time_ms
                if time_until_start > 0:
                    next_update_ms = min(next_update_ms, time_until_start)
                continue
            if isinstance(track, VFXPlaybackTrack):
                local_time = track.get_local_time_ms(current_timeline_time_ms)
                time_to_next_frame = track.frame_duration_ms - (local_time % track.frame_duration_ms)
                next_update_ms = min(next_update_ms, time_to_next_frame)
            elif isinstance(track, OscillatingItemTrack):
                # Schedule updates for oscillation
                local_time = track.get_local_time_ms(current_timeline_time_ms)
                time_since_last = local_time - track.last_update_time
                time_to_next_update = track.update_interval_ms - time_since_last
                if time_to_next_update > 0:
                    next_update_ms = min(next_update_ms, time_to_next_update)
                else:
                    next_update_ms = min(next_update_ms, track.update_interval_ms)
            elif isinstance(track, StaticItemTrack):
                # Only schedule updates during fade period
                if track.fade_steps > 0:
                    local_time = track.get_local_time_ms(current_timeline_time_ms)
                    if local_time >= track.fade_start_local_ms:
                        fade_elapsed = local_time - track.fade_start_local_ms
                        time_to_next_step = track.time_per_fade_step - (fade_elapsed % track.time_per_fade_step)
                        next_update_ms = min(next_update_ms, time_to_next_step)
        return max(self.tick_rate_ms, next_update_ms)
    
    def play(self):
        if not self.tracks:
            return
        self.is_playing = True
        self.timeline_start_time_ms = int(time.time() * 1000)
        
        debug_message(f"Timeline: Starting with {len(self.tracks)} tracks, tick={self.tick_rate_ms}ms, max_updates={self.max_updates_per_frame}", 88)
        
        while self.is_playing:
            current_time_ms = int(time.time() * 1000) - self.timeline_start_time_ms
            
            # PHASE 1: Add NEW operations to queue with CURRENT time as queue time
            # This is critical - each update gets queued at the current frame time
            for track in self.tracks:
                # Check if track needs to start
                if track.should_start(current_time_ms):
                    cost = 1
                    # Check if already queued
                    already_queued = any(op[2] == track and op[1] == 'start' for op in self.operation_queue)
                    if not already_queued:
                        # Queue with CURRENT time - when this operation was requested
                        self.operation_queue.append((current_time_ms, 'start', track, cost))
                
                # Check if track needs update
                elif track.is_active and not track.is_complete:
                    if isinstance(track, (OscillatingItemTrack, DriftingCloudTrack)):
                        cost = 2
                    else:
                        cost = 1
                    
                    # Check if this track already has a queued update
                    already_queued = any(op[2] == track and op[1] == 'update' for op in self.operation_queue)
                    if not already_queued:
                        # Queue with CURRENT time - when this update was requested
                        # This ensures round-robin: all tracks requesting updates at t=120ms
                        # get equal priority, regardless of when they started
                        self.operation_queue.append((current_time_ms, 'update', track, cost))
            
            # PHASE 2: Sort queue by time (oldest queued first) + round-robin within same time
            # Operations queued earlier execute first
            # Within same queue_time, use track index for round-robin distribution
            self.operation_queue.sort(key=lambda x: (x[0], self.tracks.index(x[2]) if x[2] in self.tracks else 0))
            
            # PHASE 3: Execute operations up to limit
            operations_executed = 0
            remaining_queue = []
            
            for queue_time, operation_type, track, cost in self.operation_queue:
                # Skip if track is already complete
                if track.is_complete:
                    continue
                
                # Try to execute if we have budget
                if operations_executed + cost <= self.max_updates_per_frame:
                    if operation_type == 'start':
                        if track.should_start(current_time_ms):
                            track.start(current_time_ms)
                            operations_executed += cost
                        # Don't re-queue starts
                    elif operation_type == 'update':
                        if track.is_active and not track.is_complete:
                            track.update(current_time_ms)
                            operations_executed += cost
                        # Don't re-queue updates (will be added fresh next frame)
                else:
                    # Keep in queue for next frame (maintains wait time priority)
                    remaining_queue.append((queue_time, operation_type, track, cost))
            
            # Keep deferred operations for next frame
            self.operation_queue = remaining_queue
            
            if all(track.is_complete for track in self.tracks):
                break
            
            next_update_ms = self.get_next_update_time_ms(current_time_ms)
            # Enforce minimum delay to prevent client overload
            next_update_ms = max(self.tick_rate_ms, next_update_ms)
            Misc.Pause(int(next_update_ms))
        
        self.is_playing = False
        debug_message("Timeline: Complete", 88)

# =============================================================================
# VFX ANIMATION FUNCTIONS
# =============================================================================

def display_item_at_location(item_id, x, y, z, hue=0x0000):
    """Display a single item at specific coordinates."""
    return _send_fake_item(x, y, z, item_id, hue)

# =============================================================================
# MAIN RITUAL SEQUENCE
# =============================================================================

def perform_shadow_circle_ritual():
    """
    Timeline-based Shadow Mastery ascension ritual:
    - Alchemical symbols spawn at each orb position (dark shadow hue)
    - Inner ring: Chaga mushrooms around each orb (dark hue)
    - Middle ring: Shadow oil pools around each orb (dark hue)
    - Outer ring: Footprints around each orb (dark hue)
    - Shadow orbs (dark blue 0x081A) float above with oscillation trail
    - Center inward energy loops 3 times
    - Cascading nature tendrils VFX around circle
    - Late-stage wispy energy at center
    - Shockwave finale with dark blue hue
    - All decorations fade out at the end
    """
    try:
        # Get player position as center
        center_x = int(Player.Position.X)
        center_y = int(Player.Position.Y)
        center_z = int(Player.Position.Z)
        
        # Load config
        cfg = RITUAL_CONFIG
        circle_cfg = cfg["circle"]
        color_cfg = cfg["color"]
        symbol_cfg = cfg["phase_symbols"]
        orb_cfg = cfg["phase_orbs"]
        deco_cfg = cfg["phase_decorations"]
        clouds_cfg = cfg["phase_drifting_clouds"]
        center_cfg = cfg["phase_center_energy"]
        symbol_vfx_cfg = cfg["phase_symbol_vfx"]
        center_late_cfg = cfg["phase_center_energy_late"]
        finale_cfg = cfg["phase_finale"]
        fade_cfg = cfg["phase_fade"]
        
        # Dynamic trail length based on mastery level (element_count)
        # More orbs = shorter trails to prevent client overload
        element_count = circle_cfg["element_count"]
        if element_count <= 8:
            orb_cfg["trail_length"] = 2  # Full trail for 8 or fewer
        elif element_count <= 11:
            orb_cfg["trail_length"] = 1  # Medium trail for 9-11
        else:
            orb_cfg["trail_length"] = 1  # Minimal trail for 12+
        
        debug_message("=" * 60, 88)
        debug_message("Shadow Mastery - Level Up Ritual", 88)
        debug_message(f"Center: ({center_x}, {center_y}, {center_z})", 68)
        debug_message(f"Elements: {circle_cfg['element_count']}, Radius: {circle_cfg['radius']}", 68)
        debug_message(f"Mastery Level {element_count}: Trail length set to {orb_cfg['trail_length']}", 68)
        debug_message(f"Color: {color_cfg['scheme']}, Shadow Hue: {hex(color_cfg['shadow_orb_hue'])}", 68)
        debug_message("=" * 60, 88)
        
        # Generate circle points
        circle_points = generate_circle_points(
            center_x, center_y, circle_cfg["radius"], 
            circle_cfg["element_count"], circle_cfg["rotation_degrees"]
        )
        
        # Create timeline with rate limiting
        timeline = AnimationTimeline(
            tick_rate_ms=cfg["timeline"]["minimum_tick_rate_ms"],
            max_updates_per_frame=cfg["timeline"]["max_updates_per_frame"]
        )
        
        # =====================================================================
        # BUILD TIMELINE: Add all animation tracks
        # =====================================================================
        
        # Calculate timing for fade/removal
        symbol_vfx_effect = VFX_EFFECTS[symbol_vfx_cfg["vfx_effect"]]
        symbol_vfx_duration = len(symbol_vfx_effect["frames"]) * symbol_vfx_effect["frame_duration"]
        symbol_vfx_start_base = center_cfg["start_delay_ms"] + symbol_vfx_cfg["start_offset_ms"]
        last_symbol_vfx_start = symbol_vfx_start_base + ((circle_cfg["element_count"] - 1) * symbol_vfx_cfg["stagger_delay_ms"])
        symbol_vfx_end = last_symbol_vfx_start + symbol_vfx_duration
        
        # Shockwave timing
        shockwave_effect = VFX_EFFECTS[finale_cfg["vfx_effect"]]
        shockwave_start = symbol_vfx_end + finale_cfg["delay_after_symbol_vfx_ms"]
        
        # Fade timing - stagger the vanishing sequence
        fade_duration = fade_cfg["fade_steps"] * fade_cfg["fade_step_delay_ms"]
        base_fade_start = shockwave_start + fade_cfg["delay_after_finale_ms"]
        
        # Decorations vanish first (instant removal at base_fade_start)
        decorations_end = base_fade_start
        
        # Orbs vanish 500ms after decorations (instant removal)
        orbs_end = base_fade_start + 500
        
        # Symbols persist fully visible until 500ms after orbs vanish, THEN start fading
        symbols_fade_start = base_fade_start + 1000  # 1000ms = decorations gone + 500ms wait + orbs gone + 500ms wait
        
        # Track 1-N: Alchemical symbols at each orb position (fade last)
        shadow_symbol_hue = color_cfg["shadow_hue"] if symbol_cfg.get("use_shadow_hue") else 0x0000
        for i, (orb_x, orb_y) in enumerate(circle_points):
            symbol_id = ALCHEMICAL_SYMBOLS[i % len(ALCHEMICAL_SYMBOLS)]
            # Use shadow hue if configured, otherwise use element hue
            if symbol_cfg.get("use_shadow_hue"):
                hue = shadow_symbol_hue
            else:
                hue = get_hue_for_element(i, circle_cfg["element_count"])
            z = center_z + symbol_cfg["z_offset"]
            
            timeline.add_track(StaticItemTrack(
                start_time_ms=i * symbol_cfg["spawn_delay_ms"],
                end_time_ms=symbols_fade_start,  # Symbols persist longest
                item_id=symbol_id,
                position=(orb_x, orb_y, z),
                hue=hue,
                fade_steps=fade_cfg["fade_steps"],
                fade_duration_ms=fade_duration
            ))
        
        # Track: Drifting Shadow Clouds (if enabled)
        if clouds_cfg.get("enabled", False):
            cloud_count = clouds_cfg["cloud_count"]
            spawn_radius = clouds_cfg["spawn_area_radius"]
            min_distance = clouds_cfg["min_distance"]
            cloud_z = center_z + clouds_cfg["z_offset"]
            
            # Generate random cloud positions (no overlap)
            cloud_positions = []
            max_attempts = 100
            
            for _ in range(cloud_count):
                for attempt in range(max_attempts):
                    # Random position within spawn radius
                    angle = random.uniform(0, 2 * math.pi)
                    distance = random.uniform(0, spawn_radius)
                    cloud_x = int(center_x + distance * math.cos(angle))
                    cloud_y = int(center_y + distance * math.sin(angle))
                    
                    # Check distance from other clouds
                    valid = True
                    for existing_x, existing_y in cloud_positions:
                        dist = math.sqrt((cloud_x - existing_x)**2 + (cloud_y - existing_y)**2)
                        if dist < min_distance:
                            valid = False
                            break
                    
                    if valid:
                        cloud_positions.append((cloud_x, cloud_y))
                        break
            
            # Spawn drifting clouds
            for i, (cloud_x, cloud_y) in enumerate(cloud_positions):
                timeline.add_track(DriftingCloudTrack(
                    start_time_ms=clouds_cfg["start_delay_ms"],
                    end_time_ms=decorations_end,  # Clouds last until decorations fade
                    vfx_frames=clouds_cfg["vfx_frames"],
                    frame_duration_ms=clouds_cfg["frame_duration_ms"],
                    start_position=(cloud_x, cloud_y, cloud_z),
                    hue=clouds_cfg["hue"],
                    drift_speed_ms=clouds_cfg["drift_speed_ms"],
                    z_amplitude=clouds_cfg["z_amplitude"]
                ))
            
            debug_message(f"Added {len(cloud_positions)} drifting shadow clouds", 68)
        
        # Track N+1 to 2N: Shadow Orbs floating above symbols
        orb_start_offset = orb_cfg["start_offset_ms"]
        shadow_hue = color_cfg["shadow_orb_hue"] if orb_cfg.get("use_shadow_hue") else 0x0000
        
        if orb_cfg.get("oscillate", False):
            # Use oscillating track for wave effect
            for i, (orb_x, orb_y) in enumerate(circle_points):
                z = center_z + orb_cfg["z_offset"]
                
                timeline.add_track(OscillatingItemTrack(
                    start_time_ms=orb_start_offset + (i * orb_cfg["spawn_delay_ms"]),
                    end_time_ms=orbs_end,  # Orbs vanish before symbols fade
                    item_id=orb_cfg["item_id"],
                    position=(orb_x, orb_y, z),
                    hue=shadow_hue,
                    z_amplitude=orb_cfg.get("z_amplitude", 10),
                    update_interval_ms=orb_cfg.get("oscillate_speed_ms", 100),
                    z_direction=1,  # All start going up
                    trail_length=orb_cfg.get("trail_length", 3)  # Trail effect for smooth visuals
                ))
        else:
            # Use static track (no oscillation)
            for i, (orb_x, orb_y) in enumerate(circle_points):
                z = center_z + orb_cfg["z_offset"]
                
                timeline.add_track(StaticItemTrack(
                    start_time_ms=orb_start_offset + (i * orb_cfg["spawn_delay_ms"]),
                    end_time_ms=orbs_end,  # Orbs vanish before symbols fade
                    item_id=orb_cfg["item_id"],
                    position=(orb_x, orb_y, z),
                    hue=shadow_hue,
                    fade_steps=0,
                    fade_duration_ms=0
                ))
        
        # Track 2N+1 onwards: Decoration circles around each orb
        deco_start_base = deco_cfg["start_offset_ms"]
        inner_ring_cfg = deco_cfg["inner_ring"]
        middle_ring_cfg = deco_cfg["middle_ring"]
        outer_ring_cfg = deco_cfg.get("outer_ring", None)
        
        current_time = deco_start_base
        for orb_index, (orb_x, orb_y) in enumerate(circle_points):
            orb_hue = get_hue_for_element(orb_index, circle_cfg["element_count"])
            
            # Inner decoration ring around this orb (Daemon Blood)
            inner_deco_points = generate_circle_points(
                orb_x, orb_y, inner_ring_cfg["radius"],
                inner_ring_cfg["points"], 0
            )
            for point_index, (x, y) in enumerate(inner_deco_points):
                z = center_z + inner_ring_cfg["z_offset"]
                
                # Get item_id - handle string keys (lookup in SHADOW_ITEMS) or direct item_id
                item_id_config = inner_ring_cfg["item_id"]
                if isinstance(item_id_config, str):
                    # Lookup in SHADOW_ITEMS dictionary
                    item_id = SHADOW_ITEMS.get(item_id_config, 0x0F7D)
                else:
                    item_id = item_id_config
                
                # Use random hue from scheme or custom hue based on config
                if inner_ring_cfg.get("use_scheme_hue", True):
                    # Randomly select from base_hues array
                    scheme = color_cfg["scheme"]
                    hue_family = HUE_FAMILIES.get(scheme, HUE_FAMILIES["blue"])
                    inner_hue = random.choice(hue_family["base_hues"])
                else:
                    inner_hue = inner_ring_cfg.get("hue", 0x0000)
                timeline.add_track(StaticItemTrack(
                    start_time_ms=current_time + (point_index * deco_cfg["spawn_delay_per_item_ms"]),
                    end_time_ms=decorations_end,  # Decorations vanish before orbs
                    item_id=item_id,
                    position=(x, y, z),
                    hue=inner_hue,
                    fade_steps=0,  # Instant removal, no fade
                    fade_duration_ms=0
                ))
            
            # Middle decoration ring around this orb (Organs + Intestines)
            middle_deco_points = generate_circle_points(
                orb_x, orb_y, middle_ring_cfg["radius"],
                middle_ring_cfg["points"], 0
            )
            for point_index, (x, y) in enumerate(middle_deco_points):
                z = center_z + middle_ring_cfg["z_offset"]
                # Get item list - handle string keys (lookup in SHADOW_ITEMS) or direct lists
                item_ids_config = middle_ring_cfg["item_ids"]
                if isinstance(item_ids_config, str):
                    # Special case for SHADOW_OIL_POOLS
                    if item_ids_config == "BLOOD_SPLATTERS":
                        item_list = SHADOW_OIL_POOLS
                    else:
                        # Lookup in SHADOW_ITEMS dictionary
                        lookup_result = SHADOW_ITEMS.get(item_ids_config, [])
                        # Handle single int or list
                        if isinstance(lookup_result, int):
                            item_list = [lookup_result]
                        else:
                            item_list = lookup_result
                elif isinstance(item_ids_config, int):
                    # Single item ID
                    item_list = [item_ids_config]
                else:
                    item_list = item_ids_config
                
                # Random selection from list
                if item_list:
                    item_id = random.choice(item_list) if middle_ring_cfg.get("random_selection") else item_list[0]
                else:
                    item_id = 0x1CED  # Fallback
                # Use random hue from scheme or custom hue based on config
                if middle_ring_cfg.get("use_scheme_hue", True):
                    # Randomly select from base_hues array
                    scheme = color_cfg["scheme"]
                    hue_family = HUE_FAMILIES.get(scheme, HUE_FAMILIES["blue"])
                    middle_hue = random.choice(hue_family["base_hues"])
                else:
                    middle_hue = middle_ring_cfg.get("hue", 0x0000)
                timeline.add_track(StaticItemTrack(
                    start_time_ms=current_time + (point_index * deco_cfg["spawn_delay_per_item_ms"]),
                    end_time_ms=decorations_end,  # Decorations vanish before orbs
                    item_id=item_id,
                    position=(x, y, z),
                    hue=middle_hue,
                    fade_steps=0,  # Instant removal, no fade
                    fade_duration_ms=0
                ))
            
            # Outer decoration ring around this orb (Blood Splatters)
            if outer_ring_cfg:
                outer_deco_points = generate_circle_points(
                    orb_x, orb_y, outer_ring_cfg["radius"],
                    outer_ring_cfg["points"], 0
                )
                for point_index, (x, y) in enumerate(outer_deco_points):
                    z = center_z + outer_ring_cfg["z_offset"]
                    # Get item list - handle string keys (lookup in SHADOW_ITEMS) or use SHADOW_OIL_POOLS
                    item_ids_config = outer_ring_cfg.get("item_ids", "BLOOD_SPLATTERS")
                    if isinstance(item_ids_config, str):
                        if item_ids_config == "BLOOD_SPLATTERS":
                            item_list = SHADOW_OIL_POOLS
                        else:
                            # Lookup in SHADOW_ITEMS dictionary
                            lookup_result = SHADOW_ITEMS.get(item_ids_config, SHADOW_OIL_POOLS)
                            # Handle single int or list
                            if isinstance(lookup_result, int):
                                item_list = [lookup_result]
                            else:
                                item_list = lookup_result
                    elif isinstance(item_ids_config, int):
                        # Single item ID
                        item_list = [item_ids_config]
                    else:
                        item_list = item_ids_config
                    
                    # Random selection from list
                    if outer_ring_cfg.get("random_selection") and item_list:
                        item_id = random.choice(item_list)
                    else:
                        item_id = item_list[0] if item_list else 0x122A
                    # Use random hue from scheme or custom hue based on config
                    if outer_ring_cfg.get("use_scheme_hue", True):
                        # Randomly select from base_hues array
                        scheme = color_cfg["scheme"]
                        hue_family = HUE_FAMILIES.get(scheme, HUE_FAMILIES["blue"])
                        outer_hue = random.choice(hue_family["base_hues"])
                    else:
                        outer_hue = outer_ring_cfg.get("hue", 0x0000)
                    timeline.add_track(StaticItemTrack(
                        start_time_ms=current_time + (point_index * deco_cfg["spawn_delay_per_item_ms"]),
                        end_time_ms=decorations_end,  # Decorations vanish before orbs
                        item_id=item_id,
                        position=(x, y, z),
                        hue=outer_hue,
                        fade_steps=0,  # Instant removal, no fade
                        fade_duration_ms=0
                    ))
            
            # Move to next orb's decoration timing
            current_time += deco_cfg["spawn_delay_per_orb_ms"]
        
        # Track: Looping inward energy at center (with camera offset)
        center_effect = VFX_EFFECTS[center_cfg["vfx_effect"]]
        center_z_energy = center_z + center_cfg["z_offset"]
        center_hue = center_cfg["hue"] if center_cfg["hue"] != 0x0000 else get_scheme_hue("middle")
        
        # Apply camera offset to position effect "in front" of player in isometric view
        if center_cfg.get("camera_offset", False):
            center_vfx_x = center_x + center_cfg.get("offset_x", 0)
            center_vfx_y = center_y + center_cfg.get("offset_y", 0)
        else:
            center_vfx_x = center_x
            center_vfx_y = center_y
        
        timeline.add_track(VFXPlaybackTrack(
            start_time_ms=center_cfg["start_delay_ms"],
            vfx_frames=center_effect["frames"],
            frame_duration_ms=center_effect["frame_duration"],
            position=(center_vfx_x, center_vfx_y, center_z_energy),
            hue=center_hue,
            loop=True,
            loop_count=center_cfg["loop_count"]
        ))
        
        # Tracks: Overlapping VFX at each symbol location
        for i, (x, y) in enumerate(circle_points):
            # Use designated hue from config, or fall back to shadow hue
            if "hue" in symbol_vfx_cfg:
                hue = symbol_vfx_cfg["hue"]
            elif symbol_vfx_cfg.get("use_shadow_hue"):
                hue = color_cfg.get("shadow_hue", 1)
            else:
                hue = 0x0000  # No hue
            z = center_z + symbol_vfx_cfg["z_offset"]
            
            timeline.add_track(VFXPlaybackTrack(
                start_time_ms=symbol_vfx_start_base + (i * symbol_vfx_cfg["stagger_delay_ms"]),
                vfx_frames=symbol_vfx_effect["frames"],
                frame_duration_ms=symbol_vfx_effect["frame_duration"],
                position=(x, y, z),
                hue=hue,
                loop=True,
                loop_count=symbol_vfx_cfg["loop_count"]
            ))
        
        # Track: Late-stage wispy energy at center (with camera offset)
        center_late_effect = VFX_EFFECTS[center_late_cfg["vfx_effect"]]
        center_late_start = symbol_vfx_end + center_late_cfg["delay_after_symbol_vfx_ms"]
        center_late_z = center_z + center_late_cfg["z_offset"]
        center_late_hue = center_late_cfg["hue"] if center_late_cfg["hue"] != 0x0000 else get_scheme_hue("middle")
        
        # Apply camera offset to position effect "in front" of player
        if center_late_cfg.get("camera_offset", False):
            center_late_x = center_x + center_late_cfg.get("offset_x", 0)
            center_late_y = center_y + center_late_cfg.get("offset_y", 0)
        else:
            center_late_x = center_x
            center_late_y = center_y
        
        timeline.add_track(VFXPlaybackTrack(
            start_time_ms=center_late_start,
            vfx_frames=center_late_effect["frames"],
            frame_duration_ms=center_late_effect["frame_duration"],
            position=(center_late_x, center_late_y, center_late_z),
            hue=center_late_hue,
            loop=True,
            loop_count=center_late_cfg["loop_count"]
        ))
        
        # Track: Shockwave finale at center (with camera offset)
        if finale_cfg.get("use_shockwave_hue"):
            finale_hue = color_cfg["shockwave_hue"]
        elif finale_cfg.get("use_scheme_hue"):
            finale_hue = get_scheme_hue("brightest")
        else:
            finale_hue = 0x0000
        
        # Apply camera offset to position effect "in front" of player
        if finale_cfg.get("camera_offset", False):
            finale_x = center_x + finale_cfg.get("offset_x", 0)
            finale_y = center_y + finale_cfg.get("offset_y", 0)
        else:
            finale_x = center_x
            finale_y = center_y
        
        timeline.add_track(VFXPlaybackTrack(
            start_time_ms=shockwave_start,
            vfx_frames=shockwave_effect["frames"],
            frame_duration_ms=shockwave_effect["frame_duration"],
            position=(finale_x, finale_y, center_z + finale_cfg["z_offset"]),
            hue=finale_hue,
            loop=True,
            loop_count=finale_cfg["loop_count"]
        ))
        
        # =====================================================================
        # EXECUTE TIMELINE
        # =====================================================================
        
        debug_message(f"Timeline: {len(timeline.tracks)} tracks scheduled", 68)
        timeline.play()
        
        debug_message("=" * 60, 88)
        debug_message("Blood Mastery Ascension Orb Circle Ritual - Complete", 88)
        debug_message("=" * 60, 88)
        
    except Exception as e:
        debug_message(f"Error in ritual: {e}", 33)
        import traceback
        debug_message(traceback.format_exc(), 33)

# =============================================================================
# GUMP LAUNCHER UI
# =============================================================================

def add_centered_label_with_outline(gd, x, y, w, h, text, hue):
    """Draw a centered label with black outline for readability."""
    try:
        approx_char_px = 6
        text_x = x + (w // 2) - max(0, len(text)) * approx_char_px // 2
        text_y = y + (h // 2) - 7
        outline_color = 0  # black
        offsets_r1 = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
        offsets_r2 = [(-2, 0), (2, 0), (0, -2), (0, 2), (-2, -1), (-2, 1), (2, -1), (2, 1), (-1, -2), (1, -2), (-1, 2), (1, 2)]
        for dx, dy in offsets_r2:
            Gumps.AddLabel(gd, text_x + dx, text_y + dy, outline_color, text)
        for dx, dy in offsets_r1:
            Gumps.AddLabel(gd, text_x + dx, text_y + dy, outline_color, text)
        Gumps.AddLabel(gd, text_x, text_y, hue, text)
    except Exception:
        pass

def render_shadow_ascension_gump():
    """Render the Shadow Ascension launcher gump."""
    global CURRENT_MASTERY_LEVEL
    
    gd = Gumps.CreateGump(movable=True)
    Gumps.AddPage(gd, 0)
    
    # Background
    Gumps.AddBackground(gd, 0, 0, GUMP_WIDTH, GUMP_HEIGHT, 30546)
    Gumps.AddAlphaRegion(gd, 0, 0, GUMP_WIDTH, GUMP_HEIGHT)
    
    # Header - dark desaturated blue
    try:
        Gumps.AddHtml(gd, 2, 0, GUMP_WIDTH - 4, 18,
                      "<center><basefont color=#4A4A6B>Shadow Mastery Ascension</basefont></center>", 0, 0)
    except Exception:
        pass
    
    # Display orb item with hue from config
    orb_item_id = RITUAL_CONFIG["phase_orbs"]["item_id"]
    orb_hue = RITUAL_CONFIG["color"]["shadow_orb_hue"]
    
    orb_x = GUMP_WIDTH // 2 - 20
    orb_y = 25
    
    try:
        Gumps.AddItem(gd, orb_x, orb_y, orb_item_id, orb_hue)
    except Exception:
        pass
    
    # Ascend button (large black button with red letters) - moved up 20px
    button_y = 70
    button_x = (GUMP_WIDTH - BUTTON_LARGE_WIDTH) // 2
    
    try:
        # Large button background
        Gumps.AddButton(gd, button_x, button_y, BUTTON_LARGE_ART, BUTTON_LARGE_ART, BUTTON_ASCEND, 1, 0)
        # Black sliver overlay to darken button
        Gumps.AddImageTiled(gd, button_x, button_y, BUTTON_LARGE_WIDTH, BUTTON_LARGE_HEIGHT, SLIVER_OVERLAY_TILE)
        # Dark blue "ASCEND" text - shifted left 5 pixels
        add_centered_label_with_outline(gd, button_x - 5, button_y, BUTTON_LARGE_WIDTH, BUTTON_LARGE_HEIGHT, "ASCEND", 0x0001)
    except Exception:
        pass
    
    # Level selection buttons (1-12 in 3 rows of 4) - no label, tighter spacing
    level_buttons_start_y = button_y + BUTTON_LARGE_HEIGHT + 10
    button_gap = 3
    buttons_per_row = 4
    
    # Calculate starting X to center the buttons
    total_width = (BUTTON_SMALL_WIDTH * buttons_per_row) + (button_gap * (buttons_per_row - 1))
    start_x = (GUMP_WIDTH - total_width) // 2
    
    for level in range(1, 13):
        row = (level - 1) // buttons_per_row
        col = (level - 1) % buttons_per_row
        
        btn_x = start_x + (col * (BUTTON_SMALL_WIDTH + button_gap))
        btn_y = level_buttons_start_y + (row * (BUTTON_SMALL_HEIGHT + button_gap))
        
        # All buttons use small art with black sliver overlay
        try:
            # Small button background
            Gumps.AddButton(gd, btn_x, btn_y, BUTTON_SMALL_ART, BUTTON_SMALL_ART, BUTTON_LEVEL_BASE + level, 1, 0)
            # Black sliver overlay to darken button
            Gumps.AddImageTiled(gd, btn_x, btn_y, BUTTON_SMALL_WIDTH, BUTTON_SMALL_HEIGHT, SLIVER_OVERLAY_TILE)
            
            # Highlight current level with dark blue, others with medium gray
            if level == CURRENT_MASTERY_LEVEL:
                # Selected level - dark blue text
                add_centered_label_with_outline(gd, btn_x, btn_y, BUTTON_SMALL_WIDTH, BUTTON_SMALL_HEIGHT, str(level), 0x0001)
            else:
                # Unselected level - medium gray text
                add_centered_label_with_outline(gd, btn_x, btn_y, BUTTON_SMALL_WIDTH, BUTTON_SMALL_HEIGHT, str(level), 0x0385)
        except Exception:
            pass
    
    # Send gump
    Gumps.SendGump(GUMP_ID, Player.Serial, GUMP_START_X, GUMP_START_Y, gd.gumpDefinition, gd.gumpStrings)

def process_gump_response():
    """Process gump button clicks and handle ritual execution."""
    global CURRENT_MASTERY_LEVEL
    
    while True:
        # Check for gump data without blocking
        gump_data = Gumps.GetGumpData(GUMP_ID)
        
        if not gump_data:
            # No gump data - gump was closed
            debug_message("Gump closed by user", 68)
            break
        
        button_id = gump_data.buttonid
        
        if button_id == 0:
            # No button pressed yet, wait a bit and check again
            Misc.Pause(100)  # Short pause to prevent CPU spinning
            continue
        
        elif button_id == BUTTON_ASCEND:
            # Ascend button clicked - close gump and start ritual
            debug_message(f"Starting Shadow Ascension ritual with {CURRENT_MASTERY_LEVEL} orbs", 68)
            if DEBUG_MODE:
                Misc.SendMessage(f"Shadow Ascension: Level {CURRENT_MASTERY_LEVEL}", 0x0001)
            
            # Close current gump
            Gumps.CloseGump(GUMP_ID)
            
            # Update config with selected mastery level
            RITUAL_CONFIG["circle"]["element_count"] = CURRENT_MASTERY_LEVEL
            
            # Perform ritual
            try:
                perform_shadow_circle_ritual()
            except Exception as e:
                debug_message(f"Error in ritual: {e}", 33)
                import traceback
                debug_message(traceback.format_exc(), 33)
            
            # Exit after ritual completes (run once mode)
            debug_message("Shadow Ascension complete - script ending", 68)
            break
        
        elif BUTTON_LEVEL_BASE <= button_id <= BUTTON_LEVEL_BASE + 12:
            # Level button clicked
            new_level = button_id - BUTTON_LEVEL_BASE
            CURRENT_MASTERY_LEVEL = new_level
            debug_message(f"Mastery level set to {CURRENT_MASTERY_LEVEL}", 68)
            
            # Re-render gump to show updated selection
            render_shadow_ascension_gump()
            
            # Small pause after re-render
            Misc.Pause(100)

# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """Main execution function - launches gump UI"""
    try:
        # Render initial gump
        render_shadow_ascension_gump()
        
        # Process gump responses in loop
        process_gump_response()
        
    except Exception as e:
        debug_message(f"Error in main: {e}", 33)
        import traceback
        debug_message(traceback.format_exc(), 33)

if __name__ == "__main__":
    main()
