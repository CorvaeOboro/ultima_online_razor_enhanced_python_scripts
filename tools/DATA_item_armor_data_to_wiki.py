"""
DATA Armor Data to Wiki - External Processing Tool

Processes the universal JSON database created by DEV_item_armor_data.py
Creates wiki tables and analysis reports from armor testing data

Features:
- Master table with all item/modifier combinations
- Conflict detection for inconsistent data
- Sample count verification
- Statistical analysis of AR modifiers

VERSION:: 20250902
"""

import json
import os
import sys
from collections import defaultdict, Counter
from datetime import datetime

# Configuration
INPUT_FILE = "../data/armor_universal_database.json"
OUTPUT_DIR = "../wiki"
DEBUG_MODE = True

# Table Generation Toggles
GENERATE_MASTER_TABLE = True      # Detailed development table with all data
GENERATE_ARMOR_COMPARE = True     # Wiki table for armor (excludes shields)
GENERATE_SHIELDS_COMPARE = True   # Wiki table for shields only
GENERATE_TYPE_SPECIFIC = True     # Individual tables for each armor type
GENERATE_CONFLICT_REPORT = True   # Data validation report
GENERATE_STATS_REPORT = True      # Statistical analysis

def debug_msg(message):
    """Debug message output"""
    if DEBUG_MODE:
        print(f"[DATA_PROCESSOR] {message}")

def get_armor_type(item_name):
    """Determine armor type from item name"""
    item_lower = item_name.lower()
    
    # Check for specific armor types (order matters - check studded first)
    if 'studded' in item_lower:
        return 'Studded'
    elif 'leather' in item_lower:
        return 'Leather'
    elif any(keyword in item_lower for keyword in ['ring', 'ringmail']):
        return 'Ringmail'
    elif any(keyword in item_lower for keyword in ['bone']):
        return 'Bone'
    elif any(keyword in item_lower for keyword in ['chain', 'chainmail']):
        return 'Chainmail'
    elif any(keyword in item_lower for keyword in ['plate', 'platemail', 'helmet', 'helm', 'bascinet', 'close helm', 'norse helm', 'great helm']):
        return 'Platemail'
    else:
        return 'Other'

def load_armor_data():
    """Load armor data from universal JSON database"""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        input_path = os.path.join(script_dir, INPUT_FILE)
        
        if not os.path.exists(input_path):
            debug_msg(f"Input file not found: {input_path}")
            return None
        
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        debug_msg(f"Loaded {len(data.get('armor_entries', []))} armor entries")
        return data
        
    except Exception as e:
        debug_msg(f"Error loading armor data: {e}")
        return None

def analyze_armor_data(armor_entries):
    """Analyze armor data for patterns and conflicts"""
    # Group by item_id + ar_modifiers combination
    item_combinations = defaultdict(list)
    conflicts = []
    
    for entry in armor_entries:
        item_id = entry.get('item_id', 'unknown')
        item_name = entry.get('item_name', 'Unknown')
        layer = entry.get('layer', 'Unknown')
        ar_modifiers = tuple(sorted(entry.get('ar_modifiers', [])))
        quality_modifiers = tuple(sorted(entry.get('quality_modifiers', [])))
        deltas = entry.get('deltas', {})
        
        # Create unique key for item + AR modifiers
        key = (item_id, ar_modifiers)
        item_combinations[key].append({
            'item_name': item_name,
            'layer': layer,
            'ar_modifiers': ar_modifiers,
            'quality_modifiers': quality_modifiers,
            'ar_delta': deltas.get('ar_delta', 0),
            'dex_delta': deltas.get('dex_delta', 0),
            'str_delta': deltas.get('str_delta', 0),
            'int_delta': deltas.get('int_delta', 0),
            'timestamp': entry.get('timestamp', '')
        })
    
    # Check for conflicts (same item+modifier with different AR values)
    for key, entries in item_combinations.items():
        if len(entries) > 1:
            ar_values = [e['ar_delta'] for e in entries]
            if len(set(ar_values)) > 1:
                conflicts.append({
                    'item_id': key[0],
                    'ar_modifiers': key[1],
                    'item_name': entries[0]['item_name'],
                    'ar_values': ar_values,
                    'sample_count': len(entries)
                })
    
    return item_combinations, conflicts

