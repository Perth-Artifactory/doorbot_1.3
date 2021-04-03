"""
Tests for TagReaderInterface

Author: Tazard, 2021
Compatibility: Python3
"""
import time
import json
from tag_reader_interface import TagReaderInterface

TEST_CONFIG = "config/tag_reader_config.json"

def received_tag(tag):
    print("received tag - '{:X}'".format(tag))

def main():
    with open(TEST_CONFIG, 'r') as f:
        config = json.load(f)
    
    o = TagReaderInterface(config, on_tag_received_callback=received_tag)

    while True:
        o.check()
        time.sleep(0.001)


if __name__ == "__main__":
    main()
