import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

class TableAgent:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-pro')

    def run(self, prompt, schema):
        full_prompt = f"""Given the following SQL schema, determine which tables are relevant to the user's prompt.

Schema: {schema}

Prompt: {prompt}

Relevant Tables:"""
        return self.model.generate_content(full_prompt)
