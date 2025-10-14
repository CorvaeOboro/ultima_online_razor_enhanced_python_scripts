"""
DEV API Player - a Razor Enhanced Python Script for Ultima Online

Comprehensive testing of Player API properties
Tests and displays information about all Player object properties

REFERENCE = https://razorenhanced.readthedocs.io/api/Player.html

=== PLAYER API OVERVIEW ===
The Player class provides access to all player character information including:
- Stats (STR, DEX, INT, HP, Mana, Stamina)
- Equipment and containers (Backpack, Bank, Mount, Quiver)
- Resistances and bonuses
- Position and movement
- Buffs and status effects
- Followers and pets

This script comprehensively tests ALL Player properties and generates:
1. Console output showing each property value or error
2. JSON report with test results and property values
3. Summary statistics of working vs failed properties

Player.AR Int32 Resistance to Phisical damage.
Player.Backpack Item Player backpack, as Item object.
Player.Bank Item Player bank chest, as Item object.
Player.Body Int32 Player Body or MobileID (see: Mobile.Body)
Player.Buffs List[String] List of Player active buffs:
Meditation Agility Animal Form Arcane Enpowerment Arcane Enpowerment (new) Arch Protection Armor Pierce Attunement Aura of Nausea Bleed Bless Block Bload Oath (caster) Bload Oath (curse) BloodWorm Anemia City Trade Deal Clumsy Confidence Corpse Skin Counter Attack Criminal Cunning Curse Curse Weapon Death Strike Defense Mastery Despair Despair (target) Disarm (new) Disguised Dismount Prevention Divine Fury Dragon Slasher Fear Enchant Enemy Of One Enemy Of One (new) Essence Of Wind Ethereal Voyage Evasion Evil Omen Faction Loss Fan Dancer Fan Fire Feeble Mind Feint Force Arrow Berserk Fly Gaze Despair Gift Of Life Gift Of Renewal Healing Heat Of Battle Hiding Hiryu Physical Malus Hit Dual Wield Hit Lower Attack Hit Lower Defense Honorable Execution Honored Horrific Beast Hawl Of Cacophony Immolating Weapon Incognito Inspire Invigorate Invisibility Lich Form Lighting Strike Magic Fish Magic Reflection Mana Phase Mass Curse Medusa Stone Mind Rot Momentum Strike Mortal Strike Night Sight NoRearm Orange Petals Pain Spike Paralyze Perfection Perseverance Poison Poison Resistance Polymorph Protection Psychic Attack Consecrate Weapon Rage Rage Focusing Rage Focusing (target) Reactive Armor Reaper Form Resilience Rose Of Trinsic Rotworm Blood Disease Rune Beetle Corruption Skill Use Delay Sleep Spell Focusing Spell Focusing (target) Spell Plague Splintering Effect Stone Form Strangle Strength Surge Swing Speed Talon Strike Vampiric Embrace Weaken Wraith Form
Player.ColdResistance Int32 Resistance to Cold damage.
Player.DamageChanceIncrease Int32 Get total Damage Chance Increase.
Player.DefenseChanceIncrease Int32 Get total Defense Chance Increase.
Player.Dex Int32 Stats value for Dexterity.
Player.DexterityIncrease Int32 Get total Dexterity Increase.
Player.Direction String Player current direction, as text.
Player.EnergyResistance Int32 Resistance to Energy damage.
Player.EnhancePotions Int32 Get total Enhance Potions.
Player.FasterCasting Int32 Get total Faster Casting.
Player.FasterCastRecovery Int32 Get total Faster Cast Recovery.
Player.Female Boolean Player is a female.
Player.FireResistance Int32 Resistance to Fire damage.
Player.Followers Int32 Player current amount of pet/followers.
Player.FollowersMax Int32 Player maximum amount of pet/followers.
Player.Gold Int32 Player total gold, in the backpack.
Player.HasSpecial Boolean Player have a special abilities active.
Player.HitPointsIncrease Int32 Get total Hit Points Increase.
Player.HitPointsRegeneration Int32 Get total Hit Points Regeneration.
Player.Hits Int32 Current hit points.
Player.HitsMax Int32 Maximum hit points.
Player.InParty Boolean Player is in praty.
Player.Int Int32 Stats value for Intelligence.
Player.IntelligenceIncrease Int32 Get total Intelligence Increase.
Player.IsGhost Boolean Player is a Ghost
Player.LowerManaCost Int32 Get total Lower Mana Cost.
Player.LowerReagentCost Int32 Get total Lower Reagent Cost.
Player.Luck Int32 Player total luck.
Player.Mana Int32 Current mana.
Player.ManaIncrease Int32 Get total Mana Increase.
Player.ManaMax Int32 Maximum mana.
Player.ManaRegeneration Int32 Get total Mana Regeneration.
Player.Map Int32 Player current map, or facet.
Player.MaximumHitPointsIncrease Int32 Get total Maximum Hit Points Increase.
Player.MaximumManaIncrease Int32 Get total Maximum Mana Increase.
Player.MaximumStaminaIncrease Int32 Get total Maximum Stamina Increase.
Player.MaxWeight Int32 Player maximum weight.
Player.MobileID Int32 Player MobileID or Body (see: Mobile.MobileID)
Player.Mount Item Player current Mount, as Item object.
NOTE: On some server the Serial return by this function doesn’t match the mount serial.
Player.Name String Player name.
Player.Notoriety Byte Player notoriety
1: blue, innocent 2: green, friend 3: gray, neutral 4: gray, criminal 5: orange, enemy 6: red, hostile 6: yellow, invulnerable
Player.Paralized Boolean Player is Paralized. True also while frozen because of casting of spells.
Player.Poisoned Boolean Player is Poisoned
Player.PoisonResistance Int32 Resistance to Poison damage.
Player.Position Point3D Current Player position as Point3D object.
Player.Quiver Item Player quiver, as Item object.
Player.ReflectPhysicalDamage Int32 Get total Reflect Physical Damage.
Player.Serial Int32 Player unique Serial.
Player.SpellDamageIncrease Int32 Get total Spell Damage Increase.
Player.Stam Int32 Current stamina.
Player.StaminaIncrease Int32 Get total Stamina Increase.
Player.StaminaRegeneration Int32 Get total Stamina Regeneration.
Player.StamMax Int32 Maximum stamina.
Player.StatCap Int32 Get the stats cap.
Player.StaticMount Int32 Retrieves serial of mount set in Filter/Mount GUI.
Player.Str Int32 Stats value for Strenght.
Player.StrengthIncrease Int32 Get total Strength Increase.
Player.SwingSpeedIncrease Int32 Get total Swing Speed Increase.
Player.Visible Boolean Player is visible, false if hidden.
Player.WarMode Boolean Player has war mode active.
Player.Weight Int32 Player current weight.
Player.YellowHits Boolean Player HP bar is not blue, but yellow.

VERSION::20251014
"""

