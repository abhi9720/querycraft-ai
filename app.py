import dotenv
from flask import Flask
from main import bp as main_bp
from api import api_bp
import logging
from logging.handlers import RotatingFileHandler

# Load environment variables from .env file
dotenv.load_dotenv()

def create_app():
    app = Flask(__name__)

    # Set up logging to a file
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
        filename="agent.log",
        filemode="a",  # Append to the log file
    )


    # Register the blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)

    return app
