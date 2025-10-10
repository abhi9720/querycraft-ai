from agents.base import BaseAgent

class ColumnPruneAgent(BaseAgent):
    def run(self, prompt, schema):
        full_prompt = f"""Given the following SQL schema, determine which tables are relevant to the user's prompt and remove any columns that are not relevant to the user's prompt. Retain all primary and foreign key columns.

Schema: {schema}

Prompt: {prompt}

Relevant Tables:"""
        return self.model.generate_content(full_prompt)
