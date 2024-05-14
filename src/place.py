import requests

from src.weather import Weather, WeatherMaster
from constants import GEOCODER_API_KEY, SERPAPI_API_KEY, BASE_CITY_IMAGE


class Place:
    weather: Weather
    properties: dict
    image: str
    forecast: list

    @staticmethod
    def get_properties(lat: float, lng: float):
        request = f'https://geocode-maps.yandex.ru/1.x?apikey={GEOCODER_API_KEY}&geocode={lng}, {lat}&lang=en_US&format=json'
        response = requests.get(request).json()
        return response

    @staticmethod
    def get_image(city):
        request = f'https://serpapi.com/search?engine=yandex_images&text={city}&api_key={SERPAPI_API_KEY}'
        image_response = requests.get(request).json()
        try:
            return image_response["images_results"][0]["original"]
        except IndexError:
            try:
                request = f'https://serpapi.com/search?engine=yandex_images&text={city}&api_key={SERPAPI_API_KEY}'
                image_response = requests.get(request).json()
                return image_response["hits"][0]['largeImageURL']
            except IndexError:
                return BASE_CITY_IMAGE

    def __init__(self, lat: float, lng: float):
        self.lat = lat
        self.lng = lng
        self.properties = self.get_properties(lat, lng)
        self.weather = WeatherMaster.get_today((lat, lng))
        self.forecast = WeatherMaster.get_forecast((lat, lng))

    def card(self):
        metadata = self.properties["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        result = {
            'name': metadata["name"],
            'weather': self.weather,
            'image': self.get_image(metadata["name"]),
            'forecast': self.forecast
        }
        return result
