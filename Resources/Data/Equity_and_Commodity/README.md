# Equity Data Procurement, Analysis and Parsing

## Overview

This subdirectory focusses on the procurement, analysis, and parsing of equity data. It contains a set of Jupyter notebooks and a Python script, each tailored for specific tasks within the domain of financial data analysis. 

## Overview of the Data 
### Contents
- `ts_recv`  
  The capture-server-received timestamp expressed as the number of nanoseconds since the UNIX epoch.

- `ts_event`  
  The matching-engine-received timestamp expressed as the number of nanoseconds since the UNIX epoch.

- `rtype`  
  The record type. Each schema corresponds with a single rtype value.

- `publisher_id`  
  The publisher ID assigned by Databento, which denotes dataset and venue.

- `instrument_id`  
  The numeric instrument ID.

- `action`  
  The event action. Can be [A]dd, [C]ancel, [M]odify, clea[R] book, [T]rade, or [F]ill.

- `side`  
  The order side. Can be [A]sk, [B]id or [N]one.

- `price`  
  The order price expressed as a signed integer where every 1 unit corresponds to 1e-9, i.e. 1/1,000,000,000 or 0.000000001.

- `size`  
  The order quantity.

- `channel_id`  
  The channel ID assigned by Databento as an incrementing integer starting at zero.

- `order_id`  
  The order ID assigned at the venue.

- `flags`  
  A combination of packet end with matching engine status.

- `ts_in_delta`  
  The matching-engine-sending timestamp expressed as the number of nanoseconds before ts_recv.

- `sequence`  
  The message sequence number assigned at the venue.

- `symbol`  
  The requested symbol for the instrument.

### Key Considerations 
- Every trade action has a corresponding fill and cancel message with the side on the trade message corresponding to the incoming order and the side on the fill message corresponding to the order that was taken out. An exception to this is when the trade has a [N]one type and this corresponds to other trades not visble on the orderbook like hidden orders.
## Data Parsing
We Parsed the Data into two specific formats message formats compatible with Strategy Studio. 

### Notebooks

1. **Databento API Usage (`databento.ipynb`)**
   - Purpose: Demonstrates the usage of the Databento API for data retrieval and analysis in a finance context.
   - Usage: Execute the notebook to see examples of Databento API calls and data manipulation. Adjust API queries to fetch different datasets.

2. **Date Choice Analysis (`date_choice.ipynb`)**
   - Purpose: Focuses on selecting and analyzing financial data to select the specific dates to test our strategy on, using daily candlestick data from Yahoo Finance.
   - Usage: Use this notebook to examine the methodology followed to select our date ranges for the strategy, also contains miscellaneous code that helps generate the current, front month and n month contract codes given a particular date for CL(Crude Oil Futures) traded on CME.

3. **Equity Notebook (`Equity_notebook.ipynb`)**
   - Purpose: Specializes in the analysis of equity data using the Databento parser.
   - Usage: Analyze various equity datasets by running the notebook. Can be customized for different equities or analysis techniques.

4. **Commodity Notebook (`Commodity_notebook.ipynb`)**
   - Purpose: Analyzes commodity-related data, integrating with the Databento parser for data retrieval.
   - Usage: Open in Jupyter and run cells to process commodity data. Modify parameters or functions as needed for specific commodity analysis.
### Python Script

- **Databento Parser (`databento_parser.py`)**
  - Purpose: A Python class for parsing and handling data using the Databento API. It facilitates data retrieval and manipulation in pandas DataFrames.
  - Usage: Import this script into your Python projects to leverage Databento API's capabilities. Use its methods to set up data retrieval parameters and process the data as needed.

## Installation

Ensure you have Python 3.6 installed, as Databento is compatible with this version. Additionally, install these dependencies:

- Jupyter Notebook or Jupyter Lab
- Pandas
- Numpy
- Databento API package
- `yfinance` for Yahoo Finance data
- `dotenv` for managing environment variables

