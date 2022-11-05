"""
Class to read both RFID and NFC keys using Doorbot 1.3 hat.

Since the callback is probably coming from another thread, the keys and any error messages
are stored in global lists. The main application can read these out whenever convenient.
"""

import pigpio
import wiegand

# The callback adds keys to this list. So check here for new key reads.
pending_keys = []

# 
pending_errors = []

def callback(bits, value, reader_type):
    """Called when a wiegand string is read"""
    if bits == 26:
        # 26-bits is the 24-bit wiegand data with parity. Its the most widely supported format.

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
            pending_keys.append(card_id)
        else:
            msg = f"ERROR ({reader_type=}): Invalid Parity - {value} (0x{value:0X})"
            pending_errors.append(msg)

    else:
        msg = f"ERROR ({reader_type=}): Unexpected Number Bits - {bits=}, {value=} (0x{value:0X})"
        pending_errors.append(msg)

def callback_rfid(bits, value):
    callback(bits, value, "RFID")

def callback_nfc(bits, value):
    callback(bits, value, "NFC")

class KeyReader:
    def __init__(self):
        """Sets up decoders for RFID and NFC. When keys are read, callback will be called."""
        self.pi = pigpio.pi()
        self.w_rfid = wiegand.decoder(self.pi, 5, 6, callback_rfid)
        self.w_nfc = wiegand.decoder(self.pi, 12, 13, callback_nfc)

    def __del__(self):
        self.w_rfid.cancel()
        self.w_nfc.cancel()
        self.pi.stop()



