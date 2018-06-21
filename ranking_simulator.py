## This code models a basic ranking strategy, in which the top/bottom quantile is sold short and the bottom/top quintile is bought long.
## Author: Miguel Opeña
## Version: 3.0.2

import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import single_download
import ticker_universe
import return_calculator
import plotter

def asset_ranker(tickerUniverse, startdate, enddate, folderPath, lowQuant, highQuant, switchpos=False):
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
	low_bound = ranking.metric.quantile(lowQuant)
	high_bound = ranking.metric.quantile(highQuant)
	longpos = ranking.symbol[ranking.metric < low_bound].values.tolist()
	shortpos = ranking.symbol[ranking.metric > high_bound].values.tolist() 
	# If you want to switch which quantile goes long or short, then the values of longpos and shortpos are switched
	if switchpos:
		temp = longpos
		longpos = shortpos
		shortpos = temp
	# Returns the long and short position symbols
	return longpos, shortpos

def portfolio_generator(longpos, shortpos, startdate, enddate, folderPath="", numshares=1):
	"""	Given a pool of stocks to buy long and sell short, this function simulates their value over time. 
		Inputs: list of stocks to buy long, list of stocks to sell short, start date to open positions, 
			end date to open positions, folder path to read files from, 
		Outputs: portfolio value (high, low, open, close) over time
	"""
	# Uses the S&P 500 to get index for portfolio
	seed = single_download.fetch_symbol_from_drive("^GSPC", function="DAILY", folderPath=folderPath)
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
	prompts = sys.argv
	## Handles which symbol the user wants to download.
	tickerUniverse = []
	name = ""
	if "-tickerUniverse" not in prompts:
		raise ValueError("No ticker universe provided. Please try again")
	# Yields data on the S&P 500
	elif "SNP500" in prompts:
		tickerUniverse = ticker_universe.obtain_parse_wiki(selection="SNP500", seed="^GSPC")
		name = "SNP500"
	# Yields data on the Dow 30
	elif "DOW30" in prompts:
		tickerUniverse = ticker_universe.obtain_parse_wiki(selection="DOW30", seed="^DJI")
		name = "DOW30"
	# Yields data on the NASDAQ 100
	elif "NASDAQ100" in prompts:
		tickerUniverse = ticker_universe.obtain_parse_nasdaq()
		name = "NASDAQ100"
	## Handles where the user wants to download their files. 
	# Default folder path is relevant to the author only. 
	folderPath = "C:/Users/Miguel/Documents/EQUITIES/stockDaily"
	if "-folderPath" not in prompts:
		print("Warning: the program will use default file paths, which may not be compatible on your computer.")
	else: 
		folderPath = prompts[prompts.index("-folderPath") + 1]
	## Handles collection of the four dates
	# Gets the start date for ranking
	startRankDate = ""
	if "-startRankDate" not in prompts:
		raise ValueError("No start date for ranking provided. Please try again.")
	else:
		startRankDate = prompts[prompts.index("-startRankDate") + 1]
	# Gets the end date for ranking
	endRankDate = ""
	if "-endRankDate" not in prompts:
		raise ValueError("No end date for ranking provided. Please try again.")
	else:
		endRankDate = prompts[prompts.index("-endRankDate") + 1]
	# Gets the start date for portfolio testing
	startTestDate = ""
	if "-startTestDate" not in prompts:
		raise ValueError("No start date for testing provided. Please try again.")
	else:
		startTestDate = prompts[prompts.index("-startTestDate") + 1]
	# Gets the end date for portfolio testing
	endTestDate = ""
	if "-endTestDate" not in prompts:
		raise ValueError("No end date for testing provided. Please try again.")
	else:
		endTestDate = prompts[prompts.index("-endTestDate") + 1]
	## Handles which index/asset should be the baseline 
	baselineSymbol = "^GSPC"
	if "-baseline" not in prompts:
		print("Default baseline: S&P 500 index")
	else:
		baselineSymbol = prompts[prompts.index("-baseline") + 1]
	# Sets up baseline index/asset
	baseline = single_download.fetch_symbol_from_drive(baselineSymbol, function="DAILY", folderPath=folderPath)
	baseline = baseline[startTestDate:endTestDate]
	## Handles the lower bound for quantiles
	lowQuant = 0.2
	if "-lowQuant" in prompts: lowQuant = float(prompts[prompts.index("-lowQuant") + 1])
	## Handles the higher bound for quantiles
	highQuant = 0.8
	if "-highQuant" in prompts: highQuant = float(prompts[prompts.index("-highQuant") + 1])
	## Handles whether one wants to switch the long and short positions
	switchpos = ("-switchPos" in prompts)
	## Handles whether one wants to show the plot
	showplt = ("-showPlot" in prompts)
	## Handles the file name of plot
	plotName = "STRATEGY_01"
	if "-plotName" in prompts: plotName = prompts[prompts.index("-plotName") + 1]
	## Handles how many shares to include in the portfolio
	numShares = 1
	if "-numShares" in prompts: numShares = int(prompts[prompts.index("-numShares") + 1])
	# Sets up the portfolio
	longpos, shortpos = asset_ranker(tickerUniverse, startRankDate, endRankDate, folderPath, lowQuant, highQuant, switchpos=switchpos)
	portfolio = portfolio_generator(longpos, shortpos, startTestDate, endTestDate, folderPath=folderPath)
	startValue, endValue, returns, baseReturns = return_calculator.portfolio_valuation(portfolio, baseline)
	# Spits out some numerical info about the portfolio performance
	print("\nStarting portfolio value: %f" % startValue)
	print("Ending portfolio value: %f" % endValue)
	print("Return on this strategy: %f" % returns)
	print("Return on S&P500 index: %f" % baseReturns)
	print("Sharpe ratio: %f" % return_calculator.sharpe_ratio(portfolio))
	# Plots the portfolio
	plotter.portfolio_plot(portfolio, baseline, folderPath=folderPath, showPlot=showplt, title=plotName)

if __name__ == "__main__":
	main()