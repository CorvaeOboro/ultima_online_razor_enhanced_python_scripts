"""
UI Boss Health Bar - a Razor Enhanced Python Script for Ultima Online

display the health bar for known bosses when nearby , a custom gump top center that is otherwise hidden
an arpg style big red boss enemy health bar , phase markers , side image embellishments 
optionally opens classic uo healthbar and attack boss onsight 
                ___.o.____
  ..o\<{|[   |  Boss Name   |   ]|}>\o..  

TODO:
- boss specific color tint presets ( red default , darkness purple , poison green , grey )

HOTKEY:: AutoStart on Login
VERSION:: 20250918
"""

import time
import random

DEBUG_MODE = False # Debug toggle , sends messages
# SETTINGS 
GET_CUO_HEALTHBAR = True  # If True, attempt to use CUO.OpenMobileHealthBar() to open the bosses in game healthbar 
AUTO_ATTACK_NEW_BOSSES = False  # If True, auto-attack a boss the first time it's detected
SHOW_PHASE_MARKERS = True # thirds
SHOW_HEALTH_NUMBERS = False # not useful , most health is diplayed out of 25
# GUMP images toggle
SIDE_IMAGES_ENABLED = True
FLOURISH_ARROWS_ENABLED = True
TOP_CENTER_IMAGE_ENABLED = True

# TESTING MODE: apply a random boss title to normal creatures for visualization testing
TESTING_FAKE_BOSS_MODE = False
TESTING_TARGET_NAMES = {"a harpy", "a giant rat"}
USE_SIMPLE_TITLES = False  # When True, prefer display_simple over decorated display
TESTING_FAKE_BOSS_RENAME_MS = 8000 # In testing mode, how often to rotate the randomized title for a target (milliseconds)

# Name rendering
# Use classic label-based rendering with black outline for readability

def simplify_title(title: str) -> str:
    """Return a simplified display title by stripping decorative ASCII, keeping letters, digits, spaces and common punctuation."""
    try:
        # Keep alphanumerics, space, apostrophe, hyphen, comma, period
        return ''.join(ch for ch in title if ch.isalnum() or ch in " '-.,").strip()
    except Exception:
        return title

# Cleaner input dictionaries (base -> display). Keep inline comments next to entries.
KNOWN_BOSSES_UO_TITLES = {
    "abyssal infernal": "¸¸·¯·¸¸·¯· Abyssal Infernal ·¯·¸¸·¯·¸¸",  # fiery abyss,  flourish of chaos
    "abyssmal horror": "◈═╡ Abyssmal Horror ╞═◈",  # jagged abyssal 
    "anon": "¤º°`°º¤ Anon ¤º°`°º¤",  # mysterious,  
    "barracoon the piper": "¸¸♬·¯·♪ Barracoon the Piper ♪·¯·♬¸¸",  # bardic musical energy
    "barracoon": "¸„.-•~¹°”ˆ Barracoon ˜”°¹~•-.„.",  # already styled, bard ratman, music
    "bone daemon": "☠══✦ Bone Daemon ✦══☠",  # skeletal, infernal
    "charybdis": "~~¤( Charybdis )¤~~",  # oceanic whirlpool # good
    "chief paroxysmus": "۞¤ø„¸ Chief Paroxysmus ¸„ø¤۞",  # grotesque swelling plague 
    "cora the sorceress": "✧*:･ﾟ✧ Cora the Sorceress ✧･ﾟ:*✧",  # mystical arcane 
    "corgul the soulbinder": "☯═══ Corgul the Soulbinder ═══☯",  # binding duality 
    "dark father": "††† Dark Father †††",  # gothic,  crosses
    "darknight creeper": "⋆✢ Darknight Creeper ✢⋆",  # shadowed spark  
    "dragon turtle": "≋≋≋ Dragon Turtle ≋≋≋",  # waves, sea beast 
    "dread horn": "↯↯ Dread Horn ↯↯",  # thunderous primal force
    "drelgor the impaler": "══╬ Drelgor the Impaler ╬══",  # brutal, spear
    "exodus": "✦°°✦ Exodus ✦°°✦",  # divine radiance
    #"fleshrenderer": "Fleshrenderer", # removed as this is sometimes a standard creature on custom shard
    "ilhenir the stained": ".-^-.-^-.- Ilhenir the Stained -.-^-.-^-.-.",  # corrupted, 
    "impaler": "══╬ Impaler ╬══",  # spear
    "juo'nar": "-=†=- Juo'nar -=†=-",  # dark knight, necrotic cross
    "khal ankur": "~=~ Khal Ankur ~=~",  # desertmystic sands
    "lady melisande": "°º¤ø¤º°` Lady Melisande ´°º¤ø¤º°",  # ornate  
    "lord oaks": "~~~ Lord Oaks ~~~",  # angel, natural, forest druid 
    "medusa": "<<< Medusa >>>",  # piercing gaze
    "mephitis": "-·=» Mephitis «=·-",  # venomous sting
    "meraktus the tormented": "==[ Meraktus the Tormented ]==",  # chained   
    "moltrog the void seer": "~*~ Moltrog the Void Seer ~*~",  #  void shimmer
    "monstrous interred grizzle": "-=¤=- Monstrous Interred Grizzle -=¤=-",  # tomb and burial 
    "navrey night-eyes": "°-( Navrey Night-Eyes )-°",  # spiderweb trap, enclosing
    "neira the necromancer": "+†+ Neira the Necromancer +†+",  # gothic necromancy
    "osiredon the scalis enforcer": "-<><>- Osiredon the Scalis Enforcer -<><>-",  # ocean  and 
    "ozymandias": "—=≡ Ozymandias ≡=—",  # ancient monolith,  
    #"primeval lich": "Primeval Lich", # removed as this is sometimes a standard creature on custom shard
    "rikktor": "==={ Rikktor }===",  # earthshaking  
    "semidar": "─ +† Semidar †+ ─",  # succubus
    #"shadow knight": "Shadow Knight", # removed as this is sometimes a standard creature on custom shard
    "shadowlords": "--= Shadowlords =--",  #  darkness
    "shanty the pirate": "~-=-~ Shanty the Pirate ~-=-~",  # waves 
    "shimmering effusion": "*~*~ Shimmering Effusion ~*~*",  # radiant magical shimmer
    "silvani": "~*~ Silvani ~*~",  #  forest nature fae # good
    "slasher of veils": "-=\\ Slasher of Veils /=-",  #  jagged cuts
    "stygian dragon": "<<< Stygian Dragon >>>",  # abyssal wings
    "the harrower": "+-- The Harrower --+",  #  ominous ritual
    "travesty": "=-[ Travesty ]- =",  # fae
    "twaulo of the glade": "~~~ Twaulo of the Glade ~~~",  # forest
    "virtuebane": "++= Virtuebane =++",  # blasphem
    "vorothal the mindflayer": "-{ Vorothal the Mindflayer }-",  # psychic grasp
    "zipactriotl": "==< Zipactriotl >==",  # ancient 
}

