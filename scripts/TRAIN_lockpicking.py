"""
TRAIN Lockpicking - a Razor Enhanced Python script for Ultima Online
Trains Lockpicking skill to 90 using a training box and lockpicks

Features:
- finds and uses lockpick training box
- Uses lockpicks from backpack
- Continues until skill reaches 90
- Provides feedback on training progress

VERSION::20250621
"""

import sys
from System.Collections.Generic import List
from Scripts.utilities.items import FindItem
import time

# Configuration
TARGET_SKILL = 90.0  # Stop training at this skill level
LOCKPICK_ID = 0x14FC  # Item ID for lockpicks
TRAINING_BOX_ID = 0x09AA  # Training box item ID
# TRAINING_BOX_HUE = 0x0000  # Default hue for training box
DELAY_BETWEEN_PICKS = 1000  # Delay in ms between lockpicking attempts

def find_training_box():
    """Find the lockpicking training box in player's backpack"""
    if not Player.Backpack:
        Misc.SendMessage("No backpack found!", 33)
        return None
        
    training_box = Items.FindByID(TRAINING_BOX_ID, -1, Player.Backpack.Serial)
    if not training_box:
        Misc.SendMessage("No training box found in backpack!", 33)
        return None
        
    return training_box

def find_lockpicks():
    """Find lockpicks in player's backpack"""
    if not Player.Backpack:
        Misc.SendMessage("No backpack found!", 33)
        return None
        
    lockpicks = Items.FindByID(LOCKPICK_ID, -1, Player.Backpack.Serial)
    if not lockpicks:
        Misc.SendMessage("No lockpicks found in backpack!", 33)
        return None
        
    return lockpicks

def train_lockpicking():
    """Main training loop"""
    Misc.SendMessage("Starting Lockpicking training...", 66)
    
    while Player.GetRealSkillValue('Lockpicking') < TARGET_SKILL:
        # Find required items
        training_box = find_training_box()
        lockpicks = find_lockpicks()
        
        if not training_box or not lockpicks:
            Misc.SendMessage("Missing required items. Stopping training.", 33)
            break
            
        # Use lockpick on training box
        Items.UseItem(lockpicks)
        Target.WaitForTarget(1000)
        Target.TargetExecute(training_box)
        
        # Wait for the lockpicking attempt
        Misc.Pause(DELAY_BETWEEN_PICKS)
        
        # Show progress
        current_skill = Player.GetRealSkillValue('Lockpicking')
        Misc.SendMessage(f"Current Lockpicking: {current_skill:.1f}", 66)
        
        # Check if we've reached target skill
        if current_skill >= TARGET_SKILL:
            Misc.SendMessage("Target skill reached! Training complete.", 67)
            break

# Start the training
if __name__ == '__main__':
    train_lockpicking()
