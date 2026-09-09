# Twilio Email API — Python Demo

Send emails via `comms.twilio.com/v1/Emails` and collect recipient addresses via inbound SMS to a Twilio number.

> **Note:** Twilio Email is **not** SendGrid — different endpoint, different auth, Liquid (not Handlebars) templating.

---

## Prerequisites

- Python 3.8+
- A [Twilio account](https://www.twilio.com/try-twilio)
- A verified sender domain (Console → **Messaging → Email → Senders**)
- An SMS-capable Twilio phone number (only needed for `poll_sms.py`)

---

## Quickstart

1. **Install dependencies**

   ```
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure credentials**

   ```
   cp .env.example .env
   ```

   Fill in `.env`:

   ```
   TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   TWILIO_AUTH_TOKEN=your_auth_token
   FROM_ADDRESS=demo@yourdomain.com
   TWILIO_PHONE_NUMBER=+15005550006
   ```

3. **Send email**

   ```
   python demo_email.py simple you@example.com          # single send
   python demo_email.py batch recipients.txt            # batch send (one email per line)
   python demo_email.py status <operationId>            # check delivery status
   ```

4. **Collect emails via SMS**

   Ask attendees to text their email address to your Twilio number, then:

   ```
   python poll_sms.py                                    # list inbound SMS + parsed emails
   ```

   Copy the deduped list into `recipients.txt` and run `demo_email.py batch`.

---

## Files

| File | Purpose |
|---|---|
| `demo_email.py` | Send single or batch emails via the Twilio Email API |
| `poll_sms.py` | Poll a Twilio number for inbound SMS and extract email addresses |
| `recipients.txt` | One email address per line, `#` comments allowed |
| `.env.example` | Template for required environment variables |

---

## Verify a sender domain

1. Twilio Console → **Messaging → Email → Senders → Add Sender Domain**.
2. Add the DKIM CNAMEs + SPF records to your DNS provider.
3. Click **Verify** — propagation usually takes a few minutes.

Your `FROM_ADDRESS` must use this verified domain (e.g. `demo@yourdomain.com`).

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `401 Unauthorized` | Check `TWILIO_ACCOUNT_SID` / `TWILIO_AUTH_TOKEN`. Don't use a `SG.`-prefix SendGrid key. |
| `400 must be a well-formed email address` | `FROM_ADDRESS` must be `local@domain`, not just a domain. |
| `400` sender error | `FROM_ADDRESS` domain must match a Verified Sender. |
| `202` but email never arrives | Run `python demo_email.py status <operationId>` for per-recipient failure reasons. |

---

## References

- [Twilio Email API docs](https://www.twilio.com/docs/email)

---

## License

MIT — see [LICENSE](LICENSE).
