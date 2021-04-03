# Enable debug logging
import logging
# logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.INFO)
# Verify it works
from slack import WebClient
client = WebClient()
api_response = client.api_test()
