from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from sandbox import SandboxManager
import asyncio

app = FastAPI()
sandbox_mgr = SandboxManager()

@app.on_event("startup")
async def startup_event():
    """
    On startup, you might want to start the sandbox automatically.
    Note: This is a simple example. A real app would need more
    robust process management.
    """
    # sandbox_mgr.start()
    print("Backend server started. Sandbox can be started via an API call.")


@app.get("/sse")
async def sse(request: Request):
    """
    Server-Sent Events endpoint to stream events from the sandbox.
    """
    async def event_stream():
        # This is a simplified stream. A real implementation would
        # listen to a message queue or a log file from the sandbox.
        async for event in sandbox_mgr.stream_events():
            # Check if the client has disconnected
            if await request.is_disconnected():
                print("Client disconnected.")
                break
            yield f"data: {event}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")

@app.get("/")
def read_root():
    return {"message": "Termux Agent Backend is running."}
