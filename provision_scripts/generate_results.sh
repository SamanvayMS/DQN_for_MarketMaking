workingDir="$1"
instanceName="$2"
startDate="$3"
endDate="$4"
outputDirectory="$5"
fullReports="$6"

# runs the backtest and gets the last cra file name
last_cra_file_name=$("$workingDir"/provision_scripts/run_backtest.sh "$instanceName" "$startDate" "$endDate" | grep '\.cra' | tail -n1 | awk '{print $NF}')

# check if the last cra file is equal to ""
if [ -z "$last_cra_file_name" ]; then
    echo "The last .cra file mentioned is empty"
    exit 1
fi

cd /home/vagrant/ss/bt/utilities/ && ./StrategyCommandLine cmd export_cra_file "$last_cra_file_name" "$output_directory" "$fullReports" "$fullReports"

