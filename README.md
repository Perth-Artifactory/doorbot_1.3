# doorbot_1.3
DoorBot 1.3 consisting of a Raspberry Pi 2 and custom made DoorBot v1.3 shield

## Installation

Install this package (required for mp3s in `pygame`):
```
sudo apt-get install python3-pygame
sudo apt-get install python3-sdl2
```

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

## Run

Run this in commandline to activate the python virtual environment:
```
source .venv/bin/activate
```

Run the app
```
python -m doorbot
```
