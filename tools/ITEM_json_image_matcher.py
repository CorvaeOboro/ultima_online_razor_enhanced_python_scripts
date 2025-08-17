"""JSON Image Matcher with GUI

Reads JSON files from the /data directory and searches for matching images
based on ItemID with flexible hexadecimal filename matching.

Features:
- Tkinter GUI for folder selection and operation
- Scans all JSON files in /data directory
- Extracts ItemID values from JSON entries
- Searches target image folder for matching files
- Flexible hex matching: "0x00cb2" matches "0xcb2", "0x0cb2", "0x000cb2", etc.
- Copies matched images to organized subfolders in /data/matching/
- Prevents duplicate copying

VERSION::20250729
"""

import json
import os
import re
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path

# Global Parameters
DEFAULT_DATA_DIR = r"d:\ULTIMA\SCRIPTS\RazorEnhanced_Python\data"
# """D:\ULTIMA\MODS\UOFiddler\EXPORTS\ART_Unchained"""
DEFAULT_IMAGE_DIR = r"D:\ULTIMA\MODS\UOFiddler\EXPORTS\ART_Unchained"
DEBUG_MODE = True

class JSONImageMatcherGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("JSON Image Matcher")
        self.root.geometry("800x600")
        
        # Variables
        self.data_directory = tk.StringVar(value=DEFAULT_DATA_DIR)
        self.image_directory = tk.StringVar(value=DEFAULT_IMAGE_DIR)
        
        # Results storage
        self.json_items = []
        self.matched_items = []
        self.unmatched_items = []
        self.image_files = []
        self.copied_files = []
        
        # Supported image extensions
        self.image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff']
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Data directory selection
        ttk.Label(main_frame, text="Data Directory:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.data_directory, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_data_dir).grid(row=0, column=2, padx=5)
        
        # Image directory selection
        ttk.Label(main_frame, text="Image Directory:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.image_directory, width=50).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_image_dir).grid(row=1, column=2, padx=5)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="Start Matching & Copy", command=self.start_matching).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Log", command=self.clear_log).pack(side=tk.LEFT, padx=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Log area
        ttk.Label(main_frame, text="Log:").grid(row=4, column=0, sticky=(tk.W, tk.N), pady=(10, 0))
        self.log_text = scrolledtext.ScrolledText(main_frame, width=80, height=20)
        self.log_text.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 0))
        
    def browse_data_dir(self):
        directory = filedialog.askdirectory(initialdir=self.data_directory.get())
        if directory:
            self.data_directory.set(directory)
            
    def browse_image_dir(self):
        directory = filedialog.askdirectory(initialdir=self.image_directory.get())
        if directory:
            self.image_directory.set(directory)
            
    def log(self, message):
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def clear_log(self):
        self.log_text.delete(1.0, tk.END)
        
    def start_matching(self):
        self.progress.start()
        self.log("Starting JSON Image Matching and Copy Process...")
        
        try:
            matcher = JSONImageMatcher(self.data_directory.get(), self.image_directory.get(), self.log)
            success = matcher.run_matching_and_copy_process()
            
            if success:
                self.log("\n=== PROCESS COMPLETED SUCCESSFULLY ===")
                messagebox.showinfo("Success", "JSON Image matching and copying completed successfully!")
            else:
                self.log("\n=== PROCESS FAILED OR INCOMPLETE ===")
                messagebox.showwarning("Warning", "Process completed with errors. Check the log for details.")
                
        except Exception as e:
            self.log(f"Error: {str(e)}")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        finally:
            self.progress.stop()

