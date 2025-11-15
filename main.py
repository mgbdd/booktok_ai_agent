from dotenv import load_dotenv
from utils import get_filepath, load_books
import os
from generate_content import process_books, save_book_content
from send_book_data import build_payload_from_list, send_book_data

if __name__ == "__main__":
    load_dotenv()
    
    input = get_filepath(os.getenv("INPUT_FILE_PATH"))
    output = get_filepath(os.getenv("OUTPUT_FILE_PATH"))

    # генерация контента
    data = load_books(input)
    book_data = process_books(data)
    save_book_content(book_data, output)

    #отправка контента
    data_to_send = load_books(output)
    payload = build_payload_from_list(data_to_send)
    url = os.getenv("URL")
    send_book_data(payload, url)