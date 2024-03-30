import subprocess
import os


def make_with_python(command):
    # Execute the command
    result = subprocess.run(command, capture_output=True, text=True)

    # Check the result
    if result.returncode == 0:
        print("Command executed successfully.")
        print("Output:", result.stdout)
    else:
        print("Error occurred:", result.stderr)
        
if __name__=="__main__":
    # Command to execute
    command = ["make", "start_server"]
    
    # Execute the command
    make_with_python(command)