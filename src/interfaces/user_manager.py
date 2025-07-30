"""
Manaage downloading, storing and authorising keys and sounds for each user.
"""

import os
import json
import logging

logger = logging.getLogger(__name__)

class UserManager:
    def __init__(self, api_client, cache_path):
        self.api_client = api_client
        self.cache_path = cache_path

        # Load initial copy of keys from disk in case network is down on startup
        self.user_data = self._load_keys()

        if self.user_data is None or len(self.user_data) == 0:
            logger.error("No keys were loaded")

    def is_key_authorised(self, key):
        """Return True if key is authorised to open the door"""
        return self.user_data is not None and key in self.user_data
    
    def key_count(self):
        if self.user_data is None:
            return 0
        return len(self.user_data)
    
    def get_user_details(self, key):
        if self.user_data is not None and key in self.user_data:
            return self.user_data[key]
        return None

    def get_users_with_custom_sounds(self):
        # Filter to those with custom sound
        if self.user_data is not None:
            return {key: user for key, user in self.user_data.items() if "sound" in user}
        return {}

    async def download_keys(self):
        """
        Download keys and populate custom sound info.
        Returns True if keys changed.
        """
        # Download keys
        new_keys = await self.api_client.get_door_keys()

        if new_keys is not None:
            # Iterate through users and fetch sound URLs if sound hash has changed
            for key, data in new_keys.items():
                if "sound" in data and "tidyhq" in data:
                    # Check if sound hash has changed
                    fetch = True
                    existing_user_details = self.get_user_details(key)
                    if existing_user_details is not None and "sound" in existing_user_details:
                        if existing_user_details["sound"] == data["sound"]:
                            # Sound hash has not changed, don"t both fetching URL
                            fetch = False
                    if fetch:
                        # Sound hash has changed
                        sound_data = await self.api_client.get_sound_data(data["tidyhq"])
                        if sound_data is not None and "url" in sound_data:
                            data["sound_url"] = sound_data["url"]
                    else:
                        data["sound_url"] = existing_user_details["sound_url"]
            if new_keys != self.user_data:
                # Keys successfully downloaded and are different, save
                self.user_data = new_keys
                self._save_keys()
                return True
        return False

    def _load_keys(self):
        if os.path.exists(self.cache_path):
            with open(self.cache_path, "r") as file:
                keys = json.load(file)
            logger.debug(f"Loaded keys from {self.cache_path}")
            return keys
        else:
            logger.warn(f"No keys file found at {self.cache_path}")
            return None

    def _save_keys(self):
        with open(self.cache_path, "w") as file:
            json.dump(self.user_data, file, indent=4)
        logger.debug(f"Saved keys to {self.cache_path}")

