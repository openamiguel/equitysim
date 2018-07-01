## This code models assorted strategies and returns a dataframe of trades.
## -1 corresponds to sell short, 0 to hold, 1 to buy long, and 'X' to clear all positions
## Author: Miguel Opeña
## Version: 1.2.3

import logging
import pandas as pd

import single_download
import technicals_calculator


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def hold_clear(trend_baseline, switch=False):
	"""	Simulates a very basic strategy: 
		Inputs: trend and baseline data, order to switch start from long to short
	"""
	timestamp = trend_baseline.index
	# Initializes the portfolio trades dataframe
	trades = pd.DataFrame(0, index=timestamp, columns=['all_trades'])
	# Gets the second date in the input data and fills it with long/short
	second_date = timestamp[1]
	trades.all_trades[second_date] = -1 if switch else 1
	# Gets the last date in the input data and fills it with clear
	last_date = timestamp[-1]
	trades.all_trades[last_date] = 'X'
	return trades

def crossover(trend_baseline, switch=False):
	"""	Simulates a crossover strategy for a trend and baseline. 
		Sells if trend crosses down below baseline, buys if trend crosses up above baseline. 
		Inputs: trend and baseline data (price data unnecessary for this function), command to switch buy/sell signals
		Outputs: dataframe of timestamp index and trade signals
	"""
	# Saves timestamp to give the portfolio output an index
	timestamp = trend_baseline.index
	# Saves start date as variable
	start_date = timestamp[0]
	# Initializes the portfolio trades dataframe
	trades = pd.DataFrame(0, index=timestamp, columns=['all_trades'])
	# Initialize boolean check variable
	was_greater = (trend_baseline.trend[start_date] > trend_baseline.baseline[start_date])
	# Start iterating through the trend-baseline dataframe
	for date in timestamp:
		current_trend = trend_baseline.trend[date]
		current_base = trend_baseline.baseline[date]
		# Buys long if trend crosses below baseline
		if current_trend < current_base and was_greater: 
			logger.debug('Date:{}\tLONG position added.'.format(date))
			was_greater = not was_greater
			# 1 is the code for long positions
			trades.all_trades[date] = 1
		# Sells short if trend crosses above baseline
		elif current_trend > current_base and not was_greater:
			logger.debug('Date:{}\tSHORT position added.'.format(date))
			was_greater = not was_greater
			# -1 is the code for short positions
			trades.all_trades[date] = -1
		# Otherwise, hold all positions
		else:
			logger.debug('Date:{}\tAll positions held.'.format(date))
			continue
	# If prompted to switch, the long and short positions are safely switched
	if switch:
		trades.replace(-1, 7, inplace=True)
		trades.replace(1, -1, inplace=True)
		trades.replace(7, 1, inplace=True)
	return trades

def zscore_distance(trend_baseline, zscores=[-1,0.5,1], switch=False):
	"""	Simulates a zscore proximity strategy for a trend and baseline. 
		Sells if trend is too far above baseline, buys if trend is too far below baseline, unloads if insufficient distance. 
		Inputs: price data with trend and baseline, list of z-scores to use as buy, sell, and clear signals, command to switch buy/sell signals
		Outputs: dataframe of timestamp index and trade signals
	"""
	# Saves timestamp to give the portfolio output an index
	timestamp = trend_baseline.index
	# Initializes the portfolio positions dataframe
	trades = pd.DataFrame(0, index=timestamp, columns=['all_trades'])
	# Initialize the z-score data
	zscore_running = (trend_baseline.trend - trend_baseline.baseline) / trend_baseline.trend.std()
	# Start iterating through the trend-baseline dataframe
	for date in timestamp:
		current_trend = trend_baseline.trend[date]
		current_base = trend_baseline.baseline[date]
		current_zscore = zscore_running[date]
		# Buys long if trend crosses below baseline
		if current_zscore < zscores[0]:
			logger.debug('Date:{}\tLONG position added.'.format(date))
			# 1 is the code for long positions
			trades.all_trades[date] = 1
		# Sells short if trend crosses above baseline
		elif current_zscore > zscores[-1]: 
			logger.debug('Date:{}\tSHORT position added.'.format(date))
			# -1 is the code for short positions
			trades.all_trades[date] = -1
		# Clears positions if trend is too close to baseline
		elif abs(current_zscore) < zscores[1]:
			logger.debug('Date:{}\tCLEAR positions.'.format(date))
			# 'X' is the code to clear positions
			trades.all_trades[date] = 'X'
		# Otherwise, hold all positions
		else:
			logger.debug('Date:{}\tAll positions held.'.format(date))
			continue
	# If prompted to switch, the long and short positions are safely switched
	if switch:
		trades.replace(-1, 7, inplace=True)
		trades.replace(1, -1, inplace=True)
		trades.replace(7, 1, inplace=True)
	return trades

def main():
	symbol="AAPL"
	folder_path="C:/Users/Miguel/Documents/EQUITIES/stockDaily"
	start_date = "2014-01-01"
	end_date = "2018-06-28"
	tick_data = single_download.fetch_symbol_from_drive(symbol, folderPath=folder_path)
	tick_data =tick_data[start_date:end_date]
	trend = technicals_calculator.exponential_moving_average(tick_data.close, num_periods=30)
	baseline = technicals_calculator.exponential_moving_average(tick_data.close, num_periods=90)
	trend_baseline = pd.concat([trend, baseline], axis=1)
	trend_baseline.columns = ['trend','baseline']
	trades = crossover(trend_baseline)
	print(trades)

if __name__ == "__main__":
	main()