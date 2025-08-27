#!/usr/bin/env python3
"""
Slack Testing Script for Doorbot

This script runs a simplified version of the Doorbot Slack app with all hardware
interfaces mocked, allowing you to test the Slack home view and button interactions
without needing the actual Raspberry Pi hardware.

Usage:
    python slack_testing_app.py

Set these environment variables or update the config below:
    SLACK_BOT_TOKEN="xoxb-your-bot-token"
    SLACK_APP_TOKEN="xapp-your-app-token"
"""

import asyncio
import time
import logging
import os
from unittest.mock import Mock, MagicMock
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from slack_bolt.app.async_app import AsyncApp
from slack_sdk.errors import SlackApiError

# Import our interfaces
from doorbot.interfaces import slack_blocks

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ===== CONFIGURATION =====
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN", "")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN", "")
ADMIN_USER_ID = os.getenv("ADMIN_USER_ID", "")  # User ID to check (user running test)

# ===== MOCK INTERFACES =====

class MockConfig:
    """Mock configuration that doesn't require a config file"""
    def __init__(self):
        self.admin_usergroup_id = None  # Will use hardcoded admin user for testing
        self.channel = "#doorbot-slack-test"
        self.channel_logs = "#doorbot-test-2"

class MockGPIO:
    """Mock GPIO interface"""
    def __init__(self):
        self.relay_state = False
        logger.info("🔌 Mock GPIO initialized")
    
    def set_relay(self, channel, state):
        self.relay_state = state
        state_str = "ON" if state else "OFF"
        logger.info(f"🔌 Mock GPIO: Relay {channel} set to {state_str}")
    
    def get_relay(self, channel):
        return self.relay_state

class MockBlinkstick:
    """Mock Blinkstick interface"""
    def __init__(self):
        self.color = "white"
        logger.info("💡 Mock Blinkstick initialized")
    
    def set_colour_name(self, color):
        self.color = color
        logger.info(f"💡 Mock Blinkstick: Color set to {color}")
    
    def set_white(self):
        self.set_colour_name("white")

class MockUserManager:
    """Mock user manager"""
    def __init__(self):
        logger.info("👥 Mock User Manager initialized")
    
    async def download_keys(self):
        logger.info("👥 Mock: Downloading keys...")
        await asyncio.sleep(1)  # Simulate network delay
        logger.info("👥 Mock: Keys downloaded successfully")
        return True
    
    def key_count(self):
        return 42

class MockSoundPlayer:
    """Mock sound player"""
    def __init__(self):
        logger.info("🔊 Mock Sound Player initialized")
    
    def play_sound(self, sound_name):
        logger.info(f"🔊 Mock: Playing sound '{sound_name}'")

class MockTTS:
    """Mock text-to-speech"""
    def __init__(self):
        logger.info("🗣️ Mock TTS initialized")
    
    def non_blocking_speak(self, text):
        logger.info(f"🗣️ Mock TTS: Speaking '{text}'")

# ===== SETUP MOCKS =====
config = MockConfig()
mock_gpio = MockGPIO()
blink = MockBlinkstick()
user_manager = MockUserManager()
sound_player = MockSoundPlayer()
text_to_speech = MockTTS()

# Record start time for uptime
start_time = time.monotonic()

# Create the Slack app
app = AsyncApp(token=SLACK_BOT_TOKEN)

# ===== COPY THE LOADING BUTTON FUNCTIONS =====

def patch_home_blocks(blocks, block_id, action_id, appended_text=None, replacement_text=None, style=None):
    """Patch blocks for home view buttons with loading indicators or updates"""
    import copy
    
    new_blocks = copy.deepcopy(blocks)
    
    for block in new_blocks:
        if block.get("block_id") == block_id:
            # Handle different block types
            if "elements" in block:
                for element in block["elements"]:
                    if element.get("action_id") == action_id:
                        if replacement_text:
                            element["text"]["text"] = replacement_text
                        elif appended_text:
                            # Remove any existing loading indicator first
                            current_text = element["text"]["text"]
                            if " :spinthinking:" in current_text:
                                current_text = current_text.replace(" :spinthinking:", "")
                            element["text"]["text"] = current_text + appended_text
                        
                        if style:
                            element["style"] = style
            elif "accessory" in block and block["accessory"].get("action_id") == action_id:
                # Handle section blocks with accessory buttons
                if replacement_text:
                    block["accessory"]["text"]["text"] = replacement_text
                elif appended_text:
                    current_text = block["accessory"]["text"]["text"]
                    if " :spinthinking:" in current_text:
                        current_text = current_text.replace(" :spinthinking:", "")
                    block["accessory"]["text"]["text"] = current_text + appended_text
                
                if style:
                    block["accessory"]["style"] = style
    
    return new_blocks

async def set_loading_icon_on_button(body, client, logger):
    """Set the spinning icon on the button for home view"""
    try:
        # Get the action that was clicked
        action = body["actions"][0]
        
        # Patch the blocks with loading indicator
        new_blocks = patch_home_blocks(
            blocks=body["view"]["blocks"],
            block_id=action.get("block_id"),
            action_id=action["action_id"],
            appended_text=" :spinthinking:"
        )
        
        # Update the home view
        await client.views_publish(
            user_id=body["user"]["id"],
            view={
                "type": "home",
                "blocks": new_blocks,
            }
        )
        logger.info("Loading indicator added to button")
    except SlackApiError as e:
        logger.error(f"Failed to update home view: {e.response['error']}")

