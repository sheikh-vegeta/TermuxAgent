from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from sandbox import SandboxManager
import asyncio
import json

app = FastAPI()
sandbox_mgr = SandboxManager()

# Use asyncio.Queue to bridge the gap between the HTTP request-response cycle
# of the /chat endpoint and the long-lived connection of the /sse endpoint.
event_queue = asyncio.Queue()

@app.post("/chat")
async def chat_endpoint(request: Request):
    """
    Receives a command from the user, executes it in the sandbox via SandboxManager,
    and queues the result to be sent over the SSE stream.
    """
    try:
        data = await request.json()
        command = data.get("message")

        if not command:
            return JSONResponse(status_code=400, content={"message": "No message/command provided in request."})

        # Acknowledge receipt of the command by putting a status message in the queue.
        await event_queue.put({"type": "status", "data": f"Received command: '{command}'. Executing..."})

        # Asynchronously run the command. The sandbox_mgr handles the communication.
        result = await sandbox_mgr.run_command(command)

        # Put the final result dictionary into the queue.
        await event_queue.put({"type": "result", "data": result})

        return {"status": "Command sent for execution."}
    except Exception as e:
        error_msg = f"Error processing chat request: {e}"
        print(error_msg)
        # Also try to inform the client via SSE if possible
        await event_queue.put({"type": "error", "data": error_msg})
        return JSONResponse(status_code=500, content={"message": error_msg})

@app.get("/sse")
async def sse_stream(request: Request):
    """
    This endpoint streams events from the event_queue to the connected client.
    It's a long-lived connection.
    """
    async def event_generator():
        while True:
            try:
                # Wait for a message from the queue.
                message = await event_queue.get()

                if await request.is_disconnected():
                    print("Client disconnected, closing SSE stream.")
                    break

                # The message is already a dict, so we just need to dump it to a string.
                yield f"data: {json.dumps(message)}\n\n"

            except asyncio.CancelledError:
                # This happens when the client disconnects.
                print("SSE stream cancelled.")
                break
            except Exception as e:
                print(f"Error in SSE stream: {e}")
                # Don't break the loop on other errors, just report them.
                yield f"data: {json.dumps({'type': 'error', 'data': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/")
def read_root():
    return {"message": "Termux Agent Backend is running."}

# To run this server: uvicorn main_server:app --host 0.0.0.0 --port 8000 --reload
