import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram import Router, F
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv

from commands import FILMS_COMMAND, START_COMMAND, FILM_CREATE_COMMAND
from data import get_films, add_film, save_films
from models import Film
from keyboards import films_keyboard_markup, FilmCallback, WatchCallback, SearchCallback
from utils import is_admin

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

class SearchState(StatesGroup):
    query = State()

class MovieStates(StatesGroup):
    edit_query = State()
    edit_description = State()
    filter_criteria = State()

class FilmCreateState(StatesGroup):
    name = State()
    description = State()
    rating = State()
    genre = State()
    year = State()
    actors = State()
    poster = State()
    video = State()

class MovieDeleteState(StatesGroup):
    delete_query = State()

def AdminFilter():
    return F.from_user.id.func(lambda uid: is_admin(uid))

@dp.message(START_COMMAND)
async def start(message: types.Message):
    user_id = message.from_user.id

    if is_admin(user_id):
        await message.answer(
            "Привіт, адміністратор!👋\n\n"
            "/start — Старт бота\n"
            "/films — Список фільмів\n"
            "/create_film — Додати фільм\n"
            "/search_film — Пошук фільму\n"
            "/delete_movie — Видалити фільм\n"
            "/edit_movie — Редагувати опис\n"
            "/filter_movies — Фільтр фільмів"
        )
        return

    await message.answer(
        "Привіт!👋 Я Filmchik-Bot\n\n"
        "/start — Старт бота\n"
        "/search_film — Пошук фільму за назвою\n"
        "/filter_movies — Фільтрувати фільми за жанром, роком або актором"
    )

@dp.message(FILMS_COMMAND, AdminFilter())
async def films(message: types.Message):
    films = get_films()

    kb = InlineKeyboardBuilder()
    for film in films:
        kb.button(text=film["name"], callback_data=f"film_{film['id']}")
    kb.adjust(1)

    await message.answer("Список фільмів:", reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("film_"))
async def open_film(callback: types.CallbackQuery):
    film_id = int(callback.data.split("_")[1])
    films = get_films()
    film_data = next((f for f in films if f["id"] == film_id), None)

    if not film_data:
        await callback.answer("Помилка")
        return

    film = Film(**film_data)

    kb = InlineKeyboardBuilder()
    if film.video:
        kb.button(text="🎥 Дивитися", url=film.video)
    kb.adjust(1)

    text = (
        f"🎬 {film.name}\n"
        f"📅 {film.year}\n"
        f"⭐ {film.rating}\n"
        f"🎭 {film.genre}\n"
        f"👤 {', '.join(film.actors)}\n\n"
        f"{film.description}"
    )

    if film.poster:
        await callback.message.answer_photo(film.poster, caption=text, reply_markup=kb.as_markup())
    else:
        await callback.message.answer(text, reply_markup=kb.as_markup())
        await callback.answer()

@dp.message(FILM_CREATE_COMMAND, AdminFilter())
async def film_create(message: types.Message, state: FSMContext):
    await state.set_state(FilmCreateState.name)
    await message.answer("Введіть назву фільму:")

@dp.message(FilmCreateState.name)
async def film_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(FilmCreateState.description)
    await message.answer("Введіть опис фільму:")

