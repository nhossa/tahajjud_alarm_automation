import json
from botocore.exceptions import ClientError
import requests
import boto3
from datetime import datetime, timezone
import dotenv
import os

# === CONFIGURATION ===
dotenv.load_dotenv()  # load .env if present

BUCKET_NAME = os.getenv("S3_BUCKET_NAME")     # your actual S3 bucket
STATE_PREFIX = "state/"                       # folder within S3
SOURCE = "auto"                               # for tracking updates
STATE_KEY = f"{STATE_PREFIX}{datetime.now().strftime('%Y-%m-%d')}.json"

s3 = boto3.client("s3")

# === LOCATION FETCH ===
def get_current_location():
    """Fetch current location from IP-based API."""
    resp = requests.get("http://ip-api.com/json/", timeout=10)
    data = resp.json()

    if data["status"] != "success":
        raise RuntimeError(f"Location API error: {data}")

    return {
        "source": SOURCE,
        "lat": round(data["lat"], 4),
        "lon": round(data["lon"], 4),
        "timezone": data["timezone"],
        "updated_at_utc": datetime.now(timezone.utc).isoformat()
    }

# === S3 UTILITIES ===
def get_latest_state_key():
    """Return the most recently modified state object key under 'state/'."""
    resp = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=STATE_PREFIX)
    if "Contents" not in resp:
        return None  # no files yet

    latest = max(resp["Contents"], key=lambda obj: obj["LastModified"])
    return latest["Key"]

def fetch_existing_state():
    """Download the most recent state file from S3 (if exists)."""
    latest_key = get_latest_state_key()
    if not latest_key:
        return None

    try:
        obj = s3.get_object(Bucket=BUCKET_NAME, Key=latest_key)
        data = obj["Body"].read().decode("utf-8")
        return json.loads(data)
    except ClientError as e:
        print(f"⚠️ Failed to fetch latest state: {e}")
        return None

def upload_if_changed(new_state):
    """Compare new vs existing, and upload a new file if changed or none exists."""
    old_state = None  # always define first

    try:
        old_state = fetch_existing_state()
        # Defensive check in case the fetched file is empty
        if not old_state:
            print("⚠️ Previous file empty or unreadable.")
            old_state = None
    except Exception as e:
        print(f"⚠️ Failed to fetch existing state: {e}")
        old_state = None

    # --- If no previous state found, upload immediately ---
    if old_state is None:
        print("📂 No previous state found — uploading initial location file.")
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=STATE_KEY,
            Body=json.dumps(new_state, indent=2),
            ContentType="application/json"
        )
        print(f"📤 Uploaded new state to s3://{BUCKET_NAME}/{STATE_KEY}")
        return True

    # --- Otherwise, compare and upload only if changed ---
    if (
        old_state.get("lat") == new_state["lat"]
        and old_state.get("lon") == new_state["lon"]
        and old_state.get("timezone") == new_state["timezone"]
    ):
        print("✅ No change detected — skipping upload.")
        return False

    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=STATE_KEY,
        Body=json.dumps(new_state, indent=2),
        ContentType="application/json"
    )
    print(f"📤 Uploaded updated location to s3://{BUCKET_NAME}/{STATE_KEY}")
    return True

# === MAIN ENTRYPOINT ===
def main():
    location = get_current_location()
    upload_if_changed(location)

if __name__ == "__main__":
    main()
