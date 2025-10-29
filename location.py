import requests

location = requests.get("http://ip-api.com/json")

location = location.json()

# for key, value in location.items():
#     print(f"{key}: {value}")


