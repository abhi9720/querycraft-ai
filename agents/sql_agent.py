from agents.base import BaseAgent

class SQLAgent(BaseAgent):
    def run(self, prompt, schema):
        full_prompt = f"""Given the following SQL schema and a user's prompt, generate a SQL query that answers the user's prompt.

Schema: {schema}

Prompt: {prompt}

SQL Query:"""
        return self.model.generate_content(full_prompt)
