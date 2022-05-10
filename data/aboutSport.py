import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm

from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash


class AboutSport(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'about_sport'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    sport_id = sqlalchemy.Column(sqlalchemy.String)
    city_id = sqlalchemy.Column(sqlalchemy.String)
    address = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    cont = sqlalchemy.Column(sqlalchemy.String, nullable=True)
