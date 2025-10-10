#!/bin/sh
export FLASK_APP=app:create_app
./.venv/bin/python -m flask run -p ${PORT:-8080} --debug
