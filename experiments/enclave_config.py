"""
EnclaveConfig is responsible for interfacing with Enclave server to
retrieve config and cache it locally.

Author: Blake 2021
Compatibility: Python3
"""
from requests.auth import HTTPBasicAuth
import json
from updating_config_loader import UpdatingConfigLoader

class EnclaveConfig:
    def __init__(self, config):
        self.config = config

        # Setup auth if needed
        if self.config["auth"]["enabled"]:
            with open(self.config["auth"]["path"]) as f:
                self.auth_config = json.load(f)
            auth_user = self.auth_config["enclave_http_username"]
            auth_pass = self.auth_config["enclave_http_password"]
            self.auth = HTTPBasicAuth(auth_user, auth_pass)
        else:
            self.auth_config = None
            self.auth = None

        self.enclave_config = UpdatingConfigLoader(
            local_path=self.config["config"]["local"], 
            remote_url=self.config["config"]["remote"],
            auth=self.auth)
        self.enclave_keys = UpdatingConfigLoader(
            local_path=self.config["keys"]["local"], 
            remote_url=self.config["keys"]["remote"],
            auth=self.auth)
