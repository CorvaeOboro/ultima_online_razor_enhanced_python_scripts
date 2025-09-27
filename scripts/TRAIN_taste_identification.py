"""
TRAIN Taste Identification - a Razor Enhanced Python script for Ultima Online

VERSION::20250922
"""
# Configuration
TARGET_SKILL_NAME = "Taste Identification"
TARGET_VALUE = 100.0
WAIT_BETWEEN_ATTEMPTS_MS = 1000  # 10 seconds to be shard-friendly
TARGET_TIMEOUT_MS = 1000

"""
Food targeting configuration (mirrors ITEM_food_eater.py sets where relevant)
We will exclude special hued variants like blue fish steak (mana) and berries.
"""

# Excluded specific hued items: (ItemID, Hue)
EXCLUDED_HUED_ITEMS = {
    (0x097B, 0x0825),  # Blue mana fish steak
    (0x09D0, 0x0480),  # Arcane Berries (Apple ID with hue 0x0480)
    (0x09D0, 0x0006),  # Tribal Berries (Apple ID with hue 0x0006)
}

# Food item IDs to consider in backpack
FOOD_ITEM_IDS = [
    # Fruits
    0x09D2,  # Peach
    0x09D0,  # Apple
    0x09D1,  # Grapes
    0x0994,  # Pear
    0x171F,  # Banana
    0x0C6A,  # Pumpkin
    0x09EC,  # Onion
    0x0C78,  # Carrot
    0x0C6C,  # Squash
    # Baked goods
    0x09EB,  # Muffins
    0x103B,  # Bread Loaf
    # Meats
    0x097D,  # Cheese
    0x09C0,  # Sausage
    0x09B7,  # Cooked Bird
    0x09F2,  # Cut of Ribs
    0x09C9,  # Ham
    0x160A,  # Leg of Lamb
    0x1608,  # Chicken Leg
    0x097A,  # Fish Steak
    0x097B,  # Fish Steak 2
    0x097E,  # Bacon
]


def get_skill_value(skill_name):
    try:
        return float(Player.GetSkillValue(skill_name))
    except Exception as e:
        Misc.SendMessage(f"Error reading skill '{skill_name}': {e}", 33)
        return 0.0


def train_taste_id_until(target_value):
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

        # Locate a valid food item in backpack (excluding specific hued variants)
        target_item = find_valid_food_in_backpack()
        if not target_item:
            Misc.SendMessage("No valid food item found in backpack to Taste ID. Retrying...", 33)
            Misc.Pause(5000)
            continue

        # Use the skill
        Player.UseSkill(TARGET_SKILL_NAME)

        # Wait for target cursor and target the chosen food item
        if Target.WaitForTarget(TARGET_TIMEOUT_MS, False):
            try:
                Target.TargetExecute(target_item.Serial)
            except Exception as e:
                Misc.SendMessage(f"TargetExecute failed: {e}", 33)
        else:
            Misc.SendMessage("No target cursor appeared. Retrying after delay...", 33)

        attempts += 1
        Misc.SendMessage(
            f"{TARGET_SKILL_NAME} attempt {attempts}, current: {current:.1f}/{target_value:.1f}",
            55,
        )

        # Wait between attempts (server-friendly)
        Misc.Pause(WAIT_BETWEEN_ATTEMPTS_MS)


def find_valid_food_in_backpack():
    """Return the first valid food item in the player's backpack not in excluded hues."""
    try:
        pack_serial = Player.Backpack.Serial
    except Exception:
        pack_serial = None
    if not pack_serial:
        return None

    for item_id in FOOD_ITEM_IDS:
        items = Items.FindByID(item_id, -1, pack_serial)
        if not items:
            continue
        if not isinstance(items, list):
            items = [items]
        for it in items:
            try:
                iid = int(it.ItemID)
                hue = int(it.Hue)
            except Exception:
                iid = it.ItemID
                hue = it.Hue
            # Ensure still in backpack and not excluded
            if it.Container != pack_serial:
                continue
            if (iid, hue) in EXCLUDED_HUED_ITEMS:
                continue
            return it
    return None


if __name__ == "__main__":
    try:
        train_taste_id_until(TARGET_VALUE)
    except Exception as e:
        Misc.SendMessage(f"Unexpected error in TRAIN_taste_identification: {e}", 33)