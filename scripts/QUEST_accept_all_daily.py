"""
QUEST accept all daily quests - a Razor Enhanced Python Script for Ultima Online

Accepts all available daily quests from Canute , select rewards are specified in dictionary QUEST_DATA

 STATUS:: working
 HOTKEY:: CTRL + Q
 VERSION::20250927
 """

DEBUG_MODE =  False
# when available this reward will always be selected , otherwise the preferred_reward in QUEST_DATA is used per quest
PREFERRED_REWARD_OVERRIDE = "Random Mastery Orb" 
# Possible rewards 
# 60 Arcane Dust # 75 Arcane Dust # 100 Arcane Dust
# 2,000 Gold # 2,500 Gold # 3,000 Gold # 3,500 Gold # 4,500 Gold # 5,000 Gold
# Runebook (Unblessed)
# Random Mastery Orb
# Random Rare Cloth # Random Bulk Resource # Random Runic Component # Magical Rose # Food Supply Crate
# Treasure Map # Page of Insight # Magical Pickaxe (double yield)
# Twin's Rage Axe # Hellclap War Hammer # Titan's Fall Axe # The Berserker's Maul

# daily quest reward selections
QUEST_DATA = {
    "Graveyard Cleanup": {
        "reward_index_map": {"75 Arcane Dust": 0, "2,500 Gold": 1, "Food Supply Crate": 2},
        "preferred_reward": "2,500 Gold",
    },
    "The Exiled Ones": {
        "reward_index_map": {"Food Supply Crate": 0, "2,000 Gold": 1, "50 Arcane Dust": 2},
        "preferred_reward": "2,000 Gold",
    },
    "City Cleanup": {
        "reward_index_map": {"Runebook (Unblessed)": 0, "1,500 Gold": 1, "100 Arcane Dust": 2},
        "preferred_reward": "Runebook (Unblessed)",
    },
    "Simply Gross": {
        "reward_index_map": {"Magical Rose": 0, "2,500 Gold": 1, "75 Arcane dust": 2},
        "preferred_reward": "2,500 Gold",
    },
    "Vermin to the North": {
        "reward_index_map": {"Random Mastery Orb": 0, "Food Supply Crate": 1, "3,500 Gold": 2},
        "preferred_reward": "Random Mastery Orb",
    },
    "The Ogre Threat": {
        "reward_index_map": {"Random Mastery Orb": 0, "3,500 Gold": 1, "Treasure Map": 2},
        "preferred_reward": "Random Mastery Orb",
    },
    "Ghost Hunt": {
        "reward_index_map": {"60 Arcane Dust": 0, "2,500 Gold": 1, "Treasure Map": 2},
        "preferred_reward": "2,500 Gold",
    },
    "Dragon's Essence": {
        "reward_index_map": {"Random Rare Cloth": 0, "Random Mastery Orb": 1, "Page of Insight": 2},
        "preferred_reward": "Random Mastery Orb",
    },
    "Viscosity": {
        "reward_index_map": {"Random Rare Cloth": 0, "Random Mastery Orb": 1, "4,500 Gold": 2},
        "preferred_reward": "Random Mastery Orb",
    },
    "Daemon's Remains": {
        "reward_index_map": {"Random Bulk Resource": 0, "3,000 Gold": 1, "Random Mastery Orb": 2},
        "preferred_reward": "Random Mastery Orb",
    },
    "Lack of Proof": {
        "reward_index_map": {"Random Rare Cloth": 0, "Random Mastery Orb": 1, "Magical Pickaxe (double yield)": 2},
        "preferred_reward": "Random Mastery Orb",
    },
    "Corrupted Blood": {
        "reward_index_map": {"Random Rare Cloth": 0, "Random Mastery Orb": 1, "4,500 Gold": 2},
        "preferred_reward": "Random Mastery Orb",
    },
    "Stolen Artifacts": {
        "reward_index_map": {"Random Bulk Resource": 0, "3,000 Gold": 1, "Random Mastery Orb": 2},
        "preferred_reward": "Random Mastery Orb",
    },
    "Land of the Dead": {
        "reward_index_map": {"100 Arcane Dust": 0, "Food Supply Crate": 1, "Treasure Map": 2},
        "preferred_reward": "100 Arcane Dust",
    },
    "Scary Affiliation": {
        "reward_index_map": {"Twin's Rage Axe": 0, "Random Bulk Resource": 1, "Random Runic Component": 2},
        "preferred_reward": "Random Bulk Resource",
    },
    "Petrified": {
        "reward_index_map": {"Random Runic Component": 0, "Random Bulk Resource": 1, "Magical Pickaxe (double yield)": 2},
        "preferred_reward": "Random Bulk Resource",
    },
    "Adamantium Hunt": {
        "reward_index_map": {"Random Runic Component": 0, "Random Bulk Resource": 1, "Magical Pickaxe (double yield)": 2},
        "preferred_reward": "Random Bulk Resource",
    },
    "Shoes of a Giant": {
        "reward_index_map": {"Random Runic Component": 0, "Titan's Fall Axe": 1, "Random Mastery Orb": 2},
        "preferred_reward": "Random Mastery Orb",
    },
    "Behorn the Infidels": {
        "reward_index_map": {"Random Runic Component": 0, "The Berserker's Maul": 1, "Random Mastery Orb": 2},
        "preferred_reward": "Random Mastery Orb",
    },
    "Sky is the Limit": {
        "reward_index_map": {"Random Runic Component": 0, "Treasure Map": 1, "Food Supply Crate": 2},
        "preferred_reward": "Random Runic Component",
    },
    "Desert Cleanup": {
        "reward_index_map": {"Random Mastery Orb": 0, "Magical Rose": 1, "Treasure Map": 2},
        "preferred_reward": "Random Mastery Orb",
    },
    "Frozen Cleansing": {
        "reward_index_map": {"Random Rare Cloth": 0, "Random Mastery Orb": 1, "Food Supply Crate": 2},
        "preferred_reward": "Random Mastery Orb",
    },
    "Lava Cleansing": {
        "reward_index_map": {"Hellclap War Hammer": 0, "Treasure Map": 1, "Food Supply Crate": 2},
        "preferred_reward": "Hellclap War Hammer",
    },
    "Contamination": {
        "reward_index_map": {"Random Rare Cloth": 0, "Random Mastery Orb": 1, "Magical Pickaxe (double yield)": 2},
        "preferred_reward": "Random Mastery Orb",
    },
    "All Aboard!": {
        "reward_index_map": {"Random Runic Component": 0, "Random Rare Cloth": 1, "3,500 Gold": 2},
        "preferred_reward": "3,500 Gold",
    },
    "Tailoring Hell": {
        "reward_index_map": {"Random Rare Cloth": 0, "Random Mastery Orb": 1, "5,000 Gold": 2},
        "preferred_reward": "Random Mastery Orb",
    },
    "Gigantic!": {
        "reward_index_map": {"Random Mastery Orb": 0, "Random Runic Component": 1, "Treasure Map": 2},
        "preferred_reward": "Random Mastery Orb",
    },
    "Evil Within": {
        "reward_index_map": {"Random Rare Cloth": 0, "Random Mastery Orb": 1, "5,000 Gold": 2},
        "preferred_reward": "Random Mastery Orb",
    },
    "Death Wings": {
        "reward_index_map": {"Random Runic Component": 0, "Treasure Map": 1, "Food Supply Crate": 2},
        "preferred_reward": "Random Runic Component",
    },
    "Ancient Sanctuary": {
        "reward_index_map": {"Random Rare Cloth": 0, "Random Mastery Orb": 1, "Treasure Map": 2},
        "preferred_reward": "Random Mastery Orb",
    },
}


