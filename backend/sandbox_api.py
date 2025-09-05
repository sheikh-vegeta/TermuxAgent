from fastapi import FastAPI
import asyncio

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Sandbox API is running."}

@app.post("/execute")
async def execute_in_sandbox(command: dict):
    """
    Executes a command in the sandbox and returns the output.
    """
    cmd_text = command.get("command")
    if not cmd_text:
        return {"status": "error", "message": "No command provided."}

    print(f"Executing in sandbox: {cmd_text}")

    try:
        process = await asyncio.create_subprocess_shell(
            cmd_text,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        response = {
            "status": "completed",
            "command": cmd_text,
            "stdout": stdout.decode().strip(),
            "stderr": stderr.decode().strip(),
            "returncode": process.returncode
        }
        print(f"Execution finished with return code {process.returncode}")
        return response

    except Exception as e:
        print(f"Error executing command: {e}")
        return {"status": "error", "command": cmd_text, "message": str(e)}
