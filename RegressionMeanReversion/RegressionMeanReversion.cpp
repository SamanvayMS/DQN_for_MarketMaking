// Refer to the header files for the explanation of the functions in detail
// In VSCode, hovering your mouse above the function renders the explanation of from the .h file as a pop up
#ifdef _WIN32
    #include "stdafx.h"
#endif

#include "RegressionMeanReversion.h"

using namespace RCM::StrategyStudio;
using namespace RCM::StrategyStudio::MarketModels;
using namespace RCM::StrategyStudio::Utilities;

using namespace std;

// Constructor to initialize member variables of the class to their initial values.
RegressionMeanReversion::RegressionMeanReversion(StrategyID strategyID,
                    const string& strategyName,
                    const string& groupName):
    Strategy(strategyID, strategyName, groupName),
    reg_map_(),
    absolute_stop_(0.2),
    strategy_active_(true),
    debug_(true),
    max_inventory_(100),
    window_size_(30),
    previous_prediction_(0),
    inventory_liquidation_increment_(10),
    inventory_liquidation_interval_(10),
    bar_interval_(1){
    }
// Destructor for class
RegressionMeanReversion::~RegressionMeanReversion(){
}

void RegressionMeanReversion::DefineStrategyParams(){
    params().CreateParam(CreateStrategyParamArgs("debug", STRATEGY_PARAM_TYPE_STARTUP, VALUE_TYPE_BOOL, debug_));
    params().CreateParam(CreateStrategyParamArgs("max_inventory", STRATEGY_PARAM_TYPE_STARTUP, VALUE_TYPE_INT, max_inventory_));
    params().CreateParam(CreateStrategyParamArgs("window_size", STRATEGY_PARAM_TYPE_STARTUP, VALUE_TYPE_INT, window_size_));
    params().CreateParam(CreateStrategyParamArgs("absolute_stop", STRATEGY_PARAM_TYPE_STARTUP, VALUE_TYPE_DOUBLE, absolute_stop_));
    params().CreateParam(CreateStrategyParamArgs("inventory_liquidation_increment", STRATEGY_PARAM_TYPE_STARTUP, VALUE_TYPE_INT, inventory_liquidation_increment_));
    params().CreateParam(CreateStrategyParamArgs("inventory_liquidation_interval", STRATEGY_PARAM_TYPE_STARTUP, VALUE_TYPE_INT, inventory_liquidation_interval_));
    params().CreateParam(CreateStrategyParamArgs("bar_interval", STRATEGY_PARAM_TYPE_STARTUP, VALUE_TYPE_INT, bar_interval_));
    params().CreateParam(CreateStrategyParamArgs("strategy_active", STRATEGY_PARAM_TYPE_STARTUP, VALUE_TYPE_BOOL, strategy_active_));
    params().CreateParam(CreateStrategyParamArgs("previous_prediction", STRATEGY_PARAM_TYPE_STARTUP, VALUE_TYPE_DOUBLE, previous_prediction_));
}

void RegressionMeanReversion::DefineStrategyCommands(){
}

// By default, SS will register to trades/quotes/depth data for the instruments you have requested via command_line.
void RegressionMeanReversion::RegisterForStrategyEvents(StrategyEventRegister* eventRegister, DateType currDate)
{   
    SetInventoryParams();
    int bar_interval;
    int inventory_liquidation_interval;
    int inventory_liquidation_increment;

    if (!(params().GetParam("bar_interval")->Get(&bar_interval) and params().GetParam("inventory_liquidation_interval")->Get(&inventory_liquidation_interval) and params().GetParam("inventory_liquidation_increment")->Get(&inventory_liquidation_increment))){
        cout << "Error in getting parameters" << endl;
        return;
    }

    for (SymbolSetConstIter it = symbols_begin(); it != symbols_end(); ++it) {
        eventRegister->RegisterForBars(*it, BAR_TYPE_TIME, bar_interval);
    }
    eventRegister->RegisterForRecurringScheduledEvents("liquidation_time",USEquityCloseUTCTime(currDate)-boost::posix_time::minutes((inventory_liquidation_increment+1)*inventory_liquidation_interval),USEquityCloseUTCTime(currDate)-boost::posix_time::minutes(inventory_liquidation_interval),boost::posix_time::minutes(inventory_liquidation_interval));
    eventRegister->RegisterForSingleScheduledEvent("terminate strategy",USEquityCloseUTCTime(currDate)-boost::posix_time::minutes(inventory_liquidation_interval));
}

