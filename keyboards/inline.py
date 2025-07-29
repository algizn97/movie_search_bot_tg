from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging.config
from logger_helper.logger_helper import LOGGING_CONFIG

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("inline")


def get_movie_selection_keyboard(movies, current_page: int) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для выбора фильмов.

    :param movies: Список фильмов для отображения.
    :param current_page: Текущая страница пагинации.
    :return: InlineKeyboardMarkup с кнопками для выбора фильмов.
    """
    keyboard = InlineKeyboardBuilder()
    items_per_page = 6
    start_index = (current_page - 1) * items_per_page
    logger.debug("Создание клавиатуры для выбора фильмов. Текущая страница: %d", current_page)
    total_pages = 0

    for index, movie in enumerate(movies):
        button_index = start_index + index
        keyboard.add(
            InlineKeyboardButton(
                text=f"{button_index + 1}. {movie['name']}",
                callback_data=f"select_movie:{button_index}"
            )
        )
        total_pages += 1
        logger.debug("Добавлена кнопка для фильма: %s с индексом %d", movie['name'], button_index)

    if current_page > 1:
        keyboard.add(
            InlineKeyboardButton(
                text="◀️ Назад",
                callback_data=f"navigate:previous:{current_page - 1}"
            )
        )
        logger.debug("Добавлена кнопка 'Назад' на странице %d", current_page)

    if items_per_page == len(movies):
        keyboard.add(
            InlineKeyboardButton(
                text="Дальше ▶️",
                callback_data=f"navigate:next:{current_page + 1}"
            )
        )
        logger.debug("Добавлена кнопка 'Дальше' на странице %d", current_page)

    return keyboard.adjust(2).as_markup()
