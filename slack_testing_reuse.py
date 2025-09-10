#!/usr/bin/env python3
"""
Interactive Slack Testing Script - Uses REAL handlers from app.py

This script patches Python's import system to mock hardware dependencies,
then imports and uses the actual Slack handlers from app.py.

NO CHANGES TO APP.PY REQUIRED!

Usage: python slack_testing_reuse.py
"""

import sys
import os
import asyncio
import logging
import time
from unittest.mock import Mock, AsyncMock, MagicMock

# Setup logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ===== STEP 1: PATCH IMPORTS BEFORE IMPORTING APP =====

logger.info("🔧 Setting up mocks for hardware interfaces...")

# Mock all the hardware modules BEFORE importing app.py
class MockPigpio:
    def pi(self):
        logger.info("🔌 Mock pigpio.pi() called")
        return MockPi()

class MockPi:
    def __init__(self):
        self.connected = True
        
    def stop(self):
        logger.info("🔌 Mock Pi.stop() called")

class MockDoorbotHatGpio:
    def __init__(self, pi):
        logger.info("🔌 Mock DoorbotHatGpio initialized")
        self.relay_state = {}
        
    def set_relay(self, channel, state):
        self.relay_state[channel] = state
        state_str = "ON" if state else "OFF"
        logger.info(f"🔌 Mock GPIO: Relay {channel} set to {state_str}")
        
    def read_switches(self):
        logger.info("🔌 Mock GPIO: Reading switches")
        return {0: False, 1: False}  # Mock switch states

class MockKeyReader:
    def __init__(self, pi):
        logger.info("🏷️ Mock KeyReader initialized")
        
    def start_reading(self):
        logger.info("🏷️ Mock KeyReader: Start reading")
        
    def stop_reading(self):
        logger.info("🏷️ Mock KeyReader: Stop reading")

class MockBlinkstickInterface:
    def __init__(self):
        logger.info("💡 Mock BlinkstickInterface initialized")
        self.color = "blue"
        
    def set_colour_name(self, color):
        self.color = color
        logger.info(f"💡 Mock Blinkstick: Color set to {color}")
        
    def set_white(self):
        self.set_colour_name("white")

class MockTidyAuthClient:
    def __init__(self, base_url, token):
        logger.info(f"🔐 Mock TidyAuthClient initialized (url: {base_url})")

class MockUserManager:
    def __init__(self, api_client, cache_path):
        logger.info(f"👥 Mock UserManager initialized (cache: {cache_path})")
        
    async def download_keys(self):
        logger.info("👥 Mock UserManager: Downloading keys...")
        await asyncio.sleep(1)  # Simulate API delay
        logger.info("👥 Mock UserManager: Keys downloaded successfully!")
        return True
        
    def key_count(self):
        return 42

class MockSoundDownloader:
    def __init__(self, users_with_custom_sounds, download_directory):
        logger.info(f"🔊 Mock SoundDownloader initialized")
        
    def download_next_sound(self):
        return False  # No more sounds to download

class MockSoundPlayer:
    def __init__(self, sound_dir, custom_sound_dir):
        logger.info(f"🔊 Mock SoundPlayer initialized")
        
    def play_sound(self, sound_name):
        logger.info(f"🔊 Mock SoundPlayer: Playing sound '{sound_name}'")

class MockMonotonicWaiter:
    def __init__(self, name):
        self.name = name
        self._duration = 0
        logger.info(f"⏰ Mock MonotonicWaiter '{name}' initialized")
        
    def set_wait_time(self, duration_s):
        self._duration = duration_s
        logger.info(f"⏰ Mock {self.name}: Wait time set to {duration_s}s")
        
    async def wait(self):
        if self._duration > 0:
            logger.info(f"⏰ Mock {self.name}: Timer triggered ({self._duration}s)")
            self._duration = 0
            return True
        await asyncio.sleep(0.1)
        return False

class MockTextToSpeech:
    def non_blocking_speak(self, text):
        logger.info(f"🗣️ Mock TTS: Speaking '{text}'")

# Create a mock text_to_speech module
mock_tts_module = Mock()
mock_tts_module.non_blocking_speak = MockTextToSpeech().non_blocking_speak

