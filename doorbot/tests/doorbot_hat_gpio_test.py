import time
from doorbot.interfaces import doorbot_hat_gpio

def main():
    # time.sleep(1)
    door_channel = "R1"
    hat = doorbot_hat_gpio.DoorbotHatGpio()
    hat.set_relay(door_channel, True)
    time.sleep(1)
    hat.set_relay(door_channel, False)
    # time.sleep(1)

if __name__ == "__main__":
    main()

