from agents.base import BaseAgent

class ColumnPruneAgent(BaseAgent):
    def run(self, prompt, schema):
        full_prompt = f"""Given the following SQL schema, determine which tables are relevant to the user's prompt and return a new schema containing only the relevant tables and columns. Retain all primary and foreign key columns for the relevant tables.

**Instructions:**
1. Analyze the user's prompt to identify the necessary information.
2. From the original schema, select only the tables that are required to answer the prompt.
3. For the selected tables, include all primary key and foreign key columns.
4. Include other columns from the selected tables only if they are directly mentioned or implied in the user's prompt.
5. Your output should be ONLY the pruned SQL schema, in `CREATE TABLE` format. Do not include any other text or explanation.

Original Schema:
{schema}

Prompt: {prompt}

Pruned SQL Schema:"""
        response = self.model.generate_content(full_prompt)
        return response.parts[0].text.strip()
