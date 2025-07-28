import os

current_directory = os.path.dirname(os.path.abspath(__file__))
log_directory = os.path.join(current_directory, 'loggers')
os.makedirs(log_directory, exist_ok=True)
log_filename = os.path.join(log_directory, 'app.log')

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",  # Формат даты
        },
    },
    "handlers": {
        "timed_rotating_file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": log_filename,
            "when": "midnight",  # Время ротации (каждую полночь)
            "interval": 1,  # Интервал в днях
            "backupCount": 7,  # Количество сохраняемых архивов (0 - не сохранять)
            "formatter": "default",
            "encoding": "utf-8",
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "loggers": {
        "main": {
            "handlers": ["console", "timed_rotating_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "api": {
            "handlers": ["console", "timed_rotating_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "handlers_main": {
            "handlers": ["console", "timed_rotating_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "common": {
            "handlers": ["console", "timed_rotating_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "callback_logger": {
            "handlers": ["console", "timed_rotating_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "movie_search": {
            "handlers": ["console", "timed_rotating_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "movie_search_api": {
            "handlers": ["console", "timed_rotating_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "movie_by_rating_api": {
            "handlers": ["console", "timed_rotating_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "movie_by_rating": {
            "handlers": ["console", "timed_rotating_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "low_budget_movie": {
            "handlers": ["console", "timed_rotating_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "low_budget_movie_api": {
            "handlers": ["console", "timed_rotating_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "high_budget_movie": {
            "handlers": ["console", "timed_rotating_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "high_budget_movie_api": {
            "handlers": ["console", "timed_rotating_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "movie_by_genre": {
            "handlers": ["console", "timed_rotating_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "movie_by_genre_api": {
            "handlers": ["console", "timed_rotating_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "history": {
            "handlers": ["console", "timed_rotating_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "database": {
            "handlers": ["console", "timed_rotating_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "config": {
            "handlers": ["console", "timed_rotating_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "inline": {
            "handlers": ["console", "timed_rotating_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "reply": {
            "handlers": ["console", "timed_rotating_file"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}
