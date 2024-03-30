#!/bin/bash

instanceName="$1"
startDate="$2"
endDate="$3"

echo $instanceName &&
echo $startDate &&
echo $endDate &&

cd /home/vagrant/ss/bt/utilities/ && ./StrategyCommandLine cmd start_backtest "$startDate" "$endDate" "$instanceName" 0 

# Path to your log file
log_file="/home/vagrant/ss/bt/logs/main_log.txt"

sleep 1
while true; do
    # Get the number of lines in the log file
    num_lines=$(wc -l < "$log_file")
    # Initialize line_number to 0
    line_number=$(grep -n "finished\.$" "$log_file" | tail -n 1 | cut -d: -f1)
    echo "$num_lines"
    echo "$line_number"
    # Check if the last line ending with "finished." is the last line in the log file
    if [ "$num_lines" -gt "$line_number" ]; then
        echo "Waiting for strategy to finish"
        sleep 5
    else
        last_cra_file=$(grep '\.cra' "$log_file" | tail -n1 | awk '{print $NF}')
        echo "found CRA file :- "
        echo "$last_cra_file"
        echo "Strategy finished"
        break
    fi
done

echo "run backtest complete"
echo " **************************************************************************************************** "