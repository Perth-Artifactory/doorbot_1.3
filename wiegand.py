#!/usr/bin/env python

import pigpio

class decoder:

   """
   A class to read Wiegand codes of an arbitrary length.

   The code length and value are returned.

   EXAMPLE

   #!/usr/bin/env python

   import time

   import pigpio

   import wiegand

   def callback(bits, code):
      print("bits={} code={}".format(bits, code))

   pi = pigpio.pi()

   w = wiegand.decoder(pi, 14, 15, callback)

   time.sleep(300)

   w.cancel()

   pi.stop()
   """

   def __init__(self, pi, gpio_0, gpio_1, callback, bit_timeout=5):

      """
      Instantiate with the pi, gpio for 0 (green wire), the gpio for 1
      (white wire), the callback function, and the bit timeout in
      milliseconds which indicates the end of a code.

      The callback is passed the code length in bits and the value.
      """

      self.pi = pi
      self.gpio_0 = gpio_0
      self.gpio_1 = gpio_1

      self.callback = callback

      self.bit_timeout = bit_timeout

      self.in_code = False

      self.pi.set_mode(gpio_0, pigpio.INPUT)
      self.pi.set_mode(gpio_1, pigpio.INPUT)

      self.pi.set_pull_up_down(gpio_0, pigpio.PUD_UP)
      self.pi.set_pull_up_down(gpio_1, pigpio.PUD_UP)

      self.cb_0 = self.pi.callback(gpio_0, pigpio.FALLING_EDGE, self._cb)
      self.cb_1 = self.pi.callback(gpio_1, pigpio.FALLING_EDGE, self._cb)

   def _cb(self, gpio, level, tick):

      """
      Accumulate bits until both gpios 0 and 1 timeout.
      """

      if level < pigpio.TIMEOUT:
         gpio_s = {True: 'gpio_0', False: 'gpio_1'}[gpio == self.gpio_0]
         # print(f"{gpio_s=}, {level=}, {tick=} us", end="")

         if self.in_code == False:
            self.bits = 1
            self.num = 0

            self.in_code = True
            self.code_timeout = 0
            self.pi.set_watchdog(self.gpio_0, self.bit_timeout)
            self.pi.set_watchdog(self.gpio_1, self.bit_timeout)

            # print()
            self.last_tick = tick
         else:
            self.bits += 1
            self.num = self.num << 1

            # print(f", Delta={tick - self.last_tick} us")
            self.last_tick = tick

         if gpio == self.gpio_0:
            self.code_timeout = self.code_timeout & 2 # clear gpio 0 timeout
         else:
            self.code_timeout = self.code_timeout & 1 # clear gpio 1 timeout
            self.num = self.num | 1

      else:

         if self.in_code:

            if gpio == self.gpio_0:
               self.code_timeout = self.code_timeout | 1 # timeout gpio 0
            else:
               self.code_timeout = self.code_timeout | 2 # timeout gpio 1

            if self.code_timeout == 3: # both gpios timed out
               self.pi.set_watchdog(self.gpio_0, 0)
               self.pi.set_watchdog(self.gpio_1, 0)
               self.in_code = False
               self.callback(self.bits, self.num)

   def cancel(self):

      """
      Cancel the Wiegand decoder.
      """

      self.cb_0.cancel()
      self.cb_1.cancel()

if __name__ == "__main__":

   import time

   import pigpio

   import wiegand

   def callback(bits, value):
      if bits == 26:
         # Parity checking from here:
         # https://github.com/paulo-raca/YetAnotherArduinoWiegandLibrary/blob/master/src/Wiegand.cpp

         # The trailing half of the bits are odd parity (including parity bit).
         # Trailing half is what arrives last - the low bits.
         count_trailing = 0
         for i in range(0, bits//2):
            if (value >> i) & 0x01 == 0x01:
               count_trailing += 1
         trailing_parity_odd = (count_trailing % 2 == 1)

         # Leading half is even parity (high bits)
         count_leading = 0
         for i in range(bits//2, bits):
            if (value >> i) & 0x01 == 0x01:
               count_leading += 1
         leading_parity_even = (count_leading % 2 == 0)

         if trailing_parity_odd and leading_parity_even:
            # Extract the card value from inner 24-bits (drop first and last parity bits)
            card_id = (value >> 1) & (2**(bits-2)-1)
            print(f"VALID CARD ({bits-2}): {card_id}, 0x{card_id:0X}")
         else:
            print(f"ERROR: Invalid Parity - dec {value}, 0x{value:0X}, {count_trailing=} ({trailing_parity_odd=}), {count_leading=} ({leading_parity_even=})")
         
      else:
         print("bits={} value={}".format(bits, value))

   pi = pigpio.pi()

   w_rfid = wiegand.decoder(pi, 5, 6, callback)

   w_nfc = wiegand.decoder(pi, 12, 13, callback)

   time.sleep(300)

   w_rfid.cancel()
   w_nfc.cancel()

   pi.stop()
