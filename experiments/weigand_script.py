#!/usr/bin/python3
from  pywiegand import WiegandReader
import time

users = []

print("Initialising scanner...")
reader = WiegandReader(5,6)

def converter(weigand):
    A = 30
    top = weigand >> A
    top = top << A
    cut = weigand - top
    cut = cut >> 7
    cut += 1
    return cut

# def unlock():
#     # print("Unlocking door")

# def sound(s):
#     # print("Playing: {}.mp3".format(s))

while True:
    # input("Press enter to scan buffer: ")
    # input()
    scan = ""
    scan = reader.read()

    try:
        key = converter(int(scan))
        # print(f"key = {key}, 0x{key:X}")
        print(f"{scan},{key:0>10},,,")
        # print(f"{key}")
    except TypeError:
        pass

    time.sleep(0.1)

    # print("data: {}".format(scan))
    # if scan:
    #     if scan in users:
    #         unlock()
    #         sound("granted")
    #     else:
    #         sound("denied")