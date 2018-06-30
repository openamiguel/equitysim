## This code models two strategies: a crossover and a zscore distance. Both rely on mean reversion principles.
## Author: Miguel Opeña
## Version: 3.3.1

import pandas as pd
import sys

import command_parser
import plotter
import return_calculator
import single_download
import technicals_calculator

def crossover(price_with_trends, startvalue=1000, numtrades=1, switch=False):
	"""	Simulates a crossover strategy for a trend and baseline. 
		Sells if trend crosses down below baseline, buys if trend crosses up above baseline. 
		Inputs: price data with trend and baseline, starting value of portfolio, the number of trades in each order, 
			command to switch buy/sell signals
		Outputs: dataframe of timestamp index and price, dates to go long, dates to go short
	"""
	# Saves timestamp to give the portfolio output an index
	timestamp = price_with_trends.index
	previous_date = timestamp[0]
	start_date = timestamp[0]
	# Iniitalize lists of buy long and sell short dates
	long_dates = []
	short_dates = []
	# Initialize portfolio with zero positions
	numPositions = 0
	portfolio = pd.DataFrame(startvalue, index=timestamp, columns=['price'])
	# Initialize boolean check variable
	isGreater = (price_with_trends.trend[start_date] > price_with_trends.baseline[start_date])
	# Portfolio value
	portfolio_value = startvalue
	# Start iterating through the price, trend, and baseline data
	for date in timestamp:
		print("The date is {0}. Current portfolio value at {1} with {2} positions held in asset.".format(date, portfolio_value, numPositions))
		# Seeds the dataframe with start value
		if date == start_date:
			continue
		current_price = price_with_trends.price[date]
		current_trend = price_with_trends.trend[date]
		current_baseline = price_with_trends.baseline[date]
		# Establish the conditions for executing trades
		condition1 = current_trend < current_baseline and isGreater
		condition2 = current_trend > current_baseline and not isGreater
		# If prompted, switch the conditions
		if switch:
			temp = condition1
			condition1 = condition2
			condition2 = temp
		# Exit shorts and go long if trend crosses down below baseline
		if condition1:
			isGreater = not isGreater
			# Exit previous short positions
			portfolio.price[date] = portfolio.price[previous_date] + numPositions * current_price
			print(portfolio.price[previous_date])
			print(portfolio.price[date])
			print("Exited {0} positions in asset.".format(numPositions))
			# Reset number of positions after exit
			numPositions = 0
			# Execute long positions
			portfolio.price[date] = portfolio.price[previous_date] - numtrades * current_price
			numPositions += numtrades
			long_dates.append(date)
			print("Acquired {0} LONG positions in asset.\n".format(numtrades))
		# Exit longs and go short if trend crosses up above baseline
		elif condition2:
			isGreater = not isGreater
			# Exit previous long positions
			portfolio.price[date] = portfolio.price[previous_date] - numPositions * current_price
			print("Exited {0} positions in asset.".format(numPositions))
			# Reset number of positions after exit
			numPositions = 0
			# Execute short positions
			portfolio.price[date] = portfolio.price[previous_date] + numtrades * current_price
			numPositions -= numtrades
			short_dates.append(date)
			print("Acquired {0} SHORT positions in asset.\n".format(numtrades))
		# Otherwise, simply hold one's position
		else: 
			portfolio.price[date] = portfolio.price[previous_date]
			print("No positional movement in asset.\n")
		previous_date = date
		portfolio_value = portfolio.price[date]
	# Return dataframe with timestamp, portfolio price over time
	return portfolio, long_dates, short_dates