# Non-destructive probe of Player.* properties listed above

import time
import os
import json


# GLOBAL SETTINGS
BASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
OUTPUT_FILE = os.path.join(BASE_PATH, "api_player_test_output.json")
RUN_USAGE_EXAMPLES = True
DEBUG_MODE = True

def out(msg, color=90):
    try:
        # Don't add prefix for empty messages (used for spacing)
        if msg:
            Misc.SendMessage(f"[PLAYER] {msg}", color)
        else:
            Misc.SendMessage("", color)
    except Exception:
        if msg:
            print(f"[PLAYER] {msg}")
        else:
            print("")


def _fmt_item(it):
    try:
        if not it:
            return "None"
        try:
            s = it.Serial
        except Exception:
            s = None
        cnt = None
        try:
            cont = it.Contains
            if cont is not None:
                cnt = len(list(cont))
        except Exception:
            cnt = None
        base = f"Item(serial={hex(int(s)) if s not in (None, '') else 'None'})"
        return base + (f", contains={cnt}" if cnt is not None else "")
    except Exception:
        return "<item>"


def _fmt_point3d(p):
    try:
        x = p.X if p is not None else None
        y = p.Y if p is not None else None
        z = p.Z if p is not None else None
        return f"Point3D(X={x}, Y={y}, Z={z})"
    except Exception:
        return str(p)


