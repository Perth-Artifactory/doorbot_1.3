"""
Interface with doorbot 1.3 hat digital inputs and ouput

Author: Tazard 2021
Compatibility: Python3
"""

import time
import serial
import RPi.GPIO as GPIO


DEBOUNCE_WAIT_S = 0.1


class DebouncedInput:
    def __init__(self, pin, wait_time_s=DEBOUNCE_WAIT_S):
        """Debounces a digital input pin by ignoring transitions for certain time"""
        self.pin = pin
        self.wait_time_s = wait_time_s
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


class Output:
    def __init__(self, pin):
        self.pin = pin

    def set(self, state):
        GPIO.output(self.pin, state)


class DoorbotHatInterface:
    def __init__(self, config,
            on_door_closed_changed=None, on_green_button_pressed=None, 
            on_red_button_pressed=None, on_doorbell_pressed=None):
        """
        Interface class to Doorbot Hat 1.3 digital inputs and outputs
        
        Provides functions for setting relays on/off (named by their function)
        and will trigger callbacks when inputs are triggered
        """
        self.log("Setup start")

        self.config = config

        self.on_door_closed_changed = on_door_closed_changed
        self.on_green_button_pressed = on_green_button_pressed
        self.on_red_button_pressed = on_red_button_pressed
        self.on_doorbell_pressed = on_doorbell_pressed

        self.setup_io()

        self.door_closed_input = DebouncedInput(self.pin_locator("input", "door_closed_switch"))
        self.green_button_input = DebouncedInput(self.pin_locator("input", "green_button"))
        self.red_button_input = DebouncedInput(self.pin_locator("input", "red_button"))
        self.doorbell_input = DebouncedInput(self.pin_locator("input", "doorbell"))

        self.door_solenoid_output = Output(self.pin_locator("output", "door_solenoid"))
        self.foyer_lights_output = Output(self.pin_locator("output", "foyer_lights"))
        self.carpark_lights_output = Output(self.pin_locator("output", "carpark_lights"))
        self.spare_output = Output(self.pin_locator("output", "spare"))

        self.log("Setup complete")

    def __del__(self):
        GPIO.cleanup()

    def log(self, message):
        print("[DoorbotHatInterface] {}".format(message))

    def pin_locator(self, direction, functionality):
        """For a given direction (input|output), find the functionality specified (e.g. door solenoid)"""
        ch = self.config["functionality"]["digital_" + direction][functionality]
        return self.config["io"]["digital_" + direction][ch]["pin"]

    def setup_io(self):
        """Set pin modes of inputs and outputs and init outputs to off"""
        GPIO.setmode(GPIO.BCM)

        # Outputs
        outputs = self.config["io"]["digital_output"]
        for name in outputs:
            # Set pin direction
            GPIO.setup(outputs[name]["pin"], GPIO.OUT)
            # Initialise pin low (relay off)
            GPIO.output(outputs[name]["pin"], False)

        # Inputs
        inputs = self.config["io"]["digital_input"]
        for name in outputs:
            # Set pin direction
            GPIO.setup(inputs[name]["pin"], GPIO.IN)

    def set_door_solenoid(self, unlocked):
        self.log("Set Door Solenoid Unlocked = {}".format(unlocked))
        self.door_solenoid_output.set(state=unlocked)

    def set_foyer_lights(self, on):
        self.log("Set Foyer Lights On = {}".format(on))
        self.foyer_lights_output.set(state=on)

    def set_carpark_lights(self, on):
        self.log("Set Carpark Lights On = {}".format(on))
        self.carpark_lights_output.set(state=on)

    def set_spare(self, on):
        self.log("Set Spare On = {}".format(on))
        self.spare_output.set(state=on)

    def read_inputs(self):
        # Check door closed switch
        self.door_closed_input.update()
        if self.door_closed_input.has_changed():
            self.log("Door closed switch changed to {}".format(self.door_closed_input.value()))
            self.on_door_closed_changed(self.door_closed_input.value())

        # Check green button and trigger only if its now high (has been pressed)
        self.green_button_input.update()
        if self.green_button_input.has_changed() and self.green_button_input.value():
            self.log("Green button pressed")
            self.on_green_button_pressed()

        # Check green button and trigger only if its now high (has been pressed)
        self.red_button_input.update()
        if self.red_button_input.has_changed() and self.red_button_input.value():
            self.log("Red button pressed")
            self.on_red_button_pressed()

        # Check doorbell button and trigger only if its now high (has been pressed)
        self.doorbell_input.update()
        if self.doorbell_input.has_changed() and self.doorbell_input.value():
            self.log("Doorbell pressed")
            self.on_doorbell_pressed()
