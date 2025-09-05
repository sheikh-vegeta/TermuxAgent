import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# We import the app factory function after loading the env vars
from termux_agent.app import create_app

# Get host and port from environment variables, with defaults
host = os.environ.get("FLASK_RUN_HOST", "0.0.0.0")
port = int(os.environ.get("FLASK_RUN_PORT", 5000))
debug = os.environ.get("FLASK_DEBUG", "True").lower() in ["true", "1"]

app = create_app()

if __name__ == "__main__":
    app.run(host=host, port=port, debug=debug)
