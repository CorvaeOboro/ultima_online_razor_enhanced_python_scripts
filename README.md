# Ultima Online Classic Razor Enhanced Python Scripts 
[ultima online classic](https://github.com/ClassicUO/ClassicUO) [razor enhanced](https://github.com/razorenhanced/razorenhanced) python scripts focused on UI customization and ritual magic

- each script is self-contained and can be run independently 
- many of the scripts are work in progress

# CATEGORIES
- [UI](#UI) = user interface displays using custom gumps
- [RITUAL](#RITUAL) = place items in world creating patterns
- [ITEM](#ITEM) = item and container management
- [MISC](#MISC) = miscellaneous interaction
- [SPELL](#SPELL) = spell casting
- [TRAIN](#TRAIN) = training skills
- [GATHER](#GATHER) = gather items from the world
- [DEV](#DEV) = Development tools

# SCRIPTS

## UI
- [UI_health_arpg_status_bars.py](scripts/UI_health_arpg_status_bars.py) – large color coded horizontal bars for health, mana , and bandage timer
- <img src="https://raw.githubusercontent.com/CorvaeOboro/ultima_online_razor_enhanced_python_scripts/refs/heads/main/docs/ultima_ui_health_bar_long.jpg?raw=true"/>
- [UI_summon_health_monitor.py](scripts/UI_summon_health_monitor.py) – display the health of summoned creatures
- <img src="https://raw.githubusercontent.com/CorvaeOboro/ultima_online_razor_enhanced_python_scripts/refs/heads/main/docs/ultima_ui_summons_health.jpg?raw=true"/>
- [UI_spell_hotbar_hotkeys.py](scripts/UI_spell_hotbar_hotkeys.py) – Spell hotbar , added hotkey display

## RITUAL
ritual magic 
| <a href="https://raw.githubusercontent.com/CorvaeOboro/ultima_online_razor_enhanced_python_scripts/refs/heads/main/docs/ultima_ritual_of_rejuvenation_01.jpg?raw=true"> <img src="https://raw.githubusercontent.com/CorvaeOboro/ultima_online_razor_enhanced_python_scripts/refs/heads/main/docs/ultima_ritual_of_rejuvenation_01.jpg?raw=true" width="160" height="160" /> </a>| <a href="https://raw.githubusercontent.com/CorvaeOboro/ultima_online_razor_enhanced_python_scripts/refs/heads/main/docs/ultima_ritual_of_andaria_gate_01.jpg?raw=true"> <img src="https://raw.githubusercontent.com/CorvaeOboro/ultima_online_razor_enhanced_python_scripts/refs/heads/main/docs/ultima_ritual_of_andaria_gate_01.jpg?raw=true" width="160" height="160" /> </a> | <a href="https://raw.githubusercontent.com/CorvaeOboro/ultima_online_razor_enhanced_python_scripts/refs/heads/main/docs/ultima_ritual_of_compassion_01.jpg?raw=true"> <img src="https://raw.githubusercontent.com/CorvaeOboro/ultima_online_razor_enhanced_python_scripts/refs/heads/main/docs/ultima_ritual_of_compassion_01.jpg?raw=true" width="160" height="160" /> </a>  | <a href="https://raw.githubusercontent.com/CorvaeOboro/ultima_online_razor_enhanced_python_scripts/refs/heads/main/docs/ultima_ritual_of_luna_01.jpg?raw=true"> <img src="https://raw.githubusercontent.com/CorvaeOboro/ultima_online_razor_enhanced_python_scripts/refs/heads/main/docs/ultima_ritual_of_luna_01.jpg?raw=true" width="160" height="160" /> </a>  |
| :---: | :---: | :---: | :---: |

- [RITUAL_circles_expanded_uor_brit.py](scripts/RITUAL_circles_expanded_uor_brit.py) – Places a mandala  with multiple circles, gems, lanterns
- [RITUAL_feast.py](scripts/RITUAL_feast.py) – Places a feast with radial food items
- [RITUAL_pentagram_expanded.py](scripts/RITUAL_pentagram_expanded.py) – Places a pentagram ritual with star, circles, and candle 
- [RITUAL_spiral_round.py](scripts/RITUAL_spiral_round.py) – Places a rotated spiral with smooth corners using black pearls

## ITEM
- [ITEM_organize_backpack.py](scripts/ITEM_organize_backpack.py) – Organizes backpack items by type into  position
- [ITEM_organize_junk_salvager.py](scripts/ITEM_organize_junk_salvager.py) – Moves low-tier items to a junk backpack and salvages 
- [ITEM_transfer_container_to_backpack.py](scripts/ITEM_transfer_container_to_backpack.py) – Moves all items from target container to player
- [ITEM_weight_manager.py](scripts/ITEM_weight_manager.py) – Drops unfavored items and over maximum reagents
- [ITEM_drop_gold.py](scripts/ITEM_drop_gold.py) – Drops all gold 
- [ITEM_food_eater.py](scripts/ITEM_food_eater.py) – Eat food until full
- [ITEM_mount_toggle.py](scripts/ITEM_mount_toggle.py) – Toggles mounting of ethereal horse

## MISC
- [LOOT_treasure.py](scripts/LOOT_treasure.py) – Unlocks, opens, and loot nearby treasure chests
- [QUEST_turn_in_items.py](scripts/QUEST_turn_in_items.py) – Automate Quest turn-ins 
- [RECALL_bank.py](scripts/RECALL_bank.py) – Recall bank or home
- [COMBAT_pouch.py](scripts/COMBAT_pouch.py) – stun break using trapped pouch
- [PICKUP_gold_and_meditate.py](scripts/PICKUP_gold_and_meditate.py) – meditate

## SPELL
- [SPELL_attack_nearest.py](scripts/SPELL_attack_nearest.py) – Attack spells at nearest enemy, prioritizing Energy Bolt.
- [SPELL_bless_other.py](scripts/SPELL_bless_other.py) –  Bless the nearest friendly player 
- [SPELL_create_food.py](scripts/SPELL_create_food.py) – Create Food until out of mana

## TRAIN
- [TRAIN_alchemy.py](scripts/TRAIN_alchemy.py) – Trains Alchemy skill , optional poison-only mode
- [TRAIN_lockpicking.py](scripts/TRAIN_lockpicking.py) – Trains Lockpicking skill 
- [TRAIN_magery_spiritspeak.py](scripts/TRAIN_magery_spiritspeak.py) – Trains Magery and Spiritspeak 

## GATHER
- [GATHER_fishing_directional_loop.py](scripts/GATHER_fishing_directional_loop.py) – Fishes in facing direction, chops fish, drops unwanted items
- [GATHER_lumberjack_loop.py](scripts/GATHER_lumberjack_loop.py) – Continuously chops trees for rare resources , drops logs
- [GATHER_mining_loop.py](scripts/GATHER_mining_loop.py) – Continuously mines for rare resources , drops ore

## DEV
- [DEV_gump_debugger.py](scripts/DEV_gump_debugger.py) – Analyze ingame gumps outputs JSON 
- [DEV_item_inspector.py](scripts/DEV_item_inspector.py) – Backpack items and equipment info to JSON
- [DEV_item_to_list.py](scripts/DEV_item_to_list.py) –  Inspected item exported to categorized JSON 


# THANKS
- many thanks to the ultima online custom shard community , 
- many thanks to the creators of razor, razor enhanced and the wiki
- https://github.com/razorenhanced/razorenhanced

# LICENSE
free to all , [creative commons zero CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/)  , free to redistribute , attribution not required