## This code can download the constituents of the S&P 500, the Dow 30, and/or the NASDAQ 100.
## Alternatively, it can download each index as one combined file of closing prices.
## Author: Miguel Opeña
## Version: 3.1.1

import datetime
import pandas as pd
import time
import sys

import single_download
import ticker_universe

# Delay prevents HTTP 503 errors (AlphaVantage recommends 10, but 15 works in practice)
DELAY = 11

def download_separate(tickerUniverse, apiKey, function="DAILY", outputSize="full", folderPath="", interval=""):
	""" Downloads data on given tickers as far back as possible, including opening price, closing price, and volume.
		Downloads AS SEPARATE FILES. For a combined file, see download_combined(tickers) below. 
		Includes data on index itself.

		Inputs: symbol, API key (user-specific), time series function (default: daily), output size (default: full), 
			folder path to write files to (default: empty), time interval (for intraday data only)
		Outputs: 0 if everything works
	"""
	for symbol in tickerUniverse:
		# Read each symbol and write to file (hence writeFile=True)
		single_download.fetch_symbol(symbol, apiKey, function=function, outputSize=outputSize, folderPath=folderPath, writeFile=True, interval=interval)
		# Delay prevents HTTP 503 errors
		time.sleep(DELAY)
	return 0

def download_combined(tickerUniverse, apiKey, function="DAILY", folderPath="", outputFileName="", writeFile=True, interval=""):
	""" Downloads data on given tickers as far back as possible, storing CLOSING PRICE ONLY.
		Downloads AS ONE COMBINED FILE. For separate files, see download_separate(tickers) above. 
		Includes data on index itself.

		Inputs: symbol, API key (user-specific), time series function (default: daily), 
			folder path to write files to (default: empty), order to write file (default: yes),
			time interval (for intraday data only)
		Outputs: combined DataFrame with CLOSING PRICE ONLY prices of all tickers
	"""
	combinedData = pd.DataFrame()
	for symbol in tickerUniverse:
		tickData = single_download.fetch_symbol(symbol, apiKey, function=function, folderPath=folderPath, interval=interval)
		# Using an outer join, merges this ticker's data with the rest of combined data
		combinedData = pd.merge(combinedData, tickData[['close']], how='outer', left_index=True, right_index=True)
		print("Data merged!")
		# Delay prevents HTTP 503 errors
		time.sleep(DELAY)		
	# Flips the data around (AlphaVantage presents it in reverse chronological order, but I prefer regular chronological)
	combinedData = combinedData.reindex(index=combinedData.index[::-1])
	# Column names are replaced with the ticker names
	combinedData.columns = tickerUniverse
	# Saves ticker data to CSV, if requested
	if writeFile:
		print("Saving combined data..")
		if folderPath == "":
			raise ValueError("You did not give single_download.py a file path to write your file. Please try again.")
		else:
			combinedData.to_csv(folderPath + "/AAAA_" + outputFileName + "_COMBINED_" + function + ".csv")
			print("Data on " + symbol + " successfully saved!\n")
	# Returns dataset
	return combinedData

def main():
	""" User interacts with interface through command prompt, which obtains several "input" data. 
		Here are some examples of how to run this program: 

		python prelim_download.py -tickerUniverse SNP500 -folderPath C:/Users/Miguel/Desktop/stockData -separate -apiKey <INSERT KEY> -timeSeriesFunction DAILY
			This will download separate files of daily data on S&P 500 tickers to the desired folder path.

		python prelim_download.py -tickerUniverse DOW30 -folderPath C:/Users/Miguel/Desktop/stockData -combined -apiKey <INSERT KEY> -timeSeriesFunction DAILY
			This will download a combined file of daily (closing price only) data on the Dow 30 tickers to the desired folder path. 

		python prelim_download.py -tickerUniverse NASDAQ100 -folderPath C:/Users/Miguel/Desktop/stockData -separate -apiKey <INSERT KEY> -timeSeriesFunction INTRADAY -interval 1min
			This will download separate files of intraday data (1 minute interval) on NASDAQ 100 tickers to the desired folder path. 

		Inputs: implicit through command prompt
		Outputs: 0 if everything works
	"""
	prompts = sys.argv
	## Handles which symbol the user wants to download.
	tickerUniverse = []
	name = ""
	if "-tickerUniverse" not in prompts:
		raise ValueError("No ticker universe provided. Please try again")
	# Yields data on the S&P 500
	elif "SNP500" in prompts:
		tickerUniverse = ticker_universe.obtain_parse_wiki(selection="SNP500", seed="^GSPC")
		name = "SNP500"
	# Yields data on the Dow 30
	elif "DOW30" in prompts:
		tickerUniverse = ticker_universe.obtain_parse_wiki(selection="DOW30", seed="^DJI")
		name = "DOW30"
	# Yields data on the NASDAQ 100
	elif "NASDAQ100" in prompts:
		tickerUniverse = ticker_universe.obtain_parse_nasdaq()
		name = "NASDAQ100"
	# Yields data on user-provided tickers
	else:
		tickerPath = prompts[prompts.index("-ticker") + 1]
		tickFrame = pd.read_csv(tickerPath, names=['tickers'])
		tickerUniverse = tickFrame.tickers.tolist()
		name = "CUSTOM"
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
	## Handles user choice of separate or combined
	if "-separate" in prompts:
		download_separate(tickerUniverse, apiKey, function=function, folderPath=folderPath, interval=interval)
	elif "-combined" in prompts:
		download_combined(tickerUniverse, apiKey, function=function, folderPath=folderPath, outputFileName=name, interval=interval)
	# Closing output
	print("Download complete. Have a nice day!")
	return 0

if __name__ == "__main__":
	main()