__author__ = 'Samanvay Malapally Sudhakara'

import sys
import csv
import gzip
import os
import re
from datetime import datetime, timezone, timedelta

def unix_to_utc(unix_time):
    utc_time = datetime.fromtimestamp(float(unix_time), timezone.utc)
    return utc_time.strftime('%Y-%m-%d %H:%M:%S.%f')
'''
STRATEGY STUDIO FORMAT

Trades
Line Format:
COLLECTION_TIME,SOURCE_TIME,SEQ_NUM,TICK_TYPE,MARKET_CENTER,PRICE,SIZE[,FEED_TYPE,[SIDE[,TRADE_CON D_TYPE,TRADE_COND]]]

Depth Update By Price (OrderBook data)
Line Format:
COLLECTION_TIME,SOURCE_TIME,SEQ_NUM,TICK_TYPE,MARKET_CENTER,SIDE,PRICE,SIZE[,NUM_ORDERS[,IS_IMPLIED[,REASON[,IS_PARTIAL]]]]

Depth Update By Order (OrderBook data)
Line Format:
COLLECTION_TIME,SOURCE_TIME,SEQ_NUM,TICK_TYPE,MARKET_CENTER,SIDE,ORDER_ID,PRICE,SIZE[,MMID[,REASON[,OLD_ ORDER_ID[,OLD_ORDER_PRICE[,PRIORITY_INDICATOR[,IS_PARTIAL]]]]]]
'''


class Crypto_Parser():
    def __init__(self, filepath, currency_pair):
        self.file_path = filepath
        self.currency_pair = currency_pair
        self.dates = set()
        
    def parse_date(self,date_str):
        return datetime.strptime(date_str, "%Y%m%d")
    
    def format_date(self,date):
        return datetime.strftime(date, "%Y%m%d")
    
    def find_date_ranges(self,dates):
        sorted_dates = sorted(map(self.parse_date, dates))
        ranges = []
        start = end = sorted_dates[0]

        for date in sorted_dates[1:]:
            if date == end + timedelta(days=1):
                end = date
            else:
                ranges.append((start, end))
                start = end = date
        ranges.append((start, end))

        return [("From " + self.format_date(start) + " to " + self.format_date(end)) if start != end else self.format_date(start) for start, end in ranges]

    def extract_dates_from_filenames(self):
        pattern = re.compile(r"BTC_USDT-orderbooks-(\d{8})\d{2}\.csv\.gz")

        for filename in os.listdir(self.file_path):
            match = pattern.search(filename)
            if match:
                self.dates.add(match.group(1))
        self.dates = sorted(list(self.dates))
        date_ranges = self.find_date_ranges(self.dates)
        for range_str in date_ranges:
            print(f'data from {range_str} is present')
        
    def get_files_for_date(self,date):
        pattern = f"^{self.currency_pair}-orderbooks-{date}(\\d{{2}})\\.csv\\.gz$"
        files = [f for f in os.listdir(self.file_path) if re.match(pattern, f)]
        files.sort(key=lambda x: x[-6:-4])  # Sort by hour
        if len(files) == 0:
            raise Exception(f"No files found for date {date}")
        elif len(files) < 24:
            raise Exception(f"Only {len(files)} files found for date {date}")
        else:
            return files
    
    def process_row_(self,row,first_file = True):
        time = unix_to_utc(row[0]) # time converted to utc
        order_type = row[1] # order type helps decide whether to match or add to the orderbook
        price = float(row[2]) # price is the key
        side = 1 if float(row[3]) > 0 else 2 # 1 for buy and 2 for sell
        qty = abs(float(row[3])) # quantity is always positive
        sequential_id = row[4] # helps keep track of the order of the orders
        bunched = row[5] # No idea if we need this for the ss model
        
        if order_type == 'set' and first_file:
            # depth update by price 
            return f'{time},{time},{sequential_id},P,Binance,{side},{price},{qty}'
        elif order_type == 'make':
            # depth update by order
            return f'{time},{time},{sequential_id},,Binance,{side},{price},{qty}'
        elif order_type == 'take':
            # trade
            return f'{time},{time},{sequential_id},{order_type},Binance,{side},{price},{qty}'
    
    def parse_files(self,start_date = None,end_date = None):
        dates = self.dates if start_date == None and end_date == None else self.dates[self.dates.index(start_date):self.dates.index(end_date)+1]
        for date in dates:
            print(date)
            files = self.get_files_for_date(date)
            for file in files:
                with gzip.open(self.file_path+file, 'rt') as f:
                    reader = csv.reader(f)
                    for row in reader:
                        print(row)
                        break
                    break

if __name__ == "__main__":
    parser = Crypto_Parser("BTC_USDT/futures_usdt/", "BTC_USDT")
    parser.extract_dates_from_filenames()
    print('enter start and end date to run parser based on above ranges in same format as above')
    print('if you want to run for all dates press enter instead of entering dates')
    # add code to read dates from input
    date1 = input('start_date: ')
    date2 = input('end_date: ')
    if date1 == '' and date2 == '':
        parser.parse_files()
    else:
        parser.parse_files(date1,date2)

# **************************************************************************************************************************************************************************************
# tests

# chcek if processed rows are right 
def process_data(row):
    time = unix_to_utc(row[0])
    order_type = row[1]
    price = float(row[2])
    side = 'Bid' if float(row[3]) > 0 else 'Ask'
    quantity = abs(float(row[3]))
    order_id = row[4]
    merged_count = row[5]
    # Insert your data processing logic here
    # For now, we'll just return the row as is
    return f'{time},{time},{order_id},{order_type},Binance,{side},{price},{quantity}'

input_filename = 'BTC_USDT/futures_usdt/BTC_USDT-orderbooks-2022010100.csv.gz'
compressed_output_filename = input_filename.split('.')[0] + '_processed.csv.gz'

# Open the input gzip file for reading and the output gzip file for writing
with gzip.open(input_filename, 'rt') as gzfile_in: #, gzip.open(compressed_output_filename, 'wt', newline='') as gzfile_out:
    reader = csv.reader(gzfile_in)
    #writer = csv.writer(gzfile_out)
    for row in reader:
        print(row)
        processed_row = process_data(row)
        print(processed_row)
    