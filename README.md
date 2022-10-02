# doorbot_1.3
DoorBot 1.3 consisting of a Raspberry Pi 2 and custom made DoorBot v1.3 shield

## Python Virtual Environment

Create virtual environment
```
python3 -m venv .venv
```

Run this in commandline to activate the python virtual environment:
```
source .venv/bin/activate
```

## Env variable

The bolt examples use an environmnet variable to provide tokens. For socket mode, set it like:
```
export SLACK_APP_TOKEN=xapp-your-token
export SLACK_BOT_TOKEN=xoxb-your-token
```
