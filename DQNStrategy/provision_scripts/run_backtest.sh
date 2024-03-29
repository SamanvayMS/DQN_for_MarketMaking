#!/bin/bash

instanceName="$1"
startDate="$2"
endDate="$3"

echo $instanceName &&
echo $startDate &&
echo $endDate &&

cd /home/vagrant/ss/bt/utilities/ && ./StrategyCommandLine cmd start_backtest "$startDate" "$endDate" "$instanceName" 0 
echo " **************************************************************************************************** "

# Path to your log file
log_file="path/to/your/logfile.log"
sleep 1
while true; do
    # Get the number of lines in the log file
    num_lines=$(wc -l < "$log_file")
    line_number=$(grep -n "finished\.$" "$log_file" | tail -n 1 | cut -d: -f1)
    # Check if the last line ending with "finished." is the last line in the log file
    if [ "$num_lines" -gt "$line_number" ]; then
        echo "Waiting for strategy to finish"
        sleep 1
    else
        break
    fi
done
