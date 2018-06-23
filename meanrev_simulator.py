## This code models a very basic mean reversion strategy, using daily closing prices of one stock. 
## Author: Miguel Opeña
## Version: 2.0.0

import pandas as pd
import numpy as np

import plotter
import single_download
import technicals_calculator

# Later on: add option to switch buy/sell signals
def crossover(price_with_trends, startDate, endDate, startValue=1000, numTrades=1):
	"""	Simulates a crossover strategy for a trend and baseline. 
		Sells if trend crosses down below baseline, buys if trend crosses up above baseline. 
		Inputs: price data with trend and baseline, start date for price window, end date for price window,  
			starting value of portfolio, the number of trades in each order
		Outputs: dataframe of timestamp index and price
	"""
	# Saves timestamp to give the portfolio output an index
	price_with_trends_window = price_with_trends[startDate:endDate]
	timestamp = price_with_trends_window.index
	previous_date = startDate
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
			print("Acquired {0} SHORT positions in asset.\n".format(numTrades))
		# Otherwise, simply hold one's position
		else: 
			portfolio.price[date] = portfolio.price[previous_date]
			print("No positional movement in asset held.\n")
		previous_date = date
		portfolioVal = portfolio.price[date]
	# Return dataframe with timestamp, portfolio price over time
	return portfolio

def zscore_distance(price_with_trends, startDate, endDate, startValue=1000, numTrades=1):
	"""	Simulates a zscore proximity strategy for a trend and baseline. 
		Sells if trend crosses down below baseline, buys if trend crosses up above baseline, unloads if insufficient distance. 
		Inputs: price data with trend and baseline, start date for price window, end date for price window,  
			starting value of portfolio, the number of trades in each order
		Outputs: dataframe of timestamp index and price
	"""
	# Saves timestamp to give the portfolio output an index
	price_with_trends_window = price_with_trends[startDate:endDate]
	timestamp = price_with_trends_window.index
	previous_date = startDate
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
			print("Acquired {0} SHORT positions in asset.\n".format(numTrades))
		# Buy long if z-score < -1
		elif current_zscore < -1: 
			portfolio.price[date] = portfolio.price[previous_date] - current_price * numTrades
			numPositions += numTrades
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
	return portfolio

startDate = "2014-01-02"
endDate = "2018-06-01"
start = 1000

folderPath = "C:/Users/Miguel/Documents/EQUITIES/stockDaily"

tickData = single_download.fetch_symbol_from_drive("TSLA", folderPath=folderPath)
price = tickData.close
trend = technicals_calculator.SMA(price, numPeriods=1)
baseline = technicals_calculator.SMA(price, numPeriods=90)
price_with_trends = pd.concat([price, trend, baseline], axis=1)
price_with_trends.columns = ['price','trend','baseline']
price_with_trends.dropna(inplace=True)

zscore_distance(price_with_trends, startDate, endDate, startValue=start, numTrades=1)

plotter.price_plot(price_with_trends[startDate:endDate], "GS", folderPath=folderPath, names=['price', 'SMA01', 'SMA90'], showPlot=True)