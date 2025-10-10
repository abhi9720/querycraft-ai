from flask import render_template, request, jsonify
from . import bp
from agents.intent_agent import IntentAgent
from agents.table_agent import TableAgent
from agents.column_prune_agent import ColumnPruneAgent
from agents.query_explanation_agent import QueryExplanationAgent
from .extensions import cache

@bp.route("/")
def index():
    return render_template("index.html")

@bp.route("/api/generate", methods=["POST"])
@cache.cached(timeout=300)
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
        relevant_columns = column_prune_agent.run(prompt, relevant_tables.text)

        # This is where the GenAI gateway would be called to generate the final query
        # For now, we will just return the pruned schema
        return jsonify({"sql": relevant_columns.text})

    elif "EXPLAIN_SQL" in intent.text:
        query_explanation_agent = QueryExplanationAgent()
        explanation = query_explanation_agent.run(prompt)
        return jsonify({"sql": explanation.text})

    else:
        return jsonify({"sql": "Could not determine intent."})
