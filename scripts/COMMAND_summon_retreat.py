"""
COMMAND Summon Retreat - a Razor Enhanced Python Script for Ultima Online

retreat damaged summons to swap aggro , 
uses the contetext menu on pet to follow you , then renguage with guard later

# Overview
# - Uses Player.Pets API to get list of pet/summon Mobile objects
# - Player.Pets returns Mobile objects directly (not serials)
# - Determines lowest-health summon (percent HP)
# - Uses context menu on that pet's serial to issue "Follow Me" so it retreats
# - Finds the nearest hostile using Mobiles.Filter
# - Orders one of the other summons (preferably the healthiest) to "Command Kill" and targets that hostile

STATUS:: working , some issues not finding pets sometimes range issue?
HOTKEY:: 6 ( 3-5 is other pet commands )
VERSION::20251017
"""

DEBUG_ON = False

ONLY_GREATER_SUMMONS = True # When True: ignores lesser summons like blade spirits
INCLUDE_LESSER_SUMMONS = False  # When False: ignores blade spirits
FOLLOW_LABELS = ["Command: Follow"] # Context menu label variants to try 
COMMAND_KILL_LABELS = ["Command: Kill"]

# Timing
CONTEXT_TIMEOUT_MS = 1000
PAUSE_AFTER_FOLLOW_MS = 1200
PAUSE_AFTER_COMMAND_KILL_MS = 300
TARGET_WAIT_MS = 4000

# Ranges
SUMMON_SCAN_RANGE = 30
HOSTILE_SCAN_RANGE = 12

# Colors
MSG_DEBUG = 67
MSG_ERROR = 33
MSG_OK = 68

#=========================================================

def debug(msg, color=MSG_DEBUG):
    if DEBUG_ON:
        try:
            Misc.SendMessage(f"[SummonRetreat] {msg}", color)
        except Exception:
            pass

def clean_name(name):
    try:
        s = (name or "").lower().strip()
        if s.startswith("a "):
            s = s[2:]
        return s
    except Exception:
        return str(name or "")

def is_blade_spirit_name(name):
    try:
        s = str(name or "").lower().strip()
        s = s.replace("(summoned)", "").strip()
        cname = clean_name(s)
        return cname in ("blade spirit", "blade spirits")
    except Exception:
        return False

def is_summon(mobile):
    """Detect summoned creatures ."""
    try:
        if mobile is None:
            return False
        name = str(getattr(mobile, 'Name', '') or '').lower()
        if "(summoned)" in name:
            return True
        # Check properties if available
        if getattr(mobile, 'PropsUpdated', False):
            for prop in getattr(mobile, 'Properties', []) or []:
                p = str(prop).lower()
                if "(summoned)" in p or "summoned creature" in p:
                    return True
        # Fallback: match base summon archetypes from monitor
        # Greater summons: elementals, daemons, pixies
        greater_summons = [
            "blood elemental",
            "greater air elemental",
            "greater earth elemental",
            "greater fire elemental",
            "greater water elemental",
            "daemon",
            "earth elemental",
            "fire elemental",
            "water elemental",
            "air elemental",
            "pixie",
        ]
        # Lesser summons: blade spirits, energy vortex, etc.
        lesser_summons = [
            "blade spirits",
            "energy vortex",
        ]
        
        cname = clean_name(name)
        
        # If ONLY_GREATER_SUMMONS is enabled, only match greater summons
        if ONLY_GREATER_SUMMONS:
            return any(b in cname for b in greater_summons)
        else:
            # Match both greater and lesser summons
            return any(b in cname for b in greater_summons + lesser_summons)
    except Exception:
        return False

def distance_chebyshev(a_pos, b_pos):
    try:
        return max(abs(int(a_pos.X) - int(b_pos.X)), abs(int(a_pos.Y) - int(b_pos.Y)))
    except Exception:
        return 9999

def get_player_pos():
    try:
        return Player.Position
    except Exception:
        return None

