import asyncio
import json
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
import google.generativeai as genai

# Local module imports
from sandbox import SandboxManager
from config import load_config
import tools

# --- Globals ---
app = FastAPI()
sandbox_mgr = SandboxManager()
event_queue = asyncio.Queue()

# Load system prompt once at startup
try:
    with open("backend/prompt.md", "r") as f:
        SYSTEM_PROMPT = f.read()
except FileNotFoundError:
    print("ERROR: backend/prompt.md not found. The agent will not have instructions.")
    SYSTEM_PROMPT = "You are a helpful assistant."

# --- FastAPI Events ---
@app.on_event("startup")
async def startup_event():
    """
    On startup, load config and configure the generative AI model.
    """
    try:
        config = load_config()
        gemini_api_key = config.get("api_keys", {}).get("gemini")
        if not gemini_api_key or "YOUR_GEMINI_API_KEY" in gemini_api_key:
            print("WARNING: Gemini API key not found or not configured in config.json.")
        else:
            genai.configure(api_key=gemini_api_key)
            print("Gemini API configured successfully.")
    except FileNotFoundError:
        print("WARNING: config.json not found. API keys cannot be loaded.")

# --- Tool Dispatcher ---
async def dispatch_tool(tool_call: dict) -> dict:
    """
    Calls the appropriate tool based on the JSON object from the AI model.
    """
    tool_name = tool_call.get("tool")
    await event_queue.put({"type": "status", "data": f"AI requested to use tool: `{tool_name}`"})

    if tool_name == "shell":
        command = tool_call.get("command")
        if not command:
            return {"status": "error", "message": "No command provided for shell tool."}
        return await sandbox_mgr.run_command(command)

    elif tool_name == "google_search":
        query = tool_call.get("query")
        if not query:
            return {"status": "error", "message": "No query provided for google_search tool."}
        return await tools.google_search(query)

    else:
        return {"status": "error", "message": f"Unknown tool: {tool_name}"}

# --- API Endpoints ---
@app.post("/chat")
async def chat_endpoint(request: Request):
    """
    This is the main agent loop.
    1. Gets user request.
    2. Asks AI model to decide which tool to use.
    3. Executes the tool.
    4. Puts the result on the event queue for the SSE stream.
    """
    try:
        data = await request.json()
        user_message = data.get("message")
        if not user_message:
            return JSONResponse(status_code=400, content={"message": "No message provided."})

        await event_queue.put({"type": "status", "data": "Evaluating user request..."})

        # Ask the AI model for a tool call
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        prompt = f"{SYSTEM_PROMPT}\n\nUser Request: {user_message}"
        response = await model.generate_content_async(prompt)

        tool_call_json = response.text.strip()

        # The model sometimes wraps the JSON in ```json ... ```, so we clean it.
        if tool_call_json.startswith("```json"):
            tool_call_json = tool_call_json[7:-4].strip()

        try:
            tool_call = json.loads(tool_call_json)
        except json.JSONDecodeError:
            error_msg = "AI did not respond with valid JSON for tool call."
            print(f"ERROR: {error_msg}\nAI Response:\n{response.text}")
            await event_queue.put({"type": "error", "data": f"{error_msg}\nRaw AI response: {response.text}"})
            return {"status": "error", "message": error_msg}

        # Execute the chosen tool
        result = await dispatch_tool(tool_call)

        # Put the final result onto the queue
        await event_queue.put({"type": "result", "data": result, "tool_name": tool_call.get("tool")})

        return {"status": "Tool execution initiated."}

    except Exception as e:
        error_msg = f"An unexpected error occurred in the chat endpoint: {e}"
        print(error_msg)
        await event_queue.put({"type": "error", "data": error_msg})
        return JSONResponse(status_code=500, content={"message": error_msg})

@app.get("/sse")
async def sse_stream(request: Request):
    """
    Streams events from the event_queue to the connected client.
    """
    # This function remains the same as before.
    async def event_generator():
        while True:
            try:
                message = await event_queue.get()
                if await request.is_disconnected():
                    print("Client disconnected.")
                    break
                yield f"data: {json.dumps(message)}\n\n"
            except asyncio.CancelledError:
                break
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/")
def read_root():
    return {"message": "Termux Agent Backend is running."}
