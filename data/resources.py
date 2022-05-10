from data.db_session import create_session
from data.Cities import City
from data.sport import Sport


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