def zscore_distance(price_with_trends, startvalue=1000, numtrades=1, switch=False, zscorevalues=[-1,0.5,1]):
	"""	Simulates a zscore proximity strategy for a trend and baseline. 
		Sells if trend crosses down below baseline, buys if trend crosses up above baseline, unloads if insufficient distance. 
		Inputs: price data with trend and baseline, starting value of portfolio, the number of trades in each order, 
			command to switch buy/sell signals, list of z-scores to use as buy, sell, and clear signals
		Outputs: dataframe of timestamp index and price, dates to go long, dates to go short
	"""
	# Saves timestamp to give the portfolio output an index
	timestamp = price_with_trends.index
	previous_date = timestamp[0]
	start_date = timestamp[0]
	# Iniitalize lists of buy long and sell short dates
	long_dates = []
	short_dates = []
	# Initialize portfolio with zero positions
	numPositions = 0
	portfolio = pd.DataFrame(startvalue, index=timestamp, columns=['price'])
	# Initialize portfolio value
	portfolio_value = startvalue
	# Builds dataframe of z-scores over time using zscore formula: trend minus baseline, all divided by stdev
	stdev = price_with_trends.trend.std()
	zscores = pd.DataFrame(price_with_trends.trend)
	zscores.columns = ['baseline']
	zscores = zscores.subtract(price_with_trends.baseline, axis=0)
	zscores = zscores.divide(stdev)
	zscores.columns = ['zscore']
	# Iterates through every datte in the window
	for date in timestamp:
		print("The date is {0}. Current portfolio value at {1} with {2} positions held in asset.".format(date, portfolio_value, numPositions))
		if date == start_date:
			continue
		# Gets asset values at current time
		current_price = price_with_trends.price[date]
		current_trend = price_with_trends.trend[date]
		current_baseline = price_with_trends.baseline[date]
		current_zscore = zscores.zscore[date]
		# We don't want to run out of funds for trading. 
		if numtrades * current_price >= portfolio_value:
			print("You have insufficient funds to continue trading.")
			break
		# Establish the conditions for executing trades
		condition1 = current_zscore > zscorevalues[-1]
		condition2 = current_zscore < zscorevalues[0]
		# If prompted, switch the conditions
		if switch:
			temp = condition1
			condition1 = condition2
			condition2 = temp
		# Sell short
		if condition1:
			portfolio.price[date] = portfolio.price[previous_date] + current_price * numtrades
			numPositions -= numtrades
			short_dates.append(date)
			print("Acquired {0} SHORT positions in asset.\n".format(numtrades))
		# Buy long
		elif condition2: 
			portfolio.price[date] = portfolio.price[previous_date] - current_price * numtrades
			numPositions += numtrades
			long_dates.append(date)
			print("Acquired {0} LONG positions in asset.\n".format(numtrades))
		# Clear positions
		elif abs(current_zscore) < zscorevalues[1]:
			portfolio.price[date] = portfolio.price[previous_date] + current_price * numPositions
			# Useless to display dumping 0 positions
			if numPositions > 0:
				print("Cleared {0} positions in asset.\n".format(numPositions))
			else:
				print("No positions to clear.\n")
			numPositions = 0
		# In all other cases, hold positions
		else: 
			portfolio.price[date] = portfolio.price[previous_date]
			print("No positional movement in asset.\n")
		previous_date = date
		portfolio_value = portfolio.price[date]
	# Return dataframe with timestamp, portfolio price over time
	return portfolio, long_dates, short_dates

