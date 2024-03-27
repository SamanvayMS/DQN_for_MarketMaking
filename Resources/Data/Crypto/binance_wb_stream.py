import csv
import json
import time
import os
from binance.client import Client
from binance.streams import BinanceSocketManager

# Binance API credentials
api_key = os.getenv("Binance_api_key")
api_secret = os.getenv("Binance_api_secret")

# Initialize client
client = Client(api_key, api_secret)

# Name of the CSV file where data will be stored
csv_file = 'order_depth_data.csv'

# Function to handle incoming depth messages
def process_depth_message(msg):
    # Check if message is valid
    if msg['e'] == 'depthUpdate':
        # Extracting relevant data
        data = {
            'Event Time': msg['E'],
            'Symbol': msg['s'],
            'First Update ID': msg['U'],
            'Final Update ID': msg['u'],
            'Bids': msg['b'],
            'Asks': msg['a']
        }
        # Writing data to CSV
        with open(csv_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([data['Event Time'], data['Symbol'], data['First Update ID'], data['Final Update ID'], json.dumps(data['Bids']), json.dumps(data['Asks'])])

# Initialize WebSocket manager
bsm = BinanceSocketManager(client)

# Start the WebSocket
conn_key = bsm.start_depth_socket('BTCUSDT', process_message)

# Start the WebSocket manager
bsm.start()

# Run for 10 minutes
time.sleep(600)

# Stop the socket
bsm.stop_socket(conn_key)

# Stop the WebSocket manager
bsm.close()
