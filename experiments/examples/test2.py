import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

relay_pins = [19, 20, 21, 22]
input_pins = [23, 24, 25, 26]

for pin in relay_pins:
	GPIO.setup(pin, GPIO.OUT)

for pin in input_pins:
	GPIO.setup(pin, GPIO.IN)

val2 = False
while True:
	try:
		for pin_in, pin_out in zip(input_pins, relay_pins):
			val = GPIO.input(pin_in)
			print("pin_in = {}, val = {}".format(pin_in, val))
		GPIO.output(relay_pins[0], val2)
		val2 = not val2
		time.sleep(1)
	except KeyboardInterrupt:
		break

GPIO.cleanup()

