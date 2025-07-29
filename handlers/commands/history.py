import logging.config
from datetime import datetime

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

import keyboards.inline as kbi
import keyboards.reply as kbr
from database.model import History
from handlers.commands.callback import generate_response_message
from logger_helper.logger_helper import LOGGING_CONFIG
from state.states import HistoryState
from utils.paginator import Paginator

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("history")

router = Router()


@router.message(Command("history"))
async def cmd_history(message: types.Message, state: FSMContext) -> None:
    """
    Обработчик команды /history.
    Устанавливает состояние FSM на ожидание ввода даты.

    :param message: Сообщение, содержащее команду от пользователя.
    :param state: Контекст состояния FSM.
    """
    try:
        await state.set_state(HistoryState.history)
        await message.reply(
            text="Введите дату в формате ГГГГ-ММ-ДД:", reply_markup=kbr.to_main
        )
        logger.debug(
            "Command history processed successfully for user: %s",
            message.from_user.full_name,
        )
    except Exception as e:
        logger.error(
            "Error processing command history for user %s: %s",
            message.from_user.full_name,
            e,
        )


@router.message(HistoryState.history)
async def process_date(message: types.Message, state: FSMContext) -> None:
    """
    Обработчик ввода даты.
    Запрашивает историю поиска по указанной дате.

    :param message: Сообщение от пользователя с датой.
    :param state: Контекст состояния FSM.
    """
    try:
        input_date = datetime.strptime(message.text, "%Y-%m-%d").date()

        if input_date > datetime.now().date():
            await message.reply("Пожалуйста, введите дату не позже сегодняшнего дня.")
            return

        results = (
            History.select()
            .where(
                (History.user == message.from_user.id) & (History.date == input_date)
            )
            .dicts()
        )

        movies = list(results)

        if not movies:
            await message.answer(
                "К сожалению, ничего не найдено.", reply_markup=kbr.main
            )
            logger.info(
                "No movies found for user %s with date '%s'",
                message.from_user.full_name,
                input_date,
            )
            return

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
            "Successfully processed date input for user %s", message.from_user.full_name
        )
    except ValueError:
        await message.reply(
            "Пожалуйста, введите дату в корректном формате (ГГГГ-ММ-ДД)."
        )
    except Exception as e:
        logger.error(
            "Error processing date input for user %s",
            message.from_user.full_name,
            e,
            exc_info=True,
        )
        await message.reply(
            "Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте позже.",
            reply_markup=kbr.main,
        )
