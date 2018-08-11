## This code contains the re-consolidated download functions, and can perform any one of the following tasks:
## Download one stock (one-stock-one-file) from API, load one stock (one-stock-one-variable) from local drive, download many stocks (one-stock-one-file) from API, or load many stocks (many-stocks-one-variable) from local drive
## Author: Miguel Opeña
## Version: 2.1.3

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
handler = logging.FileHandler('{}/equitysim_download.log'.format(LOGDIR))
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

# Sample format for stocks: "{}function=TIME_SERIES_{}&symbol={}&apikey={}&datatype={}&outputsize={}"
# Sample format for forex: "{}function=FX_{}&from_symbol={}&to_symbol={}&apikey={}&datatype={}&outputsize={}"

class CDownloader:
	""" A class to download one, or many, symbols from AlphaVantage """
	def __init__(self, folderpath, api_key, function="DAILY", interval="", 
		    output_size="full", datatype="csv", 
		    url_format="{}function=TIME_SERIES_{}&symbol={}&apikey={}&datatype={}&outputsize={}"):
		self.folderpath = folderpath
		self.api_key = api_key
		self.function = function
		self.interval = interval
		# Checks if user has failed to account for the interval
		if function == "INTRADAY" and interval == "":
			logger.warning("Class CDownloader constructor must take interval as a parameter if INTRADAY chosen as function")
			logger.warning("Default value of interval set to 1 minute")
			self.interval = "1min"
		self.output_size = output_size
		self.datatype = datatype
		self.url_format = url_format
		# Number of seconds to delay between each downloader query
		self.delay = 15
		# Start of the URL for AlphaVantage queries
		self.main_url = "https://www.alphavantage.co/query?"

	def load_single(self, symbol, writefile=False):
		""" Downloads data on a single symbol from AlphaVantage according to user parameters, as a dataframe and (if prompted) as a file. 
			See the AlphaVantage documentation for more details. 
			Inputs: symbol (can be a tuple or list of two symbols), order to
				write file (default: No)
			Outputs: dataframe with all available data on symbol
		"""
		# Checks if the read path involves a stock or forex
		read_path = ""
		# Symbol string will come up in the file name
		symbol_str = ""
		# Forex case
		if type(symbol) is tuple or type(symbol) is list and len(symbol) >= 2:
			logger.info("Downloading the provided symbols: {} and {}".format(symbol[0], symbol[1]))
			read_path = self.url_format.format(self.main_url, self.function, symbol[0], symbol[1], self.api_key, self.datatype, self.output_size)
			symbol_str = symbol[0] + "_" + symbol[1]
		# Equity case
		elif type(symbol) is str or len(symbol) == 1:
			symbol_str = symbol[0] if type(symbol) is not str else symbol
			logger.info("Downloading the symbol {} from AlphaVantage".format(symbol_str))
			read_path = self.url_format.format(self.main_url, self.function, symbol_str, self.api_key, self.datatype, self.output_size)
		# Outputs the read path file
		logger.debug("Attempting to scrape URL: %s", read_path)
		# Checks if the function is intraday (regardless of the type of data)
		if self.function == "INTRADAY":
			read_path = read_path + "&interval=" + self.interval
		tick_data = None
		# Accounts for the fact that AlphaVantage lacks certain high-volume ETFs and mutual funds
		try:
			tick_data = pd.read_csv(read_path, index_col='timestamp')
		except ValueError:
			logger.error(symbol_str + " not found by AlphaVantage. Download unsuccessful.")
			return tick_data
		logger.info(symbol_str + " successfully downloaded!")
		# Flips the data around (AlphaVantage presents it in reverse chronological order, but I prefer regular chronological)
		tick_data = tick_data.reindex(index=tick_data.index[::-1])
		# Saves ticker data to file, if requested
		if writefile:
			logger.info("Saving data on " + symbol_str + "...")
			write_path = self.folderpath + "/" + symbol_str + "_" + self.function
			if self.interval != "": 
				write_path = write_path + "&" + self.interval
			tick_data.to_csv(write_path + "." + self.datatype)
			logger.info("Data on " + symbol_str + " successfully saved!")
		# Returns the data on symbol
		return tick_data

	def load_separate(self, tickerverse):
		""" Downloads OHCLV (open-high-close-low-volume) data on given tickers.
			Inputs: ticker universe
			Outputs: True if everything works
		"""
		current_symbols = io_support.get_current_symbols(self.folderpath)
		for symbol in tickerverse:
			if symbol in current_symbols: continue
			# Read each symbol and write to file (hence writeFile=True)
			self.load_single(symbol, writefile=True)
			# Delay prevents HTTP 503 errors
			time.sleep(self.delay)
		return True

