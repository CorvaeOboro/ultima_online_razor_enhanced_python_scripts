"""
RITUAL of ORBS - a Razor Enhanced Python Script for Ultima Online

14 mastery orbs raised on pillars surrounded by thematic items , at the center is a branching darkness
Orbs = Air, Fire, Earth, Shadow, Blood, Doom, Fortune, Artisan, Bulwark, Poison, Lyric, Death, Druidic, Holy

1) Shapes 
- Center stack: dark cloth base with cracked pattern, black pearl rings, outer plant-bowl ring
- Pillars: under each orb, per-orb base stack -> stacked plant bowls -> lantern -> orb
- Orb circle: 14-orb ring , with per-orb decorations
- Decorations: rings, arrows, symbols, and lines around each orb
  - Rings: circular points; may remove axis-aligned points for smoothing
  - Arrows: point away from center toward each orb
  - Symbols: predefined patterns (triangle, rune, gear, note)
  - Lines: straight lines from center to orb

2) Systems 
- Orbs Item Themes are defined by ORB_DEFINITIONS
- Random pools: decorations may specify random_pool and randomize to pick per-point items
- Stacks: decorations may specify stack_amount or stack_min/stack_max for piles (gold)
- Ordering: ORDER_SMALLEST_FIRST toggles placement order 
- a Preview mode 

ORBS THEME ITEMS________________________________________________
- Air:             sapphire gem , feathers 
- Fire (Fira):     amber gem , kindling, fire ruby 
- Earth:           fertile earth , iron ore 
- Shadow:          dark cloth , black pearl , nightsight potion ( dark blue ) 
- Blood:           refresh potion
- Doom:            explosion potion , mana potion
- Fortune:         gold coins , citrine 
- Artisan:         tools , gears
- Bulwark:         shields , ingots
- Poison:          poison potion , bottle of ichor
- Lyric:           instruments , star sapphire 
- Death:           bones , bone piles , rib cage 
- Druidic:         seeds , parasitic plant 
- Holy:            strength potion , diamonds, faery dust 

VERSION::20250826
"""
import math
import time
import random

# ===== Global toggles =====
DEBUG_MODE = False
SAFE_MODE = False
PREVIEW_MODE = True           # If True, render client-side only
USE_AUTO_Z_STACKING = True     # If True, use Z=-1 for all item placements (let game handle stacking)

# ===== Layer toggles =====
ENABLE_CENTER_CRACKS = True           # cloth cracks made from Cloth
ENABLE_CENTER_CRACKS_CLOTH = True      # cloth crack arms (main layer)
ENABLE_CENTER_CRACKS_EYE_NEWT = True   # eye of newt crack arms (mystical layer)
ENABLE_CENTER_PEARL = True            # black pearl crack rings
ENABLE_CENTER_BOWL_RING = False       # plant bowl ring around center
# Orbs and their decorations
ENABLE_ORBS = True                    # place orb pillars + orbs on the ring
ENABLE_ORB_DECORATIONS = True         # place per-orb decorations

# ===== Global Exclusion Zone =====
# center platform cant place
ENABLE_EXCLUSION_ZONE = True          # If True, skip placement attempts on excluded coordinates
EXCLUSION_ZONE_RADIUS = 1             # Radius around center to exclude (0=center only, 1=center+adjacent, 2=center+2 rings)

# Orb whitelist: if empty, place all. Otherwise only place these keys (normalized, e.g., "druidic").
ORB_KEYS_ALLOWED = []
# "fire", # good needs more 
# "earth",
# "druidic",
# "death",
# "fortune", # good
# "blood",
# "artisan",
# "doom",
# "poison",
# "bulwark",
# "holy",
# "shadow",
# "lyric",
# "air", # good , needs more

ORDER_SMALLEST_FIRST = False # inner rings (smallest radius) to be placed LAST on top.
# we reversed this direction so the inner rings sort on top of outer rings
ENABLE_LIGHTING_ACTION = False # Lighting the candle is shard-dependent. We attempt to Use it if configured.
# we are lighting them after currently

# ===== SHAPES  =====
ORB_CIRCLE = {
    "radius": 14,       # distance from center for the 14 orb positions
    "rotation": 12,    # base rotation; may be overridden by strategy below
    "count": 14,
}

# Rotation strategy for better isometric presentation
# Options: "fixed" (use FIXED_ROTATION_DEG), "half_step" (360/count/2 offset)
# ORB_ROTATION_STRATEGY = "half_step"
ORB_ROTATION_STRATEGY = "fixed"
FIXED_ROTATION_DEG = 45

# Default decoration layout when not specified per-orb
INNER_RING_RADIUS = 1
MIDDLE_RING_RADIUS = 3
OUTER_RING_RADIUS = 4
RING_POINTS = 12
RING_ROTATION = 0
LINE_SPACING = 1

# Pillar construction
PILLAR_BOWL_STACK_COUNT = 5
STACK_Z_STEP = 1          # Z increment per stacked item
STACK_TOP_EXTRA = 1       # Extra Z for items that sit on top of a layer

# Do not allow orb-related items to cover the center layers
ORB_CENTER_EXCLUSION_RADIUS = 6  # tiles around center off-limits for orb decorations

# Center-layer visuals (cloth cracks, black pearl rings, plant bowl ring)
CENTER_CRACK_ARMS = 10
CENTER_CRACK_MIN_LEN = 5
CENTER_CRACK_MAX_LEN = 10
CENTER_PEARL_RING_RADII = [2, 3, 17]
CENTER_PEARL_RING_POINTS = [12, 16, 100]
CENTER_BOWL_RING_RADIUS = 6
CENTER_BOWL_RING_POINTS = 16

# Crack branching 
CENTER_CRACK_BRANCH_CHANCE = 0.25            # chance per segment to start a branch
CENTER_CRACK_MAX_BRANCHES_PER_ARM = 2        # cap branches per main arm
CENTER_CRACK_BRANCH_ANGLE_OFFSET_MIN = 20    # degrees away from main direction (min)
CENTER_CRACK_BRANCH_ANGLE_OFFSET_MAX = 55    # degrees away from main direction (max)
CENTER_CRACK_BRANCH_MIN_LEN = 2
CENTER_CRACK_BRANCH_MAX_LEN = 4

# Black pearl crack tuning (extends further and stacks more near center)
PEARL_CRACK_MIN_LEN = CENTER_CRACK_MIN_LEN + 2
PEARL_CRACK_MAX_LEN = CENTER_CRACK_MAX_LEN + 4
PEARL_CRACK_ARMS = CENTER_CRACK_ARMS
PEARL_STACK_MAX = 10               # maximum items stacked at center
PEARL_STACK_FALLOFF = 2.0         # tiles per -1 stack as distance increases
PEARL_STACK_SIGMA = 1.2           # smooth falloff shaping for center stacking
PEARL_STACK_PREVIEW_DELAY_MS = 120  # pause between stacked preview placements

# ===== TIMING  =====
PAUSE_DURATION = 350
PAUSE_DURATION_PLACE = 550
MAX_DISTANCE = 2

GOTO_BASE_DELAY = 250
GOTO_MAX_RETRIES = 1
WIGGLE_RADII = [0]

WIGGLE_ANGLES = [0, 45, 90, 135, 180, 225, 270, 315]
WALK_REPEATS_PER_DIR = 2

CENTER_BIAS_ENABLED = True
CENTER_NUDGE_DISTANCE = 3
CENTER_NUDGE_STEPS = 2

PLACE_MAX_RETRIES = 2
PLACE_BACKOFF_BASE = 250
POINT_TIMEOUT_MS = 1500
POINT_BREATHER_MS = 250

RATE_MIN_GAP_MS = 350
LOOP_YIELD_MS = 40
JITTER_MS = 50
LAST_ACTION_MS = 0

# In preview mode, we want much snappier timings
PREVIEW_DELAY_SCALE = 0.3   # 30% of normal delays
PREVIEW_JITTER_MS = 10      # smaller random jitter window
PREVIEW_DEFAULT_HUE = 0x0000   # 0 means no hue
PREVIEW_Z_OFFSET = 3 # avoiding clipping with ground
PREVIEW_RANDOM_POOL_DELAY_MS = 600  # extra delay per preview random-pool item to avoid client overload

MAX_PHASE_FAILURES = 6
PLACED_COORDS_BY_ITEM = {}
BAD_COORDS = set()
EXCLUDED_COORDS = set()  # Global exclusion zone coordinates
ENABLE_STACK_TRACKING = True
# Tracks the next available Z at a given (x,y) after successful placements.
PLACED_TOP_Z = {}

#//==========================================================================
# ITEM IDS
ORB_ITEM_ID = 0x573E # All orbs share the same base item ID; hues come from ORB_DEFINITIONS directly
DEFAULT_CLOTH_HUE = 0x025A # Default cloth hue for the base layer when an orb definition doesn't specify one

MATERIAL_ITEM_IDS = {
    # Base items 
    "Cloth": 0x1766,
    "Plant Bowl": 0x15FD,
    "Lantern": 0x0A25,
    # Air
    "Sapphire": [0x0F11, 0x0F19, 0x0F21],
    "Agility Potion": [0x0F08],
    "Feather": [0x1BD1],
    "Spider Silk": [0x0F8D],
    "Empty Bottle": [0x0F0E],
    # Fire
    "Amber": [0x0F25],
    "Fire Ruby": [0x3197],
    "Ruby": [0x0F13],
    "Kindling": [0x0DE1],
    "Cure Potion": [0x0F07],
    # Earth
    "Fertile Dirt": [0x0F81],
    "Iron Ore": [0x19B7, 0x19B8, 0x19B9, 0x19BA],
    "Lodestone": [0x5739],
    "Mandrake Root": [0x0F86],
    # Shadow
    "Black Pearl": [0x0F7A],
    "Spider Carapace": [0x5720],
    "Invisibility Potion": [0x0F0A],      # hue 0x048D when applicable
    "Night Sight Potion": [0x0F06],
    # Blood
    "Refresh Potion": [0x0F0B],
    "Blood Moss": [0x0F7B],
    # Doom
    "Amethyst": [0x0F16],
    "Mana Potion": [0x0F0D],              # hue 0x0387 when applicable
    "Explosion Potion": [0x0F0D],
    "Eye of Newt": [0x0F87],
    # Fortune
    "Citrine": [0x0F15],
    "Gold Coin": 0x0EED,
    "Sulphorous Ash": [0x0F8C],
    # Poison
    "Poison Potion": [0x0F0A],
    "Nightshade": [0x0F88],
    "Bottle of Ichor": [0x5748],
    "Emerald": [0x0F10],
    # Death
    "Bones": [0x0F7E],
    "Bone Piles": [0x1B0E, 0x1B0B, 0x1B0C],
    "Rib Cage": [0x1B17],
    # Druidic
    "Tourmaline": [0x0F18, 0x0F2D],
    "Parasitic Plant": [0x3190],
    "Seed of Renewal": [0x5736],
    "Mandrake Root": [0x0F86],
    # Holy
    "Diamond": [0x0F26],
    "Strength Potion": [0x0F09],
    "Faery Dust": [0x5745],
    # Artisan
    "Gears": [0x1053],
    # (uses tools from TOOL_ITEM_IDS)
    # Bulwark
    "Iron Ingot": [0x1BF2],
    # (uses shields from SHIELD_ITEM_IDS)
    # Lyrical
    # (uses instruments from INSTRUMENT_ITEM_IDS)
    "Star Sapphire": [0x0F0F],
}

# Gold coin specific handling
GOLD_ITEM_ID = MATERIAL_ITEM_IDS.get("Gold Coin")
GOLD_STACK_AMOUNTS = [1, 5, 20]

# Common shield Item IDs 
SHIELD_ITEM_IDS = [
    0x1B72,  # Bronze Shield
    0x1B73,  # Buckler
    0x1B74,  # Metal Kite Shield
    0x1B75,  # Shield
    0x1B76,  # Heater Shield
    0x1B77,  # Shield
    0x1B78,  # Wooden Shield
    0x1B79,  # Shield
    0x1B7A,  # Wooden Kite Shield
    0x1B7B,  # Metal Shield
    0x1BC3,  # Chaos Shield
    0x1BC4,  # Order Shield
]

