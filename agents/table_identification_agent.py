from agents.base import BaseAgent

class TableIdentificationAgent(BaseAgent):
    def run(self, prompt, schema, schema_graph=None):
        """
        Identify relevant tables from the user prompt.
        If schema_graph is provided, include related tables automatically.
        """
        # Step 1: Use LLM as fallback / first-pass identification
        full_prompt = f"""Given the following SQL schema and a user's prompt, identify the tables required to answer the user's question. Your output should be a comma-separated list of table names.

**Instructions:**
1. Only list the tables that are essential to answering the prompt.
2. Do not include any other text, explanation, or markdown.
3. If no tables are relevant, return an empty string.

Schema:
{schema}

Prompt: {prompt}

Required Tables:"""
        response = self.model.generate_content(full_prompt)
        try:
            identified_tables = [t.strip() for t in response.parts[0].text.strip().split(",") if t.strip()]
        except IndexError:
            identified_tables = []

        # Step 2: Use schema_graph to include related tables (joins)
        if schema_graph:
            additional_tables = set()
            for table in identified_tables:
                related = schema_graph.get_related_tables(table)
                # Add only if prompt implies a join or combined info
                for r in related:
                    keywords = ["join", "with", "details", "info", "data"]
                    if any(k in prompt.lower() for k in keywords):
                        additional_tables.add(r)
            identified_tables = sorted(list(set(identified_tables) | additional_tables))

        return ", ".join(identified_tables)