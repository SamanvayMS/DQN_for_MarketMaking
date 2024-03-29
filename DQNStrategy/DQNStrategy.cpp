// Refer to the header files for the explanation of the functions in detail
// In VSCode, hovering your mouse above the function renders the explanation of from the .h file as a pop up
#ifdef _WIN32
    #include "stdafx.h"
#endif

#include "DQNStrategy.h"

using namespace RCM::StrategyStudio;
using namespace RCM::StrategyStudio::MarketModels;
using namespace RCM::StrategyStudio::Utilities;

using namespace std;

// Constructor to initialize member variables of the class to their initial values.
DQNStrategy::DQNStrategy(StrategyID strategyID,
                    const string& strategyName,
                    const string& groupName):
    Strategy(strategyID, strategyName, groupName),
    name("DQNStrategy"),
    working("working"){
    }
// Destructor for class
DQNStrategy::~DQNStrategy(){}

void DQNStrategy::DefineStrategyParams(){
    params().CreateParam(CreateStrategyParamArgs("name", STRATEGY_PARAM_TYPE_STARTUP, VALUE_TYPE_STRING, name));
    params().CreateParam(CreateStrategyParamArgs("working", STRATEGY_PARAM_TYPE_STARTUP, VALUE_TYPE_STRING, working));
}

void DQNStrategy::DefineStrategyCommands(){}

// By default, SS will register to trades/quotes/depth data for the instruments you have requested via command_line.
void DQNStrategy::RegisterForStrategyEvents(StrategyEventRegister* eventRegister, DateType currDate){
    for (SymbolSetConstIter it = symbols_begin(); it != symbols_end(); ++it) {
        eventRegister->RegisterForBars(*it, BAR_TYPE_TIME, 10);
        }
}
void DQNStrategy::OnTrade(const TradeDataEventMsg& msg) {}

void DQNStrategy::OnScheduledEvent(const ScheduledEventMsg& msg) {}

void DQNStrategy::OnOrderUpdate(const OrderUpdateEventMsg& msg) {}

void DQNStrategy::OnBar(const BarEventMsg& msg){
    cout << "Bar event" << endl;
    cout << msg. << endl;
    cout << working << endl;
}

void DQNStrategy::OnQuote(const QuoteEventMsg& msg){}

void DQNStrategy::OnMarketState(const MarketStateEventMsg& msg){}

void DQNStrategy::OnResetStrategyState(){}

void DQNStrategy::OnParamChanged(StrategyParam& param) {
    cout << param.param_name() << " has changed to " << param.ToString() << endl;
}