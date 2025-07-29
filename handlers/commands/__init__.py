__all__ = ("router",)

from aiogram import Router

from .callback import router as callback
from .handlers_main import router as handlers
from .high_budget_movie import router as high_budget_movie
from .history import router as history
from .low_budget_movie import router as low_budget_movie
from .movie_by_genre import router as movie_by_genre
from .movie_by_rating import router as movie_by_rating
from .movie_search import router as movie_search

router = Router(name=__name__)
router.include_router(handlers)
router.include_router(callback)
router.include_router(movie_search)
router.include_router(movie_by_genre)
router.include_router(movie_by_rating)
router.include_router(low_budget_movie)
router.include_router(high_budget_movie)
router.include_router(history)