# Common artisan tool Item IDs 
TOOL_ITEM_IDS = [
    0x0F9D,  # Sewing Kit
    0x14FC,  # Lockpicks
    0x1EB8,  # Tinker Tools
    0x0F9F,  # Scissors
    0x0E9B,  # Mortar and Pestle
    0x13E3,  # Smith's Hammer
    0x0FBB,  # Tongs
    0x1034,  # Saw
    0x102C,  # Plane
    0x10E4,  # Draw Knife
    0x10E5,  # Froe
    0x10E7,  # Scorp
    0x10E6,  # Inshave
    0x0E86,  # Pickaxe
    0x0F39,  # Shovel
    0x0F43,  # Hatchet
    0x0DC0,  # Fishing Pole
]

# Standing Harp, Lap Harp, Lute, Drum, Tambourine, Tambourine (tassel)
INSTRUMENT_ITEM_IDS = [
    0x0EB1,  # Standing Harp
    0x0EB2,  # Lap Harp
    0x0EB3,  # Lute
    0x0E9C,  # Drum
    0x0E9D,  # Tambourine
    0x0E9E,  # Tambourine (tassel)
]

# Declarative random pools for decorations 
RANDOM_POOLS = {
    "shields": SHIELD_ITEM_IDS,
    "tools": TOOL_ITEM_IDS,
    "instruments": INSTRUMENT_ITEM_IDS,
}

# ===== Orb placement order control =====
# which orb (by key) goes to which circle slot (index).
ORB_ORDER = {
    0: "fire",
    1: "earth",
    2: "druidic",
    3: "death",
    4: "fortune",
    5: "blood",
    6: "artisan",
    7: "doom",
    8: "poison",
    9: "bulwark",
    10: "holy",
    11: "shadow",
    12: "lyric",
    13: "air",
}

# ===== Per-orb definitions =====
# Each orb defines: key, orb hue, and decorations.
# Decorations support types: ring, arrow, symbol, line. Each has its own config.
ORB_DEFINITIONS = [
    {
        "key": "air",
        "orb_hue": 0x0487,
        "decorations": [
            {"type": "ring", "item_ids": MATERIAL_ITEM_IDS["Sapphire"], "radius": INNER_RING_RADIUS, "points": RING_POINTS, "rotation": 0},
            {"type": "ring", "item_ids": MATERIAL_ITEM_IDS["Agility Potion"], "radius": MIDDLE_RING_RADIUS, "points": RING_POINTS, "rotation": 0},
            {"type": "ring", "item_ids": MATERIAL_ITEM_IDS["Spider Silk"], "radius": OUTER_RING_RADIUS, "points": 20, "rotation": 0},
            {"type": "ring", "item_ids": MATERIAL_ITEM_IDS["Empty Bottle"], "radius": 4, "points": 8, "rotation": 22},
            {"type": "symbol", "item_ids": MATERIAL_ITEM_IDS["Agility Potion"], "pattern": "rune", "scale": 2},
            {"type": "line", "item_ids": MATERIAL_ITEM_IDS["Feather"], "length": 4, "spacing": 1},
            {"type": "line", "item_ids": MATERIAL_ITEM_IDS["Sapphire"], "length": 4, "spacing": 1},
            {"type": "line", "item_ids": MATERIAL_ITEM_IDS["Sapphire"], "length": 3, "spacing": 1, "direction": "inward", "start_offset": 1},
            {"type": "line", "item_ids": MATERIAL_ITEM_IDS["Empty Bottle"], "length": 5, "spacing": 1, "direction": "outward", "start_offset": 4},
        ],
    },
    {
        "key": "fire",
        "orb_hue": 0x0665,
        "decorations": [
            {"type": "ring", "item_ids": MATERIAL_ITEM_IDS["Fire Ruby"], "radius": INNER_RING_RADIUS, "points": RING_POINTS, "rotation": 0},
            {"type": "ring", "item_ids": MATERIAL_ITEM_IDS["Kindling"], "radius": 2, "points": RING_POINTS, "rotation": 0},
            {"type": "ring", "item_ids": MATERIAL_ITEM_IDS["Amber"], "radius": MIDDLE_RING_RADIUS, "points": RING_POINTS, "rotation": 0},
            {"type": "ring", "item_ids": MATERIAL_ITEM_IDS["Cure Potion"], "radius": OUTER_RING_RADIUS, "points": 36, "rotation": 22},
            {"type": "symbol", "item_ids": MATERIAL_ITEM_IDS["Amber"], "pattern": "triangle", "scale": 2},
            {"type": "line", "item_ids": MATERIAL_ITEM_IDS["Amber"], "length": 4, "spacing": 1},
            {"type": "line", "item_ids": MATERIAL_ITEM_IDS["Amber"], "length": 3, "spacing": 1, "direction": "inward", "start_offset": 1},
        ],
    },
    {
        "key": "earth",
        "orb_hue": 0x0592,
        "decorations": [
            {"type": "ring", "item_ids": MATERIAL_ITEM_IDS["Iron Ore"], "radius": INNER_RING_RADIUS, "points": RING_POINTS, "rotation": 0},
            {"type": "ring", "item_ids": MATERIAL_ITEM_IDS["Lodestone"], "radius": 2, "points": RING_POINTS, "rotation": 0},
            {"type": "ring", "item_ids": MATERIAL_ITEM_IDS["Iron Ore"], "radius": MIDDLE_RING_RADIUS, "points": RING_POINTS, "rotation": 0},
            {"type": "ring", "item_ids": MATERIAL_ITEM_IDS["Mandrake Root"], "radius": OUTER_RING_RADIUS, "points": 24, "rotation": 0},
            {"type": "symbol", "item_ids": MATERIAL_ITEM_IDS["Fertile Dirt"], "pattern": "rune", "scale": 2},
            {"type": "line", "item_ids": MATERIAL_ITEM_IDS["Lodestone"], "length": 5, "spacing": 1},
            {"type": "line", "item_ids": MATERIAL_ITEM_IDS["Lodestone"], "length": 3, "spacing": 1, "direction": "inward", "start_offset": 1},
        ],
    },
    {
        "key": "shadow",
        "orb_hue": 0x048D,
        "decorations": [
            {"type": "ring", "item_ids": MATERIAL_ITEM_IDS["Spider Carapace"], "radius": INNER_RING_RADIUS, "points": RING_POINTS, "rotation": 0},
            {"type": "ring", "item_ids": MATERIAL_ITEM_IDS["Cloth"], "radius": 2, "points": RING_POINTS, "rotation": 0},
            {"type": "ring", "item_ids": MATERIAL_ITEM_IDS["Eye of Newt"], "radius": 3, "points": RING_POINTS, "rotation": 0},
            {"type": "ring", "item_ids": MATERIAL_ITEM_IDS["Invisibility Potion"], "radius": MIDDLE_RING_RADIUS, "points": RING_POINTS, "rotation": 0, "hue": 0x048D},
            {"type": "ring", "item_ids": MATERIAL_ITEM_IDS["Black Pearl"], "radius": OUTER_RING_RADIUS, "points": 24, "rotation": 0},
            {"type": "symbol", "item_ids": MATERIAL_ITEM_IDS["Black Pearl"], "pattern": "rune", "scale": 2},
            {"type": "line", "item_ids": MATERIAL_ITEM_IDS["Black Pearl"], "length": 4, "spacing": 1},
            {"type": "line", "item_ids": MATERIAL_ITEM_IDS["Black Pearl"], "length": 3, "spacing": 1, "direction": "inward", "start_offset": 1},
        ],
    },
    {
        "key": "doom",
        "orb_hue": 0x08A5,
        "decorations": [
            {"type": "ring", "item_ids": MATERIAL_ITEM_IDS["Mana Potion"], "radius": INNER_RING_RADIUS, "points": RING_POINTS, "rotation": 0, "hue": 0x0387},
            {"type": "ring", "item_ids": MATERIAL_ITEM_IDS["Explosion Potion"], "radius": 2, "points": RING_POINTS, "rotation": 0},
            {"type": "ring", "item_ids": MATERIAL_ITEM_IDS["Mana Potion"], "radius": MIDDLE_RING_RADIUS, "points": RING_POINTS, "rotation": 0, "hue": 0x0387},
            {"type": "ring", "item_ids": MATERIAL_ITEM_IDS["Black Pearl"], "radius": OUTER_RING_RADIUS, "points": RING_POINTS, "rotation": 0},
            {"type": "symbol", "item_ids": MATERIAL_ITEM_IDS["Amethyst"], "pattern": "rune", "scale": 2},
            {"type": "line", "item_ids": MATERIAL_ITEM_IDS["Amethyst"], "length": 7, "spacing": 1},
            {"type": "line", "item_ids": MATERIAL_ITEM_IDS["Amethyst"], "length": 3, "spacing": 1, "direction": "inward", "start_offset": 1},
            {"type": "ring", "item_ids": MATERIAL_ITEM_IDS["Eye of Newt"], "radius": 3, "points": RING_POINTS, "rotation": 0},
        ],
    },
    {
        "key": "blood",
        "orb_hue": 0x0662,
        "decorations": [
            {"type": "ring", "item_ids": MATERIAL_ITEM_IDS["Refresh Potion"], "radius": INNER_RING_RADIUS, "points": RING_POINTS, "rotation": 0},
            {"type": "ring", "item_ids": MATERIAL_ITEM_IDS["Refresh Potion"], "radius": MIDDLE_RING_RADIUS, "points": RING_POINTS, "rotation": 0},
            {"type": "ring", "item_ids": MATERIAL_ITEM_IDS["Ruby"], "radius": OUTER_RING_RADIUS, "points": 24, "rotation": 0},
            {"type": "symbol", "item_ids": MATERIAL_ITEM_IDS["Blood Moss"], "pattern": "rune", "scale": 2},
            {"type": "line", "item_ids": MATERIAL_ITEM_IDS["Blood Moss"], "length": 4, "spacing": 1},
            {"type": "line", "item_ids": MATERIAL_ITEM_IDS["Blood Moss"], "length": 3, "spacing": 1, "direction": "inward", "start_offset": 1},
        ],
    },
    {
        "key": "holy",
        "orb_hue": 0x09A4,
        "decorations": [
            {"type": "ring", "item_ids": MATERIAL_ITEM_IDS["Faery Dust"], "radius": INNER_RING_RADIUS, "points": RING_POINTS, "rotation": 0},
            {"type": "ring", "item_ids": MATERIAL_ITEM_IDS["Faery Dust"], "radius": MIDDLE_RING_RADIUS, "points": RING_POINTS, "rotation": 0},
            {"type": "ring", "item_ids": MATERIAL_ITEM_IDS["Strength Potion"], "radius": OUTER_RING_RADIUS, "points": 20, "rotation": 0},
            {"type": "symbol", "item_ids": MATERIAL_ITEM_IDS["Diamond"], "pattern": "rune", "scale": 2},
            {"type": "line", "item_ids": MATERIAL_ITEM_IDS["Diamond"], "length": 4, "spacing": 1},
            {"type": "line", "item_ids": MATERIAL_ITEM_IDS["Diamond"], "length": 3, "spacing": 1, "direction": "inward", "start_offset": 1},
        ],
    },
    {
        "key": "poison",
        "orb_hue": 0x0046,
        "decorations": [
            {"type": "ring", "item_ids": MATERIAL_ITEM_IDS["Bottle of Ichor"], "radius": INNER_RING_RADIUS, "points": RING_POINTS, "rotation": 0},
            {"type": "ring", "item_ids": MATERIAL_ITEM_IDS["Nightshade"], "radius": 2, "points": RING_POINTS, "rotation": 0},
            {"type": "ring", "item_ids": MATERIAL_ITEM_IDS["Poison Potion"], "radius": MIDDLE_RING_RADIUS, "points": RING_POINTS, "rotation": 0},
            {"type": "ring", "item_ids": MATERIAL_ITEM_IDS["Nightshade"], "radius": 4, "points": 22, "rotation": 0},
            {"type": "symbol", "item_ids": MATERIAL_ITEM_IDS["Emerald"], "pattern": "rune", "scale": 2},
            {"type": "line", "item_ids": MATERIAL_ITEM_IDS["Nightshade"], "length": 5, "spacing": 1, "direction": "inward", "start_offset": 1},
        ],
    },
    {
        "key": "fortune",
        "orb_hue": 0x08A8,
        "decorations": [
            {"type": "ring", "item_ids": MATERIAL_ITEM_IDS["Gold Coin"], "radius": INNER_RING_RADIUS, "points": RING_POINTS, "rotation": 0},
            {"type": "ring", "item_ids": MATERIAL_ITEM_IDS["Gold Coin"], "radius": 2, "points": RING_POINTS, "rotation": 0},
            {"type": "ring", "item_ids": MATERIAL_ITEM_IDS["Gold Coin"], "radius": MIDDLE_RING_RADIUS, "points": RING_POINTS, "rotation": 0},
            {"type": "ring", "item_ids": MATERIAL_ITEM_IDS["Sulphorous Ash"], "radius": OUTER_RING_RADIUS, "points": 24, "rotation": 0},
            {"type": "symbol", "item_ids": MATERIAL_ITEM_IDS["Citrine"], "pattern": "rune", "scale": 2},
            {"type": "line", "item_ids": MATERIAL_ITEM_IDS["Citrine"], "length": 7, "spacing": 1},
            {"type": "line", "item_ids": MATERIAL_ITEM_IDS["Citrine"], "length": 3, "spacing": 1, "direction": "inward", "start_offset": 1},
            {"type": "line", "item_ids": MATERIAL_ITEM_IDS["Gold Coin"], "length": 3, "spacing": 1, "direction": "outward", "start_offset": 8},
        ],
    },
    {
        "key": "artisan",
        "orb_hue": 0x0455,
        "decorations": [
            {"type": "ring", "random_pool": "tools", "randomize": True, "radius": INNER_RING_RADIUS, "points": RING_POINTS, "rotation": 0},
            {"type": "ring", "random_pool": "tools", "randomize": True, "radius": MIDDLE_RING_RADIUS, "points": RING_POINTS, "rotation": 0},
            {"type": "symbol", "item_ids": MATERIAL_ITEM_IDS["Star Sapphire"], "pattern": "gear", "scale": 2},
            {"type": "line", "item_ids": MATERIAL_ITEM_IDS["Star Sapphire"], "length": 4, "spacing": 1},
            {"type": "line", "item_ids": MATERIAL_ITEM_IDS["Star Sapphire"], "length": 3, "spacing": 1, "direction": "inward", "start_offset": 1},
        ],
    },
    {
        "key": "bulwark",
        "orb_hue": 0x0835,
        "decorations": [
            {"type": "ring", "random_pool": "shields", "randomize": True, "radius": INNER_RING_RADIUS, "points": RING_POINTS, "rotation": 0},
            {"type": "ring", "item_ids": MATERIAL_ITEM_IDS["Iron Ingot"], "radius": 2, "points": RING_POINTS, "rotation": 0},
            {"type": "ring", "random_pool": "shields", "randomize": True, "radius": MIDDLE_RING_RADIUS, "points": RING_POINTS, "rotation": 0},
            {"type": "symbol", "item_ids": MATERIAL_ITEM_IDS["Strength Potion"], "pattern": "triangle", "scale": 2},
            {"type": "line", "item_ids": MATERIAL_ITEM_IDS["Iron Ingot"], "length": 5, "spacing": 1},
            {"type": "line", "item_ids": MATERIAL_ITEM_IDS["Iron Ingot"], "length": 3, "spacing": 1, "direction": "inward", "start_offset": 1},
        ],
    },
    {
        "key": "lyric",
        "orb_hue": 0x0485,
        "decorations": [
            {"type": "ring", "random_pool": "instruments", "randomize": True, "radius": INNER_RING_RADIUS, "points": RING_POINTS, "rotation": 0},
            {"type": "ring", "item_ids": MATERIAL_ITEM_IDS["Amethyst"], "radius": 2, "points": RING_POINTS, "rotation": 0},
            {"type": "ring", "random_pool": "instruments", "randomize": True, "radius": MIDDLE_RING_RADIUS, "points": RING_POINTS, "rotation": 0},
            {"type": "symbol", "random_pool": "instruments", "randomize": True, "pattern": "note", "scale": 2},
            {"type": "line", "item_ids": MATERIAL_ITEM_IDS["Amethyst"], "length": 4, "spacing": 1},
            {"type": "line", "item_ids": MATERIAL_ITEM_IDS["Amethyst"], "length": 3, "spacing": 1, "direction": "inward", "start_offset": 1},
        ],
    },
    {
        "key": "death",
        "orb_hue": 0x0005,
        "decorations": [
            {"type": "ring", "item_ids": MATERIAL_ITEM_IDS["Bones"] + MATERIAL_ITEM_IDS["Bone Piles"] + MATERIAL_ITEM_IDS["Rib Cage"], "radius": INNER_RING_RADIUS, "points": RING_POINTS, "rotation": 0},
            {"type": "ring", "item_ids": MATERIAL_ITEM_IDS["Bone Piles"], "radius": 1, "points": 4, "rotation": 0},
            {"type": "ring", "item_ids": MATERIAL_ITEM_IDS["Eye of Newt"], "radius": 4, "points": 24, "rotation": 0},
            {"type": "ring", "item_ids": MATERIAL_ITEM_IDS["Bones"] + MATERIAL_ITEM_IDS["Bone Piles"] + MATERIAL_ITEM_IDS["Rib Cage"], "radius": MIDDLE_RING_RADIUS, "points": RING_POINTS, "rotation": 0},
            {"type": "symbol", "item_ids": MATERIAL_ITEM_IDS["Black Pearl"], "pattern": "rune", "scale": 2},
            {"type": "line", "item_ids": MATERIAL_ITEM_IDS["Bones"], "length": 7, "spacing": 1},
            {"type": "line", "item_ids": MATERIAL_ITEM_IDS["Bones"], "length": 5, "spacing": 1, "angle_offset": 0},
            {"type": "line", "item_ids": MATERIAL_ITEM_IDS["Bones"], "length": 4, "spacing": 1, "direction": "outward", "start_offset": 2},
        ],
    },
    {
        "key": "druidic",
        "orb_hue": 0x0954,
        "decorations": [
            {"type": "ring", "item_ids": MATERIAL_ITEM_IDS["Parasitic Plant"], "radius": INNER_RING_RADIUS, "points": RING_POINTS, "rotation": 0},
            {"type": "ring", "item_ids": MATERIAL_ITEM_IDS["Seed of Renewal"], "radius": 3, "points": 20, "rotation": 0},
            {"type": "ring", "item_ids": MATERIAL_ITEM_IDS["Tourmaline"], "radius": MIDDLE_RING_RADIUS, "points": RING_POINTS, "rotation": 0},
            {"type": "symbol", "item_ids": MATERIAL_ITEM_IDS["Tourmaline"], "pattern": "rune", "scale": 2},
            {"type": "line", "item_ids": MATERIAL_ITEM_IDS["Tourmaline"], "length": 4, "spacing": 1},
            {"type": "line", "item_ids": MATERIAL_ITEM_IDS["Tourmaline"], "length": 3, "spacing": 1, "direction": "inward", "start_offset": 1},
        ],
    }
]