def create_master_table(item_combinations):
    """Create master wiki table with all item/modifier combinations"""
    table_lines = []
    
    # Header
    table_lines.append("{| class=\"wikitable sortable\"")
    table_lines.append("! Item Name !! Item ID !! Layer !! AR Modifiers !! Quality Modifiers !! AR Bonus !! DEX Penalty !! STR Penalty !! INT Penalty !! Sample Count")
    table_lines.append("|-")
    
    # Sort by item name, then by AR modifier
    sorted_items = sorted(item_combinations.items(), key=lambda x: (x[1][0]['item_name'], x[0][1]))
    
    for key, entries in sorted_items:
        item_id, ar_modifiers = key
        
        # Calculate averages for multiple samples
        ar_deltas = [e['ar_delta'] for e in entries]
        dex_deltas = [e['dex_delta'] for e in entries]
        str_deltas = [e['str_delta'] for e in entries]
        int_deltas = [e['int_delta'] for e in entries]
        
        avg_ar = sum(ar_deltas) / len(ar_deltas) if ar_deltas else 0
        avg_dex = sum(dex_deltas) / len(dex_deltas) if dex_deltas else 0
        avg_str = sum(str_deltas) / len(str_deltas) if str_deltas else 0
        avg_int = sum(int_deltas) / len(int_deltas) if int_deltas else 0
        
        # Get representative entry data
        entry = entries[0]
        item_name = entry['item_name']
        layer = entry['layer']
        quality_mods = ', '.join(entry['quality_modifiers']) if entry['quality_modifiers'] else '-'
        ar_mods = ', '.join(ar_modifiers) if ar_modifiers else 'None'
        
        # Format penalties (show only if non-zero)
        dex_penalty = f"{avg_dex:+.0f}" if avg_dex != 0 else "-"
        str_penalty = f"{avg_str:+.0f}" if avg_str != 0 else "-"
        int_penalty = f"{avg_int:+.0f}" if avg_int != 0 else "-"
        
        table_lines.append(f"| {item_name} || {item_id} || {layer} || {ar_mods} || {quality_mods} || {avg_ar:+.0f} || {dex_penalty} || {str_penalty} || {int_penalty} || {len(entries)}")
        table_lines.append("|-")
    
    table_lines.append("|}") 
    
    return '\n'.join(table_lines)

def create_armor_compare_table(item_combinations):
    """Create ARMOR_COMPARE wikitable showing base AR and modifier columns (excludes shields)"""
    return _create_compare_table(item_combinations, exclude_layers={'LeftHand', 'RightHand'}, table_title="ARMOR_COMPARE")

def create_shields_compare_table(item_combinations):
    """Create SHIELDS_COMPARE wikitable showing base AR and modifier columns (shields only)"""
    return _create_compare_table(item_combinations, include_layers={'LeftHand', 'RightHand'}, table_title="SHIELDS_COMPARE")

def create_type_specific_tables(item_combinations):
    """Create individual wikitables for each armor type"""
    type_tables = {}
    
    # Get all armor types from the data
    armor_types = set()
    for entries in item_combinations.values():
        entry = entries[0]
        armor_type = get_armor_type(entry['item_name'])
        armor_types.add(armor_type)
    
    # Create table for each type
    for armor_type in sorted(armor_types):
        if armor_type == 'Other':  # Skip 'Other' category for type-specific tables
            continue
            
        table_content = _create_type_filtered_table(item_combinations, armor_type)
        if table_content:
            type_tables[armor_type] = table_content
    
    return type_tables

def _create_type_filtered_table(item_combinations, target_type):
    """Create a wikitable filtered by armor type"""
    # Filter items by armor type
    filtered_combinations = {}
    
    for key, entries in item_combinations.items():
        entry = entries[0]
        armor_type = get_armor_type(entry['item_name'])
        
        if armor_type == target_type:
            filtered_combinations[key] = entries
    
    if not filtered_combinations:
        return None
    
    # Use the existing compare table logic with filtered data
    return _create_compare_table(filtered_combinations, table_title=f"{target_type.upper()}_COMPARE")

