import time
import serial
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
 
Tag1 = str('0000000C000C')
Tag2 = str('0000000C080C')
Tag3 = str('0000000C010C')
Tag4 = str('0000000C090C')
Tag5 = str('0000000C0A0C')
Tag6 = str('0000000C0D0C')
GPIO.setup(23,GPIO.OUT)
GPIO.setup(24,GPIO.OUT)
GPIO.output(23,False)
GPIO.output(24,False)
PortRF = serial.Serial('/dev/serial0',9600)
#PortRF.reset_input_buffer()
PortRF.flushInput()
while True:
    ID = ""
    read_byte = PortRF.read()
    if read_byte=="\x02":
        for Counter in range(12):
            read_byte=PortRF.read()
            ID = ID + str(read_byte)
            print hex(ord( read_byte))
        print ID
        if ID == Tag1:
            print "White - Ashoka"
            GPIO.output(23,True)
            GPIO.output(24,False)
            #PortRF.reset_input_buffer()
            PortRF.flushInput()
            time.sleep(5)
            GPIO.output(23,False)
        else:
            GPIO.output(23,False)
            print "Access Denied"
            GPIO.output(24,True)
            #PortRF.reset_input_buffer()
            PortRF.flushInput()
            time.sleep(5)
            GPIO.output(24,False)
