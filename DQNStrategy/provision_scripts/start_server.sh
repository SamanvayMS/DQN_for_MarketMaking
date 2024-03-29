
echo "Starting server" &&
# quits previously created server
cd /home/vagrant/ss/bt/utilities && ./StrategyCommandLine cmd quit
# starts up the server and keeps it in the background
cd /home/vagrant/ss/bt/ && ./StrategyServerBacktesting server.log 2>&1 & 
echo "Started server" &&
echo " **************************************************************************************************** "

