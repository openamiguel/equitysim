## This code contains a bunch of code for technical indicators.
## Author: Miguel Opeña
## Version: 1.13.1

import numpy as np
import pandas as pd

import plotter
import single_download

def aroon(tick_data, num_periods=25):
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
	for i in range(0, len(tick_data.index) + 1 - num_periods):
		# Gets the proper tick date window
		start_date = tick_data.index[i]
		end_date = tick_data.index[i + num_periods - 1]
		tick_data_window = tick_data[start_date:end_date]
		# Gets the recent maximum and minimum relative to the date window
		max_index = tick_data_window.close.idxmax()
		min_index = tick_data_window.close.idxmin()
		# Gets number of periods since previous extremum
		max_dist = len(tick_data[max_index:end_date]) - 1
		min_dist = len(tick_data[min_index:end_date]) - 1
		# Populates the output dataframes
		aroon_up.aroon_up[end_date] = 100 * (num_periods - max_dist) / num_periods
		aroon_down.aroon_down[end_date] = 100 * (num_periods - min_dist) / num_periods
	return aroon_up, aroon_down

def aroon_oscillator(tick_data, num_periods=25):
	"""	Computes the Aroon oscillator of an asset over time, which is simply AroonUp minus AroonDown
		Inputs: dataframe with opening price, closing price, high price, low price over given timespan;
			also includes number of periods to perform calculation
		Outputs: dataframe with Aroon oscillator over time
	"""
	# Gets AroonUp and AroonDown from the aroon function
	aroon_up, aroon_down = aroon(tick_data, num_periods=num_periods)
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

def dema(input_values, num_periods=30):
	"""	Computes the so-called double exponential moving average (DEMA) of a time series over certain timespan.
		Inputs: input values, number of periods in DEMA
		Outputs: DEMA over given timespan
	"""
	# If input is Series, output is Dataframe
	if isinstance(input_values, pd.Series):
		ema = exponential_moving_average(input_values, num_periods=num_periods)
		ema2 = exponential_moving_average(ema.EMA, num_periods=num_periods)
		dema = pd.DataFrame(index=input_values.index, columns=['DEMA'])
		# This is the formula for DEMA
		for i in range(0, len(input_values.index)):
			dema.DEMA[i] = 2 * ema.EMA[i] - ema2.EMA[i]
		return dema
	# If input is list, output is list
	elif isinstance(input_values, list):
		ema = np.array(exponential_moving_average(input_values, num_periods=num_periods))
		ema2 = np.array(exponential_moving_average(exponential_moving_average(input_values, num_periods=num_periods), num_periods=num_periods))
		# This is the formula for DEMA
		dema = 2 * ema - ema2
		return dema.tolist()
	else:
		raise ValueError("Unsupported data type given as input to dema in technicals_calculator.py")
		return None

def ease_of_movt(tick_data, constant=1000000000):
	"""	Computes the ease of movement indicator (EMV). The constant is set to 1e+9 for plotting purposes. 
		Inputs: dataframe with high price, low price, and volume over given timespan; constant in the box ratio calculation
		Outputs: EMV over given timespan
	"""
	# Initializes empty dataframe to hold EMV values
	emv = pd.DataFrame(index=tick_data.index, columns=['EMV'])
	for i in range(1, len(tick_data.index)):
		# Calculates the midpoint move and box ratio at current time
		midpoint_move = (tick_data.high[i] - tick_data.low[i] - (tick_data.high[i-1] - tick_data.low[i-1])) / 2
		box_ratio = (tick_data.volume[i] / constant) / (tick_data.high[i] - tick_data.low[i])
		# Calculates EMV from the previous variables
		emv.EMV[i] = midpoint_move / box_ratio
	return emv

def exponential_moving_average(input_values, num_periods=30):
	"""	Computes the exponential moving average (EMA) of a time series over certain timespan.
		Inputs: input values, number of periods in EMA
		Outputs: EMA over given timespan
	"""
	K = 2 / (num_periods + 1)
	# If input is Series, output is Dataframe
	if isinstance(input_values, pd.Series):
		ema = pd.DataFrame(index=input_values.index, columns=['EMA'])
		input_values.dropna(axis=0, inplace=True)
		input_values.rename('EMA', inplace=True)
		ema.EMA = input_values[0]
		# Iterates through and populates dataframe output
		for i in range(1, len(input_values.index)):
			ema.EMA[i] = ema.EMA[i-1] + K * (input_values[i] - ema.EMA[i-1])
		return ema
	# If input is list, output is list
	elif isinstance(input_values, list):
		ema = [input_values[0]]
		# Iterates through and populates list output
		for i in range(1, len(input_values)):
			ema.append(ema[i-1] + K * (input_values[i] - ema[i-1]))
		return ema
	else:
		raise ValueError("Unsupported data type given as input to exponential_moving_average in technicals_calculator.py")
		return None

