"""
UI Player Health and Mana Status Bars - a Razor Enhanced Python Script for Ultima Online

Creates a custom gump showing health, mana, and stamina in a ARPG-style horizontal bar layout.
- Horizontal progress bars for health, mana, 
- Color intensity based on current health ( Green > Yellow > Red )
- Flashing loss of segment on damage taken
- Purple when poisoned
- Small dots horizontally for stamina 

TODO:
bandage duration 
add color dict for changing color scheme ( Blue to Orange gradient )
update to use optional setting.json , this way we can still default the gump locations to be visible on small resolution (laptop) , then have specific favored placement set . maybe this could be visible in first time usage , like a LOCK , that once clicked it hides the editablity and now loads into the placement of gump for your monitor 
add global toggle for emoting , and features
add in check if logged in , currently this shows on the login screen after logging out
add bandage duration and poison tick timing so we can better visualize 

HOTKEY:: AutoStart on Login
VERSION :: 20250908
"""

import time
import re

DEBUG_MODE = False # debug prints and messages 

# gump ID= 4294967295  = the max value , randomly select a high number gump so its unique
GUMP_ID =  3411114321
if Gumps.HasGump(GUMP_ID):
    Gumps.CloseGump(GUMP_ID)


# Art IDs for gump elements
GUMP_ART = {
    "BACKGROUND": 3500,  # Standard gump background
    "BAR": 5210,        # 12x16 pixel bar segment
    "SMALL_BAR": 9350,  # Smaller bar for stamina
}

# Bar segment dimensions , LARGE = Health Mana  , SMALL = Stamina 
SEGMENT_DIMENSIONS = {
    "LARGE": {
        "WIDTH": 12,   # Pixels wide
        "HEIGHT": 16,  # Pixels tall
    },
    "SMALL": {
        "WIDTH": 4,    # Pixels wide
        "HEIGHT": 8,   # Pixels tall
    }
}

# Status effect configurations
STATUS_EFFECTS = {
    "bandage": {
        "duration": 7000,  # 7 seconds in ms , this is modified by DEX we are using average
        "color": 168,     # Green
        "flash_color": 53, # Yellow
        "pattern": r"You begin applying the bandages",
    },
    "poison": {
        "duration": 30000,  # 30 seconds in ms
        "color": 0x01A2,   # Purple 
        "pattern": r"You have been poisoned",
    },
    "bleed": {
        "duration": 15000,  # 15 seconds in ms
        "color": 33,       # Red
        "pattern": r"You are bleeding",
    }
}

# Cooldown for saying "[emote oh" when critically low HP (in milliseconds) , 10 min
EMOTE_OH_COOLDOWN_MS = 600 * 1000

