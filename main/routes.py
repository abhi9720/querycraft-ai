from flask import render_template, request, jsonify
from . import bp
from agents.intent_agent import IntentAgent
from agents.table_agent import TableAgent
from agents.column_prune_agent import ColumnPruneAgent
from agents.sql_agent import SQLAgent
from agents.query_explanation_agent import QueryExplanationAgent

@bp.route("/")
def index():
    return render_template("index.html")

@bp.route("/api/generate", methods=["POST"])
def generate():
    prompt = request.json["prompt"]
    
    with open("schema.sql") as f:
        schema = f.read()

    intent_agent = IntentAgent()
    intent = intent_agent.run(prompt)

    if "GENERATE_SQL" in intent.text:
        table_agent = TableAgent()
        relevant_tables = table_agent.run(prompt, schema)

        column_prune_agent = ColumnPruneAgent()
        pruned_schema = column_prune_agent.run(prompt, relevant_tables.text)

        sql_agent = SQLAgent()
        sql_query = sql_agent.run(prompt, pruned_schema.text)

        query_explanation_agent = QueryExplanationAgent()
        explanation = query_explanation_agent.run(prompt, sql_query.text)

        return jsonify({"sql": sql_query.text, "explanation": explanation.text})

    elif "EXPLAIN_SQL" in intent.text:
        query_explanation_agent = QueryExplanationAgent()
        explanation = query_explanation_agent.run(prompt, request.json["sql"]) # Assuming the SQL is sent in the request
        return jsonify({"explanation": explanation.text})

    else:
        return jsonify({"sql": "Could not determine intent.", "explanation": ""})
