import time
from doorbot.interfaces import wiegand_key_reader

reader = wiegand_key_reader.KeyReader()

while True:
    while len(wiegand_key_reader.pending_keys) > 0:
        key = wiegand_key_reader.pending_keys.pop(0)
        print(f"Read a key: {key}")

    while len(wiegand_key_reader.pending_errors) > 0:
        msg = wiegand_key_reader.pending_errors.pop(0)
        print("Gave an error:  " + str(msg))

    time.sleep(0.1)

