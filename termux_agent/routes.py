import os
import subprocess
from functools import wraps
from flask import Blueprint, request, jsonify, render_template, current_app, Response
from .gemini_client import GeminiClient
from .services.execution_service import ExecutionService

# Create a Blueprint for API routes
api_bp = Blueprint('api_bp', __name__)

# --- Initialize Services ---
execution_service = ExecutionService()
try:
    gemini_client = GeminiClient()
except ValueError as e:
    gemini_client = None
    print(f"Error initializing GeminiClient: {e}")


# --- API Key Authentication ---
def require_api_key(f):
    """
    Decorator to protect routes with an API key.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        expected_api_key = os.environ.get('API_KEY')
        if not expected_api_key:
            return jsonify({"error": "API key is not configured on the server."}), 500
        provided_key = request.headers.get('X-API-Key')
        if not provided_key or provided_key != expected_api_key:
            return jsonify({"error": "Unauthorized. Invalid or missing API key."}), 401
        return f(*args, **kwargs)
    return decorated_function

# --- Service Availability Check ---
def check_gemini_service(f):
    """
    Decorator to check if the Gemini client is available.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if gemini_client is None:
            return jsonify({"error": "AI service is unavailable. Check server configuration."}), 503
        return f(*args, **kwargs)
    return decorated_function

# --- Web Interface Routes ---
@api_bp.route('/')
def index():
    """
    Serves the main web chat interface.
    """
    return render_template('index.html')

@api_bp.route('/terminal')
def terminal():
    """
    Serves the terminal interface.
    """
    return render_template('terminal.html')

# --- API Routes ---
@api_bp.route('/api/chat', methods=['POST'])
@require_api_key
@check_gemini_service
def chat_handler():
    """
    Handles chat requests using the Gemini client.
    The OpenAPI spec for this is in openapi.yaml.
    """
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"error": "Invalid request. 'message' field is required."}), 400

    user_message = data.get('message')
    history = data.get('history', [])

    # Get the response from the Gemini client
    ai_reply = gemini_client.send_chat_message(user_message, history)

    # Update history
    new_history = history + [
        {'role': 'user', 'parts': [user_message]},
        {'role': 'model', 'parts': [ai_reply]}
    ]

    return jsonify({
        "reply": ai_reply,
        "history": new_history
    })

@api_bp.route('/api/execute', methods=['POST'])
@require_api_key
def execute_handler():
    """
    Executes a shell command and streams the output.
    The OpenAPI spec for this is in openapi.yaml.
    """
    data = request.get_json()
    if not data or 'command' not in data:
        return Response("Invalid request. 'command' field is required.", status=400, mimetype='text/plain')

    command = data.get('command')
    in_vm = data.get('in_vm', False)

    # The actual streaming is handled by the generator function passed to the Response object
    return Response(execution_service.stream_command(command, in_vm), mimetype='text/plain')

@api_bp.route('/api/device-check', methods=['GET'])
@require_api_key
def device_check_handler():
    """
    Performs a series of checks on the Termux environment to validate compatibility.
    """
    checks = {
        "architecture": "uname -m",
        "proot_distro_installed": "command -v proot-distro",
        "termux_api_package": "dpkg -s termux-api"
    }

    results = {}
    # We can't use the streaming service here easily, so we'll use a simple subprocess run.
    for key, command in checks.items():
        try:
            # Using subprocess.run to get the full output at once.
            process = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                check=False # Do not raise exception on non-zero exit codes
            )

            if process.returncode == 0:
                results[key] = {"status": "success", "output": process.stdout.strip()}
            else:
                # For checks like 'command -v', a non-zero exit code means 'not found'.
                # For dpkg, it means not installed.
                results[key] = {"status": "failure", "output": process.stderr.strip()}

        except Exception as e:
            results[key] = {"status": "error", "output": str(e)}

    return jsonify(results)
