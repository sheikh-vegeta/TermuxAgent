import httpx
import asyncio

class SandboxManager:
    """
    Manages communication with the Sandbox API which runs inside the proot-distro.
    """
    def __init__(self, api_base_url="http://127.0.0.1:8080"):
        self.api_base_url = api_base_url
        print(f"SandboxManager configured to use Sandbox API at: {self.api_base_url}")

    async def run_command(self, command: str) -> dict:
        """
        Sends a command to the Sandbox API for execution and returns the result.

        Args:
            command: The shell command to execute in the sandbox.

        Returns:
            A dictionary containing the execution result from the Sandbox API.
        """
        url = f"{self.api_base_url}/execute"
        payload = {"command": command}

        print(f"Sending command to sandbox: '{command}'")

        try:
            # Using a longer timeout to allow for slow commands
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()  # Raise an exception for 4xx/5xx responses
                return response.json()
        except httpx.ConnectError as e:
            error_msg = f"Connection to Sandbox API failed: {e}. Is the sandbox and its API server running?"
            print(error_msg)
            return {
                "status": "error",
                "message": error_msg,
                "command": command,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1,
            }
        except httpx.RequestError as e:
            error_msg = f"An error occurred while requesting the Sandbox API: {e}"
            print(error_msg)
            return {
                "status": "error",
                "message": error_msg,
                "command": command,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1,
            }
        except Exception as e:
            error_msg = f"An unexpected error occurred: {e}"
            print(error_msg)
            return {
                "status": "error",
                "message": error_msg,
                "command": command,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1,
            }
