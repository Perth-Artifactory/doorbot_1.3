"""
Integration tests for Slack app functionality.
These tests require real Slack tokens and should be run manually.

This test suite imports the REAL functions from app.py by mocking hardware dependencies first.
This ensures integration tests validate the actual implementation, not a copy.

The mocking approach (defined in conftest.py):
1. Mock hardware modules BEFORE importing app.py
2. Import the actual functions from app.py
3. Test the real implementation with mocked dependencies

To run these tests, set the following environment variables:
- SLACK_BOT_TOKEN: Your Slack bot token
- SLACK_APP_TOKEN: Your Slack app token (for socket mode)
- TEST_USER_ID: A test user ID to simulate actions

Example:
export SLACK_BOT_TOKEN="xoxb-your-bot-token"
export SLACK_APP_TOKEN="xapp-your-app-token"
export TEST_USER_ID="U12345"
python -m pytest doorbot/tests/test_slack_integration.py -v
"""

import pytest
import asyncio
import os
from unittest.mock import MagicMock
from slack_bolt.app.async_app import AsyncApp
from slack_sdk.errors import SlackApiError
import copy
import sys

# Hardware mocks are automatically installed by conftest.py
# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Import the REAL functions from app.py
from doorbot.app import patch_home_blocks, set_loading_icon_on_button, reset_button_after_action

# Import slack_blocks for testing
from doorbot.interfaces import slack_blocks


@pytest.mark.integration
@pytest.mark.skipif(
    not all([
        os.getenv("SLACK_BOT_TOKEN"),
        os.getenv("SLACK_APP_TOKEN"),
        os.getenv("TEST_USER_ID")
    ]),
    reason="Slack tokens and test user ID not provided"
)
class TestSlackIntegration:
    """Integration tests that require real Slack tokens"""

    @pytest.fixture
    def slack_app(self):
        """Create a real Slack app for testing"""
        return AsyncApp(token=os.getenv("SLACK_BOT_TOKEN"))

    @pytest.fixture
    def test_user_id(self):
        """Get test user ID from environment"""
        return os.getenv("TEST_USER_ID")

    @pytest.fixture
    def mock_body_unlock(self, test_user_id):
        """Mock Slack body for unlock button action"""
        return {
            "actions": [{
                "action_id": "unlock",
                "block_id": "unlock_section",
                "value": "30"
            }],
            "user": {"id": test_user_id},
            "view": {
                "blocks": copy.deepcopy(slack_blocks.home_view["blocks"])
            }
        }

    @pytest.fixture
    def mock_logger(self):
        """Mock logger"""
        return MagicMock()

    @pytest.mark.asyncio
    async def test_publish_home_view_with_loading_icon(self, slack_app, mock_body_unlock, mock_logger):
        """Test publishing home view with loading icon to real Slack"""
        try:
            await set_loading_icon_on_button(
                body=mock_body_unlock,
                client=slack_app.client,
                logger=mock_logger
            )
            
            # If we get here, the API call succeeded
            assert True, "Successfully published home view with loading icon"
            
        except SlackApiError as e:
            pytest.fail(f"Slack API error: {e.response['error']}")

    @pytest.mark.asyncio
    async def test_full_button_interaction_flow(self, slack_app, mock_body_unlock, mock_logger):
        """Test the complete flow: loading -> success -> reset"""
        try:
            # Step 1: Show loading icon
            await set_loading_icon_on_button(
                body=mock_body_unlock,
                client=slack_app.client,
                logger=mock_logger
            )
            
            # Step 2: Simulate some work
            await asyncio.sleep(1)
            
            # Step 3: Show success and reset
            await reset_button_after_action(
                body=mock_body_unlock,
                client=slack_app.client,
                logger=mock_logger,
                success_text="Test completed! ✓",
                delay_seconds=2
            )
            
            assert True, "Successfully completed full button interaction flow"
            
        except SlackApiError as e:
            pytest.fail(f"Slack API error: {e.response['error']}")

    @pytest.mark.asyncio
    async def test_publish_original_home_view(self, slack_app, test_user_id):
        """Test publishing the original home view"""
        try:
            await slack_app.client.views_publish(
                user_id=test_user_id,
                view=slack_blocks.home_view
            )
            
            assert True, "Successfully published original home view"
            
        except SlackApiError as e:
            pytest.fail(f"Slack API error: {e.response['error']}")


if __name__ == "__main__":
    # Instructions for running integration tests
    print("Integration Tests for Slack Loading Buttons")
    print("==========================================")
    print()
    print("To run these tests, you need to set environment variables:")
    print("export SLACK_BOT_TOKEN='xoxb-your-bot-token'")
    print("export SLACK_APP_TOKEN='xapp-your-app-token'")  
    print("export TEST_USER_ID='U12345'")
    print()
    print("Then run: python -m pytest doorbot/tests/test_slack_integration.py -v")
    print()
    print("Note: These tests will actually publish to your Slack workspace!")
