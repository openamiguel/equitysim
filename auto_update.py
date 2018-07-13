## This code can update all stock files in a given folder directory. 
## Author: Miguel Opeña
## Version: 4.1.2

import glob
import logging
import pandas as pd
import sys
import time

import command_parser
import download

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Delay prevents HTTP 503 errors (AlphaVantage recommends 10, but 15 works in practice)
DELAY = 15

def update_in_folder(folder_path, file_path, api_key):
	""" Automatically updates the SEPARATE file at the given path. The name of said file must follow naming conventions within this program!

		Inputs: folder path to look for files, file path of actual file, API key of user
		Outputs: 0 if everything works
	"""
	# Reads the old data from its file location
	old_data = pd.read_csv(file_path, index_col='timestamp')
	old_data.dropna(how='any',inplace=True)
	# Removes duplicates
	old_data = old_data[~old_data.index.duplicated(keep='first')]
	# Gets the most recent date in the old ticker data
	last_date = old_data.index[-1]
	# Parses the file name using the split function (assumes adherence to naming conventions from download.py)
	file_name = file_path.split(folder_path)[1][1:]
	name_split = file_name.split(".csv")[0].split("_")		
	symbol = name_split[0]
	logger.info("Auto-updating " + symbol + " from AlphaVantage...")
	# Gets the function (daily, intradaily, etc.) from the file name
	# Now gets the adjusted ones properly
	function = "_".join(name_split[1:])
	interval = ""
	if "&" in function:
		functionSplit = function.split("&")
		function = functionSplit[0]
		interval = functionSplit[1]
	# We only need the compact version if the data is not intraday
	output_size = "full" if function == "INTRADAY" else compact
	new_data = download.load_single(symbol, api_key, function=function, output_size=output_size, interval=interval)
	# If unavailable, don't download
	if new_data is None:
		# Delay prevents HTTP 503 errors
		logger.info(symbol + " update failed and skipped.")
		time.sleep(DELAY)
		return None
	# Isolates the data that is new (based on last date/time collected)
	new_data = new_data[(new_data.index == last_date).cumsum() > 0]
	new_data = new_data.drop(index=last_date) if last_date in list(new_data.index.values)
	# Concatenate along row
	finished_output = pd.concat([old_data, new_data])
	# Writes allTickerData to chosen folder path
	finished_output.to_csv(file_path, index_label='timestamp')
	logger.info("Data on " + symbol + " successfully updated!\n")
	# Delay prevents HTTP 503 errors
	time.sleep(DELAY)
	# Returns 0 if the program runs to completion
	return True

def main():
	""" User interacts with interface through command prompt, which obtains several "input" data. 
		Here is an example of how to run this program: 

		python auto_update.py -folderPath C:/Users/Miguel/Desktop/stockData -apiKey <INSERT KEY>
			This will update all stock data at the given folderpath.

		Inputs: implicit through command prompt
		Outputs: True if everything works
	"""
	prompts = sys.argv
	## Handles where the user wants to download their files. 
	# Default folder path is relevant to the author only. 
	folder_path = command_parser.get_generic_from_prompts(prompts, query="-folderPath", default="C:/Users/Miguel/Documents/stockData", req=False)
	## Handles the user's API key. 
	api_key = command_parser.get_generic_from_prompts(prompts, query="-apiKey")
	## Gets all CSV files in the folder
	all_files = glob.glob(folder_path + "/*.csv")
	## Updates all files in folder
	for file_path in all_files:
		update_in_folder(folder_path, file_path, api_key)
	return True

if __name__ == "__main__":
	main()
