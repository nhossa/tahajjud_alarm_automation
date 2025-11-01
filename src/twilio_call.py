from twilio.rest import Client
import os
import time


# Use env vars
account_sid = os.environ["TWILIO_SID"]
auth_token = os.environ["TWILIO_TOKEN"]
client = Client(account_sid, auth_token)

status = None
def execute_call(from_number, to_number ):
    for i in range(2):
        call = client.calls.create(
            to=to_number,
            from_=from_number,
            twiml='<Response><Say voice="alice">It is time for Tahajjud. Wake up and pray.</Say></Response>'
        )
        sid = call.sid
        print("Call initiated, SID:", sid)
            # Poll every 10s until call ends
        for attempt in range(6):  # wait up to 1 minute
            status = client.calls(sid).fetch().status
            print("Status:", status)
            if status in ["completed", "failed", "busy", "no-answer", "canceled"]:
                break
            time.sleep(10)
        if status == "completed":
            print("✅ Call answered and completed.")
            break
        else:
            print(f"⚠️ Call ended with status: {status}")