import time
import os
from slack_sdk.web import WebClient
from slack_sdk.socket_mode import SocketModeClient


from slack_sdk.socket_mode.response import SocketModeResponse
from slack_sdk.socket_mode.request import SocketModeRequest

CHANNELS = {
    'doorbot-test-2': 'C01T0KF6LES',
    'doorbot-slack-test': 'C01QQJK62GP',
}

def format_blockkit_message(name, rfid, status, level):
    s = """
    [
		{
			"type": "section",
			"fields": [
				{
					"type": "mrkdwn",
					"text": "*Name:* Blake"
				},
				{
					"type": "mrkdwn",
					"text": "*RFID:* 23094ATSE20398"
				},
				{
					"type": "mrkdwn",
					"text": "*Status:* :white_check_mark: Door unlocked"
				},
				{
					"type": "mrkdwn",
					"text": "*Level:* 1"
				}
			]
		},
		{
			"type": "divider"
		}
	]"""
    s = s.replace("%NAME%", name)
    s = s.replace("%RFID%", rfid)
    s = s.replace("%STATUS%", status)
    s = s.replace("%LEVEL%", level)
    return s

def process(client: SocketModeClient, req: SocketModeRequest):
    print("new request")
    print(req.type)
    print(req)
    if req.type == "events_api":
        # Acknowledge the request anyway
        response = SocketModeResponse(envelope_id=req.envelope_id)
        client.send_socket_mode_response(response)

        # Add a reaction to the message if it's a new message
        print(req.payload["event"]["type"])
        print(req.payload)
        if req.payload["event"]["type"] == "message" \
            and req.payload["event"].get("subtype") is None:
            client.web_client.reactions_add(
                name="eyes",
                channel=req.payload["event"]["channel"],
                timestamp=req.payload["event"]["ts"],
            )

def setup():
    # Initialize SocketModeClient with an app-level token + WebClient
    client = SocketModeClient(
        # This app-level token will be used only for establishing a connection
        app_token=os.environ.get("SLACK_APP_TOKEN"),  # xapp-A111-222-xyz
        # You will be using this WebClient for performing Web API calls in listeners
        web_client=WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))  # xoxb-111-222-xyz
    )

    # Add a new listener to receive messages from Slack
    # You can add more listeners like this
    client.socket_mode_request_listeners.append(process)
    # Establish a WebSocket connection to the Socket Mode servers
    client.connect()
    
    return client

def main():
    socket_client = setup()
    client = socket_client.web_client

    # response = client.chat_postMessage(
    #         channel="C01QQJK62GP",
    #         text="Hello from your app! :tada:"
    #     )
    # print(response)

    # Just not to stop this process
    while True:
        print('send message')
        msg = format_blockkit_message(
                        name="Blake Superlongnamed Fullname", rfid="3874023SDT", 
                        status="Unlocked", level="1")
        print('sending: '+ msg)
        response = client.chat_postMessage(
                # channel=CHANNELS['doorbot-test-2'],
                channel="C01T0KF6LES",
                text="Backup message",
                blocks=msg
            )
        print(response)
        time.sleep(20)

if __name__ == "__main__":
    main()