@dp.message(FilmCreateState.description)
async def film_desc(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(FilmCreateState.rating)
    await message.answer("Введіть рейтинг:")

@dp.message(FilmCreateState.rating)
async def film_rating(message: types.Message, state: FSMContext):
    await state.update_data(rating=message.text)
    await state.set_state(FilmCreateState.genre)
    await message.answer("Введіть жанр:")

@dp.message(FilmCreateState.genre)
async def film_genre(message: types.Message, state: FSMContext):
    await state.update_data(genre=message.text)
    await state.set_state(FilmCreateState.year)
    await message.answer("Введіть рік:")

@dp.message(FilmCreateState.year)
async def film_year(message: types.Message, state: FSMContext):
    await state.update_data(year=message.text)
    await state.set_state(FilmCreateState.actors)
    await message.answer("Введіть акторів через кому:")

@dp.message(FilmCreateState.actors)
async def film_actors(message: types.Message, state: FSMContext):
    actors = [a.strip() for a in message.text.split(",")]
    await state.update_data(actors=actors)
    await state.set_state(FilmCreateState.poster)
    await message.answer("Вставте URL постера:")

@dp.message(FilmCreateState.poster)
async def film_poster(message: types.Message, state: FSMContext):
    await state.update_data(poster=message.text)
    await state.set_state(FilmCreateState.video)
    await message.answer("Вставте пряме посилання на відео:")

@dp.message(FilmCreateState.video)
async def film_video(message: types.Message, state: FSMContext):
    await state.update_data(video=message.text)

    film = await state.get_data()
    films = get_films()
    film["id"] = len(films)
    add_film(film)

    await message.answer("Фільм додано!")
    await state.clear()

@dp.message(Command("search_film"))
async def search_start(message: types.Message, state: FSMContext):
    await message.answer("Введіть назву фільму:")
    await state.set_state(SearchState.query)

@dp.message(SearchState.query)
async def search_action(message: Message, state: FSMContext):
    q = message.text.lower()
    films = get_films()
    results = [f for f in films if q in f["name"].lower()]

    if not results:
        await message.answer("Не знайдено")
        await state.clear()
        return

    kb = InlineKeyboardBuilder()
    for film in results:
        kb.button(text=film["name"], callback_data=f"film_{film['id']}")
    kb.adjust(1)

    await state.clear()
    await message.answer("Знайдено:", reply_markup=kb.as_markup())

@dp.message(Command("delete_movie"), AdminFilter())
async def delete_movie(message: types.Message, state: FSMContext):
    await message.answer("Введіть назву фільму:")
    await state.set_state(MovieDeleteState.delete_query)

@dp.message(MovieDeleteState.delete_query)
async def delete_action(message: types.Message, state: FSMContext):
    q = message.text.lower().strip()
    films = get_films()

    for film in films:
        film_name = film["name"].lower()

        if q in film_name:
            films.remove(film)
            save_films(films)
            await message.answer(f"Фільм «{film['name']}» видалено")
            await state.clear()
            return

    await message.answer("Не знайдено")
    await state.clear()


@dp.message(Command("edit_movie"), AdminFilter())
async def edit_movie(message: types.Message, state: FSMContext):
    await message.answer("Назва фільму:")
    await state.set_state(MovieStates.edit_query)

@dp.message(MovieStates.edit_query)
async def edit_select(message: types.Message, state: FSMContext):
    q = message.text.lower()
    films = get_films()
    matches = [f for f in films if q in f["name"].lower()]

    if not matches:
        await message.answer("Не знайдено")
        return
    if len(matches) > 1:
        txt = "\n".join(f["name"] for f in matches)
        await message.answer(txt)
        return

    await state.update_data(film=matches[0])
    await state.set_state(MovieStates.edit_description)
    await message.answer("Новий опис:")

@dp.message(MovieStates.edit_description)
async def edit_desc(message: types.Message, state: FSMContext):
    new = message.text
    films = get_films()
    data = await state.get_data()
    film = data["film"]

    for f in films:
        if f["name"] == film["name"]:
            f["description"] = new
            break

    save_films(films)
    await state.clear()
    await message.answer("Оновлено")

@dp.message(Command("filter_movies"))
async def filter_start(message: types.Message, state: FSMContext):
    await message.answer("Введіть жанр, рік або акторів:")
    await state.set_state(MovieStates.filter_criteria)

@dp.message(MovieStates.filter_criteria)
async def filter_action(message: types.Message, state: FSMContext):
    c = message.text.lower()
    films = get_films()

    res = [
        f for f in films
        if c in str(f.get("genre", "")).lower()
        or str(f.get("year", "")).lower() == c
        or any(c in actor.lower() for actor in f.get("actors", []))
    ]

    if not res:
        await message.answer("❌ Не знайдено. Спробуйте ще раз:")
        return

    if len(res) > 1:
        kb = InlineKeyboardBuilder()
        for f in res:
            kb.button(text=f["name"], callback_data=f"film_{f['id']}")
        kb.adjust(1)
        await message.answer("🔎 Знайдено кілька фільмів:", reply_markup=kb.as_markup())
        await state.clear()
        return

    f = res[0]

    kb = InlineKeyboardBuilder()
    if f.get("video"):
        kb.button(text="🎥 Дивитися", url=f["video"])
    kb.adjust(1)

    text = (
        f"🎬 <b>{f['name']}</b>\n"
        f"📅 {f.get('year', '—')}\n"
        f"⭐ {f.get('rating', '—')}\n"
        f"🎭 {f.get('genre', '—')}\n"
        f"👤 {', '.join(f.get('actors', []))}\n\n"
        f"{f.get('description', '')}"
    )

    if f.get("poster"):
        await message.answer_photo(
            f["poster"], caption=text, reply_markup=kb.as_markup(), parse_mode="HTML"
        )
    else:
        await message.answer(text, reply_markup=kb.as_markup(), parse_mode="HTML")

    await state.clear()

if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
