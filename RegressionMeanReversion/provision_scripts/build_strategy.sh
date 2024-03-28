#!/bin/bash

instanceName="$1"
strategyName="$2"
startDate="$3"
endDate="$4"
symbols="$5"
accountsize="$6"

echo $instanceName
echo $strategyName
echo $startDate
echo $endDate
echo $symbols

cd /home/vagrant/ss/bt/utilities; ./StrategyCommandLine cmd quit
sleep 10
cd /home/vagrant/ss/bt/ ; ./StrategyServerBacktesting &
sleep 1
echo "Started server"
cd /home/vagrant/ss/bt/utilities
./StrategyCommandLine cmd create_instance "$instanceName" "$strategyName" UIUC SIM-1001-101 dlariviere $accountsize -symbols $symbols
echo "Created instance"
sleep 1
