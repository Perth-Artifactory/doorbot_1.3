import asyncio
import argparse
from src.interfaces.tidyauth_client import TidyAuthClient
from src.interfaces.user_manager import UserManager

import logging
logging.basicConfig(level=logging.DEBUG)


# Usage
cache_path = "user_cache.json"

parser = argparse.ArgumentParser()
parser.add_argument("token")
parser.add_argument("key_to_play")
args = parser.parse_args()

# Usage
# base_url = "http://enclave:5000"  # At Artifactory
base_url = "http://localhost:1338"  # At home via tsh
token = args.token

client = TidyAuthClient(base_url, token)

async def main():
    user_manager = UserManager(api_client=client, cache_path=cache_path)

    print("Initial key loading")
    keys_changed = await user_manager.download_keys()
    print(f"{keys_changed=}")

    authed = user_manager.is_key_authorised(args.key_to_play)
    print(f"User is authed = {authed}")

    user = user_manager.get_user_details(args.key_to_play)
    print(f"User details = {user}")

    authed = user_manager.is_key_authorised("123")
    print(f"User is authed = {authed}")

    print("Updating keys")
    keys_changed = await user_manager.download_keys()
    print(f"{keys_changed=}")

asyncio.run(main())