def _create_compare_table(item_combinations, exclude_layers=None, include_layers=None, table_title="COMPARE"):
    """Internal function to create compare tables with layer filtering"""
    # Get all possible AR modifiers from the data
    all_ar_modifiers = set()
    item_data = {}
    
    for key, entries in item_combinations.items():
        item_id, ar_modifiers = key
        entry = entries[0]  # Representative entry
        item_name = entry['item_name']
        layer = entry['layer']
        
        # Apply layer filtering
        if exclude_layers and layer in exclude_layers:
            continue
        if include_layers and layer not in include_layers:
            continue
        
        # Calculate average AR for this combination
        ar_deltas = [e['ar_delta'] for e in entries]
        dex_deltas = [e['dex_delta'] for e in entries]
        avg_ar = sum(ar_deltas) / len(ar_deltas) if ar_deltas else 0
        avg_dex = sum(dex_deltas) / len(dex_deltas) if dex_deltas else 0
        
        # Skip items with 0 AR bonus
        if avg_ar == 0:
            continue
            
        # Track all AR modifiers
        for mod in ar_modifiers:
            all_ar_modifiers.add(mod)
        
        # Group by item (ignore modifiers for grouping)
        item_key = (item_id, item_name, layer)
        if item_key not in item_data:
            item_data[item_key] = {}
        
        # Store AR value for this modifier combination
        mod_key = tuple(sorted(ar_modifiers)) if ar_modifiers else ()
        item_data[item_key][mod_key] = {
            'ar': avg_ar,
            'dex': avg_dex,
            'sample_count': len(entries)
        }
    
    # Return empty if no data after filtering
    if not item_data:
        return f"No {table_title.lower()} data available."
    
    # Sort AR modifiers for consistent column order
    sorted_ar_modifiers = sorted(all_ar_modifiers)
    
    # Create table
    table_lines = []
    table_lines.append("{| class=\"wikitable sortable\"")
    
    # Header - Type, Layer, Name, Base AR + each modifier + DEX penalty
    header = "! Type !! Layer !! Item Name !! Base AR"
    for modifier in sorted_ar_modifiers:
        header += f" !! {modifier} AR"
    header += " !! DEX Penalty"
    table_lines.append(header)
    table_lines.append("|-")
    
    # Sort items by name
    sorted_items = sorted(item_data.items(), key=lambda x: x[0][1])  # Sort by item_name
    
    for item_key, modifier_data in sorted_items:
        item_id, item_name, layer = item_key
        
        # Get base AR (no modifiers)
        base_ar = modifier_data.get((), {}).get('ar', '???')
        base_dex = modifier_data.get((), {}).get('dex', 0)
        
        # Skip if no base AR data
        if base_ar == '???' and len(modifier_data) == 0:
            continue
            
        # Get armor type
        armor_type = get_armor_type(item_name)
        
        # Start row with Type, Layer, Name
        row = f"| {armor_type} || {layer} || {item_name} || "
        
        # Base AR (remove + sign)
        if base_ar == '???':
            row += "???"
        else:
            row += f"{base_ar:.0f}"
        
        # Each modifier column (remove + sign)
        for modifier in sorted_ar_modifiers:
            mod_key = (modifier,)  # Single modifier tuple
            if mod_key in modifier_data:
                ar_value = modifier_data[mod_key]['ar']
                row += f" || {ar_value:.0f}"
            else:
                row += " || ???"
        
        # DEX penalty (space instead of dash when no penalty)
        dex_penalty = " "
        if base_dex != 0:
            dex_penalty = f"{base_dex:+.0f}"
        elif modifier_data:  # Use first available if no base
            first_data = next(iter(modifier_data.values()))
            if first_data['dex'] != 0:
                dex_penalty = f"{first_data['dex']:+.0f}"
        
        row += f" || {dex_penalty}"
        
        table_lines.append(row)
        table_lines.append("|-")
    
    table_lines.append("|}")
    
    return '\n'.join(table_lines)

