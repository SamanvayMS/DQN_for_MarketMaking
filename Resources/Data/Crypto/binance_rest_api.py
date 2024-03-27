import requests
import pandas as pd
import time
from datetime import datetime

def get_order_book(symbol, limit=1000):
    """
    Fetch the historical order book data for a given symbol from Binance US.
    :param symbol: Trading pair symbol, e.g., 'BTCUSD'.
    :param limit: Number of order book entries to retrieve, max 1000.
    :return: Historical order book data as a DataFrame.
    """
    url = f"https://api.binance.us/api/v3/depth"
    params = {'symbol': symbol, 'limit': limit}
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)
        df['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        return df
    else:
        return pd.DataFrame(columns=['timestamp'])

def continuously_fetch_data(symbol, interval_seconds=10, csv_file="order_book_data.csv"):
    """
    Continuously fetch order book data for a given symbol and append it to a CSV file.
    :param symbol: Trading pair symbol.
    :param interval_seconds: Interval in seconds between data fetches.
    :param csv_file: Name of the CSV file to store the data.
    """
    while True:
        data = get_order_book(symbol)
        print(data)
        #data.to_csv(csv_file, mode='a', header=not pd.read_csv(csv_file).size, index=False)
        #time.sleep(interval_seconds)

# Example usage: Continuously fetch data for BTCUSD and store it in 'btc_usd_order_book.csv'
continuously_fetch_data('BTCUSDT', interval_seconds=10, csv_file="btc_usd_order_book.csv")
