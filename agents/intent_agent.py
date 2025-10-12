from agents.base import BaseAgent

class IntentAgent(BaseAgent):
    def run(self, prompt, history=None):
        history = history or []
        # Create a simplified history string, including the type for bot messages
        history_str_parts = []
        for m in history:
            sender = m.get('sender', 'unknown')
            message = m.get('message', '')
            msg_type = m.get('type')
            if sender == 'bot' and msg_type == 'sql_query':
                history_str_parts.append(f"bot: (Generated SQL Query) {message}")
            else:
                history_str_parts.append(f"{sender}: {message}")
        history_str = "\n".join(history_str_parts)

        full_prompt = f"""Analyze the user's prompt and conversation history to classify the primary intent. The user is interacting with a database.

**Possible Intents:**

-   **`sql_generation`**: The user wants to write a completely new SQL query. This is the default if no other intent fits.
-   **`query_modification`**: The user wants to modify the most recently generated SQL query. Keywords like "change", "modify", "add", "remove", "instead of", or follow-up questions like "who are they?", "what are their names?", "show me their emails" after a query about users, are strong signals for this intent.
-   **`query_explanation`**: The user is providing a SQL query and wants an explanation of what it does. The prompt itself will likely be a SQL query (e.g., starting with 'SELECT').
-   **`direct_answer`**: The user is asking a conversational question (e.g., "what is your name") that can be answered without database access.

**Instructions:**

-   Carefully consider the user's prompt and the full conversation history.
-   A question asking for more details about the results of the immediately preceding query (like "who has these orders?" after a query that found orders) is a `query_modification`.
-   If the user's prompt *is* a SQL query, the intent is `query_explanation`.
-   Your output must be ONLY the single intent classification. Do not include any other text.

**History:**
{history_str}

**User Prompt:** {prompt}

**Intent:**"""
        response = self.model.generate_content(full_prompt)
        return response.parts[0].text.strip()
