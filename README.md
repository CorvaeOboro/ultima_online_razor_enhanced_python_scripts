# Ultima Online Classic Razor Enhanced Python Scripts 
[ultima online classic](https://github.com/ClassicUO/ClassicUO) [razor enhanced](https://github.com/razorenhanced/razorenhanced) python scripts focused on UI customization and ritual magic

<center>

| [DOWNLOAD](https://github.com/CorvaeOboro/ultima_online_razor_enhanced_python_scripts/archive/refs/heads/main.zip) | [INSTALL](#INSTALL) | 
|:---:|:---:|

</center>

- each script is self-contained and can be run independently 
- many of the scripts are work in progress

<center>

| [UI](#UI) | [RITUAL](#RITUAL) | [ITEM](#ITEM) | [MISC](#MISC) | [SPELL](#SPELL) | [TRAIN](#TRAIN) | [GATHER](#GATHER) | [DEV](#DEV) |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|

</center>

## UI
user interface custom gumps 
- [UI_health_arpg_status_bars.py](scripts/UI_health_arpg_status_bars.py) – large color coded horizontal bars for health, mana , and stamina
- <img src="https://raw.githubusercontent.com/CorvaeOboro/ultima_online_razor_enhanced_python_scripts/refs/heads/main/docs/ultima_ui_health_bar_long.gif?raw=true"/>
- [UI_summon_health_monitor.py](scripts/UI_summon_health_monitor.py) – display the health of summoned creatures at a consistent position
- <img src="https://raw.githubusercontent.com/CorvaeOboro/ultima_online_razor_enhanced_python_scripts/refs/heads/main/docs/ultima_ui_summons_health.png?raw=true"/>
- [UI_experience_progress_tracker.py](scripts/UI_experience_progress_tracker.py) – visualize progression system as progress bar , parsed from journal
- <img src="https://raw.githubusercontent.com/CorvaeOboro/ultima_online_razor_enhanced_python_scripts/refs/heads/main/docs/UI_experience_progress_tracker.png?raw=true"/>
- [UI_boss_healthbar.py](scripts/UI_boss_healthbar.py) – large boss health bar appears at top of screen when nearby known bosses
- <img src="https://raw.githubusercontent.com/CorvaeOboro/ultima_online_razor_enhanced_python_scripts/refs/heads/main/docs/ultima_ui_boss_health_bar.png?raw=true"/>
- [UI_walia_item_inspect.py](scripts/UI_walia_item_inspect.py) – WALIA (What Am I Looking At) in-game item inspection to display detailed properties, crafting info, and custom descriptions
- <img src="https://raw.githubusercontent.com/CorvaeOboro/ultima_online_razor_enhanced_python_scripts/refs/heads/main/docs/ultima_ui_walia_item_info.png?raw=true"/>
- <img src="https://raw.githubusercontent.com/CorvaeOboro/ultima_online_razor_enhanced_python_scripts/refs/heads/main/docs/ultima_ui_walia_item_info_20250903.png?raw=true"/>
- <img src="https://raw.githubusercontent.com/CorvaeOboro/ultima_online_razor_enhanced_python_scripts/refs/heads/main/docs/ultima_ui_walia_item_info_20250910.png?raw=true"/>
- [UI_journal_filtered.py](scripts/UI_journal_filtered.py) – minimal journal filtered and focused on local chat and events
- <img src="https://raw.githubusercontent.com/CorvaeOboro/ultima_online_razor_enhanced_python_scripts/refs/heads/main/docs/ultima_ui_journal_filtered.png?raw=true"/>
- [UI_layout_preset.py](scripts/UI_layout_preset.py) – move gumps to specified positions
- <img src="https://raw.githubusercontent.com/CorvaeOboro/ultima_online_razor_enhanced_python_scripts/refs/heads/main/docs/ultima_ui_layout_preset.gif?raw=true"/>
- [UI_action_buttons.py](scripts/UI_action_buttons.py) – button layout for emotes , say , and scripts
- <img src="https://raw.githubusercontent.com/CorvaeOboro/ultima_online_razor_enhanced_python_scripts/refs/heads/main/docs/ultima_ui_UI_action_buttons.png?raw=true"/>

## RITUAL
ritual magic 
| <a href="https://raw.githubusercontent.com/CorvaeOboro/ultima_online_razor_enhanced_python_scripts/refs/heads/main/docs/ultima_ritual_of_rejuvenation_01.jpg?raw=true"> <img src="https://raw.githubusercontent.com/CorvaeOboro/ultima_online_razor_enhanced_python_scripts/refs/heads/main/docs/ultima_ritual_of_rejuvenation_01.jpg?raw=true" width="170" height="170" /> </a>| <a href="https://raw.githubusercontent.com/CorvaeOboro/ultima_online_razor_enhanced_python_scripts/refs/heads/main/docs/ultima_ritual_of_andaria_gate_01.jpg?raw=true"> <img src="https://raw.githubusercontent.com/CorvaeOboro/ultima_online_razor_enhanced_python_scripts/refs/heads/main/docs/ultima_ritual_of_andaria_gate_01.jpg?raw=true" width="170" height="170" /> </a> | <a href="https://raw.githubusercontent.com/CorvaeOboro/ultima_online_razor_enhanced_python_scripts/refs/heads/main/docs/ultima_ritual_of_compassion_01.jpg?raw=true"> <img src="https://raw.githubusercontent.com/CorvaeOboro/ultima_online_razor_enhanced_python_scripts/refs/heads/main/docs/ultima_ritual_of_compassion_01.jpg?raw=true" width="170" height="170" /> </a>  | <a href="https://raw.githubusercontent.com/CorvaeOboro/ultima_online_razor_enhanced_python_scripts/refs/heads/main/docs/ultima_ritual_of_luna_01.jpg?raw=true"> <img src="https://raw.githubusercontent.com/CorvaeOboro/ultima_online_razor_enhanced_python_scripts/refs/heads/main/docs/ultima_ritual_of_luna_01.jpg?raw=true" width="170" height="170" /> </a>  |
| :---: | :---: | :---: | :---: |

- [RITUAL_circles_expanded_uor_brit.py](scripts/RITUAL_circles_expanded_uor_brit.py) – Places a mandala  with multiple circles, gems, lanterns
- [RITUAL_feast.py](scripts/RITUAL_feast.py) – Places a feast with radial food items
- [RITUAL_pentagram_expanded.py](scripts/RITUAL_pentagram_expanded.py) – Places a pentagram ritual with star, circles, and candle 
- [RITUAL_spiral_round.py](scripts/RITUAL_spiral_round.py) – Places a rotated spiral with smooth corners using black pearls

## ITEM
- [ITEM_organize_backpack.py](scripts/ITEM_organize_backpack.py) – Organizes backpack items by type into position
- <img src="https://raw.githubusercontent.com/CorvaeOboro/ultima_online_razor_enhanced_python_scripts/refs/heads/main/docs/ultima_ITEM_organize_backpack.webp?raw=true"/>
- [ITEM_organize_chest.py](scripts/ITEM_organize_chest.py) – Organizes targeted container by grouping similar items into bins with grid layout
- [ITEM_filter_junk_salvager.py](scripts/ITEM_filter_junk_salvager.py) – Moves low-tier items to a junk backpack and salvages , filter by type and affixes 
- [ITEM_weight_manager.py](scripts/ITEM_weight_manager.py) – Drops unfavored items and over maximum reagents
- [ITEM_transfer_container_to_backpack.py](scripts/ITEM_transfer_container_to_backpack.py) – Moves all items from target container to player
- [ITEM_mana_restorative.py](scripts/ITEM_mana_restorative.py) – Consumes mana restorative items based on missing mana 
- [ITEM_drop_gold.py](scripts/ITEM_drop_gold.py) – Drops all gold to ground
- [ITEM_food_eater.py](scripts/ITEM_food_eater.py) – Eat food until full
- [ITEM_mount_toggle.py](scripts/ITEM_mount_toggle.py) – Toggles mounting of ethereal horse
- [ITEM_use_kindling.py](scripts/ITEM_use_kindling.py) – Use kindling until campfire

## MISC
- [LOOT_treasure.py](scripts/LOOT_treasure.py) – Unlocks, opens, and loot nearby treasure chests
- [QUEST_turn_in_items.py](scripts/QUEST_turn_in_items.py) – Automate Quest turn-ins 
- [RECALL_bank.py](scripts/RECALL_bank.py) – Recall bank or home , specific rune # in runebook
- [COMBAT_pouch_stunbreak.py](scripts/COMBAT_pouch_stunbreak.py) – stun break using trapped pouch
- [PICKUP_gold_and_meditate.py](scripts/PICKUP_gold_and_meditate.py) – meditate

## SPELL
- [SPELL_attack_nearest.py](scripts/SPELL_attack_nearest.py) – Attack spells at nearest enemy, prioritizing Energy Bolt, conditional based on available reagents and mana
- [SPELL_bless_other.py](scripts/SPELL_bless_other.py) – Bless the nearest friendly player
- [SPELL_buff_self.py](scripts/SPELL_buff_self.py) – Buff yourself with Magic Reflect, ArchProtection, Bless
- [SPELL_create_food.py](scripts/SPELL_create_food.py) – Create Food until out of mana
- [SPELL_invis_self.py](scripts/SPELL_invis_self.py) – Cast Invisibility on yourself and re-cast as needed
- [SPELL_cure_heal_self.py](scripts/SPELL_cure_heal_self.py) – ArchCure poison and heal self based on conditional 

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
- [DEV_font_color_gump.py](scripts/DEV_font_color_gump.py) – UO font hue hex codes in a custom Gump

# INSTALL
- [download](https://github.com/CorvaeOboro/ultima_online_razor_enhanced_python_scripts/archive/refs/heads/main.zip) the python scripts and extract the zip into a location of your choice , it will include python .py files in a scripts folder .
- in game with [RazorEnhanced](https://github.com/razorenhanced/razorenhanced) click on the Scripting tab and ADD the .py files of the scripts you would like to use .
- once added the scripts will be listed in the Scripting tab , clicking on the script and set the settings like ( AutoStart on Login ) for UI scripts , and may set hotkeys for them in the Hotkeys tab under Scripts .

# TROUBLESHOOTING
- "import" errors = download [python](https://www.python.org/downloads/) and copy the Lib folder contents into Lib folder in RazorEnhanced

# THANKS
- many thanks to the ultima online custom shard community , 
- many thanks to the creators of razor, razor enhanced and the wiki
- https://github.com/razorenhanced/razorenhanced

# LICENSE
free to all , [creative commons zero CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/)  , free to redistribute , attribution not required