# Project Report: Development and Implementation of a DQN Market Making Agent Using Strategy Studio for Backtesting

This project report details the design, implementation, and backtesting of a Deep Q-Network (DQN) Market Making Agent, conducted to explore innovative approaches to algorithmic trading within the proprietary trading firm. The agent is designed to operate in financial markets, aiming to earn profits from bid-ask spreads while managing inventory levels and mitigating risks. Strategy Studio was employed as the primary software for backtesting the agent's performance in simulated market environments. This project encapsulates a multi-disciplinary approach, integrating deep learning, reinforcement learning (RL), and quantitative finance methodologies.

## Introduction

Market making involves providing liquidity to the market by simultaneously offering to buy and sell a financial instrument, thereby making a market. A successful market maker profits from the spread between the buying and selling prices while managing the risks associated with holding inventory. The advent of deep reinforcement learning (DRL) and its application in quantitative finance has opened new avenues for developing sophisticated market-making strategies that can learn and adapt to market dynamics.

### Project Objective

The primary objective of this project was to design and implement a DQN Market Making Agent capable of learning optimal trading strategies in various market conditions. The DQN would be built and trained by simulating the environment with RCM-Xs Strategy Studio. The model would later be evaluated on the same.

## Methodology

### DQN Market Making Agent Design

#### 1. Environment

The Market environment was simulated using RCMXs Strategy-Studio. The State variables and stage rewards are written into a file which is used as a memory buffer for storing experiences. The Strategy is run for an entire day after which the DQN is trained for < n > number of iterations based on the new experiences.  

#### 2. State Representation

The state space included features crucial for decision-making, such as the current bid-ask spread, order book imbalance, historical price movements, and the agent's inventory level. Efforts were made to optimize the representation for efficiency and relevance.
State Features :- 

* Bid Ask Spread :-
  - Z score normalised value of the bid and ask spread.
  - This helps the model learn from the tightening or widening of spreads.

* Orderbook Imbalance :-
  - Order book imbalance measures the relative size difference between buy and sell orders in the order book.
  - Order Book Imbalance = (Volume of Buy Orders - Volume of Sell Orders) / (Volume of Buy Orders + Volume of Sell Orders)

* Volatility of Mid Price :-
  - n period volatility of the stock price that is z score normalised.
  - this helps the model learn from changes in volatility of the stock price.

* Buy Order Intensity :-
  - number of incoming buy orders in the past interval.

* Sell Order Intensity :-
  - number of incoming sell orders in the past interval.
  
#### 3. Action Space

A Market Maker places limit orders on either side of the orderbook.
- Order Location/price:
  - place bid(ask) relative to best bid or relative to best ask(bid).
  - action space size :-
    - relative to best bid:-
      - < to be filled >
    - relative to best ask :- 0 to n where n represents number of pips from the best ask with 0 being at the best ask.
- Order Size :
  - Order Sizes can range from 0 till the maximum limit set. Ratio of bid and ask sizes can also be varied.
  - action space size :-
    

#### 4. Reward Function

The reward function was tailored to incentivize profitable trades and effective inventory management, incorporating metrics such as profit and loss (P&L), inventory costs, and market impact considerations.

#### 5. Neural Network Architecture

The DQN architecture comprised an input layer matching the state space, multiple hidden layers for feature extraction, and an output layer representing the Q-values for each action. The design aimed for a balance between complexity and learning capability.

### Backtesting with Strategy Studio

Strategy Studio provided a comprehensive environment for backtesting the DQN Market Making Agent. The software's extensive historical data, customizable market conditions, and detailed performance analytics were instrumental in evaluating the agent's strategy.

## Results

The backtesting phase involved numerous simulations under various market conditions to assess the agent's performance, adaptability, and risk management. The DQN Market Making Agent demonstrated promising results, achieving profitable outcomes across different scenarios while effectively managing inventory levels. Strategy Studio's analytics revealed insights into the agent's decision-making process, highlighting areas of strength and potential improvement.

## Discussion

### Key Findings

- **Adaptability**: The agent showed a high degree of adaptability to changing market conditions, a testament to the robustness of the DQN framework.
- **Risk Management**: Effective inventory management and risk mitigation strategies were crucial in maximizing profitability and minimizing losses.
- **Performance Optimization**: Continuous refinement of state representation, action space, and reward function was essential for improving performance.

### Challenges

- **Market Dynamics**: Simulating complex market dynamics and their impact on the agent's learning process posed significant challenges.
- **Computational Complexity**: Managing the computational demands of training the DQN model, especially with a high-dimensional state space, required careful resource allocation.

## Conclusion

The development and implementation of the DQN Market Making Agent represent a significant step forward in applying deep reinforcement learning to algorithmic trading. The successful backtesting in Strategy Studio underscores the potential of DRL-based strategies in market making. Future work will focus on further refining the agent's model, exploring advanced DRL techniques, and deploying the agent in live trading environments to validate its real-world efficacy.

## Acknowledgements

This project was made possible through the collaborative efforts of the trading team, the support of the proprietary trading firm, and the use of advanced tools like Strategy Studio. Special thanks are extended to all team members and stakeholders who contributed their expertise and insights.
