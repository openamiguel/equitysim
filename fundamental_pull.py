## From the downloaded JSON files, this code pulls data on specific tags,
## which are then compiled into a report about the company's performance.
## Part of the fundamental analysis.
## Author: Miguel Opeña
## Version: 1.1.3

import logging
import os
import pandas as pd

import download

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

def get_tags_in_file(filepath):
	""" Fetches a list of all unique tags in a given JSON file of EDGAR data.
		Inputs: file path of JSON file
		Outputs: list of unique tags in said file
	"""
	# Opens the EDGAR JSON at the given filepath
	jsonfile = open(filepath, 'r')
	# Stores unique tags
	tag_uniques = []
	# Reads line-by-line for tags
	for line in jsonfile.readlines():
		# Skips metadata and accession number lines
		if "line" not in line:
			continue
		# Hardcodes the tag location
		this_tag = line.split('\"')[5]
		if this_tag not in tag_uniques:
			tag_uniques.append(this_tag)
	tag_uniques.sort()
	return tag_uniques

def get_tag_data(filepath, tags, quarters=1, datatype="monetary", to_write=False, to_print=False):
	""" Fetches a list of all data from EDGAR JSON, relevant to a specific tag.
		Inputs: file path of JSON file, chosen tag
		Outputs: data on the chosen tag
	"""
	# Assembles outpiut dataframe
	tag_df = pd.DataFrame(columns = ['end_date_rounded', 'value'])
	# Opens the Financial JSON at the given filepath
	jsonfile = open(filepath, 'r')
	taglist = [tags] if type(tags) is str else tags
	if to_write: outfile = open(filepath.replace('.json', '_{}_Report.json'.format(taglist[0])), 'w+')
	# Reads line-by-line for tags
	for line in jsonfile.readlines():
		if datatype != "" and "\"datatype\":\"{}\"".format(datatype) not in line: 
			continue
		# Reads lines with tag information only
		if any([tag in line for tag in taglist]):
			tag_data = line.replace("{\"end_date_rounded\"", "\n{\"end_date_rounded\"")
			tag_split = tag_data.split('\n')
			for entry in tag_split:
				# Checks if the number of quarters is correct
				if "\"num_quarters\":{0:.1f}".format(quarters) in entry:
					# Isolates the value and date of interest
					this_date = entry.split(',')[0].split(':')[1][1:-1]
					this_val = entry.split(',')[3].split(':')[1][1:-1]
					this_val = this_val.replace('}]', '')
					tag_df = tag_df.append({'end_date_rounded':this_date, 'value':float(this_val)}, ignore_index=True)
			if to_print: print(tag_data)
			if to_write: outfile.write(tag_data)
	if to_write: outfile.close()
	# Before sorting, the last values for each timestamp should be more recent
	tag_df.drop_duplicates(subset=['end_date_rounded'], keep='last', inplace=True)
	tag_df.set_index('end_date_rounded', inplace=True)
	tag_df.sort_index(inplace=True)
	# Warn the user if a dataframe is empty
	if tag_df.empty:
		logger.warning("Warning: the following tags were not found in this file: {}".format(str(taglist)))
	return tag_df

def main():
	symbol = "AAPL"
	stockpath = "/Users/openamiguel/Documents/EQUITIES/stockDaily"
	tick_data = download.load_single_drive(symbol, folderpath=stockpath)
	stock_price = pd.DataFrame(tick_data.close)
	inpath = "/Users/openamiguel/Documents/EQUITIES/stockDaily/Financials/{}_Financials.json".format(symbol)
	# print(get_tags_in_file(inpath))
	net_sales = get_tag_data(inpath, "SalesRevenueNet")
	operating_expenses = get_tag_data(inpath, "OperatingExpenses")
	interest = get_tag_data(inpath, "InterestPaid")
	dividend = get_tag_data(inpath, "Dividend", datatype="perShare")
	tax = get_tag_data(inpath, "IncomeTaxesPaidNet")
	assets = get_tag_data(inpath, "Assets")
	gross_profit = get_tag_data(inpath, "GrossProfit")
	cogs = get_tag_data(inpath, ["CostOfGoodsSold", "CostOfGoodsAndServicesSold"])
	eps_basic = get_tag_data(inpath, "EarningsPerShareBasic", datatype="perShare")
	eps_diluted = get_tag_data(inpath, "EarningsPerShareDiluted", datatype="perShare")
	operating_income = net_sales - operating_expenses
	gross_income = net_sales - cogs
	net_income = gross_income - interest - tax
	gross_sales = net_sales + cogs + operating_expenses + tax
	payout_ratio = dividend / eps_basic
	price_earnings = pd.concat([stock_price, eps_diluted], axis=1)
	# price_earnings.value = price_earnings.value.fillna(method='ffill')
	price_earnings.dropna(how='any', axis=0, inplace=True)
	print(price_earnings)

if __name__ == "__main__":
	main()