import json
import os

DATA_FILE = "data.json"


def load_data():
    if not os.path.exists(DATA_FILE):
        return {"films": []}

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def normalize_ids(films: list):
    for index, film in enumerate(films):
        if film.get("id") != index:
            film["id"] = index
    return films


def get_films(film_id=None):
    data = load_data()
    films = data.get("films", [])
    films = normalize_ids(films)
    save_data({"films": films})

    if film_id is None:
        return films

    if 0 <= film_id < len(films):
        return films[film_id]
    return None


def add_film(film_data):
    data = load_data()
    films = data.get("films", [])
    films.append(film_data)
    films = normalize_ids(films)
    save_data({"films": films})


def save_films(films):
    films = normalize_ids(films)
    save_data({"films": films})


def search_films(query):
    films = get_films()
    query = query.lower()

    return [
        film for film in films
        if query in film.get("name", "").lower()
    ]


def update_film(updated_film):
    data = load_data()
    films = data.get("films", [])

    for i, film in enumerate(films):
        if film["name"].lower() == updated_film["name"].lower():
            films[i] = updated_film
            break

    films = normalize_ids(films)
    save_data({"films": films})
