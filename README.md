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

Activate pigpiod:
```
sudo systemctl enable pigpiod
sudo systemctl start pigpiod
```

playsound requires gstreamer (activate venv before installing):
```
sudo apt-get install python3-gst-1.0 gstreamer1.0-plugins-good gstreamer1.0-plugins-ugly gstreamer1.0-tools
```

## Run

Restart pigpiod at least once after boot to prevent random relay toggle glitch
```
sudo systemctl restart pigpiod
```

Run this in commandline to activate the python virtual environment:
```
source .venv/bin/activate
```

Run the app
```
python -m doorbot
```
