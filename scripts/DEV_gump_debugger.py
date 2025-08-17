"""
Development Gump Debugger - a Razor Enhanced Python Script for Ultima Online

Gump analysis and debugging tool , output is sent to chat log and a json file to be reviewed
journal logs are stored in Classic U client folder =
\Data\Client\JournalLogs\2025_03_18_01_35_39_journal.txt

- gump property extraction
- start script then open a gump in game to store properties to json

DOCUMENTATION:
https://razorenhanced.net/dokuwiki/doku.php?id=gump_funcs

VERSION::20250808
"""
DEBUG_TO_INGAME_MESSAGE = True
DEBUG_TO_JSON = True

import time
import os

def to_json(obj, indent=4, _level=0):
    """Custom JSON serializer for dict, list, str, int, float, bool, None."""
    sp = ' ' * (indent * _level)
    if isinstance(obj, dict):
        items = []
        for k, v in obj.items():
            items.append(f'{sp}    "{str(k)}": {to_json(v, indent, _level+1)}')
        return '{\n' + ',\n'.join(items) + f'\n{sp}' + '}'
    elif isinstance(obj, list):
        items = [to_json(i, indent, _level+1) for i in obj]
        return '[\n' + ',\n'.join(' ' * (indent * (_level+1)) + i for i in items) + f'\n{sp}]'
    elif isinstance(obj, str):
        return '"' + obj.replace('"', '\\"') + '"'
    elif obj is True:
        return 'true'
    elif obj is False:
        return 'false'
    elif obj is None:
        return 'null'
    else:
        return str(obj)


