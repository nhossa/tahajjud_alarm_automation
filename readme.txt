==============================
  TAHAJJUD AUTOMATION PROJECT
==============================

This project is a cloud-based event-driven automation that calculates daily Tahajjud time based on Maghrib and Fajr timings, schedules an AWS EventBridge rule, and triggers a Lambda function that logs the event to S3 and makes a call through Twilio.

It runs completely in the cloud. No local scripts or servers are needed.

------------------------------
OVERVIEW
------------------------------

Core Idea:
Use AWS services to automatically determine prayer times and trigger an alarm without manual input. The system updates itself daily.

Components:

lambda_function.py: main entry point. Calculates times, creates an EventBridge rule, and handles both planning and alarm logic.

alarm.py: triggered when the EventBridge rule fires. Logs execution details to S3 and calls the user via Twilio.

twilio_call.py: contains Twilio voice call logic.

location.py: fetches the most recent latitude, longitude, and timezone from S3.

------------------------------
AWS SERVICES USED
------------------------------

Lambda - runs all code serverlessly
EventBridge - creates and triggers scheduled events
S3 - stores state (latest location) and execution logs
IAM - grants Lambda permission to access S3 and EventBridge

------------------------------
ENVIRONMENT VARIABLES
------------------------------

These must be set inside the Lambda configuration:

S3_BUCKET = your-bucket-name
TWILIO_SID = your Twilio Account SID
TWILIO_TOKEN = your Twilio Auth Token
TO_NUMBER = your phone number in E.164 format (e.g., 1234567890)
FROM_NUMBER = your Twilio-verified number 

------------------------------
IAM POLICY REQUIREMENTS
------------------------------

The Lambda execution role must allow access to S3 and EventBridge.

An example permission JSON is attached

------------------------------
S3 SETUP
------------------------------

Create an S3 bucket 

Inside the bucket, create a folder named "state"

Upload an initial state file to "state/test.json" with content like:

{
"source": "manual",
"lat": 38.0000
"lon": -77.0000,
"timezone": "America/New_York",
"updated_at_utc": "2025-10-29T23:40:00Z"
}

This file provides the location data for prayer time calculations.

------------------------------
DEPLOYMENT STEPS
------------------------------

Install dependencies locally:
pip install -r requirements.txt -t src/

Create the deployment package:
cd src
zip -r ../function.zip .
cd ..

Upload the entire project folder — including the application code and all installed dependencies
 (such as Twilio and Requests) — as a ZIP file when updating the Lambda function.

 Note: typing_extensions will be automatically installed as part of the dependencies when uploading or packaging the Lambda function.

------------------------------
DAILY SCHEDULER SET-UP
------------------------------
After deploying both Lambda functions, a daily EventBridge scheduler must be created to automatically invoke your lambda function once per day. This Lambda calculates prayer times, determines the next Tahajjud window, and sets up the alarm event for that night.

To create the recurring daily schedule:

Go to AWS Console → EventBridge → Schedules.

Click Create schedule and configure the following:

Name: your-lambda-scheduler

Schedule pattern: Cron expression

Expression: 0 0 * * ? *
(Runs every day at 12:00 AM Eastern Time, which is midnight in Sterling, VA.)

Target type: Lambda function

Target: your_lambda.py

Enable the schedule to be recurring daily

Once created, it appears under the EventBridge Schedules tab as Enabled, with the target type LAMBDA_Invoke.

From that point forward, the system is fully automated:

The scheduler triggers planner-lambda daily at midnight.

The planner computes prayer times and creates a one-time EventBridge rule for that night’s Tahajjud alarm.

After the alarm fires, the rule is deleted, and the cycle repeats automatically each day.

You only need to create this daily scheduler once — the entire pipeline runs continuously without any manual maintenance.

------------------------------
TESTING
------------------------------

Manual test from AWS Console:

{
"trigger": "manual"
}

This runs the planner and creates a one-time EventBridge rule.

To test the Twilio call:
{
"kind": "tahajjud"
}
(The function checks the event payload to decide whether to schedule a new alarm or execute the current one.)

This runs the Twilio call logic and logs the result to S3.

HOW THE SYSTEM WORKS

The planner Lambda runs daily via the eventbridge scheduler.

It retrieves Maghrib and Fajr times from the Aladhan API.

It calculates the next Tahajjud time and generates a UTC cron expression.

It creates an EventBridge rule scheduled to trigger at that time.

When the rule triggers, the same Lambda switches to alarm mode.

The alarm makes a Twilio voice call and logs the status off that call into S3.

After execution, the EventBridge rule is deleted automatically.

PROJECT STRUCTURE


NOTES

Fully event-driven and serverless.

Uses only managed AWS services. Initially was going to run cron on system but that is not reliable. 

Scales automatically and costs almost nothing on AWS free tier. Twilio give a $15 dollar trial. 

Can be extended with SMS, notifications, or automatic coordinate updates.

AUTHOR
Naim Hossain
Cloud Automation | AWS | Python | DevOps | Serverless Systems
