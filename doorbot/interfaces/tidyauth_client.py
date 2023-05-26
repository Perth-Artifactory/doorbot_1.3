"""
Connect to tidy auth API and download keys and unlock sound info
"""
import logging
import aiohttp
from aiohttp import ClientSession, ClientResponseError, ClientConnectionError
from asyncio.exceptions import TimeoutError

logger = logging.getLogger(__name__)

class TidyAuthClient:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.token = token

    async def test_route(self):
        params = {"token": self.token}
        try:
            timeout = aiohttp.ClientTimeout(total=60)
            async with ClientSession(timeout=timeout) as session:
                async with session.get(f"{self.base_url}/", params=params) as response:
                    if response.status == 200:
                        logger.debug("test_route - Valid token")
                        return True
                    elif response.status == 401:
                        logger.debug("test_route - Invalid token")
                    else:
                        logger.debug(f"test_route - Unexpected response: {response.status}")
        except ClientResponseError as e:
            logger.error(f"test_route - ClientResponseError: {e}")
        except ClientConnectionError as e:
            logger.error(f"test_route - ClientConnectionError: Could not connect to server: {e}")
        except TimeoutError as e:
            logger.error(f"test_route - TimeoutError: {e}")
        except Exception as e:
            logger.error(f"test_route - Unexpected error: {e}")
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
            logger.error(f"get_door_keys - ClientResponseError: {e}")
        except ValueError as e:
            logger.error(f"get_door_keys - JSONDecodeError: {e}")
        except ClientConnectionError as e:
            logger.error(f"get_door_keys - ClientConnectionError: Could not connect to server: {e}")
        except TimeoutError as e:
            logger.error(f"get_door_keys - TimeoutError: {e}")
        except Exception as e:
            logger.error(f"get_door_keys - Unexpected error: {e}")
        return None

    async def zc(self, tidyhq_id):
        params = {"token": self.token, "tidyhq_id": tidyhq_id}
        try:
            async with ClientSession() as session:
                async with session.get(f"{self.base_url}/api/v1/data/sound", params=params) as response:
                    # Gives 401 if user doesn"t have any sound, don"t raise_for_status.
                    # The contents differentiates it
                    return await response.json()
        except ClientResponseError as e:
            logger.error(f"get_sound_data - ClientResponseError: {e}")
        except ValueError as e:
            logger.error(f"get_sound_data - JSONDecodeError: {e}")
        except ClientConnectionError as e:
            logger.error(f"get_door_keys - ClientConnectionError: Could not connect to server: {e}")
        except TimeoutError as e:
            logger.error(f"get_door_keys - TimeoutError: {e}")
        except Exception as e:
            logger.error(f"get_door_keys - Unexpected error: {e}")
        return None