KNOWN_BOSSES_CUSTOM_TITLES = {
    "ixir": "-= Ixir =-",
    "goliath": "===[ Goliath ]===",
    "yog-sothoth": "-< YOG-SOTHOTH >-",
    "skeleton king": "+++ Skeleton King +++",
    "bog king": "~~~ Bog King ~~~",
    "celestus": "*=* Celestus *=*", #good
    "gargantua": "-= Gargantua =-",
    "gorgon": ">>> Gorgon <<<", # demon
    "norg": "== Norg ==", # giant
    "malcanthet": "-+- Malcanthet -+-", 
    "surgat": "=== Surgat ===", 
    "eligor": "-=| Eligor |=-", # wizard 
    "the undying": "+-- The Undying --+", 
    "lord of darkness": "=== Lord of Darkness ===", 
    "sandstorm templar": "-= Sandstorm Templar =-", 
    "a dread horn": "-> A Dread Horn <-", # miniboss in sandstorm
    "an abomination": "==[ An Abomination ]==", # miniboss in sandstorm
    "a flesh devourer": "-= IT THAT DEVOURS =-", # miniboss in wrong
    "paradigm": "-<>- Paradigm -<>-", # dragon electric 
    "a frozen ancestor": "*~ A Frozen Ancestor ~*", #boss
    "sergutthy": "-= Sergutthy =-", # mini boss
    "a stygian drakeling": "-< A Stygian Drakeling >-", # mini boss
    "molten wyvern": ">> Molten Wyvern <<", #boss
    "tharnok": "== Tharnok ==", #boss
    "a swamp abomination": "~~ A Swamp Abomination ~~", #boss
    "abysmal balron": "-= Abysmal Balron =-", #boss
    "glassyalabolas": "-*- Glassyalabolas -*-", # mini boss
}

# Now generate structured dictionaries from the clean input, adding display_simple automatically
KNOWN_BOSSES_UO = {
    base: {
        'display': display,
        'display_simple': simplify_title(display),
        'comment': ''
    }
    for base, display in KNOWN_BOSSES_UO_TITLES.items()
}

KNOWN_BOSSES_CUSTOM = {
    base: {
        'display': display,
        'display_simple': simplify_title(display),
        'comment': ''
    }
    for base, display in KNOWN_BOSSES_CUSTOM_TITLES.items()
}

