from aiogram.filters import Command
from  aiogram.types.bot_command import BotCommand

START_COMMAND = Command('start')
FILMS_COMMAND = Command('films')
FILM_CREATE_COMMAND = Command("create_film")
FILM_SEARCH_COMMAND = Command('film_search')
EDIT_MOVIE_COMMAND = Command("edit_movie")
FILTER_MOVIES_COMMAND = Command("filter_movies")

START_BOT_COMMAND = BotCommand(command='start', description='Почати розмову')
FILMS_BOT_COMMAND = BotCommand(command='films', description='Перегляд списку фільмів')
FILM_CREATE_BOT_COMMAND = BotCommand(command='create_film', description='Додати фільм')
FILM_SEARCH_BOT_COMMAND = BotCommand(command='film_search', description='Знайти фільм за назвою')
FILM_DELETED_BOT_COMMAND = BotCommand(command='delete_movie', description='Видалити фільм за назвою')
EDIT_MOVIE_COMMAND = BotCommand(command='edit_movie', description='Редагувати фільм')
FILTER_MOVIES_COMMAND = BotCommand(command='filter_movies', description='Фільтрувати фільми за жанром або роком випуску')
