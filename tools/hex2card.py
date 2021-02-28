#!/usr/bin/env python

# trivial script to convert RFID out to match numeric card string
# Andrew Elwell <Andrew.Elwell@gmail.com>
# 6F0030A7CD -> 0003188685

import sys
for card in sys.argv[1:]:
    print "Hex: %s Prefix: %d Id: %010d" % (card, int(card[:2],16), int(card[-8:],16))