def create_conflict_report(conflicts):
    """Create conflict report for data validation"""
    if not conflicts:
        return "## Data Validation\n\n**No conflicts detected** - All item/modifier combinations show consistent values.\n"
    
    report_lines = []
    report_lines.append("## Data Validation - Conflicts Detected")
    report_lines.append("")
    report_lines.append("The following items show inconsistent AR values for the same modifier combination:")
    report_lines.append("")
    
    for conflict in conflicts:
        ar_mods = ', '.join(conflict['ar_modifiers']) if conflict['ar_modifiers'] else 'None'
        ar_vals = ', '.join(map(str, conflict['ar_values']))
        report_lines.append(f"* **{conflict['item_name']}** ({conflict['item_id']}) with {ar_mods}")
        report_lines.append(f"  - AR values: {ar_vals} (from {conflict['sample_count']} samples)")
        report_lines.append("")
    
    return '\n'.join(report_lines)

def create_statistics_report(item_combinations, armor_entries):
    """Create statistical analysis report"""
    report_lines = []
    report_lines.append("## Statistical Analysis")
    report_lines.append("")
    
    # Total counts
    total_entries = len(armor_entries)
    unique_combinations = len(item_combinations)
    
    # AR modifier frequency
    ar_modifier_counts = Counter()
    quality_modifier_counts = Counter()
    layer_counts = Counter()
    
    for entries in item_combinations.values():
        entry = entries[0]  # Representative entry
        for mod in entry['ar_modifiers']:
            ar_modifier_counts[mod] += 1
        for mod in entry['quality_modifiers']:
            quality_modifier_counts[mod] += 1
        layer_counts[entry['layer']] += 1
    
    report_lines.append(f"* **Total test samples**: {total_entries}")
    report_lines.append(f"* **Unique item/modifier combinations**: {unique_combinations}")
    report_lines.append("")
    
    # Data sampling progress analysis
    report_lines.extend(_create_sampling_progress_analysis(item_combinations))
    
    # AR modifier effectiveness analysis
    report_lines.extend(create_ar_modifier_effectiveness_analysis(item_combinations))
    
    # AR Modifiers frequency
    if ar_modifier_counts:
        report_lines.append("### AR Modifier Frequency")
        for modifier, count in ar_modifier_counts.most_common():
            report_lines.append(f"* **{modifier}**: {count} items")
        report_lines.append("")
    
    # Quality Modifiers frequency  
    if quality_modifier_counts:
        report_lines.append("### Quality Modifier Frequency")
        for modifier, count in quality_modifier_counts.most_common():
            report_lines.append(f"* **{modifier}**: {count} items")
        report_lines.append("")
    
    # Layer distribution
    report_lines.append("### Equipment Layer Distribution")
    for layer, count in layer_counts.most_common():
        report_lines.append(f"* **{layer}**: {count} items")
    
    return '\n'.join(report_lines)

