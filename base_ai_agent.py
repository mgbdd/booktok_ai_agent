import os
from dotenv import load_dotenv
from abc import ABC, abstractmethod
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain.tools import tool
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from utils import AgentState, get_prompt
from langchain_tavily import TavilySearch
from typing import List


load_dotenv()

class BaseAIAgent(ABC):
    def __init__(self):
        # !!! для каждого наследника добавить llm
        self.llm = None
        
        self.generate_description_tool = tool(self._generate_description)
        self.generate_ideas_tool = tool(self._generate_ideas) 
        self.make_json_answer_tool = tool(self._make_json_answer)

        self.agent = self._build_grapg()
    

    def _call_tavily_search(self, state: AgentState) -> AgentState:
        try:
            search_tool = TavilySearch(api_key=os.getenv("TAVILY_API_KEY"), max_results=5)
            name = state['book_name']
            author = state['author']
            summary_query = f"Описание книги {name} автора {author}"
            summary = search_tool.invoke(summary_query)
            answer = ''
            for result in summary['results']:
                answer = answer + '\n' + result['content']

            genre_query = f"Жанр книги {name} автора {author}"
            genre = search_tool.invoke(genre_query)
            genre_answer = ''
            for result in genre['results']:
                genre_answer = genre_answer + '\n' + result['content']


            return {
                "messages": [AIMessage(content=f"Найдены данные Tavily")],
                "genre" : genre_answer,
                "summary": answer
            }
        except Exception as e:
            print(f"Ошибка в _call_tavily_search: {e}")
            return {
                "messages": [AIMessage(content="Ошибка при поиске информации о книге")],
                "genre" : None,
                "summary": None
            }

    
    def _generate_description(self, summary: str, book: str, author: str, genre : str) -> str:
        """
        Эта функция генерирует жанр и краткое описание заданной книги, которое
        соответствует данным, найденным в интернете
        """
        try:
            system_template = get_prompt(os.getenv("SUMMARY_PROMPT"))

            prompt = ChatPromptTemplate.from_messages([
                ("system", system_template),
                ("user", f"Книга {book} автора {author}. Информация о жанре: {genre}. Информация о книге из Интернета: {summary}")
            ])

            chain = prompt | self.llm | StrOutputParser()
            result = chain.invoke({"book": book, "author": author, "genre": genre, "summary": summary})
            return result
        except Exception as e:
            print(f"Ошибка в _generate_description: {e}")
            return "Описание не удалось сгенерировать."


    def _call_generate_description(self,  state : AgentState) -> AgentState:
        try:
            book = state["book_name"]
            author = state["author"]
            summary = state["summary"]
            genre = state["genre"]
            full_result = self.generate_description_tool.invoke({"summary" : summary, "book" : book, "author" : author, "genre" : genre})            
            if full_result == 'Описание не удалось сгенерировать.':
                raise Exception
            new_genre, new_summary = full_result.split(sep=";")
            return {
                "messages": [AIMessage(content="Сгенерировано описание")],
                "genre" : new_genre,
                "summary" : new_summary
            }
        except Exception as e:
            print(f"Ошибка при вызове _call_generate_description: {e}")
            return {
                "messages": [AIMessage(content="Попытка сгенерировать описание")],
                "genre" : None,
                "summary": None
            }
    
    def _generate_ideas(self, book : str, author : str,  summary : str) -> str:
        """
        Эта функция генерирует список ключевых идей книги
        """
        system_temlate = get_prompt(os.getenv("IDEAS_PROMPT"))
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_temlate),
                ("user", f"Книга: {book}, автор: {author}, краткое содержание: {summary}")
            ]
        )
        chain = prompt | self.llm | StrOutputParser()
        result = chain.invoke({"book" : book, "author" : author, "summary" : summary})
        return result
    
    def _call_generate_ideas(self,  state : AgentState) -> AgentState:
        try:
            book = state["book_name"]
            author = state["author"]
            summary = state["summary"]
            result = self.generate_ideas_tool.invoke({"book" : book, "author" : author, "summary" : summary})
            return {
                "messages": [AIMessage(content="Сгенерированы идеи")],
                "ideas" : result
            }
        except Exception as e:
            print(f"Ошибка при вызове _call_generate_ideas: {e}")
            return {
                "messages": [AIMessage(content="Попытка сгенерировать идеи")],
                "ideas": None
            }
    
    def _make_json_answer(self, book : str, author : str, genre : str, summary : str, ideas : str) -> dict:
        """
        Эта функция объединяет предыдущие результаты в единый json ответ
        """
        system_template = get_prompt(os.getenv("JSON_PROMPT"))
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_template),
                ("user", "{book}, {author}, {genre}, {summary}, {ideas}")
            ]
        )
        chain = prompt | self.llm | JsonOutputParser()
        result = chain.invoke({"book" : book, "author" : author, "genre" : genre, "summary" : summary, "ideas" : ideas})
        return result
    
    def _call_make_json_answer(self, state : AgentState) -> AgentState:
        try:
            book = state["book_name"]
            author = state["author"]
            summary = state["summary"]
            ideas = state["ideas"]
            genre = state["genre"]
            result = self.make_json_answer_tool.invoke({"book": book, "author": author, "genre": genre, "summary" : summary, "ideas" : ideas})
            return {
                "messages" : [AIMessage(content="Сформирован JSON ответ")],
                "full_answer": result
            }
        except Exception as e:
            print(f"Ошибка при вызове _call_make_json_answer: {e}")
            return {
                "messages": [AIMessage(content="Попытка формирования единого JSON ответа")], 
                "full_answer": None
            }
        
    
    def _build_grapg(self):
        graph_builder = StateGraph(AgentState)
        graph_builder.add_node("tavily", self._call_tavily_search)
        graph_builder.add_node("generate_description", self._call_generate_description)
        graph_builder.add_node("generate_ideas", self._call_generate_ideas)
        graph_builder.add_node("make_json_answer", self._call_make_json_answer)

        graph_builder.set_entry_point("tavily")
        graph_builder.add_edge("tavily", "generate_description")
        graph_builder.add_edge("generate_description", "generate_ideas")
        graph_builder.add_edge("generate_ideas", "make_json_answer")
        graph_builder.add_edge("make_json_answer", END)
        agent = graph_builder.compile()
        return agent
    
    def run(self, book_data : dict):
        book, author = list(book_data.items())[0]
        initial_state = {
            "messages": [HumanMessage(content=book)],
            "book_name": book, 
            "author": author, 
            "genre" : None, 
            "summary": None, 
            "ideas": None,
            "full_answer": None
        }
        try:
            result = self.agent.invoke(initial_state)
            full_result = result.get("full_answer", {})
            return full_result
        except Exception as e:
            print(f"Ошибка при вызове agent.invoke: {e}")  
            return None
