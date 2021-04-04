"""
Interface with doorbot 1.3 hat digital inputs and ouput

Author: Tazard 2021
Compatibility: Python3
"""

import time
import serial
import RPi.GPIO as GPIO

# Input switch debounce time
DEBOUNCE_WAIT_S = 0.1
# Boolean state of GPIO output to turn relay on
RELAY_ON = True
RELAY_OFF = not RELAY_ON


class DebouncedInput:
    def __init__(self, pin: int):
        """Debounces a digital input pin by ignoring transitions for certain time.
        Value = High: Open circuit (switch not pressed)
                Low: Closed circuit (switch pressed)
        """
        self.pin = pin
        self.wait_time_s = DEBOUNCE_WAIT_S
        self.current_value = None
        self.bouncing = False
        self.last_bounce_time = None
        self.value_changed = False

    def update(self):
        value = GPIO.input(self.pin)

        # Normally high inputs (open circuit is pullup)
        # Invert so that unpressed buttons are low and pressed is high
        value = not value

        if self.current_value is None:
            # Initialise to first value
            self.current_value = value
            return
        
        elif not self.bouncing and value == self.current_value:
            # The boring, nothing has changed case
            pass

        elif not self.bouncing and value != self.current_value:
            # Value has changed, start bounce timer, set value to new value
            self.bouncing = True
            self.last_bounce_time = time.monotonic()
            self.current_value = value
            self.value_changed = True

        elif self.bouncing and (time.monotonic() - self.last_bounce_time) <= self.wait_time_s:
            # We are in the time allowed for debounce, ignore changes
            pass
         
        elif self.bouncing and (time.monotonic() - self.last_bounce_time) > self.wait_time_s:
            # We have finished the time allowed for debouncing, reset
            self.bouncing = False
            self.last_bounce_time = None

    def value(self):
        return self.current_value

    def has_changed(self):
        """Return whether value has changed since last call of this method"""
        v = self.value_changed
        self.value_changed = False
        return v


class RelayOutput:
    def __init__(self, pin: int):
        self.pin = pin

    def set(self, relay_on: bool):
        """Set new state for hat relay"""
        # Flip the logic if RELAY_ON is false
        if RELAY_ON:
            state = relay_on
        else:
            state = not relay_on
        GPIO.output(self.pin, state)


class DoorbotHatInterface:
    def __init__(self, config:dict, on_input_change):
        """
        Interface class to Doorbot Hat 1.3 digital inputs and outputs
        
        Provides functions for setting relays on/off
        and will trigger callback when inputs change
        """
        self.log("Setup start")
        self.config = config
        self.on_input_change = on_input_change
        self.setup_io()
        self.inputs = [
            DebouncedInput(self.pin_locator("input", "channel1")),
            DebouncedInput(self.pin_locator("input", "channel2")),
            DebouncedInput(self.pin_locator("input", "channel3")),
            DebouncedInput(self.pin_locator("input", "channel4"))
        ]
        self.outputs = [
            RelayOutput(self.pin_locator("output", "channel1")),
            RelayOutput(self.pin_locator("output", "channel2")),
            RelayOutput(self.pin_locator("output", "channel3")),
            RelayOutput(self.pin_locator("output", "channel4"))
        ]
        self.log("Setup complete")

    def __del__(self):
        GPIO.cleanup()

    def log(self, message: str):
        print("[DoorbotHatInterface] {}".format(message))

    def pin_locator(self, direction, channel):
        """For a given direction (input|output), lookup the pin for a channel"""
        return self.config["io"]["digital_" + direction + "_pins"][channel]

    def setup_io(self):
        """Set pin modes of inputs and outputs and init outputs to off"""
        # Use BCM pin map
        GPIO.setmode(GPIO.BCM)

        # Outputs
        outputs = self.config["io"]["digital_output_pins"]
        for ch in outputs:
            # Set pin direction
            GPIO.setup(outputs[ch], GPIO.OUT)
            # Initialise pin as relay off
            GPIO.output(outputs[ch], RELAY_OFF)

        # Inputs
        inputs = self.config["io"]["digital_input_pins"]
        for ch in outputs:
            # Set pin direction
            GPIO.setup(inputs[ch], GPIO.IN)

    def set_output(self, channel_number: int, relay_on: bool):
        """Set state of given relay on doorbot hat"""
        if not (1 <= channel_number <= 4):
            raise Exception("Invalid output channel number {}".format(channel_number))
        state_text = {True: "On", False: "Off"}[relay_on]
        self.log("Set Output Channel {} to Relay {}".format(channel_number, state_text))
        output_index = channel_number - 1
        self.outputs[output_index].set(relay_on=relay_on)

    def read_inputs(self):
        """Read doorbot hat inputs and fire callbacks on change"""
        for index, di in enumerate(self.inputs):
            di.update()
            if di.has_changed():
                # Closed circuit (pressed) is True here
                value = di.value()
                channel = index + 1
                self.log("Input Channel {} Changed to {}".format(channel, value))
                self.on_input_change(channel, value)
