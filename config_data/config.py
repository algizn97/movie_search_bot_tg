import os
from dotenv import load_dotenv, find_dotenv
import logging.config
from logger_helper.logger_helper import LOGGING_CONFIG

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("config")


if not find_dotenv():
    logger.error("Переменные окружения не загружены, так как отсутствует файл .env")
    exit(1)
else:
    load_dotenv()
    logger.info("Файл .env успешно загружен.")

BOT_TOKEN = os.getenv("BOT_TOKEN")
RAPID_API_KEY = os.getenv("RAPID_API_KEY")

if not BOT_TOKEN or not RAPID_API_KEY:
    logger.error("Ошибка: Необходимо установить переменные окружения BOT_TOKEN и RAPID_API_KEY в файле .env")
    exit(1)

logger.info("Переменные окружения успешно загружены.")