import os
from flask import Flask
from flask_cors import CORS
from flasgger import Swagger

def create_app():
    """
    Application factory for the Flask app.
    """
    app = Flask(__name__, template_folder='../templates', static_folder='../static')

    # Load configuration from environment variables
    app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "a_default_secret_key")

    # Configure Flasgger for API documentation
    app.config["SWAGGER"] = {
        "title": "Termux Agent API",
        "uiversion": 3,
        "openapi": "3.0.2",
        "specs_route": "/api/docs/",
    }
    # The Swagger instance is created here, referencing the openapi.yaml file
    Swagger(app, template_file="../openapi.yaml")

    # Enable CORS for all domains on all routes
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Import and register the API routes
    with app.app_context():
        from . import routes
        app.register_blueprint(routes.api_bp)

    return app
