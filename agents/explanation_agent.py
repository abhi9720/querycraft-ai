from agents.base import BaseAgent

class ExplanationAgent(BaseAgent):
    def run(self, prompt, sql):
        full_prompt = f"""Given the user's prompt and the following SQL query, provide a concise, easy-to-understand explanation of what the query does. Your explanation should be in markdown format.

        Prompt: {prompt}

        SQL Query:
        {sql}

        Explanation:"""
        return self.model.generate_content(full_prompt)
