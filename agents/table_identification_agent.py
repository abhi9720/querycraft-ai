from agents.base import BaseAgent

class TableIdentificationAgent(BaseAgent):
    def run(self, prompt, schema):
        full_prompt = f"""Given the following SQL schema and a user's prompt, identify the tables required to answer the user's question. Your output should be a comma-separated list of table names.

**Instructions:**
1.  Only list the tables that are essential to answering the prompt.
2.  Do not include any other text, explanation, or markdown.
3.  If no tables are relevant, return an empty string.

Schema:
{schema}

Prompt: {prompt}

Required Tables:"""
        response = self.model.generate_content(full_prompt)
        return response.parts[0].text.strip()
