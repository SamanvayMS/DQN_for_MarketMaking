ifdef INTEL
    CC=icc
else
    CC=g++
endif

ifdef DEBUG
    CFLAGS=-c -g -fPIC -fpermissive -std=c++11
else
    CFLAGS=-c -fPIC -fpermissive -O3 -std=c++11
endif

LIBPATH=../../../../libs/x64
INCLUDEPATH=../../../../includes
INCLUDES=-I/usr/include -I$(INCLUDEPATH)
LDFLAGS=$(LIBPATH)/libstrategystudio_analytics.a $(LIBPATH)/libstrategystudio.a $(LIBPATH)/libstrategystudio_transport.a $(LIBPATH)/libstrategystudio_marketmodels.a $(LIBPATH)/libstrategystudio_utilities.a $(LIBPATH)/libstrategystudio_flashprotocol.a

INSTANCE_NAME=DQNStrategy# single word, no special characters
STRATEGY_NAME=DQNStrategy# should be your cpp file name, single word, no special characters
START_DATE=2023-11-30# start of the earliest date
END_DATE=2023-11-30 # end of the latest date
SYMBOLS=XNAS.ITCH-AAPL
PARAMETERS=name=DQNStrategy1|working=working
ACCOUNTSIZE=1000000
EPISODE_DATE=2023-11-30
EPISODE_PARAMETERS=name=DQNStrategy2|working=workingverywell

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

git_pull:
	chmod +x ./provision_scripts/git_pull.sh
	./provision_scripts/git_pull.sh

make_executable:
	chmod +x ./provision_scripts/*.sh
	chmod +x ./provision_scripts/*.py
#	ls -l ./provision_scripts/

delete_instance: make_executable
	pypy3 ./provision_scripts/delete_instance.py "$(INSTANCE_NAME)" "$(STRATEGY_NAME)"

clean_dlls:
	mkdir -p /home/vagrant/ss/bt/strategies_dlls
	rm -rf /home/vagrant/ss/bt/strategies_dlls/*

move_strategy_dll: delete_instance clean_dlls all
	cp $(LIBRARY) /home/vagrant/ss/bt/strategies_dlls/.

start_server: move_strategy_dll 
	./provision_scripts/start_server.sh

create_instance: start_server
	./provision_scripts/create_instance.sh "$(INSTANCE_NAME)" "$(STRATEGY_NAME)" "$(SYMBOLS)" "$(PARAMETERS)" "$(ACCOUNTSIZE)"

run_backtest: create_instance
	./provision_scripts/run_backtest.sh "$(INSTANCE_NAME)" "$(START_DATE)" "$(END_DATE)"

edit_params:
	./provision_scripts/edit_parameters.sh "$(INSTANCE_NAME)" "$(STRATEGY_NAME)" "$(EPISODE_PARAMETERS)"

edit_and_run_backtest: edit_params
	./provision_scripts/run_backtest.sh "$(INSTANCE_NAME)" "$(EPISODE_DATE)" "$(EPISODE_DATE)"


