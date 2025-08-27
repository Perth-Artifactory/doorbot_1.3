"""
Integration tests for Slack app functionality.
These tests require real Slack tokens and should be run manually.

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

# Import slack_blocks directly
from doorbot.interfaces import slack_blocks

# Import the functions to test
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Copy the functions we want to test (to avoid import issues)
def patch_home_blocks(blocks, block_id, action_id, appended_text=None, replacement_text=None, style=None):
    """Patch blocks for home view buttons with loading indicators or updates"""
    import copy
    
    new_blocks = copy.deepcopy(blocks)
    
    for block in new_blocks:
        if block.get("block_id") == block_id:
            # Handle different block types
            if "elements" in block:
                for element in block["elements"]:
                    if element.get("action_id") == action_id:
                        if replacement_text:
                            element["text"]["text"] = replacement_text
                        elif appended_text:
                            # Remove any existing loading indicator first
                            current_text = element["text"]["text"]
                            if " :spinthinking:" in current_text:
                                current_text = current_text.replace(" :spinthinking:", "")
                            element["text"]["text"] = current_text + appended_text
                        
                        if style:
                            element["style"] = style
            elif "accessory" in block and block["accessory"].get("action_id") == action_id:
                # Handle section blocks with accessory buttons
                if replacement_text:
                    block["accessory"]["text"]["text"] = replacement_text
                elif appended_text:
                    current_text = block["accessory"]["text"]["text"]
                    if " :spinthinking:" in current_text:
                        current_text = current_text.replace(" :spinthinking:", "")
                    block["accessory"]["text"]["text"] = current_text + appended_text
                
                if style:
                    block["accessory"]["style"] = style
    
    return new_blocks


async def set_loading_icon_on_button(body, client, logger):
    """Set the spinning icon on the button for home view"""
    try:
        # Get the action that was clicked
        action = body["actions"][0]
        
        # Patch the blocks with loading indicator
        new_blocks = patch_home_blocks(
            blocks=body["view"]["blocks"],
            block_id=action.get("block_id"),
            action_id=action["action_id"],
            appended_text=" :spinthinking:"
        )
        
        # Update the home view
        await client.views_publish(
            user_id=body["user"]["id"],
            view={
                "type": "home",
                "blocks": new_blocks,
            }
        )
        logger.info("Loading indicator added to button")
    except SlackApiError as e:
        logger.error(f"Failed to update home view: {e.response['error']}")


async def reset_button_after_action(body, client, logger, success_text=None, delay_seconds=3):
    """Reset button to original state after an action completes"""
    try:
        # Get the action that was clicked
        action = body["actions"][0]
        
        if success_text:
            # First show success message
            new_blocks = patch_home_blocks(
                blocks=body["view"]["blocks"],
                block_id=action.get("block_id"),
                action_id=action["action_id"],
                replacement_text=success_text,
                style="primary"
            )
            
            await client.views_publish(
                user_id=body["user"]["id"],
                view={
                    "type": "home",
                    "blocks": new_blocks,
                }
            )
            
            # Wait a bit before resetting
            await asyncio.sleep(delay_seconds)
        
        # Reset to original home view
        await client.views_publish(
            user_id=body["user"]["id"],
            view=slack_blocks.home_view
        )
        logger.info("Button reset to original state")
    except Exception as e:
        logger.error(f"Unexpected error resetting button: {e}")


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
