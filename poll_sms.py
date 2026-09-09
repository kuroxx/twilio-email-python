"""
List inbound SMS to a Twilio phone number and extract email addresses.

Requires in .env:
    TWILIO_ACCOUNT_SID=ACxxxx
    TWILIO_AUTH_TOKEN=xxxx
    TWILIO_PHONE_NUMBER=+15005550006

Usage:
    python poll_sms.py                   # today (local time), default
    python poll_sms.py --all             # all inbound messages
    python poll_sms.py --since 2026-09-01  # from a specific date (inclusive)
"""

import os
import re
import sys
from datetime import date, datetime, time

from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")


def parse_args(argv: list[str]) -> datetime | None:
    """Return the `date_sent_after` cutoff, or None for --all."""
    if "--all" in argv:
        return None
    if "--since" in argv:
        i = argv.index("--since")
        if i + 1 >= len(argv):
            print("Usage: python poll_sms.py --since YYYY-MM-DD")
            sys.exit(1)
        day = date.fromisoformat(argv[i + 1])
    else:
        day = date.today()
    return datetime.combine(day, time.min).astimezone()


def main() -> None:
    since = parse_args(sys.argv[1:])

    client = Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])
    to_number = os.environ["TWILIO_PHONE_NUMBER"]

    kwargs = {"to": to_number}
    if since is not None:
        kwargs["date_sent_after"] = since

    messages = list(reversed(client.messages.list(**kwargs)))  # oldest first

    label = "all time" if since is None else f"since {since.date().isoformat()}"
    print(f"Inbound messages to {to_number} ({label}): {len(messages)}\n")

    emails = []
    for m in messages:
        match = EMAIL_RE.search(m.body or "")
        email = match.group(0).lower() if match else None
        marker = "✓" if email else "✗"
        date_str = m.date_sent.isoformat() if m.date_sent else "?"
        print(f"[{marker}] {date_str}  {m.from_}  body={m.body!r}  -> {email}")
        if email:
            emails.append(email)

    unique = sorted(set(emails))
    print(f"\nUnique email addresses ({len(unique)}):")
    for e in unique:
        print(f"  {e}")


if __name__ == "__main__":
    main()