# All orbs share the same base item ID; hues come from ORB_DEFINITIONS directly
ORB_ITEM_ID = 0x573E
#//==========================================================================

# ===== Apply external orb item/hue info =====
def _normalize_orb_key(name):
    try:
        n = (name or "").strip().lower()
        # remove trailing " orb" if present and spaces
        if n.endswith(" orb"):
            n = n[:-4]
        return n.replace(" ", "")
    except Exception:
        return ""

# Build ordered orb definitions according to ORB_ORDER mapping (position -> orb key).
# Any unspecified positions are filled from remaining definitions in their original order.
def get_ordered_orb_definitions():
    try:
        if not ORB_ORDER:
            return list(ORB_DEFINITIONS)
        # Map normalized key -> definition
        def_map = {}
        for d in ORB_DEFINITIONS:
            k = _normalize_orb_key(d.get("key", ""))
            if k:
                def_map[k] = d
        count = int(ORB_CIRCLE.get("count", len(ORB_DEFINITIONS)))
        ordered = [None] * count
        used_keys = set()
        # Place specified ones by index
        for pos, raw_key in sorted(ORB_ORDER.items(), key=lambda kv: kv[0]):
            if 0 <= int(pos) < count:
                nk = _normalize_orb_key(raw_key)
                d = def_map.get(nk)
                if d is not None and nk not in used_keys:
                    ordered[int(pos)] = d
                    used_keys.add(nk)
        # Fill the rest with remaining definitions preserving original order
        cursor = 0
        for d in ORB_DEFINITIONS:
            nk = _normalize_orb_key(d.get("key", ""))
            if nk in used_keys:
                continue
            while cursor < count and ordered[cursor] is not None:
                cursor += 1
            if cursor >= count:
                break
            ordered[cursor] = d
            used_keys.add(nk)
            cursor += 1
        # Filter any trailing None
        return [d for d in ordered if d is not None]
    except Exception:
        # Fallback to default order on any error
        return list(ORB_DEFINITIONS)

def initialize_exclusion_zone(center_x, center_y):
    """Initialize the global exclusion zone around center coordinates"""
    global EXCLUDED_COORDS
    EXCLUDED_COORDS.clear()
    
    if not ENABLE_EXCLUSION_ZONE:
        return
    
    # Add center and surrounding grid cells based on radius
    for dx in range(-EXCLUSION_ZONE_RADIUS, EXCLUSION_ZONE_RADIUS + 1):
        for dy in range(-EXCLUSION_ZONE_RADIUS, EXCLUSION_ZONE_RADIUS + 1):
            x = center_x + dx
            y = center_y + dy
            EXCLUDED_COORDS.add((x, y))
    
    debug_message(f"Exclusion zone initialized: {len(EXCLUDED_COORDS)} coordinates around ({center_x},{center_y}) radius {EXCLUSION_ZONE_RADIUS}", 68)

def is_coordinate_excluded(x, y):
    """Check if coordinate is in the global exclusion zone"""
    return ENABLE_EXCLUSION_ZONE and (x, y) in EXCLUDED_COORDS

def debug_message(msg, color=0):
    if DEBUG_MODE:
        try:
            Misc.SendMessage(msg, color)
        except Exception:
            print(msg)

def _convert_packet_to_bytes(packet_list):
    byte_list = []
    for value in packet_list:
        if value:
            byte_list.append(int(value, 16))
        else:
            byte_list.append(0)
    return byte_list

def _send_fake_item(item_x, item_y, item_z, item_id_4hex_with_space, hue_4hex_with_space):
    try:
        packet = (
            "F3 00 01 00 48 FC BB 12 "
            + item_id_4hex_with_space
            + " 00 00 01 00 01 05 88 06 88 0A 00 04 15 20 00 00"
        )
        packet_list = packet.split(" ")

        serial_hex = hex(random.randrange(0, 0xFFFFFF))[2:].zfill(6)

        i_loc_x = hex(int(item_x))[2:].zfill(4)
        i_loc_y = hex(int(item_y))[2:].zfill(4)
        i_loc_z = hex(int(item_z))[2:].zfill(2)

        x1, x2 = i_loc_x[:2], i_loc_x[2:]
        y1, y2 = i_loc_y[:2], i_loc_y[2:]

        hues = hue_4hex_with_space.split(" ")

        packet_list[5] = serial_hex[0:2]
        packet_list[6] = serial_hex[2:4]
        packet_list[7] = serial_hex[4:6]
        packet_list[15] = x1
        packet_list[16] = x2
        packet_list[17] = y1
        packet_list[18] = y2
        packet_list[19] = i_loc_z
        packet_list[21] = hues[0]
        packet_list[22] = hues[1]

        byte_list = _convert_packet_to_bytes(packet_list)
        PacketLogger.SendToClient(byte_list)
    except Exception as e:
        debug_message(f"Preview send failed: {e}", 33)