def main():
	""" User interacts with program through command prompt. 
		Example prompts: 

		python meanrev_simulator.py -symbol GS -folderPath C:/Users/Miguel/Desktop/stockData -baseline ^^GSPC -start_date 2016-06-05 -end_date 2017-06-05 -plotName STRATEGY_02 -startVal 1000000 -numShares 10 -crossover -showPlot 
			This will simulate a mean reversion strategy, based on simple crossover, ranking portfolio for the S&P 500 ticker universe using the S&P 500 index as baseline, with the given dates to rank and trade the portfolio. 

		Inputs: implicit through command prompt
		Outputs: 0 if everything works
	"""
	prompts = sys.argv
	## Handles which symbol the user wants to download.
	symbol = command_parser.get_generic_from_prompts(prompts, "-symbol")
	## Handles where the user wants to download their files. 
	# Default folder path is relevant to the author only. 
	folder_path = command_parser.get_generic_from_prompts(prompts, query="-folderPath", default="C:/Users/Miguel/Documents/EQUITIES/stockDaily", req=False)
	## Handles collection of the start and end dates for trading
	start_date = command_parser.get_generic_from_prompts(prompts, query="-startDate")
	end_date = command_parser.get_generic_from_prompts(prompts, query="-endDate")
	## Handles which index/asset should be the baseline 
	baselineSymbol = command_parser.get_generic_from_prompts(prompts, query="-baseline", default="^GSPC", req=False)
	## Handles the file name of plot
	plotName = command_parser.get_generic_from_prompts(prompts, query="-plotName", default="STRATEGY_01", req=False)
	## Handles the initial value of the portfolio
	start_value = command_parser.get_generic_from_prompts(prompts, query="-startValue", default=1000000, req=False)
	start_value = float(start_value)
	## Handles how many shares for each trade
	num_shares = command_parser.get_generic_from_prompts(prompts, query="-numShares", default=1, req=False)
	num_shares = int(num_shares)
	## Handles whether one wants to show the plot
	showplt = "-showPlot" in prompts
	## Handles whether one wants to switch buy and sell signals
	to_switch = "-switch" in prompts
	## Sets up the price data from local drive
	tick_data = single_download.fetch_symbol_from_drive(symbol, folderPath=folder_path)
	trend = technicals_calculator.exponential_moving_average(tick_data.close, num_periods=30)
	baseline = technicals_calculator.exponential_moving_average(tick_data.close, num_periods=90)
	cmo = technicals_calculator.chande_momentum_oscillator(tick_data.close, num_periods=14)
	# Sets up baseline index/asset
	portfolio_baseline = single_download.fetch_symbol_from_drive(baselineSymbol, function="DAILY", folderPath=folder_path)
	portfolio_baseline = portfolio_baseline[start_date:end_date]
	# Consolidates the price, trend, and baseline into one dataframe
	price_with_trends = pd.concat([tick_data.close, trend, baseline, cmo], axis=1)
	price_with_trends.columns = ['price','trend','baseline','CMO']
	price_with_trends.dropna(inplace=True)
	price_with_trends = price_with_trends[start_date:end_date]
	## Handles choice between crossover and zscore strategy
	portfolio = None
	long_dates = []
	short_dates = []
	title = ""
	if "-crossover" in prompts: 
		portfolio, long_dates, short_dates = crossover(price_with_trends, startvalue=start_value, switch=to_switch, numtrades=num_shares)
		portfolio.columns=['close']
		title = "PORTFOLIO STRATEGY CROSSOVER"
	elif "-zscore" in prompts:
		portfolio, long_dates, short_dates = zscore_distance(price_with_trends, startvalue=start_value, switch=to_switch, numtrades=num_shares, zscorevalues=[-0.5,0.25,0.5])
		portfolio.columns=['close']
		title = "PORTFOLIO STRATEGY ZSCORE"
	else:
		raise ValueError("No strategy provided. Please try again.")
	port_price = pd.concat([portfolio.close, portfolio_baseline.close], axis=1)
	port_price.columns = ['portfolio', 'baseline']
	# plotter.price_plot(price_with_trends[start_date:end_date], symbol, folderpath=folder_path, subplot=[True,True,True,False], returns=[False,False,False,False], longdates=long_dates, shortdates=short_dates, showPlot=showplt)
	plotter.price_plot(port_price, symbol=title, folderpath=folder_path, subplot=[True,True], returns=[True,True], showPlot=showplt)
	start_value, endValue, returns, baseReturns = return_calculator.portfolio_valuation(portfolio, portfolio_baseline)
	# Spits out some numerical info about the portfolio performance
	print("\nStarting portfolio value: %f" % start_value)
	print("Ending portfolio value: %f" % endValue)
	print("Return on this strategy: %f" % returns)
	print("Return on S&P500 index: %f" % baseReturns)
	print("Sharpe ratio: %f" % return_calculator.sharpe_ratio(portfolio))

if __name__ == "__main__":
	main()