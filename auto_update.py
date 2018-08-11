#!/usr/bin/python
# -*- coding: utf8 -*-

## This code can update all stock files in a given folder directory. 
## Author: Miguel Opeña
## Version: 4.2.0

import logging
import os
import pandas as pd
import sys
import time

import command_parser
from download import CDownloader

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

# Delay prevents HTTP 503 errors (AlphaVantage recommends 10, but 15 works in practice)
DELAY = 15

class CUpdater:
	def __init__(self, api_key, folderpath):
		self.api_key = api_key
		self.folderpath = folderpath
		self.delay = 15

	def get_downloader_object(self):
		""" Generates an instance of CDownloader used to update the files.
			Inputs: none
			Outputs: an instance of CDownloader
		"""
		# Assumes that the first file will be of the same function and interval as all other data
		file_name = os.listdir(self.folderpath)[0]
		name_split = file_name.split(".csv")[0].split("_")
		# Gets the function (daily, intradaily, etc.) from the file name
		filename_suffix = name_split[1] if len(name_split) == 2 else name_split[2]
		function = filename_suffix
		interval = ""
		# The suffix has an ampersand character if and only if the file is intraday
		if "&" in filename_suffix:
			function_split = filename_suffix.split("&")
			function = function_split[0]
			interval = function_split[1]
		# Save the output size
		# If the data is on a DAILY function, then compact is sufficient (100 days of data)
		output_size = "full" if function == "INTRADAY" else "compact"
		downloader = None
		if "FOREX" in self.folderpath:
			fx_format = "{}function=FX_{}&from_symbol={}&to_symbol={}&apikey={}&datatype={}&outputsize={}"
			downloader = CDownloader(self.folderpath, self.api_key, function, interval, output_size, url_format=fx_format)
		else:
			downloader = CDownloader(self.folderpath, self.api_key, function, interval, output_size)
		# Return the CDownloader instance
		return downloader

	def update_files(self, downloader):
		""" Automatically updates all equity/forex files in a given folder. 
			Inputs: downloader object initialized with function within file path
			Outputs: True if everything works
		"""
		for curpath, directories, files in os.walk(self.folderpath):
			for file in files:
				# Reads the old data from its file location
				inpath = os.path.join(curpath, file)
				old_data = pd.read_csv(inpath, index_col='timestamp')
				old_data.dropna(how='any',inplace=True)
				# Removes duplicates
				old_data = old_data[~old_data.index.duplicated(keep='first')]
				# Gets the most recent date in the old ticker data
				last_date = old_data.index[-1]
				# Parses the file name using the split function (assumes adherence to naming conventions from download.py)
				file_name = inpath.split(self.outpath)[1][1:]
				name_split = file_name.split(".csv")[0].split("_")
				# Gets a string representing the symbol 
				symbol = name_split[0] if len(name_split) == 2 else (name_split[0], name_split[1])
				logger.info("Auto-updating " + str(symbol) + " from AlphaVantage...")
				new_data = downloader.load_single(symbol, writeFile=True)
				# If unavailable, don't download
				if new_data is None:
					# Delay prevents HTTP 503 errors
					logger.info(str(symbol) + " update failed and skipped.")
					time.sleep(self.delay)
					return None
				# Isolates the data that is new (based on last date/time collected)
				# Accounts for issues if data has not been updated in a long time
				if last_date in list(new_data.index.values):
					new_data = new_data[(new_data.index == last_date).cumsum() > 0]
					new_data = new_data.drop(index=last_date)
				# Concatenate along row
				finished_output = pd.concat([old_data, new_data])
				# Writes allTickerData to chosen folder path
				finished_output.to_csv(inpath, index_label='timestamp')
				logger.info("Data on " + str(symbol) + " successfully updated!")
				# Delay prevents HTTP 503 errors
				time.sleep(self.delay)
		# Returns True if the program runs to completion
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
	folder_path = command_parser.get_generic_from_prompts(prompts, query="-folderPath", default="/Users/openamiguel/Documents/EQUITIES/stockDaily", req=False)
	## Handles the user's API key. 
	api_key = command_parser.get_generic_from_prompts(prompts, query="-apiKey")
	## Updates all files in folder
	updater = CUpdater(api_key, folder_path)
	downloader = updater.get_downloader_object()
	updater.update_files(downloader)

if __name__ == "__main__":
	main()