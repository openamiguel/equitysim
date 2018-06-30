## This code models a basic ranking strategy, in which the top/bottom quantile is sold short and the bottom/top quintile is bought long.
## Author: Miguel Opeña
## Version: 3.1.1

import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import command_parser
import plotter
import return_calculator
import single_download
import ticker_universe

def asset_ranker(tickerUniverse, startdate, enddate, folderPath, low_quant, high_quant, switchpos=False):
	"""	Ranks a universe of stock tickers based on a given metric.
		By default, the top 20% in this ranking are deemed overvalued, so they are sold short. 
		Likewise, the bottom 20% are deemed undervalued, so they are bought long. 
		One can also choose to switch the quantiles, 
			i.e. the top quantile will be bought long, and the bottom quantile will be sold short. 
		Inputs: ticker universe, start date for price window, end date for price window, folder path, 
			the lower quantile, the upper quantile, 
			order to switch long and short positions (default: no)
		Outputs: list of symbols to buy long and sell short
	"""
	metric = []
	for symbol in tickerUniverse:
		# Reads file from given filepath
		tick_data = single_download.fetch_symbol_from_drive(symbol, function="DAILY", folderPath=folderPath)
		if tick_data is None:
			metric.append(np.NaN)
			print(symbol + " not found. Continuing...")
			continue
		# Checks if the date window spills over available data
		if startdate < tick_data.index[0] or enddate > tick_data.index[-1]:
			metric.append(np.NaN)
			print("Warning: insufficient data on " + symbol + "\n")
			continue
		# Splices the data to include those between start date and end date only
		thisWindow = tick_data[startdate:enddate]
		thisClose = thisWindow.close.values.tolist()
		# Second check for issues in window spillover
		if thisClose == []:
			metric.append(np.NaN)
			print("Warning: insufficient data on " + symbol + "\n")
			continue
		# In this case, metric determined by overall returns of price
		val = return_calculator.overall_returns(thisClose)
		metric.append(val)
		# print(symbol + " successfully processed!\n")
	# Builds dataframe of symbols and metrics
	ranking = pd.DataFrame({'symbol': tickerUniverse, 'metric': metric})
	# Sorts and cleans the dataframe
	ranking.sort_values(by=['metric'], inplace=True, ascending=False)
	ranking.reset_index(inplace=True, drop=True)
	# If symbol could not be ranked, then don't include it
	ranking.dropna(inplace=True)
	# Isolates the stocks in the bottom quantile and top quantile of ranking, respectively
	low_bound = ranking.metric.quantile(low_quant)
	high_bound = ranking.metric.quantile(high_quant)
	longpos = ranking.symbol[ranking.metric < low_bound].values.tolist()
	shortpos = ranking.symbol[ranking.metric > high_bound].values.tolist() 
	# If you want to switch which quantile goes long or short, then the values of longpos and shortpos are switched
	if switchpos:
		temp = longpos
		longpos = shortpos
		shortpos = temp
	# Returns the long and short position symbols
	return longpos, shortpos

def portfolio_generator(longpos, shortpos, startdate, enddate, folderPath="", numshares=1, baseline="^GSPC"):
	"""	Given a pool of stocks to buy long and sell short, this function simulates their value over time. 
		Inputs: list of stocks to buy long, list of stocks to sell short, start date to open positions, 
			end date to open positions, folder path to read files from, 
		Outputs: portfolio value (high, low, open, close) over time
	"""
	# Uses the S&P 500 to get index for portfolio
	seed = single_download.fetch_symbol_from_drive(baseline, function="DAILY", folderPath=folderPath)
	timestamps = seed[startdate:enddate].index
	# Initializes an empty portfolio-over-time dataframe
	portfolio = pd.DataFrame(index=timestamps, columns=['open','high','low','close'])
	for symbol in (longpos + shortpos):
		# Reads file from given filepath
		tick_data = single_download.fetch_symbol_from_drive(symbol, function="DAILY", folderPath=folderPath)
		# Checks if the date window spills over available data
		if startdate < tick_data.index[0] or enddate > tick_data.index[-1]:
			print("Warning: insufficient data on " + symbol)
			continue
		# Isolates asset data to this window
		this_asset = tick_data[startdate:enddate]
		# Volume data is unimportant to pricing of portfolio
		this_asset.drop(labels="volume", axis=1)
		# Multiplies value of each asset by number of shares
		this_asset = this_asset.multiply(numshares, fill_value=0)
		# Adds the value of each long position over time to the portfolio
		if symbol in longpos:
			portfolio = portfolio.add(this_asset, fill_value=0)
		# Subtracts the value of each short position over time to the portfolio
		else:
			portfolio = portfolio.subtract(this_asset, fill_value=0)
	# Return portfolio
	return portfolio

