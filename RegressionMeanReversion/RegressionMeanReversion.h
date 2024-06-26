// This is a preprocessor directive that ensures that the header file is included only once in a given compilation unit, to avoid multiple definitions.
#pragma once

// These are include guards that prevent redefinition of class names, macro constants, and typedef names. 
// Include guards help avoiding name conflicts in large software projects.
#ifndef _STRATEGY_STUDIO_LIB_EXAMPLES_SIMPLE_MOMENTUM_STRATEGY_H_
#define _STRATEGY_STUDIO_LIB_EXAMPLES_SIMPLE_MOMENTUM_STRATEGY_H_

// This is a conditional preprocessor directive that defines a macro _STRATEGY_EXPORTS as __declspec(dllexport) on Windows platform, and empty on other platforms.
// This macro is used to export the HelloworldStrategy class to the dynamic link library (DLL) that is loaded by the trading engine.
#ifdef _WIN32
    #define _STRATEGY_EXPORTS __declspec(dllexport)
#else
    #ifndef _STRATEGY_EXPORTS
    #define _STRATEGY_EXPORTS
    #endif
#endif

/**
 * Below are header files that are used by the HelloworldStrategy class. We just tell the compiler to look for these files.
 * You will not have Strategy.h & Instrument.h in your directory. These are part of the SDK.
 * Strategy.h is the main header file for the strategy development kit and provides access to the core functionality of the trading engine.
 * Instrument.h is a header file for instrument specific data. 
 * The remaining headers provide various utility functions.
**/
#include <Strategy.h>
#include <MarketModels/Instrument.h>
#include <MarketModels/IAggrOrderBook.h>
#include <Analytics/ScalarRollingWindow.h>
#include <Analytics/InhomogeneousOperators.h>
#include <Analytics/IncrementalEstimation.h>
#include <Utilities/ParseConfig.h>
#include <IPositionRecord.h>
#include <Order.h>
#include <BarDataTypes.h>

#include <string>
#include <unordered_map>
#include <iostream>
#include <algorithm> 
#include <cmath>

// Import namespace RCM::StrategyStudio to avoid explicit namespace qualification when using names from this namespace
using namespace RCM::StrategyStudio;
using namespace RCM::StrategyStudio::Utilities;
using namespace std;

struct RegressionResult {
    double slope;
    double prediction;
};
class Regression {
public:
    explicit Regression(int window_size) : window(window_size) {}

    void Reset()
    {
        window.clear();
    }

    RegressionResult Update(double val)
    {
        window.push_back(val);
        return CalculatePredictedValue();
    }

    RegressionResult CalculatePredictedValue()
    {
        RegressionResult result;
        if (window.size() <= 1) {
            result.slope = 0; // or some other appropriate default value
            result.prediction = 0;
            return result;
        } // handle insufficient data

        double sum_x = 0;
        double sum_y = 0;
        double sum_xy = 0;
        double sum_xx = 0;
        int n = window.size();

        int i = 0;
        for (auto it = window.begin(); it != window.end(); ++it, ++i) {
            double value = *it;
            sum_x += i;
            sum_y += value;
            sum_xy += (i * value);
            sum_xx += (i * i);
        }

        double mean_x = sum_x / n;
        double mean_y = sum_y / n;

        double ss_xx = sum_xx - n * mean_x * mean_x;
        double ss_xy = sum_xy - n * mean_x * mean_y;

        double slope = ss_xy / ss_xx;
        double intercept = mean_y - slope * mean_x;

        result.slope = ss_xy / ss_xx;
        result.prediction = result.slope * (n+1) + intercept;

        return result;
    }

    bool FullyInitialized() const { return window.full(); }

private:
    Analytics::ScalarRollingWindow<double> window;
};


// Class declaration
class RegressionMeanReversion : public Strategy {

public:
    typedef boost::unordered_map<const Instrument*, Regression> RegMap;
    // creates an unordered map where keys are instrument names and values are corresponding classes 
    // all these pairs are set to a map called MomentumMap
    typedef RegMap::iterator RegMapIterator; 
    // we define an iterator that iterates through these key value pairs

    // Constructor & Destructor functions for this class
    RegressionMeanReversion(StrategyID strategyID,
        const std::string& strategyName,
        const std::string& groupName);
    ~RegressionMeanReversion();

public:

    // Below are event handling functions the user can override on the cpp file to create their own strategies.
    // Polymorphic behavior is achieved in C++ by using virtual functions, which allows the same function to behave differently depending on the type of object it is called on.

