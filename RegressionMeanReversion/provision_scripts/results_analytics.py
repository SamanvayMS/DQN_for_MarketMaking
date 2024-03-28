import pandas as pd
import numpy as np
import json
import sys
import os
# import time
import re
import sys
import glob
import matplotlib.pyplot as plt
import numpy as np
import os
import fnmatch

class Utils:
    def __init__(self,cra_file,backtest_directory,symbols,parameters):
        # Paths
        self.backtest_directory = backtest_directory
        self.json_file_path = self.backtest_directory + 'backtest_info.json'
        self.cra_file = cra_file
        self.unique_id = None
        self.symbols=symbols
        self.parameters=parameters

        # Dataframes
        self.pnl = None
        self.fill = None
        self.order = None
        # New results template json
        self.new_results = None

        # Flags
        self.skip_analysis = False
        
    def extract_unique_id(self, file_path):
        file_name = os.path.basename(file_path)
        return file_name.split('_')[3]

    def expand_parameters(self):
        param_list = self.parameters.split('|')
        for param in param_list:
            split_param = param.split('=')
            self.new_results['parameters'][split_param[0]]=split_param[1]
            
    def split_parameters_to_string(self):
        param_list = self.parameters.split('|')
        param_string = 'Parameters:\n'
        for param in param_list:
            param_string = param_string + param + '\t'
        return param_string

    def extract_details_from_filename(self):
        pattern = r'BACK_([A-Za-z0-9]+)_([0-9]{4}-[0-9]{2}-[0-9]{2})_([0-9]+)_start_([0-9]{2}-[0-9]{2}-[0-9]{4})_end_([0-9]{2}-[0-9]{2}-[0-9]{4})'
        match = re.search(pattern, self.cra_file)

        if match:
            self.cra_attributes = [match.group(1),match.group(2),match.group(3),match.group(4),match.group(5)]
            self.new_results = {
            'backtest_date': match.group(2),
            'unique_id': match.group(3),
            'symbols':self.symbols,
            'parameters':{},
            'instance_name': match.group(1),
            'start_date': match.group(4),
            'end_date': match.group(5),
            'has_csv':True,
            'stats':{'pnl':{},'fill':{}},
            }
            self.expand_parameters()
        else:
            raise ValueError("Results filename format doesn't match expected pattern")
        # self.file_modified_datetime = time.ctime(os.path.getmtime(file_path))

    def load_csv_files(self):
        # Format the filenames based on the unique_id, start_date, and end_date
        self.unique_id = self.extract_unique_id(self.cra_file)
        self.extract_details_from_filename()
        if self.unique_id:
            json_data = self.read_json()
            if json_data:
                latest_instance = json_data[0]
                if latest_instance['unique_id'] == self.unique_id:
                    print("no new results")
                    return
                else:
                    self.update_json()
            else:
                self.create_json()
        else:
            raise ValueError('unique id not found')
       # Patterns to match files based only on the unique_id
        patterns = {
            'pnl': f"BACK_*_{self.unique_id}_*_pnl.csv",
            'fill': f"BACK_*_{self.unique_id}_*_fill.csv",
            'order': f"BACK_*_{self.unique_id}_*_order.csv"
        }

        # Check if files exist and read them
        all_exist = True
        for key, pattern in patterns.items():
            # Find file matching the pattern
            file_path = self.find_file_by_pattern(pattern)
            if file_path and os.path.isfile(file_path):
                # Read CSV and store in the respective attribute
                setattr(self, key, pd.read_csv(file_path))
            else:
                all_exist = False
                break

        if not all_exist:
            print("CSVs not generated.")
            self.pnl = self.fill = self.order = None
            self.new_results['has_csv'] = False
            self.skip_analysis = True

    def find_file_by_pattern(self, pattern):
        # Implementation for searching file matching the pattern in self.backtest_directory
        # This should return the full path of the matching file or None if not found
        # Dummy implementation (replace with actual search logic)
        directory = self.backtest_directory + 'csv_files'
        print(f" accesing {directory} for csv files")
        for root, dirs, files in os.walk(directory):
            for file in files:
                if fnmatch.fnmatch(file, pattern):
                    return os.path.join(root, file)
        return None

    def is_any_csv_empty(self):
        if self.pnl is not None:
            if len(self.pnl) == 0:
                print("No P&L recorded.")
                self.skip_analysis = True
        else:
            self.skip_analysis = True
            print("PnL CSV not loaded.")

        if self.fill is not None:
            if len(self.fill) == 0:
                print("No fills recorded.")
                self.skip_analysis = True
        else:
            self.skip_analysis = True
            print("Fill CSV not loaded.")

        if self.order is not None:
            if len(self.order) == 0:
                print("No orders recorded.")
                self.skip_analysis = True
        else:
            self.skip_analysis = True
            print("Order CSV not loaded.")

        if not self.skip_analysis:
            print("No empty CSV files found.")
    
    def read_json(self):
        if not os.path.exists(self.json_file_path):
            return None
        with open(self.json_file_path, 'r') as file:
            return json.load(file)

    def create_json(self):
        json_data = []
        json_data.insert(0, self.new_results)
        with open(self.json_file_path, 'w') as file:
            json.dump(json_data, file, indent=4)

    def update_json(self,same = False):        
        json_data = self.read_json()     
        if same:
            json_data[0] = self.new_results
        else:
            json_data.insert(0, self.new_results)
        with open(self.json_file_path, 'w') as file:
            json.dump(json_data, file, indent=4)

