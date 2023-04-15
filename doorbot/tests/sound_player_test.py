import argparse
import pygame
import time
from doorbot.interfaces.tidyauth_client import DoorKeysClient
from doorbot.interfaces.sound_player import SoundPlayer

import logging
logging.basicConfig(level=logging.DEBUG)


# Usage
sound_directory = "sounds"
custom_sound_dir = "sounds/custom"

parser = argparse.ArgumentParser()
parser.add_argument('token')
parser.add_argument('key_to_play')
args = parser.parse_args()

# Usage
# base_url = "http://enclave:5000"  # At Artifactory
base_url = "http://localhost:1338"  # At home via tsh
token = args.token

client = DoorKeysClient(base_url, token)
if not client.test_route():
    raise Exception("Test API connection fail")

door_keys = client.get_door_keys()

# Initialize the SoundPlayer with the sound directory
sound_player = SoundPlayer(sound_directory, custom_sound_dir)

# Play the sound for a given key
sound_player.play_access_granted_or_custom(args.key_to_play, door_keys)

while pygame.mixer.music.get_busy() == True:
    continue


sound_player.play_access_granted_or_custom("123", door_keys)

while pygame.mixer.music.get_busy() == True:
    continue

sound_player.play_denied()

while pygame.mixer.music.get_busy() == True:
    continue

time.sleep(0.5)

