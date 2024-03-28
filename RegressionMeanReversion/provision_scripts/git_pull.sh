cd /home/vagrant/ss/sdk/RCM/StrategyStudio/examples/strategies/

REPO_DIR="group_01_project"
# rm -rf "$REPO_DIR"

if [ -d "$REPO_DIR" ]; then
    cd "$REPO_DIR"
    git fetch origin
    git reset --hard origin/samanvay # we do hard reset because we want to overwrite any local changes
    cd ..
    echo "We pulled the repo."
else
    # USE YOUR HTTPS URL HERE IF SSH DOESN'T WORK
    git clone -b samanvay git@gitlab.engr.illinois.edu:fin556_algo_market_micro_fall_2023/fin556_algo_fall_2023_group_01/group_01_project.git
    echo "We created the repo."
fi