class PnLAnalytics:
    def __init__(self, pnl_df, fill_df, order_df, account_size=1000000):
        self.account_size = float(account_size)
        self.pnl_df = pnl_df
        self.fill_df = fill_df
        self.order_df = order_df
        
    def create_pnl_stats(self):
        self.pnl_df['account_value'] = self.pnl_df['Cumulative PnL'] + self.account_size
        self.pnl_df['PnL'] = self.pnl_df['Cumulative PnL'].diff().fillna(0)
        self.pnl_df['cumulative_pnl_percentage'] = ((self.pnl_df['account_value'] / self.account_size)-1) * 100
        self.pnl_df['returns'] = self.pnl_df['account_value'].pct_change().fillna(0)

    def calculate_sharpe_ratio(self,PNL=True):
        # Adjust risk-free rate for the number of periods
        if PNL:
            sharpe_ratio = np.mean(self.pnl_df['PnL']) / np.std(self.pnl_df['PnL'])
        else:
            sharpe_ratio = np.mean(self.pnl_df['returns']) / np.std(self.pnl_df['returns'])
        return sharpe_ratio
    
    def calculate_sortino_ratio(self,PNL=True):
        if PNL:
            downside_returns = self.pnl_df['PnL'][self.pnl_df['PnL'] < 0]
            downside_deviation = np.sqrt(np.mean(np.square(downside_returns)))
            excess_returns = self.pnl_df['PnL']
            sortino_ratio = np.mean(excess_returns) / downside_deviation if downside_deviation != 0 else np.nan
        else:
            downside_returns = self.pnl_df['returns'][self.pnl_df['returns'] < 0]
            downside_deviation = np.sqrt(np.mean(np.square(downside_returns)))
            excess_returns = self.pnl_df['returns']
            sortino_ratio = np.mean(excess_returns) / downside_deviation if downside_deviation != 0 else np.nan
        return sortino_ratio

    def calculate_max_drawdown(self):
        running_max = (self.pnl_df['account_value']).cummax()
        self.pnl_df['drawdown'] = (self.pnl_df['account_value'] - running_max) / running_max
        max_drawdown = self.pnl_df['drawdown'].min()
        return max_drawdown

    def calculate_net_pnl(self):
        net_pnl = self.pnl_df['account_value'].iloc[-1] - self.pnl_df['account_value'].iloc[0]
        return net_pnl
    
    def create_plots(self,directory,unique_id,text_to_add=''):
        
        def add_text_to_figure(figure, text):
            figure.text(0.5, 0.01, text, ha='center', fontsize=12, color='grey')
            
        fig, axs = plt.subplots(4,1, figsize=(20, 40))
        axs[0].plot(self.pnl_df['Time'], self.pnl_df['account_value'])
        axs[0].set_title('Account Value')
        axs[0].set_xlabel('Time')
        axs[0].set_ylabel('Account Value')
        axs[0].grid(True)
        
        axs[1].plot(self.pnl_df['Time'], self.pnl_df['cumulative_pnl_percentage'], color='green', label='Cumulative PnL Percentage')
        axs[1].plot(self.pnl_df['Time'], self.pnl_df['drawdown'], color='red' , alpha=0.5, label='drawdown')
        axs[1].set_title('% returns')
        axs[1].set_xlabel('Time')
        axs[1].set_ylabel('Cumulative PnL Percentage')
        axs[1].grid(True)
        
        axs[2].plot(self.pnl_df['Time'], self.pnl_df['returns'])
        axs[2].set_title('% returns')
        axs[2].set_xlabel('Time')
        axs[2].set_ylabel('Returns')
        axs[2].grid(True)
        
        axs[3].plot(self.pnl_df['Time'], self.pnl_df['PnL'])
        axs[3].set_title('PnL')
        axs[3].set_xlabel('Time')
        axs[3].set_ylabel('PnL')
        axs[3].grid(True)
        
        add_text_to_figure(fig, text_to_add)
        
        directory = directory + 'result_plots/'
        os.makedirs(directory, exist_ok=True)
        file_path = os.path.join(directory, unique_id + 'results_plot.png')
        plt.savefig(file_path)
        
        # Additional plots
        fig, axs = plt.subplots(2,1, figsize=(20, 20))
        
        axs[0].hist(self.pnl_df['PnL'], bins=50, color='blue', alpha=0.7)
        axs[0].set_title('PnL Distribution')
        axs[0].set_xlabel('PnL')
        axs[0].set_ylabel('Frequency')
        axs[0].grid(True)

        axs[1].scatter(self.pnl_df['Time'], self.pnl_df['returns'], color='purple')
        axs[1].set_title('Returns Over Time')
        axs[1].set_xlabel('Time')
        axs[1].set_ylabel('Returns')
        axs[1].grid(True)

        add_text_to_figure(fig, text_to_add)
        
        # Save additional plots
        additional_file_path = os.path.join(directory, unique_id + 'additional_results_plot.png')
        plt.savefig(additional_file_path)
        
