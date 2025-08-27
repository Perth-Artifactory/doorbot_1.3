# Doorbot Test Suite

This directory contains tests for the Doorbot application, with a focus on the Slack integration and loading button functionality.

## Test Files

### `test_slack_app.py`

Unit tests for the Slack loading button functionality. These tests:

- Test the `patch_home_blocks` function that modifies Slack blocks with loading indicators
- Test the `set_loading_icon_on_button` function that shows spinning icons
- Test the `reset_button_after_action` function that shows success and resets buttons
- Validate the structure of Slack blocks
- Mock all external dependencies, so they run without requiring real Slack tokens

### `test_slack_integration.py`

Integration tests that require real Slack tokens. These tests:

- Actually call the Slack API to test the loading button flow
- Require environment variables: `SLACK_BOT_TOKEN`, `SLACK_APP_TOKEN`, `TEST_USER_ID`
- Should be run manually when you want to test against a real Slack workspace

## Running Tests

### Unit Tests (No Setup Required)

```bash
# Run all unit tests
python -m pytest doorbot/tests/test_slack_app.py -v

# Run with coverage
python -m pytest doorbot/tests/test_slack_app.py --cov=doorbot --cov-report=html
```

### Integration Tests (Requires Slack Tokens)

```bash
# Set environment variables
export SLACK_BOT_TOKEN="xoxb-your-bot-token"
export SLACK_APP_TOKEN="xapp-your-app-token" 
export TEST_USER_ID="U12345"

# Run integration tests
python -m pytest doorbot/tests/test_slack_integration.py -v
```

### All Tests

```bash
# Run all tests (integration tests will be skipped if no tokens)
python -m pytest -v

# Run only unit tests (exclude integration)
python -m pytest -v -m "not integration"
```

## Test Coverage

The current test suite covers:

- ✅ Loading button functionality
- ✅ Block patching logic
- ✅ Success message display
- ✅ Button reset functionality
- ✅ Error handling
- ✅ Slack block structure validation

## What We're Testing

The loading button feature provides visual feedback when users click buttons in the Slack home view:

1. **Loading State**: When a button is clicked, it immediately shows `:spinthinking:` emoji
2. **Success State**: After the operation completes, it briefly shows a success message with ✓
3. **Reset State**: After a delay, it resets back to the original button text

This provides better UX for actions that might take a few seconds (like unlocking doors, updating keys, etc.).

## Adding New Tests

When adding new Slack functionality:

1. Add unit tests to `test_slack_app.py` with mocked dependencies
2. Add integration tests to `test_slack_integration.py` if you need to test against real Slack API
3. Follow the existing pattern of testing both success and error cases
4. Ensure tests are isolated and don't depend on external state

## Legacy Test Files

Note: This directory also contains older test files (`*_test.py`) that are standalone scripts rather than proper pytest tests. These are excluded from the pytest configuration but can still be run manually if needed.
