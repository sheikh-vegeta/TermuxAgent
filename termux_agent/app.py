import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

def create_app():
    """
    Application factory for the Flask app.
    """
    app = Flask(__name__, template_folder='../templates', static_folder='../static')

    # Load configuration from environment variables
    app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "a_default_secret_key")

    # --- Swagger UI setup ---
    SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI
    API_URL = '/api/spec'      # URL for the openapi.yaml

    # Create a route to serve the openapi.yaml file
    @app.route(API_URL)
    def send_spec():
        # The spec is in the root directory, so we use '..' to go up one level
        # from the app's root_path, which is typically the 'termux_agent' directory.
        return send_from_directory('..', 'openapi.yaml')

    # Create Swagger UI blueprint
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={'app_name': "Termux Agent API"}
    )
    app.register_blueprint(swaggerui_blueprint)

    # Enable CORS for all domains on all routes
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Import and register the API routes
    with app.app_context():
        from . import routes
        app.register_blueprint(routes.api_bp)

    return app
