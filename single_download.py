## This code can download any one stock/ETF/fund/index symbol from AlphaVantage's API. 
## Author: Miguel Opeña
## Version: 3.2.0

import pandas as pd
import sys

# Start of the URL for AlphaVantage queries
MAIN_URL = "https://www.alphavantage.co/query?"

def fetch_symbol(symbol, apiKey, function="DAILY", outputSize="full", dataType="csv", folderPath="", writeFile=False, interval=""):
	""" Downloads data on a single symbol according to user parameters, as a dataframe and (if prompted) as a file. 
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
		print(symbol + " not found by AlphaVantage. Download unsuccessful.")
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
	symbol = ""
	if "-symbol" in prompts:
		symbol = prompts[prompts.index("-symbol") + 1]
	else:
		raise ValueError("No symbol provided. Please try again.")
	## Handles where the user wants to download their files. 
	# Default folder path is relevant to the author only. 
	folderPath = "C:/Users/Miguel/Documents/stockData"
	if "-folderPath" not in prompts:
		print("Warning: the program will use default file paths, which may not be compatible on your computer.")
	else: 
		folderPath = prompts[prompts.index("-folderPath") + 1]
	## Handles the user's API key. 
	apiKey = ""
	if "-apiKey" in prompts:
		apiKey = prompts[prompts.index("-apiKey") + 1]
	else:
		raise ValueError("No API key provided. Please try again.")
	## Handles the desired time series function. 
	function = ""
	if "-timeSeriesFunction" in prompts:
		function = prompts[prompts.index("-timeSeriesFunction") + 1]
	else:
		raise ValueError("No time series function provided. Please try again.")
	# Handles the special case: if INTRADAY selected. 
	interval = ""
	if function == "INTRADAY" and "-interval" in prompts:
		interval = prompts[prompts.index("-interval") + 1]
	elif function == " INTRADAY" and "-interval" not in prompts:
		raise ValueError("No interval for INTRADAY data provided. Please try again.")
	# Runs the code
	fetch_symbol(symbol, apiKey, function=function, folderPath=folderPath, writeFile=True, interval=interval)
	# Closing output
	print("Download complete. Have a nice day!")
	return 0

if __name__ == "__main__":
	main()