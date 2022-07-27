"""
Script to test the various GPIO on the board

Author: Tazard 2022
Compatibility: Python3
"""

import time
import json
from doorbot_hat_interface import DoorbotHatInterface

CONFIG = {
    "doorbot_hat": {
        "io": {
            "digital_output_pins": {
                "serial_14": 14,
                "serial_15": 15,
                "A1": 2,
                "A2": 3,
                "A3": 9,
                "A4": 10,
                "A5": 11,
                "A6": 8,
                "A7": 7,
                "A8": 4,
            },
            "digital_input_pins": {
                # "channel1": 23,
                # "channel2": 24,
                # "channel3": 25,
                # "channel4": 26
            }
        }
    },
}


def on_input_change(channel:int, state:bool):
    print("on_input_change - channel: {}, state: {}".format(channel, state))

def main():
    last_time = time.monotonic()
    count = 0

    # with open(TEST_CONFIG, 'r') as f:
        # config = json.load(f)
    config = CONFIG["doorbot_hat"]
    
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
            o.set_output(5, count > 6)
            o.set_output(6, count > 7)
            o.set_output(7, count > 8)
            o.set_output(8, count > 9)
            o.set_output(9, count > 10)
            o.set_output(10, count > 11)
            count += 1
            count %= 12

if __name__ == "__main__":
    main()
