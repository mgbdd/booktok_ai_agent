from typing import List, Annotated, TypedDict, Optional
from langchain_core.messages import BaseMessage
import os
from pathlib import Path

def get_filepath(filename, current_dir=Path(__file__).parent.resolve()):
    for root, dirs, files in os.walk(current_dir):
        if filename in files:
            return str(Path(root) / filename)
    return None

def get_prompt(filename):
    try:
        filepath = get_filepath(filename)
        with open(filepath, "r", encoding="utf-8") as f:
            prompt = f.read()
            return prompt
    except FileNotFoundError:
        print(f"Файл '{filename}' не был найден.")
        return ""
    except Exception as e:
        print(f"Ошибка при чтении файла {filename}: {e}")
        return ""

class FullAnswer(TypedDict):
    """
    Обязательная структура для поля full_answer (финальный JSON).
    """
    Title: str
    Author: str
    Genre: str
    Summary: str
    Ideas: List[str] # Ключ "Ideas" должен содержать List из str

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], lambda x, y: x + y] #сообщения о работе агента
    book_name: str
    author : str
    genre : str
    summary : Optional[str] #общая json строка, включающая и название, и автора, и жанр, и содержание
    ideas: Optional[str]
    full_answer: Optional[FullAnswer]