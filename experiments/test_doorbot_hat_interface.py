"""
Tests for DoorbotHatInterface

Author: Tazard, 2021
Compatibility: Python3
"""

import time
import json
from doorbot_hat_interface import DoorbotHatInterface

TEST_CONFIG = "config/main_config.json"


def on_input_change(channel:int, state:bool):
    print("on_input_change - channel: {}, state: {}".format(channel, state))

def main():
    last_time = time.monotonic()
    count = 0

    with open(TEST_CONFIG, 'r') as f:
        config = json.load(f)
    config = config["doorbot_hat"]
    
    o = DoorbotHatInterface(config, on_input_change)

    while True:
        # Read inputs which will fire callbacks when switch closed
        o.read_inputs()
        time.sleep(0.001)

        # Cycle through setting each relay so they can be tested
        if time.monotonic() - last_time > 2:
            last_time = time.monotonic()
            o.set_output(1, count > 2)
            o.set_output(2, count > 3)
            o.set_output(3, count > 4)
            o.set_output(4, count > 5)
            count += 1
            count %= 7

if __name__ == "__main__":
    main()