def create_ar_modifier_effectiveness_analysis(item_combinations):
    """Calculate average percentage increase for AR modifiers"""
    analysis_lines = []
    analysis_lines.append("### AR Modifier Effectiveness Analysis")
    analysis_lines.append("")
    
    # Collect data for analysis
    modifier_data = {}  # modifier -> list of (base_ar, modified_ar, type, layer)
    
    # Get all unique items and their modifier combinations
    item_data = {}
    for key, entries in item_combinations.items():
        item_id, ar_modifiers = key
        entry = entries[0]
        item_name = entry['item_name']
        layer = entry['layer']
        armor_type = get_armor_type(item_name)
        
        # Calculate average AR for this combination
        ar_deltas = [e['ar_delta'] for e in entries]
        avg_ar = sum(ar_deltas) / len(ar_deltas) if ar_deltas else 0
        
        # Skip items with 0 AR
        if avg_ar == 0:
            continue
        
        # Group by item (ignore modifiers for grouping)
        item_key = (item_id, item_name, layer, armor_type)
        if item_key not in item_data:
            item_data[item_key] = {}
        
        # Store AR value for this modifier combination
        mod_key = tuple(sorted(ar_modifiers)) if ar_modifiers else ()
        item_data[item_key][mod_key] = avg_ar
    
    # Calculate percentage increases for each modifier
    for item_key, mod_combinations in item_data.items():
        item_id, item_name, layer, armor_type = item_key
        
        # Get base AR (no modifiers)
        base_ar = mod_combinations.get((), None)
        if base_ar is None or base_ar == 0:
            continue
        
        # Calculate percentage increase for each single modifier
        for mod_key, modified_ar in mod_combinations.items():
            if len(mod_key) == 1:  # Only single modifiers
                modifier = mod_key[0]
                pct_increase = ((modified_ar - base_ar) / base_ar) * 100
                
                if modifier not in modifier_data:
                    modifier_data[modifier] = []
                
                modifier_data[modifier].append({
                    'base_ar': base_ar,
                    'modified_ar': modified_ar,
                    'pct_increase': pct_increase,
                    'armor_type': armor_type,
                    'layer': layer,
                    'item_name': item_name
                })
    
    # Calculate overall averages for each modifier
    analysis_lines.append("#### Overall AR Modifier Effectiveness")
    for modifier in sorted(modifier_data.keys()):
        data_points = modifier_data[modifier]
        avg_pct = sum(d['pct_increase'] for d in data_points) / len(data_points)
        sample_count = len(data_points)
        analysis_lines.append(f"* **{modifier}**: {avg_pct:.1f}% average increase ({sample_count} samples)")
    analysis_lines.append("")
    
    # Calculate averages by armor type
    analysis_lines.append("#### AR Modifier Effectiveness by Armor Type")
    for modifier in sorted(modifier_data.keys()):
        analysis_lines.append(f"**{modifier}:**")
        
        # Group by armor type
        type_data = {}
        for data_point in modifier_data[modifier]:
            armor_type = data_point['armor_type']
            if armor_type not in type_data:
                type_data[armor_type] = []
            type_data[armor_type].append(data_point['pct_increase'])
        
        for armor_type in sorted(type_data.keys()):
            pct_increases = type_data[armor_type]
            avg_pct = sum(pct_increases) / len(pct_increases)
            analysis_lines.append(f"  - {armor_type}: {avg_pct:.1f}% ({len(pct_increases)} samples)")
        analysis_lines.append("")
    
    # Calculate averages by layer
    analysis_lines.append("#### AR Modifier Effectiveness by Layer")
    for modifier in sorted(modifier_data.keys()):
        analysis_lines.append(f"**{modifier}:**")
        
        # Group by layer
        layer_data = {}
        for data_point in modifier_data[modifier]:
            layer = data_point['layer']
            if layer not in layer_data:
                layer_data[layer] = []
            layer_data[layer].append(data_point['pct_increase'])
        
        for layer in sorted(layer_data.keys()):
            pct_increases = layer_data[layer]
            avg_pct = sum(pct_increases) / len(pct_increases)
            analysis_lines.append(f"  - {layer}: {avg_pct:.1f}% ({len(pct_increases)} samples)")
        analysis_lines.append("")
    
    return analysis_lines

