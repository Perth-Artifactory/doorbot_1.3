"""
List the user groups
"""

import os
import logging
import json
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from slack_bolt.app.async_app import AsyncApp

logging.basicConfig(level=logging.DEBUG)
general_logger = logging.getLogger()

class Config:
    """Config loader"""
    def __init__(self) -> None:
        with open("config.json", "r") as f:
            config = json.load(f)

        self.SLACK_APP_TOKEN = config["SLACK_APP_TOKEN"]
        self.SLACK_BOT_TOKEN = config["SLACK_BOT_TOKEN"]

# Load the config
config = Config()

# Load the slack bolt app framework
app = AsyncApp(token=config.SLACK_BOT_TOKEN)

# def check_auth(b):
#     """Check whether a user/channel is authorised"""
#     if b['user']['id'] == 'U7DD219GF':  # tazard
#         return True
#     return False

# def get_user_name(b):
#     return b['user']['name']

# def get_response_value(b):
#     """Find the value action payload from dropdown"""
#     for block in b['actions']:
#         if 'selected_option' in block:
#             return block['selected_option']['value']
#         else:
#             return block['value']

# @app.event("app_home_opened")
# async def update_home_tab(client, event, logger):
#     try:
#         client.usergroups_users_list()

#         # views.publish is the method that your app uses to push a view to the Home tab
#         await client.views_publish(
#             # the user that opened your app's app home
#             user_id=event["user"],
#             # the view object that appears in the app home
#             view=slack_blocks.home_view
#         )

#     except Exception as e:
#         logger.error(f"Error publishing home tab: {e}")

# @app.action("sendMessage")
# async def handle_send_message(ack, body, logger):
#     await ack()
#     logger.info("app.action 'sendMessage':" + str(body))
#     if check_auth(body):
#         value = get_response_value(body)
#         logger.info(f"SEND MESSAGE = {value}")
#         await post_slack_log(f"Admin '{get_user_name(body)}' played message: {value}")
#         messages = {"key_disabled":"noticeDisabled",
#                     "volunteer_contact":"noticeContact",
#                     "covid":"noticeCOVID",
#                     "notice_you":"noticePresence"}
#         # value = findValue(body,"sendMessage")
#         # say("<@{}> sent the predefined message '{}'".format(body['user']['id'], value))
#         # play(messages[value],OS="WIN")



async def usergroups_list():
    """Main worker coroutine to poll the RFID reader and unlock the door"""
    result = await app.client.usergroups_list()

    general_logger.info("##############")
    general_logger.info("##############")
    general_logger.info("##############")
    general_logger.info("##############")
    general_logger.info("##############")
    general_logger.info("##############")
    # general_logger.info(f"{result}")
    # general_logger.info(f"id = {grp['id']}, name = {grp['name']}")

    usergroups = result['usergroups']

    for grp in usergroups:
        general_logger.info(f"Name = {grp['name']}, Handle = {grp['handle']}, ID = {grp['id']}")

async def main():
    asyncio.ensure_future(usergroups_list())
    handler = AsyncSocketModeHandler(app, config.SLACK_APP_TOKEN)
    await handler.start_async()

if __name__ == "__main__":
    general_logger.info("Starting up")
    import asyncio
    asyncio.run(main())
