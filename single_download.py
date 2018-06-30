## This code can download any one stock/ETF/fund/index symbol from AlphaVantage's API. 
## Author: Miguel Opeña
## Version: 3.4.0

import pandas as pd
import sys

import command_parser

# Start of the URL for AlphaVantage queries
MAIN_URL = "https://www.alphavantage.co/query?"

def fetch_symbol(symbol, apiKey, function="DAILY", outputSize="full", dataType="csv", folderPath="", writeFile=False, interval=""):
	""" Downloads data on a single symbol from AlphaVantage according to user parameters, as a dataframe and (if prompted) as a file. 
		See the AlphaVantage documentation for more details. 

		Inputs: symbol, API key (user-specific), time series function (default: daily), output size (default: full), 
			output type (default: CSV), folder path to write files to (default: empty), order to write file (default: no),
			time interval (for intraday data only)
		Outputs: dataframe with all available data on symbol
	"""
	# Sets up the link to read the symbol from
	readPath = MAIN_URL + "function=TIME_SERIES_" + function + "&symbol=" + symbol + "&apikey=" + apiKey + "&datatype=" + dataType + "&outputsize=" + outputSize
	if function == "INTRADAY":
		readPath = readPath + "&interval=" + interval
	# Gives a tidbit of verbose output
	print("Downloading " + symbol + " from AlphaVantage...")
	tickData = None
	# Accounts for the fact that AlphaVantage lacks certain high-volume ETFs and mutual funds
	try:
		tickData = pd.read_csv(readPath, index_col='timestamp')
	except ValueError:
		print(symbol + " not found by AlphaVantage. Download unsuccessful.\n")
		return None
	print(symbol + " successfully downloaded!")
	# Flips the data around (AlphaVantage presents it in reverse chronological order, but I prefer regular chronological)
	tickData = tickData.reindex(index=tickData.index[::-1])
	# Saves ticker data to CSV, if requested
	if writeFile:
		print("Saving data on " + symbol + "...")
		if folderPath == "":
			raise ValueError("You did not give single_download.py a file path to write your file. Please try again.")
		else:
			writePath = folderPath + "/" + symbol + "_" + function
			if interval != "": 
				writePath = writePath + "&" + interval
			tickData.to_csv(writePath + ".csv")
			print("Data on " + symbol + " successfully saved!\n")
	# Returns the data on symbol
	return tickData

def fetch_symbol_from_drive(symbol, function="DAILY", interval="", folderPath=""):
	""" Downloads data on a single symbol from local drive according to user parameters, as a dataframe. 

		Inputs: symbol, time series function (default: daily), time interval (for intraday data only), folder path to look for file (default: empty)
		Outputs: dataframe with all available data on symbol
	"""
	readPath = folderPath + "/" + symbol + "_" + function
	if interval != "":
		readPath = readPath + "&" + interval
	readPath = readPath + ".csv"
	print("Retrieving " + symbol + " from local drive...")
	tickData = None
	try:
		tickData = pd.read_csv(readPath, index_col='timestamp')
	except FileNotFoundError:
		print("Retrieval unsuccessful. File not found at " + readPath + "\n")
		return None
	tickData = tickData[~tickData.index.duplicated(keep='first')]
	print("Data on " + symbol + " successfully retrieved!\n")
	return tickData

def main():
	""" User interacts with program through command prompt. 
		Example prompts: 

		python single_download.py -symbol MSFT -folderPath C:/Users/Miguel/Desktop/stockData -apiKey <INSERT KEY> -timeSeriesFunction DAILY
			This will download daily data on Microsoft (MSFT) stock to the requested folder path. 

		python single_download.py -symbol GS -folderPath C:/Users/Miguel/Desktop/stockData -apiKey <INSERT KEY> -timeSeriesFunction WEEKLY
			This will download weekly data on Goldman Sachs (GS) stock to the requested folder path. 

		python single_download.py -symbol AAPL -folderPath C:/Users/Miguel/Desktop/stockData -apiKey <INSERT KEY> -timeSeriesFunction INTRADAY -interval 1min
			This will download 1 minute intraday data on Apple (AAPL) stock to the requested folder path. 

		Inputs: implicit through command prompt
		Outputs: 0 if everything works
	"""
	prompts = sys.argv
	## Handles which symbol the user wants to download.
	symbol = command_parser.get_generic_from_prompts(prompts, "-symbol")
	## Handles where the user wants to download their files. 
	# Default folder path is relevant to the author only. 
	folder_path = command_parser.get_generic_from_prompts(prompts, query="-folderPath", default="C:/Users/Miguel/Documents/EQUITIES/stockDaily", req=False)
	## Handles the user's API key. 
	apiKey = command_parser.get_generic_from_prompts(prompts, query="-apiKey")
	## Handles the desired time series function. 
	function = command_parser.get_generic_from_prompts(prompts, query="-function")
	## Handles the special case: if INTRADAY selected. 
	interval = ""
	intraday = function == "INTRADAY"
	if intraday:
		interval = command_parser.get_generic_from_prompts(prompts, query="-interval")## Handles user choice of separate or combined
	# Runs the code
	fetch_symbol(symbol, apiKey, function=function, folderPath=folder_path, writeFile=True, interval=interval)
	# Closing output
	print("Download complete. Have a nice day!")
	return 0

if __name__ == "__main__":
	main()