# Merge with custom overriding defaults where keys overlap (custom wins)
KNOWN_BOSSES = {**KNOWN_BOSSES_UO, **KNOWN_BOSSES_CUSTOM}

#//==========================================================================
#TIMING
UPDATE_RATE = 1000 #ms  # idle/default update rate
FAST_UPDATE_RATE = 300  # ms # When a boss has been seen recently, use a faster update
RECENT_BOSS_SEEN_MS = 5000 # Consider a boss "recently seen" if spotted within this window
SEARCH_RANGE_MAX = 30  # tiles to search for boss candidates
STALE_MS = 15000     # prune unseen candidates after 15s

# Unique gump ID (large, unlikely to collide)
GUMP_ID = 3411114999

GUMP_ART = {
    "BACKGROUND": 3500,  # Standard gump background
    "BAR": 5210,         # 12x16 pixel bar segment (tinted for fill)
    "BAR_BG": 2624,      # Dark tile for depleted portion background
}

# UI image assets for side embellishments (dragon edges)
# Keys match requested naming to reference IDs by descriptive name
# Left:  0x28B4  |  Right: 0x28BE
UI_GUMP_IMAGES = {
    "ui_quest_edgeDragon_0x28B4": 0x28B4,  # left edge
    "ui_quest_edgeDragon_0x28BE": 0x28BE,  # right edge
}

# Flourish arrow gump images (rendered behind everything else)
FLOURISH_IMAGES = {
    "left_flourish_arrow_red": 4235,   # left flourish arrow red
    "right_flourish_arrow_red": 4236,  # right flourish arrow red
}

# Dimensions and layout
# Width stays a multiple of 12 for clean tiling of 12px bar art
BAR_WIDTH = 432            # wider (36 * 12)
BAR_HEIGHT = 25            # taller (will stack 12x16 segments vertically)
PADDING = 6                # Padding inside background
OUTLINE_THICKNESS = 2      # Visual border thickness
OUTLINE_IMAGE_TINT = 37  # Tint hue for the bar's image outline (use a dark red/gray). Set to None for no tint.

# Name label controls
NAME_OFFSET_X = 0          # horizontal tweak from centered position
NAME_OFFSET_Y = 17          # vertical offset from top padding (move down by increasing)
NAME_DUPLICATE_COUNT = 2   # how many times to draw the main red label for boldness

# Text width tuning for centering ( this is not good , not working well )
# trying to center the text based on the length but we need to account for irregular ascii characters
NAME_CHAR_W_LOWER = 5
NAME_CHAR_W_UPPER = 5
NAME_CHAR_W_DIGIT = 5
NAME_CHAR_W_SPACE = 5
NAME_CHAR_W_PUNCT = 5
NAME_CHAR_W_EXT = 5        # non-ascii decorative symbols
NAME_EXTRA_OUTLINE_W = 0   # extra for glow/outline spread

# Optional side images (left/right) to embellish the bar
SIDE_IMAGE_W = 59            # approximate width of the dragon edge art
SIDE_IMAGE_H = 25            # approximate height of the dragon edge art
SIDE_IMAGE_GAP = 0           # spacing between side image and bar
SIDE_IMAGE_LEFT_KEY = "ui_quest_edgeDragon_0x28B4"
SIDE_IMAGE_RIGHT_KEY = "ui_quest_edgeDragon_0x28BE"
# Stacking to make images appear bigger (simulated scaling)
SIDE_IMAGE_STACK = True
SIDE_IMAGE_GROW_PIX = 6      # visual growth by layering; 0 disables growth
SIDE_IMAGE_TINT = 1250         # dark red tint for side embellishments (distinct from filigree)
#2038

# Flourish arrow configuration (rendered behind everything else)
FLOURISH_LEFT_OFFSET_X = 60   # left flourish position from left edge
FLOURISH_RIGHT_OFFSET_X = 70  # right flourish position from right edge (double the left offset)
FLOURISH_OFFSET_Y = -38        # vertical offset (negative = higher up)
FLOURISH_TINT = 2999          # dark hue for flourishes
# Top-center filigree (arch) image
TOP_CENTER_IMAGE_ID = 30077     # center filigree arch
TOP_CENTER_IMAGE_TINT = 2999      # even darker red hue; fallback to COLOR['bar_fill'] if needed
TOP_CENTER_IMAGE_OFFSET_Y = -6  # place slightly above bar_y
TOP_CENTER_IMAGE_OFFSET_X = 0   # fine-tune centering if needed
TOP_CENTER_IMAGE_W = 64         # approximate width used for centering

# Screen placement (top of screen)
GUMP_X = 540               # X position; adjust to your preference
GUMP_Y = 0                # Near the top edge

