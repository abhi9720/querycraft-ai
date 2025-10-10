import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

class QueryExplanationAgent:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-pro')

    def run(self, prompt):
        full_prompt = f"""Explain the following SQL query in plain English.

Query: {prompt}

Explanation:"""
        return self.model.generate_content(full_prompt)
