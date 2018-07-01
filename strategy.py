## This code models assorted strategies and returns a dataframe of trades.
## -1 corresponds to sell short, 0 to hold, 1 to buy long, and 'X' to clear all positions
## Author: Miguel Opeña
## Version: 1.0.0

def crossover(trend_baseline, switch=False):
	"""	Simulates a crossover strategy for a trend and baseline. 
		Sells if trend crosses down below baseline, buys if trend crosses up above baseline. 
		Inputs: trend and baseline data (price data unnecessary for this function), command to switch buy/sell signals
		Outputs: dataframe of timestamp index and price, dates to go long, dates to go short
	"""
	# Saves timestamp to give the portfolio output an index
	timestamp = trend_baseline.index
	# Initializes the portfolio positions dataframe
	trades = pd.DataFrame(0, index=timestamp, columns['trade'])
	# Initialize boolean check variable
	was_greater = (trend_baseline.trend[start_date] > trend_baseline.baseline[start_date])
	# Start iterating through the trend-baseline dataframe
	for date in timestamp:
		current_trend = trend_baseline.trend[date]
		current_base = trend_baseline.baseline[date]
		# Sells long if trend crosses below baseline
		if current_trend < current_base and was_greater: 
			was_greater = not was_greater
			# 1 is the code for long positions
			trades[date] = 1
		# Sells short if trend crosses above baseline
		elif current_trend > current_base and not was_greater:
			was_greater = not was_greater
			# -1 is the code for short positions
			trades[date] = -1
		# Otherwise, hold all positions
		else:
			continue
	# If prompted to switch, the long and short positions are safely switched
	if switch:
		trades.replace(-1, 7, inplace=True)
		trades.replace(1, -1, inplace=True)
		trades.replace(7, 1, inplace=True)
	return trades