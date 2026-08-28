import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

llm = ChatGoogleGenerativeAI(
    model = 'gemini-3.5-flash-lite',
    api_key = api_key,
    temperature = 0,
    request_timeout = 30.0,
    max_retries = 2
)

def get_llm_response_text(response) -> str:
    """Extract clean string text from langchain LLM response."""
    if hasattr(response, 'content'):
        content = response.content
    else:
        content = str(response)

    if isinstance(content, str):
        return content.strip()
    elif isinstance(content, list):
        extracted = []
        for block in content:
            if isinstance(block, dict):
                extracted.append(block.get("text", str(block)))
            elif hasattr(block, 'text'):
                extracted.append(block.text)
            else:
                extracted.append(str(block))
        return "".join(extracted).strip()
    return str(content).strip()