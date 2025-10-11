
import traceback
import logging
from flask import jsonify, request
import json
import os
from dotenv import load_dotenv

from agents.orchestrator_agent import OrchestratorAgent
from database.factory import get_database_connector

from . import api_bp

# Load environment variables from .env file
load_dotenv()

# Get database configuration from environment variables
db_type = os.getenv("DB_TYPE")
db_name = os.getenv("DB_NAME")

# Create a database connector instance
connector = get_database_connector(db_type, db_name)

# Set up logging to a file
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="error.log",
    filemode="a",  # Append to the log file
)

@api_bp.route("/tables", methods=["GET"])
def get_tables():
    conn = None
    try:
        conn = connector.get_connection()
        cursor = conn.cursor()
        cursor.execute(connector.get_tables_query())
        tables = [row[0] for row in cursor.fetchall()]
        return jsonify(tables)
    except Exception as e:
        logging.exception("An error occurred while fetching tables.")
        return jsonify({"error": "An internal server error occurred.", "description": str(e)}), 500
    finally:
        if conn:
            connector.close_connection(conn)

@api_bp.route("/table/<table_name>", methods=["GET"])
def get_table_schema(table_name):
    conn = None
    try:
        conn = connector.get_connection()
        cursor = conn.cursor()

        # Fetch columns and their types from the database
        cursor.execute(connector.get_table_schema_query(table_name))
        columns_info = cursor.fetchall()
        columns = []
        for col in columns_info:
            columns.append({"name": col[1], "type": col[2]})

        # Fetch sample data
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        sample_data = [dict(zip(column_names, row)) for row in rows]

        # Enrich with metadata from schema.json
        with open("schema.json") as f:
            schema_json = json.load(f)
        
        table_metadata = schema_json.get(table_name, {})
        table_description = table_metadata.get("description", "")
        column_descriptions = {col["name"]: col.get("description", "") for col in table_metadata.get("columns", [])}

        for col in columns:
            col["description"] = column_descriptions.get(col["name"], "")

        return jsonify({
            "description": table_description,
            "columns": columns,
            "sample_data": sample_data
        })

    except Exception as e:
        logging.exception("An error occurred while fetching table schema.")
        return jsonify({"error": "An internal server error occurred.", "description": str(e)}), 500
    finally:
        if conn:
            connector.close_connection(conn)


@api_bp.route("/generate", methods=["POST"])
def generate():
    conn = None
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400

        prompt = data.get("prompt")
        tables = data.get("tables")  # The list of confirmed tables from the frontend
        history = data.get("history") # The conversation history

        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400

        # Connect to the database and get all table names
        conn = connector.get_connection()
        cursor = conn.cursor()
        cursor.execute(connector.get_tables_query())
        all_tables = [row[0] for row in cursor.fetchall()]

        # Load metadata from schema.json
        with open("schema.json") as f:
            schema_json = json.load(f)

        # Build the combined schema string for the LLM
        schema = ""
        for table_name in all_tables:
            # Get table description from metadata
            table_metadata = schema_json.get(table_name, {})
            table_description = table_metadata.get("description", "")
            schema += f"Table `{table_name}`: {table_description}\n"

            # Get column info from the database
            cursor.execute(connector.get_table_schema_query(table_name))
            columns_info = cursor.fetchall()

            # Get column descriptions from metadata
            column_metadata = {col["name"]: col.get("description", "") for col in table_metadata.get("columns", [])}

            for col in columns_info:
                col_name = col[1]
                col_type = col[2]
                col_description = column_metadata.get(col_name, "")
                schema += f"  `{col_name}`: {col_type} ({col_description})\n"
            schema += "\n"

        # Orchestrator Agent
        orchestrator = OrchestratorAgent()
        result = orchestrator.run(prompt, schema, tables, history)

        return jsonify(result)

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
    finally:
        if conn:
            connector.close_connection(conn)
