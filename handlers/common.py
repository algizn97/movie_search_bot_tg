import logging.config

from aiogram import Router, types
from aiogram.fsm.context import FSMContext

from logger_helper.logger_helper import LOGGING_CONFIG

router = Router(name=__name__)

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("common")


@router.message()
async def unknown_message(message: types.Message, state: FSMContext) -> None:
    """
    Обработчик для неожиданных сообщений.
    Информирует пользователя о том, что команда не распознана.

    :param message: Сообщение от пользователя.
    :param state: Контекст состояния FSM.
    """
    try:
        await state.clear()
        await message.answer(
            text="Извините, я вас не понял. "
            "Пожалуйста, используйте одну из следующих команд:\n"
            "/movie_search - Поиск фильма/сериала по названию\n"
            "/movie_by_genre - Поиск фильма/сериала по жанру\n"
            "/movie_by_rating - Поиск фильмов/сериалов по рейтингу\n"
            "/low_budget_movie - Поиск фильмов/сериалов с низким бюджетом\n"
            "/high_budget_movie - Поиск фильмов/сериалов с высоким бюджетом\n"
            "/history - История запросов",
            parse_mode=None,
        )
        logger.debug(
            "Received unknown message from user %s: %s",
            message.from_user.full_name,
            message.text,
        )
    except Exception as e:
        logger.error("Error handling unknown message: %s", e)
        await message.answer(
            "Произошла ошибка при обработке вашего сообщения. Пожалуйста, попробуйте позже."
        )
