import os
from dotenv import load_dotenv
from abc import ABC, abstractmethod
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
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
        
        #TODO: TavilySearch tool, api_key в .env
        #TODO: generate description tool
        
        self.generate_ideas_tool = tool(self.generate_ideas) 
        self.make_json_answer_tool = tool(self.make_json_answer)

        self.agent = self.build_grapg()

    #TODO + написать промпт (?)
    def _call_tavily_search(self, state : AgentState) -> AgentState:
        return

    #TODO + написать промпт
    def _generate_description(self, query : str) -> str:
        return
    def _call_generate_description(self, state : AgentState) -> AgentState:
        return
    
    def _generate_ideas(self, book : str, author : str,  summary : str) -> str:
        """
        This tool generate a list of ideas that \n
        reflect the content of the given book
        """
        system_temlate = get_prompt(os.getenv("IDEAS_PROMPT"))
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_temlate),
                ("user", "{book}, {author}, {summary}")
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
    
    @abstractmethod
    def _make_json_answer(self, summary : str, ideas : str) -> dict:
        pass
    
    def _call_make_json_answer(self, state : AgentState) -> AgentState:
        try:
            summary = state["summary"]
            ideas = state["ideas"]
            result = self.make_json_answer_tool.invoke({"summary" : summary, "ideas" : ideas})
            return {
                "messages" : [AIMessage(content="Сформирован JSON ответ")],
                "full_answer": result
            }
        except Exception as e:
            print(f"Ошибка при вызове _call_make_json_answer")
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
            return {}
