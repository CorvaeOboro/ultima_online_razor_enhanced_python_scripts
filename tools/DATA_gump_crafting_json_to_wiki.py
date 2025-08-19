"""
DATA gump crafting json to wiki converter

This is NOT a Razor Enhanced script. It is a Python utility to convert the
output JSON from `scripts/DEV_crafting_gump_crawler.py` into MediaWiki markup.

It produces:
- A top category index table linking to per-category anchors
- Per-category sections with a sortable table of items and fields
- A global materials totals table, listing how many times each material is used
  and which items (with links to their category anchors) consume it.
  
Usage:
  python tools/DEV_gump_crafting_json_to_wiki.py \
    -i "D:\\ULTIMA\\SCRIPTS\\RazorEnhanced_Python\\data\\gump_crafting_YYYYMMDDHHMMSS.json" \
    -o "D:\\ULTIMA\\SCRIPTS\\RazorEnhanced_Python\\wiki\\gump_crafting_YYYYMMDDHHMMSS.wiki.txt"

SORTABLE TABLE EXAMPLE =
```
{| class="wikitable sortable"
|-
! name
! data
! more data
|-
| cats
| 273
| 53
|-
| dogs
| 65
| 8,492
|-
| mice
| 1,649
| 548
|}
```

VERSION:: 20250819
"""
import argparse
import json
import os
import sys
from collections import defaultdict, Counter

def _script_parent_paths():
    """Return (project_root, data_dir, wiki_dir) based on this script's location.
    tools/DEV_gump_crafting_json_to_wiki.py -> project_root is parent of tools/
    """
    here = os.path.abspath(os.path.dirname(__file__))
    project_root = os.path.abspath(os.path.join(here, os.pardir))
    data_dir = os.path.join(project_root, 'data')
    wiki_dir = os.path.join(project_root, 'wiki')
    return project_root, data_dir, wiki_dir

def _find_latest_crafting_json(data_dir: str) -> str:
    """Find the most recently modified JSON file in data_dir with prefix 'gump_crafting'."""
    if not os.path.isdir(data_dir):
        return None
    candidates = []
    try:
        for name in os.listdir(data_dir):
            if not name.lower().endswith('.json'):
                continue
            if not name.lower().startswith('gump_crafting'):
                continue
            full = os.path.join(data_dir, name)
            try:
                mtime = os.path.getmtime(full)
            except Exception:
                continue
            candidates.append((mtime, full))
    except Exception:
        return None
    if not candidates:
        return None
    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]

def _read_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def _normalize_items(json_root):
    """Return a list of flat items from either a flat list or the full crawl structure."""
    # Case 1: already a list of items (OUTPUT_ITEM only mode)
    if isinstance(json_root, list):
        return json_root
    # Case 2: full structure with categories
    items = []
    cats = (json_root or {}).get('categories', {})
    for cat_key, cat_data in cats.items():
        for it in (cat_data.get('items') or []):
            parsed = (it or {}).get('parsed') or {}
            if parsed:
                # ensure category filled
                if 'category' not in parsed:
                    parsed['category'] = cat_key
                items.append(parsed)
    return items

def _anchor_for_category(category: str) -> str:
    # MediaWiki section links typically use the header text; spaces are fine, but
    # we keep it simple and consistent.
    return category

def _escape_cell(val):
    if val is None:
        return ''
    s = str(val)
    # Avoid breaking table syntax with leading pipes
    return s.replace('\n', ' ').replace('\r', ' ')

def _materials_to_string(mats):
    if not mats:
        return ''
    return '; '.join(f"{m.get('name','')} ({m.get('qty','')})" for m in mats)

def _build_category_index(grouped):
    lines = []
    lines.append('{| class="wikitable"')
    lines.append('|-')
    lines.append('! Category')
    lines.append('! Items')
    for cat, items in grouped.items():
        link = f"[[#{_anchor_for_category(cat)}|{cat}]]"
        lines.append('|-')
        lines.append(f"| {link}")
        lines.append(f"| {len(items)}")
    lines.append('|}')
    return '\n'.join(lines)

