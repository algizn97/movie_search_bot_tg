import logging.config
from typing import Dict, Optional

from aiogram import Router, types
from aiogram.exceptions import TelegramServerError
from aiogram.fsm.context import FSMContext

import keyboards.inline as kbi
from logger_helper.logger_helper import LOGGING_CONFIG

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("callback_logger")

router = Router(name=__name__)


def format_movie_message(movie: Dict[str, Optional[str]]) -> str:
    """
    Форматирует сообщение о фильме.

    :param movie: Словарь с информацией о фильме, содержащий ключи:
                  'title', 'description', 'rating', 'year', 'genres', 'age_rating'.
    :return: Строка с отформатированным сообщением о фильме.
    """
    return (
        f"**Название:** {movie['name']}\n\n"
        f"**Рейтинг:** {movie.get('rating', 'Нет данных')}\n"
        f"**Год:** {movie.get('year', 'Нет данных')}\n"
        f"**Жанр:** {movie.get('genres', 'Нет данных')}\n"
        f"**Возрастной рейтинг:** {movie.get('ageRating', 'Нет данных')}\n\n"
        f"**О фильме:** {movie['description']}\n"
    )


def generate_response_message(paginator) -> str:
    """
    Генерирует сообщение с информацией о фильмах для текущей страницы пагинатора.

    :param paginator: Объект пагинатора, содержащий информацию о текущих фильмах и страницах.
    :return: Форматированное сообщение о фильмах.
    """
    current_movies = paginator.get_current()
    return "\n\n".join(
        [
            f"{index + 1 + (paginator.current_page - 1) * paginator.items_per_page}. {movie['name']}\n"
            f"IMDb: {movie['rating']} | "
            f"Год: {movie['year']} | "
            f"Жанр: {''.join(movie['genres'])}"
            for index, movie in enumerate(current_movies)
        ]
    )


@router.callback_query(lambda c: c.data.startswith("select_movie:"))
async def process_movie_selection(
    callback_query: types.CallbackQuery, state: FSMContext
):
    data = await state.get_data()
    paginator = data.get("paginator")

    if paginator is None:
        await callback_query.answer(
            "Кнопка недоступна. Нажмите 'На главную'", show_alert=True
        )
        logger.warning("Paginator is None.")
        return

    try:
        selected_index = int(callback_query.data.split(":")[1])
        selected_movie = paginator.items[selected_index]

        response_message = format_movie_message(selected_movie)

        await callback_query.answer(f"Вы выбрали фильм {selected_movie['name']}")

        poster_url = selected_movie.get("poster_url")

        if poster_url and (
            poster_url.startswith("http:") or poster_url.startswith("https:")
        ):
            await callback_query.message.answer_photo(
                photo=poster_url, caption=response_message, parse_mode="Markdown"
            )
        else:
            await callback_query.message.answer(response_message, parse_mode="Markdown")

        logger.info(
            "User %s selected movie '%s'",
            callback_query.from_user.full_name,
            selected_movie["name"],
        )
    except (ValueError, IndexError) as e:
        await callback_query.answer("Ошибка выбора фильма.", show_alert=True)
        logger.warning(
            "Error selecting movie for user %s: %s",
            callback_query.from_user.full_name,
            e,
        )
    except TelegramServerError as e:
        await callback_query.answer(
            "Произошла ошибка при обработке вашего запроса.", show_alert=True
        )
        logger.error(
            "Unexpected error occurred for user %s: %s",
            callback_query.from_user.full_name,
            e,
        )


@router.callback_query(lambda c: c.data.startswith("navigate:next:"))
async def process_page_next(callback_query: types.CallbackQuery, state: FSMContext):
    """
    Обработчик нажатия кнопки 'Дальше' для навигации по страницам результатов.

    :param callback_query: Объект CallbackQuery от Aiogram.
    :param state: Контекст состояния FSM.
    """
    logging.info("Next button pressed by user %s", callback_query.from_user.full_name)

    data = await state.get_data()
    paginator = data.get("paginator")

    if paginator is None:
        await callback_query.answer(
            "Кнопка недоступна. Нажмите 'На главную'", show_alert=True
        )
        logger.warning("NoneType object has no attribute get_current")
        return

    try:
        if paginator.has_next():
            paginator.next()

            await state.update_data(paginator=paginator)

            response_message = generate_response_message(paginator)

            await callback_query.message.edit_text(
                response_message,
                reply_markup=kbi.get_movie_selection_keyboard(
                    paginator.get_current(), paginator.current_page
                ),
            )

            logger.info(
                "User %s navigated to page %d",
                callback_query.from_user.full_name,
                paginator.current_page,
            )
        else:
            await callback_query.answer("Нет больше страниц.", show_alert=True)
            logger.info(
                "User %s attempted to navigate past the last page",
                callback_query.from_user.full_name,
            )
    except Exception as e:
        logger.error("Error occurred while navigating to next page: %s", e)


@router.callback_query(lambda c: c.data.startswith("navigate:previous:"))
async def process_page_back(callback_query: types.CallbackQuery, state: FSMContext):
    """
    Обработчик нажатия кнопки 'Назад' для навигации по страницам результатов.

    :param callback_query: Объект CallbackQuery от Aiogram.
    :param state: Контекст состояния FSM.
    """
    logging.info(
        "Previous button pressed by user %s", callback_query.from_user.full_name
    )

    data = await state.get_data()
    paginator = data.get("paginator")

    if paginator is None:
        await callback_query.answer(
            "Кнопка недоступна. Нажмите 'На главную'", show_alert=True
        )
        logger.warning("NoneType object has no attribute get_current")
        return

    try:
        if paginator.has_previous():
            paginator.previous()

            await state.update_data(paginator=paginator)

            response_message = generate_response_message(paginator)

            await callback_query.message.edit_text(
                response_message,
                reply_markup=kbi.get_movie_selection_keyboard(
                    paginator.get_current(),
                    paginator.current_page,
                ),
            )
            logger.info(
                "User %s navigated to page %d",
                callback_query.from_user.full_name,
                paginator.current_page,
            )
        else:
            await callback_query.answer("Нет предыдущих страниц.", show_alert=True)
            logger.info(
                "User %s attempted to navigate before the first page",
                callback_query.from_user.full_name,
            )
    except Exception as e:
        logger.error("Error occurred while navigating to previous page: %s", e)
