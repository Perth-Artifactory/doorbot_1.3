# import sys
# Load the local source directly
# sys.path.insert(1, "./python-slack-sdk")


# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)


# Verify it works
from slack_sdk import WebClient
client = WebClient()
# api_response = client.api_test()
result = client.files_upload(r"/mnt/c/Users/tazar/Downloads/test.jpg")
print(result)
# https://join.slack.com/share/zt-noqe3u4y-Evm5CCKWkCr7RZFh6pjhEw