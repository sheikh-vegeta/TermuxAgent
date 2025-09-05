from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Sandbox API is running."}

@app.post("/execute")
async def execute_in_sandbox(command: dict):
    # In a real implementation, this would execute the command
    # using the 'safety' and 'sandbox' modules.
    cmd_text = command.get("command", "no command given")
    print(f"Executing in sandbox: {cmd_text}")
    return {"status": "executed", "command": cmd_text}
