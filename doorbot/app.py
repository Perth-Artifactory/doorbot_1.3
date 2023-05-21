"""
Doorbot_1.3

RFID and NFC based access control system for the Perth Artifactory.
Interfaces with Slack and other services for administration and logging.
"""

import math
import logging
import json
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from slack_bolt.app.async_app import AsyncApp
import asyncio
import pigpio

from doorbot.interfaces import slack_blocks
from doorbot.interfaces.doorbot_hat_gpio import DoorbotHatGpio
from doorbot.interfaces.wiegand_key_reader import KeyReader
from doorbot.interfaces.blinkstick_interface import BlinkstickInterface
from doorbot.interfaces.tidyauth_client import TidyAuthClient
from doorbot.interfaces.user_manager import UserManager
from doorbot.interfaces.sound_downloader import SoundDownloader
from doorbot.interfaces.sound_player import SoundPlayer
from doorbot.interfaces import text_to_speech

logging.basicConfig(level=logging.DEBUG)
general_logger = logging.getLogger("app")

# ======= Config =======

class Config:
    """Config loader"""

    def __init__(self) -> None:
        with open("config.json", "r") as f:
            config = json.load(f)

        self.mock_raspberry_pi = config["mock_raspberry_pi"]
        self.SLACK_APP_TOKEN = config["SLACK_APP_TOKEN"]
        self.SLACK_BOT_TOKEN = config["SLACK_BOT_TOKEN"]
        self.channel = config["slack_channel"]
        self.admin_usergroup_handle = config["admin_usergroup_handle"]
        self.relay_channel = config["relay_channel"]
        self.tidyauth_url = config["tidyauth"]["url"]
        self.tidyauth_token = config["tidyauth"]["token"]
        self.tidyauth_cache_file = config["tidyauth"]["cache_file"]
        self.tidyauth_update_interval_seconds = config["tidyauth"]["update_interval_seconds"]
        self.sounds_dir = config["sounds_dir"]
        self.custom_sounds_dir = config["custom_sounds_dir"]

        self.admin_users = []


# Load the config
config = Config()


# ======= Setup =======

# App should only create this once
pigpio_pi = pigpio.pi()

# Load the Doorbot hat GPIO
hat_gpio = DoorbotHatGpio(pigpio_pi)

# Create RFID reader class
key_reader = KeyReader(pigpio_pi)

# Blinkstick - more LEDs!
blink = BlinkstickInterface()

# Keep track of concurrent door unlocks with a countdown
global_lock_countdown_seconds = 0

# TidyAuth API Client
tidyauth_client = TidyAuthClient(base_url=config.tidyauth_url, token=config.tidyauth_token)

# User manager, using tidyauth API
user_manager = UserManager(api_client=tidyauth_client, cache_path=config.tidyauth_cache_file)

# Sound player
sound_player = SoundPlayer(sound_dir=config.sounds_dir, custom_sound_dir=config.custom_sounds_dir)

# Load the slack bolt app framework
app = AsyncApp(token=config.SLACK_BOT_TOKEN)


# ======= Door Unlocking Methods =======

def gpio_unlock(time_s: float):
    hat_gpio.set_relay(config.relay_channel, True)
    global global_lock_countdown_seconds
    if time_s > global_lock_countdown_seconds:
        # Start or extend unlock time
        global_lock_countdown_seconds = time_s
        general_logger.info(f"gpio_unlock - Unlocked door and set countdown to {global_lock_countdown_seconds} s")
    else:
        general_logger.info(f"gpio_unlock - Door already unlocked for another {global_lock_countdown_seconds} s (requested: {time_s=} s)")



def gpio_lock():
    general_logger.info(f"gpio_lock - Locking door")
    hat_gpio.set_relay(config.relay_channel, False)


# ======= Slack Helper Methods =======

def check_auth(b):
    """Check whether a user/channel is authorised to control doorbot via slack"""
    try:
        if b['user']['id'] in config.admin_users:
            return True
    except KeyError as e:
        general_logger.error(f'check_auth exception: {e}')
        pass
    return False


