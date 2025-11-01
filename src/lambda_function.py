import json
import requests
from datetime import datetime, date, time, timedelta
from zoneinfo import ZoneInfo
import boto3
import os
from alarm import trigger_alarm
from location import load_latest_location


def lambda_handler(event, context):
    # === Mode Switch ===
    if event.get("kind") == "tahajjud":
        # ALARM MODE
        return trigger_alarm(event, context)
    
    #PLANNER MODE
    events = boto3.client("events")
    lambda_client = boto3.client("lambda")
    alarm_arn = context.invoked_function_arn

    location = load_latest_location()
    tz_str = location["timezone"]
    tz = ZoneInfo(tz_str)

    now_local = datetime.now(tz)
    local_today = now_local.date()
    local_tomorrow = local_today + timedelta(days=1)

    BASE_URL = "https://api.aladhan.com/v1/timings/"
    lat, lon = location["lat"], location["lon"]
    today_str = local_today.strftime("%d-%m-%Y")
    tomorrow_str = local_tomorrow.strftime("%d-%m-%Y")

    def fetch_timings(url: str) -> dict:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        j = r.json()
        if j.get("code") != 200 or "data" not in j or "timings" not in j["data"]:
            raise ValueError(f"Aladhan bad response: {j}")
        return j["data"]["timings"]

    today_url = f"{BASE_URL}{today_str}?latitude={lat}&longitude={lon}&timezonestring={tz_str}&method=2"
    tomorrow_url = f"{BASE_URL}{tomorrow_str}?latitude={lat}&longitude={lon}&timezonestring={tz_str}&method=2"

    today_timings = fetch_timings(today_url)
    tomorrow_timings = fetch_timings(tomorrow_url)

    maghrib_str = today_timings["Maghrib"].strip()
    fajr_str = tomorrow_timings["Fajr"].strip()

    h, m = map(int, maghrib_str.split(":")[:2])
    M = datetime.combine(local_today, time(h, m), tzinfo=tz)
    h, m = map(int, fajr_str.split(":")[:2])
    F = datetime.combine(local_tomorrow, time(h, m), tzinfo=tz)

    night_length = F - M
    tahajjud_time = M + (night_length * (2/3)) - timedelta(minutes=2)
    tahajjud_utc = tahajjud_time.astimezone(ZoneInfo("UTC"))


    #start of making rule and target for tahajjud
    cron_expr = f"cron({tahajjud_utc.minute} {tahajjud_utc.hour} {tahajjud_utc.day} {tahajjud_utc.month} ? {tahajjud_utc.year})"
    print("Cron expression:", cron_expr)

    rule_name = f"alarm-{tahajjud_utc.date()}-tahajjud"
    response = events.put_rule(
        Name=rule_name,
        ScheduleExpression=cron_expr,
        State="ENABLED",
        Description=f"Tahajjud alarm for {tahajjud_utc.date()}"
    )

    target_input = json.dumps({
        "kind": "tahajjud",
        "plan_id": str(tahajjud_utc.date())
    })

    #put what you want eventbridge to run
    events.put_targets(
        Rule=rule_name,
        Targets=[
            {
                "Id": "1",
                "Arn": alarm_arn,
                "Input": target_input
            }
        ]
    )
    print("Created rule and attached target:", rule_name)

    return {
        "maghrib": M.isoformat(),
        "tahajjud": tahajjud_time.isoformat(),
        "fajr": F.isoformat(),
        "timezone": tz_str
    }
