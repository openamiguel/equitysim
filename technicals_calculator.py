## This code contains a bunch of code for technical indicators.
## Author: Miguel Opeña
## Version: 1.3.0

import pandas as pd

import plotter
import single_download

def aroon(tick_data, numPeriods=25):
	"""	Computes the Aroon indicator of an asset over time. 
		This code assumes that number of periods refers to the number of periods for which data is provided, not the number of actual time periods.
		Inputs: dataframe with opening price, closing price, high price, low price over given timespan;
			also includes number of periods to perform calculation
		Outputs: dataframes with AroonUp and AroonDown over time
	"""
	# Assume that input is dataframe
	aroon_up = pd.DataFrame(index=tick_data.index, columns=['aroon_up'])
	aroon_down = pd.DataFrame(index=tick_data.index, columns=['aroon_down'])
	# Iterates through all datewindows
	for i in range(0, len(tick_data.index) + 1 - numPeriods):
		# Gets the proper tick date window
		start_date = tick_data.index[i]
		end_date = tick_data.index[i + numPeriods - 1]
		tick_data_window = tick_data[start_date:end_date]
		# Gets the recent maximum and minimum relative to the date window
		max_index = tick_data_window.close.idxmax()
		min_index = tick_data_window.close.idxmin()
		# Gets number of periods since previous extremum
		max_dist = len(tick_data[max_index:end_date]) - 1
		min_dist = len(tick_data[min_index:end_date]) - 1
		# Populates the output dataframes
		aroon_up.aroon_up[end_date] = 100 * (numPeriods - max_dist) / numPeriods
		aroon_down.aroon_down[end_date] = 100 * (numPeriods - min_dist) / numPeriods
	return aroon_up, aroon_down

def aroon_oscillator(tick_data, numPeriods=25):
	"""	Computes the Aroon oscillator of an asset over time, which is simply AroonUp minus AroonDown
		Inputs: dataframe with opening price, closing price, high price, low price over given timespan;
			also includes number of periods to perform calculation
		Outputs: dataframe with Aroon oscillator over time
	"""
	# Gets AroonUp and AroonDown from the aroon function
	aroon_up, aroon_down = aroon(tick_data, numPeriods=numPeriods)
	aroon_up.columns = ['aroon']
	aroon_down.columns = ['aroon']
	# Initializes and populates output
	aroon_osc = pd.DataFrame(index=tick_data.index, columns=['aroon_oscillator'])
	aroon_osc = aroon_up.subtract(aroon_down,axis=1)
	# Returns Aroon oscillator
	return aroon_osc

def average_price(tick_data):
	"""	Computes the average price of an asset over time. 
		Inputs: dataframe with opening price, closing price, high price, low price over given timespan
		Outputs: average price over given timespan
	"""
	# Assume that input is dataframe
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
	startDate = "2018-01-02"
	endDate = "2018-06-01"
	tickData = single_download.fetch_symbol_from_drive(symbol, function=function, folderPath=folderPath, interval=interval)
	tickData = tickData[startDate:endDate]
	trend = aroon_oscillator(tickData)
	price_with_trends = pd.concat([tickData.close, trend])
	price_with_trends.columns = ["price","trend"]
	plotter.price_plot(price_with_trends, symbol, folderPath, names=["price","aroon","NA"], savePlot=True, showPlot=True)