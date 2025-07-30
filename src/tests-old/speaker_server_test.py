import base64
import requests
import json

# Setup your basic authentication details
USERNAME = 'user'
PASSWORD = 'password'
AUTH = (USERNAME, PASSWORD)

# Setup your server address
BASE_URL = 'http://localhost:5000'


def call_speak(text):
    data = {'text': text}
    response = requests.post(f'{BASE_URL}/speak', auth=AUTH, json=data)
    return response.json()


def call_play_mp3_base64(file_path):
    with open(file_path, 'rb') as f:
        data = base64.b64encode(f.read()).decode('utf-8')

    payload = {'base64_mp3': data}
    response = requests.post(f'{BASE_URL}/play_mp3_base64', auth=AUTH, json=payload)
    return response.json()


# Test calling the endpoints
if __name__ == "__main__":
    # Call the /speak endpoint
    print(call_speak("Hello, this is a test!"))

    # Call the /play_mp3_base64 endpoint
    print(call_play_mp3_base64("sounds/denied.mp3"))

    # Call the /play_mp3_base64 endpoint
    print(call_play_mp3_base64("sounds/granted.mp3"))

    # Call the /play_mp3_base64 endpoint
    print(call_play_mp3_base64("sounds/granted.mp3"))
