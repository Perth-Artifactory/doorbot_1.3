"""
Play sounds for key access
"""

import pygame
import os
import fnmatch
import logging

logger = logging.getLogger(__name__)

class SoundPlayer:
    def __init__(self, sound_dir, custom_sound_dir):
        self.sound_dir = sound_dir
        self.custom_sound_dir = custom_sound_dir
        pygame.mixer.init()

    def find_sound_by_hash(self, sound_hash):
        for file_name in os.listdir(self.custom_sound_dir):
            if fnmatch.fnmatch(file_name, f"*_{sound_hash}.mp3"):
                return os.path.join(self.custom_sound_dir, file_name)
        return None

    def play_access_granted_or_custom(self, key, keys_data):
        # Fallback option if no custom sound is simply "access granted"
        sound_to_play = os.path.join(self.sound_dir, "granted.mp3")

        # Try to find a custom sound
        if key in keys_data:
            key_data = keys_data[key]
            if "sound" in key_data:
                sound_hash = key_data["sound"]
                file_path = self.find_sound_by_hash(sound_hash)
                if file_path:
                    sound_to_play = file_path

        pygame.mixer.music.load(sound_to_play)
        pygame.mixer.music.play()
        logger.debug(f"Playing access granted for key {key}: {sound_to_play}")

    def play_denied(self):
        sound_to_play = os.path.join(self.sound_dir, "denied.mp3")
        pygame.mixer.music.load(sound_to_play)
        pygame.mixer.music.play()
        logger.debug(f"Playing access denied")
