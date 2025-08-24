"""
 COMBAT POUCH STUN BREAK - A Razor Enhanced Python Script for Ultima Online
 
 opens a trapped pouch in inventory to break paralyze
 find by hue , once the trapped pouch is used , it will be normal hue and we select a different trapped pouch to use
 TODO:
 - include refreshing trap pouch , 
 - include the hue variant range 
 - add check if paralyzed
 - if not paralyzed and not in combat , and there are unhued pouches then we should cast trap on all untrapped pouches ( like a self restock based on context )

HOTKEY:: D
VERSION::20250714
"""

DO_PARALYZE_CHECK = False # set to false if there are other stun effects that arent trackable
DEBUG_MODE = False
ENABLE_POUCH_REFRESH = False  # Set to False to skip refreshing untrapped pouches

pouchType = 0x0E79 # pouch item id
pouchHue = 0x0021 # red alternate = 0x0026

self_pack = Player.Backpack.Serial

def debug_message(msg, color=67, always=False):
    # always=True will send regardless of DEBUG_MODE (for critical messages)
    if DEBUG_MODE or always:
        Misc.SendMessage(f"[Pouch] {msg}", color)

def get_untrapped_pouches(itemid, trapped_hue, source):
    # Return a list of pouch items that are not trapped (not the trapped hue)
    untrapped = []
    for item in Items.FindBySerial(source).Contains:
        if item.ItemID == itemid and item.Hue != trapped_hue:
            untrapped.append(item)
    return untrapped

def getByItemID(itemid, itemhue, source):
    # Find an item id in backpack and return the item object
    for item in Items.FindBySerial(source).Contains:
        if item.ItemID == itemid and item.Hue == itemhue:
            return item
        else:
            Misc.NoOperation()
            
def refresh_untrapped_pouches():
    try:
        paralyzed = Player.Paralyzed
    except AttributeError:
        debug_message("Could not check Player.Paralyzed; skipping paralysis check.", 33)
        paralyzed = False
    try:
        in_combat = Player.InCombat
    except AttributeError:
        debug_message("Could not check Player.InCombat; skipping combat check.", 33)
        in_combat = False
    if not paralyzed and not in_combat:
        untrapped = get_untrapped_pouches(pouchType, pouchHue, self_pack)
        if untrapped:
            debug_message(f'Refreshing {len(untrapped)} untrapped pouches...')
            for pouch in untrapped:
                Spells.CastMagery('Magic Trap')
                Target.WaitForTarget(2000, False)
                if Target.HasTarget:
                    Target.TargetExecute(pouch)
                    Misc.Pause(1200)  # Wait for spell to finish
                else:
                    debug_message('No target cursor for Magic Trap!', 33)
        else:
            debug_message('No untrapped pouches to refresh.', 68)

def usePouch():
    pouch = getByItemID(pouchType, pouchHue, self_pack)
    if pouch is not None:
        debug_message('STUN BREAK', 37, always=True)
        Items.UseItem(pouch)
    else:
        debug_message('NO TRAPPED POUCHES FOUND', 47, always=True)
        
if ENABLE_POUCH_REFRESH:
    refresh_untrapped_pouches()
usePouch()