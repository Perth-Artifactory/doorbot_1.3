"""
Tests for DoorbotHatInterface

Author: Tazard, 2021
Compatibility: Python3
"""

import time
import json
from doorbot_hat_interface import DoorbotHatInterface

TEST_CONFIG = "config/doorbot_hat_definition.json"


def on_door_closed_changed(state):
    print("on_door_closed_changed - ", state)

def on_green_button_pressed():
    print("on_green_button_pressed")

def on_red_button_pressed():
    print("on_red_button_pressed")

def on_doorbell_pressed():
    print("on_doorbell_pressed")

def main():
    last_time = time.monotonic()
    count = 0

    with open(TEST_CONFIG, 'r') as f:
        config = json.load(f)
    
    o = DoorbotHatInterface(config, 
            on_door_closed_changed, on_green_button_pressed,
            on_red_button_pressed, on_doorbell_pressed)

    while True:
        # Read inputs which will fire callbacks when switch closed
        o.read_inputs()
        time.sleep(0.001)

        # Cycle through setting each relay so they can be tested
        if time.monotonic() - last_time > 2:
            last_time = time.monotonic()
            o.set_door_solenoid(unlocked=count > 2)
            o.set_foyer_lights(on=count > 3)
            o.set_carpark_lights(on=count > 4)
            o.set_spare(on=count > 5)
            count += 1
            count %= 7

if __name__ == "__main__":
    main()