class CLoader:
	""" A class to load one, or several, symbols from local hard drive """
	def __init__(self, folderpath, function="DAILY", interval="", 
		    output_size="full", datatype="csv"):
		self.folderpath = folderpath
		self.function = function
		self.interval = interval
		# Checks if user has failed to account for the interval
		if function == "INTRADAY" and interval == "":
			logger.warning("Class CLoader constructor must take interval as a parameter if INTRADAY chosen as function")
			logger.warning("Default value of interval set to 1 minute")
			self.interval = "1min"
		self.output_size = output_size
		self.datatype = datatype

	def load_single_drive(self, symbol):
		""" Downloads data on a single file (equity or forex) from local drive. 
			Inputs: symbol String or tuple object
			Outputs: dataframe with all available data on symbol
		"""
		# Checks if the symbol input is forex or equity
		readpath = ""
		symbol_str = ""
		# Forex case
		if type(symbol) is tuple or type(symbol) is list and len(symbol) >= 2:
			symbol_str = symbol[0] + "_" + symbol[1]
		# Equity case
		elif type(symbol) is str or len(symbol) == 1:
			symbol_str = symbol[0] if type(symbol) is not str else symbol
		readpath = self.folderpath + "/" + symbol_str + "_" + self.function
		if self.interval != "":
			readpath = readpath + "&" + self.interval
		readpath = readpath + "." + self.datatype
		logger.info("Retrieving " + symbol_str + " from local drive...")
		tick_data = None
		try:
			tick_data = pd.read_csv(readpath, index_col='timestamp')
		except FileNotFoundError:
			logger.error("Retrieval unsuccessful. File not found at " + readpath)
			return tick_data
		# De-duplicates the index
		tick_data = tick_data[~tick_data.index.duplicated(keep='first')]
		logger.info("Data on " + symbol_str + " successfully retrieved!")
		return tick_data

	def load_combined_drive(self, tickerverse, column_choice="close"):
		""" Downloads OHCLV (open-high-close-low-volume) data on given tickers in compact or full form.
			Inputs: ticker universe, choice of column to write (default: close)
			Outputs: combined output as dataframe
		"""
		combined_output = pd.DataFrame()
		for symbol in tickerverse:
			# Read each symbol and concatenate with previous symbols
			tick_data = self.load_single_drive(symbol)
			combined_output = pd.concat([combined_output, tick_data[column_choice]], axis=1)
		# Makes each column the symbol of asset (to avoid confusion)
		combined_output.columns = tickerverse
		return combined_output

class CMacroDownloader:
	""" A class to download macro data from handpicked sources. """
	def __init__(self):
		# Initialize variables
		return
	def get_world_bank():
		# Gets data from the World Bank
		# Download file from the World Bank link
		# Parse it and clean if needed
		# Save to folderpath
		return

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
	## Handles user choice of forex or equity (not forex)
	if name == "FOREX":
		fx_format = "{}function=FX_{}&from_symbol={}&to_symbol={}&apikey={}&datatype={}&outputsize={}"
		downloader = CDownloader(folder_path, api_key, function, interval, url_format=fx_format)
		downloader.load_separate(tickerverse)
	else:
		downloader = CDownloader(folder_path, api_key, function, interval)
		downloader.load_separate(tickerverse)
	## Closing output
	logger.info("Download complete. Have a nice day!")

if __name__ == "__main__":
	main()
