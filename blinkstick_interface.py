"""
A class to control USB led light inside doorbot
"""

from enum import Enum
from blinkstick import blinkstick


class Colour(Enum):
    WHITE = 0
    RED = 1
    GREEN = 2
    BLUE = 3
    BLACK = 4
    YELLOW = 5


class BlinkstickInterface:
    COLOUR_LOOKUP = {
        Colour.WHITE: [50, 50, 50],
        Colour.BLACK: [0, 0, 0],
        Colour.GREEN: [255, 0, 0],
        Colour.BLUE: [0, 255, 0],
        Colour.RED: [0, 0, 255],
        Colour.YELLOW: [255, 255, 0],
    }

    def __init__(self) -> None:
        """Sets up blinkstick"""
        self.stick = blinkstick.find_first()

    def ledset(self, col=Colour.WHITE):
        """Set the colour by name"""
        if col in self.COLOUR_LOOKUP.keys():
            self.stick.set_led_data(0, self.COLOUR_LOOKUP[col]*8)
