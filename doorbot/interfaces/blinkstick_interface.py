"""
A class to control USB led light inside doorbot
"""

from blinkstick import blinkstick

class BlinkstickInterface:
    def __init__(self) -> None:
        """Sets up blinkstick"""
        self.stick = blinkstick.find_first()

    def set_white(self):
        if self.stick is not None:
            self.stick.set_color(name='white')

    def set_colour_name(self, colour_name):
        """
        Set colour by W3 CSS name
        https://www.w3.org/TR/css-color-3/
        """
        if self.stick is not None:
            self.stick.set_color(name=colour_name)

    def set_colour_rgb(self, red, green, blue):
        if self.stick is not None:
            self.stick.set_color(red=red, green=green, blue=blue)