def test_property(name, getter_func, json_output, formatter=None):
    """
    Test a single Player property and record results
    
    Args:
        name: Property name
        getter_func: Function that returns the property value
        json_output: JSON output dictionary to update
        formatter: Optional function to format the value for display
    
    Returns:
        Tuple of (success, value, error_msg)
    """
    try:
        value = getter_func()
        
        # Format for display
        if formatter:
            display_value = formatter(value)
        else:
            display_value = str(value)
        
        out(f"{name}: {display_value}")
        
        # Store in JSON with proper type conversion
        if value is None:
            json_value = None
        elif isinstance(value, bool):
            json_value = bool(value)
        elif isinstance(value, (int, float)):
            json_value = int(value) if isinstance(value, int) else float(value)
        elif isinstance(value, str):
            json_value = str(value)
        elif isinstance(value, list):
            json_value = [str(item) for item in value]
        else:
            # For complex objects, store string representation
            json_value = str(value)
        
        json_output["properties"][name] = json_value
        json_output["test_report"][name] = {
            "works": True,
            "error": None,
            "has_value": value is not None
        }
        
        return True, value, None
        
    except Exception as e:
        error_msg = str(e)
        out(f"{name}: ERROR {error_msg}", 33)
        
        json_output["errors"].append({
            "property": name,
            "error": error_msg
        })
        json_output["test_report"][name] = {
            "works": False,
            "error": error_msg,
            "has_value": False
        }
        
        return False, None, error_msg


