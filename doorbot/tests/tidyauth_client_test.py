
import argparse
from doorbot.interfaces.tidyauth_client import DoorKeysClient

parser = argparse.ArgumentParser()
parser.add_argument('token')
args = parser.parse_args()

# Usage
# base_url = "http://enclave:5000"  # At Artifactory
base_url = "http://localhost:1338"  # At home via tsh
token = args.token

client = DoorKeysClient(base_url, token)

# Test the route
client.test_route()

# Get door keys from tidyhq
door_keys = client.get_door_keys()
print(door_keys)

# Get sound data for a specific TidyHQ contact ID
sound_data = client.get_sound_data(tidyhq_id=1768863)  # No sound - B
print(sound_data)

# Get sound data for a specific TidyHQ contact ID
sound_data = client.get_sound_data(tidyhq_id=1952718)  # Has sound - F
print(sound_data)
