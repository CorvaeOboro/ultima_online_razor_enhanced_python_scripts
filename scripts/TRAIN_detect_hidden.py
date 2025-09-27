"""
TRAIN detect hidden - a Razor Enhanced Python script for Ultima Online

Training Detect Hidden by using the skill and targeting self

VERSION::20250922
"""

TARGET_SKILL_NAME = "Detect Hidden"
TARGET_VALUE = 60.0 # target skill max
WAIT_BETWEEN_ATTEMPTS_MS = 10000  # 10 seconds 
TARGET_TIMEOUT_MS = 10000

def get_skill_value(skill_name):
    try:
        return float(Player.GetSkillValue(skill_name))
    except Exception as e:
        Misc.SendMessage(f"Error reading skill '{skill_name}': {e}", 33)
        return 0.0

def train_detect_hidden_until(target_value):
    start_val = get_skill_value(TARGET_SKILL_NAME)
    Misc.SendMessage(
        f"Training {TARGET_SKILL_NAME} from {start_val:.1f} to {target_value:.1f}...",
        68,
    )

    attempts = 0
    while True:
        current = get_skill_value(TARGET_SKILL_NAME)
        if current >= target_value:
            Misc.SendMessage(
                f"{TARGET_SKILL_NAME} reached target {current:.1f} >= {target_value:.1f}. Done.",
                68,
            )
            break

        # Use the skill
        Player.UseSkill(TARGET_SKILL_NAME)

        # Wait for target cursor and target self (player's own serial)
        if Target.WaitForTarget(TARGET_TIMEOUT_MS, False):
            try:
                Target.TargetExecute(Player.Serial)
            except Exception as e:
                Misc.SendMessage(f"TargetExecute failed: {e}", 33)
        else:
            Misc.SendMessage("No target cursor appeared. Retrying after delay...", 33)

        attempts += 1
        Misc.SendMessage(
            f"{TARGET_SKILL_NAME} attempt {attempts}, current: {current:.1f}/{target_value:.1f}",
            55,
        )

        # Wait between attempts 
        Misc.Pause(WAIT_BETWEEN_ATTEMPTS_MS)

if __name__ == "__main__":
    try:
        train_detect_hidden_until(TARGET_VALUE)
    except Exception as e:
        Misc.SendMessage(f"Unexpected error in TRAIN_detect_hidden: {e}", 33)