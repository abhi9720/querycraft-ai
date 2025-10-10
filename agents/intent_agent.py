import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

class IntentAgent:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-pro')

    def run(self, prompt):
        full_prompt = f"""Determine the intent of the following prompt. The two possible intents are: GENERATE_SQL and EXPLAIN_SQL.

Prompt: {prompt}

Intent:"""
        return self.model.generate_content(full_prompt)
