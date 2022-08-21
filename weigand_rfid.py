#!/usr/bin/python3
from  pywiegand import WiegandReader


# Weigand RFID Reader Pins (Using RPi GPIO/BCM mapping)
PIN_D0 = 5
PIN_D1 = 6


class WeigandRfid:
    def __init__(self) -> None:
        """Connect to Weigand RFID reader and receive tags when calling 'read()'."""
        self.log("Initialising scanner...")
        self.reader = WiegandReader(PIN_D0, PIN_D1)

    def log(self, message: str):
        print("[WeigandRfid] {}".format(message))

    def read(self) -> int:
        """
        Tries to read a tag and returns it and returns 0 if no tag found since last read.
        Converts from Weigand format into the int printed on side of tag (and what USB RFID
        reader reads tag as).
        """
        scan = self.reader.read()
        if type(scan) is str:
            # We have read a tag rather than got an empty list (or list of key presses)
            tag_id = self.weigand_to_rfid(int(scan))
            self.log("Read tag '{}' (raw data was: '{}')".format(tag_id, scan))
            return tag_id
        return 0

    def weigand_to_rfid(val: int) -> int:
        """
        Converts the decimal string from weigand RFID receiver to the
        decimal string printed on keyfobs and also what USB RFID receiver
        outputs.
        """
        # Remove top bit - doesn't seem to be used
        bits = 31
        top = val >> bits
        top = top << bits
        result = val - top

        # Shift down by 7 - this aligns it correctly and cuts lower bits
        result = result >> 7

        # Extract bit 1 (2nd bit) which is used as bit 0 in final
        result = result + ((val & 0b10) >> 1)

        return result