def _format_hex_4_with_space(value):
    s = f"{int(value) & 0xFFFF:04X}"
    return s[:2] + " " + s[2:]

def preview_item_at(x, y, z, item_id, hue=PREVIEW_DEFAULT_HUE):
    item_hex = _format_hex_4_with_space(item_id)
    hue_hex = _format_hex_4_with_space(hue)
    _send_fake_item(x, y, z, item_hex, hue_hex)

def now_ms():
    return int(time.time() * 1000)

def pause_ms(ms):
    if PREVIEW_MODE:
        scaled = int(ms * PREVIEW_DELAY_SCALE)
        jitter = random.randint(0, PREVIEW_JITTER_MS)
        Misc.Pause(max(0, scaled + jitter))
    else:
        Misc.Pause(int(ms + random.randint(0, JITTER_MS)))

def throttle(min_gap_ms=RATE_MIN_GAP_MS):
    global LAST_ACTION_MS
    t = now_ms()
    if LAST_ACTION_MS == 0:
        LAST_ACTION_MS = t
        return
    elapsed = t - LAST_ACTION_MS
    eff_gap = int(min_gap_ms * PREVIEW_DELAY_SCALE) if PREVIEW_MODE else min_gap_ms
    if elapsed < eff_gap:
        Misc.Pause(eff_gap - elapsed)
    LAST_ACTION_MS = now_ms()

def get_ground_z(x, y):
    """Get the actual ground Z coordinate at the specified tile."""
    try:
        # Get static tiles at this position
        tiles = Statics.GetStaticsTileInfo(x, y, Player.Map)
        if tiles and len(tiles) > 0:
            # Use the Z of the highest walkable tile
            walkable_tiles = [t for t in tiles]
            if walkable_tiles:
                ground_z = max(t.StaticZ for t in walkable_tiles)
                debug_message(f"get_ground_z({x},{y}): found static tiles, using Z={ground_z}", 68)
                return ground_z
        # Fallback to land tile Z
        land_z = Statics.GetLandZ(x, y, Player.Map)
        debug_message(f"get_ground_z({x},{y}): using land Z={land_z}", 68)
        return land_z
    except Exception as e:
        debug_message(f"get_ground_z({x},{y}): error {e}, using player Z={Player.Position.Z}", 68)
        return Player.Position.Z

def compute_target_z(x, y, proposed_z):
    """Return the Z to use for placement, stacking above prior placements at (x,y)."""
    # Get the actual ground Z at this location
    ground_z = get_ground_z(x, y)
    
    if ENABLE_STACK_TRACKING:
        prev = PLACED_TOP_Z.get((x, y))
        if prev is not None:
            try:
                # Always stack on top of previous items
                return int(prev) + STACK_Z_STEP
            except Exception:
                return prev + STACK_Z_STEP
    
    # Use ground Z as base instead of proposed Z
    return ground_z

def is_safe_ground(x, y, game_map=None):
    if game_map is None:
        game_map = Player.Map
    if (x, y) in BAD_COORDS:
        return False
    try:
        land_id = Statics.GetLandID(x, y, game_map)
    except Exception:
        return False
    BAD_LAND_IDS = {0x0001}
    if land_id in BAD_LAND_IDS:
        return False
    return True

