import logging.config

import requests

from config_data.config import RAPID_API_KEY
from logger_helper.logger_helper import LOGGING_CONFIG

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("api")

url = "https://api.kinopoisk.dev/"
headers = {"accept": "application/json", "X-API-KEY": RAPID_API_KEY}


def fetch_data():
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        logger.debug("Успешный запрос к API: %s", response.status_code)
    except (
        requests.exceptions.RequestException
    ) as e:  # Fixed: changed to catch RequestException
        logger.error("Ошибка при выполнении запроса: %s", e)
    except ValueError as e:
        logger.error("Ошибка при декодировании JSON: %s", e)


fetch_data()
