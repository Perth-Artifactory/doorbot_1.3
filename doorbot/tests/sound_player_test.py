import argparse
import pygame
import time
from doorbot.interfaces.tidyauth_client import TidyAuthClient
from doorbot.interfaces.user_manager import UserManager
from doorbot.interfaces.sound_player import SoundPlayer

import logging
logging.basicConfig(level=logging.DEBUG)

def wait_for_music():
    while pygame.mixer.music.get_busy() == True:
        continue

# Usage
sound_directory = "sounds"
custom_sound_dir = "sounds/custom"

client = TidyAuthClient(base_url="http://none", token="")

user_manager = UserManager(client, "user_cache.json.example")

# Initialize the SoundPlayer with the sound directory
sound_player = SoundPlayer(sound_directory, custom_sound_dir)

# Play the sound for a given key
sound_player.play_access_granted_or_custom(user_manager.get_user_details("0123456789"))
wait_for_music()

sound_player.play_access_granted_or_custom({"name": "Test user, no sound"})
wait_for_music()

sound_player.play_denied()
wait_for_music()

time.sleep(0.5)

# Test where all sound files don't exist
print()
print("Test if sound dir doesn't exist")
sound_player = SoundPlayer('baddir', 'baddir')

sound_player.play_denied()
wait_for_music()

sound_player.play_access_granted_or_custom(None)
wait_for_music()

sound_player.play_access_granted_or_custom(user_manager.get_user_details("0123456789"))
wait_for_music()

time.sleep(0.5)
