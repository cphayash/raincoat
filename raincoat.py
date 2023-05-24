import json
import requests
import sys
from typing import Any, Dict, Union

from api_key import getApiKey


"""
Raincoat

A script to suggest clothing based on the weather
    ie:
        - if it's raining, suggest a raincoat.
        - If it's rainy and cold, a raincoat and hoodie.
"""


API_KEY = getApiKey()
COUNTRY_CODE = "us"
ICON_URL = "https://openweathermap.org/img/w/{icon_code}.png"

PANTS = {
    "thermal jeans": {
        "min": float("-inf"),
        "max": 49,
    },
    "jeans": {
        "min": 50,
        "max": 79,
    },
    "shorts": {
        "min": 80,
        "max": float("inf"),
    },
}

SHIRT = {
    "long sleeve shirt": {
        "min": float("-inf"),
        "max": 49,
    },
    "T-shirt": {
        "min": 50,
        "max": float("inf"),
    },
}

OUTERWEAR = {
    "heavy jacket": {
        "min": float("-inf"),
        "max": 59,
    },
    "light jacket": {
        "min": 30,
        "max": 60,
    },
    "hoodie": { 
        "min": 50,
        "max": 70,
    },
}

SHOES = {
    "boots": {
        "min": float("-inf"),
        "max": 29,
    },
    "sneakers": {
        "min":  30,
        "max": 73,
    },
    "slippers": {
        "min": 74,
        "max": float("inf"),
    },
}

SOCKS = {
    "long warm socks": {
        "min": float("-inf"),
        "max": 49,
    },
    "socks": {
        "min": 50,
        "max": float("inf"),
    }
}

GLOVES = {
    "gloves": {
        "min": float("-inf"),
        "max": 40,
    },
}

OUTFIT = {
    "pants": PANTS,
    "shirt": SHIRT,
    "outerwear": OUTERWEAR,
    "shoes": SHOES,
    "socks": SOCKS,
    "gloves": GLOVES,
}


class City(object):
    def __init__(self, city_dict):
        self.name = city_dict["name"]
        self.lat = city_dict["coord"]["lat"]
        self.lon = city_dict["coord"]["lon"]
        self.iso2 = city_dict["country"]


class CurrentWeather(object):
    def __init__(self, current_weather: dict):
        weather = current_weather["weather"][0]

        self.dt = current_weather["dt"]     
        self.temp = round((float(current_weather["temp"]) - 273.15) * 9/5 + 32, 2)
        self.feels_like = current_weather["feels_like"]
        self.clouds = current_weather["clouds"]
        self.visibility = current_weather["visibility"]
        self.wind_speed = current_weather["wind_speed"]
        self.weather = weather["main"]
        self.description = weather["description"]
        self.icon = weather["icon"]


class Outfit(object):
    def __init__(self, current_weather: CurrentWeather):
        for item in OUTFIT:
            options = OUTFIT[item]
            self.__setattr__(item, None)
            for option in options:
                if current_weather.temp >= options[option]["min"] and current_weather.temp <= options[option]["max"]:
                    self.__setattr__(item, option)
        
    def __str__(self):
        res = []
        attributes = [item for item in dir(self) if not item.startswith("__")]
        for item in attributes:
            res.append(f"{item}: {self.__getattribute__(item)}")
        return "\n".join(res)


def get_weather(url) -> Dict[str, Any]:
    req = requests.get(url)

    return json.loads(req.content)


def get_onecall_weather(lat, lon, exclude=["hourly", "daily"]) -> CurrentWeather:
    return CurrentWeather(
        get_weather(
            f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude={','.join(exclude)}&appid={API_KEY}"
        )["current"]
    )


def get_5_3_weather(zip_code) -> Dict[str, Any]:
    return get_weather(
        f"http://api.openweathermap.org/data/2.5/forecast?zip={zip_code},{COUNTRY_CODE}&appid={API_KEY}"
    )


def get_img_url(icon_code) -> str:
    return ICON_URL.format(icon_code=icon_code)


def print_summary(city, current_weather) -> None:
    print(f"{city.name} ({city.iso2})")
    print(f"lat, lon: {city.lat}, {city.lon}")
    print()
    print(get_img_url(current_weather.icon))
    print(f"Current temp: {current_weather.temp}°F")
    print("Condition:", current_weather.weather)
    print("Description:", current_weather.description)


def main() -> None:
    zip_code = int(sys.argv[1]) if len(sys.argv) > 1 else None

    if not zip_code:
        print("Zip code required.  Exiting...")
        sys.exit(1)

    forecast_weather = get_5_3_weather(zip_code)

    if not forecast_weather or forecast_weather["cod"] != "200":
        print("Error.  Exiting...")
        sys.exit(1)

    city = City(forecast_weather["city"])

    current_weather = get_onecall_weather(city.lat, city.lon, [])

    print_summary(city, current_weather)

    outfit = Outfit(current_weather)

    print(outfit)



if __name__ == "__main__":
    main()
    