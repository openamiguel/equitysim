## General program to add metadata to the Financials JSON files.
## Author: Miguel Opeña
## Version: 1.0.6

from datetime import datetime
import logging
import pandas as pd

import io_support

FORMAT = '%(asctime)-15s %(user)-8s %(levelname)s:%(message)s'
logging.basicConfig(filename='/Users/openamiguel/Desktop/LOG/example.log', level=logging.DEBUG, format=FORMAT)
logger = logging.getLogger(__name__)
logger.info("----------INITIALIZING NEW RUN OF {}----------".format(__name__))

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
	for idx in table.index:
		this_symbol = table.symbol[idx]
		if this_symbol not in current_symbols: continue
		# Saves date effective and ratio
		this_date_effective = table.date[idx]
		this_ratio = table.ratio[idx]
		# Saves date that data was retrieved
		this_date_retrieved = datetime.now().strftime("%Y-%m-%d %H:%M")
		json_row = "{{\"stock_split\":{{\"date_effective\":\"{}\",\"ratio\":\"{}\",\"datetime_retrieved\":\"{}\",\"data_source\":\"{}\"}}}}".format(this_date_effective, this_ratio, this_date_retrieved, datasource)
		logger.info("Row to be added to stock symbol %s file: %s", this_symbol, json_row)
		## TODO: insert code to add json_row to file
	return table

tab = stock_split("/Users/openamiguel/Documents/EQUITIES/stockDaily")