def get_summons_from_player_pets():
    """Return list of summoned pets using Player.Pets API with HP info."""
    try:
        # Use Player.Pets to get list of pet Mobile objects (not serials!)
        pets = Player.Pets
        if not pets or len(pets) == 0:
            debug("No pets found via Player.Pets", MSG_DEBUG)
            return []
        
        debug(f"Found {len(pets)} pets via Player.Pets API", MSG_DEBUG)
        result = []
        
        for mobile in pets:
            try:
                if not mobile:
                    debug(f"Null mobile in pets list", MSG_DEBUG)
                    continue
                
                # Check if it's in range
                distance = Player.DistanceTo(mobile)
                if distance > SUMMON_SCAN_RANGE:
                    debug(f"Pet {mobile.Name} too far away ({distance} tiles)", MSG_DEBUG)
                    continue
                
                # Get HP info
                cur = int(getattr(mobile, 'Hits', 0))
                mx = int(getattr(mobile, 'HitsMax', 0))
                hp_pct = (float(cur) / float(mx)) if mx > 0 else 0.0
                
                # Get actual name from property[0] instead of mobile.Name (which shows buff messages)
                actual_name = mobile.Name
                try:
                    props = Mobiles.GetPropStringList(mobile.Serial)
                    if props and len(props) > 0:
                        actual_name = str(props[0]).strip()
                except Exception:
                    pass

                if not INCLUDE_LESSER_SUMMONS and is_blade_spirit_name(actual_name):
                    debug(f"Skipping lesser summon: {actual_name}", MSG_DEBUG)
                    continue
                
                result.append({
                    'mobile': mobile,
                    'serial': mobile.Serial,
                    'name': actual_name,
                    'mobile_name_property': mobile.Name,
                    'hits': cur,
                    'hitsmax': mx,
                    'hp_pct': hp_pct,
                    'distance': distance,
                })
                debug(f"Added pet: {actual_name} ({hp_pct*100:.0f}% HP, {distance} tiles)", MSG_DEBUG)
                
            except Exception as e:
                debug(f"Error processing pet {mobile}: {e}", MSG_ERROR)
                continue
        
        return result
    except Exception as e:
        debug(f"Error in get_summons_from_player_pets: {e}", MSG_ERROR)
        return []

def pick_weakest(summons):
    if not summons:
        return None
    return sorted(summons, key=lambda s: (s['hp_pct'], s['hits'], s['hitsmax']))[0]

def pick_strongest(summons, exclude_serial=None):
    cands = [s for s in summons if s['serial'] != exclude_serial]
    if not cands:
        return None
    return sorted(cands, key=lambda s: (-s['hp_pct'], -s['hitsmax'], -s['hits']))[0]

def use_context_menu_variants(target_serial, labels, timeout_ms=CONTEXT_TIMEOUT_MS):
    for label in labels:
        try:
            debug(f"Trying context menu label: '{label}'", MSG_DEBUG)
            Misc.UseContextMenu(int(target_serial), str(label), int(timeout_ms))
            debug(f"Context menu '{label}' succeeded", MSG_OK)
            return True
        except Exception as e:
            debug(f"Context menu '{label}' failed: {e}", MSG_DEBUG)
            continue
    debug(f"All context menu labels failed for serial 0x{target_serial:08X}", MSG_ERROR)
    return False

def find_nearest_hostile(max_range=HOSTILE_SCAN_RANGE):
    """Return nearest hostile (grey/orange/red) within range, else None."""
    try:
        f = Mobiles.Filter()
        f.Enabled = True
        f.RangeMax = int(max_range)
        f.CheckLineOfSight = False
        # 3=Grey, 4=Orange, 5=Red
        f.Notorieties.Add(3)
        f.Notorieties.Add(4)
        f.Notorieties.Add(5)
        enemies = Mobiles.ApplyFilter(f)
        if not enemies:
            return None
        ppos = get_player_pos()
        if not ppos:
            return None
        # pick by nearest 
        enemies_sorted = sorted(enemies, key=lambda e: distance_chebyshev(ppos, getattr(e, 'Position', ppos)))
        return enemies_sorted[0] if enemies_sorted else None
    except Exception as e:
        debug(f"Error in find_nearest_hostile: {e}", MSG_ERROR)
        return None

def get_mobile_full_info(mobile):
    """Get full mobile info including all properties"""
    try:
        info_lines = []
        info_lines.append(f"Serial: 0x{mobile.Serial:08X}")
        info_lines.append(f"mobile.Name property: {mobile.Name}")
        
        # Get all properties using Mobiles.GetPropStringList
        props = Mobiles.GetPropStringList(mobile.Serial)
        if props and len(props) > 0:
            actual_name = str(props[0]).strip()
            info_lines.append(f"Actual Name (prop[0]): {actual_name}")
            info_lines.append(f"Properties ({len(props)} total):")
            for i, prop in enumerate(props[:10]):  # Show first 10
                info_lines.append(f"  [{i}] {prop}")
            if len(props) > 10:
                info_lines.append(f"  ... and {len(props) - 10} more")
        
        return "\n".join(info_lines)
    except Exception as e:
        return f"Error getting mobile info: {e}"

