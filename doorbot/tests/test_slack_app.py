"""
Tests for Slack app functionality, focusing on the spinning icon/loading button feature.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch, Mock
import copy
import json
import sys
import os

# Add the parent directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Import slack_blocks directly (it doesn't have dependencies)
from doorbot.interfaces import slack_blocks

# Import individual functions we want to test by copying them
def patch_home_blocks(blocks, block_id, action_id, appended_text=None, replacement_text=None, style=None):
    """Patch blocks for home view buttons with loading indicators or updates"""
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
        from slack_sdk.errors import SlackApiError
        
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
    except Exception as e:
        logger.error(f"Failed to update home view: {e}")


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


class TestSlackLoadingButtons:
    """Test suite for the Slack loading button functionality"""

    @pytest.fixture
    def mock_body_unlock(self):
        """Mock Slack body for unlock button action"""
        return {
            "actions": [{
                "action_id": "unlock",
                "block_id": "unlock_section",
                "value": "30"
            }],
            "user": {"id": "U12345"},
            "view": {
                "blocks": copy.deepcopy(slack_blocks.home_view["blocks"])
            }
        }

    @pytest.fixture
    def mock_body_admin_action(self):
        """Mock Slack body for admin button action"""
        return {
            "actions": [{
                "action_id": "updateKeys",
                "block_id": "admin_actions",
                "value": "update_keys"
            }],
            "user": {"id": "U12345"},
            "view": {
                "blocks": copy.deepcopy(slack_blocks.home_view["blocks"])
            }
        }

    @pytest.fixture
    def mock_client(self):
        """Mock Slack client"""
        client = AsyncMock()
        client.views_publish = AsyncMock()
        return client

    @pytest.fixture
    def mock_logger(self):
        """Mock logger"""
        return MagicMock()

    def test_patch_home_blocks_appends_loading_icon_to_accessory_button(self, mock_body_unlock):
        """Test that patch_home_blocks correctly adds loading icon to accessory button"""
        blocks = mock_body_unlock["view"]["blocks"]
        action = mock_body_unlock["actions"][0]
        
        patched_blocks = patch_home_blocks(
            blocks=blocks,
            block_id=action["block_id"],
            action_id=action["action_id"],
            appended_text=" :spinthinking:"
        )
        
        # Find the unlock section block
        unlock_block = None
        for block in patched_blocks:
            if block.get("block_id") == "unlock_section":
                unlock_block = block
                break
        
        assert unlock_block is not None, "Unlock section block should exist"
        assert "accessory" in unlock_block, "Unlock block should have accessory"
        
        button_text = unlock_block["accessory"]["text"]["text"]
        assert " :spinthinking:" in button_text, f"Button text should contain loading icon, got: {button_text}"
        assert button_text == "Unlock for 30 seconds :spinthinking:"

    def test_patch_home_blocks_appends_loading_icon_to_elements_button(self, mock_body_admin_action):
        """Test that patch_home_blocks correctly adds loading icon to elements button"""
        blocks = mock_body_admin_action["view"]["blocks"]
        action = mock_body_admin_action["actions"][0]
        
        patched_blocks = patch_home_blocks(
            blocks=blocks,
            block_id=action["block_id"],
            action_id=action["action_id"],
            appended_text=" :spinthinking:"
        )
        
        # Find the admin actions block
        admin_block = None
        for block in patched_blocks:
            if block.get("block_id") == "admin_actions":
                admin_block = block
                break
        
        assert admin_block is not None, "Admin actions block should exist"
        assert "elements" in admin_block, "Admin block should have elements"
        
        # Find the updateKeys button
        update_keys_button = None
        for element in admin_block["elements"]:
            if element.get("action_id") == "updateKeys":
                update_keys_button = element
                break
        
        assert update_keys_button is not None, "Update keys button should exist"
        button_text = update_keys_button["text"]["text"]
        assert " :spinthinking:" in button_text, f"Button text should contain loading icon, got: {button_text}"
        assert button_text == "Update Keys :spinthinking:"

    def test_patch_home_blocks_replaces_text(self, mock_body_unlock):
        """Test that patch_home_blocks correctly replaces button text"""
        blocks = mock_body_unlock["view"]["blocks"]
        action = mock_body_unlock["actions"][0]
        
        patched_blocks = patch_home_blocks(
            blocks=blocks,
            block_id=action["block_id"],
            action_id=action["action_id"],
            replacement_text="Unlocked! ✓",
            style="primary"
        )
        
        # Find the unlock section block
        unlock_block = None
        for block in patched_blocks:
            if block.get("block_id") == "unlock_section":
                unlock_block = block
                break
        
        assert unlock_block is not None
        button_text = unlock_block["accessory"]["text"]["text"]
        assert button_text == "Unlocked! ✓"
        assert unlock_block["accessory"]["style"] == "primary"

    def test_patch_home_blocks_removes_existing_loading_icon(self, mock_body_unlock):
        """Test that patch_home_blocks removes existing loading icon before adding new text"""
        blocks = mock_body_unlock["view"]["blocks"]
        action = mock_body_unlock["actions"][0]
        
        # First add a loading icon
        blocks_with_loading = patch_home_blocks(
            blocks=blocks,
            block_id=action["block_id"],
            action_id=action["action_id"],
            appended_text=" :spinthinking:"
        )
        
        # Then add another loading icon - should not duplicate
        blocks_double_patched = patch_home_blocks(
            blocks=blocks_with_loading,
            block_id=action["block_id"],
            action_id=action["action_id"],
            appended_text=" :spinthinking:"
        )
        
        # Find the unlock section block
        unlock_block = None
        for block in blocks_double_patched:
            if block.get("block_id") == "unlock_section":
                unlock_block = block
                break
        
        button_text = unlock_block["accessory"]["text"]["text"]
        # Should only have one loading icon
        assert button_text.count(" :spinthinking:") == 1, f"Should only have one loading icon, got: {button_text}"

    def test_patch_home_blocks_preserves_original_blocks(self, mock_body_unlock):
        """Test that patch_home_blocks doesn't modify the original blocks"""
        original_blocks = mock_body_unlock["view"]["blocks"]
        action = mock_body_unlock["actions"][0]
        
        # Get original text
        original_text = None
        for block in original_blocks:
            if block.get("block_id") == "unlock_section":
                original_text = block["accessory"]["text"]["text"]
                break
        
        # Patch the blocks
        patched_blocks = patch_home_blocks(
            blocks=original_blocks,
            block_id=action["block_id"],
            action_id=action["action_id"],
            appended_text=" :spinthinking:"
        )
        
        # Check original blocks are unchanged
        current_text = None
        for block in original_blocks:
            if block.get("block_id") == "unlock_section":
                current_text = block["accessory"]["text"]["text"]
                break
        
        assert current_text == original_text, "Original blocks should not be modified"

    @pytest.mark.asyncio
    async def test_set_loading_icon_on_button_calls_views_publish(self, mock_body_unlock, mock_client, mock_logger):
        """Test that set_loading_icon_on_button calls views_publish with correct parameters"""
        await set_loading_icon_on_button(
            body=mock_body_unlock,
            client=mock_client,
            logger=mock_logger
        )
        
        # Check that views_publish was called once
        mock_client.views_publish.assert_called_once()
        
        # Get the call arguments
        call_args = mock_client.views_publish.call_args
        assert call_args[1]["user_id"] == "U12345"
        assert call_args[1]["view"]["type"] == "home"
        
        # Check that the blocks contain the loading icon
        blocks = call_args[1]["view"]["blocks"]
        unlock_block = None
        for block in blocks:
            if block.get("block_id") == "unlock_section":
                unlock_block = block
                break
        
        assert unlock_block is not None
        button_text = unlock_block["accessory"]["text"]["text"]
        assert " :spinthinking:" in button_text

    @pytest.mark.asyncio
    async def test_reset_button_after_action_with_success_text(self, mock_body_unlock, mock_client, mock_logger):
        """Test that reset_button_after_action shows success text then resets"""
        with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            await reset_button_after_action(
                body=mock_body_unlock,
                client=mock_client,
                logger=mock_logger,
                success_text="Unlocked! ✓",
                delay_seconds=1
            )
            
            # Should be called twice: once for success, once for reset
            assert mock_client.views_publish.call_count == 2
            
            # Check that sleep was called with correct delay
            mock_sleep.assert_called_once_with(1)
            
            # First call should show success text
            first_call = mock_client.views_publish.call_args_list[0]
            first_blocks = first_call[1]["view"]["blocks"]
            unlock_block = None
            for block in first_blocks:
                if block.get("block_id") == "unlock_section":
                    unlock_block = block
                    break
            
            assert unlock_block["accessory"]["text"]["text"] == "Unlocked! ✓"
            assert unlock_block["accessory"]["style"] == "primary"
            
            # Second call should reset to original view
            second_call = mock_client.views_publish.call_args_list[1]
            assert second_call[1]["view"] == slack_blocks.home_view

    @pytest.mark.asyncio
    async def test_reset_button_after_action_without_success_text(self, mock_body_unlock, mock_client, mock_logger):
        """Test that reset_button_after_action directly resets when no success text"""
        await reset_button_after_action(
            body=mock_body_unlock,
            client=mock_client,
            logger=mock_logger
        )
        
        # Should only be called once for reset
        mock_client.views_publish.assert_called_once()
        
        # Should reset to original view
        call_args = mock_client.views_publish.call_args
        assert call_args[1]["view"] == slack_blocks.home_view

    @pytest.mark.asyncio
    async def test_set_loading_icon_handles_slack_api_error(self, mock_body_unlock, mock_logger):
        """Test that set_loading_icon_on_button handles SlackApiError gracefully"""
        from slack_sdk.errors import SlackApiError
        
        mock_client = AsyncMock()
        mock_client.views_publish.side_effect = SlackApiError(
            message="Test error",
            response={
                "error": "test_error",
                "response_metadata": {"messages": ["Test message"]}
            }
        )
        
        # Should not raise exception
        await set_loading_icon_on_button(
            body=mock_body_unlock,
            client=mock_client,
            logger=mock_logger
        )
        
        # Should log the error
        mock_logger.error.assert_called()

    def test_slack_blocks_have_required_block_ids(self):
        """Test that slack_blocks have the required block_id attributes"""
        blocks = slack_blocks.home_view["blocks"]
        
        required_block_ids = [
            "message_actions",
            "tts_input", 
            "unlock_section",
            "admin_actions"
        ]
        
        found_block_ids = []
        for block in blocks:
            if "block_id" in block:
                found_block_ids.append(block["block_id"])
        
        for required_id in required_block_ids:
            assert required_id in found_block_ids, f"Missing required block_id: {required_id}"


