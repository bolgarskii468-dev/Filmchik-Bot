from aiogram.fsm.state import StatesGroup, State

class FilmCreateState(StatesGroup):
    name = State()
    year = State()
    rating = State()
    genre = State()
    actors = State()
    description = State()
    poster = State()