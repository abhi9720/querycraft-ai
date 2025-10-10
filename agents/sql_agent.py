from agents.base import BaseAgent

class SQLAgent(BaseAgent):
    def run(self, prompt, schema):
        full_prompt = f"""Given the following SQL schema, write a single, syntactically correct SQL query that answers the user's prompt. Your output should be ONLY the query itself, with no other text, explanation, or markdown.

**Instructions:**
1.  Only use the columns present in the provided schema.
2.  Do not invent new column names that are not in the schema.
3.  Ensure the query is syntactically correct for MySQL.

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
