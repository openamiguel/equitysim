## This code plots a portfolio's performance against a baseline. 
## Author: Miguel Opeña
## Version: 3.5.0

import sys
import pandas as pd
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

import return_calculator
import single_download

YEARS = mdates.YearLocator()
MONTHS = mdates.MonthLocator()

def price_plot(price_with_trends, symbol, folderPath, names=["price","trend","baseline"], longDates=[], shortDates=[], savePlot=True, showPlot=False):
	"""	Given a dataframe of price, trend, and baseline data, plots the price against trend and baseline. 
	Given a stock ticker, this function computes the rolling mean (with two metrics thereof) and saves it to a Pyplot figure.
		These calculations are all performed with the daily closing price. No other data is needed. 
		One has the option to show the window live, and to save it locally. 
		Inputs: symbol of company, the company's English name, start date of given window, end date of given window, 
			rolling lengths (default: 30-day and 90-day), order to save plot locally (default: yes), 
			order to show plot on command line (default: no) 
		Outputs: dataframe of daily closing price, rolling mean over X days, and rolling mean over Y days
	"""
	# Titles and labels a plot of ticker data
	plotTitle = symbol
	for name in names:
		if name != "NA":
			plotTitle = plotTitle + " " + name
	# Initializes plot as variable
	fig, ax = plt.subplots()
	# Sets up plot title and labels
	plt.title(plotTitle)
	plt.xlabel("Time [Months]")
	plt.ylabel("Price [USD]")
	time = pd.to_datetime(price_with_trends.index)
	# Plots the price, trend, and baseline (but only if one is allowed to)
	if names[0] != "NA": ax.plot(time, price_with_trends.price, label=names[0])
	if names[1] != "NA": ax.plot(time, price_with_trends.trend, label=names[1])
	if names[2] != "NA": ax.plot(time, price_with_trends.baseline, label=names[2])
	# Parses the lists of longDates and shortDates
	for date in (longDates + shortDates):
		mark = "^" if date in longDates else "v"
		col = "green" if date in longDates else "red"
		ax.scatter(date, 0, marker=mark, color=col)
	# Adds a legend
	plt.legend()
	# Formats the x-axis: major ticks are years, minor ticks are months
	ax.xaxis.set_major_locator(YEARS)
	ax.xaxis.set_minor_locator(MONTHS)
	fig.autofmt_xdate()
	# If requested, save the file (default: do not save)
	if savePlot:
		figFilePath = folderPath + "/images/" + symbol + "_" + "_".join(names) + ".png"
		plt.savefig(figFilePath)
	# If requested, show the plot
	if showPlot:
		plt.show()
	plt.close(fig)

def portfolio_plot(portfolio, baseline, folderPath, baselineLabel="Baseline", savePlot=True, showPlot=False, title="STRATEGY_01"):
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
		figFilePath = folderPath + "/images/" + title + ".png"
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
	if function == "INTRADAY" and "-interval" in prompts:
		interval = prompts[prompts.index("-interval") + 1]
	elif function == " INTRADAY" and "-interval" not in prompts:
		raise ValueError("No interval for INTRADAY data provided. Please try again.")
	## Handles collection of the four dates
	# Gets the start date for ranking
	startDate = ""
	if "-startDate" not in prompts:
		raise ValueError("No start date for ranking provided. Please try again.")
	else:
		startDate = prompts[prompts.index("-startDate") + 1]
	# Gets the end date for ranking
	endDate = ""
	if "-endDate" not in prompts:
		raise ValueError("No end date for ranking provided. Please try again.")
	else:
		endDate = prompts[prompts.index("-endDate") + 1]
	# Handles intraday plots properly
	## Runs the plot code on the lone symbol
	tickData = single_download.fetch_symbol_from_drive(symbol, function=function, folderPath=folderPath)
	tickData = tickData[startDate:endDate]
	tickData.columns = ['open', 'high', 'low', 'price', 'volume']
	price_plot(tickData, symbol, folderPath, names=["price","NA","NA"], savePlot=True, showPlot=True)
	return 0

if __name__ == "__main__":
	main()