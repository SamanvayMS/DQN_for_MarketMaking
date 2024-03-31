import subprocess
import sys

def make_with_python(command):
    try:
        # Execute the command with check=True to automatically raise an exception for non-zero return codes
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=100)
        print("Command executed successfully.")
        return True  # Indicates success
    except subprocess.CalledProcessError as e:
        # Catches errors where the subprocess itself fails to run or returns a non-zero exit status.
        print(f"Command '{e.cmd}' returned non-zero exit status {e.returncode}.")
    except subprocess.TimeoutExpired as e:
        # Catches timeout errors
        print(f"Command '{e.cmd}' timed out after {e.timeout} seconds.")
    except Exception as e:
        # Catches any other exceptions
        print(f"An unexpected error occurred: {e}")
    return False  # Indicates failure

if __name__=="__main__":
    # Command to execute
    episode_parameters = "name=DQNStrategy2|working=workingverywell"
    episode_date = "2023-11-30"
    if sys.argv[1] == "0":
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
    
    # Execute the commands, stopping if one fails
    for command in commands:
        success = make_with_python(command)
        if not success:
            sys.exit(1)  # Terminate the program if a command fails