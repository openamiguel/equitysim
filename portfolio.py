## This code uses trading signals from strategy.py to model a portfolio across one or many stocks.
## Author: Miguel Opeña
## Version: 1.2.5

import logging
from math import floor
import pandas as pd

import single_download
import strategy
import technicals_calculator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def apply_trades(prices, trades, initialval=10000, seed=0.1, numtrades=1):
	"""	Applies a set of trades to a set of assets to calculate portfolio value over time
		Inputs: dataframe of prices for multiple symbols, dataframe of trade signals, initial value to invest in, 
			proportion of initial value to seed the portfolio with, number of trades for each transaction
	"""
	# Saves timestamp to give the portfolio output an index
	timestamp = prices.index
	# Merges all the price columns into a consolidated column
	prices['all_prices'] = prices.sum(axis=1)
	# Saves starting portfolio value
	startval = prices.all_prices[timestamp[0]]
	# Checks if start value can cover one share of each asset
	# Note: one could instead assume fractional shares
	if startval > initialval:
		logger.error("Error: insufficient funds to start trading.")
		return None
	# Saves the number of positions total
	# Starts with as many positions as one can fill with given initial value
	numpositions = int(floor(seed * initialval / startval))
	# Sets up the portfolio as a dataframe
	portfolio = pd.DataFrame(initialval - startval * numpositions, index=timestamp, columns=['price'])
	# Saves the previous date
	last_date = timestamp[0]
	# Iterates through all the dates (starts on second given date)
	for date in timestamp[1:]:
		current_price = prices.all_prices[date]
		current_trade = trades.all_trades[date]
		# Buys positions, reducing portfolio value
		if current_trade == 1:
			portfolio.price[date] = portfolio.price[last_date] - current_price * numtrades
			numpositions += numtrades
			logger.debug('Date: {0}\tPortfolio modified by {1} LONG positions.'.format(date, numtrades))
		# Holds positions, leaving portfolio value unchanged
		elif current_trade == 0:
			portfolio.price[date] = portfolio.price[last_date]
			logger.debug('Date: {0}\tPortfolio positions held.'.format(date))
		# Sells positions, increasing portfolio value
		elif current_trade == -1:
			portfolio.price[date] = portfolio.price[last_date] + current_price * numtrades
			numpositions -= numtrades
			logger.debug('Date: {0}\tPortfolio modified by {1} SHORT positions.'.format(date, numtrades))
		# Clears portfolio positions
		elif current_trade == 'X':
			portfolio.price[date] = portfolio.price[last_date] + current_price * numpositions
			if numpositions > 0:
				logger.debug('Date: {0}\tNo portfolio positions to clear.'.format(date))
			else:
				logger.debug('Date: {0}\tPortfolio cleared {1} positions.'.format(date, numpositions))
			numpositions = 0
		# No other values are currently permitted
		else:
			logger.error("Error: bad trading signal found at date {0}".format(date))
		# Checks if any assets left to trade
		if portfolio.price[last_date] <= 0:
			logger.error("Error: Portfolio has run out of funds at {}.".format(date))
			return None
		logger.info('Date: {0}\tPortfolio value at ${1}.'.format(date, portfolio.price[date]))
		last_date = date
	return portfolio

def main():
	symbol="AAPL"
	folder_path="C:/Users/Miguel/Documents/EQUITIES/stockDaily"
	start_date = "2014-01-01"
	end_date = "2018-06-28"
	tick_data = single_download.fetch_symbol_from_drive(symbol, folderPath=folder_path)
	tick_data = tick_data[start_date:end_date]
	prices = pd.concat([tick_data.close], axis=1)
	trend = technicals_calculator.exponential_moving_average(tick_data.close, num_periods=30)
	baseline = technicals_calculator.exponential_moving_average(tick_data.close, num_periods=90)
	trend_baseline = pd.concat([trend, baseline], axis=1)
	trend_baseline.columns = ['trend','baseline']
	trades = strategy.zscore_distance(trend_baseline)
	portfolio = apply_trades(prices, trades)

if __name__ == "__main__":
	main()