# CUO Health Bar placement (middle of screen)
CUO_HEALTHBAR_X = 500      # X position for CUO health bars
CUO_HEALTHBAR_Y = 400      # Y position for CUO health bars

# Colors
COLOR = {
    "text": 2000,          # White (generic text)
    "text_border": 0,      # Black
    "bar_fill": 37,        # Bright Red (health fill hue) #38
    "bar_depleted": 2999,  # Very dark gray
    "background_tint": 0,  # Pure black tint for background
    "boss_name": 38,       # Boss name in red
    "boss_name_glow": 0,   # Outline/glow color (black)
    "phase_marker": 2999,  # Dark gray for phase dividers
}

#//==========================================================================

class BossHealthBar:
    def __init__(self):
        self.gump_id = GUMP_ID
        self.boss_serial = None
        self.active = False
        self.last_update = 0
        self.update_delay_ms = UPDATE_RATE  
        self.last_boss_seen_ms = 0          # timestamp (ms) when any boss candidate was last seen

        # Cache prior health to optionally animate loss , this isnt very useful because the server returns out of 25 , and boss health is slowly moving.
        self.prev_hits = None

        # Pre-calc total gump size
        extra_w = 0
        if SIDE_IMAGES_ENABLED:
            grow = SIDE_IMAGE_GROW_PIX if SIDE_IMAGE_STACK else 0
            extra_w = ((SIDE_IMAGE_W + grow) * 2) + (SIDE_IMAGE_GAP * 2)
        self.total_width = BAR_WIDTH + PADDING * 2 + extra_w
        # Ensure tall enough to show side images if enabled
        bar_area_h = BAR_HEIGHT + PADDING * 2 + 16  # room for name label
        side_h = (SIDE_IMAGE_H + PADDING * 2) if SIDE_IMAGES_ENABLED else 0
        self.total_height = max(bar_area_h, side_h)

        # Boss candidates/info cache: serial -> info
        # info = {
        #   'name': str, 'key': str, 'display': str,
        #   'last_seen_ms': int, 'distance': int,
        #   'hits': int, 'hits_max': int,
        #   'x': int, 'y': int, 'map': int
        # }
        self.boss_info = {}
        # Test-mode cache of randomized display per target serial
        # serial -> {'display': str, 'last_change_ms': int}
        self._test_fake_title_state = {}

    def debug_message(self, msg, color=68):
        if DEBUG_MODE:
            try:
                Misc.SendMessage(f"[BOSSUI] {msg}", color)
            except Exception:
                try:
                    print(f"[BOSSUI] {msg}")
                except Exception:
                    pass
    
    def attempt_auto_attack(self, mob):
        """Attempt to attack a newly seen boss once if enabled."""
        if not AUTO_ATTACK_NEW_BOSSES:
            return
        try:
            Player.Attack(mob)
            # In case a targeting cursor is up, send it to the mob
            if Target.HasTarget():
                Target.TargetExecute(mob)
            self.debug_message(f"Auto-attack issued to newly detected boss: {getattr(mob, 'Name', mob.Serial)}")
        except Exception as e:
            self.debug_message(f"attempt_auto_attack error: {e}")

    def open_cuo_healthbar(self, mob):
        """Attempt to open CUO mobile health bar for the boss if enabled."""
        if not GET_CUO_HEALTHBAR:
            return
        try:
            # CUO.OpenMobileHealthBar(mobileserial, x, y, custom)
            # Parameters: mobileserial (UInt32), x (Int32), y (Int32), custom (Boolean)
            CUO.OpenMobileHealthBar(mob.Serial, CUO_HEALTHBAR_X, CUO_HEALTHBAR_Y, True)
            self.debug_message(f"Opened CUO health bar for boss: {getattr(mob, 'Name', mob.Serial)} at ({CUO_HEALTHBAR_X}, {CUO_HEALTHBAR_Y})")
        except Exception as e:
            self.debug_message(f"open_cuo_healthbar error: {e}")