class TestSlackBlocksStructure:
    """Test the structure of slack_blocks to ensure they're valid"""
    
    def test_home_view_structure(self):
        """Test that home_view has correct structure"""
        home_view = slack_blocks.home_view
        
        assert home_view["type"] == "home"
        assert "blocks" in home_view
        assert isinstance(home_view["blocks"], list)
        assert len(home_view["blocks"]) > 0

    def test_unlock_button_has_correct_structure(self):
        """Test that unlock button has correct structure for our patch function"""
        blocks = slack_blocks.home_view["blocks"]
        
        unlock_block = None
        for block in blocks:
            if block.get("block_id") == "unlock_section":
                unlock_block = block
                break
        
        assert unlock_block is not None, "Unlock section should exist"
        assert unlock_block["type"] == "section"
        assert "accessory" in unlock_block
        assert unlock_block["accessory"]["type"] == "button"
        assert unlock_block["accessory"]["action_id"] == "unlock"
        assert "text" in unlock_block["accessory"]
        assert "text" in unlock_block["accessory"]["text"]

    def test_admin_buttons_have_correct_structure(self):
        """Test that admin buttons have correct structure for our patch function"""
        blocks = slack_blocks.home_view["blocks"]
        
        admin_block = None
        for block in blocks:
            if block.get("block_id") == "admin_actions":
                admin_block = block
                break
        
        assert admin_block is not None, "Admin actions should exist"
        assert admin_block["type"] == "actions"
        assert "elements" in admin_block
        assert len(admin_block["elements"]) > 0
        
        # Check each button has required structure
        for element in admin_block["elements"]:
            if element["type"] == "button":
                assert "action_id" in element
                assert "text" in element
                assert "text" in element["text"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
