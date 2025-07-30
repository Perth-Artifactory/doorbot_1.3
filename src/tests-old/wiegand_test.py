"""
A standalone example using weigand class to read both RFID and NFC keys
using Doorbot 1.3 hat.
"""

import time
import pigpio
from src.interfaces import wiegand

if __name__ == "__main__":
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
