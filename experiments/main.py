#!/usr/bin/python3
import json
from enclave_config import EnclaveConfig
from doorbot_hat_interface import DoorbotHatInterface
from 

class Doorbot:
    def __init__(self, config_path):
        # Load config
        with open(config_path) as f:
            self.config = json.load(f)

        # Init enclave config
        
        # Init Doorbot Hat Interface
        # Init RFID reader
        # Init slack interface
        # Init audio interface
        pass

    def run(self):
        while True:
            # Check inputs
            # Callback handlers process events
            pass


def main():



    # load config

    config,keys,good_members,members = load_config()

    # initiate slack client

    slack = SlackClient(config["slack"]["token"])

    # initiate serial connection

    s = relay_init()

    # turn on relay

    time.sleep(5)
    s.write('B'.encode())

    notify(door_activity=False,status="{} has started".format(config["name"]))

    # begin listening for RFID

    while True:
        try:
            while s.inWaiting() > 0:
                data = s.readline().decode()
                if "RFID" in data:
                    card = data[-11:-1]
                    print("data: "+data)
                    if card in good_members:
                        notify(door_activity=False,status="{} ({}) unlocked the door.".format(keys[card]["name"],card))
                        if "csound" in keys[card]["groups"]:
                            speaker(random.choice(keys[card]["sound"]))
                        else:    
                            speaker("granted")
                        if len(keys[card]["groups"]) > 0:
                            for x in keys[card]["groups"]:
                                notify(door_activity=False,status=x)
                        if "delayed" in keys[card]["groups"]:
                            unlock_door(s,30)
                        else:
                            unlock_door(s)
                        notify(door_activity=True,status="Unlocked",id=card,name=keys[card]["name"],level=keys[card]["door"])
                    elif card in members:
                        #keys[card]["name"],card
                        if keys[card]["door"] > 5:
                            speaker("covid")
                        else:
                            speaker("denied")
                        notify(door_activity=True,id=card,name=keys[card]["name"],status="Known but blocked",level=keys[card]["door"])
                        notify(door_activity=False,status="{} ({}) attempted to unlock the door but was denied because they are not part of the door group or they do not have a high enough level.".format(keys[card]["name"],card))
                    else:
                        speaker("denied")
                        notify(door_activity=True,id=card,name="Unknown",status="An unknown card was used, new cards can be added via TidyHQ")
                        notify(door_activity=False,status="Someone attempted to use an unknown key to open the door. Tag ID: {}".format(card))
                    #Reload user list
                        config,keys,good_members,members = load_config()
        except (SystemExit, KeyboardInterrupt):
            notify(door_activity=False,status="{} is shutting down.".format(config["name"]))
            break

if __name__ == "__main__":
    main()
