import os
import json
import boto3
from datetime import datetime, timezone
import twilio_call

# Create S3 client once (reuse for speed)
s3 = boto3.client("s3")
bucket = os.environ["S3_BUCKET"]
to_number = os.environ["TO_NUMBER"]
from_number = os.environ["FROM_NUMBER"]

def trigger_alarm(event, context):
    """
    Triggered by EventBridge (planner lambda creates the rule).
    Logs the event to S3, deletes the rule after it fires,
    and prepares for notification (Twilio or other).
    """

    # 1. Read input event safely
    kind = event.get("kind", "test")
    plan_id = event.get("plan_id", "manual")

    # 2. Compute current UTC timestamp
    now_utc = datetime.now(timezone.utc)
    date_prefix = now_utc.strftime("%Y-%m-%d")
    timestamp = now_utc.strftime("%Y-%m-%dT%H-%M-%SZ")

    # 3. Notify via Twilio
    twilio_call.execute_call(from_number, to_number)

    # 4. Construct S3 key and JSON body to log status of twilio call
    key = f"logs/{date_prefix}/{timestamp}-{kind}.json"
    body = {
        "kind": kind,
        "plan_id": plan_id,
        "fired_utc": now_utc.isoformat(),
        "result": twilio_call.status
    }

    # 5. Upload to S3
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=json.dumps(body, indent=2),
        ContentType="application/json"
    )

    print(f"✅ Logged alarm trigger to s3://{bucket}/{key}")

    # 6. Delete the EventBridge rule (cleanup)
    try:
        rule_name = f"alarm-{plan_id}-tahajjud"
        events = boto3.client("events")

        # Remove targets first — AWS requires this before deleting a rule
        events.remove_targets(Rule=rule_name, Ids=["1"])
        events.delete_rule(Name=rule_name)

        print(f"Deleted rule: {rule_name}")

    except Exception as e:
        print(f"Failed to delete rule: {e}")

    return {"status": "ok", "s3_key": key}