def main():
    # Initialize JSON output structure
    json_output = {
        "test_report": {},  # Summary of which properties work
        "test_timestamp": str(Misc.ScriptCurrent(False)),
        "properties": {},
        "errors": []
    }
    
    # Preliminary quick access check 
    try:
        serial = Player.Serial
        out(f"Player.Serial quick check: {serial}")
        json_output["quick_check"] = {"success": True, "serial": int(serial)}
    except Exception as e:
        out(f"Player.Serial quick check: ERROR {e}", 33)
        json_output["quick_check"] = {"success": False, "error": str(e)}

    # Brief wait for Player to initialize 
    start = time.time()
    while True:
        try:
            _ = Player.Serial
            if _:
                break
        except Exception:
            pass
        if time.time() - start > 5:
            break
        try:
            Misc.Pause(100)
        except Exception:
            time.sleep(0.1)

    out("=" * 60, 88)
    out("  PLAYER API COMPREHENSIVE TEST", 88)
    out("=" * 60, 88)
    out("")

    # SECTION: Item-like Properties
    out("=" * 60, 88)
    out("  ITEM-LIKE PROPERTIES", 88)
    out("=" * 60, 88)
    
    test_property("Backpack", lambda: Player.Backpack, json_output, _fmt_item)
    test_property("Bank", lambda: Player.Bank, json_output, _fmt_item)
    test_property("Mount", lambda: Player.Mount, json_output, _fmt_item)
    test_property("Quiver", lambda: Player.Quiver, json_output, _fmt_item)
    out("")

    # SECTION: Basic Identifiers and Flags
    out("=" * 60, 88)
    out("  BASIC IDENTIFIERS AND FLAGS", 88)
    out("=" * 60, 88)
    
    test_property("Serial", lambda: Player.Serial, json_output)
    test_property("Name", lambda: Player.Name, json_output)
    test_property("Body", lambda: Player.Body, json_output)
    test_property("MobileID", lambda: Player.MobileID, json_output)
    test_property("StaticMount", lambda: Player.StaticMount, json_output)
    test_property("Female", lambda: Player.Female, json_output)
    test_property("IsGhost", lambda: Player.IsGhost, json_output)
    test_property("Visible", lambda: Player.Visible, json_output)
    test_property("WarMode", lambda: Player.WarMode, json_output)
    test_property("InParty", lambda: Player.InParty, json_output)
    test_property("Notoriety", lambda: Player.Notoriety, json_output)
    test_property("Map", lambda: Player.Map, json_output)
    out("")

    # SECTION: Stats and Caps
    out("=" * 60, 88)
    out("  STATS AND CAPS", 88)
    out("=" * 60, 88)
    
    test_property("Str", lambda: Player.Str, json_output)
    test_property("Dex", lambda: Player.Dex, json_output)
    test_property("Int", lambda: Player.Int, json_output)
    test_property("StatCap", lambda: Player.StatCap, json_output)
    test_property("Hits", lambda: Player.Hits, json_output)
    test_property("HitsMax", lambda: Player.HitsMax, json_output)
    test_property("Stam", lambda: Player.Stam, json_output)
    test_property("StamMax", lambda: Player.StamMax, json_output)
    test_property("Mana", lambda: Player.Mana, json_output)
    test_property("ManaMax", lambda: Player.ManaMax, json_output)
    test_property("HitPointsIncrease", lambda: Player.HitPointsIncrease, json_output)
    test_property("MaximumHitPointsIncrease", lambda: Player.MaximumHitPointsIncrease, json_output)
    test_property("StaminaIncrease", lambda: Player.StaminaIncrease, json_output)
    test_property("MaximumStaminaIncrease", lambda: Player.MaximumStaminaIncrease, json_output)
    test_property("ManaIncrease", lambda: Player.ManaIncrease, json_output)
    test_property("MaximumManaIncrease", lambda: Player.MaximumManaIncrease, json_output)
    out("")

    # SECTION: Regeneration and Bonuses
    out("=" * 60, 88)
    out("  REGENERATION AND BONUSES", 88)
    out("=" * 60, 88)
    
    test_property("HitPointsRegeneration", lambda: Player.HitPointsRegeneration, json_output)
    test_property("StaminaRegeneration", lambda: Player.StaminaRegeneration, json_output)
    test_property("ManaRegeneration", lambda: Player.ManaRegeneration, json_output)
    test_property("DamageChanceIncrease", lambda: Player.DamageChanceIncrease, json_output)
    test_property("DefenseChanceIncrease", lambda: Player.DefenseChanceIncrease, json_output)
    test_property("EnhancePotions", lambda: Player.EnhancePotions, json_output)
    test_property("FasterCasting", lambda: Player.FasterCasting, json_output)
    test_property("FasterCastRecovery", lambda: Player.FasterCastRecovery, json_output)
    test_property("LowerManaCost", lambda: Player.LowerManaCost, json_output)
    test_property("LowerReagentCost", lambda: Player.LowerReagentCost, json_output)
    test_property("Luck", lambda: Player.Luck, json_output)
    test_property("ReflectPhysicalDamage", lambda: Player.ReflectPhysicalDamage, json_output)
    test_property("SpellDamageIncrease", lambda: Player.SpellDamageIncrease, json_output)
    test_property("SwingSpeedIncrease", lambda: Player.SwingSpeedIncrease, json_output)
    test_property("DexterityIncrease", lambda: Player.DexterityIncrease, json_output)
    test_property("IntelligenceIncrease", lambda: Player.IntelligenceIncrease, json_output)
    test_property("StrengthIncrease", lambda: Player.StrengthIncrease, json_output)
    out("")

    # SECTION: Resistances
    out("=" * 60, 88)
    out("  RESISTANCES", 88)
    out("=" * 60, 88)
    
    test_property("AR", lambda: Player.AR, json_output)
    test_property("FireResistance", lambda: Player.FireResistance, json_output)
    test_property("ColdResistance", lambda: Player.ColdResistance, json_output)
    test_property("PoisonResistance", lambda: Player.PoisonResistance, json_output)
    test_property("EnergyResistance", lambda: Player.EnergyResistance, json_output)
    out("")

    # SECTION: Position and Direction
    out("=" * 60, 88)
    out("  POSITION AND DIRECTION", 88)
    out("=" * 60, 88)
    
    test_property("Position", lambda: Player.Position, json_output, _fmt_point3d)
    test_property("Direction", lambda: Player.Direction, json_output)
    out("")

    # SECTION: Followers and Resources
    out("=" * 60, 88)
    out("  FOLLOWERS AND RESOURCES", 88)
    out("=" * 60, 88)
    
    test_property("Followers", lambda: Player.Followers, json_output)
    test_property("FollowersMax", lambda: Player.FollowersMax, json_output)
    test_property("Gold", lambda: Player.Gold, json_output)
    test_property("MaxWeight", lambda: Player.MaxWeight, json_output)
    test_property("Weight", lambda: Player.Weight, json_output)
    out("")

    # SECTION: State Flags
    out("=" * 60, 88)
    out("  STATE FLAGS", 88)
    out("=" * 60, 88)
    
    test_property("Paralized", lambda: Player.Paralized, json_output)
    test_property("Poisoned", lambda: Player.Poisoned, json_output)
    test_property("HasSpecial", lambda: Player.HasSpecial, json_output)
    test_property("YellowHits", lambda: Player.YellowHits, json_output)
    out("")

    # SECTION: Buffs and Lists
    out("=" * 60, 88)
    out("  BUFFS AND LISTS", 88)
    out("=" * 60, 88)
    
    # Buffs list with custom formatter
    def fmt_buffs(lst):
        n = len(lst) if lst else 0
        sample = ', '.join(lst[:5]) + (' …' if n > 5 else '') if lst else ''
        return f"{n} [{sample}]"
    
    test_property("Buffs", lambda: Player.Buffs, json_output, fmt_buffs)
    
    # BuffsInfo with custom formatter
    def fmt_buffs_info(info):
        return f"{len(info) if info else 0} detailed buffs"
    
    test_property("BuffsInfo", lambda: Player.BuffsInfo, json_output, fmt_buffs_info)
    
    # Corpses with custom formatter
    def fmt_corpses(corpses):
        return f"{len(corpses) if corpses else 0} corpses"
    
    test_property("Corpses", lambda: Player.Corpses, json_output, fmt_corpses)
    
    # Pets with custom formatter
    def fmt_pets(pets):
        return f"{len(pets) if pets else 0} pets"
    
    test_property("Pets", lambda: Player.Pets, json_output, fmt_pets)
    out("")
    
    # SECTION: Additional Properties
    out("=" * 60, 88)
    out("  ADDITIONAL PROPERTIES", 88)
    out("=" * 60, 88)
    
    test_property("Connected", lambda: Player.Connected, json_output)
    test_property("Fame", lambda: Player.Fame, json_output)
    test_property("Karma", lambda: Player.Karma, json_output)
    test_property("KarmaTitle", lambda: Player.KarmaTitle, json_output)
    test_property("HasPrimarySpecial", lambda: Player.HasPrimarySpecial, json_output)
    test_property("HasSecondarySpecial", lambda: Player.HasSecondarySpecial, json_output)
    test_property("HitChanceIncrease", lambda: Player.HitChanceIncrease, json_output)
    test_property("PrimarySpecial", lambda: Player.PrimarySpecial, json_output)
    test_property("SecondarySpecial", lambda: Player.SecondarySpecial, json_output)
    out("")

    out("=" * 60, 88)
    out("  TEST COMPLETE", 88)
    out("=" * 60, 88)
    out("")
    
    # Generate summary report
    total_properties = len(json_output["test_report"])
    working_properties = sum(1 for prop in json_output["test_report"].values() if prop["works"])
    failed_properties = sum(1 for prop in json_output["test_report"].values() if prop["works"] == False)
    
    out("=" * 60, 88)
    out("  TEST SUMMARY", 88)
    out("=" * 60, 88)
    out(f"Total properties tested: {total_properties}", 67)
    out(f"Working properties: {working_properties}", 68)
    out(f"Failed properties: {failed_properties}", 33 if failed_properties > 0 else 67)
    out(f"Success rate: {(working_properties/total_properties*100):.1f}%", 68)
    out("")
    
    if failed_properties > 0:
        out("Failed properties:", 33)
        for prop_name, prop_data in json_output["test_report"].items():
            if prop_data["works"] == False:
                out(f"  - {prop_name}: {prop_data['error']}", 33)
        out("")
    
    # Add summary to JSON
    json_output["summary"] = {
        "total_properties": total_properties,
        "working_properties": working_properties,
        "failed_properties": failed_properties,
        "success_rate": round(working_properties/total_properties*100, 1)
    }
    
    # Save JSON output
    out("=" * 60, 88)
    out("  SAVING JSON OUTPUT", 88)
    out("=" * 60, 88)
    
    try:
        # Ensure directory exists
        if not os.path.exists(BASE_PATH):
            os.makedirs(BASE_PATH)
        
        # Write JSON file
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(json_output, f, indent=2)
        
        out(f"JSON output saved to: {OUTPUT_FILE}", 68)
        out("")
    except Exception as e:
        out(f"Error saving JSON: {e}", 33)
        out("")
    
    return json_output


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

