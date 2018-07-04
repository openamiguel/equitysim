## This code contains the re-consolidated download functions, and can perform any one of the following tasks:
## Download one stock (one-stock-one-file) from API, load one stock (one-stock-one-variable) from local drive, download many stocks (one-stock-one-file) from API, or load many stocks (many-stocks-one-variable) from local drive
## Author: Miguel Opeña
## Version: 1.1.0

import pandas as pd
import time
import sys

import command_parser
import ticker_universe

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
	print("Downloading " + symbol + " from AlphaVantage...")
	tick_data = None
	# Accounts for the fact that AlphaVantage lacks certain high-volume ETFs and mutual funds
	try:
		tick_data = pd.read_csv(read_path, index_col='timestamp')
	except ValueError:
		print(symbol + " not found by AlphaVantage. Download unsuccessful.\n")
		return tick_data
	print(symbol + " successfully downloaded!")
	# Flips the data around (AlphaVantage presents it in reverse chronological order, but I prefer regular chronological)
	tick_data = tick_data.reindex(index=tick_data.index[::-1])
	# Saves ticker data to CSV, if requested
	if writefile:
		print("Saving data on " + symbol + "...")
		write_path = folderpath + "/" + symbol + "_" + function
		if interval != "": 
			write_path = write_path + "&" + interval
		tick_data.to_csv(write_path + "." + datatype)
		print("Data on " + symbol + " successfully saved!\n")
	# Returns the data on symbol
	return tick_data