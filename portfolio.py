## This code uses trading signals from 
## -1 corresponds to sell short, 0 to hold, 1 to buy long, and 'X' to clear all positions
## Author: Miguel Opeña
## Version: 1.1.1

import logging
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def apply_trades(prices, trades, injection=1000000, numtrades=1):
	"""	Applies a set of trades to a set of assets to calculate portfolio value over time
		Inputs: dataframe of prices
	"""
	# Saves timestamp to give the portfolio output an index
	timestamp = prices.index
	# Saves starting portfolio value
	startval = prices.all_prices[timestamp[0]]
	# Merges all the price columns into a consolidated column
	prices['all_prices'] = prices.sum(axis=1)
	# Checks if start value can cover one share of each asset
	# Note: one could instead assume fractional shares
	if startval > injection:
		logger.error("Error: insufficient funds to start trading.")
		return None
	# Saves the number of positions total
	# Starts with as many positions as one can fill with given injection
	numpositions = int(round(injection / startval))
	# Sets up the portfolio as a dataframe
	portfolio = pd.DataFrame(injection - startval * numpositions, index=timestamp, columns=['price'])
	# Saves the previous date
	last_date = timestamp[0]
	# Iterates through all the dates (starts on second given date)
	for date in timestamp[1:]:
		current_price = prices.all_prices[date]
		current_trade = trades.all_trades[date]
		# Checks if any assets left to trade
		if numtrades * current_price > portfolio.price[last_date]:
			logger.error("Error: Portfolio has run out of funds at {}.".format(date))
			return None
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
		logger.info('Date: {0}\tPortfolio value at ${1}.'.format(date, portfolio.price[date]))
		last_date = date
	return portfolio