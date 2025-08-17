# python-weather-agent.py

# First, install the requests library to make HTTP calls:
# pip install requests

import requests
import os
import json

# --- Configuration and API Key ---
# IMPORTANT: This program requires an API key from OpenWeather.
# 1. Sign up for a free account at https://openweathermap.org/api
# 2. Get your API key from your account dashboard.
# 3. The most secure way to use your key is via an environment variable.
#    - On Linux/macOS, run in your terminal: export OPENWEATHER_API_KEY="your_api_key_here"
#    - On Windows, run in Command Prompt: set OPENWEATHER_API_KEY="your_api_key_here"
#    - Replace 'your_api_key_here' with your actual key.

API_KEY = os.environ.get("OPENWEATHER_API_KEY")

GOOGLE_API_KEY="AIzaSyB1oM5l4kKIiqsGy-k2jUnC-FiF0VQ7F6s"
GEMINI_API_KEY="AIzaSyB1oM5l4kKIiqsGy-k2jUnC-FiF0VQ7F6s"
OPENWEATHER_API_KEY="5e8089fba040eee46d43da8676c5750a"
API_KEY="5e8089fba040eee46d43da8676c5750a"


# Check if the API key environment variable is set
if not API_KEY:
    print("Error: OPENWEATHER_API_KEY environment variable is not set.")
    print("Please set your API key as an environment variable and try again.")
    exit()

# OpenWeather API endpoint URL
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

# --- Main Function ---
def get_weather(city_name):
    """
    Fetches weather data for a given city and prints a summary.

    Args:
        city_name (str): The name of the city to get the weather for.
    """
    params = {
        "q": city_name,
        "appid": API_KEY,
        "units": "imperial"  # Use "metric" for Celsius, or "imperial" for Fahrenheit
    }

    try:
        # Make the API request
        response = requests.get(BASE_URL, params=params)
        
        # Raise an HTTPError for bad responses (4xx or 5xx)
        response.raise_for_status()
        
        # Parse the JSON response
        weather_data = response.json()

        # Check if the city was found
        if weather_data["cod"] == 200:
            # Extract relevant information
            main_weather = weather_data["main"]
            weather_description = weather_data["weather"][0]["description"]
            wind_data = weather_data["wind"]

            # Print the weather summary
            print(f"\n--- Weather for {city_name.title()} ---")
            print(f"Temperature: {main_weather['temp']}°F")
            print(f"Feels like: {main_weather['feels_like']}°F")
            print(f"Humidity: {main_weather['humidity']}%")
            print(f"Wind Speed: {wind_data['speed']} m/s")
            print(f"Description: {weather_description.title()}")
            print("---------------------------------------")
            if(city_name=="london"):
                print("The actual json data looks like this:")
                pretty_json = json.dumps(weather_data, indent=4)
                print( pretty_json )
        else:
            print(f"City not found: {city_name.title()}")

    except requests.exceptions.RequestException as e:
        # Handle network-related errors (e.g., connection refused, timeout)
        print(f"An error occurred while making the request: {e}")
    except KeyError as e:
        # Handle cases where the API response is missing expected data
        print(f"Error parsing weather data: Missing key {e}")
    except Exception as e:
        # Catch any other unexpected errors
        print(f"An unexpected error occurred: {e}")

# --- Program Entry Point ---
if __name__ == "__main__":
    print("Welcome to the AI Weather Agent!")
    print("This program provides current weather information for any city.")
    
    while True:
        city = input("\nEnter a city name (or 'exit' to quit): ")
        if city.lower() == "exit":
            print("Thank you for using the AI Weather Agent. Goodbye!")
            break
        
        get_weather(city)

