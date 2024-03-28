import pandas as pd
import numpy as np
import subprocess
import itertools
import random
import json
import time
import os
import sys

class StrategyOptimiser():
    def __init__(self,backtest_id):
        self.df = None
        self.backtest_id = backtest_id
        self.stocks = None
        self.train_stocks = None
        self.test_stocks = None
        self.dates = None
        self.makefile = 'Makefile'
        self.output_directory = '/groupstorage/group01/backtest_data/RegressionMeanReversion/'
        self.new_parameters = None
        self.train_cutoff_date = None
        self.start_date = None
        self.combinations = None

    def load_available_data(self,filepath = "../Resources/Data/Equity_and_Commodity/symbols_dates_df.csv",opt_info = "optimisation_info.txt" ):
        
        # load the stock and date data
        self.df = pd.read_csv(filepath)
        # removes repeated names
        self.stocks = self.df['stock'].unique()
        # open athe file withb optimisation info
        with open(opt_info, 'r') as file:
            lines = file.readlines()
        for line in lines:
            # will load stocks - defaults to a random selection if not provided 
            if line.startswith('TRAIN_STOCKS'):
                self.train_stocks = line.split('=')[1].split(',')
            # will load stocks - defaults to a random selection if not provided 
            if line.startswith('TEST_STOCKS'):
                self.test_stocks = line.split('=')[1].split(',')
            if line.startswith('TRAIN_CUTOFF_DATE'):
                self.train_cutoff_date = line.split('=')[1]
            if line.startswith('TIME_SPLIT_STOCK'):
                self.stocks = random.sample(self.stocks,10)
            if line.startswith('ACCOUNTSIZE'):
                self.account_size = line.split('=')[1]
        
    def generate_combinations(self,combinations_file = 'parameter_combinations.txt'):
        #open the parameters file
        with open(combinations_file, 'r') as file:
            lines = file.readlines()

        # Extract parameter names and values
        param_names = [line.strip().split('=')[0] for line in lines]
        choices = [line.strip().split('=')[1].split(',') for line in lines]

        # Generate combinations
        combinations = list(itertools.product(*choices))

        # Format combinations as strings
        formatted_combinations = []
        for combo in combinations:
            formatted_combo = '|'.join(f"{name}={value}" for name, value in zip(param_names, combo))
            formatted_combinations.append(formatted_combo)
        return formatted_combinations

    def get_stocks(self):
        aggregated_volumes = self.df.groupby('stock')['Volume'].sum().reset_index()
        sorted_stocks = aggregated_volumes.sort_values(by='Volume', ascending=False)
        high_volume_stocks = sorted_stocks['stock'].head(5).tolist()
        low_volume_stocks = sorted_stocks['stock'].tail(len(sorted_stocks) - 5).tolist()
        return high_volume_stocks, low_volume_stocks
    
    def load_json(self, file_name = None):
        if file_name is None:
            file_name = self.output_directory+'backtest_data.json'
        try:
            with open(file_name, 'r') as file:
                return json.load(file)
        except Exception as e:
            print(f"Error reading {file_name}: {e}")
            return None

    def write_json(self, data):
        path = self.output_directory+self.backtest_id+'backtest_train.json'
        json_data = self.load_json(path)
        if json_data is None:
            json_data = []
        json_data.insert(0, data)
        with open(path, 'w') as file:
            json.dump(json_data, file, indent=4)
        

    def convert_to_dict(self):
        params = self.new_parameters.split('|')
        match = {}
        for param in params:
            key,value = param.split('=')
            match[key] = value
        return match

    def find_matching_entries(self, symbols):
        json_data = self.load_json(self.output_directory)
        if json_data is None:
            return []

        for entry in json_data:
            if (entry.get('symbols') == 'XNAS.ITCH-'+symbols and 
                entry.get('backtest_id') == self.backtest_id and 
                entry.get('parameters') == self.convert_to_dict()):
                    return entry.get('unique_id'), entry.get('stats')
            else:
                raise ValueError('missing json corresponding to test')

    def gen_train_data(self):
        # if self.split_type == 'stock':
        #     print('accesed_split_type')
        if self.train_stocks is None:
            self.train_stocks,self.test_stocks = self.train_test_split_stock()
        self.combinations = self.generate_combinations()
        for comb in self.combinations:
            self.new_parameters=comb
            for stock in self.train_stocks:
                self.modify_makefile(stock)
                self.run_make_target()
                print('backtest_complete')
    
    def modify_makefile(self, stock):
        with open(self.makefile, 'r') as file:
            lines = file.readlines()

        with open(self.makefile, 'w') as file:
            for line in lines:
                if line.startswith('START_DATE=') and self.start_date is not None:
                    line = f'START_DATE={self.start_date}\n'  # Ensure newline is included
                elif line.startswith('END_DATE=') and self.train_cutoff_date is not None:
                    line = f'END_DATE={self.train_cutoff_date}\n'  # Ensure newline is included
                elif line.startswith('SYMBOLS=XNAS.ITCH-'):
                    line = f'SYMBOLS=XNAS.ITCH-{stock}\n'  # Ensure newline is included
                elif line.startswith('PARAMETERS='):
                    line = f'PARAMETERS={self.new_parameters}\n'
                elif line.startswith('ACCOUNTSIZE='):
                    line = f'ACCOUNTSIZE={self.account_size}\n'
                elif line.startswith('BACKTESTID='):
                    line = f'BACKTESTID={self.backtest_id}\n'

                file.write(line)

    def run_make_target(self):
        subprocess.run(['make', 'run_backtest'])
        
    def find_best_parameters(self):
        best_params = {}
        best_sharpe = {}
        best_sortino = {}
        best_MDD = {}
        best_net_PNL = {}
        for stock in self.train_stocks:
            for comb in self.combinations:
                self.new_parameters=comb
                u_id,stats = self.find_matching_entries(stock)
                sharpe = float(stats['sharpe_ratio'])
                sortino = float(stats['sortino_ratio'])
                MDD = float(stats['max_drawdown'])
                net_PNL = float(stats['net_pnl'])
                if sharpe>best_sharpe:
                    best_sharpe = sharpe
                    sharpe_id = u_id
                if sortino>best_sortino:
                    best_sortino = sortino
                    sortino_id = u_id
                if MDD>best_MDD:
                    best_MDD = MDD
                    MDD_id = u_id
                if net_PNL>best_net_PNL:
                    best_net_PNL = net_PNL
                    net_pnl_id = u_id
            best_params['stock']['sharpe']['value'] = best_sharpe
            best_params['stock']['sharpe']['id'] = sharpe_id
            best_params['stock']['sortino']['value'] = best_sortino
            best_params['stock']['sortino']['id'] = sortino_id
            best_params['stock']['MDD']['value'] = best_MDD
            best_params['stock']['MDD']['id'] = MDD_id
            best_params['stock']['net_PNL']['value'] = best_net_PNL
            best_params['stock']['net_PNL']['id'] = net_pnl_id
        self.write_json(best_params)
        print(best_params)
        
    def get_best_parameters(self,criteria = 'sharpe'):
        filename = self.output_directory+self.backtest_id+'backtest_train.json'
        with filename as file:
            data = json.load(file)
        u_id = data['stock'][criteria]['id']
        json_data = self.load_json(self.output_directory)
        for entry in json_data:
            if entry.get('unique_id') == u_id:
                params = entry.get('parameters')
                formatted_combo = '|'.join(f"{params.keys()}={params.values()}")
                self.new_parameters = formatted_combo

    def print_validation_stats(self):
        for stock in self.test_stocks:
            u_id,stats = self.find_matching_entries(stock)
            print('*'*50)
            print('for stock:-',stock)
            print(stats)
            print('*'*50)
            
    def test_set(self):
        for stock in self.test_stocks:
            self.get_best_parameters()
            self.modify_makefile(stock)
            self.run_make_target()
            self.print_validation_stats()
            print('Validation complete')

if __name__ == "__main__":
    backtest_id = sys.argv[1]
    optim = StrategyOptimiser(backtest_id)
    print('loading the data')
    optim.load_available_data()
    print('generating the combinations')
    optim.gen_train_data()
    print('finding the best parameters')
    optim.find_best_parameters()
    print('testing the best parameters')
    optim.test_set()