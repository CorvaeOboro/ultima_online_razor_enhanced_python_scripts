"""
Development API Player object - a Razor Enhanced script for Ultima Online.

REFERENCE = https://razorenhanced.readthedocs.io/api/Player.html
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
"""

# Non-destructive probe of Player.* properties listed above

import time


def out(msg, color=90):
    try:
        Misc.SendMessage(f"[PLAYER] {msg}", color)
    except Exception:
        print(f"[PLAYER] {msg}")


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


def main():
    # Preliminary quick access check 
    try:
        out(f"Player.Serial quick check: {Player.Serial}")
    except Exception as e:
        out(f"Player.Serial quick check: ERROR {e}", 33)

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

    out("— Player API Probe —", 67)

    # Item-like 
    try:
        out(f"Backpack: {_fmt_item(Player.Backpack)}")
    except Exception as e:
        out(f"Backpack: ERROR {e}", 33)
    try:
        out(f"Bank: {_fmt_item(Player.Bank)}")
    except Exception as e:
        out(f"Bank: ERROR {e}", 33)
    try:
        out(f"Mount: {_fmt_item(Player.Mount)}")
    except Exception as e:
        out(f"Mount: ERROR {e}", 33)
    try:
        out(f"Quiver: {_fmt_item(Player.Quiver)}")
    except Exception as e:
        out(f"Quiver: ERROR {e}", 33)

    # Basic identifiers and flags 
    try:
        out(f"Serial: {Player.Serial}")
    except Exception as e:
        out(f"Serial: ERROR {e}", 33)
    try:
        out(f"Name: {Player.Name}")
    except Exception as e:
        out(f"Name: ERROR {e}", 33)
    try:
        out(f"Body: {Player.Body}")
    except Exception as e:
        out(f"Body: ERROR {e}", 33)
    try:
        out(f"MobileID: {Player.MobileID}")
    except Exception as e:
        out(f"MobileID: ERROR {e}", 33)
    try:
        out(f"StaticMount: {Player.StaticMount}")
    except Exception as e:
        out(f"StaticMount: ERROR {e}", 33)
    try:
        out(f"Female: {Player.Female}")
    except Exception as e:
        out(f"Female: ERROR {e}", 33)
    try:
        out(f"IsGhost: {Player.IsGhost}")
    except Exception as e:
        out(f"IsGhost: ERROR {e}", 33)
    try:
        out(f"Visible: {Player.Visible}")
    except Exception as e:
        out(f"Visible: ERROR {e}", 33)
    try:
        out(f"WarMode: {Player.WarMode}")
    except Exception as e:
        out(f"WarMode: ERROR {e}", 33)
    try:
        out(f"InParty: {Player.InParty}")
    except Exception as e:
        out(f"InParty: ERROR {e}", 33)
    try:
        out(f"Notoriety: {Player.Notoriety}")
    except Exception as e:
        out(f"Notoriety: ERROR {e}", 33)
    try:
        out(f"Map: {Player.Map}")
    except Exception as e:
        out(f"Map: ERROR {e}", 33)

    # Stats and caps 
    try:
        out(f"Str: {Player.Str}")
    except Exception as e:
        out(f"Str: ERROR {e}", 33)
    try:
        out(f"Dex: {Player.Dex}")
    except Exception as e:
        out(f"Dex: ERROR {e}", 33)
    try:
        out(f"Int: {Player.Int}")
    except Exception as e:
        out(f"Int: ERROR {e}", 33)
    try:
        out(f"StatCap: {Player.StatCap}")
    except Exception as e:
        out(f"StatCap: ERROR {e}", 33)
    try:
        out(f"Hits: {Player.Hits}")
    except Exception as e:
        out(f"Hits: ERROR {e}", 33)
    try:
        out(f"HitsMax: {Player.HitsMax}")
    except Exception as e:
        out(f"HitsMax: ERROR {e}", 33)
    try:
        out(f"Stam: {Player.Stam}")
    except Exception as e:
        out(f"Stam: ERROR {e}", 33)
    try:
        out(f"StamMax: {Player.StamMax}")
    except Exception as e:
        out(f"StamMax: ERROR {e}", 33)
    try:
        out(f"Mana: {Player.Mana}")
    except Exception as e:
        out(f"Mana: ERROR {e}", 33)
    try:
        out(f"ManaMax: {Player.ManaMax}")
    except Exception as e:
        out(f"ManaMax: ERROR {e}", 33)
    try:
        out(f"HitPointsIncrease: {Player.HitPointsIncrease}")
    except Exception as e:
        out(f"HitPointsIncrease: ERROR {e}", 33)
    try:
        out(f"MaximumHitPointsIncrease: {Player.MaximumHitPointsIncrease}")
    except Exception as e:
        out(f"MaximumHitPointsIncrease: ERROR {e}", 33)
    try:
        out(f"StaminaIncrease: {Player.StaminaIncrease}")
    except Exception as e:
        out(f"StaminaIncrease: ERROR {e}", 33)
    try:
        out(f"MaximumStaminaIncrease: {Player.MaximumStaminaIncrease}")
    except Exception as e:
        out(f"MaximumStaminaIncrease: ERROR {e}", 33)
    try:
        out(f"ManaIncrease: {Player.ManaIncrease}")
    except Exception as e:
        out(f"ManaIncrease: ERROR {e}", 33)
    try:
        out(f"MaximumManaIncrease: {Player.MaximumManaIncrease}")
    except Exception as e:
        out(f"MaximumManaIncrease: ERROR {e}", 33)

    # Regeneration and bonuses 
    try:
        out(f"HitPointsRegeneration: {Player.HitPointsRegeneration}")
    except Exception as e:
        out(f"HitPointsRegeneration: ERROR {e}", 33)
    try:
        out(f"StaminaRegeneration: {Player.StaminaRegeneration}")
    except Exception as e:
        out(f"StaminaRegeneration: ERROR {e}", 33)
    try:
        out(f"ManaRegeneration: {Player.ManaRegeneration}")
    except Exception as e:
        out(f"ManaRegeneration: ERROR {e}", 33)
    try:
        out(f"DamageChanceIncrease: {Player.DamageChanceIncrease}")
    except Exception as e:
        out(f"DamageChanceIncrease: ERROR {e}", 33)
    try:
        out(f"DefenseChanceIncrease: {Player.DefenseChanceIncrease}")
    except Exception as e:
        out(f"DefenseChanceIncrease: ERROR {e}", 33)
    try:
        out(f"EnhancePotions: {Player.EnhancePotions}")
    except Exception as e:
        out(f"EnhancePotions: ERROR {e}", 33)
    try:
        out(f"FasterCasting: {Player.FasterCasting}")
    except Exception as e:
        out(f"FasterCasting: ERROR {e}", 33)
    try:
        out(f"FasterCastRecovery: {Player.FasterCastRecovery}")
    except Exception as e:
        out(f"FasterCastRecovery: ERROR {e}", 33)
    try:
        out(f"LowerManaCost: {Player.LowerManaCost}")
    except Exception as e:
        out(f"LowerManaCost: ERROR {e}", 33)
    try:
        out(f"LowerReagentCost: {Player.LowerReagentCost}")
    except Exception as e:
        out(f"LowerReagentCost: ERROR {e}", 33)
    try:
        out(f"Luck: {Player.Luck}")
    except Exception as e:
        out(f"Luck: ERROR {e}", 33)
    try:
        out(f"ReflectPhysicalDamage: {Player.ReflectPhysicalDamage}")
    except Exception as e:
        out(f"ReflectPhysicalDamage: ERROR {e}", 33)
    try:
        out(f"SpellDamageIncrease: {Player.SpellDamageIncrease}")
    except Exception as e:
        out(f"SpellDamageIncrease: ERROR {e}", 33)
    try:
        out(f"SwingSpeedIncrease: {Player.SwingSpeedIncrease}")
    except Exception as e:
        out(f"SwingSpeedIncrease: ERROR {e}", 33)
    try:
        out(f"DexterityIncrease: {Player.DexterityIncrease}")
    except Exception as e:
        out(f"DexterityIncrease: ERROR {e}", 33)
    try:
        out(f"IntelligenceIncrease: {Player.IntelligenceIncrease}")
    except Exception as e:
        out(f"IntelligenceIncrease: ERROR {e}", 33)
    try:
        out(f"StrengthIncrease: {Player.StrengthIncrease}")
    except Exception as e:
        out(f"StrengthIncrease: ERROR {e}", 33)

    # Resistances 
    try:
        out(f"AR: {Player.AR}")
    except Exception as e:
        out(f"AR: ERROR {e}", 33)
    try:
        out(f"FireResistance: {Player.FireResistance}")
    except Exception as e:
        out(f"FireResistance: ERROR {e}", 33)
    try:
        out(f"ColdResistance: {Player.ColdResistance}")
    except Exception as e:
        out(f"ColdResistance: ERROR {e}", 33)
    try:
        out(f"PoisonResistance: {Player.PoisonResistance}")
    except Exception as e:
        out(f"PoisonResistance: ERROR {e}", 33)
    try:
        out(f"EnergyResistance: {Player.EnergyResistance}")
    except Exception as e:
        out(f"EnergyResistance: ERROR {e}", 33)

    # Position and direction 
    try:
        out(f"Position: {_fmt_point3d(Player.Position)}")
    except Exception as e:
        out(f"Position: ERROR {e}", 33)
    try:
        out(f"Direction: {Player.Direction}")
    except Exception as e:
        out(f"Direction: ERROR {e}", 33)

    # Followers and containers 
    try:
        out(f"Followers: {Player.Followers}")
    except Exception as e:
        out(f"Followers: ERROR {e}", 33)
    try:
        out(f"FollowersMax: {Player.FollowersMax}")
    except Exception as e:
        out(f"FollowersMax: ERROR {e}", 33)
    try:
        out(f"Gold: {Player.Gold}")
    except Exception as e:
        out(f"Gold: ERROR {e}", 33)
    try:
        out(f"MaxWeight: {Player.MaxWeight}")
    except Exception as e:
        out(f"MaxWeight: ERROR {e}", 33)
    try:
        out(f"Weight: {Player.Weight}")
    except Exception as e:
        out(f"Weight: ERROR {e}", 33)

    # State flags 
    try:
        out(f"Paralized: {Player.Paralized}")
    except Exception as e:
        out(f"Paralized: ERROR {e}", 33)
    try:
        out(f"Poisoned: {Player.Poisoned}")
    except Exception as e:
        out(f"Poisoned: ERROR {e}", 33)
    try:
        out(f"HasSpecial: {Player.HasSpecial}")
    except Exception as e:
        out(f"HasSpecial: ERROR {e}", 33)
    try:
        out(f"YellowHits: {Player.YellowHits}")
    except Exception as e:
        out(f"YellowHits: ERROR {e}", 33)

    # Buffs list 
    try:
        lst = Player.Buffs
        n = len(lst) if lst else 0
        sample = ', '.join(lst[:5]) + (' …' if n > 5 else '') if lst else ''
        out(f"Buffs: {n} [{sample}]")
    except Exception as e:
        out(f"Buffs: ERROR {e}", 33)

    out("— End of Player API Probe —", 67)


if __name__ == '__main__':
    main()