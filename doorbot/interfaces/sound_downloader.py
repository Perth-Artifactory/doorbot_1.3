"""
Download custom unlock sounds.

To update keys or force it to redownload, create fresh instance of this class.

Stores the sounds as {file_name}_{sound_hash}.mp3 so if the hash changes, 
the new one will be used.
"""

import os
import logging
from urllib.request import urlretrieve
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class SoundDownloader:
    def __init__(self, client, keys, download_directory):
        self.client = client
        self.keys = keys
        self.download_directory = download_directory
        self.current_key_index = 0

    def download_next_sound(self):
        os.makedirs(self.download_directory, exist_ok=True)

        while self.current_key_index < len(self.keys):
            key, data = list(self.keys.items())[self.current_key_index]
            self.current_key_index += 1

            if "sound" in data and "tidyhq" in data:
                sound_hash = data["sound"]
                tidyhq_id = data["tidyhq"]
                sound_data = self.client.get_sound_data(tidyhq_id)
                if sound_data["hash"] == sound_hash:
                    url = sound_data["url"]
                    file_name = os.path.splitext(os.path.basename(urlparse(url).path))[0]
                    file_path = os.path.join(self.download_directory, f"{file_name}_{sound_hash}.mp3")
                    if not os.path.exists(file_path):
                        urlretrieve(url, file_path)
                        logger.debug(f"Downloaded sound file for TidyHQ ID {tidyhq_id} to {file_path}")
                        return True

        return False