def _build_category_section(cat, items):
    # Detect optional columns (success/exceptional)
    has_success = any('success_percent' in it and it.get('success_percent') is not None for it in items)
    has_exceptional = any('exceptional_percent' in it and it.get('exceptional_percent') is not None for it in items)

    lines = []
    lines.append(f"== {cat} ==")
    # currently we are hiding the list of items in the category , wikitable is cleaner
    #lines.append(f"; Items (count {len(items)})")
    #for it in sorted(items, key=lambda x: (x.get('name') or '').lower()):
    #    nm = it.get('name') or ''
    #    lines.append(f"* {nm}")
    #lines.append('')

    lines.append('{| class="wikitable sortable"')
    lines.append('|-')
    headers = ['Name', 'ID', 'Skill', 'Materials']

    # dont include success chance/exceptional columns
    # Optionally insert success/exceptional after Skill
    #if has_success:
    #    headers.insert(3, 'Success %')
    #if has_exceptional:
    #    idx = 4 if has_success else 3
    #    headers.insert(idx, 'Exceptional %')
    # Emit header row so the table is sortable
    lines.append('!' + '\n! '.join(headers))

    for it in sorted(items, key=lambda x: (x.get('name') or '').lower()):
        nm = _escape_cell(it.get('name'))
        gid = _escape_cell(it.get('id'))
        skill = _escape_cell(it.get('skill_required'))
        mats = _materials_to_string(it.get('materials'))
        row_parts = [nm, gid, skill]
        if has_success:
            row_parts.append(_escape_cell(it.get('success_percent')))
        if has_exceptional:
            row_parts.append(_escape_cell(it.get('exceptional_percent')))
        row_parts.append(mats)
        lines.append('|-')
        lines.append('| ' + '\n| '.join(row_parts))
    lines.append('|}')
    return '\n'.join(lines)

def _build_materials_totals(grouped):
    # Build global material usage statistics
    usage = Counter()
    used_in = defaultdict(list)  # material -> list of (category, item name)
    for cat, items in grouped.items():
        for it in items:
            nm = it.get('name') or ''
            for m in (it.get('materials') or []):
                mname = m.get('name') or ''
                if not mname:
                    continue
                usage[mname] += 1
                used_in[mname].append((cat, nm))

    lines = []
    lines.append('== Materials Totals ==')
    lines.append(f"; Total distinct materials: {len(usage)}")
    lines.append(f"; Total material mentions: {sum(usage.values())}")
    lines.append('')
    lines.append('{| class="wikitable sortable"')
    lines.append('|-')
    lines.append('! Material')
    lines.append('! Count')
    lines.append('! Used In')
    for mname, cnt in sorted(usage.items(), key=lambda x: (-x[1], x[0].lower())):
        links = []
        for (cat, item) in sorted(used_in[mname], key=lambda x: (x[0].lower(), x[1].lower())):
            link = f"[[#{_anchor_for_category(cat)}|{item}]]"
            links.append(link)
        lines.append('|-')
        lines.append(f"| {mname}")
        lines.append(f"| {cnt}")
        lines.append(f"| {'; '.join(links)}")
    lines.append('|}')
    return '\n'.join(lines)

def _skill_val(v):
    """Coerce skill value to float for sorting. Missing becomes a large sentinel."""
    if v is None:
        return 9999.0
    try:
        return float(v)
    except Exception:
        return 9999.0

