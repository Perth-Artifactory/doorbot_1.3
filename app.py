from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from slack_bolt.app.async_app import AsyncApp
import os
import logging
import json

import slack_blocks
import doorbot_hat_gpio
import weigand_rfid

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

# Load the config
config = Config()

# Load the Doorbot hat GPIO
hat_gpio = doorbot_hat_gpio.DoorbotHatGpio()

# Flag to stop async unlock function running in parallel
door_unlocked = False

# Create RFID reader class
rfid_reader = weigand_rfid.WeigandRfid()

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
    await app.client.chat_postMessage(
        channel=config.channel,
        text="Doorbot 1.3 Slack App Starting",
    )

    while True:
        # await app.client.chat_postMessage(
        #     channel=config.channel,
        #     text="Hi there!",
        # )

        tag = rfid_reader.read()
        if tag != 0:
            await app.client.chat_postMessage(
                channel=config.channel,
                text=f"Just read a tag: {tag}",
            )
            await app.client.chat_postMessage(
                channel=config.channel,
                text=f"Unlocking!",
            )
            await gpio_unlock(5.0)

        await asyncio.sleep(0.1)


async def main():
    asyncio.ensure_future(read_tags())
    handler = AsyncSocketModeHandler(app, config.SLACK_APP_TOKEN)
    await handler.start_async()

if __name__ == "__main__":
    general_logger.info("Starting up")
    import asyncio
    asyncio.run(main())
