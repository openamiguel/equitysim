## This code models assorted strategies and returns a dataframe of trades.
## -1 corresponds to sell short, 0 to hold, 1 to buy long, and 'X' to clear all positions
## Author: Miguel Opeña
## Version: 1.1.2

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import single_download
import technicals_calculator

def crossover(trend_baseline, switch=False):
	"""	Simulates a crossover strategy for a trend and baseline. 
		Sells if trend crosses down below baseline, buys if trend crosses up above baseline. 
		Inputs: trend and baseline data (price data unnecessary for this function), command to switch buy/sell signals
		Outputs: dataframe of timestamp index and trade signals
	"""
	# Saves timestamp to give the portfolio output an index
	timestamp = trend_baseline.index
	# Initializes the portfolio positions dataframe
	trades = pd.DataFrame(0, index=timestamp, columns=['trades'])
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
			trades[date] = 1
		# Sells short if trend crosses above baseline
		elif current_trend > current_base and not was_greater:
			logger.debug('Date:{}\tSHORT position added.'.format(date))
			was_greater = not was_greater
			# -1 is the code for short positions
			trades[date] = -1
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
	trades = pd.DataFrame(0, index=timestamp, columns=['trades'])
	# Initialize the z-score data
	zscore_running = (trend_baseline.trend - trend_baseline.baseline) / trend_baseline.trend.std()
	print(zscore_running)
	# Start iterating through the trend-baseline dataframe
	for date in timestamp:
		current_trend = trend_baseline.trend[date]
		current_base = trend_baseline.baseline[date]
		current_zscore = zscore_running[date]
		# Buys long if trend crosses below baseline
		if current_zscore < zscores[0]:
			logger.debug('Date:{}\tLONG position added.'.format(date))
			# 1 is the code for long positions
			trades[date] = 1
		# Sells short if trend crosses above baseline
		elif current_zscore > zscores[-1]: 
			logger.debug('Date:{}\tSHORT position added.'.format(date))
			# 1 is the code for long positions
			trades[date] = -1
		# Clears positions if trend is too close to baseline
		elif abs(current_zscore) < zscores[1]:
			logger.debug('Date:{}\tCLEAR positions.'.format(date))
			trades[date] = 2
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
	print(symbol)
	folder_path="C:/Users/Miguel/Documents/EQUITIES/stockDaily"
	print(folder)
	tick_data = single_download.fetch_symbol_from_drive(symbol, folderPath=folder_path)
	trend = technicals_calculator.exponential_moving_average(tick_data.close, num_periods=30)
	baseline = technicals_calculator.exponential_moving_average(tick_data.close, num_periods=90)
	trend_baseline = pd.concat([trend, baseline], axis=1)
	trend_baseline.columns = ['trend','baseline']
	trades = zscore_distance(trend_baseline)
	print(trades)

if __name__ == "__main__":
	main()