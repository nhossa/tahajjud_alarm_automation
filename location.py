import requests

location = requests.get("http://ip-api.com/json")

location = location.json()

print(location)

# for key, value in location.items():
#     print(f"{key}: {value}")


