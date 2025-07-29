from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import logging.config
from logger_helper.logger_helper import LOGGING_CONFIG

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("reply")

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="🔍 Поиск фильма/сериала по названию")],
    [KeyboardButton(text="🔍 Поиск фильма/сериала по жанру")],
    [KeyboardButton(text="🔍 Поиск фильмов/сериалов по рейтингу")],
    [KeyboardButton(text="🔍 Поиск фильмов/сериалов с низким бюджетом")],
    [KeyboardButton(text="🔍 Поиск фильмов/сериалов с высоким бюджетом")],
], resize_keyboard=True,
input_field_placeholder="Выберите пункт меню...")

cancel = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Отмена")]
    ], resize_keyboard=True
)

to_main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="На главную")]
], resize_keyboard=True)


genres = [
    "Комедия",
    "Детектив",
    "Мелодрама",
    "Боевик",
    "Триллер",
    "Ужасы",
    "Фантастика",
    "Приключения",
    "Драма",
    "История",
    "Биография",
    "Военный",
    "Аниме",
    "Мультфильм",
    "Спорт",
    "Вестерн",
    "Фэнтези",
    "Семейный",
    "Короткометражка",
    "Музыка",
    "Отмена"
]

async def reply_genres():
    """
    Создает клавиатуру для выбора жанров.

    :return: ReplyKeyboardMarkup с кнопками жанров.
    """
    keyboard = ReplyKeyboardBuilder()

    for genre in genres:
        keyboard.add(KeyboardButton(text=genre))
        logger.debug("Добавлен жанр: %s", genre)

    return keyboard.adjust(2).as_markup()


main_menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Да")],
        [KeyboardButton(text="Нет")],
        [KeyboardButton(text="Отмена")],
    ], resize_keyboard=True
)