"""
TRAIN Evaluate Intelligence - a Razor Enhanced Python script for Ultima Online

Training Evaluate Intelligence by using the skill and targeting a random nonplayer mobile within range.

STATUS:: working
VERSION::20250925
"""

SKILL_NAME = "Evaluate Intelligence"
TARGET_RANGE = 8  
DELAY_MS = 2500   

DEBUG_MODE = False
_ROTATION_INDEX = 0

def debug_message(msg, color=68):
    if DEBUG_MODE:
        Misc.SendMessage(f"[EvalInt] {msg}", color)

def get_valid_targets():
    # Find all mobiles in range except self, dead, or hidden
    my_serial = Player.Serial
    targets = []
    # Build a proper filter; passing None causes a null reference in Razor Enhanced
    mob_filter = Mobiles.Filter()
    mob_filter.Enabled = True
    mob_filter.RangeMax = TARGET_RANGE
    try:
        mobiles = Mobiles.ApplyFilter(mob_filter)
    except Exception as e:
        debug_message(f"Error applying mobile filter: {e}", 33)
        mobiles = []

    for mob in mobiles:
        if not mob:
            continue
        try:
            if mob.Serial == my_serial:
                continue
            if hasattr(mob, "Distance") and mob.Distance is not None and mob.Distance > TARGET_RANGE:
                continue
            if getattr(mob, "Dead", False) or getattr(mob, "Hidden", False):
                continue
            targets.append(mob)
        except Exception as e:
            debug_message(f"Skipping a mobile due to error: {e}", 33)
            continue
    return targets

def _select_rotating_target(targets):
    """pseudo-randomly vary target selection by index that increments per call"""
    global _ROTATION_INDEX
    if not targets:
        return None
    try:
        base = int(Player.Serial)
    except Exception:
        base = 0
    # Stable ordering using XOR with player serial and then by raw serial as tiebreaker
    ordered = sorted(targets, key=lambda m: ((getattr(m, 'Serial', 0) ^ base), getattr(m, 'Serial', 0)))
    idx = 0
    try:
        if len(ordered) > 0:
            idx = _ROTATION_INDEX % len(ordered)
    except Exception:
        idx = 0
    # Increment rotation for next call
    _ROTATION_INDEX = (_ROTATION_INDEX + 1) & 0x7FFFFFFF
    return ordered[idx]

def use_eval_int_on_random():
    targets = get_valid_targets()
    if not targets:
        debug_message("No valid targets in range!", 33)
        return False
    target = _select_rotating_target(targets)
    target_name = getattr(target, "Name", "Unknown")
    try:
        target_serial_hex = hex(target.Serial)
    except Exception:
        target_serial_hex = "<unknown>"
    debug_message(f"Using {SKILL_NAME} on {target_name} (Serial: {target_serial_hex})", 63)
    Player.UseSkill(SKILL_NAME)
    # Wait for target cursor (up to ~2000ms) without using time module
    waited = 0
    while not Target.HasTarget() and waited < 2000:
        Misc.Pause(50)
        waited += 50
    if not Target.HasTarget():
        debug_message("No target cursor appeared after skill use!", 33)
        return False
    Target.WaitForTarget(1000)
    try:
        Target.TargetExecute(target)
    except Exception as e:
        try:
            Target.TargetExecute(target.Serial)
        except Exception as e2:
            debug_message(f"Targeting failed: {e} / {e2}", 33)
            return False
    return True

def main():
    debug_message(f"Starting {SKILL_NAME} training script.")
    while Player.Connected:
        success = use_eval_int_on_random()
        Misc.Pause(DELAY_MS)

if __name__ == "__main__":
    main()