import logging.config
from typing import Optional

from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

import keyboards.inline as kbi
import keyboards.reply as kbr
from api.high_budget_movie_api import high_budget_movie
from database.model import History, User
from handlers.commands.callback import generate_response_message
from logger_helper.logger_helper import LOGGING_CONFIG
from state.states import HighBudget
from utils.paginator import Paginator

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("high_budget_movie")

router = Router(name=__name__)


@router.message(Command("high_budget_movie"))
@router.message(F.text == "🔍 Поиск фильмов/сериалов с высоким бюджетом")
async def cmd_low_budget_movie(message: types.Message, state: FSMContext) -> None:
    """
    Обработчик команды /high_budget_movie.
    Устанавливает состояние FSM на ожидание ввода бюджета.

    :param message: Сообщение, содержащее команду от пользователя.
    :param state: Контекст состояния FSM.
    """
    try:
        await state.set_state(HighBudget.budget)
        await message.answer(
            text="Введите максимальный бюджет от 200 млн (например 200000000-666666666):",
            reply_markup=kbr.cancel,
        )
        logger.debug(
            "Command high_budget_movie processed successfully for user: %s",
            message.from_user.full_name,
        )
    except Exception as e:
        logger.error("Error processing command high_budget_movie: %s", e)


@router.message(HighBudget.budget)
async def process_budget(message: types.Message, state: FSMContext) -> None:
    """
    Обработчик ввода бюджета.

    Сохраняет введенный пользователем бюджет в состоянии и запрашивает
    у пользователя, хочет ли он выбрать жанр фильма.
    Проверяет корректность введенного бюджета.

    :param message: Сообщение от пользователя с диапазоном бюджета.
    :param state: Контекст состояния FSM, который используется для хранения
                  данных о текущем состоянии взаимодействия с пользователем.
    """
    try:
        budget_range = message.text.split("-")

        if len(budget_range) != 2:
            await message.reply("Пожалуйста, введите бюджет в формате 'от-до'.")
            logger.warning(
                "User %s entered incorrect budget format: %s",
                message.from_user.full_name,
                message.text,
            )
            return

        try:
            min_budget = int(budget_range[0])
            max_budget = int(budget_range[1])
            logger.debug(
                "Parsed budget values - Min: %d, Max: %d", min_budget, max_budget
            )
        except ValueError:
            await message.reply(
                "Пожалуйста, введите корректные числовые значения для бюджета."
            )
            logger.warning(
                "User %s provided non-numeric budget values: %s",
                message.from_user.full_name,
                message.text,
            )
            return

        if min_budget < 200_000_000 or max_budget < min_budget:
            await message.reply(
                "Пожалуйста, убедитесь, что минимальный бюджет больше 200 миллионов и максимальный больше минимального."
            )
            logger.warning(
                "User %s provided budget out of range: %s",
                message.from_user.full_name,
                message.text,
            )
            return

        await state.update_data(budget=message.text)
        await message.answer(
            "Хотите выбрать жанр фильма?", reply_markup=kbr.main_menu_keyboard
        )
        await state.set_state(HighBudget.ask_genre)
        logger.debug(
            "Budget input processed successfully for user: %s, budget: %s",
            message.from_user.full_name,
            message.text,
        )
    except Exception as e:
        await message.reply("Произошла ошибка при обработке вашего бюджета.")
        logger.error(
            "Error processing budget for user %s: %s",
            message.from_user.full_name,
            e,
            exc_info=True,
        )


@router.message(HighBudget.ask_genre)
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
            await state.set_state(HighBudget.genre)
            logger.info("The user has selected: 'Yes' for the genre selection.")
        elif user_response == "нет":
            await message.answer(
                "Сколько вариантов вы хотите получить?", reply_markup=kbr.to_main
            )
            await state.set_state(HighBudget.count)
            logger.info(
                "The user has selected: 'No' and requested the number of results."
            )
        else:
            await message.reply(
                "Пожалуйста, выберите один из вариантов: 'Да', 'Нет' или 'Отмена'."
            )
            logger.warning("The user entered an incorrect response: %s", message.text)
    except Exception as e:
        await message.reply(
            "Произошла ошибка при обработке вашего ответа. Пожалуйста, попробуйте еще раз."
        )
        logger.error("Error in ask_genre_response: %s", e)


@router.message(HighBudget.genre)
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
        await state.set_state(HighBudget.count)
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


@router.message(HighBudget.count)
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
        budget = data.get("budget")
        genre = data.get("genre")
        movies = await high_budget_movie(budget, count, genre)

        if not movies:
            await message.answer(
                "К сожалению, ничего не найдено.", reply_markup=kbr.main
            )
            logger.info(
                "No movies found for user %s with budget '%s'",
                message.from_user.full_name,
                budget,
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
        logger.error("Error processing movie budget input: %s", e)
