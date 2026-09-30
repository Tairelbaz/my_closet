import requests

# We are asking Open-Meteo for the current weather in Rishon LeZion
url = 'https://api.open-meteo.com/v1/forecast'
params = {
    'latitude': 31.9730,  # Latitude for Rishon LeZion
    'longitude': 34.7925, # Longitude for Rishon LeZion
    'current_weather': True
}

print("Asking the internet for the weather...")
response = requests.get(url, params=params)
data = response.json()

temp = data['current_weather']['temperature']
print(f"Success! The current temperature is {temp}°C")