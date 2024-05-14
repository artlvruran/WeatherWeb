import datetime
import requests

from constants import *


class Weather:
    date: int
    temperature: float
    pressure: float
    wind_speed: float
    humidity: float

    def get_dict(self):
        return {
            'date': datetime.datetime.fromtimestamp(self.date).strftime('%Y-%m-%d %H:%M:%S'),
            'temperature': self.temperature,
            'pressure': self.pressure,
            'wind_speed': self.wind_speed,
            'humidity': self.humidity
        }


class WeatherToday(Weather):
    def __init__(self, pos: tuple):
        lat, lon = pos
        current_weather_request = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&lang=en&appid={WEATHER_API_KEY}'
        weather_response = requests.get(current_weather_request).json()

        self.date = int(datetime.datetime.now().timestamp())
        self.temperature = int(weather_response['main']['temp'])
        self.pressure = weather_response['main']['pressure']
        self.wind_speed = weather_response['wind']['speed']
        self.humidity = weather_response['main']['humidity']
        self.description = weather_response['weather'][0]['description']


class WeatherMaster:
    @staticmethod
    def celc_from_kelvin(temp):
        return round(temp - 273.15)

    @staticmethod
    def get_today(pos: tuple):
        weather = WeatherToday(pos)
        weather.temperature = WeatherMaster.celc_from_kelvin(weather.temperature)
        return weather

    @staticmethod
    def get_forecast(pos: tuple):
        forecast_request = f'https://api.openweathermap.org/data/2.5/onecall?lat={pos[1]}&lon={pos[0]}&appid={WEATHER_API_KEY}'
        forecast = requests.get(forecast_request).json()

        forecast_hourly = [{
            "time": datetime.datetime.utcfromtimestamp(
                int(forecast["hourly"][i]["dt"]) + int(forecast["timezone_offset"])).strftime('%H:%M'),
            "temp": f'{WeatherMaster.celc_from_kelvin(forecast["hourly"][i]["temp"])} °C',
            "icon": f'https://openweathermap.org/img/wn/{forecast["hourly"][i]["weather"][0]["icon"]}.png'
        }
            for i in range(len(forecast["hourly"]))]

        return forecast_hourly
