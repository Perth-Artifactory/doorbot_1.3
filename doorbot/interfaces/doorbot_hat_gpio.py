"""
Interface with Doorbot 1.3 hat digital inputs and ouput (GPIO).
Control Relays and read from switches.

Author: Tazard, 2022
Compatibility: Python3
"""

import time
import RPi.GPIO as GPIO


# Input switch debounce time
DEBOUNCE_WAIT_S = 0.1
# Boolean state of GPIO output to turn relay on
RELAY_ON = True
RELAY_OFF = not RELAY_ON

# Labels for switches
ID_SWITCH_1 = 'SW1'
ID_SWITCH_2 = 'SW2'
ID_SWITCH_3 = 'SW3'
ID_SWITCH_4 = 'SW4'

# Labels for relays
ID_RELAY_1 = 'R1'
ID_RELAY_2 = 'R2'
ID_RELAY_3 = 'R3'
ID_RELAY_4 = 'R4'


class DebouncedInput:
    def __init__(self, pin: int):
        """
        Debounces a digital input pin by ignoring transitions for certain time.
        Inverts value so that HIGH is switch pressed and LOW is unpressed.
        """
        self.pin = pin
        self.wait_time_s = DEBOUNCE_WAIT_S
        self.current_value = None
        self.bouncing = False
        self.last_bounce_time = None
        self.value_changed = False

    def update(self):
        # value = High: Open circuit (switch not pressed)
        #         Low: Closed circuit (switch pressed)
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


class DoorbotHatGpio:
    def __init__(self):
        """
        Interface class to Doorbot Hat 1.3 digital inputs and outputs

        Provides functions for setting relays on/off
        and functions for checking if switches are pressed.
        """
        self.log("Setup start")

        # Use BCM pin map
        GPIO.setmode(GPIO.BCM)

        self.switches = {}
        self.setup_switches(id=ID_SWITCH_1, pin=23)
        self.setup_switches(id=ID_SWITCH_2, pin=24)
        self.setup_switches(id=ID_SWITCH_3, pin=25)
        self.setup_switches(id=ID_SWITCH_4, pin=26)

        self.relays = {}
        self.setup_relays(id=ID_RELAY_1, pin=19)
        self.setup_relays(id=ID_RELAY_2, pin=20)
        self.setup_relays(id=ID_RELAY_3, pin=21)
        self.setup_relays(id=ID_RELAY_4, pin=22)

        self.log("Setup complete")

    def __del__(self):
        GPIO.cleanup()

    def log(self, message: str):
        print("[DoorbotHatInterface] {}".format(message))

    def setup_switches(self, id, pin):
        # Set pin direction
        GPIO.setup(pin, GPIO.IN)
        # Create the debouncer object
        self.switches[id] = DebouncedInput(pin)

    def setup_relays(self, id, pin):
        # Set pin direction
        GPIO.setup(pin, GPIO.OUT)
        # Initialise pin as relay off
        GPIO.output(pin, RELAY_OFF)
        # Create the relay object
        self.relays[id] = RelayOutput(pin)

    def set_relay(self, id, relay_on: bool):
        """Set state of given relay on doorbot hat"""
        if id not in self.relays:
            raise Exception("Invalid relay '{}'".format(id))
        state_text = {True: "On", False: "Off"}[relay_on]
        self.log("Set Relay '{}' to '{}'".format(id, state_text))
        self.relays[id].set(relay_on=relay_on)

    def read_switches(self) -> dict:
        """Read doorbot hat input switches and return current values"""
        results = {}
        for id in self.switches:
            switch = self.switches[id]
            switch.update()
            results[id] = switch.value()
            if switch.has_changed():
                value = switch.value()
                self.log("Switch '{}' Changed to '{}'".format(id, value))
