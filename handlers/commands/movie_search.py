import logging.config
from typing import Optional

from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

import keyboards.inline as kbi
import keyboards.reply as kbr
from api.movie_search_api import search_movies
from database.model import History, User
from handlers.commands.callback import generate_response_message
from logger_helper.logger_helper import LOGGING_CONFIG
from state.states import Search
from utils.paginator import Paginator

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("movie_search")

router = Router(name=__name__)


@router.message(Command("movie_search"))
@router.message(F.text == "🔍 Поиск фильма/сериала по названию")
async def cmd_movie_search(message: types.Message, state: FSMContext) -> None:
    """
    Обработчик команды /movie_search.
    Устанавливает состояние FSM на ожидание ввода названия фильма/сериала.

    :param message: Сообщение, содержащее команду от пользователя.
    :param state: Контекст состояния FSM.
    """
    try:
        await state.set_state(Search.name)
        await message.answer(
            text="Введите название фильма/сериала:", reply_markup=kbr.cancel
        )
        logger.debug(
            "Command movie_search processed successfully for user: %s",
            message.from_user.full_name,
        )
    except IndexError as e:
        logger.error("Error processing command movie_search: %s", e)


@router.message(Search.name)
async def process_name(message: types.Message, state: FSMContext) -> None:
    """
    Обработчик ввода названия фильма/сериала.
    Сохраняет название в состоянии и запрашивает количество вариантов.

    :param message: Сообщение от пользователя с названием фильма/сериала.
    :param state: Контекст состояния FSM.
    """
    try:
        await state.update_data(name=message.text)
        await state.set_state(Search.count)
        await message.answer(
            "Сколько вариантов вы хотите получить?", reply_markup=kbr.to_main
        )
        logger.debug(
            "Title input processed successfully for user: %s, name: %s",
            message.from_user.full_name,
            message.text,
        )
    except ValueError as e:
        logger.error("Error processing name input: %s", e)


async def validate_count(count: int) -> Optional[str]:
    """
    Проверяет, является ли переданное число допустимым количеством фильмов.

    Параметры:
    count (int): Количество фильмов для поиска.

    Возвращает:
    Optional[str]: Сообщение об ошибке, если количество недопустимо,
                   иначе None.

    Условия проверки:
    - Если count <= 0, возвращает сообщение о необходимости ввода положительного числа.
    - Если count > 250, возвращает сообщение о превышении лимита.
    """
    if count <= 0:
        return "Пожалуйста, введите положительное число."
    elif count > 250:
        return "Лимит не должен превышать 250."
    return None


@router.message(Search.count)
async def process_count(message: types.Message, state: FSMContext) -> None:
    """
    Обработчик ввода количества вариантов фильмов для отображения.
    Получает данные из состояния и делает запрос к API для поиска фильмов.

    :param message: Сообщение от пользователя с количеством вариантов.
    :param state: Контекст состояния FSM.

    Отправляет пользователю найденные фильмы или сообщение об их отсутствии.
    """
    try:
        count = int(message.text)
        validation_error = await validate_count(count)

        if validation_error:
            await message.reply(validation_error)
            logger.warning(
                "User %s entered an invalid count: %s",
                message.from_user.full_name,
                message.text,
            )
            return

        data = await state.get_data()
        name = data.get("name")
        movies = await search_movies(name, count)

        if not movies:
            await message.answer(
                "К сожалению, ничего не найдено.", reply_markup=kbr.main
            )
            logger.info(
                "No movies found for user %s with name '%s'",
                message.from_user.full_name,
                name,
            )
            return

        User.get_or_create(
            user_id=message.from_user.id,
            defaults={"username": message.from_user.username},
        )
        for movie in movies:
            History.create(
                user_id=message.from_user.id,
                name=movie["name"],
                description=movie["description"],
                rating=movie["rating"],
                year=movie["year"],
                genres=movie["genres"],
                ageRating=movie["ageRating"],
                poster_url=movie["poster_url"],
            )

        paginator = Paginator(movies, items_per_page=6)
        response_message = generate_response_message(paginator)

        await message.answer(f"Найдено фильмов: {len(movies)}")
        await message.answer(
            response_message,
            reply_markup=kbi.get_movie_selection_keyboard(
                paginator.get_current(), paginator.current_page
            ),
            parse_mode="Markdown",
        )
        await state.clear()
        await state.update_data(paginator=paginator)
        logger.debug(
            "Successfully processed count input for user %s",
            message.from_user.full_name,
        )
    except ValueError:
        await message.reply("Пожалуйста, введите корректное число.")
        logger.error(
            "ValueError for user %s: Invalid input '%s'",
            message.from_user.full_name,
            message.text,
        )
    except Exception as e:
        logger.error("Error processing count input: %s", e)
