import argparse
import time
from doorbot.interfaces.tidyauth_client import TidyAuthClient
from doorbot.interfaces.user_manager import UserManager
from doorbot.interfaces.sound_player import SoundPlayer

import logging
logging.basicConfig(level=logging.DEBUG)

# Usage
sound_directory = "sounds"
custom_sound_dir = "sounds/custom"

client = TidyAuthClient(base_url="http://none", token="")

user_manager = UserManager(client, "user_cache.json.example")

# Initialize the SoundPlayer with the sound directory
sound_player = SoundPlayer(sound_directory, custom_sound_dir)

def wait_until_done():
    print("Waiting")
    while True:
        time.sleep(1)
        if not sound_player.player.is_playing():
            time.sleep(1)
            break
        print("Looping")
        


print()
print("Play the sound for a given key")
sound_player.play_access_granted_or_custom(user_manager.get_user_details("0123456789"))
time.sleep(0.5)
print("Interrupt the previous")
sound_player.play_access_granted_or_custom(user_manager.get_user_details("0123456789"))
time.sleep(5)

sound_player.play_access_granted_or_custom({"name": "Test user, no sound"})
time.sleep(5)

sound_player.play_denied()
time.sleep(1)
sound_player.play_denied()
time.sleep(0.5)
print("Interrupt the previous")
sound_player.play_denied()
time.sleep(5)


print()
print("Test if sound dir doesn't exist")
sound_player = SoundPlayer('baddir', 'baddir')

sound_player.play_denied()
time.sleep(1)

sound_player.play_access_granted_or_custom(None)
time.sleep(1)

sound_player.play_access_granted_or_custom(user_manager.get_user_details("0123456789"))
time.sleep(1)

print()
print("Play and wait")
sound_player.play_sound(sound_directory + '/granted.mp3')
wait_until_done()
sound_player.play_sound(sound_directory + '/denied.mp3')
wait_until_done()
sound_player.play_sound(sound_directory + '/granted.mp3')
wait_until_done()

