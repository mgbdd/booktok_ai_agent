import json
import requests
from typing import List, Dict, Any
import tqdm
from agents.mistral_agent import MistralAIAgent

def load_books(path: str) -> List[Dict[str, Any]]:

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("Файл должен содержать список JSON-объектов")
    return data

def get_authors(authors):
    if authors is None or authors == []:
        return "Неизвестно"
    else:
        author_list = ""
        for author in authors:
            first_name = author["first_name"]
            if author["third_name"] == None:
                middle_name = ''
            else:
                middle_name = author["third_name"]
            last_name = author["last_name"]

            if author == authors[-1]:
                author_list = author_list + f'{first_name} {middle_name} {last_name}'
            else:
                author_list = author_list + f'{first_name} {middle_name} {last_name}, '
        return author_list

def get_ai_data(title, authors):
    try:
        agent = MistralAIAgent()
        book_data = {title: authors}
        result = agent.run(book_data)
        if result is None:
            raise Exception
        return result
    except Exception as e:
        print(f"Неудачная попытка генерации контента книги {title} автора(-ов) {authors}: {e}")
        return None


def get_book_data(books):
    result_data = []
    for book in books:

        invalid_book = book["book"] is None or book["book"]["title"] is None or book["book"]["title"] == ""
        if invalid_book:
            print("Недостаточно данных")
            continue

        title = book["book"]["title"]
        authors = get_authors(book["book"]["authors"])

        result = get_ai_data(title, authors)
        if result is None:
            result_data.append(
                {
                    "book": {
                    "title": book["book"]["title"],
                    "authors": book["book"]["authors"],
                    "genre": [],
                    "description": "",
                    "key_ideas": []
                    }   
                }   
            )
            print('-')
        else:
            result_data.append(result)
            print('+')
        
    return result_data

def send_data_to_file (book_data, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(book_data, f, indent=4, ensure_ascii=False)   
        

if __name__ == "__main__":
    INPUT_FILE_PATH = "input_books.json"
    OUTPUT_FILE_PATH = "books.json"
    data = load_books(INPUT_FILE_PATH)
    book_data = get_book_data(data)
    send_data_to_file(book_data, OUTPUT_FILE_PATH)