# Inject mocks into sys.modules BEFORE importing
sys.modules['pigpio'] = MockPigpio()
sys.modules['doorbot.interfaces.doorbot_hat_gpio'] = Mock(DoorbotHatGpio=MockDoorbotHatGpio)
sys.modules['doorbot.interfaces.wiegand_key_reader'] = Mock(KeyReader=MockKeyReader)
sys.modules['doorbot.interfaces.blinkstick_interface'] = Mock(BlinkstickInterface=MockBlinkstickInterface)
sys.modules['doorbot.interfaces.tidyauth_client'] = Mock(TidyAuthClient=MockTidyAuthClient)
sys.modules['doorbot.interfaces.user_manager'] = Mock(UserManager=MockUserManager)
sys.modules['doorbot.interfaces.sound_downloader'] = Mock(SoundDownloader=MockSoundDownloader)
sys.modules['doorbot.interfaces.sound_player'] = Mock(SoundPlayer=MockSoundPlayer)
sys.modules['doorbot.interfaces.monotonic_waiter'] = Mock(MonotonicWaiter=MockMonotonicWaiter)
sys.modules['doorbot.interfaces.text_to_speech'] = mock_tts_module

logger.info("✅ All hardware interfaces mocked successfully!")

# ===== STEP 2: NOW IMPORT APP.PY - IT WILL USE OUR MOCKS =====

logger.info("📦 Importing doorbot.app with mocked dependencies...")

# Add current directory to path so we can import doorbot
sys.path.insert(0, '/home/tazard/doorbot_1.3')

try:
    from doorbot import app
    logger.info("✅ Successfully imported doorbot.app!")
except Exception as e:
    logger.error(f"❌ Failed to import doorbot.app: {e}")
    raise

# ===== STEP 3: CHECK WHAT APP ACTUALLY CREATED =====

logger.info("🔍 Checking what app.py actually created...")
logger.info(f"app.pigpio_pi type: {type(app.pigpio_pi)}")
logger.info(f"app.hat_gpio type: {type(app.hat_gpio)}")
logger.info(f"app.blink type: {type(app.blink)}")

# Let's see if our mocks worked or if we need to replace the instances
if hasattr(app.hat_gpio, 'set_relay'):
    logger.info("✅ hat_gpio has set_relay method - our mock worked!")
else:
    logger.warning("⚠️ hat_gpio missing set_relay - need to replace instance")

# Test calling a method
try:
    app.blink.set_colour_name('test')
    logger.info("✅ blink.set_colour_name worked - our mock is good!")
except Exception as e:
    logger.warning(f"⚠️ blink method failed: {e}")

logger.info("✅ App instances checked - no manual replacement needed!")

# Override some functions to avoid real side effects
original_post_slack_door = app.post_slack_door
original_post_slack_log = app.post_slack_log

async def mock_post_slack_door(message):
    logger.info(f"📤 Mock Slack Door: {message}")

async def mock_post_slack_log(message):
    logger.info(f"📤 Mock Slack Log: {message}")

app.post_slack_door = mock_post_slack_door
app.post_slack_log = mock_post_slack_log

logger.info("✅ App module patched with mocks!")

# ===== STEP 4: RUN THE REAL APP WITH MOCKED DEPENDENCIES =====

async def run_testing_app():
    """Run the real Slack app with mocked hardware"""
    logger.info("🚀 Starting Doorbot with REAL handlers and MOCK hardware!")
    
    try:
        # Send startup message using real Slack client
        await app.app.client.chat_postMessage(
            channel=app.config.channel,
            text="🧪 Doorbot Testing Mode - Using REAL handlers with MOCK hardware!"
        )
        logger.info("📤 Startup message sent!")
    except Exception as e:
        logger.warning(f"⚠️ Could not send startup message: {e}")
    
    # Start the socket mode handler (this uses the real handlers!)
    from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
    handler = AsyncSocketModeHandler(app.app, app.config.SLACK_APP_TOKEN)
    
    logger.info("🔗 Starting Socket Mode connection...")
    logger.info("🎯 Now you can test buttons in Slack - they use the REAL handlers!")
    logger.info("💡 All hardware actions will be logged but not executed")
    
    await handler.start_async()

if __name__ == "__main__":
    try:
        asyncio.run(run_testing_app())
    except KeyboardInterrupt:
        logger.info("🛑 Testing stopped by user")
    except Exception as e:
        logger.error(f"💥 Error: {e}")
        raise
