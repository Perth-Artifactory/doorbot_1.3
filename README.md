# doorbot_1.3
DoorBot 1.3 consisting of a Raspberry Pi 2 and custom made DoorBot v1.3 shield

## Installation

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
python app.py
```
