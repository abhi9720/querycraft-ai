from flask import render_template, request, jsonify
from . import bp
from agents.table_agent import TableAgent
from agents.sql_agent import SQLAgent
from agents.query_explanation_agent import QueryExplanationAgent
import re

@bp.route("/")
def index():
    return render_template("index.html", title="Flask App with Jinja2")

@bp.route("/api/suggest_tables", methods=["POST"])
def suggest_tables():
    prompt = request.json["prompt"]
    with open("schema.sql") as f:
        schema = f.read()

    table_agent = TableAgent()
    # The table agent returns a string of comma-separated table names.
    relevant_tables_str = table_agent.run(prompt, schema)
    
    # Parse the string into a list of table names
    table_names = [table.strip() for table in relevant_tables_str.split(',')]

    return jsonify({"tables": table_names})


@bp.route("/api/generate_sql", methods=["POST"])
def generate_sql():
    prompt = request.json["prompt"]
    tables = request.json["tables"]

    with open("schema.sql") as f:
        schema = f.read()

    # Filter the schema to include only the selected tables.
    pruned_schema = ""
    for table in tables:
        # Find the CREATE TABLE statement for the current table
        match = re.search(f"CREATE TABLE `{table}` .*?;", schema, re.DOTALL)
        if match:
            pruned_schema += match.group(0) + "\n\n"

    sql_agent = SQLAgent()
    sql_query = sql_agent.run(prompt, pruned_schema)

    query_explanation_agent = QueryExplanationAgent()
    explanation = query_explanation_agent.run(prompt, sql_query)

    return jsonify({"sql": sql_query, "explanation": explanation})
