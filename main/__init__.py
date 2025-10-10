from flask import Blueprint

bp = Blueprint("main", __name__, template_folder="templates", url_prefix="/")

from . import routes
