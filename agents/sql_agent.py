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
        return self._clean_sql(response.parts[0].text)

    def modify_sql(self, original_sql, modification_prompt, schema, tables):
        table_list = ", ".join(tables)
        full_prompt = f"""Given an original SQL query, the database schema, a list of the tables used in that query, and a user's request, modify the query to meet the user's needs.

**Instructions:**
1.  Your output must be ONLY the modified SQL query, with no other text, explanation, or markdown.
2.  The original query used the following tables: {table_list}. Your modification will likely use these tables as well.
3.  If the user's request requires information from a table not in the original query, you **MAY** join additional tables from the schema.
4.  Your query **MUST** only use columns that are explicitly listed in the schema.
5.  If the user's request cannot be fulfilled with the given schema, return a descriptive error message starting with "Error:".

**Database Schema:**
{schema}

**Original SQL Query:**
{original_sql}

**User's Modification Request:**
{modification_prompt}

**Modified SQL Query:**"""
        response = self.model.generate_content(full_prompt)
        return self._clean_sql(response.parts[0].text)

    def _clean_sql(self, sql_text):
        cleaned_sql = sql_text.strip()
        if cleaned_sql.startswith("```sql"):
            cleaned_sql = cleaned_sql[len("```sql"):].strip()
        if cleaned_sql.endswith("```"):
            cleaned_sql = cleaned_sql[:-len("```"):].strip()
        return cleaned_sql
