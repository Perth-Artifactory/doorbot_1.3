# doorbot_1.3
DoorBot 1.3 consisting of a Raspberry Pi 2 and custom made DoorBot v1.3 shield

## Codebase Overview

The project is an asynchronous Slack bot that controls hardware on a Raspberry Pi. The main entry point is `doorbot/app.py`, which sets up logging, loads configuration, and starts hardware interfaces. It defines Slack bot actions for unlocking the door, sending messages, and other operations.

### General Structure

- `doorbot/app.py` – main async application launched via `python -m doorbot`. It handles logging, configuration, hardware interfaces and defines Slack actions.
- `doorbot/interfaces/` – hardware and API interfaces such as:
  - `doorbot_hat_gpio.py` for controlling the DoorBot hat relays and inputs via `pigpio`.
  - `wiegand_key_reader.py` and `wiegand.py` for reading RFID/NFC cards.
  - `blinkstick_interface.py` to drive the BlinkStick LED strip.
  - `tidyauth_client.py` and `user_manager.py` for fetching authorised keys.
  - `sound_downloader.py`, `sound_player.py`, and `text_to_speech.py` for audio playback and TTS.
  - `slack_blocks.py` containing Slack BlockKit payloads.
- `doorbot/utils/` – miscellaneous scripts such as `convert_old_rfid_key.py` or `name_association.py`.
- `speaker_server.py` – optional Flask server exposing simple `/speak` and `/play_mp3_base64` endpoints.
- `experiments/` and `doorbot/tests/` – test scripts and hardware demos.
- `config.json.template` – example configuration with tokens, Slack channels, and TidyAuth settings.

### Pointers for Learning

- Explore Slack Bolt usage in `app.py` and the BlockKit layouts in `slack_blocks.py`.
- Check out hardware interfaces (`doorbot_hat_gpio.py`, `wiegand_key_reader.py`) and review the schematics under `schematics/`.
- Understand how `tidyauth_client.py` and `user_manager.py` manage authorised keys.
- Look into the audio helpers for VLC playback and text-to-speech.
- Review `doorbot.service` and `speaker_server.service` for deployment as systemd services.
- Logging is sent to Slack via a custom handler in `app.py`.
- From here you might delve deeper into Slack Bolt features, pigpio for advanced hardware interaction, or experiment with new Slack actions and home tab views.

## Installation

Install this package for TTS:
```
sudo apt-get install espeak
```

Create virtual environment
```
python3 -m venv .venv
```

Activate the python virtual environment:
```
source .venv/bin/activate
```

Install requirements:
```
pip install -r requirements.txt
```

Copy config template
```
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
```
sudo cp speaker_server.service /etc/systemd/system
sudo cp doorbot.service /etc/systemd/system
sudo systemctl daemon-reload
```

Reboot the pi and your app is now live

## During Operation

The app will run as a service `doorbot`. The usual systemctl commands apply:
```
sudo systemctl start doorbot
sudo systemctl stop doorbot
sudo systemctl restart doorbot
```

Inspecting logging and status via systemctl and journald:
```
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

## Development

Run this in commandline to activate the python virtual environment:
```
source .venv/bin/activate
```

Run the app for development
```
python -m doorbot
```


