import argparse
from doorbot.interfaces.sound_downloader import SoundDownloader
from doorbot.interfaces.tidyauth_client import DoorKeysClient
import time
import logging
logging.basicConfig(level=logging.DEBUG)

# Usage
download_directory = "sounds/custom"

parser = argparse.ArgumentParser()
parser.add_argument('token')
args = parser.parse_args()

# Usage
# base_url = "http://enclave:5000"  # At Artifactory
base_url = "http://localhost:1338"  # At home via tsh
token = args.token

client = DoorKeysClient(base_url, token)
if not client.test_route():
    raise Exception("Test API connection fail")

door_keys = client.get_door_keys()

# Initialize the SoundDownloader with the DoorKeysClient, door keys, and download directory
sound_downloader = SoundDownloader(client, door_keys, download_directory)

# Download the sound files
while sound_downloader.download_next_sound():
    print('got another!')
    time.sleep(0.01)
