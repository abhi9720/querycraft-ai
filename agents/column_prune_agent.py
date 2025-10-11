import re
from agents.base import BaseAgent

class ColumnPruneAgent(BaseAgent):
    def run(self, prompt, schema, tables):
        full_prompt = f"""Given the following SQL schema, a user\'s prompt, and a list of relevant tables, prune the schema to include ONLY the necessary columns from those tables.

**Instructions:**
1.  For each table in the provided list of relevant tables, identify the columns that are essential to answer the user\'s prompt.
2.  ALWAYS include all primary and foreign key columns for the selected tables.
3.  Only include other columns if they are directly mentioned or strongly implied in the user\'s prompt.
4.  Your output should be ONLY the pruned SQL schema in `CREATE TABLE` format.
5.  Do not include any other text, explanation, or markdown.

**Original Schema:**
{schema}

**User\'s Prompt:** {prompt}

**Relevant Tables:**
{', '.join(tables)}

**Pruned SQL Schema:**"""
        response = self.model.generate_content(full_prompt)
        
        try:
            pruned_schema_str = response.parts[0].text.strip()
        except IndexError:
            pruned_schema_str = ""

        pruned_schema_dict = {}
        # The schema can be either CREATE TABLE statements or just table names with columns.
        # This regex handles both formats.
        create_table_statements = re.findall(r"(CREATE TABLE `)?(.*?)(?(1)` \((.*?)\);|(.*))".strip(), pruned_schema_str, re.DOTALL)

        for match in create_table_statements:
            table_name = match[1] if match[1] else match[3].split('\n')[0].replace('Table `','').replace('`:','')
            columns_str = match[2] if match[2] else match[3]

            column_names = re.findall(r"^\s*`([^`]+)`", columns_str, re.MULTILINE)
            if table_name in tables:
                pruned_schema_dict[table_name] = column_names

        return pruned_schema_dict
