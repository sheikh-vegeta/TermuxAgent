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
model = None  # Will be initialized on startup

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
    """On startup, load config and configure the generative AI model."""
    global model
    try:
        config = load_config()
        gemini_api_key = config.get("api_keys", {}).get("gemini")
        if not gemini_api_key or "YOUR_GEMINI_API_KEY" in gemini_api_key:
            print("WARNING: Gemini API key not found or not configured. AI features will be disabled.")
        else:
            genai.configure(api_key=gemini_api_key)
            model = genai.GenerativeModel('gemini-1.5-pro-latest')
            print("Gemini API configured successfully.")
    except FileNotFoundError:
        print("WARNING: config.json not found. API keys cannot be loaded.")

# --- Core Agent Logic ---
async def handle_tool_use(tool_call: dict):
    """Handles a single tool call from the AI."""
    tool_name = tool_call.get("tool")
    params = tool_call.get("params", {})
    await event_queue.put({"type": "status", "data": f"AI requested to use tool: `{tool_name}`"})

    if tool_name == "shell":
        result = await sandbox_mgr.run_command(params.get("command", ""))
    elif tool_name == "google_search":
        result = await tools.google_search(params.get("query", ""))
    else:
        result = {"status": "error", "message": f"Unknown tool: {tool_name}"}

    await event_queue.put({"type": "result", "data": result, "tool_name": tool_name})

async def handle_planning(plan: list, original_request: str):
    """Handles a research plan from the AI."""
    await event_queue.put({"type": "plan", "data": plan})

    collected_results = []
    for i, query in enumerate(plan):
        await event_queue.put({"type": "status", "data": f"Executing step {i+1}/{len(plan)}: Searching for '{query}'..."})
        search_result = await tools.google_search(query)
        await event_queue.put({"type": "plan_step_result", "data": search_result, "step": i+1})
        if search_result.get("status") == "success":
            collected_results.extend(search_result.get("results", []))

    await event_queue.put({"type": "status", "data": "All information gathered. Synthesizing report..."})

    synthesis_prompt = f"""
    Here is the collected research data on the topic: "{original_request}".
    Please synthesize this information into a concise and well-structured report.
    The data is a list of search results, each with a title, link, and snippet.
    Focus on extracting the key insights and trends from the data.

    Collected Data:
    {json.dumps(collected_results, indent=2)}
    """

    synthesis_response = await model.generate_content_async(synthesis_prompt)
    await event_queue.put({"type": "final_report", "data": synthesis_response.text})


# --- API Endpoints ---
@app.post("/chat")
async def chat_endpoint(request: Request):
    """This is the main agent entry point."""
    try:
        data = await request.json()
        user_message = data.get("message")
        if not user_message:
            return JSONResponse(status_code=400, content={"message": "No message provided."})

        if not model:
            await event_queue.put({"type": "error", "data": "AI model is not configured. Please check API keys."})
            return JSONResponse(status_code=500, content={"message": "AI model not configured."})

        await event_queue.put({"type": "status", "data": "Evaluating request..."})

        prompt = f"{SYSTEM_PROMPT}\n\nUser Request: {user_message}"
        response = await model.generate_content_async(prompt)

        response_json_str = response.text.strip()
        if response_json_str.startswith("```json"):
            response_json_str = response_json_str[7:-4].strip()

        try:
            ai_response = json.loads(response_json_str)
        except json.JSONDecodeError:
            error_msg = f"AI did not respond with valid JSON. Raw response: {response.text}"
            await event_queue.put({"type": "error", "data": error_msg})
            return JSONResponse(status_code=500, content={"message": error_msg})

        # --- Mode Dispatcher ---
        mode = ai_response.get("mode")
        if mode == "planning":
            # This is a research task. It's a long-running job, so we start it
            # in the background and return immediately. The results will be streamed.
            asyncio.create_task(handle_planning(ai_response.get("plan", []), user_message))
        elif mode == "tool_use":
            # This is a single, short-lived tool call.
            await handle_tool_use(ai_response)
        else:
            error_msg = f"AI responded with an unknown mode: '{mode}'"
            await event_queue.put({"type": "error", "data": error_msg})
            return JSONResponse(status_code=500, content={"message": error_msg})

        return {"status": "Request is being processed."}

    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        print(error_msg)
        await event_queue.put({"type": "error", "data": error_msg})
        return JSONResponse(status_code=500, content={"message": error_msg})

@app.get("/sse")
async def sse_stream(request: Request):
    """Streams events from the event_queue to the client."""
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
