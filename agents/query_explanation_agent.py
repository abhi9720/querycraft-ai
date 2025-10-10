from agents.base import BaseAgent

class QueryExplanationAgent(BaseAgent):
    def run(self, prompt, query):
        full_prompt = f"""Given the following SQL query and the user's prompt, provide a natural language explanation of the query.

Query: {query}

Prompt: {prompt}

Explanation:"""
        return self.model.generate_content(full_prompt)
