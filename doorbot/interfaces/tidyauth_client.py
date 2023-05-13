"""
Connect to tidy auth API and download keys and unlock sound info
"""
import aiohttp
import logging
from aiohttp import ClientSession, ClientResponseError

logger = logging.getLogger(__name__)

class TidyAuthClient:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.token = token

    async def test_route(self):
        params = {"token": self.token}
        try:
            async with ClientSession() as session:
                async with session.get(f"{self.base_url}/", params=params) as response:
                    if response.status == 200:
                        logger.debug("Valid token")
                        return True
                    elif response.status == 401:
                        logger.debug("Invalid token")
                        return False
                    else:
                        logger.debug(f"Unexpected response: {response.status}")
                        return False
        except ClientResponseError as e:
            logger.error(f"ClientResponseError: {e}")
            return False

    async def get_door_keys(self):
        update_source = "tidyhq"
        params = {"token": self.token, "update": update_source}
        try:
            async with ClientSession() as session:
                async with session.get(f"{self.base_url}/api/v1/keys/door", params=params) as response:
                    response.raise_for_status()
                    return await response.json()
        except ClientResponseError as e:
            logger.error(f"ClientResponseError: {e}")
        except ValueError as e:
            logger.error(f"JSONDecodeError: {e}")
        return None

    async def get_sound_data(self, tidyhq_id):
        params = {"token": self.token, "tidyhq_id": tidyhq_id}
        try:
            async with ClientSession() as session:
                async with session.get(f"{self.base_url}/api/v1/data/sound", params=params) as response:
                    # Gives 401 if user doesn"t have any sound, don"t raise_for_status.
                    # The contents differentiates it
                    return await response.json()
        except ClientResponseError as e:
            logger.error(f"ClientResponseError: {e}")
        except ValueError as e:
            logger.error(f"JSONDecodeError: {e}")
        return None
