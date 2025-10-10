import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

class ColumnPruneAgent:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-pro')

    def run(self, prompt, schema):
        full_prompt = f"""Given the following SQL schema, determine which columns are relevant to the user's prompt and return a pruned schema.

Schema: {schema}

Prompt: {prompt}

Pruned Schema:"""
        return self.model.generate_content(full_prompt)
