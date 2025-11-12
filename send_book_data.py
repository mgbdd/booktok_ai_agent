import json
import requests
from typing import List, Dict, Any

def load_books(path: str) -> List[Dict[str, Any]]:

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("Файл должен содержать список JSON-объектов")
    return data


def build_payload_from_list(books: List[Dict[str, Any]]) -> dict:
    items = [build_payload(book) for book in books]
    return {"items": items}

def build_payload(book_data: dict) -> dict:
    book = book_data.get("book", {})

    # --- Авторы ---
    authors = []
    for author in book.get("authors", []):
        authors.append({
            "first_name": author.get("first_name"),
            "second_name": author.get("last_name"),  # last_name → second_name
            "third_name": author.get("third_name")
        })

    # --- Жанры ---
    genres = [{"name": g} for g in book.get("genre", [])]

    # --- Карточки (ключевые идеи) ---
    cards = [{"content": idea} for idea in book.get("key_ideas", [])]

    # --- Формируем итог ---
    return {
        "title": book.get("title"),
        "description": book.get("description"),
        "authors": authors,
        "genres": genres,
        "cards": cards
    }


def send_book_data(payload: dict, url: str, timeout: int = 10) -> requests.Response:
    """
    Отправляет готовый payload POST-запросом на указанный URL.
    Возвращает объект requests.Response.
    """
    headers = {"Content-Type": "application/json; charset=utf-8"}

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=timeout)
        response.raise_for_status()
        print(f"✅ Успешно отправлено! Статус: {response.status_code}")
        return response
    except requests.RequestException as e:
        print(f"❌ Ошибка при отправке запроса: {e}")
        raise


if __name__ == "__main__":
    FILE_PATH = "books.json"
    data = load_books(FILE_PATH)
    payload = build_payload_from_list(data)
    
    url = "https://194.87.213.141/"

    send_book_data(payload, url)
    