#//=========      Boss Detection & Matching      ===============

    def get_boss_mobile(self):
        if not self.boss_serial:
            return None
        try:
            mob = Mobiles.FindBySerial(self.boss_serial)
            return mob
        except Exception:
            return None

    def normalize(self, s):
        try:
            return s.lower().strip()
        except Exception:
            return ""

    def match_known_boss(self, name):
        """Return (base_key, display_str) if name contains a known base boss name, else (None, None)."""
        n = self.normalize(name)
        if not n:
            return None, None
        for base, meta in KNOWN_BOSSES.items():
            b = self.normalize(base)
            if b and b in n:
                display_str = meta.get('display_simple') if USE_SIMPLE_TITLES else meta.get('display')
                return base, (display_str or base)
        return None, None

    def distance_to_player(self, mob):
        try:
            p = Player.Position
            m = mob.Position
            return max(abs(p.X - m.X), abs(p.Y - m.Y))
        except Exception:
            return 9999

    def search_for_boss_candidates(self):
        """search nearby mobiles and update boss_info for those matching KNOWN_BOSSES."""
        try:
            f = Mobiles.Filter()
            f.Enabled = True
            f.RangeMax = SEARCH_RANGE_MAX
            # Prefer hostiles; if unavailable, leave empty to include all
            # consider Lord Oaks or potential Blue bosses
            try:
                f.Notorieties.Add(3)  # gray
                f.Notorieties.Add(4)  # criminal
                f.Notorieties.Add(5)  # orange/war
                f.Notorieties.Add(6)  # red
            except Exception:
                pass

            mobs = Mobiles.ApplyFilter(f)
            now = int(time.time() * 1000)

            if mobs:
                self.debug_message(f"searchning {len(mobs)} mobiles within {SEARCH_RANGE_MAX} tiles...")
                for mob in mobs:
                    try:
                        if not mob or not mob.Name:
                            continue
                        # Optional testing: force random boss titles on specific simple mobs
                        nlow = self.normalize(mob.Name)
                        if TESTING_FAKE_BOSS_MODE and nlow in TESTING_TARGET_NAMES:
                            try:
                                # Build a list of display strings according to USE_SIMPLE_TITLES
                                all_titles = [
                                    (meta.get('display_simple') if USE_SIMPLE_TITLES else meta.get('display')) or base
                                    for base, meta in KNOWN_BOSSES.items()
                                ]
                                if all_titles:
                                    key = "test_random"
                                    # Throttle randomization per target serial
                                    st = self._test_fake_title_state.get(mob.Serial)
                                    if st and (now - st.get('last_change_ms', 0)) < TESTING_FAKE_BOSS_RENAME_MS:
                                        display = st.get('display')
                                    else:
                                        display = random.choice(all_titles)
                                        self._test_fake_title_state[mob.Serial] = {
                                            'display': display,
                                            'last_change_ms': now,
                                        }
                                else:
                                    key, display = self.match_known_boss(mob.Name)
                            except Exception:
                                key, display = self.match_known_boss(mob.Name)
                        else:
                            key, display = self.match_known_boss(mob.Name)
                        if not key:
                            self.debug_message(f"Seen mobile (no match): {mob.Name} @ {mob.Position.X},{mob.Position.Y} (serial {mob.Serial})")
                            continue
                        dist = self.distance_to_player(mob)
                        # only keep reasonably close
                        if dist > SEARCH_RANGE_MAX:
                            self.debug_message(f"Match but out of range: {mob.Name} dist {dist}")
                            continue

                        is_new = mob.Serial not in self.boss_info
                        info = self.boss_info.get(mob.Serial, {})
                        info.update({
                            'name': mob.Name,
                            'key': key,
                            'display': display or mob.Name,
                            'last_seen_ms': now,
                            'distance': dist,
                            'hits': int(getattr(mob, 'Hits', 0) or 0),
                            'hits_max': int(getattr(mob, 'HitsMax', 1) or 1),
                            'x': getattr(mob.Position, 'X', 0),
                            'y': getattr(mob.Position, 'Y', 0),
                            'map': getattr(mob, 'Map', 0),
                        })
                        self.boss_info[mob.Serial] = info
                        if is_new:
                            self.attempt_auto_attack(mob)
                            self.open_cuo_healthbar(mob)
                        # mark recent boss sighting
                        self.last_boss_seen_ms = now
                        self.debug_message(f"Matched boss candidate: [{info['display']}] serial {mob.Serial} dist {dist} HP {info['hits']}/{info['hits_max']}")
                    except Exception:
                        continue

            # prune stale
            to_del = []
            for serial, info in self.boss_info.items():
                if now - info.get('last_seen_ms', 0) > STALE_MS:
                    to_del.append(serial)
            for serial in to_del:
                self.boss_info.pop(serial, None)
                # also clear test-mode state for this serial
                try:
                    self._test_fake_title_state.pop(serial, None)
                except Exception:
                    pass
            if to_del:
                self.debug_message(f"Pruned {len(to_del)} stale candidates")
        except Exception as e:
            self.debug_message(f"search_for_boss_candidates error: {e}")

    def auto_select_best_boss(self):
        """If no manual selection, choose the closest boss candidate."""
        if self.boss_serial:
            return
        try:
            if not self.boss_info:
                return
            best = None
            best_dist = None
            for serial, info in self.boss_info.items():
                dist = info.get('distance', 9999)
                if best_dist is None or dist < best_dist:
                    best_dist = dist
                    best = serial
            if best:
                self.boss_serial = best
                self.prev_hits = None
                self.debug_message(f"Auto-selected boss: {self.boss_info[best].get('display')} [{best}]")
        except Exception as e:
            self.debug_message(f"auto_select_best_boss error: {e}")

