import logging.config
from logger_helper import LOGGING_CONFIG
from datetime import date
from peewee import Model, CharField, DateField, SqliteDatabase, TextField, IntegerField, ForeignKeyField
import os

db_directory = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(db_directory, exist_ok=True)

db = SqliteDatabase(os.path.join(db_directory, 'movie_base.db'))

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("database")


class User(Model):
    """
    Модель для хранения пользователей.

    Атрибуты:
        user_id (int): ID пользователя.
        username (str): Имя пользователя
    """

    user_id = IntegerField(unique=True)
    username = CharField(null=True)

    class Meta:
        database = db


class History(Model):
    """
    Модель для хранения истории поиска фильмов.

    Атрибуты:
        user (ForeignKeyField): Ссылка на модель пользователя.
        date (datetime): Дата создания записи.
        name (str): Название фильма.
        description (str): Описание фильма.
        rating (str): Рейтинг фильма (например, IMDb).
        year (int): Год выпуска фильма.
        genres (str): Жанры фильма, разделенные запятыми.
        ageRating (str): Возрастной рейтинг фильма.
        poster_url (str): URL постера фильма.
    """

    user = ForeignKeyField(User, backref='searches')
    date = DateField(default=date.today)
    name = CharField()
    description = TextField()
    rating = CharField()
    year = CharField()
    genres = TextField()
    ageRating = CharField()
    poster_url = CharField()

    class Meta:
        database = db


def initialize_database():
    """Инициализация базы данных и создание таблиц."""
    try:
        db.connect()
        logger.info("Connected to the database.")

        # Создание таблиц, если они еще не существуют
        db.create_tables([User, History], safe=True)
        logger.info("Tables created successfully.")

    except Exception as e:
        logger.error("Error connecting to the database: %s", e)

    finally:
        if not db.is_closed():
            db.close()
            logger.info("Database connection closed.")


initialize_database()
