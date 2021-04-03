#!/usr/bin/python3

import serial
import json
import time
import sys
import os
import requests
import random
from requests.auth import HTTPBasicAuth
# from slackclient import SlackClient

ENCLAVE_URL_CONFIG = 'https://enclave.guthrie.artifactory.org.au/door/config.json'
ENCLAVE_URL_KEYS = 'https://enclave.guthrie.artifactory.org.au/door/keys.json'
# HTTP Auth username/password stored in "config/auth_config.json".
# See "config/auth_config-example.json" for the format. Request current user/password
# from active maintainers of doorbot.

auth = HTTPBasicAuth(ENCLAVE_AUTH_USER, ENCLAVE_AUTH_PASS)


def load_config():
    """Loads configuration from disk and checks for update from enclave"""

    config = requests.get('https://enclave.guthrie.artifactory.org.au/door/config.json', auth=HTTPBasicAuth('doorbot', 'Kn0ckKn0ck')).json()
    keys = requests.get('https://enclave.guthrie.artifactory.org.au/door/keys.json', auth=HTTPBasicAuth('doorbot', 'Kn0ckKn0ck')).json()
    active_members = []
    members = []
    for x in keys:
	# Number corresponds to access level. 0 = no access, 1 = standard key member, 3 = committee
        if keys[x]["door"] > 0:
            active_members.append(x)
        members.append(x)
    return (config,keys,active_members,members)


def relay_init():
    """Initialise relays using serial settings from config"""
    return serial.Serial(config["serial"]["pointer"], baudrate=config["serial"]["baudrate"])

def unlock_door(relays, t=5):
    """Unlock door for t seconds"""
    relays.write('A'.encode())
    time.sleep(t)
    relays.write('a'.encode())

def speaker(sound):
    """Play requested sound, if found in config."""
    if config["sounds"].get(sound, ''):
        os.system ("mpg123 -q {} &".format(config["sounds"][sound]))
    else:
        notify(door_activity=False,status="Nonexistent sound '{}' requested".format(sound))
        #Play default
        sound = "granted"
        os.system ("mpg123 -q {} &".format(config["sounds"][sound]))

def notify(door_activity=False,id=" ",name=" ",status=" ",level=1):
    if status == "Unlocked" and name == " ":
        name = "UNNAMED KEY, IDENTIFY USER"
    if door_activity:
        print("notifying slack")
        attachments = [{"fallback":"An image of the front door",
                          "image_url":"http://space.artifactory.org.au/foyer.gif"},
                       {"fallback":"An image of the carpark",
                          "image_url":"http://space.artifactory.org.au/carpark.gif",
                          "fields":[{"title":"Name",
                   "value":name,
                   "short":True},
                  {"title":"RFID",
                   "value":id,
                   "short":True},
                  {"title":"Status",
                   "value":status,
                   "short":True},
                  {"title":"Level",
                   "value":level,
                   "short":True}]}]
        try:
            slack.api_call("chat.postMessage",channel=config["slack"]["channel"],text="Someone interacted with the door",attachments=attachments)
        except:
            print("couldn't reach slack")
    else:
        print(status)

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
