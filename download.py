## This code contains the re-consolidated download functions, and can perform any one of the following tasks:
## Download one stock (one-stock-one-file) from API, load one stock (one-stock-one-variable) from local drive, download many stocks (one-stock-one-file) from API, or load many stocks (many-stocks-one-variable) from local drive
## Author: Miguel Opeña
## Version: 2.0.6

import logging
import os
import pandas as pd
import time
import sys

import command_parser
import io_support

LOGDIR = "/Users/openamiguel/Desktop/LOG"
# Initialize logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# Set file path for logger
handler = logging.FileHandler('{}/equitysim.log'.format(LOGDIR))
handler.setLevel(logging.DEBUG)
# Format the logger
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
# Add the new format
logger.addHandler(handler)
# Format the console logger
consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.INFO)
consoleHandler.setFormatter(formatter)
# Add the new format to the logger file
logger.addHandler(consoleHandler)

logger.info("----------INITIALIZING NEW RUN OF %s----------", os.path.basename(__file__))

# Start of the URL for AlphaVantage queries
MAIN_URL = "https://www.alphavantage.co/query?"
# Delay prevents HTTP 503 errors (AlphaVantage recommends 10, but 15 works in practice)
DELAY = 15

def load_single(symbol, api_key, function="DAILY", interval="", output_size="full", writefile=False, folderpath="", datatype="csv"):
	""" Downloads data on a single symbol from AlphaVantage according to user parameters, as a dataframe and (if prompted) as a file. 
		See the AlphaVantage documentation for more details. 
		Inputs: symbol, API key (user-specific), time series function (default: daily), time interval (for intraday data only), 
			output size (default: full), order to write file (default: no), folder path to write files to (default: empty),
			output type (default: CSV)
		Outputs: dataframe with all available data on symbol
	"""
	# Sets up the link to read the symbol from
	read_path = MAIN_URL + "function=TIME_SERIES_" + function + "&symbol=" + symbol + "&apikey=" + api_key + "&datatype=" + datatype + "&outputsize=" + output_size
	if function == "INTRADAY":
		read_path = read_path + "&interval=" + interval
	# Gives a tidbit of verbose output
	logger.info("Downloading " + symbol + " from AlphaVantage...")
	tick_data = None
	# Accounts for the fact that AlphaVantage lacks certain high-volume ETFs and mutual funds
	try:
		tick_data = pd.read_csv(read_path, index_col='timestamp')
	except ValueError:
		logger.error(symbol + " not found by AlphaVantage. Download unsuccessful.")
		return tick_data
	logger.info(symbol + " successfully downloaded!")
	# Flips the data around (AlphaVantage presents it in reverse chronological order, but I prefer regular chronological)
	tick_data = tick_data.reindex(index=tick_data.index[::-1])
	# Saves ticker data to CSV, if requested
	if writefile:
		logger.info("Saving data on " + symbol + "...")
		write_path = folderpath + "/" + symbol + "_" + function
		if interval != "": 
			write_path = write_path + "&" + interval
		tick_data.to_csv(write_path + "." + datatype)
		logger.info("Data on " + symbol + " successfully saved!")
	# Returns the data on symbol
	return tick_data

def load_single_drive(symbol, function="DAILY", interval="", folderpath="", datatype="csv"):
	""" Downloads data on a single symbol from local drive according to user parameters, as a dataframe. 

		Inputs: symbol, time series function (default: daily), time interval (for intraday data only), 
			folder path to look for file (default: empty), data type (default: csv)
		Outputs: dataframe with all available data on symbol
	"""
	readpath = folderpath + "/" + symbol + "_" + function
	if interval != "":
		readpath = readpath + "&" + interval
	readpath = readpath + "." + datatype
	logger.info("Retrieving " + symbol + " from local drive...")
	tick_data = None
	try:
		tick_data = pd.read_csv(readpath, index_col='timestamp')
	except FileNotFoundError:
		logger.error("Retrieval unsuccessful. File not found at " + readpath)
		return tick_data
	# De-duplicates the index
	tick_data = tick_data[~tick_data.index.duplicated(keep='first')]
	logger.info("Data on " + symbol + " successfully retrieved!")
	return tick_data

def load_separate(tickerverse, api_key, function="DAILY", interval="", output_size="full", folderpath="", datatype="csv"):
	""" Downloads OHCLV (open-high-close-low-volume) data on given tickers in compact or full form.
		Inputs: ticker universe, API key (user-specific), time series function (default: daily), time interval (for intraday data only), 
			output size (default: full), folder path to write files to (default: empty), output type (default: CSV)
		Outputs: True if everything works
	"""
	current_symbols = io_support.get_current_symbols(folderpath)
	for symbol in tickerverse:
		if symbol in current_symbols: continue
		# Read each symbol and write to file (hence writeFile=True)
		load_single(symbol, api_key, function=function, interval=interval, output_size=output_size, writefile=True, folderpath=folderpath, datatype=datatype)
		# Delay prevents HTTP 503 errors
	time.sleep(DELAY)
	return True
	
def load_combined_drive(tickerverse, column_choice="close", function="DAILY", interval="", output_size="full", folderpath="", datatype="csv"):
	""" Downloads OHCLV (open-high-close-low-volume) data on given tickers in compact or full form.
		Inputs: ticker universe, choice of column to write, time series function (default: daily), 
			time interval (for intraday data only), output size (default: full), 
			folder path to write files to (default: empty), output type (default: CSV)
		Outputs: combined output
	"""
	combined_output = pd.DataFrame()
	for symbol in tickerverse:
		# Read each symbol and concatenate with previous symbols
		tick_data = load_single_drive(symbol, function=function, interval=interval, folderpath=folderpath, datatype=datatype)
		combined_output = pd.concat([combined_output, tick_data[column_choice]], axis=1)
	# Makes each column the symbol of asset (to avoid confusion)
	combined_output.columns = tickerverse
	return combined_output

def main():
	""" User interacts with interface through command prompt, which obtains several "input" data. 
		Here are some examples of how to run this program: 

		python download.py -tickerUniverse SNP500 -folderPath C:/Users/Miguel/Documents/EQUITIES/stockDaily -apiKey <INSERT KEY> -function DAILY
			This will download files of daily data on S&P 500 tickers to the desired folder path.

		python download.py -tickerUniverse AAPL -folderPath C:/Users/Miguel/Documents/EQUITIES/stockIntraday1Min -apiKey <INSERT KEY> -function INTRADAY -interval 1min
			This will download files of daily data on S&P 500 tickers to the desired folder path.

		Inputs: implicit through command prompt
		Outputs: 0 if everything works
	"""
	prompts = sys.argv
	## Handles which symbol the user wants to download.
	tickerverse, name = command_parser.get_tickerverse_from_prompts(prompts)
	## Handles where the user wants to download their files. 
	# Default folder path is relevant to the author only. 
	folder_path = command_parser.get_generic_from_prompts(prompts, query="-folderPath", default="/Users/openamiguel/Documents/EQUITIES/stockDaily", req=False)
	## Handles the user's API key. 
	api_key = command_parser.get_generic_from_prompts(prompts, query="-apiKey")
	## Handles the desired time series function. 
	function = command_parser.get_generic_from_prompts(prompts, query="-function")
	## Handles the special case: if INTRADAY selected. 
	interval = command_parser.get_generic_from_prompts(prompts, query="-interval") if function == "INTRADAY" else ""
	## Handles user choice of separate or combined
	load_separate(tickerverse, api_key, function=function, interval=interval, folderpath=folder_path)
	## Closing output
	logger.info("Download complete. Have a nice day!")

if __name__ == "__main__":
	main()