def main():
	""" User interacts with program through command prompt. 
		Example prompts: 

		python ranking_simulator.py -tickerUniverse SNP500 -folderPath C:/Users/Miguel/Desktop/stockData -baseline ^^GSPC -startRankDate 2016-06-05 -endRankDate 2017-06-05 -startTestDate 2017-06-06 -endTestDate 2018-06-06 -switchPos -showPlot -plotName STRATEGY_02
			This will simulate a ranking portfolio for the S&P 500 ticker universe using the S&P 500 index as baseline, with the given dates to rank and trade the portfolio. 

		Inputs: implicit through command prompt
		Outputs: 0 if everything works
	"""
	prompts = sys.argv
	## Handles which symbol the user wants to download.
	ticker_universe, name = command_parser.get_tickerverse_from_prompts(prompts)
	## Handles where the user wants to download their files. 
	# Default folder path is relevant to the author only. 
	folder_path = command_parser.get_generic_from_prompts(prompts, query="-folderPath", default="C:/Users/Miguel/Documents/EQUITIES/stockDaily", req=False)
	## Handles collection of the four dates
	# Gets the start date for ranking
	start_rank_date = command_parser.get_generic_from_prompts(prompts, query="-startRankDate")
	end_rank_date = command_parser.get_generic_from_prompts(prompts, query="-endRankDate")
	start_test_date = command_parser.get_generic_from_prompts(prompts, query="-startTestDate")
	end_test_date = command_parser.get_generic_from_prompts(prompts, query="-endTestDate")
	## Handles which index/asset should be the baseline 
	baseline_symbol = command_parser.get_generic_from_prompts(prompts, query="-baseline", default="^GSPC", req=False)
	## Handles the lower bound for quantiles
	low_quant = float(command_parser.get_generic_from_prompts(prompts, query="-lowQuant", default=0.2, req=False))
	## Handles the higher bound for quantiles
	high_quant = float(command_parser.get_generic_from_prompts(prompts, query="-highQuant", default=0.8, req=False))
	## Handles whether one wants to switch the long and short positions
	switchpos = "-switchPos" in prompts
	## Handles whether one wants to show the plot
	showplt = "-showPlot" in prompts
	## Handles the file name of plot
	plot_name = command_parser.get_generic_from_prompts(prompts, query="-plotName", default="STRATEGY_01", req=False)
	## Handles how many shares for each trade
	num_shares = int(command_parser.get_generic_from_prompts(prompts, query="-numShares", default=1, req=False))
	# Sets up baseline index/asset
	baseline = single_download.fetch_symbol_from_drive(baseline_symbol, function="DAILY", folderPath=folder_path)
	baseline = baseline[start_test_date:end_test_date]
	# Sets up the portfolio
	longpos, shortpos = asset_ranker(ticker_universe, start_rank_date, end_rank_date, folder_path, low_quant, high_quant, switchpos=switchpos)
	portfolio = portfolio_generator(longpos, shortpos, start_test_date, end_test_date, folderPath=folder_path, baseline=baseline_symbol)
	startValue, endValue, returns, baseReturns = return_calculator.portfolio_valuation(portfolio, baseline)
	# Spits out some numerical info about the portfolio performance
	print("\nStarting portfolio value: %f" % startValue)
	print("Ending portfolio value: %f" % endValue)
	print("Return on this strategy: %f" % returns)
	print("Return on {0} baseline: {1}".format(baseline_symbol, baseReturns))
	print("Sharpe ratio: %f" % return_calculator.sharpe_ratio(portfolio))
	# Plots the portfolio
	port_price = pd.concat([portfolio.close, baseline.close], axis=1)
	port_price.columns = ['portfolio', 'baseline']
	plotter.price_plot(port_price, symbol=plot_name, folderpath=folder_path, subplot=[True,True], returns=[True,True], showPlot=showplt)

if __name__ == "__main__":
	main()