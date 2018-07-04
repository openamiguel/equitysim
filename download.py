## This code contains the re-consolidated download functions, and can perform any one of the following tasks:
## Download one stock (one-stock-one-file) from API, load one stock (one-stock-one-variable) from local drive, download many stocks (one-stock-one-file) from API, or load many stocks (many-stocks-one-variable) from local drive
## Author: Miguel Opeña
## Version: 1.3.0

import pandas as pd
import time
import sys

import command_parser
import ticker_universe

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
	logger.debug("Downloading " + symbol + " from AlphaVantage...")
	tick_data = None
	# Accounts for the fact that AlphaVantage lacks certain high-volume ETFs and mutual funds
	try:
		tick_data = pd.read_csv(read_path, index_col='timestamp')
	except ValueError:
		logger.error(symbol + " not found by AlphaVantage. Download unsuccessful.")
		return tick_data
	logger.debug(symbol + " successfully downloaded!")
	# Flips the data around (AlphaVantage presents it in reverse chronological order, but I prefer regular chronological)
	tick_data = tick_data.reindex(index=tick_data.index[::-1])
	# Saves ticker data to CSV, if requested
	if writefile:
		logger.debug("Saving data on " + symbol + "...")
		write_path = folderpath + "/" + symbol + "_" + function
		if interval != "": 
			write_path = write_path + "&" + interval
		tick_data.to_csv(write_path + "." + datatype)
		logger.debug("Data on " + symbol + " successfully saved!")
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
	logger.debug("Retrieving " + symbol + " from local drive...")
	tick_data = None
	try:
		tick_data = pd.read_csv(readpath, index_col='timestamp')
	except FileNotFoundError:
		logger.error("Retrieval unsuccessful. File not found at " + readpath)
		return tick_data
	tick_data = tick_data[~tick_data.index.duplicated(keep='first')]
	logger.debug("Data on " + symbol + " successfully retrieved!")
	return tick_data

def load_separate(tickerverse, api_key, function="DAILY", interval="", output_size="full", folderpath="", datatype="csv"):
	""" Downloads OHCLV (open-high-close-low-volume) data on given tickers in compact or full form.
		Inputs: ticker universe, API key (user-specific), time series function (default: daily), time interval (for intraday data only), 
			output size (default: full), folder path to write files to (default: empty), output type (default: CSV)
		Outputs: True if everything works
	"""
	for symbol in tickerverse:
		# Read each symbol and write to file (hence writeFile=True)
		load_single(symbol, api_key, function=function, interval=interval, output_size=output_size, writefile=True, folderpath=folderpath, datatype=datatype)
		# Delay prevents HTTP 503 errors
		time.sleep(DELAY)
	return True