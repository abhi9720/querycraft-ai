from agents.base import BaseAgent

class SQLAgent(BaseAgent):
    def run(self, prompt, schema, tables):
        table_list = ", ".join(tables)
        full_prompt = f"""Given the following SQL schema, and a specific list of tables, write a single, syntactically correct SQL query that answers the user's prompt. Your output should be ONLY the query itself, with no other text, explanation, or markdown.

**Instructions:**
1.  **You must only use the following tables:** {table_list}.
2.  Your query **MUST** only use columns that are explicitly listed in the schema for the given tables.
3.  **DO NOT** invent column names.
4.  If the user's prompt cannot be answered with the given schema (e.g., if it refers to a column that does not exist), you MUST return only a descriptive error message starting with "Error:". For example: `Error: The prompt cannot be answered with the available schema.`
5.  Ensure the query is syntactically correct for MySQL.

Schema:
{schema}

Prompt: {prompt}

SQL Query:"""
        response = self.model.generate_content(full_prompt)
        # Clean up the response to remove any markdown formatting
        cleaned_sql = response.parts[0].text.strip()
        if cleaned_sql.startswith("```sql"):
            cleaned_sql = cleaned_sql[len("```sql"):].strip()
        if cleaned_sql.endswith("```"):
            cleaned_sql = cleaned_sql[:-len("```"):].strip()
        return cleaned_sql
