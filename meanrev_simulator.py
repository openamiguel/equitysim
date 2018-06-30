## This code models two strategies: a crossover and a zscore distance. Both rely on mean reversion principles.
## Author: Miguel Opeña
## Version: 3.2.7

import pandas as pd
import sys

import plotter
import return_calculator
import single_download
import technicals_calculator

def crossover(price_with_trends, start_date, end_date, startvalue=1000, numtrades=1, switch=False):
	"""	Simulates a crossover strategy for a trend and baseline. 
		Sells if trend crosses down below baseline, buys if trend crosses up above baseline. 
		Inputs: price data with trend and baseline, start date for price window, end date for price window,  
			starting value of portfolio, the number of trades in each order, command to switch buy/sell signals
		Outputs: dataframe of timestamp index and price, dates to go long, dates to go short
	"""
	# Saves timestamp to give the portfolio output an index
	price_with_trends_window = price_with_trends[start_date:end_date]
	timestamp = price_with_trends_window.index
	previous_date = start_date
	# Iniitalize lists of buy long and sell short dates
	long_dates = []
	short_dates = []
	# Initialize portfolio with zero positions
	numPositions = 0
	portfolio = pd.DataFrame(startvalue, index=timestamp, columns=['price'])
	# Initialize boolean check variable
	isGreater = (price_with_trends_window.trend[start_date] > price_with_trends_window.baseline[start_date])
	# Portfolio value
	portfolio_value = startvalue
	# Start iterating through the price, trend, and baseline data
	for date in timestamp:
		print("The date is {0}. Current portfolio value at {1} with {2} positions held in asset.".format(date, portfolio_value, numPositions))
		# Seeds the dataframe with start value
		if date == start_date:
			continue
		current_price = price_with_trends_window.price[date]
		current_trend = price_with_trends_window.trend[date]
		current_baseline = price_with_trends_window.baseline[date]
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

def zscore_distance(price_with_trends, start_date, end_date, startvalue=1000, numtrades=1, switch=False, zscorevalues=[-1,0.5,1]):
	"""	Simulates a zscore proximity strategy for a trend and baseline. 
		Sells if trend crosses down below baseline, buys if trend crosses up above baseline, unloads if insufficient distance. 
		Inputs: price data with trend and baseline, start date for price window, end date for price window,  
			starting value of portfolio, the number of trades in each order, command to switch buy/sell signals,
			list of z-scores to use as buy, sell, and clear signals
		Outputs: dataframe of timestamp index and price, dates to go long, dates to go short
	"""
	# Saves timestamp to give the portfolio output an index
	price_with_trends_window = price_with_trends[start_date:end_date]
	timestamp = price_with_trends_window.index
	previous_date = start_date
	# Iniitalize lists of buy long and sell short dates
	long_dates = []
	short_dates = []
	# Initialize portfolio with zero positions
	numPositions = 0
	portfolio = pd.DataFrame(startvalue, index=timestamp, columns=['price'])
	# Initialize portfolio value
	portfolio_value = startvalue
	# Builds dataframe of z-scores over time using zscore formula: trend minus baseline, all divided by stdev
	stdev = price_with_trends_window.trend.std()
	zscores = pd.DataFrame(price_with_trends_window.trend)
	zscores.columns = ['baseline']
	zscores = zscores.subtract(price_with_trends_window.baseline, axis=0)
	zscores = zscores.divide(stdev)
	zscores.columns = ['zscore']
	# Iterates through every datte in the window
	for date in timestamp:
		print("The date is {0}. Current portfolio value at {1} with {2} positions held in asset.".format(date, portfolio_value, numPositions))
		if date == start_date:
			continue
		# Gets asset values at current time
		current_price = price_with_trends_window.price[date]
		current_trend = price_with_trends_window.trend[date]
		current_baseline = price_with_trends_window.baseline[date]
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
	symbol = ""
	if "-symbol" in prompts:
		symbol = prompts[prompts.index("-symbol") + 1]
	else:
		raise ValueError("No symbol provided. Please try again.")
	## Handles where the user wants to download their files. 
	# Default folder path is relevant to the author only. 
	folder_path = "C:/Users/Miguel/Documents/EQUITIES/stockDaily"
	if "-folderPath" not in prompts:
		print("Warning: the program will use default file paths, which may not be compatible on your computer.")
	else: 
		folder_path = prompts[prompts.index("-folderPath") + 1]
	## Sets up the price data from local drive
	tick_data = single_download.fetch_symbol_from_drive(symbol, folderPath=folder_path)
	trend = technicals_calculator.exponential_moving_average(tick_data.close, num_periods=30)
	baseline = technicals_calculator.exponential_moving_average(tick_data.close, num_periods=90)
	cmo = technicals_calculator.chande_momentum_oscillator(tick_data.close, num_periods=14)
	# Consolidates the price, trend, and baseline into one dataframe
	price_with_trends = pd.concat([tick_data.close, trend, baseline, cmo], axis=1)
	price_with_trends.columns = ['price','trend','baseline','CMO']
	price_with_trends.dropna(inplace=True)
	## Handles collection of the four dates
	# Gets the start date for portfolio trading
	start_date = ""
	if "-startDate" not in prompts:
		raise ValueError("No start date provided. Please try again.")
	else:
		start_date = prompts[prompts.index("-startDate") + 1]
	# Gets the end date for portfolio trading
	end_date = ""
	if "-endDate" not in prompts:
		raise ValueError("No end date provided. Please try again.")
	else:
		end_date = prompts[prompts.index("-endDate") + 1]
	## Handles which index/asset should be the baseline 
	baselineSymbol = "^GSPC"
	if "-baseline" not in prompts:
		print("Default baseline: S&P 500 index")
	else:
		baselineSymbol = prompts[prompts.index("-baseline") + 1]
	# Sets up baseline index/asset
	portfolio_baseline = single_download.fetch_symbol_from_drive(baselineSymbol, function="DAILY", folderPath=folder_path)
	portfolio_baseline = portfolio_baseline[start_date:end_date]
	## Handles whether one wants to show the plot
	showplt = ("-showPlot" in prompts)
	## Handles the file name of plot
	plotName = "STRATEGY_01"
	if "-plotName" in prompts: plotName = prompts[prompts.index("-plotName") + 1]
	## Handles the initial value of the portfolio
	start_value = 1000000
	if "-startValue" in prompts:
		start_value = float(prompts[prompts.index("-startValue") + 1])
	else:
		print("Default of ${0} will be used for portfolio start value.".format(start_value))
	## Handles how many shares for each trade
	num_shares = 1
	if "-numShares" in prompts: num_shares = int(prompts[prompts.index("-numShares") + 1])
	## Handles whether one wants to switch buy and sell signals
	to_switch = "-switch" in prompts
	## Handles choice between crossover and zscore strategy
	portfolio = None
	long_dates = []
	short_dates = []
	title = ""
	if "-crossover" in prompts: 
		portfolio, long_dates, short_dates = crossover(price_with_trends, start_date, end_date, startvalue=start_value, switch=to_switch, numtrades=num_shares)
		portfolio.columns=['close']
		title = "PORTFOLIO STRATEGY CROSSOVER"
	elif "-zscore" in prompts:
		portfolio, long_dates, short_dates = zscore_distance(price_with_trends, start_date, end_date, startvalue=start_value, switch=to_switch, numtrades=num_shares, zscorevalues=[-0.5,0.25,0.5])
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