from agents.base import BaseAgent

class QueryExplanationAgent(BaseAgent):
    def run(self, prompt, query):
        # Check if the query is actually an error message
        if query.strip().startswith("Error:"):
            error_explanation_prompt = f"""The user's request could not be fulfilled.

The user asked: "{prompt}"

The system returned the following error: "{query}"

Your task is to rephrase this error into a clear, user-friendly explanation. Explain *why* the request failed based on the error message, but do not be overly technical. Focus on what the user can do next (e.g., rephrase their request, check table names).

**Good Example:**
"I couldn't find a column named 'order_date' in the 'orders' table, which is needed to group the results by month. You could try rephrasing your request to use a column that is available in the table, such as 'order_id'."

**Provide the user-friendly explanation now:**
"""
            response = self.model.generate_content(error_explanation_prompt)
            return response.parts[0].text.strip()

        # Original logic for explaining a valid SQL query
        explanation_prompt = f"""The user asked: "{prompt}"
The generated SQL query is:
```sql
{query}
```

Your task is to provide a concise, to-the-point explanation of how this SQL query answers the user's question.

**RULES:**
1.  **Be Brief:** Keep the explanation to a maximum of 3-4 sentences.
2.  **Focus on the Goal:** Explain *how* the query achieves the user's specific request.
3.  **Connect to the Prompt:** Directly reference the user's original request in the explanation.

**Provide the explanation now:**
"""
        response = self.model.generate_content(explanation_prompt)
        return response.parts[0].text.strip()
