## This code models a very basic mean reversion strategy, using daily closing prices of one stock. 
## Author: Miguel Opeña
## Version: 3.1.3

import pandas as pd
import sys

import plotter
import return_calculator
import single_download
import technicals_calculator

# Later on: add option to switch buy/sell signals
def crossover(price_with_trends, startDate, endDate, startValue=1000, numTrades=1):
	"""	Simulates a crossover strategy for a trend and baseline. 
		Sells if trend crosses down below baseline, buys if trend crosses up above baseline. 
		Inputs: price data with trend and baseline, start date for price window, end date for price window,  
			starting value of portfolio, the number of trades in each order
		Outputs: dataframe of timestamp index and price, dates to go long, dates to go short
	"""
	# Saves timestamp to give the portfolio output an index
	price_with_trends_window = price_with_trends[startDate:endDate]
	timestamp = price_with_trends_window.index
	previous_date = startDate
	# Iniitalize lists of buy long and sell short dates
	longDates = []
	shortDates = []
	# Initialize portfolio with zero positions
	numPositions = 0
	portfolio = pd.DataFrame(startValue, index=timestamp, columns=['price'])
	# Initialize boolean check variable
	isGreater = (price_with_trends_window.trend[startDate] > price_with_trends_window.baseline[startDate])
	# Portfolio value
	portfolioVal = startValue
	# Start iterating through the price, trend, and baseline data
	for date in timestamp:
		print("The date is {0}. Current portfolio value at {1} with {2} positions held in asset.".format(date, portfolioVal, numPositions))
		# Seeds the dataframe with start value
		if date == startDate:
			continue
		current_price = price_with_trends_window.price[date]
		current_trend = price_with_trends_window.trend[date]
		current_baseline = price_with_trends_window.baseline[date]
		# Exit shorts and go long if trend crosses down below baseline
		if current_trend < current_baseline and isGreater:
			isGreater = not isGreater
			# Exit previous short positions
			portfolio.price[date] = portfolio.price[previous_date] + numPositions * current_price
			print(portfolio.price[previous_date])
			print(portfolio.price[date])
			print("Exited {0} positions in asset.".format(numPositions))
			# Reset number of positions after exit
			numPositions = 0
			# Execute long positions
			portfolio.price[date] = portfolio.price[previous_date] - numTrades * current_price
			numPositions += numTrades
			longDates.append(date)
			print("Acquired {0} LONG positions in asset.\n".format(numTrades))
		# Exit longs and go short if trend crosses up above baseline
		elif current_trend > current_baseline and not isGreater:
			isGreater = not isGreater
			# Exit previous long positions
			portfolio.price[date] = portfolio.price[previous_date] - numPositions * current_price
			print("Exited {0} positions in asset.".format(numPositions))
			# Reset number of positions after exit
			numPositions = 0
			# Execute short positions
			portfolio.price[date] = portfolio.price[previous_date] + numTrades * current_price
			numPositions -= numTrades
			shortDates.append(date)
			print("Acquired {0} SHORT positions in asset.\n".format(numTrades))
		# Otherwise, simply hold one's position
		else: 
			portfolio.price[date] = portfolio.price[previous_date]
			print("No positional movement in asset held.\n")
		previous_date = date
		portfolioVal = portfolio.price[date]
	# Return dataframe with timestamp, portfolio price over time
	return portfolio, longDates, shortDates

def zscore_distance(price_with_trends, startDate, endDate, startValue=1000, numTrades=1):
	"""	Simulates a zscore proximity strategy for a trend and baseline. 
		Sells if trend crosses down below baseline, buys if trend crosses up above baseline, unloads if insufficient distance. 
		Inputs: price data with trend and baseline, start date for price window, end date for price window,  
			starting value of portfolio, the number of trades in each order
		Outputs: dataframe of timestamp index and price, dates to go long, dates to go short
	"""
	# Saves timestamp to give the portfolio output an index
	price_with_trends_window = price_with_trends[startDate:endDate]
	timestamp = price_with_trends_window.index
	previous_date = startDate
	# Iniitalize lists of buy long and sell short dates
	longDates = []
	shortDates = []
	# Initialize portfolio with zero positions
	numPositions = 0
	portfolio = pd.DataFrame(startValue, index=timestamp, columns=['price'])
	# Initialize portfolio value
	portfolioVal = startValue
	# Builds dataframe of z-scores over time using zscore formula: trend minus baseline, all divided by stdev
	stdev = price_with_trends_window.trend.std()
	zscores = pd.DataFrame(price_with_trends_window.trend)
	zscores.columns = ['baseline']
	zscores = zscores.subtract(price_with_trends_window.baseline, axis=0)
	zscores = zscores.divide(stdev)
	zscores.columns = ['zscore']
	# Iterates through every datte in the window
	for date in timestamp:
		print("The date is {0}. Current portfolio value at {1} with {2} positions held in asset.".format(date, portfolioVal, numPositions))
		if date == startDate:
			continue
		# Gets asset values at current time
		current_price = price_with_trends_window.price[date]
		current_trend = price_with_trends_window.trend[date]
		current_baseline = price_with_trends_window.baseline[date]
		current_zscore = zscores.zscore[date]
		# We don't want to run out of funds for trading. 
		if numTrades * current_price >= portfolioVal:
			print("You have insufficient funds to continue trading.")
			break
		# Sell short if z-score > 1
		if current_zscore > 1:
			portfolio.price[date] = portfolio.price[previous_date] + current_price * numTrades
			numPositions -= numTrades
			shortDates.append(date)
			print("Acquired {0} SHORT positions in asset.\n".format(numTrades))
		# Buy long if z-score < -1
		elif current_zscore < -1: 
			portfolio.price[date] = portfolio.price[previous_date] - current_price * numTrades
			numPositions += numTrades
			longDates.append(date)
			print("Acquired {0} LONG positions in asset.\n".format(numTrades))
		# Clear positions if magnitude of z-score is too low
		elif abs(current_zscore) < 0.5:
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
		portfolioVal = portfolio.price[date]
	# Return dataframe with timestamp, portfolio price over time
	return portfolio, longDates, shortDates

