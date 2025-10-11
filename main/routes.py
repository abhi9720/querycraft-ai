from flask import render_template, g
from . import bp
import json

@bp.route("/")
def index():
    with open('schema.json', 'r') as f:
        tables_data = json.load(f)
    table_names = list(tables_data.keys())
    return render_template("index.html", title="Flask App with Jinja2", tables=table_names)
