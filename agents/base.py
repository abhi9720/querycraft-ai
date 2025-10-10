import google.generativeai as genai

class BaseAgent:
    def __init__(self):
        self.llm = genai.GenerativeModel("gemini-pro")