def example_check_player_stats():
    """Example: Display player stats summary"""
    Misc.SendMessage(f"=== {Player.Name} Stats ===", 88)
    Misc.SendMessage(f"STR: {Player.Str}  DEX: {Player.Dex}  INT: {Player.Int}", 67)
    Misc.SendMessage(f"HP: {Player.Hits}/{Player.HitsMax}", 68)

def example_check_buffs():
    """Example: Check for specific buff"""
    if Player.BuffsExist("Strength", False):
        time_left = Player.BuffTime("Strength")
        Misc.SendMessage(f"Strength active: {time_left}s", 68)
    else:
        Misc.SendMessage("Strength not active", 33)

def example_attack_nearest():
    """Example: Attack nearest hostile"""
    if Player.AttackType(-1, 10, "Nearest", [], [6]):
        Misc.SendMessage("Attacking nearest enemy", 68)
    else:
        Misc.SendMessage("No enemies found", 33)

def example_use_skill():
    """Example: Use a skill"""
    skill_value = Player.GetSkillValue("Magery")
    Misc.SendMessage(f"Magery: {skill_value}", 67)
    Player.UseSkill("Magery")

def example_check_equipment():
    """Example: Check equipped weapon"""
    weapon = Player.GetItemOnLayer("RightHand")
    if weapon:
        Misc.SendMessage(f"Weapon: {weapon.Name}", 67)
    else:
        Misc.SendMessage("No weapon equipped", 33)