    /**
    * Called whenever a bar event occurs for an instrument that the strategy is subscribed to.
    * A bar event is a notification that a new bar has been formed in the price data of the instrument, where a bar represents a fixed period of time (e.g., 1 minute, 5 minutes, 1 hour) and contains information such as the opening and closing price, highest and lowest price, volume for that period.
    * The msg parameter of the OnBar function is an object of type BarEventMsg that contains information about the bar event that occurred.
    **/
    virtual void OnBar(const BarEventMsg& msg);

    /**
    * Called whenever a trade event occurs for an instrument that the strategy is subscribed to.
    * A trade event refers to a specific occurrence related to a trade of a financial instrument, such as a stock or a commodity like the execution of a buy or sell order
    * The msg parameter is an object of type TradeDataEventMsg that contains information about the trade event that occurred
    */
    virtual void OnTrade(const TradeDataEventMsg& msg);

    /**
     * This event triggers whenever a new quote for a market center arrives from a consolidate or direct quote feed,
     * or when the market center's best price from a depth of book feed changes.
     *
     * User can check if quote is from consolidated or direct, or derived from a depth feed. This will not fire if
     * the data source only provides quotes that affect the official NBBO, as this is not enough information to accurately
     * mantain the state of each market center's quote.
     */ 
    virtual void OnQuote(const QuoteEventMsg& msg);

    /**
     * This event triggers whenever a order book message arrives. This will be the first thing that
     * triggers if an order book entry impacts the exchange's DirectQuote or Strategy Studio's TopQuote calculation.
     */ 
    virtual void OnDepth(const MarketDepthEventMsg& msg){}

    /**
     * Called when a scheduled event occurs during the backtesting process.
     * Examples of actions include making trading decisions, adjusting parameters or indicators, updating strategy state, or triggering specific actions at predefined intervals and time-dependent trading strategies.
    */
    virtual void OnScheduledEvent(const ScheduledEventMsg& msg);

    // Called whenever there is an update to one of the orders placed by the strategy
    void OnOrderUpdate(const OrderUpdateEventMsg& msg);
 
    void OnResetStrategyState();

    void OnParamChanged(StrategyParam& param);


private:

    virtual void RegisterForStrategyEvents(StrategyEventRegister* eventRegister, DateType currDate);

    virtual void DefineStrategyParams();

    virtual void DefineStrategyCommands();

    void OnMarketState(const MarketStateEventMsg& msg);

    void SendOrder(const Instrument* instrument, int side);

    void InventoryLiquidation();

    void SetInventoryParams();

    double CalculateMidPrice(const Instrument* instrument);

    void RecordAccountStats(const Instrument* instrument);

    void AdjustPortfolio();

    int MaxPossibleLots(const Instrument* instrument,int side);

    void TerminateStrategy();

    void LiquidationOrder(const Instrument* instrument);

    void AbsoluteStopCheck(const Instrument* instrument);
    
private:
    // Used to store the state and data of the strategy.
    bool debug_; // a boolean variable that can be used to enable or disable debug mode.
    int max_inventory_; // max position value we can accumulate in any direction.
    int window_size_; // number of bars to use for regression
    double previous_prediction_; // previous predicted value
    int inventory_liquidation_increment_; // % decrease in inventory
    int inventory_liquidation_interval_; // time interval between inventory liquidation
    int bar_interval_; // bar interval
    boost::unordered_map<const Instrument*, Regression> reg_map_;
    bool strategy_active_;
    double absolute_stop_;

};

// extern "C" is used to tell the compiler that these functions have C-style linkage instead of C++-style linkage, which means the function names will not be mangled.
// Except the strategy name, you don't need to change anything in this section.
extern "C" {

    _STRATEGY_EXPORTS const char* GetType() {
        return "RegressionMeanReversion";
    }

    _STRATEGY_EXPORTS IStrategy* CreateStrategy(const char* strategyType,
                                   unsigned strategyID,
                                   const char* strategyName,
                                   const char* groupName) {
        if (strcmp(strategyType, GetType()) == 0) {
            return *(new RegressionMeanReversion(strategyID, strategyName, groupName));
        } else {
            return NULL;
        }
    }

    _STRATEGY_EXPORTS const char* GetAuthor() {
        return "dlariviere";
    }

    _STRATEGY_EXPORTS const char* GetAuthorGroup() {
        return "UIUC";
    }

    _STRATEGY_EXPORTS const char* GetReleaseVersion() {
        return Strategy::release_version();
    }
}

// The #endif statement marks the end of the include guard to prevent the header file from being included multiple times.
#endif
