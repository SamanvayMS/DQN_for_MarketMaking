#!/bin/bash

instanceName="$1"
startDate="$2"
endDate="$3"
symbols="$4"
parameters="$5"
accountsize="$6"
backtestid="$7"

echo $instanceName
echo $startDate
echo $endDate

csv_dump_directory="/groupstorage/group01/backtest_data/$instanceName/$backtestid/csv_files"

# Check if the directory exists
if [ ! -d "$csv_dump_directory" ]; then
    # If it doesn't exist, create it
    mkdir -p "$csv_dump_directory"
    echo "Directory created: $csv_dump_directory"
else
    echo "Directory already exists: $csv_dump_directory"
fi

# Start the backtesting server
(cd /home/vagrant/ss/bt && pwd && ls && ./StrategyServerBacktesting&)

echo "Sleeping for 2 seconds while waiting for strategy studio to boot"
sleep 2

# Start the backtest
(cd /home/vagrant/ss/bt/utilities/ && pwd && ls && ./StrategyCommandLine cmd start_backtest "$startDate" "$endDate" "$instanceName" 0)

foundFinishedLogFile=$(grep -nr "finished.$" /home/vagrant/ss/bt/logs/main_log.txt | gawk '{print $1}' FS=":"|tail -1)

echo "Last line found:",$foundFinishedLogFile

while ((logFileNumLines > foundFinishedLogFile))
do
    foundFinishedLogFile=$(grep -nr "finished.$" /home/vagrant/ss/bt/logs/main_log.txt | gawk '{print $1}' FS=":"|tail -1)
    echo "Waiting for strategy to finish"
    sleep 1
done

echo "Sleeping for 40 seconds..."
sleep 40
echo "run_backtest.sh completed"

cd /home/vagrant/ss/bt/backtesting-results

startDateFormatted=$(date -d $startDate "+%m-%d-%Y")
endDateFormatted=$(date -d $endDate "+%m-%d-%Y")

latestCRA=$(ls /home/vagrant/ss/bt/backtesting-results/BACK_${instanceName}_*start_${startDateFormatted}_end_${endDateFormatted}.cra -t | head -n1)

echo "Latest CRA file path:", $latestCRA
cd /home/vagrant/ss/bt/utilities/
pwd
./StrategyCommandLine cmd export_cra_file $latestCRA $csv_dump_directory true true
sleep 5
# ./StrategyCommandLine cmd quit
cd /home/vagrant/ss/sdk/RCM/StrategyStudio/examples/strategies/group_01_project/$instanceName/provision_scripts
# # Path to your Python script
# python_script="/home/vagrant/ss/sdk/RCM/StrategyStudio/examples/strategies/group_01_project/$instanceName/provision_scripts/results_analytics.py"
python_script="results_analytics.py"
file_path="/groupstorage/group01/backtest_data/$instanceName/$backtestid/"

echo "starting data analysis"
# # Call the Python script with the latest CRA file path and JSON file path
python3 "$python_script" "$latestCRA" "$file_path" "$symbols" "$parameters" "$accountsize"
status=$?

if [ $status -eq 0 ]; then
    echo "Python script updated backtest_data"
    # cd ..
    # git config --global user.email "sm105@illinois.edu"
    # git config --global user.name "Samanvay Malapally Sudhakara"
    # git add backtest_data.json
    # git commit -m "Added new backtest result"
    # git push origin main
    # echo "Pushed new backtest result to gitlab repo."
else
    echo "Python script did not update backtest_data"
fi