def example_pathfind():
    """Example: Pathfind to location"""
    Player.PathFindTo(2500, 500, 0)
    Misc.SendMessage("Pathfinding...", 67)

def example_chat_party():
    """Example: Send party message"""
    if Player.InParty:
        Player.ChatParty("Ready!")
        Misc.SendMessage("Party message sent", 68)

def example_check_area():
    """Example: Get current area"""
    area = Player.Area()
    Misc.SendMessage(f"Current area: {area}", 67)


# Main execution
try:
    json_output = main()
    
    # Optionally run usage examples
    if RUN_USAGE_EXAMPLES:
        out("")
        out("")
        out("=" * 60, 88)
        out("  USAGE EXAMPLES - PRACTICAL DEMONSTRATIONS", 88)
        out("=" * 60, 88)
        out("Usage examples are defined as functions above", 67)
        out("Call them individually as needed:", 67)
        out("  - example_check_player_stats()", 67)
        out("  - example_check_buffs()", 67)
        out("  - example_attack_nearest()", 67)
        out("  - example_use_skill()", 67)
        out("  - example_check_equipment()", 67)
        out("  - example_pathfind()", 67)
        out("  - example_chat_party()", 67)
        out("  - example_check_area()", 67)
        out("=" * 60, 88)
        out("  USAGE EXAMPLES COMPLETE", 88)
        out("=" * 60, 88)

except Exception as e:
    out(f"FATAL ERROR: {e}", 33)
    import traceback
    out(traceback.format_exc(), 33)