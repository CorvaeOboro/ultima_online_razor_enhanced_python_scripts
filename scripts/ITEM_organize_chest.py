"""
ITEM Organize Chest - a Razor Enhanced Python Script for Ultima Online

Organizes items in targeted container by grouping similar items into bins
and distributing them evenly across the container space.

this script is similar to ITEM_organize_backpack.py which is a version specific to the players backpack

These positions are tuned for a "150" container size without scaling items sizes 
the default is "100" container size so you may want to adjust the x and y values for your settings

binning rules:
- Items are grouped by (ItemID, Hue). This separates e.g., red/blue/yellow scrolls into distinct bins.
- Each bin is assigned a region in a grid layout sized to the number of bins.
- Within a bin, items are placed in a compact grid. Stackables consolidate naturally.

TODO:
- add a dict of known graphics with their dimensions and sub region bounding box , we can use this be better pack things like magic scrolls  , or deal with items that have a lot of alpha tranparent canvas

HOTKEY:: CTRL + U
VERSION::20250823
"""
DEBUG_MODE = True  # Set to True to enable debug/info messages

# Items will be placed within [MIN_X..MAX_X] x [MIN_Y..MAX_Y] after applying margins.
MIN_X = 40
MIN_Y = 60
MAX_X = 150
MAX_Y = 150

# Estimated per-item footprint (pixels)
ITEM_CELL_W = 16
ITEM_CELL_H = 16

# SPACING
SPACING_OFFSET = 14  # Pixels between items within a bin
MAX_ROW_SPAN = 8    # Max items per row inside a single bin before wrapping
BIN_MARGIN = 6      # Inner margin inside each bin region
MARGIN_LEFT = 0     # Container outer margins (disabled)
MARGIN_TOP = 0
MARGIN_RIGHT = 0
MARGIN_BOTTOM = 0

#//============================================================

def debug_message(message, color=68):
    """Send a message if DEBUG_MODE is enabled"""
    if DEBUG_MODE:
        Misc.SendMessage(f"[BackpackOrg] {message}", color)

def prompt_for_container():
    """Prompt the player to target a container and return its Serial.
    Returns None if canceled or invalid.
    """
    Misc.SendMessage("Target the container to organize...", 65)
    try:
        target_serial = Target.PromptTarget()
    except:
        return None
    if not target_serial:
        return None
    cont = Items.FindBySerial(target_serial)
    if cont is None:
        Misc.SendMessage("Target is not a valid item.", 33)
        return None
    # Try to open to ensure contents are loaded
    Items.UseItem(cont.Serial)
    Misc.Pause(600)
    return cont.Serial

def fetch_container_items(container_serial):
    """Return a fresh list of items contained in the given container."""
    cont = Items.FindBySerial(container_serial)
    if not cont:
        return []
    # Ensure container is open/updated
    Items.UseItem(cont.Serial)
    Misc.Pause(300)
    return list(cont.Contains) if cont.Contains else []

def build_bins(items):
    """Group items into bins by (ItemID, Hue)."""
    bins_map = {}
    for itm in items:
        hue = itm.Hue if itm.Hue is not None else 0
        key = (itm.ItemID, hue)
        if key not in bins_map:
            bins_map[key] = []
        bins_map[key].append(itm)
    # Convert to list of plain dicts and order by count desc, then ItemID, then Hue
    bin_dicts = [
        {"key": key, "items": item_list, "count": len(item_list)}
        for key, item_list in bins_map.items()
    ]
    ordered = sorted(bin_dicts, key=lambda b: (-b["count"], b["key"][0], b["key"][1]))
    return ordered

def compute_bin_grid(n_bins):
    """Compute a near-square (cols, rows) arrangement for n bins."""
    if n_bins <= 0:
        return (1, 1)
    cols = int(n_bins ** 0.5)
    while cols * cols < n_bins:
        cols += 1
    rows = (n_bins + cols - 1) // cols
    return (cols, rows)

def estimate_bin_weight(bin_obj):
    """Estimate area need for a bin based on item count and item footprint."""
    return max(1, bin_obj["count"]) * (ITEM_CELL_W * ITEM_CELL_H)

def distribute_bins_into_columns(bins, num_cols):
    """Greedy distribution of bins into columns to balance total weight.
    Returns (columns, col_weights) where columns is a list of lists of bins.
    """
    cols = [[] for _ in range(num_cols)]
    weights = [0 for _ in range(num_cols)]
    for b in bins:
        # Place next bin into the lightest column
        idx = min(range(num_cols), key=lambda i: weights[i])
        w = estimate_bin_weight(b)
        cols[idx].append(b)
        weights[idx] += w
    return cols, weights

