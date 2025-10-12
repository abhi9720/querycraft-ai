
import re
from agents.base import BaseAgent
from agents.intent_agent import IntentAgent
from agents.prompt_enhancer_agent import PromptEnhancerAgent

class OrchestratorAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.prompt_enhancer_agent = PromptEnhancerAgent()
        self.intent_agent = IntentAgent()

    def run(self, prompt, schema, tables=None, history=None):
        if isinstance(history, dict):
            messages = history.get('messages', [])
            context = history.get('context', {})
        else:
            messages = history or []
            context = {}

        # Deterministic check: If the prompt is a SQL query, explain it directly.
        if prompt.strip().lower().startswith('select'):
            from agents.query_explanation_agent import QueryExplanationAgent
            explanation_agent = QueryExplanationAgent()
            explanation = explanation_agent.run(prompt=prompt, query=prompt)
            return {"type": "direct_answer", "response": explanation}

        # Step 1: Enhance the user's prompt to be context-aware
        enhanced_prompt = self.prompt_enhancer_agent.run(prompt, history)

        if tables:
            return self._run_final_sql_generation(enhanced_prompt, schema, tables, messages, original_prompt=prompt)

        # Step 2: Determine intent using the enhanced prompt
        intent = self.intent_agent.run(enhanced_prompt, messages)

        if intent == 'query_modification':
            last_sql_query = context.get('last_query_sql') or self._get_last_sql_from_history(messages)
            last_used_tables = context.get('last_used_tables') or self._get_last_tables_from_history(messages)
            
            if last_sql_query and last_used_tables:
                return self._run_sql_modification(enhanced_prompt, schema, last_sql_query, last_used_tables)
            else:
                intent = 'sql_generation'

        # This intent is now primarily for when the user says "explain this query" without providing one.
        if intent == 'query_explanation':
            return {"type": "clarification", "response": "Of course, please provide the SQL query you would like me to explain."}

        if intent == 'direct_answer':
            from agents.direct_answer_agent import DirectAnswerAgent
            direct_answer_agent = DirectAnswerAgent()
            response = direct_answer_agent.run(prompt, messages)
            return {"type": "direct_answer", "response": response}

        if intent == 'sql_generation':
            return self._run_table_identification(enhanced_prompt, schema)
        
        # Fallback for when intent detection fails
        return {"type": "clarification", "response": "Could you please provide more details or be more specific?"}

    def _run_table_identification(self, prompt, schema):
        from agents.table_identification_agent import TableIdentificationAgent
        all_db_tables = re.findall(r"Table `([^`]*)`", schema)
        table_agent = TableIdentificationAgent()
        identified_tables_str = table_agent.run(prompt, schema)
        identified_tables = [t.strip() for t in identified_tables_str.split(",") if t.strip()] if identified_tables_str else []
        return {"type": "confirm_tables", "tables": identified_tables, "all_tables": all_db_tables}

    def _run_final_sql_generation(self, prompt, schema, tables, history, original_prompt):
        from agents.sql_agent import SQLAgent
        from agents.query_explanation_agent import QueryExplanationAgent

        sql_agent = SQLAgent()
        sql_query = sql_agent.run(prompt, schema, tables)

        if sql_query.strip().startswith("Error:"):
            return {"type": "direct_answer", "response": sql_query}

        explanation_agent = QueryExplanationAgent()
        explanation = explanation_agent.run(prompt=original_prompt, query=sql_query)

        new_context = {'last_query_sql': sql_query, 'last_used_tables': tables}
        return {"type": "sql_query", "sql": sql_query, "explanation": explanation, "context": new_context}

    def _run_sql_modification(self, prompt, schema, original_sql, tables):
        from agents.sql_agent import SQLAgent
        from agents.query_explanation_agent import QueryExplanationAgent

        sql_agent = SQLAgent()
        modified_sql = sql_agent.modify_sql(original_sql, prompt, schema, tables)

        if modified_sql.strip().startswith("Error:"):
            return {"type": "direct_answer", "response": modified_sql}

        explanation_agent = QueryExplanationAgent()
        explanation = explanation_agent.run(prompt=prompt, query=modified_sql)
        
        new_context = {'last_query_sql': modified_sql, 'last_used_tables': tables}
        return {"type": "sql_query", "sql": modified_sql, "explanation": explanation, "context": new_context}

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
