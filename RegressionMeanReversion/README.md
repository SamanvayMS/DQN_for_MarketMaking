# Strategy Overview: Volume Weighted Bid-Ask with Simple Mid Price Execution

## Description
This strategy operates on an n-level order book and focuses on the relationship between the volume-weighted bid-ask spread and the simple mid-price. The core logic triggers every second when a new bar is formed.

## Key Components
1. **Simple Mid Price (SMP):** Calculated as the average of the top bid and ask prices.
2. **Volume Weighted Bid-Ask (VWBA):** Considers the volume at each level of the order book up to 'n' levels to determine a more nuanced bid-ask spread.

## Execution Logic
- **If VWBA < SMP:** Execute a buy order at the top level bid price.
- **If VWBA > SMP:** Execute a sell order at the top level ask price.

## Inventory Close Logic 


