# Ultima Online Classic Razor Enhanced Python Scripts 
[ultima online classic](https://github.com/ClassicUO/ClassicUO) [razor enhanced](https://github.com/razorenhanced/razorenhanced) python scripts focused on UI customization and ritual magic

<center>

| [DOWNLOAD](https://github.com/CorvaeOboro/ultima_online_razor_enhanced_python_scripts/archive/refs/heads/main.zip) | [INSTALL](#INSTALL) | 
|:---:|:---:|

</center>

- each script is self-contained and can be run independently 
- many of the scripts are work in progress

<center>

| [UI](#UI) | [RITUAL](#RITUAL) | [ITEM](#ITEM) | [VFX](#VFX) | [MISC](#MISC) | [SPELL](#SPELL) | [TRAIN](#TRAIN) | [GATHER](#GATHER) | [DEV](#DEV) |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|

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
- [UI_action_buttons.py](scripts/UI_action_buttons.py) – button layout for emotes , say , and scripts
- <img src="https://raw.githubusercontent.com/CorvaeOboro/ultima_online_razor_enhanced_python_scripts/refs/heads/main/docs/ultima_UI_action_buttons.png?raw=true"/>
- [UI_item_drop.py](scripts/UI_item_drop.py) – select and place items on the ground , creating a trail , or in circles
- <img src="https://github.com/CorvaeOboro/ultima_online_razor_enhanced_python_scripts/blob/main/docs/ultima_ui_item_drop.png?raw=true"/>
- [UI_gump_layout_preset.py](scripts/UI_gump_layout_preset.py) – move gumps to specified positions
- [UI_ascii_display.py](scripts/UI_ascii_display.py) – ASCII art display system
- [UI_commands_gump.py](scripts/UI_commands_gump.py) – Command shortcuts gump
- [UI_durability.py](scripts/UI_durability.py) – Equipment durability monitor
- [UI_spell_hotbar_hotkeys.py](scripts/UI_spell_hotbar_hotkeys.py) – Spell hotbar with hotkeys

## RITUAL
ritual magic 
| <a href="https://raw.githubusercontent.com/CorvaeOboro/ultima_online_razor_enhanced_python_scripts/refs/heads/main/docs/ultima_ritual_of_rejuvenation_01.jpg?raw=true"> <img src="https://raw.githubusercontent.com/CorvaeOboro/ultima_online_razor_enhanced_python_scripts/refs/heads/main/docs/ultima_ritual_of_rejuvenation_01.jpg?raw=true" width="170" height="170" /> </a>| <a href="https://raw.githubusercontent.com/CorvaeOboro/ultima_online_razor_enhanced_python_scripts/refs/heads/main/docs/ultima_ritual_of_andaria_gate_01.jpg?raw=true"> <img src="https://raw.githubusercontent.com/CorvaeOboro/ultima_online_razor_enhanced_python_scripts/refs/heads/main/docs/ultima_ritual_of_andaria_gate_01.jpg?raw=true" width="170" height="170" /> </a> | <a href="https://raw.githubusercontent.com/CorvaeOboro/ultima_online_razor_enhanced_python_scripts/refs/heads/main/docs/ultima_ritual_of_compassion_01.jpg?raw=true"> <img src="https://raw.githubusercontent.com/CorvaeOboro/ultima_online_razor_enhanced_python_scripts/refs/heads/main/docs/ultima_ritual_of_compassion_01.jpg?raw=true" width="170" height="170" /> </a>  | <a href="https://raw.githubusercontent.com/CorvaeOboro/ultima_online_razor_enhanced_python_scripts/refs/heads/main/docs/ultima_ritual_of_luna_01.jpg?raw=true"> <img src="https://raw.githubusercontent.com/CorvaeOboro/ultima_online_razor_enhanced_python_scripts/refs/heads/main/docs/ultima_ritual_of_luna_01.jpg?raw=true" width="170" height="170" /> </a>  |
| :---: | :---: | :---: | :---: |

- [RITUAL_circles_expanded_uor_brit.py](scripts/RITUAL_circles_expanded_uor_brit.py) – Places a mandala  with multiple circles, gems, lanterns
- [RITUAL_feast.py](scripts/RITUAL_feast.py) – Places a feast with radial food items
- [RITUAL_pentagram_expanded.py](scripts/RITUAL_pentagram_expanded.py) – Places a pentagram ritual with star, circles, and candle 
- [RITUAL_spiral_round.py](scripts/RITUAL_spiral_round.py) – Places a rotated spiral with smooth corners using black pearls , options for antispiral 
- <img src="https://raw.githubusercontent.com/CorvaeOboro/ultima_online_razor_enhanced_python_scripts/refs/heads/main/docs/ultima_ritual_of_the_spiral.png?raw=true"/>
- [RITUAL_maze.py](scripts/RITUAL_maze.py) – Places a maze of hay , preview random seeds , then chose and place with packhorse help 
- <img src="https://raw.githubusercontent.com/CorvaeOboro/ultima_online_razor_enhanced_python_scripts/refs/heads/main/docs/ultima_ritual_of_the_maze.png?raw=true"/>
- [RITUAL_death.py](scripts/RITUAL_death.py) – Death ritual with skulls and bones
- [RITUAL_gems.py](scripts/RITUAL_gems.py) – Gem circle ritual
- [RITUAL_orbs.py](scripts/RITUAL_orbs.py) – Orb ritual with elemental themes

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
- [ITEM_add_scrolls_to_spellbook.py](scripts/ITEM_add_scrolls_to_spellbook.py) – Add scrolls to spellbook
- [ITEM_transfer_hay_to_packhorse.py](scripts/ITEM_transfer_hay_to_packhorse.py) – Transfer hay to packhorse
- [ITEM_withdraw_hay_from_packhorse.py](scripts/ITEM_withdraw_hay_from_packhorse.py) – Withdraw hay from packhorse

## VFX
- [VFX_mastery_ascension_blood_orb_circle.py](scripts/VFX_mastery_ascension_blood_orb_circle.py) – Blood Mastery Ascension , a ritual of effects with client side items 
- <img src="https://github.com/CorvaeOboro/ultima_online_razor_enhanced_python_scripts/blob/main/docs/ultima_vfx_mastery_ascension_blood.webp?raw=true"/>
- [VFX_mastery_ascension_nature_orb_circle.py](scripts/VFX_mastery_ascension_nature_orb_circle.py) – Nature Mastery , a ritual of effects with client side items 
- <img src="https://github.com/CorvaeOboro/ultima_online_razor_enhanced_python_scripts/blob/main/docs/ultima_vfx_mastery_ascension_nature.webp?raw=true"/>
- [VFX_mastery_ascension_shadow_orb_circle.py](scripts/VFX_mastery_ascension_shadow_orb_circle.py) – Shadow Mastery , a ritual of effects with client side items 
- <img src="https://github.com/CorvaeOboro/ultima_online_razor_enhanced_python_scripts/blob/main/docs/ultima_vfx_mastery_ascension_shadow.webp?raw=true"/>
- [VFX_mastery_ascension_fortune_orb_circle.py](scripts/VFX_mastery_ascension_fortune_orb_circle.py) – Fortune Mastery , a ritual of effects with client side items 
- <img src="https://github.com/CorvaeOboro/ultima_online_razor_enhanced_python_scripts/blob/main/docs/ultima_vfx_mastery_ascension_fortune.webp?raw=true"/>

## COMBAT
- [COMBAT_cancel_casting.py](scripts/COMBAT_cancel_casting.py) – Cancel spell casting
- [COMBAT_pouch_stunbreak.py](scripts/COMBAT_pouch_stunbreak.py) – Stun break using trapped pouch

## COMMAND
- [COMMAND_summon_pets.py](scripts/COMMAND_summon_pets.py) – Summon pets to your location via context menu 
- [COMMAND_summon_retreat.py](scripts/COMMAND_summon_retreat.py) – Retreat weakest pet via context menu

## CRAFT
- [CRAFT_arrows.py](scripts/CRAFT_arrows.py) – Arrow and bolt crafting

## HOME
- [HOME_deposit_enhancement_scrolls.py](scripts/HOME_deposit_enhancement_scrolls.py) – Deposit enhancement scrolls
- [HOME_deposit_equipment.py](scripts/HOME_deposit_equipment.py) – Deposit equipment
- [HOME_deposit_food.py](scripts/HOME_deposit_food.py) – Deposit food items
- [HOME_deposit_resource.py](scripts/HOME_deposit_resource.py) – Deposit resources
- [HOME_deposit_runic.py](scripts/HOME_deposit_runic.py) – Deposit runic items
- [HOME_deposit_scrolls.py](scripts/HOME_deposit_scrolls.py) – Deposit spell scrolls
- [HOME_deposit_treasure.py](scripts/HOME_deposit_treasure.py) – Deposit treasure items

## BANK
- [BANK_deposit_restock_unchained.py](scripts/BANK_deposit_restock_unchained.py) – Bank deposit and restock system

## QUEST
- [QUEST_accept_all_daily.py](scripts/QUEST_accept_all_daily.py) – Accepts all daily quests with specific rewards
- [QUEST_daily_progress.py](scripts/QUEST_daily_progress.py) – Daily quest progress display
- [QUEST_global_events.py](scripts/QUEST_global_events.py) – Global event quests combined display
- [QUEST_turn_in_items.py](scripts/QUEST_turn_in_items.py) – Quest turn-in items
- [QUEST_turn_in_orbs.py](scripts/QUEST_turn_in_orbs.py) – Quest turn-in orbs ( currently disabled NPC )

## MISC
- [LOOT_treasure.py](scripts/LOOT_treasure.py) – Unlocks, opens, and loot nearby treasure chests
- [PICKUP_gold_and_meditate.py](scripts/PICKUP_gold_and_meditate.py) – Pickup gold and meditate

## SPELL
- [SPELL_attack_nearest.py](scripts/SPELL_attack_nearest.py) – Cast attack spells at nearest enemy, prioritizing Energy Bolt, conditional based on available reagents and mana
- [SPELL_bless_other.py](scripts/SPELL_bless_other.py) – Bless nearby friendly player
- [SPELL_buff_self.py](scripts/SPELL_buff_self.py) – Cast Buffs on yourself Magic Reflect, ArchProtection, Bless
- [SPELL_create_food.py](scripts/SPELL_create_food.py) – Create Food until 20 mana restorative items
- [SPELL_invis_self.py](scripts/SPELL_invis_self.py) – Cast Invisibility on yourself
- [SPELL_cure_heal_self.py](scripts/SPELL_cure_heal_self.py) – ArchCure poison and heal self based on conditions
- [SPELL_death_self.py](scripts/SPELL_death_self.py) – Cast a sequence of harmful spells on self for ritual of death
- [SPELL_mage_pure_selection.py](scripts/SPELL_mage_pure_selection.py) – Pure mage spell selection using image id matching instead of journal text
- [SPELL_poison_field.py](scripts/SPELL_poison_field.py) – Cast poison field on nearest enemy
- [SPELL_recall_bank.py](scripts/SPELL_recall_bank.py) – Recall to bank then home if at bank

## TRAIN
- [TRAIN_alchemy.py](scripts/TRAIN_alchemy.py) – Trains Alchemy skill , optional poison-only mode
- [TRAIN_lockpicking.py](scripts/TRAIN_lockpicking.py) – Trains Lockpicking skill 
- [TRAIN_magery_spiritspeak.py](scripts/TRAIN_magery_spiritspeak.py) – Trains Magery and Spiritspeak
- [TRAIN_detect_hidden.py](scripts/TRAIN_detect_hidden.py) – Trains Detect Hidden skill
- [TRAIN_evaluate_Intelligence.py](scripts/TRAIN_evaluate_Intelligence.py) – Trains Evaluate Intelligence skill
- [TRAIN_taste_identification.py](scripts/TRAIN_taste_identification.py) – Trains Taste Identification skill

## GATHER
- [GATHER_fishing_directional_loop.py](scripts/GATHER_fishing_directional_loop.py) – Fishes in facing direction, chops fish, drops unwanted items
- [GATHER_lumberjack_loop.py](scripts/GATHER_lumberjack_loop.py) – Chop trees for rare resources , drops logs
- [GATHER_mining_loop.py](scripts/GATHER_mining_loop.py) – Mine for rare resources , drops ore

## DEV
- [DEV_gump_debugger.py](scripts/DEV_gump_debugger.py) – Analyze ingame gumps outputs JSON 
- [DEV_item_inspector.py](scripts/DEV_item_inspector.py) – Backpack items and equipment info to JSON
- [DEV_item_to_list.py](scripts/DEV_item_to_list.py) –  Inspected item exported to categorized JSON 
- [DEV_font_color_gump.py](scripts/DEV_font_color_gump.py) – UO font hue hex codes in a custom Gump
- [DEV_api_CUO.py](scripts/DEV_api_CUO.py) – ClassicUO API documentation
- [DEV_api_PacketLogger.py](scripts/DEV_api_PacketLogger.py) – Packet logger API
- [DEV_api_gumps.py](scripts/DEV_api_gumps.py) – Gumps API documentation
- [DEV_api_journal.py](scripts/DEV_api_journal.py) – Journal API documentation
- [DEV_api_misc.py](scripts/DEV_api_misc.py) – Misc API documentation
- [DEV_api_mobile.py](scripts/DEV_api_mobile.py) – Mobile API documentation
- [DEV_api_mobiles.py](scripts/DEV_api_mobiles.py) – Mobiles API documentation
- [DEV_api_player.py](scripts/DEV_api_player.py) – Player API documentation
- [DEV_api_statics.py](scripts/DEV_api_statics.py) – Statics API documentation
- [DEV_crafting_gump_crawler.py](scripts/DEV_crafting_gump_crawler.py) – Crafting gump crawler
- [DEV_crafting_tester.py](scripts/DEV_crafting_tester.py) – Crafting system tester
- [DEV_gump_quest_crawler.py](scripts/DEV_gump_quest_crawler.py) – Quest gump crawler
- [DEV_html_colors.py](scripts/DEV_html_colors.py) – HTML color reference
- [DEV_item_armor_data.py](scripts/DEV_item_armor_data.py) – Armor data extraction
- [DEV_items_search_world.py](scripts/DEV_items_search_world.py) – Search world for items
- [DEV_mobile_to_list.py](scripts/DEV_mobile_to_list.py) – Export mobile to list

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