"""
Separate file for blockkit blocks because they are huge and make code
hard to follow.
"""

# The Slack Home Tab
home_view = {
    "type": "home",
    "callback_id": "home_view",

    # body of the view
    "blocks":
    [
        {
            "type": "actions",
            "elements":
            [
                {
                    "type": "static_select",
                    "placeholder":
                    {
                        "type": "plain_text",
                        "text": "Select a message to send",
                        "emoji": True
                    },
                    "options":
                    [
                        {
                            "text":
                            {
                                "type": "plain_text",
                                "text": "Your key has been disabled",
                                "emoji": True
                            },
                            "value": "key_disabled"
                        },
                        {
                            "text":
                            {
                                "type": "plain_text",
                                "text": "A volunteer will contact you shortly",
                                "emoji": True
                            },
                            "value": "volunteer_contact"
                        },
                        {
                            "text":
                            {
                                "type": "plain_text",
                                "text": "COVID shutdown notice",
                                "emoji": True
                            },
                            "value": "covid"
                        },
                        {
                            "text":
                            {
                                "type": "plain_text",
                                "text": "I know you're there",
                                "emoji": True
                            },
                            "value": "notice_you"
                        }
                    ],
                    "action_id": "sendMessage"
                }
            ]
        },
        {
            "dispatch_action": True,
            "type": "input",
            "element": {
                "type": "plain_text_input",
                "action_id": "ttsMessage"
            },
            "label": {
                "type": "plain_text",
                "text": "Send a custom message via text-to-speech",
                "emoji": True
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Manually unlock the door, a sound notification will be played automatically"
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Unlock for 30 seconds",
                    "emoji": True
                },
                "value": "30",
                "action_id": "unlock"
            }
        }
    ]
}

# Message posted when door access is being reported


def door_access(name, tag, status, level):
    return [
        {
            "type": "section",
            "text": 
            {
                "type": "plain_text",
                "text": "Someone interacted with the door",
                "emoji": True
            }
        },
        {
            "type": "section",
            "fields": 
            [
                {
                    "type": "mrkdwn",
                    "text": f"*Name:*\n{name}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*RFID:*\n{tag}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Status:*\n{status}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Level:*\n{level}"
                }
            ]
        }
    ]
