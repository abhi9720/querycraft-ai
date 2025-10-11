from agents.base import BaseAgent

class QueryExplanationAgent(BaseAgent):
    def run(self, prompt, query):
        full_prompt = f"""The user asked: "{prompt}"
The generated SQL query is:
```sql
{query}
```

Your task is to provide a concise, to-the-point explanation of how this SQL query answers the user's question.

**RULES:**
1.  **Be Brief:** Keep the explanation to a maximum of 3-4 sentences. For very simple queries (like adding an index or a single-column select), one or two sentences is enough.
2.  **Focus on the Goal:** Explain *how* the query achieves the user's specific request. Do not give a generic, line-by-line tutorial on the SQL syntax.
3.  **Assume User is Technical:** Do not explain basic SQL concepts like `SELECT`, `JOIN`, `ALTER TABLE`, or `GROUP BY`.
4.  **Connect to the Prompt:** Directly reference the user's original request in the explanation.

**Good Example (for "Show me the top 5 customers by sales"):**
"This query answers your request by joining `customers` and `orders` to calculate the total sales for each customer. It then uses `ORDER BY` and `LIMIT 5` to rank them and return only the top five."

**Bad Example (for the same prompt):**
"This query first selects the customer's name from the `customers` table. Then, it uses a `LEFT JOIN` to connect to the `orders` table on the `customer_id` field. It then calculates the sum of the `amount` column and aliases it as `total_sales`. Finally, it groups the results by customer and orders them in descending order to show the highest sales first, limiting the output to 5 rows."

**Provide the explanation now:**
"""
        response = self.model.generate_content(full_prompt)
        return response.parts[0].text.strip()
