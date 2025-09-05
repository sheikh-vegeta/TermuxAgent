import subprocess
import os

class ExecutionService:
    """
    A service for executing shell commands and streaming their output.
    """

    def stream_command(self, command: str, in_vm: bool = False):
        """
        Executes a shell command and streams its stdout and stderr in real-time.

        Args:
            command (str): The command to execute.
            in_vm (bool): If True, the command is executed inside the proot-distro Ubuntu VM.

        Yields:
            str: A line of output from the command (stdout or stderr).
        """
        if in_vm:
            # Prepend the proot-distro command to run inside the Ubuntu VM.
            # The '--' is important to separate proot-distro options from the command itself.
            full_command = f"proot-distro login ubuntu -- {command}"
        else:
            full_command = command

        yield f"Executing: {full_command}\n"

        try:
            # We use Popen for non-blocking execution to read the output stream.
            # `stdout=subprocess.PIPE` and `stderr=subprocess.STDOUT` redirect stderr to stdout.
            # `text=True` decodes the output as text.
            # `bufsize=1` makes the output line-buffered.
            # `os.setsid` is used to create a new session, which allows us to kill the whole process group later if needed.
            process = subprocess.Popen(
                full_command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                preexec_fn=os.setsid
            )

            # Read the output line by line as it becomes available
            for line in iter(process.stdout.readline, ''):
                yield line

            # Wait for the process to complete and get the return code
            process.wait()
            return_code = process.returncode
            yield f"\n--- Command finished with exit code {return_code} ---\n"

        except FileNotFoundError:
            yield f"Error: Command not found. Make sure '{full_command.split()[0]}' is installed and in your PATH.\n"
        except Exception as e:
            yield f"An unexpected error occurred: {e}\n"

# Example usage (for testing)
if __name__ == '__main__':
    service = ExecutionService()

    print("--- Testing Host Execution ---")
    test_command_host = "echo 'Hello from host' && sleep 1 && ls -l"
    for output in service.stream_command(test_command_host):
        print(output, end='')

    print("\n--- Testing VM Execution (simulated) ---")
    # This will likely fail if proot-distro is not set up, but it demonstrates the command construction.
    test_command_vm = "echo 'Hello from VM' && ls -a /"
    for output in service.stream_command(test_command_vm, in_vm=True):
        print(output, end='')