def layout_bins_and_items(container_serial):
    """Scan the target container, group items into weighted bins, and place them
    into proportionally-sized regions using clear, descriptive variable names."""
    # Compute inner usable size from universal bounds and margins
    usable_width_pixels = max(0, (MAX_X - MIN_X) - (MARGIN_LEFT + MARGIN_RIGHT))
    usable_height_pixels = max(0, (MAX_Y - MIN_Y) - (MARGIN_TOP + MARGIN_BOTTOM))
    inner_width_pixels = max(16, usable_width_pixels)
    inner_height_pixels = max(16, usable_height_pixels)
    inner_origin_x = MIN_X + MARGIN_LEFT
    inner_origin_y = MIN_Y + MARGIN_TOP

    container_items = fetch_container_items(container_serial)
    if not container_items:
        debug_message("No items found in container.", 65)
        return

    bin_list_all = build_bins(container_items)
    num_bins = len(bin_list_all)
    # Choose number of columns based on number of bins (approx sqrt)
    number_of_columns = max(1, min(num_bins, int(round(num_bins ** 0.5))))
    # Distribute bins across columns to balance estimated weights
    columns_bins, column_weights = distribute_bins_into_columns(bin_list_all, number_of_columns)
    total_weight_all_columns = max(1, sum(column_weights))

    # Compute column x-edges proportionally to column weights
    column_pixel_widths = [int(round(inner_width_pixels * (w / float(total_weight_all_columns)))) for w in column_weights]
    # Fix rounding drift to ensure exact tiling across width
    width_pixel_diff = inner_width_pixels - sum(column_pixel_widths)
    if width_pixel_diff != 0 and len(column_pixel_widths) > 0:
        column_pixel_widths[0] += width_pixel_diff
    column_x_edges = [inner_origin_x]
    for column_width in column_pixel_widths:
        column_x_edges.append(column_x_edges[-1] + column_width)

    debug_message(
        f"Organizing {sum(b['count'] for b in bin_list_all)} items into {num_bins} bins across {number_of_columns} columns.",
        65,
    )

    # For each column, stack bins vertically with heights proportional to bin weights within that column
    for column_index, bins_in_column in enumerate(columns_bins):
        column_left_x = column_x_edges[column_index]
        column_right_x = column_x_edges[column_index + 1]
        column_inner_width = max(16, (column_right_x - column_left_x))

        if not bins_in_column:
            continue

        bin_weights_in_column = [estimate_bin_weight(bin_obj) for bin_obj in bins_in_column]
        column_total_weight = max(1, sum(bin_weights_in_column))
        bin_row_pixel_heights = [int(round(inner_height_pixels * (w / float(column_total_weight)))) for w in bin_weights_in_column]
        # Fix rounding drift per column to match full height
        height_pixel_diff = inner_height_pixels - sum(bin_row_pixel_heights)
        if height_pixel_diff != 0 and len(bin_row_pixel_heights) > 0:
            bin_row_pixel_heights[0] += height_pixel_diff
        row_y_edges = [inner_origin_y]
        for row_height in bin_row_pixel_heights:
            row_y_edges.append(row_y_edges[-1] + row_height)

        for row_index, bin_obj in enumerate(bins_in_column):
            region_top_y = row_y_edges[row_index]
            region_bottom_y = row_y_edges[row_index + 1]

            bin_region_origin_x = column_left_x + BIN_MARGIN
            bin_region_origin_y = region_top_y + BIN_MARGIN
            bin_region_width = max(16, (column_right_x - column_left_x) - 2 * BIN_MARGIN)
            bin_region_height = max(16, (region_bottom_y - region_top_y) - 2 * BIN_MARGIN)

            # Sort bin items by stack size (Amount desc), then by Serial for stability
            sorted_bin_items = sorted(bin_obj["items"], key=lambda it: (-getattr(it, 'Amount', 0), it.Serial))

            # Determine items per row from region width and item footprint
            step_x_pixels = max(1, SPACING_OFFSET)
            items_per_row_in_bin = max(1, min(MAX_ROW_SPAN, bin_region_width // max(ITEM_CELL_W, step_x_pixels)))

            for index_in_bin, item_obj in enumerate(sorted_bin_items):
                try:
                    col_index_within_bin = index_in_bin % items_per_row_in_bin
                    row_index_within_bin = index_in_bin // items_per_row_in_bin
                    target_x = bin_region_origin_x + col_index_within_bin * step_x_pixels
                    target_y = bin_region_origin_y + row_index_within_bin * max(1, SPACING_OFFSET)
                    # Re-fetch fresh handle to avoid stale reference after moves
                    fresh_item = Items.FindBySerial(item_obj.Serial)
                    if not fresh_item:
                        continue
                    Items.Move(fresh_item.Serial, container_serial, fresh_item.Amount, target_x, target_y)
                    Misc.Pause(500)
                    if col_index_within_bin == items_per_row_in_bin - 1:
                        Misc.Pause(200)
                except Exception as e:
                    debug_message(f"Move error bin={bin_obj['key']} item={hex(item_obj.Serial)}: {e}", 33)
            # Brief pause between bins to let container settle
            Misc.Pause(200)

def organize_targeted_container():
    cont_serial = prompt_for_container()
    if not cont_serial:
        Misc.SendMessage("Canceled or invalid target.", 33)
        return
    layout_bins_and_items(cont_serial)

def organize_dynamic():
    """Entry point: prompt for container and organize dynamically."""
    debug_message("Starting dynamic container organization...", 65)
    organize_targeted_container()

def main():
    organize_dynamic()

if __name__ == "__main__":
    main()
