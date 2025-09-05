import os
import json
import redis
import logging
from fastapi import FastAPI, Request, HTTPException
from google.generativeai import configure, GenerativeModel
from diff_match_patch import diff_match_patch
from mcp import mcp_process
from safety import sandbox_exec, command_allowlist

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("../logs/agent.log"),
        logging.StreamHandler()
    ]
)

# --- Configuration ---
def load_config():
    try:
        with open("config.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logging.warning("config.json not found, using example config. Please rename config.json.example and fill in your API key.")
        with open("config.json.example", "r") as f:
            return json.load(f)

config = load_config()
api_keys = config.get("api_keys", {})
preferences = config.get("preferences", {})
redis_config = config.get("redis", {})

# --- API and Model Setup ---
try:
    configure(api_key=api_keys.get("gemini"))
    model = GenerativeModel(preferences.get("default_model", "gemini-1.5-pro"))
except Exception as e:
    logging.error(f"Failed to configure Gemini: {e}")
    model = None

# --- Redis Setup ---
redis_client = None
if redis_config.get("use_redis"):
    try:
        redis_client = redis.Redis(
            host=redis_config.get("host"),
            port=redis_config.get("port"),
            db=redis_config.get("db"),
            decode_responses=True
        )
        redis_client.ping()
        logging.info("Successfully connected to Redis.")
    except Exception as e:
        logging.error(f"Failed to connect to Redis: {e}")
        redis_client = None

# --- System Prompt ---
with open("prompt.md", "r") as f:
    SYSTEM_PROMPT = f.read()

app = FastAPI()

# --- Helper Functions for History ---
def get_history(session_id: str) -> list:
    if redis_client:
        history_json = redis_client.get(session_id)
        return json.loads(history_json) if history_json else []
    # Fallback to file-based history
    try:
        with open(f"../logs/{session_id}.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_history(session_id: str, history: list):
    if redis_client:
        redis_client.set(session_id, json.dumps(history))
    else:
        with open(f"../logs/{session_id}.json", "w") as f:
            json.dump(history, f)

# --- API Endpoints ---
@app.post("/api/chat")
async def chat(request: Request):
    if not model:
        raise HTTPException(status_code=503, detail="AI model is not configured.")

    data = await request.json()
    code = data.get("code", "")
    context = data.get("context", "")
    user_prompt = data.get("prompt", "")
    session_id = data.get("session_id", "default_session")
    logging.info(f"Received chat request for session: {session_id}")

    history = get_history(session_id)
    full_prompt = f"{SYSTEM_PROMPT}\n\nContext: {context}\nCode: {code}\nUser: {user_prompt}\nHistory: {json.dumps(history)}"

    response_data = mcp_process(model, full_prompt)

    # Generate diff if code is present
    diff_text = ""
    if code and response_data.get("code"):
        dmp = diff_match_patch()
        patches = dmp.patch_make(code, response_data["code"])
        diff_text = dmp.patch_toText(patches)

    response_data["diff"] = diff_text

    # Update history
    new_history = history + [{"user": user_prompt, "agent": response_data}]
    save_history(session_id, new_history)
    logging.info(f"Successfully processed chat request for session: {session_id}")

    return response_data

@app.post("/api/execute")
async def execute(request: Request):
    data = await request.json()
    code_to_exec = data.get("code", "")
    logging.info(f"Received execution request for code: {code_to_exec[:80]}...")

    if not command_allowlist(code_to_exec):
        logging.warning(f"Execution denied for unsafe command: {code_to_exec}")
        raise HTTPException(status_code=403, detail="Unsafe command detected.")

    result = sandbox_exec(code_to_exec)
    logging.info(f"Execution result: {result}")
    return {"output": result}
