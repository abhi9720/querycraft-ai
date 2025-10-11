
import traceback
import logging
from flask import jsonify, request

from agents.query_explanation_agent import QueryExplanationAgent
from agents.sql_agent import SQLAgent

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

        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400

        with open("schema.sql") as f:
            schema = f.read()

        # Correctly instantiate the agents and run them
        sql_agent = SQLAgent()
        sql_query = sql_agent.run(prompt, schema)

        explanation_agent = QueryExplanationAgent()
        explanation = explanation_agent.run(prompt=prompt, query=sql_query)

        return jsonify({"sql": sql_query, "explanation": explanation})

    except Exception as e:
        # Log the exception with a full traceback to the error.log file
        logging.exception("An error occurred during query generation.")
        # Also return the error to the frontend
        return (
            jsonify(
                {
                    "error": "An internal server error occurred.",
                    "description": str(e),
                }
            ),
            500,
        )
