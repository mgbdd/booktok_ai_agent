import os
from langchain_google_genai import ChatGoogleGenerativeAI
from base_ai_agent import BaseAIAgent



class GeminiAIAgent(BaseAIAgent):
    def __init__(self):
        super().__init__()
        self.llm = ChatGoogleGenerativeAI(
        model=os.getenv("GOOGLE_MODEL"),
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )
