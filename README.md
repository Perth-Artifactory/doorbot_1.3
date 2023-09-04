# doorbot_1.3
DoorBot 1.3 consisting of a Raspberry Pi 2 and custom made DoorBot v1.3 shield

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
- Bad Read (tag not valid length): dark red (5s)
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


