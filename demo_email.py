"""
Twilio Email API demo — calls comms.twilio.com/v1/Emails directly via HTTP
Basic Auth (Account SID + Auth Token). 

Requires TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, FROM_ADDRESS in .env.

    python demo_email.py simple <email>
    python demo_email.py batch [recipients.txt]
    python demo_email.py status <operationId>
"""

import json
import os
import sys
import time

import requests
from dotenv import load_dotenv

load_dotenv()

EMAILS_URL = "https://comms.twilio.com/v1/Emails"
OPERATIONS_URL = "https://comms.twilio.com/v1/Emails/Operations/{operation_id}"

account_sid = os.environ["TWILIO_ACCOUNT_SID"]
auth_token = os.environ["TWILIO_AUTH_TOKEN"]
auth = (account_sid, auth_token)


def send_simple(to_address: str) -> dict:
    response = requests.post(
        EMAILS_URL,
        auth=auth,
        json={
            "from": {
                "address": os.environ["FROM_ADDRESS"],
                "name": "Twilio Email Demo",
            },
            "to": [{"address": to_address}],
            "content": {
                "subject": "Hello from Twilio Email",
                "html": "<h1>It works!</h1><p>Sent via <b>comms.twilio.com</b>.</p>",
                "text": "It works! Sent via comms.twilio.com.",
            },
        },
    )
    if response.status_code != 202:
        raise RuntimeError(f"Send failed ({response.status_code}): {response.text}")
    return response.json()


def load_recipients(path: str) -> list[dict]:
    """Read one email address per line from a file. Ignores blanks and `#` comments."""
    recipients = []
    with open(path) as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            recipients.append({"address": line})
    if not recipients:
        raise RuntimeError(f"No recipients found in {path}")
    return recipients


def send_batch(recipients_path: str = "recipients.txt") -> dict:
    recipients = load_recipients(recipients_path)
    print(f"Sending to {len(recipients)} recipient(s) from {recipients_path}")
    response = requests.post(
        EMAILS_URL,
        auth=auth,
        json={
            "from": {
                "address": os.environ["FROM_ADDRESS"],
                "name": "Twilio Email Demo",
            },
            "to": recipients,
            "content": {
                "subject": "Resources from Anni's Twilio Email API talk",
                "html": (
                    "<p>Hi, I'm Anni. Thank you for listening to my talk today.</p>"
                    "<p>Here are some resources to get you started:</p>"
                    "<p><b>Start here</b></p>"
                    "<ul>"
                    '<li><a href="https://www.twilio.com/try-twilio">'
                    "Sign up for a Twilio account</a></li>"
                    '<li><a href="https://github.com/kuroxx/twilio-email-python">'
                    "Explore the demo code on GitHub</a></li>"
                    "</ul>"
                    "<p><b>Learn the Twilio Email API</b></p>"
                    "<ul>"
                    '<li><a href="https://www.twilio.com/docs/email">'
                    "Twilio Email documentation</a></li>"
                    '<li><a href="https://www.twilio.com/docs/email/api/getting-started">'
                    "Send your first email</a></li>"
                    '<li><a href="https://www.twilio.com/docs/email/api/reference/mail-send-resource">'
                    "Email API reference</a></li>"
                    '<li><a href="https://www.twilio.com/docs/email/api/operations-and-email-tracking">'
                    "Track email operations and delivery</a></li>"
                    "</ul>"
                    "<p><b>Stay connected</b></p>"
                    "<ul>"
                    '<li><a href="https://luma.com/twilio-uk">'
                    "Twilio UK dev events on Luma</a></li>"
                    "</ul>"
                    "<p>Happy building!<br>Anni</p>"
                    '<p style="font-size:14px;">'
                    '<span style="color:#666;">Connect with me:</span> '
                    '<a href="https://www.linkedin.com/in/anni-in-tech/">LinkedIn</a> · '
                    '<a href="https://x.com/anni_in_tech">Twitter</a> · '
                    '<a href="https://www.instagram.com/anni_in_tech/">Instagram</a>'
                    "</p>"
                ),
                "text": (
                    "Hi, I'm Anni. Thank you for listening to my talk today.\n\n"
                    "Here are some resources to get you started:\n\n"
                    "START HERE\n"
                    "- Sign up for a Twilio account: https://www.twilio.com/try-twilio\n"
                    "- Explore the demo code on GitHub: "
                    "https://github.com/kuroxx/twilio-email-python\n\n"
                    "LEARN THE TWILIO EMAIL API\n"
                    "- Twilio Email documentation: https://www.twilio.com/docs/email\n"
                    "- Send your first email: "
                    "https://www.twilio.com/docs/email/api/getting-started\n"
                    "- Email API reference: "
                    "https://www.twilio.com/docs/email/api/reference/mail-send-resource\n"
                    "- Track email operations and delivery: "
                    "https://www.twilio.com/docs/email/api/operations-and-email-tracking\n\n"
                    "STAY CONNECTED\n"
                    "- Twilio UK dev events on Luma: https://luma.com/twilio-uk\n\n"
                    "Happy building!\nAnni\n\n"
                    "Connect with me:\n"
                    "- LinkedIn: https://www.linkedin.com/in/anni-in-tech/\n"
                    "- Twitter: https://x.com/anni_in_tech\n"
                    "- Instagram: https://www.instagram.com/anni_in_tech/\n"
                ),
            },
        },
    )
    if response.status_code != 202:
        raise RuntimeError(f"Send failed ({response.status_code}): {response.text}")
    return response.json()


def get_operation(operation_id: str) -> dict:
    response = requests.get(
        OPERATIONS_URL.format(operation_id=operation_id),
        auth=auth,
    )
    if response.status_code != 200:
        raise RuntimeError(f"Status check failed ({response.status_code}): {response.text}")
    return response.json()


def poll_until_done(operation_id: str, timeout_s: int = 30) -> dict:
    deadline = time.monotonic() + timeout_s
    while True:
        op = get_operation(operation_id)
        status = op.get("status")
        print(f"  status={status}")
        if status in {"completed", "failed"} or time.monotonic() > deadline:
            return op
        time.sleep(2)


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    if command == "simple":
        if len(sys.argv) < 3:
            print("Usage: python demo_email.py simple <email>")
            sys.exit(1)
        result = send_simple(sys.argv[2])
        print("Sent. Response:")
        print(json.dumps(result, indent=2))

    elif command == "batch":
        recipients_path = sys.argv[2] if len(sys.argv) > 2 else "recipients.txt"
        result = send_batch(recipients_path)
        print("Batch queued. Response:")
        print(json.dumps(result, indent=2))
        operation_id = result.get("operationId")
        if operation_id:
            print(f"\nPolling operation {operation_id}...")
            final = poll_until_done(operation_id)
            print("\nFinal operation state:")
            print(json.dumps(final, indent=2))

    elif command == "status":
        if len(sys.argv) < 3:
            print("Usage: python demo_email.py status <operationId>")
            sys.exit(1)
        result = get_operation(sys.argv[2])
        print(json.dumps(result, indent=2))

    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
