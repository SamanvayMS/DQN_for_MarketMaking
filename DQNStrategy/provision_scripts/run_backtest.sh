#!/bin/bash

instanceName="$1"
startDate="$2"
endDate="$3"

echo $instanceName &&
echo $startDate &&
echo $endDate &&

cd /home/vagrant/ss/bt/utilities/ && ./StrategyCommandLine cmd start_backtest "$startDate" "$endDate" "$instanceName" 0 > /home/vagrant/ss/sdk/RCM/StrategyStudio/examples/strategies/DQN_for_MarketMaking/backtest.log 
echo " **************************************************************************************************** "