async def reset_button_after_action(body, client, logger, success_text=None, delay_seconds=3):
    """Reset button to original state after an action completes"""
    try:
        # Get the action that was clicked
        action = body["actions"][0]
        
        if success_text:
            # First show success message
            new_blocks = patch_home_blocks(
                blocks=body["view"]["blocks"],
                block_id=action.get("block_id"),
                action_id=action["action_id"],
                replacement_text=success_text,
                style="primary"
            )
            
            await client.views_publish(
                user_id=body["user"]["id"],
                view={
                    "type": "home",
                    "blocks": new_blocks,
                }
            )
            
            # Wait a bit before resetting
            await asyncio.sleep(delay_seconds)
        
        # Reset to original home view
        await client.views_publish(
            user_id=body["user"]["id"],
            view=slack_blocks.home_view
        )
        logger.info("Button reset to original state")
    except Exception as e:
        logger.error(f"Unexpected error resetting button: {e}")

# ===== HELPER FUNCTIONS =====

def get_user_name(body):
    """Get user name from Slack body"""
    return body.get("user", {}).get("name", "Unknown User")

def get_response_value(body):
    """Get response value from Slack body"""
    return body.get("actions", [{}])[0].get("value", "")

def mock_gpio_unlock(time_s):
    """Mock door unlock"""
    logger.info(f"🚪 Mock: Unlocking door for {time_s} seconds")
    mock_gpio.set_relay(1, True)  # Open door
    blink.set_colour_name('green')
    # In real app, this would use a timer to relock
    
def mock_gpio_lock():
    """Mock door lock"""
    logger.info("🚪 Mock: Locking door")
    mock_gpio.set_relay(1, False)  # Close door
    blink.set_white()

async def post_slack_message(channel, message):
    """Post message to Slack channel"""
    try:
        await app.client.chat_postMessage(
            channel=channel,
            text=message
        )
        logger.info(f"📤 Posted to {channel}: {message}")
    except SlackApiError as e:
        logger.error(f"Failed to post message: {e}")

# ===== AUTHORIZATION =====

async def check_user_authed(user_id):
    """Check if user is authorized - for testing, only allow the admin user"""
    is_authed = user_id == ADMIN_USER_ID
    logger.info(f"🔐 Auth check for {user_id}: {'✅ Authorized' if is_authed else '❌ Not authorized'}")
    return is_authed

async def authed_action(body):
    """Check if action is from authorized user"""
    try:
        return await check_user_authed(body.get('user', {}).get('id'))
    except Exception as e:
        logger.error(f'Auth check failed: {e}')
    return False

# ===== SLACK HANDLERS =====

@app.event("app_home_opened")
async def update_home_tab(client, event, logger):
    """Update home tab when opened"""
    try:
        user_id = event["user"]
        is_authed = await check_user_authed(user_id)
        
        if is_authed:
            view = slack_blocks.home_view
            logger.info(f"🏠 Publishing home view for authorized user {user_id}")
        else:
            view = slack_blocks.home_view_denied
            logger.info(f"🚫 Publishing denied view for unauthorized user {user_id}")
        
        await client.views_publish(
            user_id=user_id,
            view=view
        )
    except Exception as e:
        logger.error(f"Error updating home tab: {e}")

@app.action("unlock", matchers=[authed_action])
async def handle_unlock(ack, body, logger, client):
    """Handle unlock button"""
    try:
        await ack()
        logger.info("🚪 Unlock button clicked")

        # Set loading indicator
        await set_loading_icon_on_button(body=body, client=client, logger=logger)

        # Get unlock time
        value = get_response_value(body)
        try:
            time_s = float(value)
        except ValueError:
            logger.error(f"Invalid unlock time: {value}")
            await reset_button_after_action(body=body, client=client, logger=logger)
            return

        # Mock unlock
        user_name = get_user_name(body)
        msg = f"🚪 {user_name} unlocked door for {time_s:.0f} seconds (MOCK)"
        mock_gpio_unlock(time_s)
        
        # Post to channel
        await post_slack_message(config.channel, msg)
        
        # Mock TTS
        text_to_speech.non_blocking_speak(f'Door has been opened for {time_s:.0f} seconds')
        
        # Reset button with success
        await reset_button_after_action(
            body=body, 
            client=client, 
            logger=logger, 
            success_text=f"Unlocked {time_s:.0f}s! ✓"
        )
        
    except Exception as e:
        logger.error(f"Error in unlock handler: {e}")
        await reset_button_after_action(body=body, client=client, logger=logger)

