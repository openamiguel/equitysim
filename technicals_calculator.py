## This code contains a bunch of code for technical indicators.
## Author: Miguel Opeña
## Version: 1.2.0

import pandas as pd

def average_price(open_price, close_price, high_price, low_price, asNumeric=False):
	"""	Computes the average price of an asset over time. 
		Inputs: dataframes of opening price, closing price, high price, low price over given timespan
			These can be taken as lists, dataframes, or numbers
		Outputs: average price over given timespan
	"""
	# If inputs are designated numeric:
	if asNumeric: return (open_price + close_price + high_price + low_price) / 4.0
	# Otherwise, assume that inputs are dataframes, and that all four dataframes have same index
	avg_price = pd.DataFrame(index=close_price.index, columns=['average_price'])
	# Adds up the prices into avg_price
	prices = [open_price, close_price, high_price, low_price]
	for price in prices:
		price.columns = ['average_price']
		avg_price = outDf.add(price, fill_value=0)
	# Divides by four
	avg_price = avg_price.divide(4, fill_value=0)
	return avg_price

def simple_moving_average(inputValues, numPeriods=30):
	"""	Computes the simple moving average (SMA) of a time series over certain timespan.
		Inputs: input values, number of periods in SMA
		Outputs: SMA over given timespan
	"""
	# Computes the rolling mean (default: 30-day and 90-day)
	sma = inputValues.rolling(numPeriods).mean()
	sma.columns = ['SMA' + str(numPeriods)]
	return sma