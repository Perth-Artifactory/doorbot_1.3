import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

relay_pins = [19, 20, 21, 22]
input_pins = [23, 24, 25, 26]

for pin in relay_pins:
	GPIO.setup(pin, GPIO.OUT)

for pin in input_pins:
	GPIO.setup(pin, GPIO.IN)

while True:
	try:
		for pin_in, pin_out in zip(input_pins, relay_pins):
			val = GPIO.input(pin_in)
			GPIO.output(pin_out, not val)
	except KeyboardInterrupt:
		break

GPIO.cleanup()

