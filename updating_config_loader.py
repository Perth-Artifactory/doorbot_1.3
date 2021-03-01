"""
Class to read a JSON config file from URL and cache in a local path.
"""
import json
import os
import requests

class UpdatingConfigLoader:
    def __init__(self, local_path, remote_url, auth=None):
        """A single file which is cached locally and updated from URL"""
        self.local_path = local_path
        self.remote_url = remote_url
        self.auth = auth
        self.contents = None

        self.load_from_file()
        self.update_from_url()
        self.check_valid()

    def log(self, msg):
        print("[UpdatingConfigLoader] {}".format(msg))

    def load_from_file(self):
        if os.path.exists(self.local_path):
            # Load file
            self.log("Loading file '{}'".format(self.local_path))
            with open(self.local_path, 'r') as f:
                file_str = f.read()

            # Convert to JSON
            try:
                self.contents = json.loads(file_str)
            except json.JSONDecodeError as e:
                self.log("Bad JSON file. Exception: {}. File: {}".format(self.local_path, e))
                print(file_str)
                self.contents = None
        else:
            self.log("No cached file '{}'".format(self.local_path))

    def update_from_url(self):
        # Load URL
        self.log("Loading URL '{}'".format(self.remote_url))
        remote = None
        try:
            response = requests.get(self.remote_url, auth=self.auth)
        except (ConnectionError, requests.RequestException) as e:
            s = "Error while loading '{}'. Exception: ({}) {}"
            self.log(s.format(self.remote_url, type(e), e))
            return
        
        # Convert to JSON
        try:
            remote = json.loads(response.text)
        except json.JSONDecodeError as e:
            s = "Bad JSON response. Exception: ({}) {}. Response: {}"
            self.log(s.format(type(e), e, response.text))
            print(remote)
            remote = None
            return

        # Check if local file needs updating (compare as strings for simplicity)
        if remote != self.contents:
            self.contents = remote
            self.log("Remote is different to local file, update local file")
            self.save_to_file()

    def save_to_file(self):
        self.log("Writing to {}".format(self.local_path))
        try:
            with open(self.local_path, 'w') as f:
                f.write(self.pretty_dump_json())
        except OSError as e:
            s = "Fatal Error - Invalid path for cache file '{}'. Exception: ({}) {}"
            self.log(s.format(self.local_path, type(e), e))
            raise
        
    def pretty_dump_json(self):
        return json.dumps(self.contents, sort_keys=False, indent=4)

    def check_valid(self):
        if self.contents is None:
            s = "Fatal Error - Failed to load correctly: '{}', '{}'"
            self.log(s.format(self.local_path, self.remote_url))
            raise Exception("Failed to load")
        
