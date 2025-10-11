import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

class BaseAgent:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        model_name = os.getenv("GEMINI_MODEL")

        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set.")
        if not model_name:
            raise ValueError("GEMINI_MODEL environment variable not set.")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
