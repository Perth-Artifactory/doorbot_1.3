# doorbot_1.3

DoorBot 1.3 consisting of a Raspberry Pi 2 and custom made DoorBot v1.3 shield

## Installation

Install this package for TTS:

```bash
sudo apt-get install espeak
```

Create virtual environment

```bash
python3 -m venv .venv
```

Activate the python virtual environment:

```bash
source .venv/bin/activate
```

Install requirements:

```bash
pip install -r requirements.txt
```

Copy config template

```bash
cp config.json.template config.json
```

Fill config:

- TidyAuth token: See Fletcher.
- Slack tokens: Create a new bot and generate the tokens. Bots cannot be transferred and there isn't really any downside to creating a new one. You need to give it the appropriate permissions (TODO - list them). You need to add the bot to channels you want it to interact with.
- Update slack channels for user tracking and app logging.

Setup udev rules for blinkstick

- create udev file `sudo nano /etc/udev/rules.d/85-blinkstick.rules`
- udev file contents: `SUBSYSTEM=="usb", MODE:="0666"`

Copy service files in and load them:

```bash
sudo cp speaker_server.service /etc/systemd/system
sudo cp doorbot.service /etc/systemd/system
sudo systemctl daemon-reload
```

Reboot the pi and your app is now live

## During Operation

The app will run as a service `doorbot`. The usual systemctl commands apply:

```bash
sudo systemctl start doorbot
sudo systemctl stop doorbot
sudo systemctl restart doorbot
```

Inspecting logging and status via systemctl and journald:

```bash
sudo systemctl status doorbot
journalctl -xe -u doorbot -f
```

Logs also go to file `doorbot.log` and to Slack (INFO and above).

## Colour Codes

The blinkstick will report colours like so:

- Startup: blue
- Normal Operation: white
- Liveliness Check (from Slack): dim white (1s)
- Restart App (from Slack): light purple (1s), dark blue
- Reboot Pi (from Slack): dark purple (1s), dark blue
- Access Granted (door unlock): green (while unlocked)
- Access Denied (tag not in allowed list): red (5s)
- Bad Read (tag not valid length) or Tag Code Exception: dark red (5s)
- Keys Updated: aqua (1s)

## Testing

This project includes a comprehensive test suite to ensure reliability and functionality.

### Test Structure

Tests are located in `doorbot/tests/` and are organized as follows:

- **Unit Tests**: `test_*.py` files that test individual components with mocked dependencies
- **Integration Tests**: Tests marked with `@pytest.mark.integration` that test against real services
- **Legacy Tests**: `*_test.py` files (older standalone scripts, excluded from pytest)

### Running Tests

#### Prerequisites

Activate the virtual environment:

```bash
source .venv/bin/activate
```

#### Unit Tests (No Setup Required)

```bash
# Run all unit tests
python -m pytest -v

# Run only unit tests (exclude integration tests)
python -m pytest -v -m "not integration"

# Run tests for specific module
python -m pytest doorbot/tests/test_slack_app.py -v

# Run with coverage reporting
python -m pytest --cov=doorbot --cov-report=html
```

#### Integration Tests (Requires Real Tokens)

Integration tests require real Slack tokens and should be run manually when testing against live services:

```bash
# Set required environment variables
export SLACK_BOT_TOKEN="xoxb-your-bot-token"
export SLACK_APP_TOKEN="xapp-your-app-token" 
export TEST_USER_ID="U12345"

# Run integration tests
python -m pytest doorbot/tests/test_slack_integration.py -v
```

#### Interactive Testing

For manual testing of Slack functionality with real handlers but mock hardware:

```bash
# Run the interactive testing script
python tools/interactive_slack_testing.py
```

This script:

- Uses real Slack handlers from the main app
- Mocks all hardware interfaces (GPIO, BlinkStick, etc.)
- Connects to Slack Socket Mode for real-time testing
- Logs hardware actions without executing them

### Development Tools

The project includes several development and testing utilities:

- **`tools/interactive_slack_testing.py`**: Interactive testing with real Slack handlers and mock hardware
- **`experiments/tools/`**: Various utility scripts for development (card conversion, manual unlock, etc.)
- **`experiments/`**: Development experiments and prototypes for new features

### Test Coverage

The current test suite covers:

- ✅ **Slack Loading Buttons**: Visual feedback with spinning icons and success states
- ✅ **Block Patching**: UI modification logic for dynamic button updates  
- ✅ **Error Handling**: Graceful handling of API failures
- ✅ **Integration**: End-to-end testing with real Slack API
- ✅ **Hardware Interfaces**: Unit tests for GPIO, sound, TTS, and authentication components

### Key Testing Features

#### Loading Button Functionality

Tests ensure proper visual feedback when users interact with Slack buttons:

1. **Loading State**: Button shows `:spinthinking:` emoji immediately
2. **Success State**: Brief success message with ✓ after completion  
3. **Reset State**: Return to original button text after delay

#### Hardware Mocking

Tests mock hardware dependencies to run without physical devices:

- GPIO operations (door locks, sensors)
- BlinkStick LED control
- Sound playback
- RFID/NFC readers

## Development

Run this in commandline to activate the python virtual environment:

```bash
source .venv/bin/activate
```

Run the app for development

```bash
python -m doorbot
```
