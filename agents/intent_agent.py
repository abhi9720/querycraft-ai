from agents.base import BaseAgent

class IntentAgent(BaseAgent):
    def run(self, prompt, history=None):
        history = history or []
        # Create a simplified history string
        history_str = "\n".join([f"{m['sender']}: {m['message']}" for m in history])

        full_prompt = f"""Analyze the user's prompt and conversation history to classify the primary intent.

**Possible Intents:**

-   **`sql_generation`**: The user wants to write a new SQL query to get information from the database. This is the default intent if no other intent is a good fit.
-   **`query_modification`**: The user wants to modify a previous query. Keywords like "change", "modify", "add", "instead of", "rank", "order by" often indicate this intent, especially if a query was recently generated.
-   **`query_explanation`**: The user is providing a SQL query and wants an explanation of what it does. The prompt itself will likely be a SQL query (e.g., starting with 'SELECT' or 'WITH').
-   **`awaiting_query_for_explanation`**: The user asks to have a query explained, but hasn't provided the query yet. Example: "Can you explain this query for me?".
-   **`direct_answer`**: The user is asking a conversational question that can be answered directly without accessing the database, like "what is your name" or "who are you".

**Instructions:**

-   Carefully consider the user's prompt and the provided history.
-   A recent query in the history followed by a modification request is a strong signal for `query_modification`.
-   If the user's prompt *is* a SQL query, the intent is `query_explanation`.
-   Your output must be ONLY the single intent classification. Do not include any other text, explanation, or markdown.

**History:**
{history_str}

**User Prompt:** {prompt}

**Intent:**"""
        response = self.model.generate_content(full_prompt)
        return response.parts[0].text.strip()
