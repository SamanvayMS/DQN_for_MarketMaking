ifdef INTEL
    CC=icc
else
    CC=g++
endif

ifdef DEBUG
    CFLAGS=-c -g -fPIC -fpermissive -std=c++17
else
    CFLAGS=-c -fPIC -fpermissive -O3 -std=c++17
endif

LIBPATH=../../../../libs/x64
INCLUDEPATH=../../../../includes
SQLITEPATH=/groupstorage/group01/includes/sqlite_modern_cpp/hdr
LIBTORCH_PATH=/groupstorage/group01/includes/TorchIncludes/libtorch

INCLUDES=-I/usr/include -I$(INCLUDEPATH) -I$(INCLUDEPATH)/ -I$(LIBTORCH_PATH)/include -I$(LIBTORCH_PATH)/include/torch/csrc/api/include -I$(SQLITEPATH)/
LDFLAGS=$(LIBPATH)/libstrategystudio_analytics.a $(LIBPATH)/libstrategystudio.a $(LIBPATH)/libstrategystudio_transport.a $(LIBPATH)/libstrategystudio_marketmodels.a $(LIBPATH)/libstrategystudio_utilities.a $(LIBPATH)/libstrategystudio_flashprotocol.a -lsqlite3 -L$(LIBTORCH_PATH)/lib -ltorch -lc10 -Wl,-rpath,$(LIBTORCH_PATH)/lib

INSTANCE_NAME=DQNStrategy# single word, no special characters
STRATEGY_NAME=DQNStrategy# should be your cpp file name, single word, no special characters
START_DATE=2023-11-30# start of the earliest date
END_DATE=2023-11-30# end of the latest date
SYMBOLS=XNAS.ITCH-AAPL
PARAMETERS=name=DQNStrategy1|working=working
ACCOUNTSIZE=1000000

WORKINGDIR=/home/vagrant/ss/sdk/RCM/StrategyStudio/examples/strategies/DQN_for_MarketMaking
OUTPUT_DIR=$(WORKINGDIR)/${STRATEGY_NAME}/results
FULL_REPORTS=True

# Define the names of the library, source, and header files.
LIBRARY=DQNStrategy.so
SOURCES=DQNStrategy.cpp
HEADERS=DQNStrategy.h
OBJECTS=$(SOURCES:.cpp=.o)

.PHONY: all make_executable delete_instance clean_dlls move_strategy_dll build_strategy run_backtest

all: clean $(HEADERS) $(LIBRARY)

$(LIBRARY) : $(OBJECTS)
	$(CC) -shared -Wl,-soname,$(LIBRARY).1 -o $(LIBRARY) $(OBJECTS) $(LDFLAGS)
	
.cpp.o: $(HEADERS)
	$(CC) $(CFLAGS) $(INCLUDES) $< -o $@

clean: 
	rm -rf *.o $(LIBRARY)

# Simplifies the process of resetting local changes and pulling the latest code from the repository.
git_pull:
	chmod +x $(WORKINGDIR)/provision_scripts/git_pull.sh
	$(WORKINGDIR)/provision_scripts/git_pull.sh

make_executable:
	chmod +x $(WORKINGDIR)/provision_scripts/*.sh
	chmod +x $(WORKINGDIR)/provision_scripts/*.py
#	ls -l $(WORKINGDIR)/provision_scripts/

# deletes the instance from the sqlite database
delete_instance: make_executable
	pypy3 $(WORKINGDIR)/provision_scripts/delete_instance.py "$(INSTANCE_NAME)" "$(STRATEGY_NAME)"

# previous dlls need to be removed from the strategies_dlls folder
clean_dlls:
	mkdir -p /home/vagrant/ss/bt/strategies_dlls
	rm -rf /home/vagrant/ss/bt/strategies_dlls/*

# moves the dll to the strategies_dlls folder
move_strategy_dll: delete_instance clean_dlls all
	cp $(LIBRARY) /home/vagrant/ss/bt/strategies_dlls/.

# starts the server while performing above actions
start_server: move_strategy_dll 
	$(WORKINGDIR)/provision_scripts/start_server.sh

# ********************************************************************************************************************
# The following commands are used to create an instance, edit the parameters, and run a backtest.
# ********************************************************************************************************************

# builds the strategy instance
create_instance: 
	$(WORKINGDIR)/provision_scripts/create_instance.sh "$(INSTANCE_NAME)" "$(STRATEGY_NAME)" "$(SYMBOLS)" "$(PARAMETERS)" "$(ACCOUNTSIZE)"

# runs the backtest but does not process the results
run_backtest:
	$(WORKINGDIR)/provision_scripts/run_backtest.sh "$(INSTANCE_NAME)" "$(START_DATE)" "$(END_DATE)"

# runs the backtest and processes the results
run_backtest_with_results:
	$(WORKINGDIR)/provision_scripts/generate_results.sh "$(INSTANCE_NAME)" "$(START_DATE)" "$(END_DATE)" "$(OUTPUT_DIR)" "$(FULL_REPORTS)"

# edits the parameters of the instance
edit_params:
	$(WORKINGDIR)/provision_scripts/edit_parameters.sh "$(INSTANCE_NAME)" "$(STRATEGY_NAME)" "$(EPISODE_PARAMETERS)"

# ********************************************************************************************************************



