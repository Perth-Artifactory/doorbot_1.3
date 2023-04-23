"""
Download custom unlock sounds.

The class is disposable - to start a fresh round of downloads with new user 
list, create a new instance of this class.

Stores the sounds as {file_name}_{sound_hash}.mp3 so if the hash changes, 
a new one will be created. It does not cleanup old sound files.
"""

import os
import logging
from urllib.request import urlretrieve
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class SoundDownloader:
    def __init__(self, users_with_custom_sounds, download_directory):
        self.users = users_with_custom_sounds
        self.current_user_index = 0

        self.download_directory = download_directory
        os.makedirs(self.download_directory, exist_ok=True)

    def download_next_sound(self):
        while self.current_user_index < len(self.users):
            key, user = list(self.users.items())[self.current_user_index]
            self.current_user_index += 1

            if "sound" in user and "sound_url" in user:
                sound_hash = user["sound"]
                url = user["sound_url"]
                file_name = os.path.splitext(os.path.basename(urlparse(url).path))[0]
                file_path = os.path.join(self.download_directory, f"{file_name}_{sound_hash}.mp3")
                if not os.path.exists(file_path):
                    urlretrieve(url, file_path)
                    logger.debug(f"Downloaded sound file '{file_path}'")
                    return True

        return False

