"""
UI Spell Hotbar Hotkeys - a Razor Enhanced Python Script for Ultima Online

Creates a gump of spell icons, a modern hotbar with cooldown and hotkey symbols.
This is a copy of the example with some additions.

VERSION::20250707

Ultima Online Spell Icon IDs Reference:
Circle 1:
  - Clumsy         2190
  - Create Food    2241
  - Feeblemind     2242
  - Heal           2243
  - Magic Arrow    2244
  - Night Sight    2245
  - Reactive Armor 2246
  - Weaken         2247

Circle 2:
  - Agility        2248
  - Cunning        2249
  - Cure           2250
  - Harm           2251
  - Magic Trap     2252
  - Magic Untrap   2253
  - Protection     2254
  - Strength       2255

Circle 3:
  - Bless          2256
  - Fireball       2257
  - Magic Lock     2258
  - Poison         2259
  - Telekinesis    2260
  - Teleport       2261
  - Unlock         2262
  - Wall of Stone  2263

Circle 4:
  - Arch Cure      2264
  - Arch Protection 2265
  - Curse          2266
  - Fire Field     2267
  - Greater Heal   2268
  - Lightning      2269
  - Mana Drain     2270
  - Recall         2271

Circle 5:
  - Blade Spirits  2272
  - Dispel Field   2273
  - Incognito      2274
  - Magic Reflection 2275
  - Mind Blast     2276
  - Paralyze       2277
  - Poison Field   2278
  - Summon Creature 2279

Circle 6:
  - Dispel         2280
  - Energy Bolt    2281
  - Explosion      2282
  - Invisibility   2283
  - Mark           2284
  - Mass Curse     2285
  - Paralyze Field 2286
  - Reveal         2287

Circle 7:
  - Chain Lightning 2288
  - Energy Field   2289
  - Flamestrike    2290
  - Gate Travel    2291
  - Mana Vampire   2292
  - Mass Dispel    2293
  - Meteor Swarm   2294
  - Polymorph      2295

Circle 8:
  - Earthquake     2296
  - Energy Vortex  2297
  - Resurrection   2298
  - Air Elemental  2299
  - Summon Daemon  2300
  - Earth Elemental 2301
  - Fire Elemental 2302
  - Water Elemental 2303

"""
import time

# Global flag and position
hotbar_active = True
setX = 600
setY = 600

# gump ID= 4294967295  = the max value , randomly select a high number gump so its unique
GUMP_ID =  3329354721
GUMP_ID_dynamic = 3329354722

# Dictionaries for cooldowns and flash timers (per spell button id)
cooldowns = {}   # button id => timestamp (ms) when cooldown ends
flashes = {}     # button id => timestamp (ms) when flash effect ends

# Durations in milliseconds
cooldown_duration = 5000  # 5 seconds per spell
flash_duration = 300      # Flash lasts 300 ms

# Spell definitions: (spell name, unpressed image ID, pressed image ID)
spell_buttons = [
    ("Energy Bolt",        2281, 2281),      # 2281
    ("Invisibility",       2283, 2283),      # 2283
    ("Greater Heal",       2268, 2268),      # 2268
    ("Summon Water Elemental", 2303, 2303), # 2303
    ("Poison",             2259, 2259),      # 2259
    ("Magic Trap",         2252, 2252),      # 2252
    ("Teleport",           2261, 2261),      # 2261
    ("Cure",               2250, 2250),      # 2250
    ("Arch Cure",          2264, 2264)       # 2264
]

# Hotkey labels for each spell button
hotkeys = {
    1: "Q",
    2: "W",
    3: "E",
    4: "R",
    5: "S",
    6: "D",
    7: "F",
    8: "G",
    9: "H",
    10:"0"
}

# Assumed dimensions for each spell button
button_width = 44
button_height = 44

# directional arrow image IDs for gump UI (Ultima Online art).
arrow_art_up    = 5540  # Up arrow
arrow_art_down  = 5541  # Down arrow
arrow_art_left  = 5539  # Left arrow
arrow_art_right = 5542  # Right arrow


def cleanup_gumps():
    """Close any gumps created by this script."""
    try:
        Gumps.CloseGump(GUMP_ID)
    except Exception:
        pass
    try:
        Gumps.CloseGump(GUMP_ID_dynamic)
    except Exception:
        pass

# Register cleanup on script exit (Razor Enhanced runs top-level code, so use finally block if you have a main loop)
import atexit
atexit.register(cleanup_gumps)

