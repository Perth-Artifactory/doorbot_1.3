"""
The old Arduino based RFID reader would give hex values which don't
match the number printed on the side of keys, nor what USB RFID reader
reads. This script converts those hex values to the normal representation.

All it does is drop the first 1 bytes (2 digits in hex).
"""
import os
import argparse
import json


def old_door_pi_hex_str_to_rfid(hex_str: str) -> int:
    """
    Converts the hex string from old doorpi arduino to the
    decimal string printed on keyfobs and also what USB RFID 
    receiver outputs.
    """
    # Chop off the first 2 hex chars (1 bytes). They don't
    # appear in the hex conversion of the decimal value written
    # on keyfobs and output from USB RFID reader.
    # USB RFID Reader gives 4 bytes where as keys actually have 5 bytes on them.
    hex_str = hex_str[2:]
    tag = int(hex_str, 16)
    # Zero pad out to a 10 digit decimal number
    return f"{tag:0>10}"

def convert(path, out):
    with open(path) as f:
        j = json.load(f)

    new = {}
    for key in j:
        # Convert
        tag_id = old_door_pi_hex_str_to_rfid(key)
        # Put the same block with "door, groups, name" below new key id
        new[tag_id] = j[key]

    with open(out, "w") as f:
        json.dump(new, f, indent=4)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Path to keys json to convert")
    parser.add_argument("out", help="Path to write converted json")
    args = parser.parse_args()

    convert(args.path, args.out)


if __name__ == "__main__":
    main()
