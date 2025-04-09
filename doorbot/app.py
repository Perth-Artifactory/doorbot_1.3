import asyncio
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from slack_bolt.app.async_app import AsyncApp
from doorbot.slack_handlers import register_slack_handlers
from doorbot.tools import safe_loop
from doorbot.background_tasks import (
    relock_door_loop,
    blinkstick_clear_loop,
    slack_log_loop,
    tag_reader_loop
)


class DoorbotApp:
    def __init__(
        self,
        config,
        gpio,
        key_reader,
        blinkstick,
        sound_player,
        user_manager,
        tidyauth_client,
        logger,
        slack_client,
        timer_relock,
        timer_blinkstick_white,
        timer_keys_update,
        slack_log_queue,
    ):
        self.config = config
        self.gpio = gpio
        self.key_reader = key_reader
        self.blinkstick = blinkstick
        self.sound_player = sound_player
        self.user_manager = user_manager
        self.tidyauth_client = tidyauth_client
        self.logger = logger
        self.slack = slack_client
        self.timer_relock = timer_relock
        self.timer_blinkstick_white = timer_blinkstick_white
        self.timer_keys_update = timer_keys_update
        self.slack_log_queue = slack_log_queue

        self.app = AsyncApp(token=config.SLACK_BOT_TOKEN)
        self.handler = AsyncSocketModeHandler(self.app, config.SLACK_APP_TOKEN)

        register_slack_handlers(self)

    async def run(self):
        await self.slack.chat_postMessage(
            channel=self.config.channel,
            text="Doorbot App Starting"
        )

        asyncio.create_task(safe_loop(self.logger, lambda: tag_reader_loop(self)))
        asyncio.create_task(safe_loop(self.logger, lambda: relock_door_loop(self)))
        asyncio.create_task(safe_loop(self.logger, lambda: blinkstick_clear_loop(self)))
        asyncio.create_task(safe_loop(self.logger, lambda: slack_log_loop(self)))

        await self.handler.start_async()

    async def process_tags_once(self):
        if len(self.key_reader.pending_keys) == 0:
            return

        tag = self.key_reader.pending_keys.pop(0)
        tag = f"{tag:0>10}"

        if self.user_manager.is_key_authorised(tag):
            user = self.user_manager.get_user_details(tag)
            self.gpio.set_relay(self.config.relay_channel, True)
            self.timer_relock.set_wait_time(duration_s=5.0)
            self.blinkstick.set_colour_name("green")
            self.sound_player.play_access_granted_or_custom(user)
            await self.slack.chat_postMessage(
                channel=self.config.channel,
                text=f"Access granted to {user['name']}"
            )
        else:
            self.blinkstick.set_colour_name("red")
            self.timer_blinkstick_white.set_wait_time(duration_s=5.0)
            self.sound_player.play_denied()
            await self.slack.chat_postMessage(
                channel=self.config.channel,
                text=f"Access denied for tag {tag}"
            )