def main():
	""" User interacts with program through command prompt. 
		Example prompts: 

		python meanrev_simulator.py -symbol GS -folderPath C:/Users/Miguel/Desktop/stockData -baseline ^^GSPC -startDate 2016-06-05 -endDate 2017-06-05 -plotName STRATEGY_02 -startVal 1000000 -numShares 10 -crossover -showPlot 
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
	folderPath = "C:/Users/Miguel/Documents/EQUITIES/stockDaily"
	if "-folderPath" not in prompts:
		print("Warning: the program will use default file paths, which may not be compatible on your computer.")
	else: 
		folderPath = prompts[prompts.index("-folderPath") + 1]
	## Sets up the price data from local drive
	tickData = single_download.fetch_symbol_from_drive(symbol, folderPath=folderPath)
	price = tickData.close
	trend = technicals_calculator.SMA(price, numPeriods=30)
	baseline = technicals_calculator.SMA(price, numPeriods=90)
	# Consolidates the price, trend, and baseline into one dataframe
	price_with_trends = pd.concat([price, trend, baseline], axis=1)
	price_with_trends.columns = ['price','trend','baseline']
	price_with_trends.dropna(inplace=True)
	## Handles collection of the four dates
	# Gets the start date for portfolio trading
	startDate = ""
	if "-startDate" not in prompts:
		raise ValueError("No start date provided. Please try again.")
	else:
		startDate = prompts[prompts.index("-startDate") + 1]
	# Gets the end date for portfolio trading
	endDate = ""
	if "-endDate" not in prompts:
		raise ValueError("No end date provided. Please try again.")
	else:
		endDate = prompts[prompts.index("-endDate") + 1]
	## Handles which index/asset should be the baseline 
	baselineSymbol = "^GSPC"
	if "-baseline" not in prompts:
		print("Default baseline: S&P 500 index")
	else:
		baselineSymbol = prompts[prompts.index("-baseline") + 1]
	# Sets up baseline index/asset
	portfolio_baseline = single_download.fetch_symbol_from_drive(baselineSymbol, function="DAILY", folderPath=folderPath)
	portfolio_baseline = portfolio_baseline[startDate:endDate]
	## Handles whether one wants to show the plot
	showplt = ("-showPlot" in prompts)
	## Handles the file name of plot
	plotName = "STRATEGY_01"
	if "-plotName" in prompts: plotName = prompts[prompts.index("-plotName") + 1]
	## Handles the initial value of the portfolio
	startVal = 1000000
	if "-startValue" in prompts:
		startVal = float(prompts[prompts.index("-startValue") + 1])
	else:
		print("Default of ${0} will be used for portfolio start value.".format(startVal))
	## Handles how many shares for each trade
	numShares = 1
	if "-numShares" in prompts: numShares = int(prompts[prompts.index("-numShares") + 1])
	## Handles choice between crossover and zscore strategy
	portfolio = None
	longDates = []
	shortDates = []
	if "-crossover" in prompts: 
		portfolio, longDates, shortDates = crossover(price_with_trends, startDate, endDate, startValue=startVal, numTrades=numShares)
		portfolio.columns=['close']
		plotter.price_plot(price_with_trends[startDate:endDate], symbol, folderPath, names=["price","trend","baseline"], longDates=longDates, shortDates=shortDates, savePlot=True, showPlot=showplt)
		plotter.portfolio_plot(portfolio, portfolio_baseline, folderPath=folderPath, title=symbol+"_MEAN_CROSSOVER", showPlot=showplt)
	elif "-zscore" in prompts:
		portfolio, longDates, shortDates = zscore_distance(price_with_trends, startDate, endDate, startValue=startVal, numTrades=numShares)
		portfolio.columns=['close']
		plotter.price_plot(price_with_trends[startDate:endDate], symbol, folderPath, names=["price","trend","baseline"], longDates=longDates, shortDates=shortDates, savePlot=True, showPlot=showplt)
		plotter.portfolio_plot(portfolio, portfolio_baseline, folderPath=folderPath, title=symbol+"_MEAN_ZSCORE", showPlot=showplt)
	else:
		raise ValueError("No strategy provided. Please try again.")
	startValue, endValue, returns, baseReturns = return_calculator.portfolio_valuation(portfolio, portfolio_baseline)
	# Spits out some numerical info about the portfolio performance
	print("\nStarting portfolio value: %f" % startValue)
	print("Ending portfolio value: %f" % endValue)
	print("Return on this strategy: %f" % returns)
	print("Return on S&P500 index: %f" % baseReturns)
	print("Sharpe ratio: %f" % return_calculator.sharpe_ratio(portfolio))

if __name__ == "__main__":
	main()