class JSONImageMatcher:
    def __init__(self, data_directory=None, image_directory=None, log_callback=None):
        # Default directories
        self.data_directory = data_directory or DEFAULT_DATA_DIR
        self.image_directory = image_directory or DEFAULT_IMAGE_DIR
        self.log_callback = log_callback or print
        
        # Results storage
        self.json_items = []
        self.matched_items = []
        self.unmatched_items = []
        self.image_files = []
        self.copied_files = []
        
        # Supported image extensions
        self.image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff']
        
    def log(self, message):
        """Log message using callback or print"""
        if self.log_callback:
            self.log_callback(message)
        elif DEBUG_MODE:
            print(f"[JSONImageMatcher] {message}")

    def normalize_hex_id(self, hex_string):
        """Normalize hexadecimal string for comparison"""
        if not hex_string:
            return ""
            
        # Remove '0x' prefix if present
        if hex_string.lower().startswith('0x'):
            hex_string = hex_string[2:]
            
        # Remove leading zeros and convert to lowercase
        normalized = hex_string.lstrip('0').lower()
        
        # If all zeros were removed, keep one zero
        if not normalized:
            normalized = '0'
            
        return normalized

    def create_hex_variants(self, hex_id):
        """Create all possible hex variants for flexible matching"""
        normalized = self.normalize_hex_id(hex_id)
        
        variants = set()
        
        # Add the normalized version
        variants.add(f"0x{normalized}")
        variants.add(normalized)
        
        # Add versions with leading zeros (up to 8 characters)
        for padding in range(1, 9):
            padded = normalized.zfill(padding)
            variants.add(f"0x{padded}")
            variants.add(padded)
            
        return list(variants)

    def scan_json_files(self):
        """Scan all JSON files in the data directory"""
        self.log(f"Scanning JSON files in: {self.data_directory}")
        
        if not os.path.exists(self.data_directory):
            self.log(f"ERROR: Data directory does not exist: {self.data_directory}")
            return False, []
            
        json_files = []
        try:
            for filename in os.listdir(self.data_directory):
                if filename.lower().endswith('.json'):
                    json_files.append(filename)
                    
            self.log(f"Found {len(json_files)} JSON files: {json_files}")
            
            # Process each JSON file
            for json_file in json_files:
                file_path = os.path.join(self.data_directory, json_file)
                self.process_json_file(file_path)
                
            self.log(f"Total items extracted: {len(self.json_items)}")
            return True, json_files
            
        except Exception as e:
            self.log(f"ERROR: Error scanning JSON files: {str(e)}")
            return False, []

    def process_json_file(self, file_path):
        """Process a single JSON file and extract items with ItemIDs"""
        self.log(f"Processing: {os.path.basename(file_path)}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Handle both list and single object formats
            if isinstance(data, list):
                items = data
            elif isinstance(data, dict):
                items = [data]
            else:
                self.log(f"WARNING: Unexpected JSON format in {file_path}")
                return
                
            items_found = 0
            for item in items:
                if isinstance(item, dict) and 'itemID' in item:
                    item_info = {
                        'source_file': os.path.basename(file_path),
                        'name': item.get('name', 'Unknown'),
                        'itemID': item['itemID'],
                        'serial': item.get('serial', ''),
                        'hue': item.get('hue', 0),
                        'timestamp': item.get('timestamp', ''),
                        'properties': item.get('properties', [])
                    }
                    self.json_items.append(item_info)
                    items_found += 1
                    
            self.log(f"  Extracted {items_found} items with ItemIDs")
            
        except Exception as e:
            self.log(f"ERROR: Error processing {file_path}: {str(e)}")

    def scan_image_files(self):
        """Scan all image files in the target directory"""
        self.log(f"Scanning image files in: {self.image_directory}")
        
        if not os.path.exists(self.image_directory):
            self.log(f"WARNING: Image directory does not exist: {self.image_directory}")
            return False
            
        try:
            for filename in os.listdir(self.image_directory):
                file_lower = filename.lower()
                if any(file_lower.endswith(ext) for ext in self.image_extensions):
                    self.image_files.append(filename)
                    
            self.log(f"Found {len(self.image_files)} image files")
            return True
            
        except Exception as e:
            self.log(f"ERROR: Error scanning image files: {str(e)}")
            return False

    def find_matching_images(self):
        """Find matching images for each JSON item"""
        self.log("Matching JSON items to image files...")
        
        for item in self.json_items:
            item_id = item['itemID']
            hex_variants = self.create_hex_variants(item_id)
            
            matched_files = []
            
            # Check each image file against all hex variants
            for image_file in self.image_files:
                # Remove extension for comparison
                filename_base = os.path.splitext(image_file)[0].lower()
                
                # Check direct hex variant matches
                for variant in hex_variants:
                    if variant.lower() == filename_base:
                        matched_files.append(image_file)
                        break
                
                # Also check for "Item " prefixed variants
                if filename_base.startswith("item "):
                    # Remove "item " prefix and check again
                    prefixless_name = filename_base[5:]  # Remove "item " (5 characters)
                    for variant in hex_variants:
                        if variant.lower() == prefixless_name:
                            matched_files.append(image_file)
                            break
                        
            if matched_files:
                match_info = {
                    'item': item,
                    'matched_files': matched_files
                }
                self.matched_items.append(match_info)
                self.log(f"  ✓ {item['name']} ({item_id}) -> {matched_files}")
            else:
                self.unmatched_items.append(item)
                self.log(f"  ✗ {item['name']} ({item_id}) -> No match found")
    
    def copy_matched_images(self, json_files):
        """Copy matched images to organized subfolders based on JSON files"""
        self.log("\nCopying matched images to organized subfolders...")
        
        # Create main matching directory
        matching_dir = os.path.join(self.data_directory, "matching")
        os.makedirs(matching_dir, exist_ok=True)
        
        # Group matched items by source JSON file
        items_by_json = {}
        for match in self.matched_items:
            source_file = match['item']['source_file']
            if source_file not in items_by_json:
                items_by_json[source_file] = []
            items_by_json[source_file].append(match)
        
        total_copied = 0
        total_skipped = 0
        
        for json_file in json_files:
            if json_file in items_by_json:
                # Create subfolder for this JSON file
                json_name = os.path.splitext(json_file)[0]  # Remove .json extension
                subfolder = os.path.join(matching_dir, json_name)
                os.makedirs(subfolder, exist_ok=True)
                
                self.log(f"\nProcessing {json_file} -> {json_name}/")
                
                for match in items_by_json[json_file]:
                    item = match['item']
                    for image_file in match['matched_files']:
                        source_path = os.path.join(self.image_directory, image_file)
                        
                        # Determine destination filename - remove "Item " prefix if present
                        dest_filename = image_file
                        if image_file.lower().startswith("item "):
                            # Remove "Item " prefix (case-insensitive)
                            dest_filename = image_file[5:]  # Remove first 5 characters
                            
                        dest_path = os.path.join(subfolder, dest_filename)
                        
                        try:
                            if os.path.exists(dest_path):
                                self.log(f"  SKIP: {dest_filename} (already exists)")
                                total_skipped += 1
                            else:
                                shutil.copy2(source_path, dest_path)
                                if dest_filename != image_file:
                                    self.log(f"  COPY: {image_file} -> {json_name}/{dest_filename} (prefix removed)")
                                else:
                                    self.log(f"  COPY: {image_file} -> {json_name}/{dest_filename}")
                                self.copied_files.append({
                                    'source': source_path,
                                    'dest': dest_path,
                                    'original_name': image_file,
                                    'dest_name': dest_filename,
                                    'item': item,
                                    'json_file': json_file
                                })
                                total_copied += 1
                        except Exception as e:
                            self.log(f"  ERROR: Failed to copy {image_file}: {str(e)}")
        
        self.log(f"\nCopy Summary: {total_copied} files copied, {total_skipped} files skipped")
        return total_copied, total_skipped

    def generate_report(self):
        """Generate a comprehensive report of the matching results"""
        self.log("\n" + "=" * 60)
        self.log("JSON IMAGE MATCHER REPORT")
        self.log("=" * 60)
        
        self.log(f"Data Directory: {self.data_directory}")
        self.log(f"Image Directory: {self.image_directory}")
        self.log(f"Total JSON Items: {len(self.json_items)}")
        self.log(f"Total Image Files: {len(self.image_files)}")
        self.log(f"Matched Items: {len(self.matched_items)}")
        self.log(f"Unmatched Items: {len(self.unmatched_items)}")
        self.log(f"Files Copied: {len(self.copied_files)}")
        
        if self.matched_items:
            self.log("\nMATCHED ITEMS:")
            for match in self.matched_items:
                item = match['item']
                files = match['matched_files']
                self.log(f"  {item['name']} ({item['itemID']}) -> {', '.join(files)}")
                
        if self.unmatched_items:
            self.log("\nUNMATCHED ITEMS:")
            for item in self.unmatched_items:
                self.log(f"  {item['name']} ({item['itemID']})")
                
        # Show some example hex variants for debugging
        if self.unmatched_items:
            self.log("\nEXAMPLE HEX VARIANTS (for first unmatched item):")
            first_item = self.unmatched_items[0]
            variants = self.create_hex_variants(first_item['itemID'])
            self.log(f"  {first_item['itemID']} -> {variants[:5]}...")  # Show first 5 variants

    def run_matching_and_copy_process(self, custom_image_dir=None):
        """Run the complete matching and copying process"""
        if custom_image_dir:
            self.image_directory = custom_image_dir
            
        self.log("Starting JSON to Image matching and copy process...")
        
        # Step 1: Scan JSON files
        success, json_files = self.scan_json_files()
        if not success:
            self.log("ERROR: Failed to scan JSON files")
            return False
            
        if not self.json_items:
            self.log("WARNING: No items with ItemIDs found in JSON files")
            return False
            
        # Step 2: Scan image files
        if not self.scan_image_files():
            self.log("ERROR: Failed to scan image files")
            return False
            
        # Step 3: Match items to images
        self.find_matching_images()
        
        # Step 4: Copy matched images to organized subfolders
        if self.matched_items:
            copied, skipped = self.copy_matched_images(json_files)
            self.log(f"\nImage copy completed: {copied} copied, {skipped} skipped")
        else:
            self.log("\nNo matched items found - no images to copy")
        
        # Step 5: Generate report
        self.generate_report()
        
        return True

def main():
    """Main function - can be run standalone or with GUI"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--gui':
        # Run with GUI
        root = tk.Tk()
        app = JSONImageMatcherGUI(root)
        root.mainloop()
    else:
        # Run standalone with default directories
        try:
            print("Starting JSON Image Matcher (Standalone Mode)...")
            
            matcher = JSONImageMatcher(DEFAULT_DATA_DIR, DEFAULT_IMAGE_DIR)
            success = matcher.run_matching_and_copy_process()
            
            if success:
                print("\nJSON Image matching and copying completed successfully!")
            else:
                print("\nJSON Image matching and copying failed or incomplete")
                
        except Exception as e:
            print(f"Error in JSON Image Matcher: {str(e)}")

if __name__ == "__main__":
    # Default to GUI mode
    root = tk.Tk()
    app = JSONImageMatcherGUI(root)
    root.mainloop()