QUEST_GIVER_SERIAL = 0x000000D4 # Quest giver NPC serial in Britain (daily quest giver "Canute")
DAILY_BASE_GUMP_ID = 0xDA2ACF13 # Base daily quest gump id (Available/Active/Completed)
REWARD_GUMP_ID = 0xEB54B301 # Reward selection gump id (3-option reward list)

# Primary navigation buttons on the daily quests gump
BUTTON_PREV = 1
BUTTON_NEXT = 2
BUTTON_AVAILABLE = 10   # "Available Quests"
ACCEPT_FIRST_BUTTON = 100 # Item action buttons on the Available page , first quest 

# Timing
MAX_ACCEPTS = 35           # safety cap for how many quests to accept in one run
WAIT_GUMP_MS = 10000       # default wait for gump open
LOOP_PAUSE_MS = 120        # short loop pause

"""
 # EXAMPLE OF RECORDED ACTIONS , 
 # note that each quest gump button is not unique its based on the "available" so we read the description to map to reward selection
 Mobiles.UseMobile(0x000000D4) # canute in britain the dialy quest giver
 Gumps.WaitForGump(0xda2acf13, 10000) # daily quest gump waiting to load
 Gumps.SendAction(0xda2acf13, 100) # clicking the "Accept Quest" button of the FIRST quest ( dyanmic based on what has been accepted )
 Gumps.WaitForGump(0xeb54b301, 10000) # waiting for the quest reward selection gump to load
 Gumps.SendAdvancedAction(0xeb54b301, 1, [1], [], []) # selecting reward 1 , reward selection ( 0 , 1 , 2 )  
 Gumps.WaitForGump(0xda2acf13, 10000) # waiting for the daily quest gump to load
 Gumps.SendAction(0xda2acf13, 10) # back to "Available Quests" 
 """

