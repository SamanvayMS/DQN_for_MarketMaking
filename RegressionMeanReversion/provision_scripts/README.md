
# Provision_scripts README

## 1. `update_parameters.py`

### Purpose

This Python script is designed to update trading parameters in a trading strategy.

### Functionality

- It takes command-line arguments where each argument represents a trading parameter.
- The script expects the parameters to be passed in a specific format, likely separated by the `|` character.
- Each parameter is written to a file named `parameters.txt`, which is then used by the trading strategy.

### Usage

Run the script from the command line, passing the parameters as arguments.

```bash
python update_parameters.py "param1|param2|param3..."
```

For example:

```bash
python update_parameters.py "risk_level=5|entry_threshold=1.2"
```

## 2. `results_analytics.py`

### Purpose

This script is used for analyzing and visualizing the results of trading backtests.

### Functionality

- It imports several key Python libraries like `pandas`, `numpy`, and `matplotlib`, indicating its use in data manipulation and visualization.
- The script likely processes files (possibly `.cra` files) containing backtest results and extracts relevant data.
- It may also generate various analytics such as performance metrics, risk assessments, and graphical representations of the data.

### Usage

Typically not run directly, but called from other scripts (like `run_backtest.sh`) with the required file paths and parameters.

```bash
python results_analytics.py "cra_file_path" "backtest_directory" "symbols" "parameters" "backtest_id"
```

## 3. `delete_instance.py`

### Purpose

Used for deleting or resetting instances in a trading environment.

### Functionality

- Specifics of the script's operations are not clear without a deeper look into the code.
- It likely interacts with a database or file system to remove records or files associated with a particular instance of a trading strategy.

### Usage

it requires the instance identifier as input.

```bash
python delete_instance.py "instance_id"
```

## 4. `git_pull.sh`

### Purpose

Shell script to synchronize the local repository with the remote repository.

### Functionality

- Performs a `git fetch` and a `git reset --hard` - effectively a 'git pull'
- Includes additional commands for navigating directories or handling post-pull operations.

### Usage

Run the script from the command line.

```bash
./git_pull.sh
```

## 5. `run_backtest.sh`

### Purpose

Executes backtesting of trading strategies and processes the results.

### Functionality

- Initiates the backtesting process, with specific parameters and configurations.
- Monitors the process, checking for completion.
- Once backtesting is complete, it locates the latest cra result file and calls `results_analytics.py` to process these results.
- includes steps for handling the output, such as moving files, updating a database, or pushing changes to a repository.

### Usage

Run the script from the command line. It might require specific environment variables or configurations.

```bash
./run_backtest.sh
```

