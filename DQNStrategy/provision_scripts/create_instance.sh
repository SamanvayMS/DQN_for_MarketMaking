#!/bin/bash

instanceName="$1"
strategyName="$2"
symbols="$3"
params="$4"
accountsize="$5"

echo "Creating instance" &&
cd /home/vagrant/ss/bt/utilities &&
./StrategyCommandLine cmd create_instance "$instanceName" "$strategyName" UIUC SIM-1001-101 dlariviere $accountsize -symbols $symbols - params $params &&
echo "Created instance" &&
./StrategyCommandLine cmd recheck_strategies &&
echo " **************************************************************************************************** "