#!/bin/bash

# Activate the virtual environment
source .venv/bin/activate

# Run the Flask application on the port assigned by the environment
flask --app app:create_app run --debug --host 0.0.0.0 --port $PORT
