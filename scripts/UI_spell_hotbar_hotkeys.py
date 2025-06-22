"""
UI Spell Hotbar Hotkeys - a Razor Enhanced Python Script for Ultima Online

Creates a gump of spell icons , a modern hotbar with cooldown and hotkey symbols
this is a copy of the example with some aditions 

VERSION::20250621
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
    ("Create Food",   2241, 2241),
    ("Protection",    2254, 2254),
    ("Teleport",      2261, 2261),
    ("Lightning",     2269, 2269),
    ("Recall",        2271, 2271),
    ("Energy Bolt",   2281, 2281),
    ("Invisibility",  2283, 2283),
    ("Mark",          2284, 2284),
    ("Reveal",        2287, 2287),
    ("Gate Travel",   2291, 2291)
]

# Hotkey labels for each spell button
hotkeys = {
    1: "F",
    2: "2",
    3: "3",
    4: "4",
    5: "5",
    6: "6",
    7: "7",
    8: "8",
    9: "9",
    10:"0"
}

# Assumed dimensions for each spell button
button_width = 44
button_height = 44

# Placeholder directional arrow image IDs.
# We'll use the "pressed" art for all directional buttons.
arrow_art_up    = 5001
arrow_art_down  = 5003
arrow_art_left  = 5005
arrow_art_right = 5007

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
