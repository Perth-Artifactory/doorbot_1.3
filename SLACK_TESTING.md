# Slack Interactive Testing Guide

This guide explains how to test the Doorbot Slack home view and loading buttons interactively.

## Option 1: Using the Testing Script (Recommended)

I've created `slack_testing_app.py` which runs a lightweight version of the Slack app with all hardware mocked.

### Setup

1. **Make sure the channels exist** in your Slack workspace:
   - `#doorbot-slack-test` (or update the channel name in the script)
   - `#doorbot-test-2` (for logs)

2. **Run the testing script**:
   ```bash
   cd /home/tazard/doorbot_1.3
   python slack_testing_app.py
   ```

3. **Open Slack** and go to the Doorbot app's Home tab

### What You Can Test

✅ **Home View Loading**: Opens the home view with all buttons  
✅ **Loading Buttons**: Click buttons to see `:spinthinking:` spinner  
✅ **Success Messages**: See success feedback with ✓  
✅ **Button Reset**: Watch buttons return to original state  
✅ **Authorization**: Only the configured admin user can use buttons  
✅ **Mock Hardware**: All GPIO/Blinkstick/TTS actions are logged but not executed  

### Testing Steps

1. **Start the app** - you should see "⚡️ Bolt app is running!"
2. **Open Slack** - go to the Doorbot app Home tab
3. **Try each button**:
   - **Unlock Button**: Shows loading → success → reset
   - **Update Keys**: Shows loading → mock key download → success → reset  
   - **Liveliness Check**: Shows loading → uptime display → success → reset
   - **Restart/Reboot**: Shows loading → mock action (doesn't actually restart)
4. **Watch the console** for detailed logs of all actions

## Option 2: Testing Mode in Main App

If you prefer to modify the main app, you could add a `--testing` flag:

```python
# In app.py, replace hardware initialization with:
if "--testing" in sys.argv:
    # Use mock classes
    pigpio_pi = Mock()
    hat_gpio = Mock()
    # etc...
else:
    # Use real hardware
    pigpio_pi = pigpio.pi()
    hat_gpio = DoorbotHatGpio(pigpio_pi)
    # etc...
```

## Option 3: Development Environment

For a more permanent development setup:

1. **Create a separate config file**: `config_dev.json`
2. **Set environment variable**: `DOORBOT_ENV=development`
3. **Modify app.py** to load different config and use mocks in dev mode

## Troubleshooting

**"channel_not_found" error**: Create the channels in Slack or update the channel names in the script.

**"Not authorized" when clicking buttons**: Make sure the `ADMIN_USER_ID` in the script matches your Slack user ID. You can find it by:
```bash
# Get your user ID
python -c "
import asyncio
from slack_bolt.app.async_app import AsyncApp
async def get_me():
    app = AsyncApp(token='your-bot-token')
    response = await app.client.auth_test()
    print('Your user ID:', response.get('user_id'))
asyncio.run(get_me())
"
```

**App not connecting**: Check that your `SLACK_BOT_TOKEN` and `SLACK_APP_TOKEN` are correct and the app has Socket Mode enabled.

## Benefits of This Approach

✅ **Safe**: No risk of affecting real hardware  
✅ **Fast**: No need to deploy to Raspberry Pi  
✅ **Realistic**: Uses real Slack API and actual button code  
✅ **Debuggable**: Full console logs of all actions  
✅ **Portable**: Runs on any machine with Python  

## Next Steps

Once you're happy with the button behavior:

1. **Deploy changes** to the real Raspberry Pi
2. **Test with real hardware** in a controlled way
3. **Monitor logs** for any issues in production

The testing script gives you confidence that the Slack integration works correctly before touching the real door system!
