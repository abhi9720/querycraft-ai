import dotenv
from flask import Flask
from main import bp as main_bp

# Load environment variables from .env file
dotenv.load_dotenv()

def create_app():
    app = Flask(__name__)

    # Register the blueprint
    app.register_blueprint(main_bp)

    return app
