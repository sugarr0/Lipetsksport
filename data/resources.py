from data.db_session import create_session
from data.Cities import City
from data.sport import Sport
import requests
from flask import jsonify


def get_city_id(city):
    db_sess = create_session()
    cities = db_sess.query(City).filter(City.city == city).first()
    if cities:
        return cities.id
    else:
        return None


def get_sport(ind):
    db_sess = create_session()
    sports = db_sess.query(Sport).filter(Sport.id == ind).first()
    if sports:
        return sports.sport
    else:
        return None


def get_city(ind):
    db_sess = create_session()
    cities = db_sess.query(City).filter(City.id == ind).first()
    if cities:
        return cities.city
    else:
        return None


def get_geocod(plase) -> str:
    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

    geocoder_params = {
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "geocode": plase,
        "format": "json"}

    response = requests.get(geocoder_api_server, params=geocoder_params)

    if not response:
        return ''

    json_response = response.json()
    toponym = json_response["response"]["GeoObjectCollection"][
        "featureMember"][0]["GeoObject"]
    toponym_coodrinates = toponym["Point"]["pos"]
    return str(toponym_coodrinates)
