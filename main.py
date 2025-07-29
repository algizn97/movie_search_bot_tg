import asyncio
import logging.config
from logger_helper.logger_helper import LOGGING_CONFIG
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config_data.config import BOT_TOKEN
from handlers import router as main_router

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("main")


async def main() -> None:
    """
    Основная асинхронная функция для запуска бота.

    Настраивает логирование, создает экземпляры Bot и Dispatcher,
    подключает маршрутизатор и запускает опрос.
    """
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    dp.include_router(main_router)

    try:
        logger.info("Бот успешно запущен и работает.")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error("Ошибка при запуске бота: %s", e)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот выключен")
