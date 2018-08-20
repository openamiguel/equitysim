## General program to add metadata to the Financials JSON files.
## Author: Miguel Opeña
## Version: 1.0.7

from datetime import datetime
import logging
import os
import pandas as pd

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

def date_transform(date, delim='/'):
	""" Transforms a date string into another format. Warning: currently hardcoded.
        Inputs: date string, delimiter for date string
        Outputs: reformatted date
	"""
	date_split = date.split(delim)
	return '-'.join([date_split[2], date_split[0], date_split[1]])

def stock_split(folderpath, link="http://eoddata.com/splits.aspx", datasource="EOD_Data"):
	""" Saves stock split data from EOD Data to a row for the Financials JSON files.
        Inputs: folder path to look for currently-downloaded (daily) symbols; link to data source, name thereof
        Outputs: table of relevant stock split data
	"""
	# Reads data from link
	data = pd.read_html(link)
	# Hardcoded for the default link (no other choice?)
	table = data[2]
	table.columns = ['exchange', 'symbol', 'date', 'ratio']
	table.drop(labels=0, axis=0, inplace=True)
	# Keeps the large-cap stocks (these are the only ones I have as of Jul 15, 2018)
	table = table[(table.exchange == "NASDAQ") | (table.exchange == "NYSE")]
	# Transforms the date and ratio columns
	table.date = table.date.apply(date_transform)
	table.ratio = table.ratio.apply(lambda x: " to ".join(z for z in x.split('-')) if '-' in x else x)
	# Gets current symbols in given folder
	current_symbols = io_support.get_current_symbols(folderpath, keyword="DAILY", datatype="csv")
	# Iterates through table and adds metadata if needed
	logger.debug("List of symbols: %s", str(table.symbol))
	for idx in table.index:
		this_symbol = table.symbol[idx]
		if this_symbol not rrin current_symbols: continue
		# Saves date effective and ratio
		this_date_effective = table.date[idx]
		this_ratio = table.ratio[idx]
		# Saves date that data was retrieved
		this_date_retrieved = datetime.now().strftime("%Y-%m-%d %H:%M")
		json_row = "{{\"stock_split\":{{\"date_effective\":\"{}\",\"ratio\":\"{}\",\"datetime_retrieved\":\"{}\",\"data_source\":\"{}\"}}}}".format(this_date_effective, this_ratio, this_date_retrieved, datasource)
		logger.info("Row to be added to stock symbol %s file: %s", this_symbol, json_row)
		logger.debug("Current JSON row: %s", str(json_row))
		# Look for the financials JSON file
		outpath = folderpath + "/Financials/{}_Financials.json".format(this_symbol)
		logger.info("Accessing Financal JSON file: %s", outpath)
		# Opens the file to run it
		outfile = open(outpath, 'r')
		lines = outfile.readlines()
		outfile.close()
		outfile_write = open(outpath, 'w')
		for rownum, line in enumerate(lines):
			# Writes the additional metadata after the second line
			if rownum == 1:
				outfile_write.write(json_row)
			outfile_write.write(line)
		outfile_write.close()
	return table

tab = stock_split("/Users/openamiguel/Documents/EQUITIES/stockDaily")
