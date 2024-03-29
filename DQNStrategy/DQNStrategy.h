// This is a preprocessor directive that ensures that the header file is included only once in a given compilation unit, to avoid multiple definitions.
#pragma once

// These are include guards that prevent redefinition of class names, macro constants, and typedef names. 
// Include guards help avoiding name conflicts in large software projects.
#ifndef DQNSTRATEGY_H
#define DQNSTRATEGY_H

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

// Class declaration
class DQNStrategy : public Strategy {

public:
    // Constructor & Destructor functions for this class
    DQNStrategy(StrategyID strategyID,
        const std::string& strategyName,
        const std::string& groupName);
    ~DQNStrategy();

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
    
private:
    // Used to store the state and data of the strategy.
    string name;
    string working;
};

// extern "C" is used to tell the compiler that these functions have C-style linkage instead of C++-style linkage, which means the function names will not be mangled.
// Except the strategy name, you don't need to change anything in this section.
extern "C" {

    _STRATEGY_EXPORTS const char* GetType() {
        return "DQNStrategy";
    }

    _STRATEGY_EXPORTS IStrategy* CreateStrategy(const char* strategyType,
                                   unsigned strategyID,
                                   const char* strategyName,
                                   const char* groupName) {
        if (strcmp(strategyType, GetType()) == 0) {
            return *(new DQNStrategy(strategyID, strategyName, groupName));
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