class GumpDebugger:
    def __init__(self):
        # Debug colors for different types of information
        self.colors = {
            'info': 68,      # Light Blue
            'warning': 53,    # Yellow
            'error': 33,     # Red
            'success': 63,    # Green
            'raw': 43,       # Orange
            'text': 73,      # Purple
            'id': 83,        # Cyan
            'structure': 93,  # Pink
            'button': 23     # Gold
        }
        
        # Tracking variables
        self.last_gump_id = 0
        self.active = True
        self.debug_level = 2  # 1=basic, 2=detailed, 3=full raw data
        
        # Initialize stats
        self.stats = {
            'gumps_analyzed': 0,
            'text_lines_found': 0,
            'buttons_found': 0,
            'errors': 0
        }
        # For JSON logging
        self.session_log = {
            'session_start': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),

            'gumps': []
        }
        self.current_gump_entry = None

    def debug(self, message, color='info', indent=0):
        """Send formatted debug message and/or log to session based on global booleans"""
        prefix = "    " * indent
        if DEBUG_TO_INGAME_MESSAGE:
            Misc.SendMessage(f"[GumpDebug] {prefix}{message}", self.colors[color])
        entry = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
            'message': message,
            'color': color,
            'indent': indent
        }


    def analyze_gump_text(self, gump_id):
        """Analyze all text content in the gump"""
        try:
            self.debug("Analyzing gump text:", 'text', 1)
            
            # Get all text lines
            text_lines = Gumps.LastGumpGetLineList()
            if text_lines:
                self.stats['text_lines_found'] += len(text_lines)
                self.debug(f"Found {len(text_lines)} text lines:", 'text', 2)
                
                # Show each line with its index
                for i, line in enumerate(text_lines):
                    if line.strip():  # Only show non-empty lines
                        self.debug(f"Line {i}: {line}", 'text', 3)
                        
                        # Try to detect what type of text this might be
                        if any(keyword in line.lower() for keyword in ['click', 'select', 'choose']):
                            self.debug("^ Appears to be instruction text", 'info', 4)
                        elif any(keyword in line.lower() for keyword in ['cost', 'price', 'gold']):
                            self.debug("^ Appears to be price/cost information", 'info', 4)
                        
            else:
                self.debug("No text lines found", 'warning', 2)
                
        except Exception as e:
            self.debug(f"Error analyzing text: {str(e)}", 'error', 2)
            self.stats['errors'] += 1
            
    def search_common_patterns(self, gump_id):
        """Search for common text patterns in the gump"""
        try:
            common_patterns = [
                "confirm",
                "cancel",
                "accept",
                "close",
                "next",
                "previous",
                "buy",
                "sell"
            ]
            
            self.debug("Searching for common patterns:", 'info', 1)
            for pattern in common_patterns:
                if Gumps.LastGumpTextExist(pattern):
                    self.debug(f"Found '{pattern}' pattern", 'success', 2)
                    
        except Exception as e:
            self.debug(f"Error searching patterns: {str(e)}", 'error', 2)
            self.stats['errors'] += 1
            
    def analyze_raw_data(self, gump_id):
        """Analyze raw gump data"""
        try:
            if self.debug_level >= 3:  # Only show raw data at highest debug level
                raw_data = Gumps.LastGumpRawData()
                if raw_data:
                    self.debug("Raw gump data:", 'raw', 1)
                    
                    # Split raw data into chunks for better readability
                    chunks = [raw_data[i:i+100] for i in range(0, len(raw_data), 100)]
                    for chunk in chunks:
                        self.debug(chunk, 'raw', 2)
                        
        except Exception as e:
            self.debug(f"Error analyzing raw data: {str(e)}", 'error', 2)
            self.stats['errors'] += 1
            
    def check_gump_state(self):
        """Check current gump state"""
        try:
            # Check if any gump is open
            has_gump = Gumps.HasGump()
            if not has_gump:
                return None
                
            # Get current gump ID
            current_id = Gumps.CurrentGump()
            if current_id == 0:
                return None
                
            return current_id
            
        except Exception as e:
            self.debug(f"Error checking gump state: {str(e)}", 'error')
            self.stats['errors'] += 1
            return None
            
    def analyze_gump(self, gump_id):
        """Perform complete gump analysis and log everything to JSON entry"""
        try:
            self.stats['gumps_analyzed'] += 1
            # Prepare gump entry for JSON
            # Try to extract additional gump metadata
            gump_serial = None
            gump_x = None
            gump_y = None
            gump_width = None
            gump_height = None
            gump_scale = None
            try:
                # Razor Enhanced exposes some info via Gumps.GetGumpData
                gd = None
                if hasattr(Gumps, 'GetGumpData'):
                    gd = Gumps.GetGumpData(gump_id)
                if gd:
                    gump_serial = getattr(gd, 'Serial', None)
                    gump_x = getattr(gd, 'X', None)
                    gump_y = getattr(gd, 'Y', None)
                    gump_width = getattr(gd, 'Width', None)
                    gump_height = getattr(gd, 'Height', None)
                    gump_scale = getattr(gd, 'Scale', None)
            except Exception as e:
                self.debug(f"Error extracting gump metadata: {str(e)}", 'error', 2)
            self.current_gump_entry = {
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
                'gump_id_decimal': gump_id,
                'gump_id_hex': hex(gump_id),
                'serial': hex(gump_serial) if gump_serial is not None else None,
                'position': {'x': gump_x, 'y': gump_y} if gump_x is not None and gump_y is not None else None,
                'size': {'width': gump_width, 'height': gump_height} if gump_width is not None and gump_height is not None else None,
                'scale': gump_scale,
                'text_lines': [],
                'button_positions': [],
                'raw_data': None,
                'positions': [],
            }
            self.session_log['gumps'].append(self.current_gump_entry)

            self.debug(f"\nAnalyzing Gump ID: {hex(gump_id)}", 'id')
            self.debug("Basic Information:", 'info', 1)
            self.debug(f"Decimal ID: {gump_id}", 'id', 2)
            self.debug(f"Hex ID: {hex(gump_id)}", 'id', 2)

            # Capture all text lines
            try:
                text_lines = Gumps.LastGumpGetLineList()
                if text_lines:
                    self.current_gump_entry['text_lines'] = list(text_lines)
            except:
                pass

            # Capture button/element positions if available
            try:
                positions = []
                # Try to get any element positions (if supported by Razor Enhanced API)
                if hasattr(Gumps, 'LastGumpGetElementPositions'):
                    positions = Gumps.LastGumpGetElementPositions()
                self.current_gump_entry['positions'] = list(positions) if positions else []
            except:
                pass

            # Analyze text content
            self.analyze_gump_text(gump_id)
            # Search for common patterns
            self.search_common_patterns(gump_id)

            # Capture raw data
            try:
                raw_data = Gumps.LastGumpRawData()
                if raw_data:
                    self.current_gump_entry['raw_data'] = raw_data
            except:
                pass
            # Analyze raw data if debug level is high enough
            self.analyze_raw_data(gump_id)

            # Show analysis summary
            self.debug("\nAnalysis Summary:", 'success', 1)
            self.debug(f"Text Lines: {self.stats['text_lines_found']}", 'text', 2)
            self.debug(f"Errors: {self.stats['errors']}", 'error', 2)

            self.current_gump_entry = None  # Done with this gump
        except Exception as e:
            self.debug(f"Error in gump analysis: {str(e)}", 'error')
            self.stats['errors'] += 1
    
    def monitor_gumps(self):
        """Main monitoring loop"""
        self.debug("Starting Gump Debugger...")
        self.debug(f"Debug Level: {self.debug_level}")
        
        while self.active and Player.Connected:
            try:
                current_gump = self.check_gump_state()
                
                if current_gump and current_gump != self.last_gump_id:
                    self.last_gump_id = current_gump
                    self.analyze_gump(current_gump)
                    
            except Exception as e:
                self.debug(f"Error in monitor loop: {str(e)}", 'error')
                self.stats['errors'] += 1
                
            Misc.Pause(100)  # Prevent excessive CPU usage
            
    def run(self):
        """Start the debugger and save session log as JSON on exit"""
        try:
            # Reset any existing gump state
            Gumps.ResetGump()
            # Start monitoring
            self.monitor_gumps()
        except Exception as e:
            self.debug(f"Fatal error: {str(e)}", 'error')
            raise e
        finally:
            self.debug("Gump Debugger stopped.")
            self.debug(f"Total Gumps Analyzed: {self.stats['gumps_analyzed']}")
            # Save JSON log if enabled
            if DEBUG_TO_JSON:
                try:
                    base_dir = os.path.dirname(os.path.abspath(__file__))
                    dt = time.strftime("%Y%m%d%H%M%S", time.localtime())
                    filename = f"gump_debug_{dt}.json"
                    file_path = os.path.join(base_dir, filename)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(to_json(self.session_log, indent=4))
                    if DEBUG_TO_INGAME_MESSAGE:
                        Misc.SendMessage(f"[GumpDebug] Wrote debug log to {filename}", 63)
                except Exception as e:
                    if DEBUG_TO_INGAME_MESSAGE:
                        Misc.SendMessage(f"[GumpDebug] Failed to write debug log: {str(e)}", 33)

def main():
    try:
        debugger = GumpDebugger()
        debugger.run()
        
    except Exception as e:
        Misc.SendMessage(f"Error in Gump Debugger: {str(e)}", 33)
        raise e

if __name__ == "__main__":
    main()
