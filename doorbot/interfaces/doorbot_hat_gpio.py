"""
Interface with Doorbot 1.3 hat digital inputs and output (GPIO).
Control Relays and read from switches.

Author: Tazard, 2022
Compatibility: Python3
"""

import time
import pigpio
import logging

logger = logging.getLogger(__name__)

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
    def __init__(self, pigpio_pi, pin: int):
        """
        Debounces a digital input pin by ignoring transitions for certain time.
        Inverts value so that HIGH is switch pressed and LOW is unpressed.
        """
        self.pi = pigpio_pi
        self.pin = pin
        self.wait_time_s = DEBOUNCE_WAIT_S
        self.current_value = None
        self.bouncing = False
        self.last_bounce_time = None
        self.value_changed = False

    def update(self):
        # value = High: Open circuit (switch not pressed)
        #         Low: Closed circuit (switch pressed)
        value = self.pi.read(self.pin)

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
    def __init__(self, pigpio_pi, pin: int):
        self.pi = pigpio_pi
        self.pin = pin

    def set(self, relay_on: bool):
        """Set new state for hat relay"""
        # Flip the logic if RELAY_ON is false
        if RELAY_ON:
            state = relay_on
        else:
            state = not relay_on
        self.pi.write(self.pin, state)


class DoorbotHatGpio:
    def __init__(self, pigpio_pi):
        """
        Interface class to Doorbot Hat 1.3 digital inputs and outputs

        Provides functions for setting relays on/off
        and functions for checking if switches are pressed.
        """
        self.log("Setup start")

        # On first boot, needs a bit of time or relays sometimes go haywire
        time.sleep(1)

        # pigpio uses BCM (Broadcom SOC channel) numbering by default
        self.pi = pigpio_pi

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
        self.log("Stopping pigpio")
        self.pi.stop()

        # On shutdown, needs a bit of time or sometimes goes haywire (first boot)
        time.sleep(1)

    def log(self, message: str):
        logger.debug("[DoorbotHatGpio] {}".format(message))

    def setup_switches(self, id, pin):
        # Set pin direction
        self.pi.set_mode(pin, pigpio.INPUT)
        self.pi.set_pull_up_down(pin, pigpio.PUD_UP)
        # Create the debouncer object
        self.switches[id] = DebouncedInput(self.pi, pin)

    def setup_relays(self, id, pin):
        # Set pin direction
        self.pi.set_mode(pin, pigpio.OUTPUT)
        # Initialise pin as relay off
        self.pi.write(pin, RELAY_OFF)
        # Create the relay object
        self.relays[id] = RelayOutput(self.pi, pin)

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
        return results
