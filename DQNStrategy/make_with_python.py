import subprocess
import os


def make_with_python(command):
    try:
        # Execute the command
        result = subprocess.run(command, capture_output=True, text=True, check=True, timeout=60)
        print("Command executed successfully.")
        print("Output:", result.stdout)
    except subprocess.CalledProcessError as e:
        # This catches errors where the subprocess itself fails to run or returns a non-zero exit status.
        print(f"Command '{e.cmd}' returned non-zero exit status {e.returncode}.")
        print("Error output:", e.stderr)
    except subprocess.TimeoutExpired as e:
        print(f"Command '{e.cmd}' timed out after {e.timeout} seconds.")
    except Exception as e:
        # This catches any other exceptions that are not subprocess.CalledProcessError.
        print(f"An unexpected error occurred: {e}")
        
if __name__=="__main__":
    # Command to execute
    command = ["make", "start_server"]
    
    # Execute the command
    make_with_python(command)