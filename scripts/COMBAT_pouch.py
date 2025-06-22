"""
 COMBAT POUCH STUN BREAK - A Razor Enhanced Python Script for Ultima Online
 
 opens a trapped pouch in inventory to break paralyze
 find by hue , once the trapped pouch is used , it will be normal hue and we must select a different trapped pouch to use
 TODO:
 - include refreshing trap pouch , 
 - include the hue variant range 
 - add check if paralyzed 

 VERSION::20250621
"""
DO_PARALYZE_CHECK = True # set to false if there are other stun effects that arent trackable

pouchType = 0x0E79 # pouch item id
pouchHue = 0x0021 # red alternate = 0x0026
self_pack = Player.Backpack.Serial

def getByItemID(itemid, itemhue, source):
    # Find an item id in backpack and return the item object
    for item in Items.FindBySerial(source).Contains:
        if item.ItemID == itemid and item.Hue == itemhue:
            return item
        else:
            Misc.NoOperation()
            
def usePouch():
    pouch = getByItemID(pouchType, pouchHue, self_pack)
    if pouch is not None:
        Misc.SendMessage('STUN BREAK', 37)
        Items.UseItem(pouch)
    else:
        Misc.SendMessage('NO TRAPPED POUCHES FOUND', 47)
        
usePouch()