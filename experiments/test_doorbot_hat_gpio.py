import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(19, GPIO.OUT)
# GPIO.output(19, False)


# import sys
# sys.path.append('..')
# sys.path.append('.')
# import doorbot_hat_gpio
# hat_gpio = doorbot_hat_gpio.DoorbotHatGpio()
# hat_gpio.set_relay(config.relay_channel, True)

try:
    while True:
        pass
except KeyboardInterrupt:
    GPIO.cleanup()
    print('done')
