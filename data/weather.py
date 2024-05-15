import flask
import json
import requests
import datetime
from constants import *
from flask import render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from data import db_session
from data.weather_cards import WeatherCard
from src.place import Place, PlaceMaster
from data.users import User


def celc_from_kelvin(temp):
    return round(temp - 273.15)


blueprint = flask.Blueprint(
    'weather',
    __name__,
    template_folder='templates'
)


@blueprint.route("/weather/<city>")
@login_required
def get_weather(city):
    geocoder_req = f"https://geocode-maps.yandex.ru/1.x/?apikey={GEOCODER_API_KEY}&geocode={city}&format=json"
    response = requests.get(geocoder_req).json()
    pos = response['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos'].split()

    # Текущая погода
    current_weather_request = f'https://api.openweathermap.org/data/2.5/weather?lat={pos[1]}&lon={pos[0]}&lang=en&appid={WEATHER_API_KEY}'
    weather_response = requests.get(current_weather_request).json()
    # Прогноз
    forecast_request = f'https://api.openweathermap.org/data/2.5/onecall?lat={pos[1]}&lon={pos[0]}&appid={WEATHER_API_KEY}'
    forecast = requests.get(forecast_request).json()

    forecast_hourly = [{
        "time": datetime.datetime.utcfromtimestamp(
            int(forecast["hourly"][i]["dt"]) + int(forecast["timezone_offset"])).strftime('%H:%M'),
        "temp": f'{celc_from_kelvin(forecast["hourly"][i]["temp"])} °C',
        "icon": f'https://openweathermap.org/img/wn/{forecast["hourly"][i]["weather"][0]["icon"]}.png'
    }
        for i in range(len(forecast["hourly"]))]

    forecast_daily = [{
        "time": datetime.datetime.utcfromtimestamp(
            int(forecast["daily"][i]["dt"]) + int(forecast["timezone_offset"])).strftime('%d.%m'),
        "temp_day": f'{celc_from_kelvin(forecast["daily"][i]["temp"]["day"])} °C',
        "temp_night": f'{celc_from_kelvin(forecast["daily"][i]["temp"]["night"])} °C',
        "icon": f'https://openweathermap.org/img/wn/{forecast["daily"][i]["weather"][0]["icon"]}.png'
    }
        for i in range(len(forecast["daily"]))]

    params = {
        "city": weather_response["name"] if weather_response["name"] else city,
        "temperature": f'{celc_from_kelvin(weather_response["main"]["temp"])} °C',
        "icon": f'https://openweathermap.org/img/wn/{weather_response["weather"][0]["icon"]}.png',
        "main": weather_response['weather'][0]['description'],
        "max": f"{celc_from_kelvin(weather_response['main']['temp_max'])} °C",
        "min": f"{celc_from_kelvin(weather_response['main']['temp_min'])} °C",
        "forecast_hourly": forecast_hourly,
        "forecast_daily": forecast_daily,
        "feels_like": f'{celc_from_kelvin(weather_response["main"]["feels_like"])} °C',
        "pressure": f'{round(0.750064 * float(weather_response["main"]["pressure"]), 1)} Hg',
        "wind_speed": f'{weather_response["wind"]["speed"]} m/s'
    }

    request = f'https://serpapi.com/search?engine=yandex_images&text={params["city"]}&api_key={SERPAPI_API_KEY}'
    image_response = requests.get(request).json()
    try:
        params["image"] = image_response["images_results"][0]["original"]
    except IndexError:
        try:
            request = f'https://serpapi.com/search?engine=yandex_images&text={city}&api_key={SERPAPI_API_KEY}'
            image_response = requests.get(request).json()
            params["image"] = image_response["hits"][0]['largeImageURL']
        except IndexError:
            params["image"] = BASE_CITY_IMAGE

    return render_template('general.html', **params)


@blueprint.route('/weather/<city>', methods=['POST'])
def get_city(city):
    text = request.form['search']
    return redirect(f'/weather/{text}')


@blueprint.route('/weather/cards')
@login_required
def weather_cards():
    db_sess = db_session.create_session()
    weather_crds = db_sess.query(WeatherCard).filter(WeatherCard.user_id == current_user.id).all()

    params = {
        'user': current_user,
        'cards': [(Place(card.latitude, card.longitude).card(), card.id) for card in weather_crds]
    }

    return render_template('cards.html', **params)


@blueprint.route('/weather/cards/download', methods=['POST'])
@login_required
def download_card():
    id = request.args.get('id')
    db_sess = db_session.create_session()
    card = db_sess.query(WeatherCard).filter(WeatherCard.id == id).first()
    data = Place(card.latitude, card.longitude).card()
    with open('./static/tmp/temp.txt', mode='w') as file:
        weather_dict = data['weather'].get_dict()
        result = {
            'place': data['name'],
            'weather': weather_dict,
            'forecast': data['forecast']
        }
        file.write(json.dumps(result))
    return flask.send_file('./static/tmp/temp.txt', as_attachment=True)


@blueprint.route('/weather/cards/add', methods=['POST'])
@login_required
def add_card():
    db_sess = db_session.create_session()

    text = request.form['search']
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    place = PlaceMaster.get_place(text)
    card = WeatherCard(user_id=user.id, latitude=place.lat, longitude=place.lng)

    db_sess.add(card)
    db_sess.commit()

    return redirect('/weather/cards')


@blueprint.route('/weather/cards/delete', methods=['POST'])
@login_required
def delete_card():
    db_sess = db_session.create_session()
    id = request.args.get('id')
    card = db_sess.query(WeatherCard).filter(WeatherCard.id == id).first()
    db_sess.delete(card)
    db_sess.commit()

    return redirect('/weather/cards')
