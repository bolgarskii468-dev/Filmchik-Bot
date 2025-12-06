from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder



class FilmCallback(CallbackData, prefix="film"):
    id: int

class WatchCallback(CallbackData, prefix="watch"):
    id: int

class SearchCallback(CallbackData, prefix="search"):
    id: int


def films_keyboard_markup(films: list) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    for idx, film in enumerate(films):
        kb.button(
            text=film.get("title", film.get("name", "Фільм")),
            callback_data=FilmCallback(id=idx).pack()
        )
        kb.button(
            text="🎥 Дивитися",
            callback_data=WatchCallback(id=idx).pack()
        )

    kb.adjust(2)
    return kb.as_markup()



def search_results_keyboard(films: list) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    for index, film in enumerate(films):
        kb.button(
            text=film.get("name", film.get("title", "Фільм")),
            callback_data=SearchCallback(id=index).pack()
        )

    kb.adjust(1)
    return kb.as_markup()