void RegressionMeanReversion::OnTrade(const TradeDataEventMsg& msg) {
    
    const Instrument* instrument = &msg.instrument();
    RecordAccountStats(instrument);
}

void RegressionMeanReversion::OnScheduledEvent(const ScheduledEventMsg& msg) {
    if (msg.name() == "liquidation_time"){
        InventoryLiquidation();
    }
    if (msg.name() == "terminate strategy"){
        TerminateStrategy();
    }
}

void RegressionMeanReversion::OnOrderUpdate(const OrderUpdateEventMsg& msg) {
}

void RegressionMeanReversion::OnBar(const BarEventMsg& msg){ 

    bool strategy_active;
    int window_size;
    double previous_prediction;
    if (!(params().GetParam("strategy_active")->Get(&strategy_active) and params().GetParam("window_size")->Get(&window_size) and params().GetParam("previous_prediction")->Get(&previous_prediction))){
        cout << "Error in getting parameters" << endl;
        return;
    }

    AbsoluteStopCheck(&msg.instrument());
    RegMapIterator reg_iter = reg_map_.find(&msg.instrument());
    if (reg_iter == reg_map_.end()) {
        reg_iter = reg_map_.insert(make_pair(&msg.instrument(), Regression(window_size))).first;
    }

    double price = CalculateMidPrice(&msg.instrument());
    RegressionResult reg_pair = reg_iter->second.Update(price);
    double slope = reg_pair.slope;
    double prediction = reg_pair.prediction;

    if (reg_iter->second.FullyInitialized() and strategy_active) {
        if (debug_)
            cout << "predicted value is " << prediction << "while current bid is " << msg.instrument().top_quote().bid() << "and current ask is " << msg.instrument().top_quote().ask() << endl;
        if (previous_prediction > msg.instrument().top_quote().ask() and slope > 0 ) {
            SendOrder(&msg.instrument(), 1);
        } else if (previous_prediction < msg.instrument().top_quote().bid() and slope < 0 ){
            SendOrder(&msg.instrument(), -1);
        } else {
            if (debug_)
                cout << "No trade" << endl;
        }
        params().GetParam("previous_prediction")->SetValue(prediction);
    }
}

void RegressionMeanReversion::OnQuote(const QuoteEventMsg& msg){
}

void RegressionMeanReversion::InventoryLiquidation(){
    int inventory_liquidation_increment;
    int max_inventory;
    if (!(params().GetParam("inventory_liquidation_increment")->Get(&inventory_liquidation_increment)) and params().GetParam("max_inventory")->Get(&max_inventory)){
        cout << "Error in getting parameters" << endl;
        return;
    }

    max_inventory -= inventory_liquidation_increment;
    if (max_inventory < 0)
        max_inventory = 0;

    if (debug_){
        cout << "liquidating inventory by " << inventory_liquidation_increment << endl;
        cout << "max inventory is now " << max_inventory << endl;
    }
}

void RegressionMeanReversion::SetInventoryParams(){
    int inventory_liquidation_increment;
    int max_inventory;
    if (!(params().GetParam("inventory_liquidation_increment")->Get(&inventory_liquidation_increment)) and params().GetParam("max_inventory")->Get(&max_inventory)){
        cout << "Error in getting parameters" << endl;
        return;
    }

    inventory_liquidation_increment = int(max_inventory/inventory_liquidation_increment)+1;
    params().GetParam("inventory_liquidation_increment")->SetValue(inventory_liquidation_increment);
    if (debug_)
        cout << "liquidation increment :- " << inventory_liquidation_increment << endl;
}

double RegressionMeanReversion::CalculateMidPrice(const Instrument* instrument) {
    double top_bid = instrument->top_quote().bid();
    double top_ask = instrument->top_quote().ask();
    double mid_price = (top_bid + top_ask)/2;
    return mid_price;
}

void RegressionMeanReversion::RecordAccountStats(const Instrument* instrument){
    if (debug_){
        cout << "Total PNL " << portfolio().total_pnl(instrument) << endl;
        cout << "Unrealised PNL " << portfolio().unrealized_pnl(instrument) << endl;
        cout << "Realised PNL " << portfolio().realized_pnl(instrument) << endl;
    }
}

