"""
Download custom unlock sounds
"""

import os
from urllib.request import urlretrieve

class SoundDownloader:
    def __init__(self, client, keys, download_directory):
        self.client = client
        self.keys = keys
        self.download_directory = download_directory

    def download_sounds(self):
        os.makedirs(self.download_directory, exist_ok=True)

        for key, data in self.keys.items():
            if "sound" in data and "tidyhq" in data:
                sound_hash = data["sound"]
                tidyhq_id = data["tidyhq"]
                sound_data = self.client.get_sound_data(tidyhq_id)
                if sound_data["hash"] == sound_hash:
                    url = sound_data["url"]
                    file_name = f"{tidyhq_id}_{sound_hash}.mp3"
                    file_path = os.path.join(self.download_directory, file_name)
                    urlretrieve(url, file_path)
                    print(f"Downloaded sound file for TidyHQ ID {tidyhq_id} to {file_path}")