def _create_sampling_progress_analysis(item_combinations):
    """Create data sampling progress analysis"""
    progress_lines = []
    progress_lines.append("### Data Sampling Progress")
    progress_lines.append("")
    
    # Get all unique AR modifiers from the data
    all_ar_modifiers = set()
    for entries in item_combinations.values():
        entry = entries[0]
        for mod in entry['ar_modifiers']:
            all_ar_modifiers.add(mod)
    
    # Calculate total possible combinations (base + each individual modifier)
    # Base (no modifiers) + each individual AR modifier = total combinations per item
    total_possible_per_item = 1 + len(all_ar_modifiers)  # 1 for base, + each modifier
    
    # Group by unique items (ignore modifiers for grouping)
    item_progress = {}
    for key, entries in item_combinations.items():
        item_id, ar_modifiers = key
        entry = entries[0]
        item_name = entry['item_name']
        layer = entry['layer']
        
        item_key = (item_id, item_name, layer)
        if item_key not in item_progress:
            item_progress[item_key] = {
                'tested_combinations': set(),
                'item_name': item_name,
                'layer': layer
            }
        
        # Add this combination to tested set
        mod_key = tuple(sorted(ar_modifiers)) if ar_modifiers else ()
        item_progress[item_key]['tested_combinations'].add(mod_key)
    
    # Calculate completion percentages
    completion_stats = []
    total_completion = 0
    
    for item_key, data in item_progress.items():
        tested_count = len(data['tested_combinations'])
        completion_pct = (tested_count / total_possible_per_item) * 100
        total_completion += completion_pct
        
        completion_stats.append({
            'item_name': data['item_name'],
            'layer': data['layer'],
            'tested': tested_count,
            'total_possible': total_possible_per_item,
            'completion_pct': completion_pct
        })
    
    # Calculate total progress across all items
    total_tested_combinations = sum(len(data['tested_combinations']) for data in item_progress.values())
    total_possible_combinations = len(completion_stats) * total_possible_per_item
    overall_progress_pct = (total_tested_combinations / total_possible_combinations) * 100 if total_possible_combinations > 0 else 0
    
    # Overall progress
    avg_completion = total_completion / len(completion_stats) if completion_stats else 0
    progress_lines.append(f"**Total Progress**: {overall_progress_pct:.1f}% ({total_tested_combinations}/{total_possible_combinations} total combinations)")
    progress_lines.append(f"**Average Progress**: {avg_completion:.1f}% average completion across all armor items")
    progress_lines.append(f"**Total Possible Combinations**: {total_possible_per_item} per item (Base + {len(all_ar_modifiers)} AR modifiers)")
    progress_lines.append("")
    
    # Sort by completion percentage (lowest first to highlight gaps)
    completion_stats.sort(key=lambda x: x['completion_pct'])
    
    # Show items with lowest completion first
    progress_lines.append("#### Items Needing More Testing (sorted by completion %)")
    for stat in completion_stats:
        if stat['completion_pct'] < 100:
            progress_lines.append(f"* **{stat['item_name']}** ({stat['layer']}): {stat['tested']}/{stat['total_possible']} combinations ({stat['completion_pct']:.1f}%)")
    
    # Show completed items
    completed_items = [s for s in completion_stats if s['completion_pct'] == 100]
    if completed_items:
        progress_lines.append("")
        progress_lines.append(f"#### Fully Tested Items ({len(completed_items)} items)")
        for stat in completed_items:
            progress_lines.append(f"* **{stat['item_name']}** ({stat['layer']}): Complete")
    
    progress_lines.append("")
    progress_lines.append(f"**Summary**: {len(completed_items)}/{len(completion_stats)} items fully tested ({len(completed_items)/len(completion_stats)*100:.1f}%)")
    progress_lines.append("")
    
    return progress_lines