class ARPGStatusBars:
    def __init__(self):
        # UI dimensions
        self.bar_width = 204  # Adjusted to be multiple of segment width (17 segments * 12 pixels)
        self.bar_height = 16  # Match large segment height
        self.stamina_height = 8  # Smaller height for stamina
        self.status_bar_height = 6  # Height for status effect bars
        self.spacing = 1  # Minimal spacing
        
        # Position (centered in lower screen) we are keeping these low for laptops or small monitors
        self.x = 200 # 
        self.y = 400  # Lower screen areas
        
        # Gump ID (using unique range to avoid conflicts)
        self.gump_id = GUMP_ID
        
        # Update timing
        self.last_update = 0
        self.update_delay = 100  # 100ms for smooth updates
        self.last_journal_check = 0
        self.journal_check_delay = 1000  # Check journal every second
        self.active = False
        
        # Status effects tracking
        self.status_effects = {
            "bandage": {"active": False, "start_time": 0},
            "poison": {"active": False, "start_time": 0},
            "bleed": {"active": False, "start_time": 0}
        }
        # Emote tracking
        self.last_emote_oh = 0  # timestamp in ms of last "[emote oh"
        
        # Art IDs from global config
        self.art = {
            "background": GUMP_ART["BACKGROUND"],
            "bar": {
                "large": GUMP_ART["BAR"],
                "small": GUMP_ART["SMALL_BAR"]
            }
        }
        
        # Color configurations for bars and text
        self.colors = {
            "health": {
                "high": 168,     # Bright Green
                "medium": 53,    # Yellow
                "low": 33,       # Red
                "critical": 38,  # Bright Red
                "poisoned": 0x01A2   # Purple (confirmed from DEV_font_color_gump.py)
            },
            "mana": {
                "fill": 88,     # Light Blue
                "text": 88      # Light Blue
            },
            "stamina": {
                "fill": 2118,   # Desaturated orange
            },
            "text": 2000,        # White
            "text_border": 0     # Pure black
        }
        
        # Colors for segments
        self.segment_colors = {
            "filled": {
                "health": lambda pct: (
                    self.colors["health"]["poisoned"] if self.is_poisoned() else
                    self.colors["health"]["high"] if pct >= 0.7 else
                    self.colors["health"]["medium"] if pct >= 0.4 else
                    self.colors["health"]["low"] if pct >= 0.2 else
                    self.colors["health"]["critical"]
                ),
                "mana": lambda _: self.colors["mana"]["fill"],
                "stamina": lambda _: self.colors["stamina"]["fill"]
            },
            "depleted": 2999,  # Very dark grey hue for unfilled segments
            "changed": {
                "health": 32,  # Bright red for health damage
                "mana": 63,   # Purple for mana damage
                "default": 32  # Default red for other resources
            }
        }
        
        # Track previous values for change detection (only health and mana)
        self.previous_values = {
            "health": 0,
            "mana": 0
        }
        
        # Track recently changed segments (only health and mana)
        self.changed_segments = {
            "health": [],
            "mana": []
        }
        self.change_time = 500  # Time in ms to show changed segments
        
        # Thresholds for health colors
        self.thresholds = {
            "critical": 0.2,  # 20% health
            "low": 0.4,       # 40% health
            "medium": 0.7     # 70% health
        }

    # ---- Safe rect helpers to prevent invalid texture sizes ----
    def _clamp_int(self, v, lo, hi, fallback):
        try:
            iv = int(v)
            if iv < lo:
                return lo
            if iv > hi:
                return hi
            return iv
        except Exception:
            return int(fallback)

    def _safe_rect(self, x, y, w, h, max_w=1200, max_h=1200):
        sx = self._clamp_int(x, 0, 4096, 0)
        sy = self._clamp_int(y, 0, 4096, 0)
        sw = self._clamp_int(w, 1, int(max_w), 1)
        sh = self._clamp_int(h, 1, int(max_h), 1)
        return sx, sy, sw, sh
        
    def debug_message(self, message, color=68):
        """Send debug message if DEBUG_MODE is enabled"""
        if DEBUG_MODE:
            Misc.SendMessage(f"[ARPGUI] {message}", color)

    def say_emote_oh(self):
        """Say the in-game emote '[emote oh'. Uses chat if available, else sends a client message."""
        try:
            if hasattr(Player, 'ChatSay'):
                try:
                    Player.ChatSay("[emote oh")
                    return True
                except Exception:
                    pass
            Misc.SendMessage("[emote oh", 67)
            return True
        except Exception:
            try:
                print("[ARPGUI] [emote oh")
            except Exception:
                pass
        return False

    def maybe_emote_oh(self, current_hp, max_hp):
        """Trigger '[emote oh' if below 10% HP and not triggered within cooldown."""
        try:
            if max_hp <= 0:
                return
            pct = (current_hp / float(max_hp)) if max_hp > 0 else 0.0
            now_ms = int(time.time() * 1000)
            if pct < 0.10 and (now_ms - self.last_emote_oh) >= EMOTE_OH_COOLDOWN_MS:
                if self.say_emote_oh():
                    self.last_emote_oh = now_ms
        except Exception as e:
            self.debug_message(f"maybe_emote_oh error: {e}", 33)
    
    def is_poisoned(self):
        """Check if the player is currently poisoned"""
        try:
            return Player.Poisoned
        except:
            # Fallback: check for poison status effect if Player.Poisoned doesn't work
            return self.status_effects.get("poison", {}).get("active", False)

    def start_bandage_timer(self):
        """Call this when bandage application starts. Calculates and stores expected end time."""
        dex = getattr(Player, 'Dex', 100)  # Default to 100 if not available
        # UO bandage time formula: 11 - (dex / 20), min 4s, max 11s
        duration = max(4.0, min(11.0, 11.0 - (dex / 20.0)))
        self.status_effects['bandage']['active'] = True
        self.status_effects['bandage']['start_time'] = time.time()
        self.status_effects['bandage']['duration'] = duration
        self.debug_message(f"Bandage timer started: {duration:.2f}s (DEX={dex})", 68)

    def get_bandage_timer(self):
        """Returns (remaining_time, total_duration). If not active, returns (0,0)."""
        effect = self.status_effects.get('bandage', {})
        if not effect.get('active', False):
            return 0, 0
        now = time.time()
        elapsed = now - effect.get('start_time', 0)
        duration = effect.get('duration', 6.0)
        remaining = max(0, duration - elapsed)
        if remaining <= 0:
            self.status_effects['bandage']['active'] = False
            return 0, 0
        return remaining, duration
        
    def get_bar_color(self, current, maximum, resource_type):
        """Get color based on current value percentage"""
        percentage = current / maximum if maximum > 0 else 0
        colors = self.colors[resource_type]
        
        if resource_type == "health":
            # Check for poison first - overrides all other colors
            if self.is_poisoned():
                return colors["poisoned"]
            elif percentage <= self.thresholds["critical"]:
                return colors["critical"]
            elif percentage <= self.thresholds["low"]:
                return colors["low"]
            elif percentage <= self.thresholds["medium"]:
                return colors["medium"]
            else:
                return colors["high"]
                
        if resource_type == "exp":
            return colors[resource_type]  # Use specific exp type color
            
        return colors["fill"]
            
    def draw_segmented_bar(self, gump, x, y, width, height, current, maximum, bar_type):
        """Draw a bar made of individual segments that show resource level"""
        # Use appropriate art and dimensions
        is_small = bar_type == "stamina"
        art = self.art["bar"]["small"] if is_small else self.art["bar"]["large"]
        dims = SEGMENT_DIMENSIONS["SMALL"] if is_small else SEGMENT_DIMENSIONS["LARGE"]
        
        # Calculate segments (clamped for safety)
        num_segments = width // dims["WIDTH"]
        # Prevent pathological values
        if num_segments < 1:
            num_segments = 1
        elif num_segments > 256:
            num_segments = 256
        filled_segments = int((current / maximum) * num_segments) if maximum > 0 else 0
        if filled_segments < 0:
            filled_segments = 0
        elif filled_segments > num_segments:
            filled_segments = num_segments
        
        # Get current time for change animation (only for health and mana)
        current_time = time.time() * 1000
        
        # Check for changes (only for health and mana)
        if bar_type in ["health", "mana"]:
            previous = self.previous_values[bar_type]
            if current != previous:
                if current < previous:  # Resource decreased
                    start_seg = filled_segments
                    end_seg = int((previous / maximum) * num_segments) if maximum > 0 else 0
                    self.changed_segments[bar_type].extend([
                        {"segment": i, "time": current_time}
                        for i in range(start_seg, end_seg)
                    ])
                self.previous_values[bar_type] = current
            
            # Clean up old changed segments
            self.changed_segments[bar_type] = [
                change for change in self.changed_segments[bar_type]
                if current_time - change["time"] < self.change_time
            ]
        
        # Calculate percentage for health color
        percentage = current / maximum if maximum > 0 else 0
        
        # Draw segments
        for i in range(num_segments):
            segment_x = x + i * dims["WIDTH"]
            
            # Determine segment color
            if i < filled_segments:
                # For health, use the same color for all filled segments based on percentage
                if bar_type == "health":
                    color = self.segment_colors["filled"][bar_type](percentage)
                else:
                    color = self.segment_colors["filled"][bar_type](i / num_segments)
            else:
                # Check if this is a recently changed segment (only for health and mana)
                if bar_type in ["health", "mana"]:
                    is_changed = any(
                        change["segment"] == i 
                        for change in self.changed_segments[bar_type]
                    )
                    if is_changed:
                        # Use specific color for the bar type (red for health, purple for mana)
                        color = self.segment_colors["changed"].get(bar_type, self.segment_colors["changed"]["default"])
                    else:
                        color = self.segment_colors["depleted"]
                else:
                    color = self.segment_colors["depleted"]
            
            # Draw segment (clamp X/Y)
            seg_x, seg_y, _, _ = self._safe_rect(segment_x, y, 1, 1)
            Gumps.AddImage(gump, int(seg_x), int(seg_y), art, color)
            
    def check_journal(self):
        """Check journal for status effect messages"""
        current_time = time.time() * 1000
        if (current_time - self.last_journal_check) < self.journal_check_delay:
            return
            
        self.last_journal_check = current_time
        
        # Get journal entries
        entries = Journal.GetTextByType("Regular")
        if not entries:
            return
            
        # Check for status effect triggers
        for entry in entries:
            for effect, config in STATUS_EFFECTS.items():
                if re.search(config["pattern"], entry, re.IGNORECASE):
                    self.status_effects[effect] = {
                        "active": True,
                        "start_time": current_time
                    }
                    
    def draw_status_bar(self, gump, x, y, width, height, effect_type):
        """Draw a status effect progress bar"""
        current_time = time.time() * 1000
        effect = self.status_effects[effect_type]
        config = STATUS_EFFECTS[effect_type]
        
        if not effect["active"]:
            return
            
        # Calculate progress
        elapsed = current_time - effect["start_time"]
        if elapsed >= config["duration"]:
            effect["active"] = False
            return
            
        progress = 1.0 - (elapsed / config["duration"])
        filled_width = int(width * progress)
        
        # For bandages, flash near completion
        color = config["color"]
        if effect_type == "bandage" and progress < 0.15:  # Flash in last 15%
            if int(current_time / 200) % 2:  # Flash every 200ms
                color = config["flash_color"]
        
        # Draw background (darker version of effect color)
        rx, ry, rw, rh = self._safe_rect(x, y, width, height)
        if rw > 0 and rh > 0:
            Gumps.AddImageTiled(gump, rx, ry, rw, rh, self.art["bar"]["small"])
        
        # Draw filled portion
        if filled_width > 0:
            fx, fy, fw, fh = self._safe_rect(x, y, filled_width, height)
            if fw > 0 and fh > 0:
                Gumps.AddImageTiled(gump, fx, fy, fw, fh, self.art["bar"]["small"])
            
    def create_gump(self):
        """Create the status bars gump"""
        try:
            # Create new gump with movable=True
            gump = Gumps.CreateGump(movable=True)
            
            # Add page
            Gumps.AddPage(gump, 0)
            
            # Calculate total dimensions including status bars
            total_width = self.bar_width + 4  # Minimal padding
            status_section_height = (len(STATUS_EFFECTS) * 
                                   (self.status_bar_height + self.spacing))
            total_height = int(0.55 * (self.bar_height * 2 + 
                          self.stamina_height +
                          status_section_height +
                          self.spacing * 4 + 4))  # Minimal padding, scaled down
            # Clamp overall background size
            bg_x, bg_y, bg_w, bg_h = self._safe_rect(0, 0, total_width, total_height)
            
            # Add background with pure black tint (guard against degenerate sizes)
            if bg_w > 0 and bg_h > 0:
                Gumps.AddBackground(gump, bg_x, bg_y, bg_w, bg_h, self.art["background"])
                Gumps.AddImage(gump, bg_x, bg_y, self.art["background"], 0)  # Pure black tint
                Gumps.AddAlphaRegion(gump, bg_x, bg_y, bg_w, bg_h)
            
            # Health bar
            y_pos = 5
            self.draw_segmented_bar(gump, 5, y_pos, self.bar_width, self.bar_height, 
                                  Player.Hits, Player.HitsMax, "health")
            # Health value with color based on percentage
            health_text = str(Player.Hits)
            text_x = (self.bar_width // 2) - (len(health_text) * 4)
            lx1, ly1, _, _ = self._safe_rect(text_x + 1, y_pos + 2, 1, 1)
            Gumps.AddLabel(gump, lx1, ly1, 
                          self.colors["text_border"], health_text)
            lx2, ly2, _, _ = self._safe_rect(text_x, y_pos + 1, 1, 1)
            Gumps.AddLabel(gump, lx2, ly2, 
                          self.get_bar_color(Player.Hits, Player.HitsMax, "health"), health_text)
            
            # Mana bar
            y_pos += self.bar_height + self.spacing
            self.draw_segmented_bar(gump, 5, y_pos, self.bar_width, self.bar_height,
                                  Player.Mana, Player.ManaMax, "mana")
            # Mana value in blue
            mana_text = str(Player.Mana)
            text_x = (self.bar_width // 2) - (len(mana_text) * 4)
            mx1, my1, _, _ = self._safe_rect(text_x + 1, y_pos + 2, 1, 1)
            Gumps.AddLabel(gump, mx1, my1, 
                          self.colors["text_border"], mana_text)
            mx2, my2, _, _ = self._safe_rect(text_x, y_pos + 1, 1, 1)
            Gumps.AddLabel(gump, mx2, my2, 
                          self.colors["mana"]["text"], mana_text)
            
            # Stamina bar (no text)
            y_pos += self.bar_height + self.spacing
            self.draw_segmented_bar(gump, 5, y_pos, self.bar_width, self.stamina_height,
                                  Player.Stam, Player.StamMax, "stamina")

            # Bandage progress bar (below stamina)
            remaining, duration = self.get_bandage_timer()
            if duration > 0:
                bandage_pct = 1.0 - (remaining / duration)
                bandage_width = int(self.bar_width * bandage_pct)
                bandage_y = y_pos + self.stamina_height + self.spacing
                color = self.colors["health"]["high"]  # Bright green, like stamina
                # Draw background bar (dark)
                bx, by, bw, bh = self._safe_rect(5, bandage_y, self.bar_width, self.stamina_height)
                if bw > 0 and bh > 0:
                    Gumps.AddImageTiled(gump, bx, by, bw, bh, self.art["bar"]["small"])
                # Draw filled portion (fills as time passes)
                if bandage_width > 0:
                    bfx, bfy, bfw, bfh = self._safe_rect(5, bandage_y, bandage_width, self.stamina_height)
                    if bfw > 0 and bfh > 0:
                        Gumps.AddImageTiled(gump, bfx, bfy, bfw, bfh, self.art["bar"]["small"])
                y_pos = bandage_y

            # Status effect bars
            y_pos += self.stamina_height + self.spacing
            for effect in STATUS_EFFECTS:
                self.draw_status_bar(gump, 5, y_pos, self.bar_width, 
                                   self.status_bar_height, effect)
                y_pos += self.status_bar_height + self.spacing
            
            # Send the gump
            Gumps.SendGump(self.gump_id, Player.Serial, self.x, self.y, 
                          gump.gumpDefinition, gump.gumpStrings)
            return True
            
        except Exception as e:
            self.debug_message(f"Error creating gump: {str(e)}")
            return False
            
    def update(self):
        """Update the gump display"""
        try:
            current_time = time.time() * 1000
            if (current_time - self.last_update) >= self.update_delay:
                self.check_journal()  # Check for status updates
                self.last_update = current_time
                # Low HP emote check before rendering
                self.maybe_emote_oh(getattr(Player, 'Hits', 0), getattr(Player, 'HitsMax', 0))
                self.create_gump()
                    
        except Exception as e:
            self.debug_message(f"Error updating: {str(e)}")
            
    def start(self):
        """Start the UI update loop"""
        try:
            self.debug_message("Starting ARPG-style status bars...")
            
            self.active = True
            
            while self.active and Player.Connected:
                self.update()
                Misc.Pause(50)  # Short pause for smooth updates
                
        except Exception as e:
            self.debug_message(f"Error in main loop: {str(e)}")
            self.stop()
            
    def stop(self):
        """Stop the UI and clean up"""
        self.active = False
        Gumps.CloseGump(self.gump_id)
        self.debug_message("Stopped ARPG-style status bars")

def main():
    ui = ARPGStatusBars()
    ui.start()

if __name__ == "__main__":
    main()
