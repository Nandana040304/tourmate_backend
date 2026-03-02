from django.shortcuts import render
import requests
from django.http import JsonResponse

WEATHER_API_KEY = "0a27a35e07ff188ff1c64a40daa7c317"

def get_weather(request):
    destination = request.GET.get("destination")

    if not destination:
        return JsonResponse({"error": "Destination is required"}, status=400)

    # Step 1: Get latitude & longitude using Geocoding API
    geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={destination}&limit=1&appid={WEATHER_API_KEY}"
    geo_response = requests.get(geo_url).json()

    if not geo_response:
        return JsonResponse({"error": "Place not found"}, status=404)

    lat = geo_response[0]['lat']
    lon = geo_response[0]['lon']
    place_name = geo_response[0]['name']

    # Step 2: Get weather using lat & lon
    weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric"
    weather_data = requests.get(weather_url).json()

    temperature = weather_data['main']['temp']
    condition = weather_data['weather'][0]['main']
    humidity = weather_data['main']['humidity']
    wind_speed = weather_data['wind']['speed']
    rainfall = weather_data.get('rain', {}).get('1h', 0)

    # Step 3: Safety Logic
    if temperature > 35 or wind_speed > 15 or rainfall > 20:
        safety_status = "Unsafe"
    else:
        safety_status = "Safe"

    return JsonResponse({
        "destination": place_name,
        "weather": {
            "temperature": temperature,
            "condition": condition,
            "humidity": humidity,
            "windSpeed": wind_speed,
            "rainfall": rainfall
        },
        "safetyStatus": safety_status
    })