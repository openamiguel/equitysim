## This code uses trading signals from strategy.py to model a portfolio across one or many stocks.
## Author: Miguel Opeña
## Version: 1.4.1

import logging
from math import floor
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def apply_trades(prices, trades, initialval=10000, seed=0.1, numtrades=1, transaction=7):
	"""	Applies a set of trades to a set of assets to calculate portfolio value over time
		Inputs: dataframe of prices for multiple symbols, dataframe of trade signals, initial value to invest in, 
			proportion of initial value to seed the portfolio with, number of trades for each transaction, 
			transaction cost (same currency units as initialval) for every buy and sell
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
			portfolio.price[date] = portfolio.price[last_date] - current_price * numtrades - transaction
			numpositions += numtrades
			logger.debug('Date: {0}\tPortfolio modified by {1} LONG positions.'.format(date, numtrades))
		# Holds positions, leaving portfolio value unchanged
		elif current_trade == 0:
			portfolio.price[date] = portfolio.price[last_date]
			logger.debug('Date: {0}\tPortfolio positions held.'.format(date))
		# Sells positions, increasing portfolio value
		elif current_trade == -1:
			portfolio.price[date] = portfolio.price[last_date] + current_price * numtrades - transaction
			numpositions -= numtrades
			logger.debug('Date: {0}\tPortfolio modified by {1} SHORT positions.'.format(date, numtrades))
		# Clears portfolio positions
		elif current_trade == 'X':
			portfolio.price[date] = portfolio.price[last_date] + current_price * numpositions 
			if numpositions == 0:
				logger.debug('Date: {0}\tNo portfolio positions to clear.'.format(date))
			else:
				logger.debug('Date: {0}\tPortfolio cleared {1} positions.'.format(date, numpositions))
				portfolio.price[date] = portfolio.price[date] - transaction
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