#//========      GUMP UI      ===============

    def estimate_label_width(self, text):
        try:
            w = 0
            for ch in text:
                o = ord(ch)
                if ch == ' ':
                    w += NAME_CHAR_W_SPACE
                elif '0' <= ch <= '9':
                    w += NAME_CHAR_W_DIGIT
                elif 'a' <= ch <= 'z':
                    w += NAME_CHAR_W_LOWER
                elif 'A' <= ch <= 'Z':
                    w += NAME_CHAR_W_UPPER
                elif o > 127:
                    w += NAME_CHAR_W_EXT
                else:
                    # punctuation and others
                    w += NAME_CHAR_W_PUNCT
            return w + NAME_EXTRA_OUTLINE_W
        except Exception:
            # fallback similar to old behavior
            return max(0, len(text) * 4)

    def draw_bar(self, gump, x, y, width, height, current, maximum):
        """Draw a horizontal bar with dark outline and solid red fill."""
        width = max(0, int(width))
        height = max(1, int(height))

        # Outline area (slightly larger dark border)
        outline_x = x - OUTLINE_THICKNESS
        outline_y = y - OUTLINE_THICKNESS
        outline_w = width + OUTLINE_THICKNESS * 2
        outline_h = height + OUTLINE_THICKNESS * 2

        # Draw outline by tiling the bar sprite with precise thickness
        # Top border
        Gumps.AddImageTiled(gump, outline_x, outline_y, outline_w, OUTLINE_THICKNESS, GUMP_ART["BAR"])
        # Bottom border
        Gumps.AddImageTiled(gump, outline_x, outline_y + outline_h - OUTLINE_THICKNESS, outline_w, OUTLINE_THICKNESS, GUMP_ART["BAR"])
        # Left border
        Gumps.AddImageTiled(gump, outline_x, outline_y, OUTLINE_THICKNESS, outline_h, GUMP_ART["BAR"])
        # Right border
        Gumps.AddImageTiled(gump, outline_x + outline_w - OUTLINE_THICKNESS, outline_y, OUTLINE_THICKNESS, outline_h, GUMP_ART["BAR"])

        # Depleted background of the bar (use a dark tile so fill stands out)
        Gumps.AddImageTiled(gump, x, y, width, height, GUMP_ART["BAR_BG"])  # dark background tile

        # Filled portion (solid red)
        filled_w = int((current / float(maximum)) * width) if maximum > 0 else 0
        filled_w = max(0, min(width, filled_w))
        if filled_w > 0:
            # For small heights, a single row; for ~20px heights, use 3 stacked rows to hide seams.
            if height <= 16:
                rows_y = [y]
            elif height <= 32:
                # Top, bottom, and a centered overlap to cover the join line
                top_y = y
                bottom_y = y + (height - 16)
                mid_y = y + max(0, (height // 2) - 8)
                rows_y = [top_y, bottom_y, mid_y]
            else:
                # Larger heights: tile every 16px and add an extra middle overlap
                rows_y = [y + iy for iy in range(0, height, 16)]
                rows_y.append(y + max(0, (height // 2) - 8))

            for ry in rows_y:
                for ix in range(0, filled_w, 12):
                    Gumps.AddImage(gump, x + ix, ry, GUMP_ART["BAR"], COLOR["bar_fill"])

    def add_name_label(self, gump, center_x, y, text):
        try:
            # BIG OUTER GLOW OUTLINE
            # Multi-layer glow: three radii of black around the red main label
            # Note: label font size is fixed; this simulates thicker presence
            offsets_r1 = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
            offsets_r2 = [(-2, 0), (2, 0), (0, -2), (0, 2), (-2, -1), (-2, 1), (2, -1), (2, 1), (-1, -2), (1, -2), (-1, 2), (1, 2)]
            offsets_r3 = [
                (-3, 0), (3, 0), (0, -3), (0, 3),
                (-3, -1), (-3, 1), (3, -1), (3, 1),
                (-1, -3), (1, -3), (-1, 3), (1, 3),
                (-2, -2), (2, -2), (-2, 2), (2, 2)
            ]
            for dx, dy in offsets_r3:
                Gumps.AddLabel(gump, center_x + dx, y + dy, COLOR["boss_name_glow"], text)
            for dx, dy in offsets_r2:
                Gumps.AddLabel(gump, center_x + dx, y + dy, COLOR["boss_name_glow"], text)
            for dx, dy in offsets_r1:
                Gumps.AddLabel(gump, center_x + dx, y + dy, COLOR["boss_name_glow"], text)
            # Main red label
            for _ in range(max(1, NAME_DUPLICATE_COUNT)):
                Gumps.AddLabel(gump, center_x, y, COLOR["boss_name"], text)
        except Exception as e:
            self.debug_message(f"add_name_label error: {e}")

    

    def draw_phase_markers(self, gump, x, y, width, height):
        if not SHOW_PHASE_MARKERS or width < 6:
            return
        try:
            one_third = x + int(width / 3)
            two_thirds = x + int((2 * width) / 3)
            # place markers vertically centered on the bar height
            marker_y = y + max(0, (height // 2) - 8)
            Gumps.AddLabel(gump, one_third, marker_y, COLOR["phase_marker"], "|")
            Gumps.AddLabel(gump, two_thirds, marker_y, COLOR["phase_marker"], "|")
        except Exception:
            pass

    def create_gump(self):
        try:
            gump = Gumps.CreateGump(movable=True)
            Gumps.AddPage(gump, 0)

            # Draw flourish arrows FIRST (behind everything else)
            if FLOURISH_ARROWS_ENABLED:
                try:
                    # Left flourish arrow - moved more to the right and higher
                    left_flourish_x = FLOURISH_LEFT_OFFSET_X
                    left_flourish_y = (self.total_height // 2) + FLOURISH_OFFSET_Y
                    Gumps.AddImage(gump, left_flourish_x, left_flourish_y, FLOURISH_IMAGES["left_flourish_arrow_red"], FLOURISH_TINT)
                    
                    # Right flourish arrow - moved double distance to the left and higher
                    right_flourish_x = self.total_width - FLOURISH_RIGHT_OFFSET_X - 24  # assuming ~24px width for flourish
                    right_flourish_y = (self.total_height // 2) + FLOURISH_OFFSET_Y
                    Gumps.AddImage(gump, right_flourish_x, right_flourish_y, FLOURISH_IMAGES["right_flourish_arrow_red"], FLOURISH_TINT)
                except Exception as e:
                    self.debug_message(f"flourish arrows error: {e}")

            # Ensure we have a candidate if none selected
            if not self.boss_serial:
                self.search_for_boss_candidates()
                self.auto_select_best_boss()

            mob = self.get_boss_mobile()
            has_target = mob is not None and getattr(mob, 'Exists', True)

            # If no valid target, hide the gump and exit
            if not has_target:
                try:
                    Gumps.CloseGump(self.gump_id)
                except Exception:
                    pass
                self.debug_message("No valid boss target nearby; gump hidden.")
                return False

            # Title/Name
            name = "No Boss Selected"
            hits = 0
            hits_max = 1
            if has_target:
                try:
                    raw_name = mob.Name if getattr(mob, 'Name', None) else f"[{mob.Serial}]"
                    # Prefer cached display from boss_info if available
                    info = self.boss_info.get(mob.Serial, {})
                    disp = info.get('display')
                    if not disp:
                        # Fallback: resolve via KNOWN_BOSSES matching
                        _key, _disp = self.match_known_boss(raw_name)
                        disp = _disp or raw_name
                    name = disp
                    hits = max(0, int(getattr(mob, 'Hits', 0)))
                    hits_max = max(1, int(getattr(mob, 'HitsMax', 1)))
                except Exception:
                    pass
            
            # Bar area
            # If side images are enabled, shift bar to the right to make room
            bar_x = PADDING
            if SIDE_IMAGES_ENABLED:
                bar_x += SIDE_IMAGE_W + SIDE_IMAGE_GAP
            bar_y = PADDING + 14  # leave space for name on top

            # Draw bar and container
            self.draw_bar(gump, bar_x, bar_y, BAR_WIDTH, BAR_HEIGHT, hits, hits_max)

            # Optional side images (left and right), centered vertically inside background
            if SIDE_IMAGES_ENABLED:
                try:
                    left_id = UI_GUMP_IMAGES.get(SIDE_IMAGE_LEFT_KEY)
                    right_id = UI_GUMP_IMAGES.get(SIDE_IMAGE_RIGHT_KEY)
                    cy = max(PADDING, (self.total_height - SIDE_IMAGE_H) // 2)
                    # Left image 10px further left (bounded at 0)
                    grow = SIDE_IMAGE_GROW_PIX if SIDE_IMAGE_STACK else 0
                    left_x = PADDING - 10
                    if left_x < 0:
                        left_x = 0
                    # Draw stacked copies to simulate larger image if enabled
                    if SIDE_IMAGE_STACK and grow > 0:
                        # Use small offset ring to thicken
                        s = max(1, min(3, grow // 2))
                        offsets = [
                            (0, 0),
                            (-s, 0), (s, 0), (0, -s), (0, s),
                            (-s, -s), (s, -s), (-s, s), (s, s)
                        ]
                        for dx, dy in offsets:
                            Gumps.AddImage(gump, left_x + dx, cy + dy, left_id, SIDE_IMAGE_TINT)
                    else:
                        Gumps.AddImage(gump, left_x, cy, left_id, SIDE_IMAGE_TINT)
                    # Right image at inner right padding
                    right_x = self.total_width - PADDING - (SIDE_IMAGE_W + (SIDE_IMAGE_GROW_PIX if SIDE_IMAGE_STACK else 0))
                    if SIDE_IMAGE_STACK and grow > 0:
                        s = max(1, min(3, grow // 2))
                        offsets = [
                            (0, 0),
                            (-s, 0), (s, 0), (0, -s), (0, s),
                            (-s, -s), (s, -s), (-s, s), (s, s)
                        ]
                        for dx, dy in offsets:
                            Gumps.AddImage(gump, right_x + dx, cy + dy, right_id, SIDE_IMAGE_TINT)
                    else:
                        Gumps.AddImage(gump, right_x, cy, right_id, SIDE_IMAGE_TINT)
                except Exception:
                    pass

            # Top-center filigree image, centered over the bar (before dividers)
            if TOP_CENTER_IMAGE_ENABLED:
                try:
                    center_x = bar_x + (BAR_WIDTH // 2) + TOP_CENTER_IMAGE_OFFSET_X
                    img_x = center_x - (TOP_CENTER_IMAGE_W // 2)
                    img_y = bar_y + TOP_CENTER_IMAGE_OFFSET_Y - 16
                    hue = TOP_CENTER_IMAGE_TINT if TOP_CENTER_IMAGE_TINT is not None else COLOR.get("bar_fill", 38)
                    Gumps.AddImage(gump, img_x, img_y, TOP_CENTER_IMAGE_ID, hue)
                except Exception:
                    pass

            # Draw phase dividers on top of images and bar
            self.draw_phase_markers(gump, bar_x, bar_y, BAR_WIDTH, BAR_HEIGHT)

            # Centered name label using classic outline method
            text_y = PADDING + NAME_OFFSET_Y
            est_w = self.estimate_label_width(name)
            text_x = (self.total_width - est_w) // 2 + NAME_OFFSET_X
            self.add_name_label(gump, text_x, text_y, name)

            # Optional numeric values centered on the bar (white with black outline)
            if SHOW_HEALTH_NUMBERS:
                val_text = f"{hits} / {hits_max}"
                val_x = (self.total_width // 2) - max(0, (len(val_text) * 4))
                Gumps.AddLabel(gump, val_x + 1, bar_y + 3, COLOR["text_border"], val_text)
                Gumps.AddLabel(gump, val_x, bar_y + 2, COLOR["text"], val_text)

            # Send gump
            Gumps.SendGump(self.gump_id, Player.Serial, GUMP_X, GUMP_Y, gump.gumpDefinition, gump.gumpStrings)
            return True
        except Exception as e:
            self.debug_message(f"create_gump error: {e}", 33)
            return False

    def update(self):
        try:
            now = int(time.time() * 1000)
            if (now - self.last_update) >= self.update_delay_ms:
                self.last_update = now
                # Continuous search maintains boss_info freshness
                self.search_for_boss_candidates()
                # If manual target is gone, fall back to auto selection
                if self.boss_serial and not self.get_boss_mobile():
                    self.boss_serial = None
                if not self.boss_serial:
                    self.auto_select_best_boss()
                # Adjust update pacing based on recent boss presence
                try:
                    has_target = self.get_boss_mobile() is not None
                except Exception:
                    has_target = False
                recent = has_target or (now - self.last_boss_seen_ms) <= RECENT_BOSS_SEEN_MS
                self.update_delay_ms = FAST_UPDATE_RATE if recent else UPDATE_RATE

                self.create_gump()
        except Exception as e:
            self.debug_message(f"update error: {e}")

    def start(self):
        self.active = True
        self.debug_message("Boss health bar started.")
        try:
            while self.active and Player.Connected:
                self.update()
                Misc.Pause(50)
        except Exception as e:
            self.debug_message(f"main loop error: {e}", 33)
        finally:
            self.stop()

    def stop(self):
        self.active = False
        try:
            Gumps.CloseGump(self.gump_id)
        except Exception:
            pass
        self.debug_message("Boss health bar stopped.")

def main():
    ui = BossHealthBar()
    ui.start()

if __name__ == "__main__":
    main()