def place_item_amount(x, y, item_id, amount, z=None, hue=None):
    """Place a specific amount of a stackable item at ground tile (x,y).
    Falls back to available amount if backpack has less than requested.
    """
    if item_id is None:
        return False
    try:
        amt = max(1, int(amount))
    except Exception:
        amt = 1
    base_z = (z if z is not None else Player.Position.Z)
    if PREVIEW_MODE:
        z_prev = compute_target_z(x, y, base_z)
        z_show = z_prev + int(PREVIEW_Z_OFFSET)
        preview_item_at(x, y, z_show, item_id, hue if hue is not None else PREVIEW_DEFAULT_HUE)
        if ENABLE_STACK_TRACKING:
            PLACED_TOP_Z[(x, y)] = z_prev
        return True

    offsets = [(0, 0)] if SAFE_MODE else [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
    if z is None:
        z = Player.Position.Z

    for dx_off, dy_off in offsets:
        tx = x + dx_off
        ty = y + dy_off
        if not is_valid_position(tx, ty, z):
            continue
        if not is_safe_ground(tx, ty):
            BAD_COORDS.add((tx, ty))
            continue
        z_final = compute_target_z(tx, ty, base_z)
        for attempt in range(1, PLACE_MAX_RETRIES + 1):
            item = Items.FindByID(item_id, -1, Player.Backpack.Serial)
            if not item:
                debug_message(f"Could not find item 0x{item_id:X}", 33)
                return False
            try:
                initial_count = Items.BackpackCount(item_id, -1)
            except Exception as e:
                debug_message(f"BackpackCount error for 0x{item_id:X}: {e}", 33)
                return False
            if initial_count <= 0:
                return False
            move_amt = min(amt, initial_count)
            try:
                if hue is not None:
                    pass
                # Apply Z override if auto-stacking is enabled
                actual_z = -1 if USE_AUTO_Z_STACKING else z_final
                debug_message(f"place_item_amount: MoveOnGround(serial={item.Serial}, amount={move_amt}, x={tx}, y={ty}, z={actual_z}) [calculated_z={z_final}]", 68)
                Items.MoveOnGround(item.Serial, move_amt, tx, ty, actual_z)
            except Exception as e:
                debug_message(f"MoveOnGround failed at ({tx},{ty}) for amt {move_amt}: {e}", 33)
                BAD_COORDS.add((x, y))
                pause_ms(PAUSE_DURATION + 150)
                return False
            else:
                throttle()
                pause_ms(PAUSE_DURATION_PLACE)

            for _ in range(3):
                try:
                    new_count = Items.BackpackCount(item_id, -1)
                except Exception as e:
                    debug_message(f"BackpackCount verify error: {e}", 33)
                    break
                if new_count <= initial_count - move_amt:
                    if ENABLE_STACK_TRACKING:
                        PLACED_TOP_Z[(tx, ty)] = z_final
                    return True
                pause_ms(PAUSE_DURATION)

            pause_ms(PLACE_BACKOFF_BASE * attempt)

    return False
    try:
        land_id = Statics.GetLandID(x, y, game_map)
    except Exception:
        return False
    BAD_LAND_IDS = {0x0001}
    if land_id in BAD_LAND_IDS:
        return False
    return True

def build_center_layers(center_x, center_y, center_z):
    """Construct the central layers: cloth cracks, black pearl rings, plant bowl ring."""
    cloth_id = MATERIAL_ITEM_IDS.get("Cloth")
    PILLAR_BOWL_id = MATERIAL_ITEM_IDS.get("Plant Bowl")
    bp_list = MATERIAL_ITEM_IDS.get("Black Pearl", [])
    black_pearl_id = bp_list[0] if isinstance(bp_list, list) and bp_list else None
    eye_newt_list = MATERIAL_ITEM_IDS.get("Eye of Newt", [])
    eye_newt_id = eye_newt_list[0] if isinstance(eye_newt_list, list) and eye_newt_list else None

    # 1) Cloth cracks: multiple arms with varying lengths
    if ENABLE_CENTER_CRACKS and ENABLE_CENTER_CRACKS_CLOTH and cloth_id is not None:
        angles = [i * (360 // CENTER_CRACK_ARMS) for i in range(CENTER_CRACK_ARMS)]
        for a in angles:
            length = random.randint(CENTER_CRACK_MIN_LEN, CENTER_CRACK_MAX_LEN)
            # Main arm
            main_pts = generate_line_points(center_x, center_y, a, length, spacing=1)
            place_items_at_points(main_pts, cloth_id, center_z, "Center cloth cracks", center=(center_x, center_y), hue=DEFAULT_CLOTH_HUE)

            # Branches: probabilistic small offshoots from points along the main arm
            branches_made = 0
            if length >= (CENTER_CRACK_BRANCH_MIN_LEN + 1):
                for idx in range(1, max(1, len(main_pts) - 1)):
                    if branches_made >= CENTER_CRACK_MAX_BRANCHES_PER_ARM:
                        break
                    if random.random() > CENTER_CRACK_BRANCH_CHANCE:
                        continue
                    # Choose a side and angle offset
                    side = -1 if random.random() < 0.5 else 1
                    offset = random.randint(CENTER_CRACK_BRANCH_ANGLE_OFFSET_MIN, CENTER_CRACK_BRANCH_ANGLE_OFFSET_MAX) * side
                    branch_angle = (a + offset) % 360

                    # Branch length bounded by remaining main length at this point
                    remaining = max(1, length - idx)
                    max_len_here = max(1, min(CENTER_CRACK_BRANCH_MAX_LEN, remaining))
                    if max_len_here < CENTER_CRACK_BRANCH_MIN_LEN:
                        continue
                    branch_len = random.randint(CENTER_CRACK_BRANCH_MIN_LEN, max_len_here)

                    bx, by = main_pts[idx]
                    bpts = generate_line_points(bx, by, branch_angle, branch_len, spacing=1)
                    place_items_at_points(bpts, cloth_id, center_z, "Center cloth crack branch", center=(center_x, center_y), hue=DEFAULT_CLOTH_HUE)
                    branches_made += 1

    # 1a) Eye of Newt cracks: add a second branching layer for mystical effect
    if ENABLE_CENTER_CRACKS and ENABLE_CENTER_CRACKS_EYE_NEWT:
        if eye_newt_id is None and PREVIEW_MODE:
            eye_newt_id = get_non_orb_preview_item()
    if ENABLE_CENTER_CRACKS and ENABLE_CENTER_CRACKS_EYE_NEWT and eye_newt_id is not None:
        # Use fewer arms to interleave with cloth
        angles = [i * (360 // (CENTER_CRACK_ARMS // 2)) + 15 for i in range(max(1, CENTER_CRACK_ARMS // 2))]
        for a in angles:
            length = random.randint(max(2, CENTER_CRACK_MIN_LEN - 1), max(2, CENTER_CRACK_MIN_LEN + 2))
            main_pts = generate_line_points(center_x, center_y, a, length, spacing=1)
            place_items_at_points(main_pts, eye_newt_id, center_z, "Center newt cracks", center=(center_x, center_y), hue=0x0000)

            # Light branching for Eye of Newt cracks
            branches_made = 0
            if length >= 2:
                for idx in range(1, max(1, len(main_pts) - 1)):
                    if branches_made >= 1:
                        break
                    if random.random() > 0.35:
                        continue
                    side = -1 if random.random() < 0.5 else 1
                    offset = random.randint(CENTER_CRACK_BRANCH_ANGLE_OFFSET_MIN, CENTER_CRACK_BRANCH_ANGLE_OFFSET_MAX) * side
                    branch_angle = (a + offset) % 360
                    branch_len = random.randint(1, 2)
                    bx, by = main_pts[idx]
                    bpts = generate_line_points(bx, by, branch_angle, branch_len, spacing=1)
                    place_items_at_points(bpts, eye_newt_id, center_z, "Center newt crack branch", center=(center_x, center_y), hue=0x0000)
                    branches_made += 1

    # 1b) Black pearl cracks: extend further and stack more near center
    if ENABLE_CENTER_PEARL:
        if black_pearl_id is None and PREVIEW_MODE:
            black_pearl_id = get_non_orb_preview_item()
    if ENABLE_CENTER_PEARL and black_pearl_id is not None:
        angles = [i * (360 // PEARL_CRACK_ARMS) for i in range(PEARL_CRACK_ARMS)]
        for a in angles:
            length = random.randint(PEARL_CRACK_MIN_LEN, PEARL_CRACK_MAX_LEN)
            pts = generate_line_points(center_x, center_y, a, length, spacing=1)
            for (px, py) in pts:
                # Skip if coordinate is excluded
                if is_coordinate_excluded(px, py):
                    continue
                
                # Move player to location before placing stacks
                if not PREVIEW_MODE:
                    if not goto_location_with_wiggle(px, py, center=(center_x, center_y)):
                        debug_message(f"Could not reach black pearl crack position ({px}, {py})", 33)
                        continue
                
                # distance-weighted stacking: more stacks closer to center
                dist = math.hypot(px - center_x, py - center_y)
                # Smooth Gaussian-like falloff for nicer distribution
                try:
                    norm = dist / max(0.1, PEARL_STACK_FALLOFF)
                    stack_float = PEARL_STACK_MAX * math.exp(- (norm * norm) / max(0.1, PEARL_STACK_SIGMA))
                except Exception:
                    stack_float = max(1.0, float(PEARL_STACK_MAX))
                stacks = int(round(stack_float))
                # Organic variation, but bounded
                if random.random() < 0.15:
                    stacks += 1
                stacks = max(1, min(PEARL_STACK_MAX, stacks))
                for _ in range(stacks):
                    place_item(px, py, black_pearl_id, center_z, hue=0x0000)
                    if PREVIEW_MODE:
                        pause_ms(PEARL_STACK_PREVIEW_DELAY_MS)

    # 2) Black Pearl rings: concentric circles
    if ENABLE_CENTER_PEARL:
        ring_specs = list(zip(CENTER_PEARL_RING_RADII, CENTER_PEARL_RING_POINTS))
        for radius, points in ring_specs:
            item_id = black_pearl_id
            if item_id is None and PREVIEW_MODE:
                item_id = get_non_orb_preview_item()
            if item_id is not None:
                pts = generate_circle_points(center_x, center_y, radius, points, rotation=0)
                place_items_at_points(pts, item_id, center_z, "Center black pearl ring", center=(center_x, center_y), hue=0x0000)

    # 3) Plant bowl ring around center
    if ENABLE_CENTER_BOWL_RING and PILLAR_BOWL_id is not None:
        pts = generate_circle_points(center_x, center_y, CENTER_BOWL_RING_RADIUS, CENTER_BOWL_RING_POINTS, rotation=0)
        place_items_at_points(pts, PILLAR_BOWL_id, center_z, "Center plant bowl ring", center=(center_x, center_y))

def is_valid_position(x, y, z=None):
    if z is None:
        z = Player.Position.Z
    return (
        Player.Position.X - MAX_DISTANCE <= x <= Player.Position.X + MAX_DISTANCE
        and Player.Position.Y - MAX_DISTANCE <= y <= Player.Position.Y + MAX_DISTANCE
        and Statics.GetLandID(x, y, Player.Map) not in [0x0001]
    )

def place_item(x, y, item_id, z=None, hue=None):
    if item_id is None:
        return False
    # Compute base Z and apply GLOBAL_Z_OFFSET only in preview mode
    base_z = (z if z is not None else Player.Position.Z)
    if PREVIEW_MODE:
        z_prev = compute_target_z(x, y, base_z)
        z_show = z_prev + int(PREVIEW_Z_OFFSET)
        preview_item_at(x, y, z_show, item_id, hue if hue is not None else PREVIEW_DEFAULT_HUE)
        if ENABLE_STACK_TRACKING:
            PLACED_TOP_Z[(x, y)] = z_prev
        return True

    offsets = [(0, 0)] if SAFE_MODE else [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
    if z is None:
        z = Player.Position.Z

    debug_message(f"place_item: id=0x{item_id:X} at ({x},{y},{base_z}) hue={'0x%04X'%hue if hue is not None else 'none'} | offsets={offsets}", 68)
    for dx_off, dy_off in offsets:
        tx = x + dx_off
        ty = y + dy_off
        if not is_valid_position(tx, ty, z):
            debug_message(f"place_item: skip invalid pos ({tx},{ty},{z})", 68)
            continue
        if not is_safe_ground(tx, ty):
            BAD_COORDS.add((tx, ty))
            debug_message(f"place_item: skip unsafe ground ({tx},{ty})", 68)
            continue
        z_final = compute_target_z(tx, ty, base_z)
        for attempt in range(1, PLACE_MAX_RETRIES + 1):
            item = Items.FindByID(item_id, -1, Player.Backpack.Serial)
            if not item:
                debug_message(f"Could not find item 0x{item_id:X}", 33)
                return False

            try:
                initial_count = Items.BackpackCount(item_id, -1)
            except Exception as e:
                debug_message(f"BackpackCount error for 0x{item_id:X}: {e}", 33)
                return False
            if initial_count <= 0:
                return False

            try:
                if hue is not None:
                    # Hue application depends on server mechanics; many items have preset hues only.
                    # We still place the item; visual hue comes from item variant if applicable.
                    pass
                # Apply Z override if auto-stacking is enabled
                actual_z = -1 if USE_AUTO_Z_STACKING else z_final
                debug_message(f"place_item: MoveOnGround(serial={item.Serial}, amount=1, x={tx}, y={ty}, z={actual_z}) [calculated_z={z_final}]", 68)
                Items.MoveOnGround(item.Serial, 1, tx, ty, actual_z)
            except Exception as e:
                debug_message(f"MoveOnGround failed at ({tx},{ty}): {e}", 33)
                BAD_COORDS.add((x, y))
                pause_ms(PAUSE_DURATION + 150)
                return False
            else:
                throttle()
                pause_ms(PAUSE_DURATION_PLACE)

            verified = False
            for _ in range(2):
                try:
                    new_count = Items.BackpackCount(item_id, -1)
                except Exception as e:
                    debug_message(f"BackpackCount verify error: {e}", 33)
                    break
                if new_count < initial_count:
                    verified = True
                    break
                pause_ms(PAUSE_DURATION)

            if verified:
                if ENABLE_STACK_TRACKING:
                    PLACED_TOP_Z[(tx, ty)] = z_final
                return True
            else:
                debug_message(f"place_item: verification failed (count {initial_count} -> {new_count}) on attempt {attempt} at ({tx},{ty},{z_final})", 68)
                pause_ms(PLACE_BACKOFF_BASE * attempt)

    debug_message(f"place_item: exhausted offsets for id=0x{item_id:X} at ({x},{y},{base_z}); giving up", 33)
    return False

def place_items_at_points(points, item_id, z=None, progress_msg="Placing items", center=None, hue=None):
    if not points or item_id is None:
        return set()

    total = len(points)
    placed = set()
    failures = 0
    if item_id not in PLACED_COORDS_BY_ITEM:
        PLACED_COORDS_BY_ITEM[item_id] = set()

    for i, (x, y) in enumerate(points, 1):
        debug_message(f"{progress_msg}: {i} out of {total}", 67)

        start_ms = int(time.time() * 1000)

        if (x, y) in BAD_COORDS:
            debug_message(f"Skipping known-bad coord ({x},{y})", 33)
            continue

        if is_coordinate_excluded(x, y):
            debug_message(f"Skipping excluded coord ({x},{y})", 33)
            continue

        if (x, y) in PLACED_COORDS_BY_ITEM[item_id]:
            debug_message(f"Duplicate coords for 0x{item_id:X} at ({x},{y}), skipping.", 68)
            continue

        if not PREVIEW_MODE:
            if not goto_location_with_wiggle(x, y, center=center):
                debug_message(f"Could not reach position ({x}, {y})", 33)
                failures += 1
                if failures >= MAX_PHASE_FAILURES:
                    debug_message("Too many failures in this phase; aborting phase early.", 33)
                    break
                continue

        if place_item(x, y, item_id, z, hue=hue):
            placed.add((x, y))
            PLACED_COORDS_BY_ITEM[item_id].add((x, y))
        else:
            if PREVIEW_MODE:
                # In preview, a single send is enough; no retry/backpack logic
                pass
            else:
                pause_ms(PAUSE_DURATION)

            if int(time.time() * 1000) - start_ms > POINT_TIMEOUT_MS:
                debug_message(f"Timeout at point ({x},{y}), skipping.", 33)
                BAD_COORDS.add((x, y))
                failures += 1

        pause_ms(POINT_BREATHER_MS)

    return placed

def place_stack_items_at_points(points, item_id, per_point_amount, z=None, progress_msg="Placing stack items", center=None, hue=None):
    """Place stackable items as piles by repeating placements at the same coordinates.
    Falls back to single placement if per_point_amount <= 1.
    """
    try:
        amt = int(per_point_amount)
    except Exception:
        amt = 1
    if amt <= 1:
        return place_items_at_points(points, item_id, z, progress_msg, center=center, hue=hue)
    expanded = []
    for p in points:
        expanded.extend([p] * amt)
    return place_items_at_points(expanded, item_id, z, progress_msg, center=center, hue=hue)

def place_choice_stack_items_at_points(points, item_id, choices, z=None, progress_msg="Placing choice stacks", center=None, hue=None):
    """Place stackable items with a random amount per point picked from a discrete set (choices)."""
    try:
        opts = [int(c) for c in (choices or []) if int(c) >= 1]
    except Exception:
        opts = [1]
    if not opts:
        opts = [1]
    expanded = []
    for p in points:
        amt = random.choice(opts)
        if amt <= 1:
            expanded.append(p)
        else:
            expanded.extend([p] * amt)
    return place_items_at_points(expanded, item_id, z, progress_msg, center=center, hue=hue)

def place_gold_choice_stacks(points, choices, z=None, progress_msg="Placing gold stacks", center=None, hue=None):
    """Place Gold Coin stacks per point, choosing amount from choices each point.
    Bypasses duplicate-coordinate suppression so multiple placements can occur at the same tile.
    """
    item_id = GOLD_ITEM_ID
    if not points or item_id is None:
        return set()
    try:
        opts = [int(c) for c in (choices or []) if int(c) >= 1]
    except Exception:
        opts = [1]
    if not opts:
        opts = [1]
    placed = set()
    failures = 0
    if item_id not in PLACED_COORDS_BY_ITEM:
        PLACED_COORDS_BY_ITEM[item_id] = set()
    total = len(points)
    for i, (x, y) in enumerate(points, 1):
        debug_message(f"{progress_msg}: {i} out of {total}", 67)
        if (x, y) in BAD_COORDS:
            debug_message(f"Skipping known-bad coord ({x},{y})", 33)
            continue
        if is_coordinate_excluded(x, y):
            debug_message(f"Skipping excluded coord ({x},{y})", 33)
            continue
        # If already placed gold at this coord, skip to avoid double stacking across phases
        if (x, y) in PLACED_COORDS_BY_ITEM[item_id]:
            continue
        if not PREVIEW_MODE:
            if not goto_location_with_wiggle(x, y, center=center):
                failures += 1
                if failures >= MAX_PHASE_FAILURES:
                    debug_message("Too many failures in gold placement; aborting phase early.", 33)
                    break
                continue
        amt = random.choice(opts)
        success_any = place_item_amount(x, y, item_id, amt, z, hue=hue)
        if not success_any and not PREVIEW_MODE:
            pause_ms(PAUSE_DURATION)
        if success_any:
            placed.add((x, y))
            PLACED_COORDS_BY_ITEM[item_id].add((x, y))
        else:
            failures += 1
            if failures >= MAX_PHASE_FAILURES:
                debug_message("Too many failures in gold placement; aborting phase early.", 33)
                break
        pause_ms(POINT_BREATHER_MS)
    return placed

def place_variable_stack_items_at_points(points, item_id, min_amount, max_amount, z=None, progress_msg="Placing variable stacks", center=None, hue=None):
    """Place stackable items with a random amount per point in [min_amount, max_amount]."""
    try:
        mn = int(min_amount)
        mx = int(max_amount)
    except Exception:
        mn, mx = 1, 1
    if mn < 1:
        mn = 1
    if mx < mn:
        mx = mn
    expanded = []
    for p in points:
        amt = random.randint(mn, mx)
        if amt <= 1:
            expanded.append(p)
        else:
            expanded.extend([p] * amt)
    return place_items_at_points(expanded, item_id, z, progress_msg, center=center, hue=hue)

def place_random_items_at_points(points, item_ids, z=None, progress_msg="Placing random items", center=None, hue=None):
    """Place one random item from item_ids at each point.
    Respects availability in live mode; in preview mode, any non-None is allowed.
    """
    if not points or not item_ids:
        return set()
    # Normalize list and filter Nones for selection, but keep Nones if nothing else exists
    candidates = [iid for iid in (item_ids if isinstance(item_ids, list) else [item_ids]) if iid is not None]
    if not candidates:
        return set()

    placed = set()
    total = len(points)
    failures = 0
    for i, (x, y) in enumerate(points, 1):
        debug_message(f"{progress_msg}: {i} out of {total}", 67)
        if (x, y) in BAD_COORDS:
            debug_message(f"Skipping known-bad coord ({x},{y})", 33)
            continue
        if is_coordinate_excluded(x, y):
            debug_message(f"Skipping excluded coord ({x},{y})", 33)
            continue

        if not PREVIEW_MODE:
            if not goto_location_with_wiggle(x, y, center=center):
                failures += 1
                if failures >= MAX_PHASE_FAILURES:
                    debug_message("Too many failures in random placement; aborting phase early.", 33)
                    break
                continue

        # Choose an available item randomly
        choice = None
        try_order = list(candidates)
        random.shuffle(try_order)
        if PREVIEW_MODE:
            # In preview, any candidate works
            choice = try_order[0]
        else:
            for iid in try_order:
                try:
                    if Items.BackpackCount(iid, -1) > 0:
                        choice = iid
                        break
                except Exception:
                    continue
            if choice is None:
                # fallback to first candidate to still attempt
                choice = try_order[0]

        if choice is None:
            continue

        if place_item(x, y, choice, z, hue=hue):
            placed.add((x, y))
            if choice not in PLACED_COORDS_BY_ITEM:
                PLACED_COORDS_BY_ITEM[choice] = set()
            PLACED_COORDS_BY_ITEM[choice].add((x, y))
            # In preview mode, throttle random pool placement to avoid client overload
            if PREVIEW_MODE:
                pause_ms(PREVIEW_RANDOM_POOL_DELAY_MS)
        else:
            if not PREVIEW_MODE:
                pause_ms(PAUSE_DURATION)
    return placed

def generate_circle_points(center_x, center_y, radius, points, rotation=0):
    result = []
    for i in range(points):
        angle = math.radians(rotation + (360.0 * i / max(1, points)))
        x = center_x + int(radius * math.cos(angle))
        y = center_y + int(radius * math.sin(angle))
        result.append((x, y))
    return result

def generate_line_points(origin_x, origin_y, angle_deg, length, spacing=1):
    pts = []
    angle = math.radians(angle_deg)
    vx = math.cos(angle)
    vy = math.sin(angle)
    for i in range(1, length + 1):
        x = origin_x + int(round(vx * i * spacing))
        y = origin_y + int(round(vy * i * spacing))
        pts.append((x, y))
    return pts

def filter_points_outside_radius(points, center_xy, min_radius, forbidden=None):
    """Filter out points that lie within min_radius of center_xy or in forbidden set."""
    if not points:
        return []
    cx, cy = center_xy
    fset = set(forbidden) if forbidden else set()
    result = []
    for (x, y) in points:
        if (x, y) in fset:
            continue
        if math.hypot(x - cx, y - cy) < float(min_radius):
            continue
        result.append((x, y))
    return result

def remove_axis_aligned_points(points, center_xy):
    """Remove points that align exactly on the X or Y axis relative to center_xy.
    This helps reduce the boxy/cornered appearance on low-point rings.
    """
    if not points:
        return []
    cx, cy = center_xy
    result = []
    for (x, y) in points:
        if x == cx or y == cy:
            continue
        result.append((x, y))
    return result

def attempt_walk_toward(tx, ty, max_steps=6):
    last_pos = (Player.Position.X, Player.Position.Y)
    step_delay = GOTO_BASE_DELAY
    for step in range(max_steps):
        if (abs(Player.Position.X - tx) <= MAX_DISTANCE and
            abs(Player.Position.Y - ty) <= MAX_DISTANCE):
            return True
        try:
            base_dir = get_direction(Player.Position.X, Player.Position.Y, tx, ty)
        except Exception:
            base_dir = 0

        dirs = [base_dir, (base_dir+1)%8, (base_dir+7)%8]
        moved = False
        for d in dirs:
            for rep in range(WALK_REPEATS_PER_DIR):
                try:
                    throttle()
                    Player.Walk(dir_to_str(d))
                except Exception as e:
                    debug_message(f"Walk error dir {d}: {e}", 33)
                    break
                pause_ms(step_delay)
                cur_pos = (Player.Position.X, Player.Position.Y)
                if cur_pos != last_pos:
                    moved = True
                    last_pos = cur_pos
                    break
            if moved:
                break
        if not moved:
            step_delay = int(step_delay * 1.3) + 50
            pause_ms(step_delay)
    return (abs(Player.Position.X - tx) <= MAX_DISTANCE and
            abs(Player.Position.Y - ty) <= MAX_DISTANCE)

def goto_location_with_wiggle(x, y, max_retries=GOTO_MAX_RETRIES, center=None):
    target_x = int(float(x))
    target_y = int(float(y))

    if not is_safe_ground(target_x, target_y):
        return False

    if attempt_walk_toward(target_x, target_y, max_steps=8):
        return True

    if CENTER_BIAS_ENABLED and center is not None:
        cx, cy = int(center[0]), int(center[1])
        dxc = abs(Player.Position.X - cx)
        dyc = abs(Player.Position.Y - cy)
        if dxc > CENTER_NUDGE_DISTANCE or dyc > CENTER_NUDGE_DISTANCE:
            attempt_walk_toward(cx, cy, max_steps=CENTER_NUDGE_STEPS)
            if attempt_walk_toward(target_x, target_y, max_steps=6):
                return True

    return (abs(Player.Position.X - target_x) <= MAX_DISTANCE and
            abs(Player.Position.Y - target_y) <= MAX_DISTANCE)

# ===== Direction helpers =====
def get_direction(from_x, from_y, to_x, to_y):
    dx = to_x - from_x
    dy = to_y - from_y

    if dx == 0:
        if dy < 0:
            return 0  # North
        return 4      # South
    elif dy == 0:
        if dx > 0:
            return 2  # East
        return 6      # West
    elif dx > 0:
        if dy < 0:
            return 1  # Northeast
        return 3      # Southeast
    else:
        if dy < 0:
            return 7  # Northwest
        return 5      # Southwest

def dir_to_str(d):
    mapping = {
        0: "North",
        1: "Northeast",
        2: "East",
        3: "Southeast",
        4: "South",
        5: "Southwest",
        6: "West",
        7: "Northwest",
    }
    return mapping.get(int(d) % 8, "North")

# ===== Item utilities =====
def get_first_available_item_id(item_ids, required_count=1):
    if isinstance(item_ids, int) or item_ids is None:
        item_ids = [item_ids]
    for item_id in item_ids:
        if item_id is None:
            continue
        if Items.BackpackCount(item_id, -1) >= required_count:
            return item_id
    for item_id in item_ids:
        if item_id is not None:
            return item_id
    return None

def get_non_orb_preview_item():
    """Pick a non-orb item to visualize decorations in preview mode.
    Preference: black pearl -> plant bowl -> cloth -> candle -> dye tub.
    Returns an itemID or None.
    """
    try_order = [
        MATERIAL_ITEM_IDS.get("Black Pearl", [None])[0],
        # prefer colored gems to better preview themes
        *MATERIAL_ITEM_IDS.get("Amber", []),
        *MATERIAL_ITEM_IDS.get("Sapphire", []),
        *MATERIAL_ITEM_IDS.get("Amethyst", []),
        *MATERIAL_ITEM_IDS.get("Emerald", []),
        MATERIAL_ITEM_IDS.get("Cloth"),
        MATERIAL_ITEM_IDS.get("Candle"),
        MATERIAL_ITEM_IDS.get("Dye Tub"),
        MATERIAL_ITEM_IDS.get("Plant Bowl"),  # last resort
    ]
    for iid in try_order:
        if iid is not None:
            return iid
    return None

# ===== Decoration generators =====
def get_arrow_points(orb_x, orb_y, center_x, center_y, length, spacing, angle_offset=0, start_offset=0, direction="outward"):
    # Compute angle from center to orb, apply offset and optional direction flip
    base_angle = math.degrees(math.atan2(orb_y - center_y, orb_x - center_x))
    angle = base_angle + angle_offset
    if str(direction).lower() == "inward":
        angle = (angle + 180) % 360
    # Start exactly at the orb tile and step away in the intended direction.
    # Apply optional start_offset tiles first to avoid overlapping rings around the orb.
    ux = int(round(math.cos(math.radians(angle))))
    uy = int(round(math.sin(math.radians(angle))))
    steps = max(0, int(start_offset))
    start_x = orb_x + ux * steps
    start_y = orb_y + uy * steps
    return generate_line_points(start_x, start_y, angle, length, spacing)

def get_symbol_points(kind, origin_x, origin_y, scale=2):
    pts = []
    if kind == "triangle":
        angles = [90, 210, 330]
        for a in angles:
            x = origin_x + int(round(scale * math.cos(math.radians(a))))
            y = origin_y + int(round(scale * math.sin(math.radians(a))))
            pts.append((x, y))
    elif kind == "gear":
        # simple 6-spoke
        for a in range(0, 360, 60):
            x = origin_x + int(round(scale * math.cos(math.radians(a))))
            y = origin_y + int(round(scale * math.sin(math.radians(a))))
            pts.append((x, y))
    elif kind == "note":
        pts.extend([
            (origin_x, origin_y),
            (origin_x + 1, origin_y - 1),
            (origin_x + 2, origin_y - 2),
        ])
    elif kind == "rune":
        for a in [0, 45, 90, 135, 180, 225, 270, 315]:
            x = origin_x + int(round(scale * math.cos(math.radians(a))))
            y = origin_y + int(round(scale * math.sin(math.radians(a))))
            pts.append((x, y))
    else:
        pts.append((origin_x, origin_y))
    return pts

# ===== Orchestrators =====
def get_orb_ring_positions(center_x, center_y):
    # Determine rotation per strategy
    rotation = ORB_CIRCLE.get("rotation", 0)
    count = int(ORB_CIRCLE.get("count", 14))
    if ORB_ROTATION_STRATEGY == "fixed":
        rotation = FIXED_ROTATION_DEG
    elif ORB_ROTATION_STRATEGY == "half_step" and count > 0:
        rotation = (360.0 / count) / 2.0
    return generate_circle_points(center_x, center_y, ORB_CIRCLE["radius"], count, rotation)

def get_ordered_decorations(decorations):
    # Sort by radius/length/scale depending on type, using ORDER_SMALLEST_FIRST
    def key_fn(d):
        if d.get("type") == "ring":
            return (0, d.get("radius", 0))
        if d.get("type") == "arrow":
            return (1, d.get("length", 0))
        if d.get("type") == "symbol":
            return (2, d.get("scale", 0))
        return (3, 0)

    return sorted(decorations, key=key_fn, reverse=not ORDER_SMALLEST_FIRST)

def place_base_stack(x, y, base_cfg, center_z):
    cloth_id = MATERIAL_ITEM_IDS.get("Cloth")
    candle_id = MATERIAL_ITEM_IDS.get("Candle")
    # Always use the default dark gray cloth hue; ignore per-orb base hues
    cloth_hue = DEFAULT_CLOTH_HUE
    # Place cloth and candle minimally (used by older callers; main path uses build_pillar_at)
    if cloth_id is not None:
        place_item(x, y, cloth_id, center_z, hue=cloth_hue)
    if candle_id is not None:
        place_item(x, y, candle_id, center_z + STACK_TOP_EXTRA)
        if ENABLE_LIGHTING_ACTION and not PREVIEW_MODE:
            try:
                itm = Items.FindByID(candle_id, -1, Player.Backpack.Serial)
                if itm:
                    Items.UseItem(itm)
                    pause_ms(200)
            except Exception:
                pass
    # Dye tubs are no longer placed

def build_pillar_at(x, y, base_cfg, center_z):
    """Builds a pillar at (x,y): cloth -> N plant bowls -> lantern (toggle)
    Returns the Z height where the orb should be placed (top Z), or None on failure.
    """
    cloth_id = MATERIAL_ITEM_IDS.get("Cloth")
    PILLAR_BOWL_id = MATERIAL_ITEM_IDS.get("Plant Bowl")
    lantern_id = MATERIAL_ITEM_IDS.get("Lantern")
    # Always use the default dark gray cloth hue; ignore per-orb base hues
    cloth_hue = DEFAULT_CLOTH_HUE

    # 1) Base cloth (at ground level)
    z_cloth = center_z
    debug_message(f"Pillar: start at ({x},{y}) center_z={center_z} | ids: cloth=0x{(cloth_id or 0):X}, bowl=0x{(PILLAR_BOWL_id or 0):X}, lantern=0x{(lantern_id or 0):X}", 67)
    # Safety and availability diagnostics
    safe = is_safe_ground(x, y)
    try:
        cloth_count = Items.BackpackCount(cloth_id, -1) if cloth_id is not None else 0
    except Exception:
        cloth_count = -1
    try:
        bowl_need = max(0, int(PILLAR_BOWL_STACK_COUNT))
        bowl_count = Items.BackpackCount(PILLAR_BOWL_id, -1) if PILLAR_BOWL_id is not None else 0
    except Exception:
        bowl_count = -1
    try:
        lantern_count = Items.BackpackCount(lantern_id, -1) if lantern_id is not None else 0
    except Exception:
        lantern_count = -1
    debug_message(f"Pillar: safe_ground={safe} | counts: cloth={cloth_count}, bowls_have={bowl_count}/need={bowl_need}, lantern={lantern_count}", 67)
    if not safe:
        debug_message(f"Pillar abort: unsafe ground at ({x},{y})", 33)
        return None
    # Ensure we're close enough to place on this tile
    if not PREVIEW_MODE:
        if not goto_location_with_wiggle(x, y):
            debug_message(f"Pillar abort: cannot reach ({x},{y}) before placement", 33)
            return None
    if cloth_id is not None:
        z_cloth_final = compute_target_z(x, y, z_cloth)
        debug_message(f"Pillar: placing cloth 0x{cloth_id:X} at ({x},{y}) proposed_z={z_cloth} -> final_z={z_cloth_final} hue=0x{cloth_hue:04X}", 67)
        if not place_item(x, y, cloth_id, z_cloth, hue=cloth_hue):
            debug_message(f"Pillar fail: cloth 0x{cloth_id:X} at ({x},{y},{z_cloth})", 33)
            return None

    # 2) Stack plant bowls, each one step above previous
    top_after_bowls_z = z_cloth
    if PILLAR_BOWL_id is not None and PILLAR_BOWL_STACK_COUNT > 0:
        for i in range(PILLAR_BOWL_STACK_COUNT):
            z_bowl = z_cloth + (i + 1) * STACK_Z_STEP
            z_bowl_final = compute_target_z(x, y, z_bowl)
            debug_message(f"Pillar: placing bowl {i+1}/{PILLAR_BOWL_STACK_COUNT} id=0x{PILLAR_BOWL_id:X} at ({x},{y}) proposed_z={z_bowl} -> final_z={z_bowl_final}", 67)
            if not place_item(x, y, PILLAR_BOWL_id, z_bowl):
                debug_message(f"Pillar fail: bowl {i+1}/{PILLAR_BOWL_STACK_COUNT} id=0x{PILLAR_BOWL_id:X} at ({x},{y},{z_bowl})", 33)
                return None
            top_after_bowls_z = z_bowl_final

    # 3) Place lantern on top of bowls
    lantern_z = top_after_bowls_z + STACK_TOP_EXTRA
    if lantern_id is not None:
        lantern_z_final = compute_target_z(x, y, lantern_z)
        debug_message(f"Pillar: placing lantern 0x{lantern_id:X} at ({x},{y}) proposed_z={lantern_z} -> final_z={lantern_z_final}", 67)
        if not place_item(x, y, lantern_id, lantern_z):
            debug_message(f"Pillar fail: lantern 0x{lantern_id:X} at ({x},{y},{lantern_z})", 33)
            return None
        if ENABLE_LIGHTING_ACTION and not PREVIEW_MODE:
            try:
                itm = Items.FindByID(lantern_id, -1, Player.Backpack.Serial)
                if itm:
                    Items.UseItem(itm)
                    pause_ms(200)
            except Exception:
                pass

    # 4) Compute top Z for orb (sits above lantern)
    orb_top_z = lantern_z_final + STACK_TOP_EXTRA
    debug_message(f"Pillar: computed orb_top_z={orb_top_z} (lantern_z_final={lantern_z_final} + STACK_TOP_EXTRA={STACK_TOP_EXTRA})", 67)
    return orb_top_z

def place_orb(x, y, orb_hue, center_z, z_override=None):
    """Place the shared orb item at (x,y) with the provided hue."""
    item_id = ORB_ITEM_ID
    if item_id is None:
        debug_message("Orb item ID not configured.", 33)
        return False
    z_final = z_override if z_override is not None else center_z
    return place_item(x, y, item_id, z_final, hue=orb_hue)

def place_decorations_for_orb(orb_idx, orb_pos, center, definition, center_z):
    cx, cy = center
    ox, oy = orb_pos
    # Use only explicitly defined decorations. No defaults or fallbacks.
    decos = list(definition.get("decorations", []))

    # Respect global decoration toggle and whitelist
    if not ENABLE_ORB_DECORATIONS:
        debug_message("Orb decorations disabled by toggle.", 68)
        return
    try:
        allowed = set(_normalize_orb_key(k) for k in ORB_KEYS_ALLOWED)
    except Exception:
        allowed = set()
    orb_key_norm = _normalize_orb_key(definition.get("key", ""))
    if allowed and orb_key_norm not in allowed:
        debug_message(f"Skipping decorations for orb '{orb_key_norm}' (not whitelisted).", 68)
        return

    for deco in get_ordered_decorations(decos):
        typ = deco.get("type")
        # Resolve item candidates from either explicit item_ids or a named random_pool
        item_ids = deco.get("item_ids")
        pool_name = deco.get("random_pool")
        if not item_ids and pool_name:
            item_ids = RANDOM_POOLS.get(str(pool_name).lower())
        # Require explicit item_ids and at least one non-None id
        if not item_ids:
            debug_message(f"Orb {definition.get('key')}: decoration '{typ}' skipped (no item_ids).", 33)
            continue
        if isinstance(item_ids, list):
            candidates = [iid for iid in item_ids if iid is not None]
        else:
            candidates = [item_ids] if item_ids is not None else []
        if not candidates:
            debug_message(f"Orb {definition.get('key')}: decoration '{typ}' skipped (item_ids contain only None).", 33)
            continue
        item_id = get_first_available_item_id(candidates, 1)
        if item_id is None and not deco.get("randomize", False):
            debug_message(f"Orb {definition.get('key')}: decoration '{typ}' skipped (no available items).", 33)
            continue
        if typ == "ring":
            points = generate_circle_points(ox, oy, deco.get("radius", 2), deco.get("points", 6), deco.get("rotation", 0))
            points = filter_points_outside_radius(points, (cx, cy), ORB_CENTER_EXCLUSION_RADIUS, forbidden={(ox, oy)})
            # Smoothing: remove axis-aligned points for the outer ring (larger radius) to reduce corners
            if int(deco.get("radius", 0)) == int(MIDDLE_RING_RADIUS):
                points = remove_axis_aligned_points(points, (ox, oy))
            if not points:
                continue
            if deco.get("randomize", False):
                place_random_items_at_points(points, candidates, center_z, f"Decor ring for {definition.get('key')}", center=center, hue=deco.get('hue', 0x0000))
            else:
                # Gold-specific amounts; others place exactly 1
                if item_id == GOLD_ITEM_ID:
                    place_gold_choice_stacks(points, GOLD_STACK_AMOUNTS, center_z, f"Decor ring for {definition.get('key')}", center=center, hue=deco.get('hue', 0x0000))
                else:
                    place_items_at_points(points, item_id, center_z, f"Decor ring for {definition.get('key')}", center=center, hue=deco.get('hue', 0x0000))
        elif typ == "arrow":
            pts = get_arrow_points(ox, oy, cx, cy, deco.get("length", 3), deco.get("spacing", 1), deco.get("angle_offset", 0), deco.get("start_offset", 0), deco.get("direction", "outward"))
            # Exclude points too close to center and the orb tile
            pts = filter_points_outside_radius(pts, (cx, cy), ORB_CENTER_EXCLUSION_RADIUS, forbidden={(ox, oy)})
            if not pts:
                continue
            if deco.get("randomize", False):
                place_random_items_at_points(pts, candidates, center_z, f"Decor arrow for {definition.get('key')}", center=center, hue=deco.get('hue', 0x0000))
            else:
                if item_id == GOLD_ITEM_ID:
                    place_gold_choice_stacks(pts, GOLD_STACK_AMOUNTS, center_z, f"Decor arrow for {definition.get('key')}", center=center, hue=deco.get('hue', 0x0000))
                else:
                    place_items_at_points(pts, item_id, center_z, f"Decor arrow for {definition.get('key')}", center=center, hue=deco.get('hue', 0x0000))
        elif typ == "symbol":
            sym_pts = get_symbol_points(deco.get("pattern", "rune"), ox, oy, deco.get("scale", 2))
            # Exclude points too close to center and the orb tile
            sym_pts = filter_points_outside_radius(sym_pts, (cx, cy), ORB_CENTER_EXCLUSION_RADIUS, forbidden={(ox, oy)})
            if not sym_pts:
                continue
            if deco.get("randomize", False):
                place_random_items_at_points(sym_pts, candidates, center_z, f"Decor symbol for {definition.get('key')}", center=center, hue=deco.get('hue', 0x0000))
            else:
                if item_id == GOLD_ITEM_ID:
                    place_gold_choice_stacks(sym_pts, GOLD_STACK_AMOUNTS, center_z, f"Decor symbol for {definition.get('key')}", center=center, hue=deco.get('hue', 0x0000))
                else:
                    place_items_at_points(sym_pts, item_id, center_z, f"Decor symbol for {definition.get('key')}", center=center, hue=deco.get('hue', 0x0000))
        elif typ == "center_line":
            # Draw a line from center to orb position
            angle_deg = math.degrees(math.atan2(oy - cy, ox - cx))
            length = max(1, int(round(math.hypot(ox - cx, oy - cy))))
            line_pts = generate_line_points(cx, cy, angle_deg, length, spacing=LINE_SPACING)
            # Exclude points too close to center and the orb tile
            line_pts = filter_points_outside_radius(line_pts, (cx, cy), ORB_CENTER_EXCLUSION_RADIUS, forbidden={(ox, oy)})
            if not line_pts:
                continue
            if deco.get("randomize", False):
                place_random_items_at_points(line_pts, candidates, center_z, f"Decor line for {definition.get('key')}", center=center, hue=deco.get('hue', 0x0000))
            else:
                if item_id == GOLD_ITEM_ID:
                    place_gold_choice_stacks(line_pts, GOLD_STACK_AMOUNTS, center_z, f"Decor line for {definition.get('key')}", center=center, hue=deco.get('hue', 0x0000))
                else:
                    place_items_at_points(line_pts, item_id, center_z, f"Decor line for {definition.get('key')}", center=center, hue=deco.get('hue', 0x0000))
        elif typ == "line":
            # Short radial line from near the orb; supports direction and start offset for fine placement
            pts = get_arrow_points(
                ox, oy, cx, cy,
                deco.get("length", 4),
                deco.get("spacing", 1),
                deco.get("angle_offset", 0),
                # Default to 2 so we skip the inner ring around the orb tile
                deco.get("start_offset", 2),
                # Default lines to point inward toward the center
                deco.get("direction", "inward"),
            )
            pts = filter_points_outside_radius(pts, (cx, cy), ORB_CENTER_EXCLUSION_RADIUS, forbidden={(ox, oy)})
            if not pts:
                continue
            if item_id == GOLD_ITEM_ID:
                place_gold_choice_stacks(pts, GOLD_STACK_AMOUNTS, center_z, f"Decor line for {definition.get('key')}", center=center, hue=deco.get('hue', 0x0000))
            else:
                place_items_at_points(pts, item_id, center_z, f"Decor line for {definition.get('key')}", center=center, hue=deco.get('hue', 0x0000))

def display_configuration():
    debug_message("Ritual of Orbs configuration:", 67)
    debug_message(f"Preview: {'ON' if PREVIEW_MODE else 'OFF'}; Order smallest first: {ORDER_SMALLEST_FIRST}", 67)
    debug_message(f"Orb ring radius {ORB_CIRCLE['radius']}, rotation {ORB_CIRCLE['rotation']}", 67)
    debug_message(f"Global Z offset: {PREVIEW_Z_OFFSET}", 67)
    # Show toggle states
    debug_message(f"Center: cracks={'ON' if ENABLE_CENTER_CRACKS else 'OFF'}, pearls={'ON' if ENABLE_CENTER_PEARL else 'OFF'}, bowl_ring={'ON' if ENABLE_CENTER_BOWL_RING else 'OFF'}", 67)
    debug_message(f"Orbs: place={'ON' if ENABLE_ORBS else 'OFF'}, decorations={'ON' if ENABLE_ORB_DECORATIONS else 'OFF'}", 67)
    if ORB_KEYS_ALLOWED:
        try:
            wl = ", ".join(sorted(set(_normalize_orb_key(k) for k in ORB_KEYS_ALLOWED)))
        except Exception:
            wl = ", ".join(str(k) for k in ORB_KEYS_ALLOWED)
        debug_message(f"Whitelist: {wl}", 67)
    effective_defs = get_ordered_orb_definitions()
    # Show effective order (index -> key)
    for idx, d in enumerate(effective_defs):
        k = d.get("key", "?")
        debug_message(f"{idx:02d}: {k} orb", 68)

def calculate_ritual_requirements():
    """Calculate total item requirements for the ritual and output to JSON file"""
    import json
    import sys
    from datetime import datetime
    
    requirements = {}
    
    # Helper function to add items to requirements
    def add_item_requirement(item_name, item_ids, count):
        if isinstance(item_ids, list):
            # Use first ID if multiple variants exist
            item_id = item_ids[0]
        else:
            item_id = item_ids
            
        if item_name in requirements:
            requirements[item_name]["amount"] += count
        else:
            requirements[item_name] = {
                "name": item_name,
                "id": hex(item_id),
                "amount": count
            }
    
    # Calculate center layer requirements
    if ENABLE_CENTER_CRACKS:
        if ENABLE_CENTER_CRACKS_CLOTH:
            # Cloth cracks - estimate based on arms and length
            cloth_count = CENTER_CRACK_ARMS * ((CENTER_CRACK_MIN_LEN + CENTER_CRACK_MAX_LEN) // 2)
            # Add branching estimate
            branch_estimate = int(cloth_count * CENTER_CRACK_BRANCH_CHANCE * CENTER_CRACK_MAX_BRANCHES_PER_ARM)
            cloth_count += branch_estimate
            add_item_requirement("Cloth", MATERIAL_ITEM_IDS["Cloth"], cloth_count)
            
        if ENABLE_CENTER_CRACKS_EYE_NEWT:
            # Eye of Newt cracks - similar calculation
            newt_count = CENTER_CRACK_ARMS * ((CENTER_CRACK_MIN_LEN + CENTER_CRACK_MAX_LEN) // 2)
            branch_estimate = int(newt_count * CENTER_CRACK_BRANCH_CHANCE * CENTER_CRACK_MAX_BRANCHES_PER_ARM)
            newt_count += branch_estimate
            add_item_requirement("Eye of Newt", MATERIAL_ITEM_IDS["Eye of Newt"], newt_count)
    
    if ENABLE_CENTER_PEARL:
        # Black Pearl rings
        for i, radius in enumerate(CENTER_PEARL_RING_RADII):
            points = CENTER_PEARL_RING_POINTS[i] if i < len(CENTER_PEARL_RING_POINTS) else CENTER_PEARL_RING_POINTS[-1]
            add_item_requirement("Black Pearl", MATERIAL_ITEM_IDS["Black Pearl"], points)
        
        # Black Pearl cracks with stacking
        pearl_crack_count = PEARL_CRACK_ARMS * ((PEARL_CRACK_MIN_LEN + PEARL_CRACK_MAX_LEN) // 2)
        # Estimate stacking multiplier based on center stacking
        stack_multiplier = (PEARL_STACK_MAX + 1) // 2  # Average stacking
        pearl_crack_count *= stack_multiplier
        add_item_requirement("Black Pearl", MATERIAL_ITEM_IDS["Black Pearl"], pearl_crack_count)
    
    if ENABLE_CENTER_BOWL_RING:
        add_item_requirement("Plant Bowl", MATERIAL_ITEM_IDS["Plant Bowl"], CENTER_BOWL_RING_POINTS)
    
    # Calculate orb requirements
    if ENABLE_ORBS or ENABLE_ORB_DECORATIONS:
        definitions = get_ordered_orb_definitions()
        
        # Apply whitelist filtering
        try:
            allowed = set(_normalize_orb_key(k) for k in ORB_KEYS_ALLOWED)
        except Exception:
            allowed = set()
        if allowed:
            definitions = [d for d in definitions if _normalize_orb_key(d.get("key", "")) in allowed]
        
        orb_count = min(ORB_CIRCLE.get("count", len(definitions)), len(definitions))
        
        if ENABLE_ORBS:
            # Pillar base items per orb
            add_item_requirement("Cloth", MATERIAL_ITEM_IDS["Cloth"], orb_count)  # Base cloth
            add_item_requirement("Plant Bowl", MATERIAL_ITEM_IDS["Plant Bowl"], orb_count * PILLAR_BOWL_STACK_COUNT)  # Stacked bowls
            add_item_requirement("Lantern", MATERIAL_ITEM_IDS["Lantern"], orb_count)  # Top lantern
            
            # Orbs themselves
            add_item_requirement("Orb", ORB_ITEM_ID, orb_count)
        
        if ENABLE_ORB_DECORATIONS:
            # Process each orb's decorations
            for i in range(orb_count):
                definition = definitions[i] if i < len(definitions) else definitions[-1]
                decorations = definition.get("decorations", [])
                
                for decoration in decorations:
                    dec_type = decoration.get("type", "")
                    
                    if dec_type == "ring":
                        points = decoration.get("points", RING_POINTS)
                        item_ids_key = None
                        
                        # Find item IDs
                        if "item_ids" in decoration:
                            # Direct item reference
                            for material_name, material_ids in MATERIAL_ITEM_IDS.items():
                                if decoration["item_ids"] == material_ids:
                                    item_ids_key = material_name
                                    break
                            if item_ids_key:
                                add_item_requirement(item_ids_key, decoration["item_ids"], points)
                        
                        elif "random_pool" in decoration:
                            # Random pool - estimate based on pool size
                            pool_name = decoration["random_pool"]
                            if pool_name == "tools":
                                add_item_requirement("Tools (Random)", 0x0000, points)  # Placeholder
                            elif pool_name == "shields":
                                add_item_requirement("Shields (Random)", 0x0000, points)  # Placeholder
                            elif pool_name == "instruments":
                                add_item_requirement("Instruments (Random)", 0x0000, points)  # Placeholder
                    
                    elif dec_type in ["symbol", "line"]:
                        # Symbols and lines - estimate based on scale/length
                        count = 1
                        if dec_type == "symbol":
                            scale = decoration.get("scale", 1)
                            count = scale * scale  # Rough estimate
                        elif dec_type == "line":
                            count = decoration.get("length", 1)
                        
                        # Find item IDs
                        if "item_ids" in decoration:
                            for material_name, material_ids in MATERIAL_ITEM_IDS.items():
                                if decoration["item_ids"] == material_ids:
                                    add_item_requirement(material_name, decoration["item_ids"], count)
                                    break
    
    # Convert to list and sort by name
    requirements_list = list(requirements.values())
    requirements_list.sort(key=lambda x: x["name"])
    
    # Create output data
    output_data = {
        "generated_at": datetime.now().isoformat(),
        "ritual_configuration": {
            "enable_center_cracks": ENABLE_CENTER_CRACKS,
            "enable_center_cracks_cloth": ENABLE_CENTER_CRACKS_CLOTH,
            "enable_center_cracks_eye_newt": ENABLE_CENTER_CRACKS_EYE_NEWT,
            "enable_center_pearl": ENABLE_CENTER_PEARL,
            "enable_center_bowl_ring": ENABLE_CENTER_BOWL_RING,
            "enable_orbs": ENABLE_ORBS,
            "enable_orb_decorations": ENABLE_ORB_DECORATIONS,
            "orb_count": orb_count if (ENABLE_ORBS or ENABLE_ORB_DECORATIONS) else 0,
            "orb_keys_allowed": ORB_KEYS_ALLOWED if ORB_KEYS_ALLOWED else "all"
        },
        "total_items": len(requirements_list),
        "requirements": requirements_list
    }
    
    # Write to JSON file
    filename = "ritual_requirements.json"
    try:
        with open(filename, 'w') as f:
            json.dump(output_data, f, indent=2)
        debug_message(f"Ritual requirements saved to {filename}", 68)
        debug_message(f"Total unique items needed: {len(requirements_list)}", 67)
        
        # Display summary
        total_items = sum(item["amount"] for item in requirements_list)
        debug_message(f"Total individual items: {total_items}", 67)
        
        return requirements_list
    except Exception as e:
        debug_message(f"Error saving requirements: {str(e)}", 33)
        return None

def create_arrangement(center_x, center_y):
    debug_message("Beginning orb ritual arrangement...", 67)

    center_z = Player.Position.Z

    if not PREVIEW_MODE:
        if not goto_location_with_wiggle(center_x, center_y, center=(center_x, center_y)):
            debug_message("Could not reach center position!", 33)
            return

    # Build center layers first (cracked cloth, pearl rings, plant bowl ring)
    build_center_layers(center_x, center_y, center_z)

    positions = get_orb_ring_positions(center_x, center_y)
    definitions = get_ordered_orb_definitions()

    # Apply whitelist filtering if provided
    try:
        allowed = set(_normalize_orb_key(k) for k in ORB_KEYS_ALLOWED)
    except Exception:
        allowed = set()
    if allowed:
        definitions = [d for d in definitions if _normalize_orb_key(d.get("key", "")) in allowed]

    # Ensure exactly count per available slots and definitions
    count = min(len(positions), len(definitions))

    for idx in range(count):
        ox, oy = positions[idx]
        definition = definitions[idx]

        top_z = None
        if ENABLE_ORBS:
            # Build pillar (cloth -> stacked plant bowls -> lantern) and get top Z
            top_z = build_pillar_at(ox, oy, definition.get("base", {}), center_z)
            if top_z is None:
                debug_message(f"Skipping orb at ({ox},{oy}) due to pillar failure", 33)
                # Even if pillar failed, we may still place decorations if enabled
                if ENABLE_ORB_DECORATIONS:
                    place_decorations_for_orb(idx, (ox, oy), (center_x, center_y), definition, center_z)
                continue

            # Place orb on top of lantern/pillar
            placed_orb = place_orb(ox, oy, definition.get("orb_hue"), center_z, z_override=top_z)
            debug_message(f"{'Placed' if placed_orb else 'Skipped'} orb for {definition.get('key')}", 68 if placed_orb else 33)
        else:
            debug_message("Orb placement disabled by toggle; skipping pillars/orbs.", 68)

        # Decorations per orb (may occur even if orbs are disabled)
        if ENABLE_ORB_DECORATIONS:
            place_decorations_for_orb(idx, (ox, oy), (center_x, center_y), definition, center_z)

    debug_message("Orb ritual arrangement complete!", 67)

def generate_requirements():
    """Standalone function to generate ritual requirements"""
    calculate_ritual_requirements()

def main():
    import sys
    display_configuration()
    
    # Check if user wants to calculate requirements only
    if len(sys.argv) > 1 and sys.argv[1].lower() == "requirements":
        debug_message("Calculating ritual requirements...", 67)
        calculate_ritual_requirements()
        return
    
    center_x = Player.Position.X
    center_y = Player.Position.Y
    
    # Initialize exclusion zone around center
    initialize_exclusion_zone(center_x, center_y)
    create_arrangement(center_x, center_y)

if __name__ == "__main__":
    main()