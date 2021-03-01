"""
Interface to tag reader

Author: Tazard, 2021
Compatibility: Python3
"""

import serial
import time

class TagReaderInterface:
    START_BYTE = 0x02
    END_BYTE = 0x03
    PAYLOAD_LENGTH = 12
    TAG_LENGTH = 10

    def __init__(self, config, on_tag_received_callback=None):
        """Listens for tags being sent by RDM6300 over serial"""
        self.config = config
        ser_node = self.config["serial"]
        # Run serial in non-blocking mode (timeout=0)
        self.serial = serial.Serial(ser_node["address"], ser_node["baud"], timeout=0)

        self.on_tag_received_callback = on_tag_received_callback

        self.last_read_time = 0
        self.tag_read_cooldown_s = 5

        self.reading_tag = None
        self.read_buffer = None
        self.reset()

    def reset(self):
        self.reading_tag = False
        self.read_buffer = bytes()

    def log(self, message):
        print("[TagReaderInterface] {}".format(message))

    def check(self):
        """Parses serial for new tag, returns tag string or else None"""
        data = self.read_next()

        if time.monotonic() - self.last_read_time < self.tag_read_cooldown_s:
            # Ignore serial data until at least cooldown time has elapsed
            return

        if not self.reading_tag:
            if self.matches(data, self.START_BYTE):
                # We have found the start of a tag
                self.reading_tag = True
            else:
                # Ignore all other bytes while not in "reading_tag" mode
                pass
        else:
            # We are expecting tag data
            if self.matches(data, self.END_BYTE):
                # We have found end of tag, process what we have
                self.process_tag()
            else:
                # Add the received data to the read buffer as bytes
                self.read_buffer += data
                
                if len(self.read_buffer) > self.PAYLOAD_LENGTH:
                    # We have exceeded the expected payload length without an END_BYTE
                    self.process_tag()

    def read_next(self):
        """Reads the next character from serial"""
        data = self.serial.read(size=1)
        # if data is not None and len(data) > 0:
        #     self.log("read - {}".format(data))
        return data

    def matches(self, data, value):
        """Checks if a bytes array "data" has binary "value" as first element"""
        if data is None or len(data) == 0:
            return False
        else:
            return data[0] == value

    def process_tag(self):
        """Process the bytes stored in "read_buffer" to see if there is a valid tag"""
        # Clear reading tag flag
        self.reading_tag = False

        if len(self.read_buffer) != self.PAYLOAD_LENGTH:
            s = "Invalid payload length ({} bytes). Received: {}"
            self.log(s.format(len(self.read_buffer), self.read_buffer))
            self.reset()
            return

        # Parse "tag" part bytes buffer as hex number
        # TODO: Error checking
        tag = self.read_buffer[:self.TAG_LENGTH].decode()
        tag = int(tag, base=16)

        # self.log("Potential tag: '{:X}'".format(tag))

        # Parse "checksum" part bytes buffer as hex number
        # TODO: Error checking
        checksum = self.read_buffer[self.TAG_LENGTH:].decode()
        checksum = int(checksum, base=16)

        # self.log("Checksum: '{:X}'".format(checksum))

        # Do checksum
        # Based on checksum code here: https://github.com/arduino12/rdm6300
        for i in range(0, 32+1, 8):
            # self.log("Checksum i {}: val = {:X}, checksum = {:X}".format(i, ((tag >> i) & 0xFF), checksum))
            checksum ^= ((tag >> i) & 0xFF)
        if checksum != 0:
            # Checksum should xor to zero
            self.log("Invalid checksum. Result = {}".format(checksum))
            self.reset()
            return

        # Tag is valid, do callback
        self.reset()
        self.last_read_time = time.monotonic()
        self.log("Valid tag = hex {0:X} (decimal {0})".format(tag))
        self.on_tag_received_callback(tag)




