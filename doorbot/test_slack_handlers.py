import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from slack_bolt.async_app import AsyncApp
from doorbot.slack_handlers import register_slack_handlers


@pytest.fixture
def mock_app_instance():
    mock = MagicMock()
    mock.app = AsyncApp(token="xoxb-test")
    mock.config.channel = "#test-channel"
    mock.config.relay_channel = 1
    mock.gpio.set_relay = MagicMock()
    mock.timer_relock.set_wait_time = MagicMock()
    mock.timer_blinkstick_white.set_wait_time = MagicMock()
    mock.timer_keys_update.set_wait_time = MagicMock()
    mock.blinkstick.set_colour_name = MagicMock()
    mock.slack.chat_postMessage = AsyncMock()
    mock.logger.debug = MagicMock()
    mock.logger.error = MagicMock()
    mock.start_time = 0
    return mock


@pytest.mark.asyncio
async def test_unlock_handler(mock_app_instance):
    register_slack_handlers(mock_app_instance)

    ack = AsyncMock()
    logger = MagicMock()
    body = {
        'user': {'name': 'test-user'},
        'actions': [{'value': '5'}],
    }

    handler = mock_app_instance.app._listener_runner.listener_matcher_groups['action']["unlock"]
    await handler[0].func(ack=ack, body=body, logger=logger)

    ack.assert_awaited_once()
    mock_app_instance.gpio.set_relay.assert_called_once_with(1, True)
    mock_app_instance.timer_relock.set_wait_time.assert_called_once()
    mock_app_instance.slack.chat_postMessage.assert_awaited()


# Additional tests can be added for other actions like ttsMessage, sendMessage, restartApp, etc.
