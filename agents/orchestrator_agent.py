
import logging
import re
from agents.base import BaseAgent
from agents.intent_agent import IntentAgent
from agents.prompt_enhancer_agent import PromptEnhancerAgent
from agents.table_identification_agent import TableIdentificationAgent
from agents.column_prune_agent import ColumnPruneAgent
from agents.sql_agent import SQLAgent
from agents.query_explanation_agent import QueryExplanationAgent
from agents.direct_answer_agent import DirectAnswerAgent

class OrchestratorAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.prompt_enhancer_agent = PromptEnhancerAgent()
        self.intent_agent = IntentAgent()

        self.intent_to_pipeline = {
            "sql_generation": [TableIdentificationAgent, ColumnPruneAgent, SQLAgent, QueryExplanationAgent],
            "query_modification": ['modify_sql', ColumnPruneAgent, QueryExplanationAgent],
            "query_explanation": [QueryExplanationAgent],
            "direct_answer": [DirectAnswerAgent],
        }
        
        self.logger = logging.getLogger(__name__)

    def run(self, prompt, schema, tables=None, history=None):
        self.logger.info(f"OrchestratorAgent starting with prompt: '{prompt}', tables: {tables}, history: {history is not None}")
        
        if isinstance(history, dict):
            messages = history.get('messages', [])
            context = history.get('context', {})
        else:
            messages = history or []
            context = {}

        # Step 1: Enhance the user's prompt to be context-aware
        self.logger.info(f"Calling PromptEnhancerAgent with prompt: '{prompt}'")
        enhanced_prompt = self.prompt_enhancer_agent.run(prompt, history)
        self.logger.info(f"PromptEnhancerAgent returned: '{enhanced_prompt}'")

        # If tables are confirmed by the user, we proceed with the rest of the SQL generation pipeline.
        if tables:
            self.logger.info("Tables are confirmed. Running SQL generation pipeline.")
            return self._run_sql_generation_pipeline(enhanced_prompt, schema, tables, original_prompt=prompt)

        # Step 2: Determine intent using the enhanced prompt
        self.logger.info(f"Calling IntentAgent with prompt: '{enhanced_prompt}'")
        intent = self.intent_agent.run(enhanced_prompt, messages)
        self.logger.info(f"IntentAgent returned: '{intent}'")

        # Step 3: Execute the appropriate pipeline based on the detected intent
        if intent == 'query_modification':
            self.logger.info("Intent is 'query_modification'. Starting query modification process.")
            last_sql_query = context.get('last_query_sql') or self._get_last_sql_from_history(messages)
            last_used_tables = context.get('last_used_tables') or self._get_last_tables_from_history(messages)
            self.logger.info(f"Retrieved from history: last_sql_query='{last_sql_query}', last_used_tables={last_used_tables}")

            if not last_sql_query and enhanced_prompt.strip().lower().startswith('select'):
                self.logger.info("No last query in history, but prompt looks like SQL. Identifying tables from prompt.")
                table_agent = TableIdentificationAgent()
                self.logger.info(f"Calling TableIdentificationAgent with prompt: '{enhanced_prompt}'")
                identified_tables_str = table_agent.run(enhanced_prompt, schema)
                self.logger.info(f"TableIdentificationAgent returned: '{identified_tables_str}'")
                identified_tables = [t.strip() for t in identified_tables_str.split(",") if t.strip()] if identified_tables_str else []
                return self._run_query_modification_pipeline(enhanced_prompt, schema, enhanced_prompt, identified_tables)

            if last_sql_query and last_used_tables:
                self.logger.info("Found last query in history. Running query modification pipeline.")
                return self._run_query_modification_pipeline(enhanced_prompt, schema, last_sql_query, last_used_tables)
            
            self.logger.info("No query to modify found. Falling back to 'sql_generation'.")
            intent = 'sql_generation'

        if intent == 'sql_generation':
            self.logger.info("Intent is 'sql_generation'. Identifying tables.")
            pipeline = self.intent_to_pipeline.get(intent)
            table_identification_agent = pipeline[0]()
            all_db_tables = re.findall(r"Table `([^`]*)`", schema)
            self.logger.info(f"Calling TableIdentificationAgent with prompt: '{enhanced_prompt}'")
            identified_tables_str = table_identification_agent.run(enhanced_prompt, schema)
            self.logger.info(f"TableIdentificationAgent returned: '{identified_tables_str}'")
            identified_tables = [t.strip() for t in identified_tables_str.split(",") if t.strip()] if identified_tables_str else []
            result = {"type": "confirm_tables", "tables": identified_tables, "all_tables": all_db_tables}
            self.logger.info(f"Returning table confirmation request: {result}")
            return result

        elif intent == 'direct_answer':
            self.logger.info("Intent is 'direct_answer'.")
            pipeline = self.intent_to_pipeline.get(intent)
            direct_answer_agent = pipeline[0]()
            self.logger.info(f"Calling DirectAnswerAgent with prompt: '{enhanced_prompt}'")
            response = direct_answer_agent.run(enhanced_prompt, messages)
            self.logger.info(f"DirectAnswerAgent returned: '{response}'")
            result = {"type": "direct_answer", "response": response}
            self.logger.info(f"Returning direct answer: {result}")
            return result

        elif intent == 'query_explanation':
            self.logger.info("Intent is 'query_explanation'.")
            if enhanced_prompt.strip().lower().startswith('select'):
                explanation_agent = QueryExplanationAgent()
                self.logger.info(f"Calling QueryExplanationAgent with prompt: '{enhanced_prompt}'")
                explanation = explanation_agent.run(prompt=enhanced_prompt, query=enhanced_prompt)
                self.logger.info(f"QueryExplanationAgent returned: '{explanation}'")
                result = {"type": "direct_answer", "response": explanation}
                self.logger.info(f"Returning explanation as direct answer: {result}")
                return result
            else:
                self.logger.info("No query provided for explanation. Asking for clarification.")
                return {"type": "clarification", "response": "Of course, please provide the SQL query you would like me to explain."}
        
        self.logger.warning("Could not determine a clear action. Asking for clarification.")
        return {"type": "clarification", "response": "Could you please provide more details or be more specific?"}

    def _run_sql_generation_pipeline(self, prompt, schema, tables, original_prompt):
        self.logger.info(f"Starting SQL generation pipeline for tables: {tables}")
        pipeline = self.intent_to_pipeline.get("sql_generation")
        
        column_prune_agent = pipeline[1]()
        sql_agent = pipeline[2]()
        explanation_agent = pipeline[3]()
        
        self.logger.info(f"Calling ColumnPruneAgent with prompt: '{prompt}' and tables: {tables}")
        pruned_schema = column_prune_agent.run(prompt, schema, tables)
        self.logger.info(f"ColumnPruneAgent returned pruned schema: '{pruned_schema}'")
        
        self.logger.info(f"Calling SQLAgent with prompt: '{prompt}' and tables: {tables}")
        sql_query = sql_agent.run(prompt, pruned_schema, tables)
        self.logger.info(f"SQLAgent returned: '{sql_query}'")

        if sql_query.strip().startswith("Error:"):
            self.logger.error(f"SQLAgent returned an error: {sql_query}")
            return {"type": "direct_answer", "response": sql_query}

        self.logger.info(f"Calling QueryExplanationAgent with original prompt: '{original_prompt}'")
        explanation = explanation_agent.run(prompt=original_prompt, query=sql_query)
        self.logger.info(f"QueryExplanationAgent returned: '{explanation}'")

        new_context = {'last_query_sql': sql_query, 'last_used_tables': tables}
        result = {"type": "sql_query", "sql": sql_query, "explanation": explanation, "context": new_context}
        self.logger.info(f"SQL generation pipeline finished. Returning: {result}")
        return result

    def _run_query_modification_pipeline(self, prompt, schema, original_sql, tables):
        self.logger.info(f"Starting query modification pipeline for original_sql: '{original_sql}' and tables: {tables}")
        pipeline = self.intent_to_pipeline.get("query_modification")

        sql_agent = SQLAgent()
        column_prune_agent = pipeline[1]()
        explanation_agent = pipeline[2]()
        
        self.logger.info(f"Calling ColumnPruneAgent with prompt: '{prompt}' and tables: {tables}")
        pruned_schema = column_prune_agent.run(prompt, schema, tables)
        self.logger.info(f"ColumnPruneAgent returned pruned schema: '{pruned_schema}'")
        
        self.logger.info(f"Calling SQLAgent's modify_sql with original_sql: '{original_sql}' and prompt: '{prompt}'")
        modified_sql = sql_agent.modify_sql(original_sql, prompt, pruned_schema, tables)
        self.logger.info(f"SQLAgent's modify_sql returned: '{modified_sql}'")

        if modified_sql.strip().startswith("Error:"):
            self.logger.error(f"SQLAgent's modify_sql returned an error: {modified_sql}")
            return {"type": "direct_answer", "response": modified_sql}

        self.logger.info(f"Calling QueryExplanationAgent with prompt: '{prompt}'")
        explanation = explanation_agent.run(prompt=prompt, query=modified_sql)
        self.logger.info(f"QueryExplanationAgent returned: '{explanation}'")
        
        new_context = {'last_query_sql': modified_sql, 'last_used_tables': tables}
        result = {"type": "sql_query", "sql": modified_sql, "explanation": explanation, "context": new_context}
        self.logger.info(f"Query modification pipeline finished. Returning: {result}")
        return result

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
