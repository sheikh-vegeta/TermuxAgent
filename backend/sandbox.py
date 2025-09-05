import subprocess
import asyncio

class SandboxManager:
    """
    Manages the proot-distro sandbox environment.
    """
    def __init__(self, distro="ubuntu"):
        self.distro = distro
        self.process = None

    def start(self):
        """
        Starts a login session in the specified distro.
        This is a simplified example; a real implementation would handle
        process management more robustly.
        """
        try:
            # The command needs to be run in the background to not block.
            # A more robust solution would use asyncio.create_subprocess_shell
            self.process = subprocess.Popen(
                ["proot-distro", "login", self.distro],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            print(f"Started sandbox session for distro '{self.distro}' with PID: {self.process.pid}")
        except FileNotFoundError:
            print("Error: 'proot-distro' command not found. Please ensure it is installed.")
            raise

    def stop(self):
        """Stops the sandbox process."""
        if self.process:
            self.process.terminate()
            print(f"Stopped sandbox session for distro '{self.distro}'.")

    async def stream_events(self):
        """
        A dummy event generator to simulate streaming events from the sandbox.
        In a real application, this would tail logs or use another IPC mechanism.
        """
        for i in range(10):
            yield f"Event {i} from the sandbox."
            await asyncio.sleep(1)
