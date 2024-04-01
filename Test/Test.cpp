// Refer to the header files for the explanation of the functions in detail
// In VSCode, hovering your mouse above the function renders the explanation of from the .h file as a pop up
#ifdef _WIN32
    #include "stdafx.h"
#endif

#include "Test.h"

using namespace RCM::StrategyStudio;
using namespace RCM::StrategyStudio::MarketModels;
using namespace RCM::StrategyStudio::Utilities;

using namespace std;

// Constructor to initialize member variables of the class to their initial values.
Test::Test(StrategyID strategyID,
                    const string& strategyName,
                    const string& groupName):
    Strategy(strategyID, strategyName, groupName),
    name("wrong strategy name lolll"),
    working("not working"){
    }
// Destructor for class
Test::~Test(){}

void Test::DefineStrategyParams(){
    params().CreateParam(CreateStrategyParamArgs("name", STRATEGY_PARAM_TYPE_STARTUP, VALUE_TYPE_STRING, name));
    params().CreateParam(CreateStrategyParamArgs("working", STRATEGY_PARAM_TYPE_STARTUP, VALUE_TYPE_STRING, working));
}

void Test::DefineStrategyCommands(){}

// By default, SS will register to trades/quotes/depth data for the instruments you have requested via command_line.
void Test::RegisterForStrategyEvents(StrategyEventRegister* eventRegister, DateType currDate){
    for (SymbolSetConstIter it = symbols_begin(); it != symbols_end(); ++it) {
        eventRegister->RegisterForBars(*it, BAR_TYPE_TIME, 60);
        }
}

void Test::OnTrade(const TradeDataEventMsg& msg) {}

void Test::OnScheduledEvent(const ScheduledEventMsg& msg) {}

void Test::OnOrderUpdate(const OrderUpdateEventMsg& msg) {}

void Test::OnBar(const BarEventMsg& msg){
//    cout << params().GetParam("name")->ToString() << endl;
//    cout << params().GetParam("working")->ToString() << endl;
cout << "Tensor is :- " << state << endl;
}

void Test::OnQuote(const QuoteEventMsg& msg){}

void Test::OnMarketState(const MarketStateEventMsg& msg){}

void Test::OnResetStrategyState(){}

void Test::OnParamChanged(StrategyParam& param) {
    cout << param.param_name() << " has changed to " << param.ToString() << endl;
}