import os
from langchain_mistralai import ChatMistralAI
from base_ai_agent import BaseAIAgent
from dotenv import load_dotenv

load_dotenv()

class MistralAIAgent(BaseAIAgent):
    def __init__(self):
        super().__init__()
        self.llm = ChatMistralAI(
            model=os.getenv("MISTRAL_MODEL"),
            temperature=0.7,
            api_key=os.getenv("MISTRAL_API_KEY")
        )

