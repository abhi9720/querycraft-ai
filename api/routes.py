
import traceback
import logging
from flask import jsonify, request

from agents.query_explanation_agent import QueryExplanationAgent
from agents.sql_agent import SQLAgent
from agents.table_identification_agent import TableIdentificationAgent

from . import api_bp

# Set up logging to a file
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="error.log",
    filemode="a",  # Append to the log file
)


@api_bp.route("/generate", methods=["POST"])
def generate():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400

        prompt = data.get("prompt")
        tables = data.get("tables")  # The list of confirmed tables from the frontend

        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400

        with open("schema.sql") as f:
            schema = f.read()

        if not tables:
            # If no tables are provided, it's the first step: identify tables.
            table_agent = TableIdentificationAgent()
            identified_tables = table_agent.run(prompt, schema)
            return jsonify({"tables": identified_tables.split(",")})
        else:
            # If tables are provided, it's the second step: generate the query.
            sql_agent = SQLAgent()
            sql_query = sql_agent.run(prompt, schema, tables)

            explanation_agent = QueryExplanationAgent()
            explanation = explanation_agent.run(prompt=prompt, query=sql_query)

            return jsonify({"sql": sql_query, "explanation": explanation})

    except Exception as e:
        logging.exception("An error occurred during query generation.")
        return (
            jsonify(
                {
                    "error": "An internal server error occurred.",
                    "description": str(e),
                }
            ),
            500,
        )