def _build_all_items_table(grouped):
    """Build a single combined wikitable (sortable) containing all items across
    categories, sorted by: Skill (asc), then Category (asc), then Name (asc).

    Columns: Category, Name, ID, Skill, [Success %, Exceptional %], Materials
    """
    # Flatten items with their category
    flat = []
    for cat, items in grouped.items():
        for it in items:
            flat.append((cat, it))

    # Determine optional columns
    has_success = any('success_percent' in it and it.get('success_percent') is not None for _, it in flat)
    has_exceptional = any('exceptional_percent' in it and it.get('exceptional_percent') is not None for _, it in flat)

    # Sort by skill -> category -> name
    flat.sort(key=lambda ci: (_skill_val(ci[1].get('skill_required')), (ci[0] or '').lower(), (ci[1].get('name') or '').lower()))

    lines = []
    lines.append('=== All Items (Combined) ===')
    lines.append('{| class="wikitable sortable"')
    lines.append('|-')
    headers = ['Category', 'Name', 'ID', 'Skill', 'Materials']
    if has_success:
        headers.insert(4, 'Success %')
    if has_exceptional:
        idx = 5 if has_success else 4
        headers.insert(idx, 'Exceptional %')
    lines.append('!' + '\n! '.join(headers))

    for cat, it in flat:
        catc = _escape_cell(cat)
        nm = _escape_cell(it.get('name'))
        gid = _escape_cell(it.get('id'))
        skill = _escape_cell(it.get('skill_required'))
        mats = _materials_to_string(it.get('materials'))
        row = [catc, nm, gid, skill]
        if has_success:
            row.append(_escape_cell(it.get('success_percent')))
        if has_exceptional:
            row.append(_escape_cell(it.get('exceptional_percent')))
        row.append(mats)
        lines.append('|-')
        lines.append('| ' + '\n| '.join(row))
    lines.append('|}')
    return '\n'.join(lines)

def convert_to_wiki(input_path: str) -> str:
    root = _read_json(input_path)
    items = _normalize_items(root)
    # group by category
    grouped = defaultdict(list)
    for it in items:
        cat = it.get('category') or 'Uncategorized'
        grouped[cat].append(it)

    # Build document
    parts = []
    parts.append("= Crafting Recipes =")
    parts.append("")
    parts.append("=== Category Index ===")
    parts.append(_build_category_index(grouped))
    parts.append("")
    parts.append("----")
    # Combined table of all items
    parts.append(_build_all_items_table(grouped))
    parts.append("")
    parts.append("----")
    for cat in sorted(grouped.keys(), key=lambda s: s.lower()):
        parts.append(_build_category_section(cat, grouped[cat]))
        parts.append("")
    # Materials area with separators and a top header
    parts.append("----")
    parts.append("== Materials Sections ==")
    parts.append("")
    parts.append(_build_materials_totals(grouped))
    parts.append("")
    parts.append("")
    return '\n'.join(parts)

def main():
    parser = argparse.ArgumentParser(description="Convert crafting crawler JSON to MediaWiki text")
    parser.add_argument('-i', '--input', default=None, help='Path to input JSON file; if omitted, picks latest gump_crafting*.json in data/')
    parser.add_argument('-o', '--output', default=None, help='Path to output .wiki.txt file; if omitted, writes to wiki/ with same basename')
    args = parser.parse_args()

    project_root, data_dir, wiki_dir = _script_parent_paths()

    # Resolve input path
    if args.input:
        input_path = args.input
    else:
        input_path = _find_latest_crafting_json(data_dir)
        if not input_path:
            print(f"No input provided and no gump_crafting*.json found in: {data_dir}")
            sys.exit(1)
        print(f"Auto-selected latest JSON: {input_path}")
    if not os.path.exists(input_path):
        print(f"Input not found: {input_path}")
        sys.exit(1)

    wiki_text = convert_to_wiki(input_path)

    # Resolve output path
    if args.output:
        out_path = args.output
    else:
        os.makedirs(wiki_dir, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(input_path))[0] + '.wiki.txt'
        out_path = os.path.join(wiki_dir, base_name)
        print(f"Defaulting output to: {out_path}")

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(wiki_text)

    print(f"Wrote wiki text to: {out_path}")

if __name__ == '__main__':
    main()