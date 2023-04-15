"""
Connect to tidy auth API and download keys and unlock sound info
"""

import requests

class DoorKeysClient:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.token = token

    def test_route(self):
        params = {'token': self.token}
        response = requests.get(f'{self.base_url}/', params=params)
        if response.status_code == 200:
            print("Valid token")
            return True
        elif response.status_code == 401:
            print("Invalid token")
            return False
        else:
            print(f"Unexpected response: {response.status_code}")
            return False

    def get_door_keys(self):
        update_source = 'tidyhq'
        params = {'token': self.token, 'update': update_source}
        response = requests.get(f'{self.base_url}/api/v1/keys/door', params=params)
        return response.json()

    def get_sound_data(self, tidyhq_id):
        params = {'token': self.token, 'tidyhq_id': tidyhq_id}
        response = requests.get(f'{self.base_url}/api/v1/data/sound', params=params)
        return response.json()