def get_user_name(b):
    try:
        return b['user']['name']
    except KeyError as e:
        general_logger.error(f'get_user_name exception: {e}')
        return "Unknown"


def get_response_text(b):
    """Find the text action payload from dropdown"""
    for block in b['actions']:
        if 'selected_option' in block:
            return block['selected_option']['text']['text']
        else:
            return block['text']['text']


def get_response_value(b):
    """Find the value action payload from dropdown"""
    for block in b['actions']:
        if 'selected_option' in block:
            return block['selected_option']['value']
        else:
            return block['value']


async def post_slack_log(message):
    await app.client.chat_postMessage(
        channel=config.channel,
        text=message,
    )


async def update_admin_users(client):
    # Get list of usergroups
    # Call the usergroups.list method to retrieve information about all usergroups in your workspace
    response = await client.usergroups_list(include_users=False)

    # Iterate through the list of usergroups and find the one with the specified name
    usergroup_id = None
    for group in response["usergroups"]:
        if group["handle"] == config.admin_usergroup_handle:
            usergroup_id = group["id"]
            break

    if usergroup_id is None:
        raise Exception(
            f"Could not find usergroup '{config.admin_usergroup_name}'")

    # Update authorised users
    response = await client.usergroups_users_list(usergroup=usergroup_id)
    config.admin_users = response['users']
    general_logger.debug(f"update_admin_users - Admin users are: {', '.join(config.admin_users)}")


# ======= Slack Handlers =======

@app.event("app_home_opened")
async def update_home_tab(client, event, logger):
    try:
        # Make sure we have a fresh list of admin users
        await update_admin_users(client)

        if event["user"] in config.admin_users:
            # User is allowed to control doorbot via slack
            # views.publish is the method that your app uses to push a view to the Home tab
            await client.views_publish(
                # the user that opened your app's app home
                user_id=event["user"],
                # the view object that appears in the app home
                view=slack_blocks.home_view
            )
        else:
            # User is not allowed to control doorbot via slack
            await client.views_publish(
                user_id=event["user"],
                view=slack_blocks.home_view_denied
            )
    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")


@app.action("sendMessage")
async def handle_send_message(ack, body, logger):
    await ack()
    logger.info("app.action 'sendMessage':" + str(body))
    if check_auth(body):
        text = get_response_text(body)
        logger.info(f"SEND MESSAGE = {text}")
        await post_slack_log(f"Admin '{get_user_name(body)}' played predefine TTS: {text}")
        text_to_speech.non_blocking_speak(text)
    else:
        logger.error(f"User not authorised for admin access. Allowed = '{config.admin_users}'.")


@app.action("ttsMessage")
async def handle_tts_message(ack, body, logger):
    await ack()
    logger.info("app.action 'ttsMessage':" + str(body))
    if check_auth(body):
        text = get_response_value(body)
        await post_slack_log(f"Admin '{get_user_name(body)}' played TTS: {text}")
        logger.info(f"TTS MESSAGE = {text}")
        text_to_speech.non_blocking_speak(text)
    else:
        logger.error(f"User not authorised for admin access. Allowed = '{config.admin_users}'.")




@app.action("unlock")
async def handle_unlock(ack, body, logger):
    await ack()
    logger.info("app.action 'unlock':" + str(body))
    if check_auth(body):
        value = get_response_value(body)
        try:
            time_s = float(value)
        except ValueError:
            logger.error("Invalid wait time: " + value)
        else:
            # Valid time
            msg = f"Admin '{get_user_name(body)}' manually opened door for {time_s:.1f} seconds"
            await post_slack_log(msg)
            logger.info(msg)
            gpio_unlock(time_s)
    else:
        logger.error(f"User not authorised for admin access. Allowed = '{config.admin_users}'.")


# ======= Background Tasks =======

