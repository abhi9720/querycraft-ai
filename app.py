from flask import Flask
from main.extensions import cache

def create_app():
    app = Flask(__name__)
    app.config["CACHE_TYPE"] = "redis"
    app.config["CACHE_REDIS_URL"] = "redis://localhost:6379/0"
    cache.init_app(app)

    # Register blueprints
    from main import bp as main_bp
    app.register_blueprint(main_bp)

    return app
