import logging.config

import aiohttp

from api import truncate_description
from api.api import headers, url
from logger_helper.logger_helper import LOGGING_CONFIG

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("movie_search_api")


async def search_movies(name: str, count: int) -> list:
    """
    Выполняет запрос к API для поиска фильмов по названию.

    :param name: Название фильма.
    :param count: Количество вариантов для получения.
    :return: Текстовый ответ с найденными фильмами или сообщение об их отсутствии.
    """
    url_name = f"{url}v1.4/movie/search?page=1&limit={count}&query={name}"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url_name, headers=headers) as response:
                response.raise_for_status()
                data = await response.json()
                movies = data.get("docs", [])

                filtered_movies = [movie for movie in movies if movie.get("name")]

                if filtered_movies:
                    saved_movies = []

                    for movie in filtered_movies:
                        genres = ", ".join(genre["name"] for genre in movie["genres"])
                        description = truncate_description(
                            movie["description"] or "Нет данных"
                        )
                        poster_data = movie.get("poster")
                        poster_url = (
                            poster_data.get("previewUrl")
                            if poster_data
                            else "Нет данных"
                        )
                        saved_movies.append(
                            {
                                "name": movie["name"],
                                "description": description,
                                "rating": movie.get("rating", {}).get(
                                    "imdb",
                                )
                                or "Нет данных",
                                "year": movie["year"] or "Нет данных",
                                "genres": genres or "Нет данных",
                                "ageRating": movie.get("ageRating") or "Нет данных",
                                "poster_url": poster_url or "Нет данных",
                            }
                        )
                    return saved_movies
                else:
                    return []
        except aiohttp.ClientError as e:
            logger.error("API request error: %s", e)
            return []
        except ValueError as e:
            logger.error("Data processing error: %s", e)
            return []
