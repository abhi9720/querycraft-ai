from agents.base import BaseAgent

class TableAgent(BaseAgent):
    def run(self, prompt, schema):
        full_prompt = f"""Given the following SQL schema, determine which tables are relevant to the user's prompt.

Schema: {schema}

Prompt: {prompt}

Relevant Tables:"""
        response = self.model.generate_content(full_prompt)
        return response.parts[0].text.strip()
