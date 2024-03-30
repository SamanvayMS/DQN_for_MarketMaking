instanceName="$1"
startDate="$2"
endDate="$3"
outputDirectory="$4"
fullReports="$5"

last_cra_file_name=$(./run_backtest.sh "$instanceName" "$startDate" "$endDate" | grep '\.cra' | tail -n1 | awk '{print $NF}')

# check if the last cra file is equal to ""
if [ -z "$last_cra_file_name" ]; then
    echo "The last .cra file mentioned is empty"
    exit 1
fi

cd /home/vagrant/ss/bt/utilities/ && ./StrategyCommandLine cmd export_cra_file "$last_cra_file_name" "$output_directory" "$fullReports" "$fullReports"
