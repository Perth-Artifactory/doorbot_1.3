async def relock_door_loop(app):
    done = await app.timer_relock.wait()
    if done:
        app.gpio.set_relay(app.config.relay_channel, False)
        app.blinkstick.set_colour_name("white")


async def blinkstick_clear_loop(app):
    done = await app.timer_blinkstick_white.wait()
    if done:
        app.blinkstick.set_colour_name("white")


async def slack_log_loop(app):
    if app.slack_log_queue:
        msg = app.slack_log_queue.pop(0)
        await app.slack.chat_postMessage(channel=app.config.channel_logs, text=msg)
    await asyncio.sleep(0.1)


async def tag_reader_loop(app):
    await app.process_tags_once()
    await asyncio.sleep(0.1)