def general_stochastic(tick_data, num_periods):
	"""	Computes the General Stochastic calculation of an asset over time (assumes use of closing price).
		Inputs: dataframe with closing price over given timespan
		Outputs: General Stochastic over given timespan
	"""
	# Assume that input is dataframe
	general_stoch = pd.DataFrame(index=tick_data.index, columns=['general_stochastic'])
	# Iterates through all datewindows
	for i in range(0, len(tick_data.index) + 1 - num_periods):
		# Gets the proper tick date window
		start_date = tick_data.index[i]
		end_date = tick_data.index[i + num_periods - 1]
		tick_data_window = tick_data[start_date:end_date]
		# Gets the recent maximum and minimum relative to the date window
		max_price = tick_data_window.close.max()
		min_price = tick_data_window.close.min()
		# Populates the output dataframes
		general_stoch.general_stochastic[end_date] = (tick_data.close[end_date] - min_price) / (max_price - min_price)
	return general_stoch

def macd(price):
	"""	Computes the MACD of a time series over certain timespan, which is essentially price oscillator for 26 and 12 periods, with EMA. 
		Inputs: price input
		Outputs: MACD over given timespan
	"""
	return price_oscillator(exponential_moving_average, price, num_periods_slow=26, num_periods_fast=12)

def median_price(tick_data):
	"""	Computes the median price of an asset over time. 
		Inputs: dataframe with high and low price over given timespan
		Outputs: median price over given timespan
	"""
	# Assume that input is dataframe
	med_price = pd.DataFrame(index=tick_data.index, columns=['median_price'])
	# Adds up the prices into med_price
	med_price['median_price'] = tick_data.high + tick_data.low
	# Divides by two
	med_price = med_price.divide(2)
	return med_price

def price_channel(price, num_periods):
	"""	Computes the price channels (recent maximum and minimum) of an asset over time.
		Inputs: Series of price over given timespan
		Outputs: high channel and low channel over given timespan
	"""
	# Assume that input is dataframe
	hichannel = pd.DataFrame(index=price.index, columns=['high_channel'])
	lochannel = pd.DataFrame(index=price.index, columns=['low_channel'])
	# Iterates through all datewindows
	for i in range(0, len(price.index) + 1 - num_periods):
		# Gets the proper tick date window
		start_date = price.index[i]
		end_date = price.index[i + num_periods - 1]
		price_window = price[start_date:end_date]
		# Gets the recent maximum and minimum relative to the date window
		max_price = price_window.max()
		min_price = price_window.min()
		# Populates the output dataframes
		hichannel.high_channel[end_date] = max_price
		lochannel.low_channel[end_date] = min_price
	return hichannel, lochannel

def price_oscillator(moving_avg_function, price, num_periods_slow, num_periods_fast):
	"""	Computes the price oscillator of a time series over certain timespan, which depends on a choice of moving average function.
		Inputs: choice of function, price input, number of periods for slow MA, number of periods for fast MA
		Outputs: price oscillator over given timespan
	"""
	price_osc = moving_avg_function(price, num_periods_slow) - moving_avg_function(price, num_periods_fast)
	price_osc_percent = 100 * price_osc / moving_avg_function(price, num_periods_fast)
	return price_osc, price_osc_percent

def qstick(moving_avg_function, tick_data):
	"""	Computes the Q-stick indicator of asset data over certain timespan, which depends on a choice of moving average function.
		Inputs: choice of function, dataframe with close and open price over time
		Outputs: price oscillator over given timespan
	"""
	return moving_avg_function(tick_data.close - tick_data.open)

def simple_moving_average(input_values, num_periods=30):
	"""	Computes the simple moving average (SMA) of a time series over certain timespan.
		Inputs: input values, number of periods in SMA
		Outputs: SMA over given timespan
	"""
	# Computes the rolling mean (default: 30-day and 90-day)
	sma = input_values.rolling(num_periods).mean()
	sma.columns = ['SMA' + str(num_periods)]
	return sma

def triangular_moving_average(input_values, num_periods=30):
	"""	Computes the triangular moving average (TMA) of a time series over certain timespan, which weighs the middle values more.
		Inputs: input values, number of periods in TMA
		Outputs: TMA over given timespan
	"""
	periods = num_periods if num_periods % 2 == 0 else num_periods + 1
	per1 = int(periods / 2 + 1)
	tma = simple_moving_average(input_values, num_periods=per1)
	per2 = per1 - 1
	tma = simple_moving_average(tma, num_periods=per2)
	return tma

def typical_price(tick_data):
	"""	Computes the typical price of an asset over time. 
		Inputs: dataframe with closing price, high price, low price over given timespan
		Outputs: average price over given timespan
	"""
	# Assume that input is dataframe
	typ_price = pd.DataFrame(index=tick_data.index, columns=['typical_price'])
	# Adds up the prices into typ_price
	typ_price['typical_price'] = tick_data.close + tick_data.high + tick_data.low
	# Divides by four
	typ_price = typ_price.divide(3)
	return typ_price

if __name__ == "__main__":
	symbol = "MSFT"
	function = "DAILY"
	interval = ""
	folderPath = "C:/Users/Miguel/Documents/EQUITIES/stockDaily"
	startDate = "2014-01-02"
	endDate = "2018-06-01"
	tickData = single_download.fetch_symbol_from_drive(symbol, function=function, folderPath=folderPath, interval=interval)
	tickData = tickData[startDate:endDate]
	trend = qstick(exponential_moving_average, tickData)
	price_with_trends = pd.concat([tickData.close, trend], axis=1)
	# print(price_with_trends)
	price_with_trends.columns = ["price","trend"]
	plotter.price_plot(price_with_trends, symbol, folderPath, names=["NA","q-stick","NA"], savePlot=True, showPlot=True)