def order_follow_me(summon_info):
    if not summon_info:
        return False
    serial = summon_info['serial']
    name = summon_info.get('name', 'summon')
    hp_pct = summon_info.get('hp_pct', 0) * 100
    hits = summon_info.get('hits', 0)
    hitsmax = summon_info.get('hitsmax', 0)
    mobile = summon_info.get('mobile')
    
    # Show detailed info about why we're retreating this pet
    debug("=" * 60, MSG_DEBUG)
    debug(f"RETREATING WEAKEST PET: {name}", MSG_OK)
    debug(f"HP: {hits}/{hitsmax} ({hp_pct:.1f}%)", MSG_OK)
    debug("Full Mobile Info:", MSG_DEBUG)
    if mobile:
        full_info = get_mobile_full_info(mobile)
        for line in full_info.split('\n'):
            debug(f"  {line}", MSG_DEBUG)
    debug("=" * 60, MSG_DEBUG)
    
    ok = use_context_menu_variants(serial, FOLLOW_LABELS)
    if ok:
        # "Command: Follow" brings up a target cursor - target the player
        debug(f"Waiting for target cursor...", MSG_DEBUG)
        Target.WaitForTarget(int(TARGET_WAIT_MS), False)
        if Target.HasTarget():
            try:
                debug(f"Targeting player for follow command", MSG_DEBUG)
                Target.TargetExecute(Player.Serial)
                debug(f"Issued 'Follow Me' to {name}", MSG_OK)
                Misc.Pause(PAUSE_AFTER_FOLLOW_MS)
                return True
            except Exception as e:
                debug(f"Error targeting player: {e}", MSG_ERROR)
                try:
                    if Target.HasTarget():
                        Target.Cancel()
                except Exception:
                    pass
                return False
        else:
            debug(f"No target cursor appeared after context menu", MSG_ERROR)
            return False
    else:
        debug(f"Failed to issue 'Follow Me' to {name}", MSG_ERROR)
        return False

def order_command_kill(summon_info, enemy):
    if not summon_info or not enemy:
        return False
    serial = summon_info['serial']
    name = summon_info.get('name', 'summon')

    ok = use_context_menu_variants(serial, COMMAND_KILL_LABELS)
    if not ok:
        debug(f"Failed to open 'Command Kill' on {name}", MSG_ERROR)
        return False

    # Wait for target cursor and target the enemy
    Target.WaitForTarget(int(TARGET_WAIT_MS), False)
    if Target.HasTarget():
        try:
            Target.TargetExecute(enemy)
            debug(f"Targeted enemy with 'Command Kill' using {name}", MSG_OK)
            Misc.Pause(PAUSE_AFTER_COMMAND_KILL_MS)
            return True
        except Exception as e:
            debug(f"Error targeting enemy: {e}", MSG_ERROR)
            try:
                if Target.HasTarget():
                    Target.Cancel()
            except Exception:
                pass
            return False
    else:
        debug("No target cursor after 'Command Kill'", MSG_ERROR)
        return False

#=========================================================
def main():
    try:
        # Clear any leftover target first
        if Target.HasTarget():
            Target.Cancel()
            Misc.Pause(100)

        summons = get_summons_from_player_pets()
        if not summons:
            debug("No summons found in range.", MSG_ERROR)
            return

        weakest = pick_weakest(summons)
        if not weakest:
            debug("Could not determine weakest summon.", MSG_ERROR)
            return

        # Retreat the weakest first
        order_follow_me(weakest)

        # If only one summon, we are done
        if len(summons) < 2:
            debug("Only one summon present; retreat issued only.", MSG_DEBUG)
            return

        # Find a hostile to attack
        enemy = find_nearest_hostile(HOSTILE_SCAN_RANGE)
        if not enemy:
            debug("No hostile found; skipping Command Kill.", MSG_DEBUG)
            return

        # Prefer the strongest remaining summon to attack
        attacker = pick_strongest(summons, exclude_serial=weakest['serial'])
        if not attacker:
            debug("No attacker summon available after excluding weakest.", MSG_ERROR)
            return

        # Also tell the player to attack to set aggression (optional)
        try:
            Player.Attack(enemy)
        except Exception:
            pass

        # Issue Command Kill and target the enemy
        order_command_kill(attacker, enemy)

    except Exception as e:
        debug(f"Unhandled error: {e}", MSG_ERROR)

if __name__ == "__main__":
    main()