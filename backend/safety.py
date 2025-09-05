import subprocess
import shutil
import re
import os

# Command allowlist: Regex for safe code (e.g., no os.system)
def command_allowlist(code: str) -> bool:
    """
    Checks if the code contains potentially unsafe patterns.
    A simple implementation for demonstration purposes.
    """
    unsafe_patterns = [r"os\.system", r"subprocess\.run", r"exec", r"eval"]
    for pattern in unsafe_patterns:
        if re.search(pattern, code):
            return False
    return True

# Sandbox exec: Use proot-distro (assume installed)
def sandbox_exec(code: str, timeout: int = 5) -> str:
    """
    Executes Python code in a sandboxed environment using proot-distro.
    """
    # Write to a temporary file to be executed
    temp_file = "/tmp/sandbox_exec.py"
    with open(temp_file, "w") as f:
        f.write(code)

    try:
        # Use proot-distro to run the script in an isolated Alpine Linux environment
        result = subprocess.run(
            ["proot-distro", "login", "alpine", "--", "python3", temp_file],
            capture_output=True,
            timeout=timeout,
            check=False, # Do not raise exception on non-zero exit code
            text=True
        )

        output = ""
        if result.stdout:
            output += f"Output:\n{result.stdout}\n"
        if result.stderr:
            output += f"Errors:\n{result.stderr}\n"

        return output if output else "Command executed with no output."

    except subprocess.TimeoutExpired:
        return "Execution timed out."
    except FileNotFoundError:
        return "Error: 'proot-distro' command not found. Please ensure it is installed and in your PATH."
    except Exception as e:
        return f"An unexpected error occurred during execution: {e}"

# Backup file utility
def backup_file(path: str):
    """
    Creates a backup of a file by copying it with a .bak extension.
    """
    if os.path.exists(path):
        shutil.copy(path, path + ".bak")
        return f"Backup of {path} created at {path}.bak"
    return f"File not found at {path}, no backup created."
