import subprocess
import os
import sys


def make_with_python(command):
    try:
        # Execute the command
        result = subprocess.run(command,timeout=30)
        print("Command executed successfully.")
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
    episode_parameters = "name=DQNStrategy2|working=workingverywell"
    episode_date = "2023-11-30"
    if sys.argv[1] == 0:
        commands = [
            ["make", "start_server"],
            ["make", "create_instance"],
            ["make", "run_backtest"]
            ]
    else:
        commands = [
            ["make", "start_server"],
            ["make", "create_instance"],
            ["make", "edit_params", f"EPISODE_PARAMETERS={episode_parameters}"],
            ["make", "run_backtest", f"START_DATE={episode_date}", f"END_DATE={episode_date}"]
            ]
    
    # Execute the command
    for command in commands:
        make_with_python(command)