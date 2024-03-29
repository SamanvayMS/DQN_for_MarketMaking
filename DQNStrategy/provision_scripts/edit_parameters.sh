instanceName="$1"
strategyName="$2"
new_params="$3"

echo "changing parameters to $new_params" &&
cd /home/vagrant/ss/bt/utilities && ./StrategyCommandLine cmd params $new_params {-name $instanceName} {-type $strategyName} &&

echo "parameters changed resetting strategy" &&
cd /home/vagrant/ss/bt/utilities && ./StrategyCommandLine cmd recheck_strategies &&

echo "strategy reset succesfully" &&
echo " **************************************************************************************************** "

