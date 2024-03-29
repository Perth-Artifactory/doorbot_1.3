"""
Play sounds for key access
"""

import os
import fnmatch
import logging
import time
import vlc

logger = logging.getLogger(__name__)

class SoundPlayer:
    def __init__(self, sound_dir="", custom_sound_dir=""):
        self.sound_dir = sound_dir
        self.custom_sound_dir = custom_sound_dir
        self.player = None

    def play_access_granted_or_custom(self, user):
        # Fallback option if no custom sound is simply "access granted"
        sound_to_play = os.path.join(self.sound_dir, "granted.mp3")

        if user is None:
            user = {}
        username = user["name"] if "name" in user else "unknown"

        # See if user has custom sound and it has been downloaded
        if "sound" in user:
            sound_hash = user["sound"]
            file_path = self._find_sound_by_hash(sound_hash)
            if file_path:
                sound_to_play = file_path
            else:
                logger.warn(f"Could not find custom sound for '{username}': '{sound_hash}', falling back to default")

        logger.debug(f"Playing access granted for '{username}': {sound_to_play}")
        self.play_sound(sound_to_play)        

    def play_denied(self):
        logger.debug(f"Playing access denied")
        sound_to_play = os.path.join(self.sound_dir, "denied.mp3")
        self.play_sound(sound_to_play)        

    def _find_sound_by_hash(self, sound_hash):
        if os.path.exists(self.custom_sound_dir):
            for file_name in os.listdir(self.custom_sound_dir):
                if fnmatch.fnmatch(file_name, f"*_{sound_hash}.mp3"):
                    return os.path.join(self.custom_sound_dir, file_name)
        return None

    def is_playing(self):
        return self.player is not None and self.player.is_playing()

    def wait_until_done(self):
        if self.player is not None:
            while True:
                # Wait before so we give libvlc a chance to start. If you poll too quickly, 
                # it won't yet be playing.
                time.sleep(1)
                if not self.is_playing():
                    time.sleep(1)
                    break

    def play_sound(self, path):
        if self.player is not None:
            # Its important to always stop because is_playing isn't necessarily up to date
            # and playing multiple media files are once breaks libvlc.
            self.player.stop()
        if os.path.exists(path):
            logger.debug(f"Play {path}")
            self.player = vlc.MediaPlayer(path)
            self.player.play()
        else:
            logger.error(f"Sound does not exist: '{path}'")


