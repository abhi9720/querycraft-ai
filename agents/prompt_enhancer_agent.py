from agents.base import BaseAgent

class PromptEnhancerAgent(BaseAgent):
    def run(self, prompt, history=None):
        # Use the same robust history parsing logic
        if isinstance(history, dict):
            messages = history.get('messages', [])
            context = history.get('context', {})
        else:
            messages = history or []
            context = {}

        last_sql_query = context.get('last_query_sql') or self._get_last_sql_from_history(messages)
        last_used_tables = context.get('last_used_tables') or self._get_last_tables_from_history(messages)

        # If there is no history, no enhancement is needed
        if not last_sql_query:
            return prompt

        full_prompt = f"""You are a Prompt Enhancer assistant. Your job is to analyze a user's new prompt in the context of a conversation history and rewrite it to be more explicit and context-aware for a downstream AI agent.

**Instructions:**
1.  Analyze the user's new prompt. Does it seem like a complete thought or question on its own?
2.  Now, consider the conversation history. Is the new prompt a clear and direct follow-up or modification of the **Last SQL Query**? A follow-up usually contains pronouns ("it", "they", "them") or is a fragment that doesn't make sense on its own (e.g., "now add their city", "what about the price").
3.  **If the new prompt is a clear follow-up or modification:**
    - Rewrite the prompt to be self-contained and explicit.
    - For example, if the last query was `SELECT name, age FROM users` and the new prompt is "now add their city", the enhanced prompt should be "Modify the previous query to also select the city for the users".
4.  **If the new prompt is a complete thought and can stand on its own as a new query:**
    - Return the user's prompt exactly as it is, even if it shares some keywords with the previous query.
    - For example, if the last query was about finding users with more than 3 orders, and the new prompt is "show me orders over $100", this is a NEW query, not a modification. Return "show me orders over $100".
5.  Your output MUST be ONLY the rewritten prompt, with no other text, explanation, or markdown.

**Conversation Context:**
-   **Last SQL Query:** {last_sql_query}
-   **Tables Used in Last Query:** {last_used_tables}

**User's New Prompt:** {prompt}

**Enhanced Prompt:**"""
        
        response = self.model.generate_content(full_prompt)
        enhanced_prompt = response.parts[0].text.strip()
        
        # Safety check: if the model returns an empty string or something nonsensical,
        # fall back to the original prompt.
        if not enhanced_prompt:
            return prompt
            
        return enhanced_prompt

    def _get_last_sql_from_history(self, history):
        for message in reversed(history):
            if message.get('isSql') is True:
                return message.get('message')
        return None

    def _get_last_tables_from_history(self, history):
        for message in reversed(history):
            msg_text = message.get('message', '')
            if message.get('sender') == 'user' and msg_text.startswith('Confirmed tables:'):
                tables_str = msg_text.replace('Confirmed tables:', '').strip()
                if tables_str:
                    return [table.strip() for table in tables_str.split(',')]
        return None
