#!/usr/bin/env python

# trivial script to convert numeric card/fob numbers to hex
# Andrew Elwell <Andrew.Elwell@gmail.com>

card_dec = str(input('Please Enter Decimal (printed) card/fob number without leading zeros: '))
if (card_dec[:2] == '31' or card_dec[:2] == '34'):
    print 'CARD: 6F{:08X}'.format(int(card_dec))
elif card_dec[:2] == '33':
    print 'FOB: 28{:08X}'.format(int(card_dec))
else:
    print 'UNKNOWN: ??{:08X}'.format(int(card_dec))
