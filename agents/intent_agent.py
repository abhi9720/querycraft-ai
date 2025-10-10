from agents.base import BaseAgent

class IntentAgent(BaseAgent):
    def run(self, prompt):
        full_prompt = f"""Determine the intent of the following prompt. The two possible intents are: GENERATE_SQL and EXPLAIN_SQL.

Prompt: {prompt}

Intent:"""
        return self.model.generate_content(full_prompt)
