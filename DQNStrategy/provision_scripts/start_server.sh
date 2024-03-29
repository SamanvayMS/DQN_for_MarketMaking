
echo "Starting server" 
# quits previously created server
cd /home/vagrant/ss/bt/utilities && ./StrategyCommandLine cmd quit
# starts up the server and keeps it in the background
cd /home/vagrant/ss/bt/ && ./StrategyServerBacktesting server.log 2>&1 & 
sleep 10 # sleep for 10 seconds
echo "Started server" 
echo " **************************************************************************************************** "

