import os
from langchain_mistralai import ChatMistralAI
from dotenv import load_dotenv
from base_ai_agent import BaseAIAgent

load_dotenv()

class MistralAIAgent(BaseAIAgent):
    def __init__(self):
        super().__init__()
        self.llm = ChatMistralAI(
            model="mistral-small-latest",
            temperature=0.7,
            api_key=os.getenv("MISTRAL_API_KEY")
        )

if __name__ == "__main__":
    agent = MistralAIAgent()

    book_data = {"Сила привычки": "Чарльз Дахигг"}

    result = agent.run(book_data)
    print(result)