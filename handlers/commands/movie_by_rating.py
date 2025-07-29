import logging.config
from typing import Optional

from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

import keyboards.inline as kbi
import keyboards.reply as kbr
from api.movie_by_rating_api import movie_by_rating
from database.model import History, User
from handlers.commands.callback import generate_response_message
from logger_helper.logger_helper import LOGGING_CONFIG
from state.states import Rating
from utils.paginator import Paginator

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("movie_by_rating")

router = Router(name=__name__)


@router.message(Command("movie_by_rating"))
@router.message(F.text == "🔍 Поиск фильмов/сериалов по рейтингу")
async def cmd_movie_by_rating(message: types.Message, state: FSMContext) -> None:
    """
    Обработчик команды /movie_by_rating.
    Устанавливает состояние FSM на ожидание ввода названия рейтинга.

    :param message: Сообщение, содержащее команду от пользователя.
    :param state: Контекст состояния FSM.
    """
    try:
        await state.set_state(Rating.rating)
        await message.answer(
            text="Введите рейтинг(например 7, 8 или 7.2-8):", reply_markup=kbr.cancel
        )
        logger.debug(
            "Command movie_by_rating processed successfully for user: %s",
            message.from_user.full_name,
        )
    except Exception as e:
        logger.error("Error processing command movie_by_rating: %s", e)


@router.message(Rating.rating)
async def process_rating(message: types.Message, state: FSMContext) -> None:
    """
    Обработчик ввода рейтинга.

    Сохраняет введенный пользователем рейтинг в состоянии и запрашивает
    у пользователя, хочет ли он выбрать жанр фильма.
    Проверяет корректность введенного бюджета.

    :param message: Сообщение от пользователя с рейтингом.
    :param state: Контекст состояния FSM, который используется для хранения
                  данных о текущем состоянии взаимодействия с пользователем.
    """
    try:
        rating_input = message.text

        if "-" in rating_input:
            min_rating, max_rating = map(float, rating_input.split("-"))
            if not (0 <= min_rating <= max_rating <= 10):
                await message.reply(
                    "Пожалуйста, введите корректный диапазон рейтинга от 0 до 10."
                )
                return
            await state.update_data(rating=rating_input)
        else:
            rating = float(rating_input)
            if not (0 <= rating <= 10):
                await message.reply("Пожалуйста, введите рейтинг от 0 до 10.")
                return
            await state.update_data(rating=rating)
        await message.answer(
            "Хотите выбрать жанр фильма?", reply_markup=kbr.main_menu_keyboard
        )
        await state.set_state(Rating.ask_genre)
        logger.debug(
            "Rating input processed successfully for user: %s, rating: %s",
            message.from_user.full_name,
            message.text,
        )
    except ValueError:
        await message.reply("Пожалуйста, введите корректный рейтинг или диапазон.")
        logger.error(
            "Invalid input for rating from user: %s", message.from_user.full_name
        )
    except Exception as e:
        await message.answer("Произошла ошибка при обработке вашего рейтинга.")
        logger.error("Error processing rating: %s", e)


@router.message(Rating.ask_genre)
async def ask_genre_response(message: types.Message, state: FSMContext) -> None:
    """
    Обработчик ответа пользователя на вопрос о выборе жанра.

    Запрашивает у пользователя, хочет ли он выбрать жанр. В зависимости от
    ответа пользователя (да/нет), переходит к соответствующему состоянию.

    :param message: Сообщение от пользователя с ответом на вопрос о выборе жанра.
    :param state: Контекст состояния FSM.
    """
    try:
        user_response = message.text.lower()

        if user_response == "да":
            await message.answer(
                "Выберите жанр:", reply_markup=await kbr.reply_genres()
            )
            await state.set_state(Rating.genre)
            logger.info("The user has selected: 'Yes' for the genre selection.")
        elif user_response == "нет":
            await message.answer(
                "Сколько вариантов вы хотите получить?", reply_markup=kbr.to_main
            )
            await state.set_state(Rating.count)
            logger.info(
                "The user has selected: 'No' and requested the number of results."
            )
        else:
            await message.reply(
                "Пожалуйста, выберите один из вариантов: 'Да', 'Нет' или 'Отмена'."
            )
            logger.warning("The user entered an incorrect response: %s", message.text)
    except ValueError as e:
        await message.reply(
            "Произошла ошибка при обработке вашего ответа. Пожалуйста, попробуйте еще раз."
        )
        logger.error("Error in ask_genre_response: %s", e)


@router.message(Rating.genre)
async def process_genre(message: types.Message, state: FSMContext) -> None:
    """
    Обработчик ввода жанра.

    Сохраняет выбранный пользователем жанр и запрашивает количество
    вариантов фильмов для отображения.

    :param message: Сообщение от пользователя с выбранным жанром.
    :param state: Контекст состояния FSM.
    """
    try:
        await state.update_data(genre=message.text.lower())
        await state.set_state(Rating.count)
        await message.answer(
            "Сколько вариантов вы хотите получить?", reply_markup=kbr.to_main
        )
        logger.debug(
            "Genre input processed successfully for user: %s, genre: %s",
            message.from_user.full_name,
            message.text,
        )
    except Exception as e:
        logger.error("Error processing genre input: %s", e)


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


@router.message(Rating.count)
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
        rating = data.get("rating")
        genre = data.get("genre")
        movies = await movie_by_rating(rating, count, genre)

        if not movies:
            await message.answer(
                "К сожалению, ничего не найдено.", reply_markup=kbr.main
            )
            logger.info(
                "No movies found for user %s with rating '%s'",
                message.from_user.full_name,
                rating,
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
            "Successfully processed movie count input for user %s",
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
        logger.error("Error processing movie count input: %s", e)
