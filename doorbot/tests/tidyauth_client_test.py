
import argparse
from doorbot.interfaces.tidyauth_client import TidyAuthClient

import logging
logging.basicConfig(level=logging.DEBUG)

parser = argparse.ArgumentParser()
parser.add_argument('token')
parser.add_argument('tidyhq_id')
args = parser.parse_args()

# Usage
# base_url = "http://enclave:5000"  # At Artifactory
base_url = "http://localhost:1338"  # At home via tsh
token = args.token

client = TidyAuthClient(base_url, token)

# Test the route
print(f"Test Route = {client.test_route()}")

# Get door keys from tidyhq
door_keys = client.get_door_keys()
print(door_keys)

# Get sound data for a specific TidyHQ contact ID
sound_data = client.get_sound_data(tidyhq_id=args.tidyhq_id)
print(sound_data)