void RegressionMeanReversion::AdjustPortfolio() {
}

int RegressionMeanReversion::MaxPossibleLots(const Instrument* instrument,int side){
    int current_position = portfolio().position(instrument);
    int max_order_size = 0;
    int max_inventory;
    if (!params().GetParam("max_inventory")->Get(&max_inventory)){
        cout << "Error in getting parameters" << endl;
        return 0;
    }
    if (side == 1) {
        max_order_size = max_inventory - current_position;
    } else {
        max_order_size = max_inventory + current_position;
    }
    if (debug_){
        cout << "max position:- " << max_inventory << endl;
        cout << "position :- " << current_position << endl;
        cout << "max order size :- " << max_order_size << endl;
    }
    return max_order_size;
}

void RegressionMeanReversion::SendOrder(const Instrument* instrument, int side){
    if (!instrument->top_quote().ask_side().IsValid() || !instrument->top_quote().ask_side().IsValid()) {
        std::stringstream ss;
        ss << "Skipping trade due to lack of two sided quote"; 
        logger().LogToClient(LOGLEVEL_DEBUG, ss.str());
        return;
     }

    double price = (side == 1) ? instrument->top_quote().ask() : instrument->top_quote().bid();
    int trade_size  = (side == 1) ? instrument->top_quote().ask_size() : instrument->top_quote().bid_size();
    int upper_limit = MaxPossibleLots(instrument,side);
    if (upper_limit < trade_size)
        trade_size = upper_limit;

    OrderParams params(*instrument,
                       trade_size,
                       price,
                       MARKET_CENTER_ID_NASDAQ,
                       (side == 1) ? ORDER_SIDE_BUY : ORDER_SIDE_SELL_SHORT,
                       ORDER_TIF_DAY,
                       ORDER_TYPE_MARKET);
    if (trade_size == 0)
        return;
    if (debug_){
    // Print a message indicating that a new order is being sent
    std::cout << "SendTradeOrder(): about to send new order for size "
            << trade_size
            << " at $"
            << price
            << " for symbol "
            << instrument->symbol()
            << std::endl;
    }
    trade_actions()->SendNewOrder(params);
}

void RegressionMeanReversion::OnMarketState(const MarketStateEventMsg& msg){
    cout << msg.name() << endl;
}

void RegressionMeanReversion::TerminateStrategy() {
    for (InstrumentSetConstIter it = instrument_begin(); it != instrument_end(); ++it) {
        const Instrument* instrument = it->second;
        LiquidationOrder(instrument);
    }
    params().GetParam("strategy_active")->SetValue(false);
}

void RegressionMeanReversion::LiquidationOrder(const Instrument* instrument){
    int inventory = portfolio().position(instrument);
    double price = (inventory > 0) ? instrument->top_quote().bid() - 10 : instrument->top_quote().ask() + 10;
    OrderSide action = (inventory > 0) ? ORDER_SIDE_SELL : ORDER_SIDE_BUY;

    OrderParams params(*instrument,
                       abs(inventory),
                       price,
                       MARKET_CENTER_ID_NASDAQ,
                       action,
                       ORDER_TIF_DAY,
                       ORDER_TYPE_LIMIT);

    if (debug_){
    // Print a message indicating that a new order is being sent
    std::cout << "Closing ourt all positions with order for size "
            << inventory
            << " at $"
            << price
            << " for symbol "
            << instrument->symbol()
            << std::endl;
    }
    trade_actions()->SendNewOrder(params);
}

void RegressionMeanReversion::OnResetStrategyState() {
    reg_map_.clear();
}

void RegressionMeanReversion::OnParamChanged(StrategyParam& param) {
    if (param.param_name() == "strategy_active" && param.Equals(false)){
        TerminateStrategy();
    }
}

void RegressionMeanReversion::AbsoluteStopCheck(const Instrument* instrument){
    double pnl = portfolio().total_pnl(instrument)/portfolio().initial_cash();
    double absolute_stop;
    if (!params().GetParam("absolute_stop")->Get(&absolute_stop)){
        cout << "Error in getting parameters" << endl;
        return;
    }
    if (pnl < -absolute_stop){
        LiquidationOrder(instrument);
        trade_actions()->SendCancelAll();
        params().GetParam("strategy_active")->SetValue(false);
    }
}