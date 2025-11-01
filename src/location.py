import boto3
import json
import os

s3 = boto3.client("s3")
bucket = os.environ["S3_BUCKET"]

def load_latest_location():
    prefix = "state/"
    # 1. List all objects under the 'state/' folder
    resp = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
    contents = resp.get("Contents", [])

    if not contents:
        raise ValueError("No state files found in S3.")

    # 2. Find the latest one by LastModified timestamp
    def get_modified_time(obj):
        return obj["LastModified"]
    latest = max(contents, key= get_modified_time)
    key = latest["Key"]
    print(f"Using latest state file: {key}")

    # 3. Download and parse JSON
    obj = s3.get_object(Bucket=bucket, Key=key)
    data = json.loads(obj["Body"].read())
    print(f"Loaded location: {data}")
    return data
