import logging
logging.basicConfig(level=logging.DEBUG)

import os
from slack_bolt.app.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler

app = AsyncApp(token=os.environ["SLACK_BOT_TOKEN"])

async def run_offline_task():
    while True:
        channel_id = "#doorbot-slack-test"  # Blake
        await app.client.chat_postMessage(
            channel=channel_id,
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