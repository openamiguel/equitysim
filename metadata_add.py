## General program to add metadata to the Financials JSON files.
## Author: Miguel Opeña
## Version: 1.0.1

import pandas as pd

def date_transform(date):
	""" Transforms a date string into another format.
        Inputs: date string, desired format (default: AlphaVantage format "YYYY-MM-DD")
        Outputs: reformatted date
	"""
	return date + "X"

def stock_split(link="http://eoddata.com/splits.aspx", datasource="EOD_Data"):
	# Reads data from link
	data = pd.read_html(link)
	# Hardcoded for the default link (no other choice?)
	table = data[2]
	table.columns = ['exchange', 'symbol', 'date', 'ratio']
	table.drop(labels=0, axis=0, inplace=True)
	# Keeps the large-cap stocks (these are the only ones I have as of Jul 15, 2018)
	table = table[(table.exchange == "NASDAQ") | (table.exchange == "NYSE")]
	# Transforms the date
	table.date = table.date.apply(date_transform)
	# Iterates through table and adds metadata if needed
	for idx in table.index:
		this_symbol = table.symbol[idx]
		
		print(this_symbol)
	return table

tab = stock_split()
print(tab.head())