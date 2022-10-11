"""
Doorbot_1.3

RFID and NFC based access control system for the Perth Artifactory.
Interfaces with Slack and other services for administration and logging.
"""

import os
import logging
import json
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from slack_bolt.app.async_app import AsyncApp

import slack_blocks
import doorbot_hat_gpio
import weigand_rfid
import blinkstick_interface
import updating_config_loader

logging.basicConfig(level=logging.DEBUG)
general_logger = logging.getLogger()

class Config:
    """Config loader"""
    def __init__(self) -> None:
        with open("config.json", "r") as f:
            config = json.load(f)

        self.SLACK_APP_TOKEN = config["SLACK_APP_TOKEN"]
        self.SLACK_BOT_TOKEN = config["SLACK_BOT_TOKEN"]
        self.mock_raspberry_pi = config["mock_raspberry_pi"]
        self.channel = config["slack_channel"]
        self.relay_channel = config["relay_channel"]
        self.keys_url = config["keys"]["url"]
        self.keys_cache_file = config["keys"]["cache_file"]
        self.level = config["level"]

# Load the config
config = Config()

# Load the Doorbot hat GPIO
hat_gpio = doorbot_hat_gpio.DoorbotHatGpio()

# Blinkstick - more LEDs!
blink = blinkstick_interface.BlinkstickInterface()

# Flag to stop async unlock function running in parallel
door_unlocked = False

# Create RFID reader class
rfid_reader = weigand_rfid.WeigandRfid()

# Object to manage retrieving and caching keys.
# Construction does the first update.
key_store = updating_config_loader.UpdatingConfigLoader(
    local_path=config.keys_cache_file,
    remote_url=config.keys_url,
)

# Load the slack bolt app framework
app = AsyncApp(token=config.SLACK_BOT_TOKEN)

def check_auth(b):
    """Check whether a user/channel is authorised"""
    if b['user']['id'] == 'U7DD219GF':  # tazard
        return True
    return False

def get_user_name(b):
    return b['user']['name']

def get_response_value(b):
    """Find the value action payload from dropdown"""
    for block in b['actions']:
        if 'selected_option' in block:
            return block['selected_option']['value']
        else:
            return block['value']

@app.event("app_home_opened")
async def update_home_tab(client, event, logger):
    try:
        # views.publish is the method that your app uses to push a view to the Home tab
        await client.views_publish(
            # the user that opened your app's app home
            user_id=event["user"],
            # the view object that appears in the app home
            view=slack_blocks.home_view
        )

    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")

@app.action("sendMessage")
async def handle_send_message(ack, body, logger):
    await ack()
    logger.info("app.action 'sendMessage':" + str(body))
    if check_auth(body):
        value = get_response_value(body)
        logger.info(f"SEND MESSAGE = {value}")
        await post_slack_log(f"Admin '{get_user_name(body)}' played message: {value}")
        messages = {"key_disabled":"noticeDisabled",
                    "volunteer_contact":"noticeContact",
                    "covid":"noticeCOVID",
                    "notice_you":"noticePresence"}
        # value = findValue(body,"sendMessage")
        # say("<@{}> sent the predefined message '{}'".format(body['user']['id'], value))
        # play(messages[value],OS="WIN")

@app.action("ttsMessage")
async def handle_tts_message(ack, body, logger):
    await ack()
    logger.info("app.action 'ttsMessage':" + str(body))
    if check_auth(body):
        value = get_response_value(body)
        await post_slack_log(f"Admin '{get_user_name(body)}' played TTS: {value}")
        logger.info(f"TTS MESSAGE = {value}")

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
            await post_slack_log(f"Admin '{get_user_name(body)}' manually opened door for {time_s:.1f} seconds")
            logger.info(f"DOOR UNLOCK = {time_s:.1f} seconds")
            await gpio_unlock(time_s)

async def post_slack_log(message):
    await app.client.chat_postMessage(
        channel=config.channel,
        text=message,
    )


async def gpio_unlock(time_s: float):
    # Use "door_unlocked" like a lock/mutex to ensure this doesn't run in parallel
    global door_unlocked
    if not door_unlocked:
        door_unlocked = True

        hat_gpio.set_relay(config.relay_channel, True)
        general_logger.info(f"DoorbotHatGpio UNLOCKED DOOR")
        await asyncio.sleep(time_s)
        hat_gpio.set_relay(config.relay_channel, False)
        general_logger.info(f"DoorbotHatGpio LOCK DOOR")

        door_unlocked = False


async def read_tags():
    """Main worker coroutine to poll the RFID reader and unlock the door"""
    await app.client.chat_postMessage(
        channel=config.channel,
        text="Doorbot 1.3 Slack App Starting",
    )

    while True:
        tag = rfid_reader.read()
        if tag != 0:
            if tag in key_store.contents:
                key = key_store.contents[tag]
                name = key['name']
                level = key['level']
                await app.client.chat_postMessage(
                    channel=config.channel,
                    text=f"Unlocking door for {name}",
                    blocks=slack_blocks.door_access(name=name, tag=tag, status=':white_check_mark: Door unlocked', level=level)
                )
                # TODO: Play access granted
                await gpio_unlock(5.0)
            else:
                await app.client.chat_postMessage(
                    channel=config.channel,
                    text=f"Denied access to tag {tag}",
                    blocks=slack_blocks.door_access(name="Unknown", tag=tag, status=':x: Access denied', level="Unknown")
                )
                # TODO: Play access denied

        await asyncio.sleep(0.1)

async def update_keys():
    """Worker coroutine to refresh keys from the API"""
    while True:
        await asyncio.sleep(60)
        key_store.update_from_url()

async def main():
    asyncio.ensure_future(read_tags())
    asyncio.ensure_future(update_keys())
    handler = AsyncSocketModeHandler(app, config.SLACK_APP_TOKEN)
    await handler.start_async()

if __name__ == "__main__":
    general_logger.info("Starting up")
    import asyncio
    asyncio.run(main())
