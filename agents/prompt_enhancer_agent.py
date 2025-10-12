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
1.  Analyze the user's new prompt.
2.  Examine the most recent SQL query that was run.
3.  If the new prompt seems to be a follow-up or modification of the last query, rewrite the prompt to include the necessary context from the last query.
4.  If the new prompt is unrelated to the previous query, return the user's prompt exactly as it is.
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
