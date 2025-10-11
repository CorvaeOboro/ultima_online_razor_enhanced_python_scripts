"""
TRAIN Lockpicking - a Razor Enhanced Python script for Ultima Online

Training Lockpicking skill using a training box and lockpicks
Searches for lockpick training box in backpack

VERSION::20250925
"""

DEBUG_MODE = True  # Set to True to enable debug messages

TARGET_SKILL = 100.0  # Stop training at this skill level
LOCKPICK_ID = 0x14FC  # Item ID for lockpicks
TRAINING_BOX_ID = 0x09AA  # Training box item ID
DELAY_BETWEEN_PICKS = 1000  # Delay in ms between lockpicking attempts

def debug_message(msg, color=67):
    """Show debug messages only when DEBUG_MODE is enabled."""
    if DEBUG_MODE:
        Misc.SendMessage(f"[Lockpicking] {msg}", color)

def find_training_box():
    """Find the lockpicking training box in player's backpack"""
    if not Player.Backpack:
        debug_message("No backpack found!", 33)
        return None
        
    training_box = Items.FindByID(TRAINING_BOX_ID, -1, Player.Backpack.Serial)
    if not training_box:
        debug_message("No training box found in backpack!", 33)
        return None
        
    return training_box

def find_lockpicks():
    """Find lockpicks in player's backpack"""
    if not Player.Backpack:
        debug_message("No backpack found!", 33)
        return None
        
    lockpicks = Items.FindByID(LOCKPICK_ID, -1, Player.Backpack.Serial)
    if not lockpicks:
        debug_message("No lockpicks found in backpack!", 33)
        return None
        
    return lockpicks

def train_lockpicking():
    """Main training loop"""
    debug_message("Starting Lockpicking training...", 66)
    # Early exit if already at or above target
    current_skill = Player.GetRealSkillValue('Lockpicking')
    if current_skill >= TARGET_SKILL:
        debug_message(f"Current Lockpicking {current_skill:.1f} is already at or above target {TARGET_SKILL:.1f}. Nothing to do.", 68)
        return
    
    while Player.GetRealSkillValue('Lockpicking') < TARGET_SKILL:
        # Find required items
        training_box = find_training_box()
        lockpicks = find_lockpicks()
        
        if not training_box or not lockpicks:
            debug_message("Missing required items. Stopping training.", 33)
            break
            
        # Use lockpick on training box
        Items.UseItem(lockpicks)
        Target.WaitForTarget(1000)
        Target.TargetExecute(training_box)
        
        # Wait for the lockpicking attempt
        Misc.Pause(DELAY_BETWEEN_PICKS)
        
        # Show progress
        current_skill = Player.GetRealSkillValue('Lockpicking')
        debug_message(f"Current Lockpicking: {current_skill:.1f}", 66)
        
        # Check if we've reached target skill
        if current_skill >= TARGET_SKILL:
            debug_message("Target skill reached! Training complete.", 68)
            break

# Start the training
if __name__ == '__main__':
    train_lockpicking()
