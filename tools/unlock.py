#!/usr/bin/env python
import sys
import time

import serial
serial = serial.Serial("/dev/ttyACM0", baudrate=9600)

t = 30
if len(sys.argv) > 1:
    t = int(sys.argv[1])
serial.write('A')
print "door unlocked for {} seconds".format(t)
time.sleep(t)
serial.write('a')
print "door locked"
