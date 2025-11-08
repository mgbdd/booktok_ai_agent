import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from base_ai_agent import BaseAIAgent

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(base_dir, ".env")

load_dotenv(dotenv_path)

class GeminiAIAgent(BaseAIAgent):
    def __init__(self):
        super().__init__()
        self.llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )

if __name__ == "__main__":
    agent = GeminiAIAgent()

    book_data = {"Сила привычки": "Чарльз Дахигг"}

    result = agent.run(book_data)
    print(result)
