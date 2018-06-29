## This code contains several functionalities for plotting stocks: whether as individual assets (price), or as portfolios (returns).
## Author: Miguel Opeña
## Version: 3.7.1

import sys
import numpy as np
import pandas as pd
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

import return_calculator
import single_download

YEARS = mdates.YearLocator()
MONTHS = mdates.MonthLocator()
DATES = mdates.DayLocator()
HOURS = mdates.HourLocator()

def price_plot(price_with_trends, symbol, longdates, shortdates, folderpath="", savePlot=True, showPlot=False):
	"""	Given a dataframe of price, trend(s), and baseline(s) data, plots the price against trend(s) and baseline(s). 
		One has the option to show the window live, and to save it locally. 
		Inputs: price with trends, symbol of company, dates with long positions, dates with short positions, 
			folder path to write plot to, order to save plot to folder path (default: yes), order to show plot 
			on command line (default: no) 
		Outputs: dataframe of daily closing price, rolling mean over X days, and rolling mean over Y days
	"""
	# Titles and labels a plot of ticker data
	plotTitle = symbol + " " + "-".join(price_with_trends.columns.values.tolist())
	num_subplots = len(price_with_trends.columns.values.tolist())
	# Initializes plot as variable
	fig, axes = plt.subplots(num_subplots, 1, sharex=True)
	# Sets up plot title and labels
	plt.title(plotTitle)
	# Converts dataframe to regular frequency for plotting purposes
	price_with_trends.index = pd.to_datetime(price_with_trends.index)
	if intraday: price_with_trends = price_with_trends.resample('1T').asfreq()
	time = pd.to_datetime(price_with_trends.index)
	# Loops through each column of the dataframe and plots it
	i = 0
	for ax in axes:	
		ax.title(price_with_trends[price_with_trends.columns[i]])
		ax.plot(time, price_with_trends.price)
		if i == 0:
			# Parses the lists of longdates and shortdates
			for date in (longdates + shortdates):
				mark = "^" if date in longdates else "v"
				col = "green" if date in longdates else "red"
				ax.scatter(date, 0, marker=mark, color=col)
		i = i + 1
	
	
	xlab = "Time [Hours]" if intraday else "Time [Months]"
	plt.xlabel(xlab)
	plt.ylabel("Price [USD]")
	
	
	# Adds a legend
	plt.legend()
	# Formats the x-axis: major ticks are years, minor ticks are months
	if intraday:
		ax.xaxis.set_major_locator(DATES)
		ax.xaxis.set_minor_locator(HOURS)
		ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
	else:
		ax.xaxis.set_major_locator(YEARS)
		ax.xaxis.set_minor_locator(MONTHS)
		fig.autofmt_xdate()
	# If requested, save the file (default: do not save)
	if savePlot:
		figFilePath = folderpath + "/images/" + symbol + "_" + "_".join(names) + ".png"
		plt.savefig(figFilePath)
	# If requested, show the plot
	if showPlot:
		plt.show()
	plt.close(fig)

def portfolio_plot(portfolio, baseline, folderpath, baselineLabel="Baseline", savePlot=True, showPlot=False, title="STRATEGY_01"):
	"""	Plots portfolio returns against baseline returns. The plot shows rolling returns (obviously).
		Inputs: dataframe of portfolio price over time, dataframe of baseline price over time, 
			path of folder to store files in, label for baseline index, 
			order to save plot locally (default: yes), 
			order to show plot on command line (default: no), optional title for plot
		Outputs: a plot indicating portfolio returns over time
	"""
	# Collects start and end date from portfolio
	startDate = portfolio.index[0]
	endDate = portfolio.index[-1]
	# Initializes plot as variable
	fig, ax = plt.subplots()
	# Titles and labels a plot of ticker data
	plt.title("Portfolio performance over time, from " + startDate + " to " + endDate)
	plt.xlabel("Time [Days]")
	plt.ylabel("Returns [Percent]")
	# Converts dataframe to regular frequency for plotting purposes
	portfolio.index = pd.to_datetime(portfolio.index)
	# Plots the closing price and rolling means
	portList = portfolio.close.values.tolist()
	baselineList = baseline.close.values.tolist()
	ax.plot(return_calculator.get_rolling_returns(portList), label="My Portfolio")
	ax.plot(return_calculator.get_rolling_returns(baselineList), label=baselineLabel)
	# Adds a legend
	plt.legend()
	# Formats the x-axis: major ticks are years, minor ticks are months
	ax.xaxis.set_major_locator(YEARS)
	ax.xaxis.set_minor_locator(MONTHS)
	fig.autofmt_xdate()
	# If requested, save the file (default: do not save)
	if savePlot:
		figFilePath = folderpath + "/images/" + title + ".png"
		plt.savefig(figFilePath)
	# If requested, show the plot
	if showPlot:
		plt.show()
	plt.close('all')

def main():
	""" User interacts with program through command prompt. 
		Example prompts: 

		python plotter.py -symbol MSFT -folderPath C:/Users/Miguel/Desktop/stockData -timeSeriesFunction DAILY -startDate 2016-06-05 -endDate 2017-06-05
			This will plot daily data on MSFT (stored on local drive) from June 5, 2016 to June 5, 2017.
		
		python plotter.py -symbol AAPL -folderPath C:/Users/Miguel/Desktop/stockData -timeSeriesFunction INTRADAY -interval 1min -startDate 2018-06-01 12:00:00 PM -endDate 2018-06-07 12:00:00 PM
			This will plot intraday (1 minute interval) data on AAPL (stored on local drive) from June 1, 2018 12 PM to June 7, 2018 12 PM.

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
	## Handles the desired time series function. 
	function = ""
	if "-timeSeriesFunction" in prompts:
		function = prompts[prompts.index("-timeSeriesFunction") + 1]
	else:
		raise ValueError("No time series function provided. Please try again.")
	# Handles the special case: if INTRADAY selected. 
	interval = ""
	intraDay = False
	if function == "INTRADAY" and "-interval" in prompts:
		interval = prompts[prompts.index("-interval") + 1]
		intraDay = True
	elif function == " INTRADAY" and "-interval" not in prompts:
		raise ValueError("No interval for INTRADAY data provided. Please try again.")
	## Handles collection of the four dates
	# Gets the start date for ranking
	startDate = ""
	if "-startDate" not in prompts:
		raise ValueError("No start date for ranking provided. Please try again.")
	else:
		startDate = prompts[prompts.index("-startDate") + 1]
		# Handles intraday plots properly
		if intraDay:
			startDate = startDate.replace('_',' ')
	# Gets the end date for ranking
	endDate = ""
	if "-endDate" not in prompts:
		raise ValueError("No end date for ranking provided. Please try again.")
	else:
		endDate = prompts[prompts.index("-endDate") + 1]
		# Handles intraday plots properly
		if intraDay:
			endDate = endDate.replace('_',' ')
	## Handles command line option for which column of dataframe to plot
	columnChoice = "close"
	if "-column" not in prompts:
		print("By default, this will plot the closing price.")
	else:
		columnChoice = prompts[prompts.index("-column") + 1]
	## Runs the plot code on the lone symbol
	tickData = single_download.fetch_symbol_from_drive(symbol, function=function, folderpath=folderPath, interval=interval)
	tickData = tickData[startDate:endDate]
	tickData.columns = [x if x != columnChoice else "price" for x in tickData.columns.values.tolist()]
	['open', 'high', 'low', 'price', 'volume']
	price_plot(tickData, symbol, folderPath, names=[columnChoice,"NA","NA"], intraday=intraDay, savePlot=True, showPlot=True)
	return 0

if __name__ == "__main__":
	main()