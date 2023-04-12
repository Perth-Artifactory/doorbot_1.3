import time
import pigpio

pi = pigpio.pi()

time.sleep(1.0)
pi.write(19, 0)

time.sleep(1.0)
pi.write(19, 1)

time.sleep(5.0)
pi.stop()
