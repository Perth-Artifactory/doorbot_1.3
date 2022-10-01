#!/usr/bin/python3
from  pywiegand import WiegandReader
import time

users = []

print("Initialising scanner...")
# reader = WiegandReader(5,6)  # RFID
reader = WiegandReader(12,13)  # NFC

while True:
    scan = ""
    scan = reader.read()

    if type(scan) is str:
        print("Scan: {}".format(scan))
        
    # try:
    #     if 
    #     key = converter(int(scan))
    #     # print(f"key = {key}, 0x{key:X}")
    #     print(f"{scan},{key:0>10},,,")
    #     # print(f"{key}")
    # except TypeError:
    #     pass

    time.sleep(0.1)

    # print("data: {}".format(scan))
    # if scan:
    #     if scan in users:
    #         unlock()
    #         sound("granted")
    #     else:
    #         sound("denied")