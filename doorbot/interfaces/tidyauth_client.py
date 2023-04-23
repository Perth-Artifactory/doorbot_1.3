"""
Connect to tidy auth API and download keys and unlock sound info
"""

import requests
import logging
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)

class TidyAuthClient:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.token = token

    def test_route(self):
        params = {"token": self.token}
        try:
            response = requests.get(f"{self.base_url}/", params=params)
            if response.status_code == 200:
                logger.debug("Valid token")
                return True
            elif response.status_code == 401:
                logger.debug("Invalid token")
                return False
            else:
                logger.debug(f"Unexpected response: {response.status_code}")
                return False
        except RequestException as e:
            logger.error(f"RequestException: {e}")
            return False

    def get_door_keys(self):
        update_source = "tidyhq"
        params = {"token": self.token, "update": update_source}
        try:
            response = requests.get(f"{self.base_url}/api/v1/keys/door", params=params)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            logger.error(f"RequestException: {e}")
        except ValueError as e:
            logger.error(f"JSONDecodeError: {e}")
        return None

    def get_sound_data(self, tidyhq_id):
        params = {"token": self.token, "tidyhq_id": tidyhq_id}
        try:
            response = requests.get(f"{self.base_url}/api/v1/data/sound", params=params)
            # Gives 401 if user doesn"t have any sound, don"t raise_for_status.
            # The contents differentiates it
            return response.json()
        except RequestException as e:
            logger.error(f"RequestException: {e}")
        except ValueError as e:
            logger.error(f"JSONDecodeError: {e}")
        return None