def sendStaticGump():
    """Build and send the static UI elements (unchanging layer)."""
    gd = Gumps.CreateGump(movable=True)
    Gumps.AddPage(gd, 0)
    # Background sized to 500x110 to hold the hotbar and right-side controls.
    Gumps.AddBackground(gd, 0, 0, 500, 110, 30546)
    Gumps.AddAlphaRegion(gd, 0, 0, 500, 110)
    
    # --- Upper Right: Close Button & Movement Controls ---
    # Close button (button id 99)
    Gumps.AddButton(gd, 465, 5, 4017, 4018, 99, 1, 0)
    Gumps.AddTooltip(gd, r"Close Hotbar")
    # Movement buttons using the "pressed" art for both states.
    Gumps.AddButton(gd, 465, 30, arrow_art_up, arrow_art_up, 100, 1, 0)
    Gumps.AddTooltip(gd, r"Up")
    Gumps.AddButton(gd, 465, 50, arrow_art_down, arrow_art_down, 101, 1, 0)
    Gumps.AddTooltip(gd, r"Down")
    Gumps.AddButton(gd, 465, 70, arrow_art_left, arrow_art_left, 102, 1, 0)
    Gumps.AddTooltip(gd, r"Left")
    Gumps.AddButton(gd, 465, 90, arrow_art_right, arrow_art_right, 103, 1, 0)
    Gumps.AddTooltip(gd, r"Right")
    
    # --- Left: Spell Hotbar ---
    x_offset = 20
    button_id = 1
    for spell, btn_unpressed, btn_pressed in spell_buttons:
        # Add the static spell button.
        Gumps.AddButton(gd, x_offset, 10, btn_unpressed, btn_pressed, button_id, 1, 0)
        Gumps.AddTooltip(gd, r"{}".format(spell))
        # Add hotkey label below each button.
        hotkey = hotkeys.get(button_id, "")
        button_center = x_offset + (button_width // 2)
        label_x = button_center - (len(hotkey) * 4)
        Gumps.AddLabel(gd, label_x, 55, 1153, hotkey)
        x_offset += 44
        button_id += 1

    Gumps.SendGump(GUMP_ID, Player.Serial, setX, setY, gd.gumpDefinition, gd.gumpStrings)

def sendDynamicGump():
    """Build and send the dynamic overlay gump for cooldown and flash effects."""
    gd = Gumps.CreateGump(movable=False)
    Gumps.AddPage(gd, 0)
    # Use an alpha region for translucency.
    Gumps.AddAlphaRegion(gd, 0, 0, 500, 110)
    
    current_time = int(time.time() * 1000)
    x_offset = 20
    button_id = 1
    for spell, btn_unpressed, btn_pressed in spell_buttons:
        if button_id in cooldowns and current_time < cooldowns[button_id]:
            fraction = (cooldowns[button_id] - current_time) / cooldown_duration
            overlay_size = int(button_width * fraction)
            overlay_x = x_offset + (button_width - overlay_size) // 2
            overlay_y = 10 + (button_height - overlay_size) // 2
            # Image 6000 assumed to be a radial dark tint.
            Gumps.AddImage(gd, overlay_x, overlay_y, 6000)
        if button_id in flashes and current_time < flashes[button_id]:
            # Image 6001 assumed to be the flash effect.
            Gumps.AddImage(gd, x_offset, 10, 6001)
        x_offset += 44
        button_id += 1

    Gumps.SendGump(GUMP_ID_dynamic, Player.Serial, setX, setY, gd.gumpDefinition, gd.gumpStrings)

def processStaticInput():
    """Process input from the static gump."""
    global hotbar_active, setX, setY
    current_time = int(time.time() * 1000)
    Gumps.WaitForGump(GUMP_ID, 500)
    Gumps.CloseGump(GUMP_ID)
    gd = Gumps.GetGumpData(GUMP_ID)
    if not gd:
        return

    if gd.buttonid == 99:
        hotbar_active = False
    elif gd.buttonid == 100:  # Up
        setY -= 10
    elif gd.buttonid == 101:  # Down
        setY += 10
    elif gd.buttonid == 102:  # Left
        setX -= 10
    elif gd.buttonid == 103:  # Right
        setX += 10
    elif 1 <= gd.buttonid <= len(spell_buttons):
        if gd.buttonid in cooldowns and current_time < cooldowns[gd.buttonid]:
            pass
        else:
            spell = spell_buttons[gd.buttonid - 1][0]
            Spells.CastMagery(spell)
            cooldowns[gd.buttonid] = current_time + cooldown_duration
            flashes[gd.buttonid] = current_time + flash_duration
    sendStaticGump()

# Initially send the static gump.
sendStaticGump()

# Main loop: update dynamic overlay and process static input.
while Player.Connected and hotbar_active:
    processStaticInput()
    sendDynamicGump()
    Misc.Pause(100)
