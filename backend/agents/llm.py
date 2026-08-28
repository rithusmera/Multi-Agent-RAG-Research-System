import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

llm = ChatGoogleGenerativeAI(
    model = 'gemini-3.5-flash-lite',
    api_key = api_key,
    temperature = 0
)