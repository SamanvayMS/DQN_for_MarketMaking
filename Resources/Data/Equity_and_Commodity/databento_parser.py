import databento as db
import os
from dotenv import load_dotenv
import pandas as pd
import datetime as dt
import numpy as np
import gzip
import csv
from tqdm import tqdm

class Databento_parser():
    """
    A class for parsing data using the Databento API.

    Attributes:
        client (db.Historical): The Databento Historical client.
        dataset (str): The selected dataset.
        schema (str): The selected schema.
        file_location (str): The file location for storing the parsed data.
        df (pd.DataFrame): The parsed data as a DataFrame.
        overwrite (bool): Flag indicating whether to overwrite existing files.
    """

    def __init__(self) -> None:
        self.client = None
        self.dataset = None
        self.schema = None
        self.file_location = None
        self.df = None
        self.previous_row_was_fill = False
        self.current_time = '0'
        self.verbose = True 
    
    def set_verbose(self, verbose):
        """
        Sets the verbose flag.

        Args:
            verbose (bool): Flag indicating whether to print verbose output.
        """
        self.verbose = verbose
        
    def set_api_key(self, api_key_name):
        """
        Sets the API key for accessing the Databento API.

        Args:
            api_key_name (str): The name of the API key in the environment variables.
        """
        load_dotenv()
        api_key = os.getenv(api_key_name)
        self.client = db.Historical(api_key)

    def select_dataset(self, dataset):
        """
        Selects the dataset to parse.

        Args:
            dataset (str): The name of the dataset.
        
        Raises:
            Exception: If the dataset is not found.
        """
        if dataset not in self.client.metadata.list_datasets():
            raise Exception('dataset not found')
        self.dataset = dataset
        
    def select_schema(self, schema):
        """
        Selects the schema for parsing.

        Args:
            schema (str): The name of the schema.
        
        Raises:
            Exception: If the schema is not found.
        """
        if schema not in self.client.metadata.list_schemas(self.dataset):
            raise Exception('schema not found')
        self.schema = schema
        
    def select_file_location(self, file_location):
        """
        Selects the file location for storing the parsed data.

        Args:
            file_location (str): The file location.
        
        Raises:
            Exception: If the file location is not found.
        """
        if os.path.exists(file_location):
            self.file_location = file_location
        else:
            raise Exception('file location not found')

    def __check_variables(self):
        """
        Checks if the required variables are set.

        Raises:
            Exception: If any of the required variables are not set.
        """
        if self.client is None:
            raise Exception('api key not set')
        if self.dataset is None:
            raise Exception('dataset not selected')
        if self.schema is None:
            raise Exception('schema not selected')
        if self.file_location is None:
            raise Exception('file location not selected')
        
    def __get_ranges(self, date):
        """
        Gets the start and end ranges for the specified date.

        Args:
            date (str): The date in 'YYYY-MM-DD' format.

        Returns:
            tuple: A tuple containing the start and end ranges in 'YYYY-MM-DDTHH:MM' format.
        """
        if self.dataset == 'XNAS.ITCH':
            start = dt.datetime.strptime(date, '%Y-%m-%d') + dt.timedelta(hours=1)
            end = start + dt.timedelta(days=1)
            start = start.strftime('%Y-%m-%dT%H:%M')
            end = end.strftime('%Y-%m-%dT%H:%M')
        elif self.dataset == 'GLBX.MDP3':
            start = dt.datetime.strptime(date, '%Y-%m-%d')
            end = start + dt.timedelta(days=1)
            start = start.strftime('%Y-%m-%dT%H:%M')
            end = end.strftime('%Y-%m-%dT%H:%M')
        else:
            print('dataset not found')
        return start, end
        
    def get_data(self, date, symbol, Proceed='', name = None):
        """
        Gets the data for the specified date and symbol.

        Args:
            date (str): The date in 'YYYY-MM-DD' format.
            symbol (str): The symbol to retrieve data for.
            Proceed (str, optional): Proceed flag. Defaults to ''.

        Raises:
            Exception: If any of the required variables are not set.
        """
        if self.verbose:
            print('checking variables')
        self.__check_variables()
        if self.verbose:
            print(f'accessing folder: {self.file_location} for files' )
        if os.path.exists(self.file_location):
            if self.verbose:
                print('folder exists')
        else:
            print('folder not found')
            return
        new_path = f'{self.file_location}/{symbol}'
        if os.path.exists(new_path):
            if self.verbose:
                print('symbol folder exists')
        else:
            os.makedirs(new_path, exist_ok=True)
            if self.verbose:
                print('created symbol folder')
        file_path = f'{new_path}/{self.dataset}_{symbol}_{self.schema}_{date}.csv.gz'
        start, end = self.__get_ranges(date)
        if self.verbose:
            print(f'checking if file exists at {file_path}')
        if os.path.exists(file_path):
            if self.verbose:
                print('Found existing file')
        else:
            if self.verbose:
                print('file not found, gathering data')
            cost = self.client.metadata.get_cost(
                dataset=self.dataset,
                symbols=[symbol],
                schema=self.schema,
                start=start,
                end=end,
            )
            print(f'cost: {cost}')
            if Proceed == '':
                Proceed = input('Proceed? (y/n)')
            if Proceed == 'n':
                print('exiting')
                return
            
            data = self.client.timeseries.get_range(
                dataset=self.dataset,
                symbols=[symbol],
                schema=self.schema,
                start=start,
                end=end,
            )
            self.df = data.to_df()
            self.df.reset_index(inplace=True)
            if len(self.df) == 0:
                print('no data found for this date')
                return
            
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            if self.verbose:
                print('created new file')

            self.df.to_csv(file_path, index=False, compression='gzip')
            if self.verbose:
                print('gathered and stored data at ', new_path)
             
    def __parse_data(self,row):
        if self.dataset == 'XNAS.ITCH':  
            MARKET_CENTER = 'NASDAQ'
            # Input format:
            # ts_recv,ts_event,rtype,publisher_id,instrument_id,action,side,price,size,channel_id,order_id,flags,ts_in_delta,sequence,symbol

            COLLECTION_TIME = pd.to_datetime(row[0],unit = 'ns').strftime('%Y-%m-%d %H:%M:%S.%f')
            SOURCE_TIME = (pd.to_datetime(row[0],unit = 'ns') - dt.timedelta(seconds = float(row[12])/10e9)).strftime('%Y-%m-%d %H:%M:%S.%f')
            
            PARTIAL = 1 if COLLECTION_TIME == self.current_time else 0
            if (self.verbose) and (PARTIAL == 1):
                print(f"multiple events in same time found at time:- {COLLECTION_TIME} ")
            self.current_time = COLLECTION_TIME
            
            if row[5] in ['A', 'C', 'M', 'F']:
                if self.previous_row_was_fill:
                    self.previous_row_was_fill = False
                    return None
                REASON = 2 if row[5] == 'A' else 4 if row[5] == 'C' else 5 if row[5] == 'F' else 7
                if row[5] == 'F':
                    self.previous_row_was_fill = True
                SEQ_NUM = row[13]
                TICK_TYPE = 'D'
                SIDE = 1 if row[6] == 'B' else 2
                ORDER_ID = row[10]
                PRICE = row[7]
                SIZE = 0 if row[5] in ['C','F'] else row[8]
            # Line Format for Depth by order update:
                return f'{COLLECTION_TIME},{SOURCE_TIME},{SEQ_NUM},{TICK_TYPE},{MARKET_CENTER},{SIDE},{ORDER_ID},{PRICE},{SIZE},,{REASON},,,,{PARTIAL}'
            elif row[5] == 'R':
                SEQ_NUM = row[13]
                TICK_TYPE = 'R'
                return f'{COLLECTION_TIME},{SOURCE_TIME},{SEQ_NUM},{TICK_TYPE},{MARKET_CENTER}'
            elif row[5] == 'T':
                SEQ_NUM = row[13]
                TICK_TYPE = 'T'
                SIDE = 1 if row[6] == 'B' else -1 if row[6] == 'A' else 0
                ORDER_ID = row[10]
                PRICE = row[7]
                SIZE = row[8]
            # Line Format for Trade update:
            # COLLECTION_TIME,SOURCE_TIME,SEQ_NUM,TICK_TYPE,MARKET_CENTER,PRICE,SIZE[,FEED_TYPE,[SIDE[,TRADE_CON D_TYPE,TRADE_COND]]]
                return f'{COLLECTION_TIME},{SOURCE_TIME},{SEQ_NUM},{TICK_TYPE},{MARKET_CENTER},{PRICE},{SIZE},,{SIDE}'
            else:
                raise Exception('No matching flag')
        elif self.dataset == 'GLBX.MDP3':
            return None
        else:
            raise Exception('No matching Dataset')

    def convert_to_SS(self,symbol,date,output_file_path):
        
        if self.verbose:
            print('checking variables')
        self.__check_variables()
        
        if self.verbose:
            print(f'accessing folder: {self.file_location} for files' )
        
        if os.path.exists(self.file_location):
            if self.verbose:
                print('input folder exists')
        else:
            print('input folder not found')
            return
        
        if os.path.exists(output_file_path):
            if self.verbose:
                print('output folder exists')
        else:
            print('output folder not found')
            return
            
        # new_path = f'{output_file_path}/{symbol}'
        # if os.path.exists(new_path):
        #     if self.verbose:
        #         print('output symbol folder exists')
        # else:
        #     os.makedirs(new_path, exist_ok=True)
        #     if self.verbose:
        #         print('created output symbol folder')
        
        date_file_format = dt.datetime.strptime(date, '%Y-%m-%d').strftime('%Y%m%d')
        #output_file_path = f'{new_path}/tick_{self.dataset}-{symbol}_{date_file_format}.txt.gz'
        output_file_path = f'{output_file_path}/tick_{self.dataset}-{symbol}_{date_file_format}.txt.gz'
        
        input_file_path = f'{self.file_location}/{symbol}/{self.dataset}_{symbol}_{self.schema}_{date}.csv.gz'
        if os.path.exists(input_file_path):
            if self.verbose:
                print('Found input file')
        else:
            print('input file not found')
            print('please run get_data first')
            return
        
        if self.verbose:
            print(f'checking if file exists at {output_file_path}')
            
        if os.path.exists(output_file_path):
            if self.verbose:
                print('Found existing file at ')
        else:
            with gzip.open(input_file_path, 'rt') as gzfile_in, gzip.open(output_file_path, 'wt', newline='') as gzfile_out:
                reader = csv.reader(gzfile_in)
                
                # Skip the first row (column names)
                next(reader, None) 
                for row in tqdm(reader, desc="Processing rows"):
                    new_row = self.__parse_data(row)
                    if new_row != None:
                        gzfile_out.write(new_row + '\n')
            if self.verbose:
                print('converted file')

def main():
    parser = Databento_parser()
    parser.set_api_key('Databento_api_key_1')
    parser.select_dataset('XNAS.ITCH')
    parser.select_schema('mbo')
    parser.select_file_location('/Volumes/Seagate/Equity')
    parser.set_verbose(True)
    #parser.get_data('2022-02-27','AAPL')
    #parser.convert_to_SS('AAPL','2022-02-07','/Volumes/Seagate/EquityProcessed')

if __name__ == '__main__':
    main()
    
    
    
    

