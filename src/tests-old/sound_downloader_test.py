from src.interfaces.sound_downloader import SoundDownloader
from src.interfaces.tidyauth_client import TidyAuthClient
from src.interfaces.user_manager import UserManager
import time
import logging
logging.basicConfig(level=logging.DEBUG)

# Usage
download_directory = "sounds/custom"

client = TidyAuthClient(base_url="http://none", token="")

user_manager = UserManager(client, "user_cache.json.example")
users = user_manager.get_users_with_custom_sounds()
print(f"Got {len(users)} with sounds")

sound_downloader = SoundDownloader(users_with_custom_sounds=users, download_directory=download_directory)

# Download the sound files
while sound_downloader.download_next_sound():
    print("got another!")
    time.sleep(0.01)
