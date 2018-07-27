## This code uses trading signals from strategy.py to model a portfolio across one or many stocks.
## Author: Miguel Opeña
## Version: 1.5.8

import logging
from math import floor
import pandas as pd

import download
import performance
import plotter
import return_calculator
import strategy
import ticker_universe

FORMAT = '%(asctime)-15s %(user)-8s %(levelname)s:%(message)s'
logging.basicConfig(filename='/Users/openamiguel/Desktop/LOG/example.log', level=logging.INFO, format=FORMAT)
logger = logging.getLogger(__name__)
logger.info("----------INITIALIZING NEW RUN OF {}----------".format(__name__))

def asset_ranker(prices, ranking_method, lowquant=0.2, highquant=0.8, switch=False):
	"""	Applies a ranking methodology to a set of asset data, selecting quantiles of data to go long or short on.
		Inputs: dataframe of prices for multiple symbols, numbers for quantiles, order to switch long and short (default: no)
		Outputs: dataframes representing long-position assets and short-position assets
	"""
	# Sets up rank as empty dataframe, with rows indexed by symbols in prices
	rank = pd.DataFrame(index=list(prices.columns.values), columns=['ranking'])
	for column in prices:
		# Assumes that ranking_method takes Series as input
		rank.ranking[column] = ranking_method(prices[column])
	# Sorts and cleans the dataframe
	rank.sort_values(by=['ranking'], ascending=False, inplace=True)
	rank.reset_index(drop=True, inplace=True)
	# Isolates the stocks in the bottom quantile and top quantile of ranking, respectively
	bottom_bound = rank.ranking.quantile(lowquant)
	top_bound = rank.ranking.quantile(highquant)
	long_prices = prices.iloc[:,list(rank.index[rank.ranking < bottom_bound])]
	short_prices = prices.iloc[:,list(rank.index[rank.ranking > top_bound])]
	# If prompted to switch, the long and short positions are safely switched
	if switch:
		temp = long_prices
		long_prices = short_prices
		short_prices = temp
	# Returns the long and short prices
	return long_prices, short_prices

def apply_trades(prices, trades, initialval=100000, seed=0.1, numtrades=1, transaction=7):
	"""	Applies a set of trades to a set of assets to calculate portfolio value over time
		Inputs: dataframe of prices for multiple symbols, dataframe of trade signals, initial value to invest in, 
			proportion of initial value to seed the portfolio with, number of trades for each transaction, 
			transaction cost (same currency units as initialval) for every buy and sell
		Outputs: portfolio performance over time
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
	# Adds logger statement to indicate new portfolio
	logger.info("Initializing new portfolio with initial value ${0} and seed {1}%%".format(initialval, seed * 100))
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

def main():
	tickerverse = ticker_universe.obtain_parse_wiki("SNP500")
	tickerverse_copy = tickerverse
	folder_path="/Users/openamiguel/Documents/EQUITIES/stockDaily"
	start_date = "2014-01-06"
	end_date = "2018-06-28"

	prices = pd.DataFrame()
	column_choice = "close"
	for symbol in tickerverse_copy:
		symboldata = download.load_single_drive(symbol, folderpath=folder_path)
		if symboldata is not None: 
			prices = pd.concat([prices, symboldata[column_choice]], axis=1)
		else:
			tickerverse.remove(symbol)
	prices = prices[start_date:end_date]
	print(prices.columns)
	prices.columns  = tickerverse
	long_prices, short_prices = asset_ranker(prices, ranking_method=return_calculator.overall_returns)
	port = apply_trades(long_prices, strategy.hold_clear(long_prices, switch=True)) + apply_trades(short_prices, strategy.hold_clear(short_prices))

	portfolio_baseline = download.load_single_drive("^GSPC", folderpath=folder_path)
	portfolio_baseline = portfolio_baseline[~portfolio_baseline.index.duplicated(keep='first')]
	portfolio_baseline = portfolio_baseline[start_date:end_date]

	start_value, end_value, returns, baseline_returns = performance.returns_valuation(port.price, portfolio_baseline.close)

	logger.info("Starting portfolio value: {}".format(start_value))
	logger.info("Ending portfolio value: {}".format(end_value))
	logger.info("Return on this strategy: {}".format(returns))
	logger.info("Return on S&P500 index: {}".format(baseline_returns))
	logger.info("Sharpe ratio: {}".format(performance.sharpe_ratio(port.price)))

	# Plots the portfolio
	plot_name = "SNP500Ranking_New_01"
	port_price = pd.concat([port.price, portfolio_baseline.close], axis=1)
	port_price.columns = ['portfolio', 'baseline']
	plotter.price_plot(port_price, symbol=plot_name, folderpath=folder_path, subplot=[True,True], returns=[True,True], showPlot=True)

if __name__ == "__main__":
	main()