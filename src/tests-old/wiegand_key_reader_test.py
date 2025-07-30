import time
import pigpio
from src.interfaces import wiegand_key_reader

reader = wiegand_key_reader.KeyReader(pigpio.pi())

while True:
    while len(reader.pending_keys) > 0:
        key = reader.pending_keys.pop(0)
        print(f"Read a key: {key}")

    while len(reader.pending_errors) > 0:
        msg = reader.pending_errors.pop(0)
        print("Gave an error:  " + str(msg))

    time.sleep(0.1)

