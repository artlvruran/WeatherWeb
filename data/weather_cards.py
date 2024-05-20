import sqlalchemy
from .db_session import SqlAlchemyBase


class WeatherCard(SqlAlchemyBase):
    __tablename__ = 'weather_cards'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey('users.id'),
                                index=True,
                                nullable=False)

    latitude = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
    longitude = sqlalchemy.Column(sqlalchemy.Float, nullable=False)

