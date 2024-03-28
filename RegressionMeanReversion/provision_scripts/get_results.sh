#!/bin/bash

instanceName="$1"
startDate="$2"
endDate="$3"
symbols="$4"
parameters="$5"
accountsize="$6"
backtestid="$7"

csv_dump_directory="/groupstorage/group01/backtest_data/$instanceName/$backtestid/csv_files"

echo startDate
cd /home/vagrant/ss/bt/backtesting-results

startDateFormatted=$(date -d $startDate "+%m-%d-%Y")
endDateFormatted=$(date -d $endDate "+%m-%d-%Y")

latestCRA=$(ls /home/vagrant/ss/bt/backtesting-results/BACK_${instanceName}_*start_${startDateFormatted}_end_${endDateFormatted}.cra -t | head -n1)

cd /home/vagrant/ss/sdk/RCM/StrategyStudio/examples/strategies/group_01_project/"$instanceName"/provision_scripts
python_script="results_analytics.py"
file_path="/groupstorage/group01/backtest_data/${instanceName}/${backtestid}/"

# run the above script
echo "starting data analysis"
python3 "$python_script" "$latestCRA" "$file_path" "$symbols" "$parameters" "$accountsize"
status=$?

# successfully run will print the confirmation message
if [ $status -eq 0 ]; then
    echo "Python script updated backtest_data"
else
    echo "Python script did not update backtest_data"
fi