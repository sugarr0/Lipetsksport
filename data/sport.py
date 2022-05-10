import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm

from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash


class Sport(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'sports'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    sport = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    im1 = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    im2 = sqlalchemy.Column(sqlalchemy.String, nullable=True)