@app.action("updateKeys", matchers=[authed_action])
async def handle_update_keys(ack, body, logger, client):
    """Handle update keys button"""
    try:
        await ack()
        logger.info("🔑 Update keys button clicked")

        # Set loading indicator
        await set_loading_icon_on_button(body=body, client=client, logger=logger)

        # Mock key update
        user_name = get_user_name(body)
        msg = f"🔑 {user_name} requested keys update (MOCK)"
        
        # Simulate key update process
        changed = await user_manager.download_keys()
        key_count = user_manager.key_count()
        
        # Post to channel
        await post_slack_message(config.channel, f"{msg} - {key_count} keys loaded")
        
        # Set blinkstick color to indicate update
        blink.set_colour_name('aqua')
        
        # Reset button with success
        await reset_button_after_action(
            body=body, 
            client=client, 
            logger=logger, 
            success_text=f"Updated {key_count} keys! ✓"
        )
        
    except Exception as e:
        logger.error(f"Error in update keys handler: {e}")
        await reset_button_after_action(body=body, client=client, logger=logger)

@app.action("livelinessCheck", matchers=[authed_action])
async def handle_liveliness_check(ack, body, logger, client):
    """Handle liveliness check button"""
    try:
        await ack()
        logger.info("💓 Liveliness check button clicked")

        # Set loading indicator
        await set_loading_icon_on_button(body=body, client=client, logger=logger)

        # Calculate uptime
        uptime_seconds = time.monotonic() - start_time
        days, remainder = divmod(uptime_seconds, 3600*24)
        hours, _ = divmod(remainder, 3600)

        # Mock liveliness check
        user_name = get_user_name(body)
        msg = f"💓 {user_name} liveliness check - uptime {int(days)}d {int(hours)}h (MOCK)"
        
        # Post to channel
        await post_slack_message(config.channel, msg)
        
        # Flash LED
        blink.set_colour_name('gray')
        await asyncio.sleep(0.5)
        blink.set_white()
        
        # Reset button with success
        await reset_button_after_action(
            body=body, 
            client=client, 
            logger=logger, 
            success_text=f"Alive! {int(days)}d {int(hours)}h ✓"
        )
        
    except Exception as e:
        logger.error(f"Error in liveliness check handler: {e}")
        await reset_button_after_action(body=body, client=client, logger=logger)

@app.action("sendMessage")
async def handle_send_message(ack, body, logger):
    """Handle send message dropdown"""
    await ack()
    logger.info("📢 Send message selected")
    
    # In real app, this would trigger TTS
    selected = body.get("actions", [{}])[0].get("selected_option", {}).get("value", "")
    text_to_speech.non_blocking_speak(f"Message selected: {selected}")

@app.action("ttsMessage")
async def handle_tts_message(ack, body, logger):
    """Handle TTS message input"""
    await ack()
    logger.info("🗣️ TTS message entered")
    
    # In real app, this would trigger TTS
    text = body.get("actions", [{}])[0].get("value", "")
    if text:
        text_to_speech.non_blocking_speak(text)

@app.action("restartApp", matchers=[authed_action])
async def handle_restart_app(ack, body, logger, client):
    """Handle restart app button"""
    await ack()
    logger.info("🔄 Restart app button clicked")
    
    # Set loading indicator
    await set_loading_icon_on_button(body=body, client=client, logger=logger)
    
    user_name = get_user_name(body)
    msg = f"🔄 {user_name} requested app restart (MOCK - not actually restarting)"
    
    # Post to channel
    await post_slack_message(config.channel, msg)
    
    # Mock restart visual
    blink.set_colour_name('fuchsia')
    await asyncio.sleep(2)
    blink.set_colour_name('navy')
    
    logger.info("🔄 Mock restart complete (real app would exit here)")

@app.action("rebootPi", matchers=[authed_action])
async def handle_reboot_pi(ack, body, logger, client):
    """Handle reboot Pi button"""
    await ack()
    logger.info("🔄 Reboot Pi button clicked")
    
    # Set loading indicator
    await set_loading_icon_on_button(body=body, client=client, logger=logger)
    
    user_name = get_user_name(body)
    msg = f"🔄 {user_name} requested Pi reboot (MOCK - not actually rebooting)"
    
    # Post to channel
    await post_slack_message(config.channel, msg)
    
    # Mock reboot visual
    blink.set_colour_name('purple')
    await asyncio.sleep(2)
    blink.set_colour_name('navy')
    
    logger.info("🔄 Mock reboot complete (real app would reboot here)")

# ===== MAIN =====

async def run():
    """Run the testing app"""
    logger.info("🚀 Starting Doorbot Slack Testing App")
    logger.info(f"🤖 Bot token: {SLACK_BOT_TOKEN[:20]}...")
    logger.info(f"👤 Admin user: {ADMIN_USER_ID}")
    logger.info("📱 All hardware interfaces are mocked")
    
    try:
        # Send startup message
        await post_slack_message(
            config.channel,
            "🧪 Doorbot Testing App Started (All interfaces mocked)"
        )
        
        # Start socket mode handler
        handler = AsyncSocketModeHandler(app, SLACK_APP_TOKEN)
        await handler.start_async()
        
    except Exception as e:
        logger.error(f"Failed to start app: {e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        logger.info("🛑 Testing app stopped by user")
    except Exception as e:
        logger.error(f"💥 Testing app crashed: {e}")
        raise
