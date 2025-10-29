import requests
from datetime import date,datetime, timedelta
from location import location


BASE_URL= "https://api.aladhan.com/v1/timings/"

# response = requests.get("https://api.aladhan.com/v1/timings/25-10-2025?latitude=39.0503&longitude=-77.3909&timezonestring=America/New_York&method=2")



today = date.today()
today = today.strftime("%d-%m-%Y")

latitude = location["lat"]
longitude = location["lon"]
timzone = location["timezone"]

url = f"{BASE_URL}&date={today}?&latitude={latitude}&longitude={longitude}&timezonestring={timzone}&method=2"
print(url)
response = requests.get(url)
print(response.status_code)
timings = response.json()
fajr_time = timings['data']['timings']['Fajr']
fajr_time = datetime.strptime(fajr_time, "%H:%M")
tahajjud_time = (fajr_time - timedelta(minutes=30)).time()

print(tahajjud_time)