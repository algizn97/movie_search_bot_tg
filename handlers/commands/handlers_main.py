import logging.config

from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

import keyboards.reply as kbr
from database.model import User
from logger_helper.logger_helper import LOGGING_CONFIG

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("handlers_main")

router = Router(name=__name__)


@router.message(Command("start", "hello-world"))
@router.message(F.text.lower() == "привет")
async def cmd_start(message: types.Message) -> None:
    """
    Обработчик команды /start или /hello-world, а также текста 'привет'.

    :param message: Сообщение от пользователя.
    """
    user_id = message.from_user.id
    username = message.from_user.username
    try:
        User.get_or_create(user_id=user_id, defaults={"username": username})
        await message.answer(
            text="Добро пожаловать в Kinopoisk!\n"
            "Все топовые новинки, сериалы, аниме, мультфильмы найдете у нас 😉",
            reply_markup=kbr.main,
        )
        logger.debug(
            "Command start processed successfully for user: %s",
            message.from_user.full_name,
        )
    except Exception as e:
        logger.error("Error processing command start: %s", e)
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")


@router.message(F.text == "На главную")
async def cmd_to_main(message: types.Message, state: FSMContext):
    """
    Обработчик команды /to_main.
    Сбрасывает текущее состояние FSM.

    :param message: Сообщение от пользователя.
    :param state: Контекст состояния FSM.
    """
    try:
        await state.clear()
        await message.answer("Выбери пункт меню...", reply_markup=kbr.main)
        logger.debug(
            "Command to_main processed successfully for user: %s",
            message.from_user.full_name,
        )
    except Exception as e:
        logger.error("Error processing command to_main: %s", e)


@router.message(Command("help"))
async def cmd_help(message: types.Message, state: FSMContext):
    """
    Обработчик команды /help.
    Сбрасывает текущее состояние FSM.

    :param message: Сообщение от пользователя.
    :param state: Контекст состояния FSM.
    """
    try:
        await state.clear()
        await message.answer(
            text="Используйте одну из следующих команд:\n"
            "/movie_search - Поиск фильма/сериала по названию\n"
            "/movie_by_genre - Поиск фильма/сериала по жанру\n"
            "/movie_by_rating - Поиск фильмов/сериалов по рейтингу\n"
            "/low_budget_movie - Поиск фильмов/сериалов с низким бюджетом\n"
            "/high_budget_movie - Поиск фильмов/сериалов с высоким бюджетом\n"
            "/history - История запросов"
        )
        logger.debug(
            "Command help processed successfully for user: %s",
            message.from_user.full_name,
        )
    except Exception as e:
        logger.error("Error processing command help: %s", e)
        await message.answer(
            "Произошла ошибка. Пожалуйста, попробуйте позже.", reply_markup=kbr.main
        )


@router.message(Command("cancel"))
@router.message(lambda message: message.text.casefold() in ["cancel", "отмена"])
async def cmd_cancel(message: types.Message, state: FSMContext) -> None:
    """
    Обработчик команды /cancel или текста "cancel"/"отмена".
    Сбрасывает текущее состояние FSM и информирует пользователя.

    :param message: Сообщение от пользователя.
    :param state: Контекст состояния FSM.
    """
    current_state = await state.get_state()

    if current_state is None:
        await message.reply(
            text="Хорошо, но ничего не происходило.", reply_markup=kbr.main
        )
        logger.debug("Cancel command received but no active state.")
        return

    try:
        await state.clear()
        await message.answer("Команда отменена.", reply_markup=kbr.main)
        logger.debug("Command cancel executed successfully. State cleared.")
    except Exception as e:
        logger.error("Error while cancelling command: %s", e)
        await message.answer(
            "Произошла ошибка при отмене. Пожалуйста, попробуйте позже.",
            reply_markup=kbr.main,
        )