class FillAnalytics:
    def __init__(self, data):
        self.data = data

    def total_volume_traded(self):
        return self.data['Quantity'].sum()
    
    def total_volume_traded_per_symbol(self):
        return self.data.groupby('Symbol')['Quantity'].sum()

    def total_execution_cost(self):
        return self.data['ExecutionCost'].sum()
    
    def average_execution_cost_per_symbol(self):
        return self.data.groupby('Symbol')['ExecutionCost'].mean()

    def total_number_of_trades(self):
        return len(self.data)
    
if __name__ == '__main__':

    os.chdir(os.path.expanduser('~/ss/bt/backtesting-results/'))
    result_updated = False

    if len(sys.argv) > 2:
        cra_filepath = sys.argv[1]
        backtest_results_path = sys.argv[2]
        symbols = sys.argv[3]
        parameters = sys.argv[4]
        account_size = sys.argv[5]
        utils = Utils(cra_file=cra_filepath,backtest_directory=backtest_results_path,symbols=symbols,parameters=parameters)
        utils.load_csv_files()
        utils.is_any_csv_empty()

        if utils.skip_analysis:
            print("either no files or empty file/s found. Check your strategy.")
        else:
            analytics = PnLAnalytics(utils.pnl,utils.fill,utils.order,account_size)
            analytics.create_pnl_stats()
            utils.new_results['stats']['pnl']['sharpe_ratio'] = analytics.calculate_sharpe_ratio()
            utils.new_results['stats']['pnl']['sortino_ratio'] = analytics.calculate_sortino_ratio()
            utils.new_results['stats']['pnl']['max_drawdown'] = analytics.calculate_max_drawdown()
            utils.new_results['stats']['pnl']['net_pnl'] = analytics.calculate_net_pnl()
            analytics.create_plots(utils.backtest_directory,utils.unique_id,utils.split_parameters_to_string())
            # Fill Analytics
            fill_analytics = FillAnalytics(utils.fill)
            utils.new_results['stats']['fill']['total_volume_per_symbol'] = fill_analytics.total_volume_traded_per_symbol().to_dict()
            utils.new_results['stats']['fill']['total_execution_cost'] = fill_analytics.total_execution_cost()
            utils.new_results['stats']['fill']['total_trades'] = fill_analytics.total_number_of_trades()
            utils.update_json(True)
            print(utils.new_results)
            result_updated = True
    else:
        print("Missing arguments. Usage: python3 results_analytics.py <cra_filepath> <file_path> <symbols> <parameters> <accountsize>")
        sys.exit(1)

    sys.exit(0 if result_updated else 1)