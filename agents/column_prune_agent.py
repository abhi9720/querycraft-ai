import json
from agents.base import BaseAgent
from models.pruned_schema import PrunedSchema

class ColumnPruneAgent(BaseAgent):
    def run(self, prompt, schema, tables):
        full_prompt = f"""Given the following SQL schema, a user's prompt, and a list of relevant tables, identify the necessary columns from those tables to answer the user's prompt.

**Instructions:**
1.  For each table in the provided list of relevant tables, identify the columns that are essential to answer the user's prompt.
2.  Your output MUST NOT be a DDL statement.
3.  ALWAYS include all primary and foreign key columns for the selected tables.
4.  Only include other columns if they are directly mentioned or strongly implied in the user's prompt.
5.  Your output must be a JSON object that conforms to the following Pydantic schema:

    ```json
    {{
        "schema_pruned": [
            {{
                "table_name": "string",
                "used_columns": ["string"]
            }}
        ]
    }}
    ```

6.  Do not include any other text, explanation, or markdown. The output must be ONLY the JSON object.

**Original Schema:**
{schema}

**User's Prompt:** {prompt}

**Relevant Tables:**
{', '.join(tables)}

**Pruned JSON Output:**"""

        response = self.model.generate_content(
            full_prompt,
            generation_config={
                "response_mime_type": "application/json",
                "response_schema": PrunedSchema,
            }
        )

        try:
            # The response from the model with a specified schema is a JSON string.
            # We parse it into a Python dict.
            pruned_schema_dict = json.loads(response.parts[0].text)
        except (IndexError, json.JSONDecodeError) as e:
            print(f"Error parsing pruned schema response: {e}")
            # Return an empty structure in case of an error
            pruned_schema_dict = {"schema_pruned": []}

        return pruned_schema_dict