# ===========================================

def debug_message(msg, hue=1153): 
    try:
        if DEBUG_MODE:
            Misc.SendMessage(str(msg), hue)
    except Exception:
        pass

def pause_ms(ms):
    # Simple pause without 
    try:
        Misc.Pause(int(ms))
    except Exception:
        pass

def wait_for_any_gump(timeout_ms=WAIT_GUMP_MS):
    # Poll for a gump up to timeout_ms, using LOOP_PAUSE_MS intervals
    try:
        loops = max(1, int(timeout_ms // LOOP_PAUSE_MS))
    except Exception:
        loops = 50
    for _ in range(loops):
        try:
            if Gumps.HasGump():
                gid = Gumps.CurrentGump()
                if gid:
                    return gid
        except Exception:
            pass
        pause_ms(LOOP_PAUSE_MS)
    return 0

def open_quest_gump():
    debug_message("Step 1: Open quest giver gump", 68)
    try:
        try:
            Gumps.ResetGump()
        except Exception:
            pass
        Misc.Pause(120)
        Mobiles.UseMobile(QUEST_GIVER_SERIAL)
        # Prefer hinted id, fall back to any gump
        try:
            if Gumps.WaitForGump(DAILY_BASE_GUMP_ID, WAIT_GUMP_MS):
                return DAILY_BASE_GUMP_ID
        except Exception:
            pass
        return wait_for_any_gump(WAIT_GUMP_MS)
    except Exception:
        return 0

def go_to_available_page(gid=0):
    if gid == 0:
        gid = open_quest_gump()
        if gid == 0:
            return 0
    debug_message("Step 2: Navigate to 'Available Quests'", 68)
    try:
        Gumps.SendAction(gid, BUTTON_AVAILABLE)
    except Exception:
        return gid
    Misc.Pause(300)
    try:
        new_gid = Gumps.CurrentGump()
        return new_gid or gid
    except Exception:
        return gid

def snap_text_lines():
    try:
        lines = Gumps.LastGumpGetLineList()
        return [str(t).strip() for t in (lines or [])]
    except Exception:
        return []

def extract_base_quests(lines):
    """Extract base quest rows from the Available page.
    Returns list of dicts with keys: name, region, type, difficulty, status, description
    """
    if not lines:
        return []
    L = [str(x).strip() for x in lines]
    header_keys = ["Quest Name", "Region", "Type", "Difficulty", "Status"]
    header_idx = -1
    for i in range(len(L) - len(header_keys) + 1):
        if all(L[i + k].lower() == header_keys[k].lower() for k in range(len(header_keys))):
            header_idx = i
            break
    if header_idx == -1:
        return []
    i = header_idx + len(header_keys)
    quests = []
    sentinel_terms = {"next page", "active quests", "completed quests"}

    while i < len(L):
        low = L[i].lower()
        if low in sentinel_terms:
            break
        if i + 4 >= len(L):
            break
        name = L[i].strip(); region = L[i+1].strip(); qtype = L[i+2].strip(); diff = L[i+3].strip(); status = L[i+4].strip()
        rec = {"name": name, "region": region, "type": qtype, "difficulty": diff, "status": status}
        i += 5
        if i < len(L) and L[i].lower().startswith("description:"):
            rec["description"] = L[i]
            i += 1
        if i < len(L) and L[i].lower() == "accept":
            i += 1
        quests.append(rec)
    return quests

def get_first_available_quest_name():
    """Read the current 'Available' page and return the first quest name, or None if not found."""
    lines = snap_text_lines()
    quests = extract_base_quests(lines)
    if quests:
        return quests[0].get("name")
    return None

def resolve_reward_choice_for_quest(quest_name):
    """Given a quest name, resolve the preferred reward label and its index for SendAdvancedAction.
    Returns tuple (reward_index:int, reward_label:str). If unknown, returns (1, "2,500 Gold") as a default.
    """
    try:
        data = QUEST_DATA.get(quest_name)
        if not data:
            # Fallback heuristic if quest not mapped
            return 1, "2,500 Gold"
        idx_map = data.get("reward_index_map", {})
        # 1) Global override: if present in this quest's options, use it
        try:
            override = PREFERRED_REWARD_OVERRIDE.strip() if PREFERRED_REWARD_OVERRIDE else None
        except Exception:
            override = None
        if override and override in idx_map:
            debug_message(f"Override reward selection to '{override}' for quest '{quest_name}'.", 90)
            return int(idx_map[override]), override
        # 2) Quest-specific preferred reward
        preferred = data.get("preferred_reward")
        if preferred in idx_map:
            return int(idx_map[preferred]), preferred
        # Fallback: choose the lowest index available
        if idx_map:
            k, v = sorted(idx_map.items(), key=lambda kv: kv[1])[0]
            return int(v), str(k)
    except Exception:
        pass
    return 1, "2,500 Gold"

def accept_first_quest_and_select_reward():
    """Perform the 5 clear steps for a single quest:
    1) Open giver gump (if needed)
    2) Navigate to Available page
    3) Read first quest name
    4) Accept first quest (button 100)
    5) On reward gump, select the correct reward index for that quest
    Returns True if a quest was accepted and a reward was attempted.
    """
    gid = go_to_available_page(0)
    if gid == 0:
        return False

    debug_message("Step 3: Read first quest name from list", 88)
    quest_name = get_first_available_quest_name()
    if not quest_name:
        debug_message("No quest detected in first slot on this page.", 33)
        return False

    reward_index, reward_label = resolve_reward_choice_for_quest(quest_name)
    debug_message(f"First quest: '{quest_name}' -> reward '{reward_label}' (index {reward_index})", 94)

    debug_message("Step 4: Accept first quest", 68)
    try:
        Gumps.SendAction(gid, ACCEPT_FIRST_BUTTON)
    except Exception:
        return False
    # Wait for reward gump 
    try:
        if not Gumps.WaitForGump(REWARD_GUMP_ID, WAIT_GUMP_MS):
            pass
    except Exception:
        pass
    reward_gid = 0
    try:
        reward_gid = Gumps.CurrentGump()
    except Exception:
        reward_gid = 0
    if reward_gid == 0:
        reward_gid = wait_for_any_gump(WAIT_GUMP_MS)
    if reward_gid == 0:
        debug_message("Reward gump did not appear.", 33)
        return False

    debug_message("Step 5: Choose reward for accepted quest", 68)
    try:
        # Use the same pattern as recorded: second arg often treated as page/context id (1), values array holds index
        Gumps.SendAdvancedAction(reward_gid, 1, [int(reward_index)], [], [])
        Misc.Pause(200)
    except Exception:
        debug_message("Failed to send reward selection action.", 33)
        return False

    # Return to Available page 
    try:
        if not Gumps.WaitForGump(DAILY_BASE_GUMP_ID, WAIT_GUMP_MS):
            pass
    except Exception:
        pass
    base_gid = 0
    try:
        base_gid = Gumps.CurrentGump()
    except Exception:
        base_gid = 0
    if base_gid:
        try:
            Gumps.SendAction(base_gid, BUTTON_AVAILABLE)
        except Exception:
            pass
        Misc.Pause(250)
    return True

def go_next_page():
    try:
        gid = Gumps.CurrentGump()
    except Exception:
        gid = 0
    if gid == 0:
        gid = go_to_available_page(0)
        if gid == 0:
            return 0
    try:
        Gumps.SendAction(gid, BUTTON_NEXT)
    except Exception:
        return gid
    Misc.Pause(300)
    try:
        return Gumps.CurrentGump() or gid
    except Exception:
        return gid

# ===== Main  =====

def run_accept_all_daily():
    """High-level, explicit step loop to accept multiple daily quests.
    - For each iteration, accept the FIRST quest on the current page after reading its name.
    - Select the preferred reward based on QUEST_DATA.
    """
    accepted = 0
    gid = go_to_available_page(0)
    if gid == 0:
        debug_message("Failed to open 'Available Quests' page.", 33)
        return
    while accepted < MAX_ACCEPTS:
        did_accept = accept_first_quest_and_select_reward()
        if not did_accept:
            gid = go_next_page()
            if gid == 0:
                break
            did_accept = accept_first_quest_and_select_reward()
            if not did_accept:
                break
        accepted += 1
        Misc.Pause(350)
    debug_message(f"Accepted {accepted} daily quests this run.", 63)

def main():
    run_accept_all_daily()

if __name__ == "__main__":
    main()