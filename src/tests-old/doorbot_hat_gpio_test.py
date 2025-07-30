import time
import pigpio
from src.interfaces import doorbot_hat_gpio

def main():
    pi = pigpio.pi()

    # time.sleep(1)
    door_channel = "R1"
    hat = doorbot_hat_gpio.DoorbotHatGpio(pigpio_pi=pi)
    hat.set_relay(door_channel, True)
    time.sleep(1)
    hat.set_relay(door_channel, False)
    time.sleep(1)

    while True:
        print(hat.read_switches())
        time.sleep(0.1)


if __name__ == "__main__":
    main()

