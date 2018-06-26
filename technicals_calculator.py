## This code contains a bunch of code for technical indicators.
## Author: Miguel Opeña
## Version: 1.2.1

import pandas as pd

import plotter
import single_download

def average_price(tick_data):
	"""	Computes the average price of an asset over time. 
		Inputs: dataframes of opening price, closing price, high price, low price over given timespan
		Outputs: average price over given timespan
	"""
	#Assume that input is dataframe
	avg_price = pd.DataFrame(index=tick_data.index, columns=['average_price'])
	# Adds up the prices into avg_price
	avg_price['average_price'] = tick_data.open + tick_data.close + tick_data.high + tick_data.low
	# Divides by four
	avg_price = avg_price.divide(4)
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

if __name__ == "__main__":
	symbol = "MSFT"
	function = "DAILY"
	interval = ""
	folderPath = "C:/Users/Miguel/Documents/EQUITIES/stockDaily"
	startDate = "2018-01-01"
	endDate = "2018-06-01"
	tickData = single_download.fetch_symbol_from_drive(symbol, function=function, folderPath=folderPath, interval=interval)
	tickData = tickData[startDate:endDate]
	trend = average_price(tickData)
	price_with_trends = pd.concat([tickData.close, trend])
	price_with_trends.columns = ["price","trend"]
	plotter.price_plot(price_with_trends, symbol, folderPath, names=["price","average_price","NA"], savePlot=True, showPlot=True)