def save_wiki_output(content, filename):
    """Save content to wiki output file"""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(script_dir, OUTPUT_DIR)
        
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        
        filepath = os.path.join(output_path, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        debug_msg(f"Saved wiki output: {filepath}")
        return filepath
        
    except Exception as e:
        debug_msg(f"Error saving wiki output: {e}")
        return None

def main():
    """Main processing function"""
    debug_msg("Starting armor data processing...")
    
    # Load data
    data = load_armor_data()
    if not data:
        debug_msg("Failed to load armor data - exiting")
        return
    
    armor_entries = data.get('armor_entries', [])
    metadata = data.get('metadata', {})
    
    debug_msg(f"Processing {len(armor_entries)} armor entries")
    debug_msg(f"Database last updated: {metadata.get('last_updated', 'Unknown')}")
    
    # Analyze data
    item_combinations, conflicts = analyze_armor_data(armor_entries)
    
    # Create outputs based on toggles
    outputs = {}
    
    if GENERATE_MASTER_TABLE:
        outputs['master_table'] = create_master_table(item_combinations)
    
    if GENERATE_ARMOR_COMPARE:
        outputs['armor_compare_table'] = create_armor_compare_table(item_combinations)
    
    if GENERATE_SHIELDS_COMPARE:
        outputs['shields_compare_table'] = create_shields_compare_table(item_combinations)
    
    if GENERATE_TYPE_SPECIFIC:
        outputs['type_specific_tables'] = create_type_specific_tables(item_combinations)
    
    if GENERATE_CONFLICT_REPORT:
        outputs['conflict_report'] = create_conflict_report(conflicts)
    
    if GENERATE_STATS_REPORT:
        outputs['stats_report'] = create_statistics_report(item_combinations, armor_entries)
    
    # Build wiki content based on enabled outputs
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    wiki_sections = []
    wiki_sections.append(f"# Armor Data Analysis Report")
    wiki_sections.append(f"Generated: {timestamp}")
    wiki_sections.append(f"Database entries: {len(armor_entries)}")
    wiki_sections.append("")
    
    if 'armor_compare_table' in outputs:
        wiki_sections.append("## Armor Table")
        wiki_sections.append("")
        wiki_sections.append(outputs['armor_compare_table'])
        wiki_sections.append("")
    
    if 'shields_compare_table' in outputs:
        wiki_sections.append("## Shields Table")
        wiki_sections.append("")
        wiki_sections.append(outputs['shields_compare_table'])
        wiki_sections.append("")
    
    if 'type_specific_tables' in outputs:
        for armor_type, table_content in outputs['type_specific_tables'].items():
            wiki_sections.append(f"## {armor_type.upper()} Armor Table")
            wiki_sections.append("")
            wiki_sections.append(table_content)
            wiki_sections.append("")
    
    if 'master_table' in outputs:
        wiki_sections.append("## Full Item Data Table")
        wiki_sections.append("")
        wiki_sections.append(outputs['master_table'])
        wiki_sections.append("")
    
    if 'conflict_report' in outputs:
        wiki_sections.append(outputs['conflict_report'])
        wiki_sections.append("")
    
    if 'stats_report' in outputs:
        wiki_sections.append(outputs['stats_report'])
        wiki_sections.append("")
    
    # Add data source info
    wiki_sections.append("## Data Source")
    wiki_sections.append(f"* Source: armor_universal_database.json")
    wiki_sections.append(f"* Last updated: {metadata.get('last_updated', 'Unknown')}")
    wiki_sections.append(f"* Script version: {metadata.get('script_version', 'Unknown')}")
    
    wiki_content = '\n'.join(wiki_sections)
    
    # Save main report
    save_wiki_output(wiki_content, "Armor_Data_Analysis.txt")
    
    # Save individual tables if enabled
    if GENERATE_ARMOR_COMPARE and 'armor_compare_table' in outputs:
        armor_compare_content = f"""# ARMOR_COMPARE Table
Generated: {timestamp}

{outputs['armor_compare_table']}

## Notes
* Type: Armor material type (Leather, Ring, Studded, Bone, Chain, Plate, Other)
* Base AR: Armor rating with no AR modifiers
* ??? indicates no data available for that combination
* DEX Penalty: Dexterity reduction when wearing the item (space = no penalty)
* Items with 0 AR bonus are excluded
* Shields (LeftHand/RightHand layers) are excluded
"""
        save_wiki_output(armor_compare_content, "ARMOR_COMPARE.txt")
    
    if GENERATE_SHIELDS_COMPARE and 'shields_compare_table' in outputs:
        shields_compare_content = f"""# SHIELDS_COMPARE Table
Generated: {timestamp}

{outputs['shields_compare_table']}

## Notes
* Type: Armor material type (Leather, Ring, Studded, Bone, Chain, Plate, Other)
* Base AR: Armor rating with no AR modifiers
* ??? indicates no data available for that combination
* DEX Penalty: Dexterity reduction when wearing the item (space = no penalty)
* Items with 0 AR bonus are excluded
* Only shields (LeftHand/RightHand layers) are included
"""
        save_wiki_output(shields_compare_content, "SHIELDS_COMPARE.txt")
    
    # Note: Type-specific tables are now included in main analysis file, not separate files
    
    # Summary
    debug_msg(f"Processing complete!")
    debug_msg(f"- Processed {len(armor_entries)} total samples")
    debug_msg(f"- Found {len(item_combinations)} unique item/modifier combinations")
    debug_msg(f"- Detected {len(conflicts)} data conflicts")
    debug_msg(f"- Generated tables: {', '.join([k.replace('_', ' ').title() for k in outputs.keys()])}")
    
    # Show toggle status
    toggles = {
        'Master Table': GENERATE_MASTER_TABLE,
        'Armor Compare': GENERATE_ARMOR_COMPARE,
        'Shields Compare': GENERATE_SHIELDS_COMPARE,
        'Type Specific': GENERATE_TYPE_SPECIFIC,
        'Conflict Report': GENERATE_CONFLICT_REPORT,
        'Stats Report': GENERATE_STATS_REPORT
    }
    enabled_toggles = [name for name, enabled in toggles.items() if enabled]
    debug_msg(f"- Enabled outputs: {', '.join(enabled_toggles)}")

if __name__ == '__main__':
    main()