async def read_tags():
    """Main worker coroutine to poll the RFID reader and unlock the door"""
    await app.client.chat_postMessage(
        channel=config.channel,
        text="Doorbot 1.3 Slack App Starting",
    )

    while True:
        if len(key_reader.pending_keys) > 0:
            tag = key_reader.pending_keys.pop(0)

            # Pad with zeros to 10 digits like API expects
            tag = f"{tag:0>10}"

            if user_manager.is_key_authorised(tag):
                # Access granted
                user = user_manager.get_user_details(tag)
                name = user['name']
                level = user['door']
                groups = user['groups']

                unlock_time = 5.0  # Default unlock time in seconds
                if 'delayed' in groups:
                    unlock_time = 30.0
                gpio_unlock(unlock_time)

                sound_player.play_access_granted_or_custom(user)
                general_logger.info(f"read_tags - Access granted: tag = '{tag}', user = {str(user)}")
                await app.client.chat_postMessage(
                    channel=config.channel,
                    **slack_blocks.door_access(
                        name=name, tag=tag, status=':white_check_mark: Door unlocked', level=level),
                )

            else:
                # Access denied
                sound_player.play_denied()
                general_logger.info(f"read_tags - Access denied: tag = '{tag}'")
                await app.client.chat_postMessage(
                    channel=config.channel,
                    **slack_blocks.door_access(
                        name="Unknown", tag=tag, status=':x: Access denied', level="Unknown")
                )

        if len(key_reader.pending_errors) > 0:
            msg = key_reader.pending_errors.pop(0)
            general_logger.info(f"read_tags - Bad read: {msg}")
            await app.client.chat_postMessage(
                channel=config.channel,
                text=f"Bad read: {msg}",
            )

        await asyncio.sleep(0.1)

async def relock_door():
    """Worker coroutine to countdown to relocking door"""
    while True:
        global global_lock_countdown_seconds
        if global_lock_countdown_seconds > 0:
            general_logger.info(f"relock_door - start countdown: {global_lock_countdown_seconds=}")
            while True:
                await asyncio.sleep(1)
                def is_close_to_zero(value):
                    return math.isclose(value, 0.0, abs_tol=1e-9)
                if is_close_to_zero(global_lock_countdown_seconds) or global_lock_countdown_seconds <= 0:
                    gpio_lock()
                    break
                else:
                    global_lock_countdown_seconds -= 1
                general_logger.info(f"relock_door - counting down: {global_lock_countdown_seconds=}")

        await asyncio.sleep(0.1)

async def update_keys():
    """Worker coroutine to refresh keys from the API"""
    while True:
        # Update on startup
        general_logger.debug("update_keys - Update data from tidyauth")
        changed = await user_manager.download_keys()
        if changed:
            general_logger.debug("update_keys - Keys changed")
            await app.client.chat_postMessage(
                channel=config.channel,
                text="Keys updated (change received from TidyAPI)"
            )
            await download_sounds()
        await asyncio.sleep(config.tidyauth_update_interval_seconds)


async def download_sounds():
    """Worker coroutine download sounds"""
    users = user_manager.get_users_with_custom_sounds()
    general_logger.debug(f"download_sounds - Check if sounds need downloading for {len(users)} users")
    sound_downloader = SoundDownloader(
        users_with_custom_sounds=users, 
        download_directory=config.custom_sounds_dir)

    # Download the sound files
    while sound_downloader.download_next_sound():
        # Allow other things to run between sound file downloads
        await asyncio.sleep(0.5)


# ======= Main =======

async def run():
    general_logger.info("run - Starting up")
    asyncio.ensure_future(read_tags())
    asyncio.ensure_future(relock_door())
    asyncio.ensure_future(update_keys())
    asyncio.ensure_future(download_sounds())
    handler = AsyncSocketModeHandler(app, config.SLACK_APP_TOKEN)
    await handler.start_async()


def main():
    asyncio.run(run())


if __name__ == "__main__":
    main()
