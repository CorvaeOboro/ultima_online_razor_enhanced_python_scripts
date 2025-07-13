"""
Development Font Color Gump  - a Razor Enhanced Python Script for Ultima Online

visually verifying UO font hue hex codes in a custom Gump

VERSION::20250713
"""

FONT_COLORS = [
    # --- RYOGBP (Rainbow order) ---
    ('red', 0x0020),      # red
    ('dark red', 0x0024), # dark red
    ('maroon', 0x0021),   # maroon (confirmed)
    ('pink', 0x0028),     # pink (confirmed)
    ('orange', 0x0030),   # orange (near red)
    ('yellow', 0x0099),        # yellow
    ('gold', 0x08A5),     # Gold (confirmed)
    ('beige', 0x002D),    # beige (confirmed)
    ('brown', 0x01BB),    # light brown
    ('green', 0x0044),    # Green (confirmed)
    ('dark green', 0x0042), # dark green
    ('lime', 0x0040),     # lime
    ('teal', 0x0058),     # teal
    ('aqua', 0x005F),     # aqua
    ('light blue', 0x005A), # light blue
    ('blue', 0x0056),     # blue (near teal)
    ('dark blue', 0x0001),# dark blue (confirmed)
    ('purple', 0x01A2),   # purple
    ('white', 0x0384),    # white
    ('gray', 0x0385),     # Gray (confirmed)
    ('dark gray', 0x07AF),# dark gray
]

# gump ID= 4294967295  = the max value , randomly select a high number gump so its unique
GUMP_ID =  3429654444

GUMP_X = 400
GUMP_Y = 400

class FontColorGump:
    def __init__(self, colors):
        self.colors = colors

    def show(self):
        g = Gumps.CreateGump(movable=True)
        Gumps.AddPage(g, 0)
        width = 340
        height = 36 + len(self.colors) * 28
        Gumps.AddBackground(g, 0, 0, width, height, 9200)
        Gumps.AddLabel(g, 12, 8, 0x0481, "Font Color Hex Code TesterB")
        y = 36
        for name, hue in self.colors:
            # Color name in its own color
            Gumps.AddLabel(g, 24, y, hue, f"{name.title()}")
            # Hex code in same color
            Gumps.AddLabel(g, 160, y, hue, f"0x{hue:04X}")
            y += 28
        Gumps.AddButton(g, width - 32, 8, 3600, 3601, 1, 0, 0)  # Close button
        Gumps.SendGump(GUMP_ID, Player.Serial, GUMP_X, GUMP_Y, g.gumpDefinition, g.gumpStrings)

if __name__ == '__main__':
    FontColorGump(FONT_COLORS).show()
