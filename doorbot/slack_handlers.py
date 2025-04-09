import asyncio

def register_slack_handlers(app_instance):
    app = app_instance.app
    config = app_instance.config
    gpio = app_instance.gpio
    timer_relock = app_instance.timer_relock
    slack = app_instance.slack
    blinkstick = app_instance.blinkstick
    timer_blinkstick_white = app_instance.timer_blinkstick_white
    timer_keys_update = app_instance.timer_keys_update
    sound_player = app_instance.sound_player
    user_manager = app_instance.user_manager
    logger = app_instance.logger

    def get_user_name(b):
        try:
            return b['user']['name']
        except KeyError:
            return "Unknown"

    def get_response_text(b):
        for block in b['actions']:
            if 'selected_option' in block:
                return block['selected_option']['text']['text']
            else:
                return block['text']['text']

    def get_response_value(b):
        for block in b['actions']:
            if 'selected_option' in block:
                return block['selected_option']['value']
            else:
                return block['value']

    @app.action("unlock")
    async def handle_unlock(ack, body, logger):
        await ack()
        logger.debug("unlock action")
        value = get_response_value(body)
        try:
            time_s = float(value)
        except ValueError:
            logger.error("Invalid wait time: " + value)
            return

        gpio.set_relay(config.relay_channel, True)
        timer_relock.set_wait_time(duration_s=time_s)
        await slack.chat_postMessage(
            channel=config.channel,
            text=f"Admin '{get_user_name(body)}' manually opened door for {time_s:.0f} seconds"
        )

    @app.action("ttsMessage")
    async def handle_tts_message(ack, body, logger):
        await ack()
        logger.debug("ttsMessage action")
        text = get_response_value(body)
        from doorbot.interfaces import text_to_speech
        text_to_speech.non_blocking_speak(text)
        await slack.chat_postMessage(
            channel=config.channel,
            text=f"Admin '{get_user_name(body)}' played text-to-speech: {text}"
        )

    @app.action("sendMessage")
    async def handle_send_message(ack, body, logger):
        await ack()
        logger.debug("sendMessage action")
        text = get_response_text(body)
        from doorbot.interfaces import text_to_speech
        text_to_speech.non_blocking_speak(text)
        await slack.chat_postMessage(
            channel=config.channel,
            text=f"Admin '{get_user_name(body)}' played predefined TTS: {text}"
        )

    @app.action("restartApp")
    async def handle_restart_app(ack, body, logger):
        await ack()
        blinkstick.set_colour_name('fuchsia')
        await slack.chat_postMessage(
            channel=config.channel,
            text=f"Admin '{get_user_name(body)}' has asked the doorbot app to restart"
        )
        await asyncio.sleep(1)
        blinkstick.set_colour_name('navy')
        import sys
        sys.exit()

    @app.action("rebootPi")
    async def handle_reboot_pi(ack, body, logger):
        await ack()
        blinkstick.set_colour_name('purple')
        await slack.chat_postMessage(
            channel=config.channel,
            text=f"Admin '{get_user_name(body)}' has asked the Raspberry Pi to reboot"
        )
        await asyncio.sleep(1)
        blinkstick.set_colour_name('navy')
        import os
        os.system('sudo reboot')

    @app.action("livelinessCheck")
    async def handle_liveliness_check(ack, body, logger):
        await ack()
        blinkstick.set_colour_name('gray')
        timer_blinkstick_white.set_wait_time(duration_s=1)
        import time
        uptime_seconds = time.monotonic() - app_instance.start_time
        days, remainder = divmod(uptime_seconds, 3600*24)
        hours, _ = divmod(remainder, 3600)
        await slack.chat_postMessage(
            channel=config.channel,
            text=f"Admin '{get_user_name(body)}' has requested liveliness check (uptime {int(days)}d {int(hours)}h)"
        )

    @app.action("updateKeys")
    async def handle_update_keys(ack, body, logger):
        await ack()
        timer_keys_update.set_wait_time(duration_s=1)
        await slack.chat_postMessage(
            channel=config.channel,
            text=f"Admin '{get_user_name(body)}' has requested keys update"
        )
