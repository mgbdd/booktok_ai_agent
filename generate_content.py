import json
from agents.mistral_agent import MistralAIAgent
from agents.gemini_agent import GeminiAIAgent
import os

def get_authors(authors):
    """
    Парсинг авторов книг из json
    """
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

            if author["last_name"] == None:
                last_name = ''
            else:
                last_name = author["last_name"]
            # last_name = author["last_name"]

            if author == authors[-1]:
                author_list = author_list + f'{first_name} {middle_name} {last_name}'
            else:
                author_list = author_list + f'{first_name} {middle_name} {last_name}, '
        return author_list

def init_agent():
    provider = os.getenv("AI_PROVIDER")
    match provider:
        case "mistral":
            return MistralAIAgent()
        case "google":
            return GeminiAIAgent()
        case _:
            return MistralAIAgent()

def get_ai_data(title, authors):
    """
    Вызов AI-агента
    """
    try:
        agent = init_agent()
        book_data = {title: authors}
        result = agent.run(book_data)
        if result is None:
            raise Exception
        return result
    except Exception as e:
        print(f"Неудачная попытка генерации контента книги {title} автора(-ов) {authors}: {e}")
        return None


def process_books(books):
    """
    Главная функция генерации контента по книгам
    """
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
            #print('-')
        else:
            result_data.append(result)
            print('+')
        
    return result_data

def save_book_content (book_data, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(book_data, f, indent=4, ensure_ascii=False)   
        