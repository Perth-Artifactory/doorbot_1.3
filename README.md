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

Install requirements:
```
pip install -r requirements.txt
```

playsound requires gstreamer (activate venv before installing):
```
sudo apt-get install python3-gst-1.0 gstreamer1.0-plugins-good gstreamer1.0-plugins-ugly gstreamer1.0-tools
```

Copy service files in and load them:
```
sudo cp speaker_server.service /etc/systemd/system
sudo cp doorbot.service /etc/systemd/system
sudo systemctl daemon-reload
```

## Run

Run this in commandline to activate the python virtual environment:
```
source .venv/bin/activate
```

Run the app for development
```
python -m doorbot
```

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

