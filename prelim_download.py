## This code can download the constituents of the S&P 500, the Dow 30, and/or the NASDAQ 100.
## Alternatively, it can download each index as one combined file of closing prices.
## Author: Miguel Opeña
## Version: 3.5.1

import datetime
import pandas as pd
import time
import sys

import command_parser
import single_download
import ticker_universe

# Delay prevents HTTP 503 errors (AlphaVantage recommends 10, but 15 works in practice)
DELAY = 15

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

def download_combined(tickerUniverse, apiKey, function="DAILY", outputSize="full", folderPath="", outputFileName="", writeFile=True, interval=""):
	""" Downloads data on given tickers as far back as possible, storing CLOSING PRICE ONLY.
		Downloads AS ONE COMBINED FILE. For separate files, see download_separate(tickers) above. 
		Includes data on index itself.

		Inputs: symbol, API key (user-specific), time series function (default: daily), 
			folder path to write files to (default: empty), output size (default: full)
			order to write file (default: yes), time interval (for intraday data only)
		Outputs: combined DataFrame with CLOSING PRICE ONLY prices of all tickers
	"""
	combinedData = pd.DataFrame()
	for symbol in tickerUniverse:
		tickData = single_download.fetch_symbol(symbol, apiKey, outputSize=outputSize, function=function, folderPath=folderPath, interval=interval)
		# Skips invalid symbol names, as determined by single_download.py
		if tickData is None:
			continue
		# Using an outer join, merges this ticker's data with the rest of combined data
		combinedData = pd.merge(combinedData, tickData[['close']], how='outer', left_index=True, right_index=True)
		print("Data merged!\n")
		# Delay prevents HTTP 503 errors
		time.sleep(DELAY)
	# Column names are replaced with the ticker names
	combinedData.columns = tickerUniverse
	# Saves ticker data to CSV, if requested
	if writeFile:
		print("Saving combined data..")
		if folderPath == "":
			raise ValueError("You did not give single_download.py a file path to write your file. Please try again.")
		else:
			writePath = folderPath + "/" + outputFileName + "_COMBINED_" + function
			if interval != "": 
				writePath = writePath + "&" + interval
			combinedData.to_csv(writePath + ".csv")
			print("Combined data successfully saved!\n")
	# Returns dataset
	return combinedData

def main():
	""" User interacts with interface through command prompt, which obtains several "input" data. 
		Here are some examples of how to run this program: 

		python prelim_download.py -tickerUniverse SNP500 -folderPath C:/Users/Miguel/Desktop/stockData -separate -apiKey <INSERT KEY> -function DAILY
			This will download separate files of daily data on S&P 500 tickers to the desired folder path.

		python prelim_download.py -tickerUniverse DOW30 -folderPath C:/Users/Miguel/Desktop/stockData -combined -apiKey <INSERT KEY> -function DAILY
			This will download a combined file of daily (closing price only) data on the Dow 30 tickers to the desired folder path. 

		python prelim_download.py -tickerUniverse NASDAQ100 -folderPath C:/Users/Miguel/Desktop/stockData -separate -apiKey <INSERT KEY> -function INTRADAY -interval 1min
			This will download separate files of intraday data (1 minute interval) on NASDAQ 100 tickers to the desired folder path. 

		Inputs: implicit through command prompt
		Outputs: 0 if everything works
	"""
	prompts = sys.argv
	## Handles which symbol the user wants to download.
	tickerUniverse, name = command_parser.get_tickerverse_from_prompts(prompts)
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
	if "-separate" in prompts:
		download_separate(tickerUniverse, apiKey, function=function, folderPath=folderPath, interval=interval)
	elif "-combined" in prompts:
		download_combined(tickerUniverse, apiKey, function=function, folderPath=folderPath, outputFileName=name, interval=interval)
	else:
		raise ValueError("Required prompt of separate or combined not found. Please try again.")
	# Closing output
	print("Download complete. Have a nice day!")
	return 0

if __name__ == "__main__":
	main()