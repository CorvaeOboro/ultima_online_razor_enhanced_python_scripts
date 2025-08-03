"""
QUEST Turn In Orbs - Razor Enhanced Python Script for Ultima Online

Automates the process of turning in orbs to a Quest NPC, with the following logic:
1. Repeatedly open the NPC gump and press the button to add an orb.
2. Select an orb in inventory (excluding protected types).
3. Continue until 3 orbs are added, or a journal message indicates an orb could not be added.
4. Open the NPC gump again, select the button to convert to the desired orb type.
5. Repeat until there are no available orbs in the backpack (excluding protected types).
6. Debug messages are printed for each orb found, targeted, and each action taken.

HOTKEY: M
VERSION: 20250722
"""

# CONFIG: List of orb names to protect (not to turn in or convert)
PROTECTED_ORBS = [
    'Holy Orb',  
    'Druidic Orb',
    # Add more orb names to protect here
]

# CONFIG: Gump/button IDs (update as needed for your shard/NPC)
NPC_GUMP_ID =  0x70a085be  # Replace with actual gump ID
NPC_SERIAL = 0x00003DEC  # Replace with actual NPC serial
BUTTON_ADD_ORB = 5   # Gump Button to TRADE IN ORB
BUTTON_CLAIM_ORB = 13   # Gump Button to CLAIM ORB

ORB_ITEM_ID = 0x573E  # Mastery Orb item ID

# Mastery Orbs dictionary: name -> {'hue': color, 'id': ORB_ITEM_ID}
MASTERY_ORBS = {
    'Earth Orb':   {'id': ORB_ITEM_ID, 'hue': 0x0B54},
    'Fire Orb':    {'id': ORB_ITEM_ID, 'hue': 0x0026},  # Placeholder hue
    'Water Orb':   {'id': ORB_ITEM_ID, 'hue': 0x005F},  # Placeholder hue
    'Air Orb':     {'id': ORB_ITEM_ID, 'hue': 0x0481},  # Placeholder hue
    'Holy Orb':    {'id': ORB_ITEM_ID, 'hue': 0x09A4},
    'Druidic Orb': {'id': ORB_ITEM_ID, 'hue': 0x0B7A},  # Placeholder hue
    # Add or correct hues as needed
}

#//===========================================================================
def debug_message(msg):
    # Utility: Print debug messages to client
    Misc.SendMessage(f'[OrbTurnIn] {msg}', 54)

# Step 1: Find all orbs in backpack, excluding protected types
# Returns a list of orb items available for turn-in
def get_orbs_in_backpack():
    orbs = Items.FindByID(ORB_ITEM_ID, -1, Player.Backpack.Serial, -1)
    if not orbs:
        return []
    # Items.FindByID may return a single Item or a list
    if isinstance(orbs, list):
        orb_list = orbs
    else:
        orb_list = [orbs]
    # Step 2: Filter out protected orb types
    return [orb for orb in orb_list if orb.Name not in PROTECTED_ORBS]

# Step 3: Open the NPC's quest gump
# Returns True if gump opened successfully, False otherwise
def open_npc_gump():
    npc = Mobiles.FindBySerial(NPC_SERIAL)
    if not npc:
        debug_message("Cannot find Quest NPC!", 33)
        return False
    Mobiles.UseMobile(npc)  # Interact with NPC
    Misc.Pause(1000)
    # Wait for gump to open
    if Gumps.WaitForGump(NPC_GUMP_ID, 3000):
        return True
    debug_message("Failed to open NPC gump.")
    return False

# Step 4: Press a button on the NPC gump
# button_id: which button to press (add orb, claim orb, etc)
def press_gump_button(button_id):
    Gumps.WaitForGump(NPC_GUMP_ID, 3000)
    Gumps.SendAction(NPC_GUMP_ID, button_id)
    Misc.Pause(600)

# Step 5: Add up to 3 orbs to the gump, handling journal messages and claim logic
# stats: dict to track total orbs added/claimed and per-type breakdown
def add_orbs_to_gump(stats):
    added = 0
    while added < 3:
        # Step 1: Get available orbs
        orbs = get_orbs_in_backpack()
        if not orbs:
            debug_message("No more orbs available for turn-in.")
            break
        orb = orbs[0]
        # Step 2: Confirm gump is open before adding
        if not Gumps.HasGump(NPC_GUMP_ID):
            if not open_npc_gump():
                debug_message("Failed to open NPC gump for adding orb.")
                break
        debug_message(f"Targeting orb: {orb.Name}")
        # Step 3: Press add orb button and target orb
        press_gump_button(BUTTON_ADD_ORB)
        Target.WaitForTarget(2000, False)
        Target.TargetExecute(orb.Serial)
        Misc.Pause(800)
        # Step 4: Check for special journal messages
        if Journal.Search("You already traded 3 orbs! Claim one first."):
            debug_message("Claiming one now.")
            # Step 4a: If blocked, claim an orb and reset
            if open_npc_gump():
                press_gump_button(BUTTON_CLAIM_ORB)
                Misc.Pause(1200)
                debug_message("Claimed an orb.")
                Journal.Clear()
                stats['claimed'] += 1
                added = 0
            else:
                debug_message("Failed to open NPC gump to claim orb.")
            continue
        if Journal.Search("could not be added"):
            debug_message("Orb could not be added. Stopping add.")
            break
        # Step 5: Track successful orb submission
        debug_message(f"Orb {orb.Name} submitted.")
        added += 1
        stats['added'] += 1
        orb_type = orb.Name
        if orb_type not in stats['per_type']:
            stats['per_type'][orb_type] = 0
        stats['per_type'][orb_type] += 1
    return added

# Step 6: Press the CLAIM/CONVERT button to claim the reward orb
def convert_orbs():
    press_gump_button(BUTTON_CLAIM_ORB)
    Misc.Pause(1200)
    debug_message("Pressed convert button.")

def main():
    stats = {'added': 0, 'claimed': 0, 'per_type': {}}
    while True:
        orbs = get_orbs_in_backpack()
        if not orbs:
            debug_message("No orbs left to turn in. Exiting.")
            break
        if not open_npc_gump():
            debug_message("Could not open NPC gump. Exiting.")
            break
        add_orbs_to_gump(stats)
    # Summary reporting
    debug_message(f"Summary: Total orbs added: {stats['added']}, Total claimed: {stats['claimed']}")
    for orb_type, count in stats['per_type'].items():
        debug_message(f"  {orb_type}: {count} added")

if __name__ == '__main__':
    main()
