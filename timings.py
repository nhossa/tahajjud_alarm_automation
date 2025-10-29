import requests
from datetime import date,datetime, timedelta
from location import location



today = date.today()
today = today.strftime("%d-%m-%Y")

BASE_URL= f"https://api.aladhan.com/v1/timings/{today}"

latitude = location["lat"]
longitude = location["lon"]
timzone = location["timezone"]

# 2 - Islamic Society of North America calculation method
url = f"{BASE_URL}?latitude={latitude}&longitude={longitude}&timezonestring={timzone}&method=2"
response = requests.get(url)
timings = response.json()

fajr_time = timings['data']['timings']['Fajr']
print(fajr_time)