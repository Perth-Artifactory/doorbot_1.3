"""
ConfigManager is responsible for loading config from disk 
and network URLs.

Author: Blake 2021
Compatibility: Python3
"""

ENCLAVE_URL_CONFIG = 'https://enclave.guthrie.artifactory.org.au/door/config.json'
ENCLAVE_URL_KEYS = 'https://enclave.guthrie.artifactory.org.au/door/keys.json'
# HTTP Auth username/password stored in "config/auth_config.json".
# See "config/auth_config-example.json" for the format. Request current user/password
# from active maintainers of doorbot.

auth = HTTPBasicAuth(ENCLAVE_AUTH_USER, ENCLAVE_AUTH_PASS)


class ConfigManager:
    def __init__(self):
        pass