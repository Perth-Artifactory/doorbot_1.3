from readline import get_begidx
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from slack_bolt.app.async_app import AsyncApp
import os
import logging
import slack_blocks
logging.basicConfig(level=logging.DEBUG)

app = AsyncApp(token=os.environ["SLACK_BOT_TOKEN"])

DOORBOT_LOG_CHANNEL = "#doorbot-slack-test"

async def post_slack_log(message):
    await app.client.chat_postMessage(
        channel=DOORBOT_LOG_CHANNEL,
        text=message,
    )


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
        await post_slack_log(f"Admin '{get_user_name(body)}' manually opened door for {value} seconds")
        logger.info(f"DOOR UNLOCK = {value} seconds")

async def run_offline_task():
    while True:
        await app.client.chat_postMessage(
            channel=DOORBOT_LOG_CHANNEL,
            text="Hi there!",
        )
        await asyncio.sleep(60)


async def main():
    asyncio.ensure_future(run_offline_task())
    handler = AsyncSocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    await handler.start_async()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
