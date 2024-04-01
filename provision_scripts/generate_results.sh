workingDir="$1"
instanceName="$2"
startDate="$3"
endDate="$4"
outputDirectory="$5"
fullReports="$6"

CRA_path="/home/vagrant/ss/bt/backtesting-results/"
# runs the backtest and gets the last cra file name
last_cra_file_name=$("$workingDir"/provision_scripts/run_backtest.sh "$instanceName" "$startDate" "$endDate" | grep '\.cra' | tail -n1 | awk '{print $NF}')
mv "$CRA_path$last_cra_file_name" "$outputDirectory/"
sleep 10
# check if the last cra file is equal to ""
if [ -z "$last_cra_file_name" ]; then
    echo "The last .cra file mentioned is empty"
    exit 1
fi

# Check if output directory exists; if not, create it
if [ ! -d "$outputDirectory" ]; then
    mkdir -p "$outputDirectory"
fi

echo "cra file name: $last_cra_file_name"
cd /home/vagrant/ss/bt/utilities/ 
./StrategyCommandLine cmd export_cra_file "$outputDirectory$last_cra_file_name" 
echo "output directory: $outputDirectory"
echo "****************************************************************************************************"

