import re
from agents.base import BaseAgent
from agents.intent_agent import IntentAgent

class OrchestratorAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.intent_agent = IntentAgent()

    def run(self, prompt, schema, tables=None, history=None):
        history = history or []
        intent = self.intent_agent.run(prompt, history)

        if intent == 'query_modification':
            original_prompt, confirmed_tables = self._get_context_from_history(history)

            if original_prompt and confirmed_tables:
                new_prompt = f"Original request: {original_prompt}\n\nPlease modify the query to also: {prompt}"
                return self._run_sql_generation(new_prompt, schema, confirmed_tables)
            else:
                intent = 'sql_generation'

        if intent == 'query_explanation':
            from agents.query_explanation_agent import QueryExplanationAgent
            explanation_agent = QueryExplanationAgent()
            explanation = explanation_agent.run(prompt=prompt, query=prompt)
            return {"type": "direct_answer", "response": explanation}

        if intent == 'awaiting_query_for_explanation':
            return {"type": "clarification", "response": "Of course, please provide the SQL query you would like me to explain."}

        if intent == 'direct_answer':
            return {"type": "direct_answer", "response": self.generate_direct_answer(prompt)}

        if intent == 'sql_generation':
            return self._run_sql_generation(prompt, schema, tables)
        
        return {"type": "clarification", "response": "Could you please provide more details or be more specific?"}

    def _run_sql_generation(self, prompt, schema, tables=None):
        all_db_tables = re.findall(r"Table `([^`]*)`", schema)

        if not tables:
            from agents.table_identification_agent import TableIdentificationAgent
            table_agent = TableIdentificationAgent()
            identified_tables_str = table_agent.run(prompt, schema)
            
            identified_tables = []
            if identified_tables_str:
                identified_tables = [t.strip() for t in identified_tables_str.split(",") if t.strip()]

            return {"type": "confirm_tables", "tables": identified_tables, "all_tables": all_db_tables}
        else:
            from agents.column_prune_agent import ColumnPruneAgent
            from agents.sql_agent import SQLAgent
            from agents.query_explanation_agent import QueryExplanationAgent

            column_prune_agent = ColumnPruneAgent()
            pruned_schema_dict = column_prune_agent.run(prompt, schema, tables)

            sql_agent = SQLAgent()
            sql_query = sql_agent.run(prompt, pruned_schema_dict, tables)

            explanation_agent = QueryExplanationAgent()
            explanation = explanation_agent.run(prompt=prompt, query=sql_query)

            return {"type": "sql_query", "sql": sql_query, "explanation": explanation}

    def generate_direct_answer(self, prompt):
        prompt_lower = prompt.lower()
        if any(phrase in prompt_lower for phrase in ["what is your name", "who are you"]):
            return "I am a sophisticated AI assistant designed to help you with your data-related tasks."
        return "I am not sure how to answer that."

    def _get_context_from_history(self, history):
        original_prompt = None
        confirmed_tables = None

        for message in reversed(history):
            if message.get('sender') == 'user' and message.get('message', '').startswith('Confirmed tables:'):
                tables_str = message['message'].replace('Confirmed tables:', '').strip()
                if tables_str:
                    confirmed_tables = [table.strip() for table in tables_str.split(',')]
                    break
        
        if confirmed_tables:
            for message in history:
                if message.get('sender') == 'user' and not message.get('message', '').startswith('Confirmed tables:'):
                    original_prompt = message['message']
                    break

        return original_prompt, confirmed_tables
