import logging.config
import random

import aiohttp

from api import truncate_description
from api.api import headers, url
from logger_helper.logger_helper import LOGGING_CONFIG

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("movie_by_rating_api")


async def movie_by_rating(rating: str, count: int, genre: str) -> list:
    """
    Выполняет запрос к API для поиска фильмов по названию.

    :param genre: Жанр фильма.
    :param rating: Рейтинг фильмов/сериалов.
    :param count: Количество вариантов для получения.
    :return: Текстовый ответ с найденными фильмами или сообщение об их отсутствии.
    """
    if genre:
        url_name = f"{url}v1.4/movie?page=1&limit={count}&rating.imdb={rating}&genres.name={genre}"
    else:
        url_name = f"{url}v1.4/movie?page=1&limit={count}&rating.imdb={rating}"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url_name, headers=headers) as response:
                response.raise_for_status()
                data = await response.json()
                pages = data.get("pages", 0)

                if pages == 0:
                    logger.warning("No movies found for the given criteria.")
                    return []

                number_page = random.randrange(1, pages)
                if genre:
                    url_page = f"{url}v1.4/movie?page={number_page}&limit={count}&rating.imdb={rating}&genres.name={genre}"
                else:
                    url_page = f"{url}v1.4/movie?page={number_page}&limit={count}&rating.imdb={rating}"

                async with session.get(url_page, headers=headers) as res:
                    res.raise_for_status()
                    data_movie = await res.json()
                    movies = data_movie.get("docs", [])

                    saved_movies = []

                    for movie in movies:
                        name = movie.get("name") or movie.get("alternativeName")

                        if not name and movie.get("names"):
                            for name_obj in movie["names"]:
                                if name_obj.get("name") and name_obj["name"].strip():
                                    name = name_obj["name"]
                                    break

                        if not name:
                            continue

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
                                "name": name,
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
        except aiohttp.ClientError as e:
            logger.error("API request error: %s", e)
            return []
        except ValueError as e:
            logger.error("Data processing error: %s", e)
            return []
