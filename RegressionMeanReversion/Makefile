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

INSTANCE_NAME=RegressionMeanReversion# single word, no special characters
STRATEGY_NAME=RegressionMeanReversion# should be your cpp file name, single word, no special characters
START_DATE=2023-11-30# start of the earliest date
END_DATE=2023-11-30 # end of the latest date
SYMBOLS=XNAS.ITCH-AAPL
PARAMETERS=absolute_stop=0.2|strategy_active=true|debug_=false|max_inventory=100|window_size=30|previous_prediction=0|inventory_liquidation_increment=10|inventory_liquidation_interval=10|bar_interval=1
ACCOUNTSIZE=1000000
BACKTESTID=01

# Define the names of the library, source, and header files.
LIBRARY=RegressionMeanReversion.so
SOURCES=RegressionMeanReversion.cpp
HEADERS=RegressionMeanReversion.h
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
	ls -l ./provision_scripts/

delete_instance: make_executable
	pypy3 ./provision_scripts/delete_instance.py "$(INSTANCE_NAME)" "$(STRATEGY_NAME)"

clean_dlls:
	mkdir -p /home/vagrant/ss/bt/strategies_dlls
	rm -rf /home/vagrant/ss/bt/strategies_dlls/*

move_strategy_dll: delete_instance clean_dlls all
	cp $(LIBRARY) /home/vagrant/ss/bt/strategies_dlls/.

update_parameter_txt:
	pypy3 ./provision_scripts/update_parameters.py "$(PARAMETERS)"

build_strategy: move_strategy_dll update_parameter_txt
	./provision_scripts/build_strategy.sh "$(INSTANCE_NAME)" "$(STRATEGY_NAME)" "$(START_DATE)" "$(END_DATE)" "$(SYMBOLS)" "$(ACCOUNTSIZE)"

run_backtest: build_strategy
	chmod +x ./provision_scripts/run_backtest.sh
	./provision_scripts/run_backtest.sh "$(INSTANCE_NAME)" "$(START_DATE)" "$(END_DATE)" "$(SYMBOLS)" "$(PARAMETERS)" "$(ACCOUNTSIZE)" "$(BACKTESTID)"

get_results: 
	chmod +x ./provision_scripts/get_results.sh
	./provision_scripts/get_results.sh "$(INSTANCE_NAME)" "$(START_DATE)" "$(END_DATE)" "$(SYMBOLS)" "$(PARAMETERS)" "$(ACCOUNTSIZE)" "$(BACKTESTID)"
