from agents.base import BaseAgent

class QueryModificationAgent(BaseAgent):
    def run(self, query, prompt):
        full_prompt = f"""Given the following SQL query and a user's request, modify the query to meet the user's needs. Your output should only be the new, modified SQL query.

**Instructions:**
1.  Read the original query and the user's prompt carefully.
2.  Modify the query based on the user's instructions.
3.  Ensure the new query is syntactically correct.
4.  Do not include any other text, explanation, or markdown in your response. Only the SQL.

**Original Query:**
```sql
{query}
```

**User's Request:**
{prompt}

**Modified SQL Query:**"""
        response = self.model.generate_content(full_prompt)
        if not response.parts:
            return query # Return original query if modification fails
        return response.parts[0].text.strip()
