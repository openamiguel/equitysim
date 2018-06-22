## This code plots a portfolio's performance against a baseline. 
## Author: Miguel Opeña
## Version: 3.2.2

import pandas as pd
import return_calculator

import matplotlib.pyplot as plt

def price_plot(price_with_trends, symbol, folderPath, names=["price","trend","baseline"], savePlot=True, showPlot=False):
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
	plt.title(plotTitle)
	plt.xlabel("Time [Days]")
	plt.ylabel("Price [USD]")
	# Isolates each column from dataframe
	price = price_with_trends.price.values.tolist()
	trend = price_with_trends.trend.values.tolist()
	baseline = price_with_trends.baseline.values.tolist()
	# Plots the price, trend, and baseline (but only if one is allowed to)
	if names[0] != "NA": plt.plot(time, price, label=names[0])
	if names[1] != "NA": plt.plot(time, trend, label=names[1])
	if names[2] != "NA": plt.plot(time, baseline, label=names[2])
	# Deletes the x-axis ticks
	# Buggy feature
	timeTicks = []
	plt.xticks(timeTicks)
	# If requested, save the file (default: do not save)
	if savePlot:
		figFilePath = folderPath + "images/" + "_".join(names) + ".png"
		plt.savefig(figFilePath)
	# If requested, show the plot
	if showPlot:
		plt.show()

def portfolio_plot(portfolio, baseline, folderPath, savePlot=True, showPlot=False, title="STRATEGY_01"):
	"""	Plots portfolio returns against baseline returns. The plot shows rolling returns (obviously).
		Inputs: dataframe of portfolio price over time, dataframe of baseline price over time, 
			path of folder to store files in
			order to save plot locally (default: yes), 
			order to show plot on command line (default: no), optional title for plot
		Outputs: a plot indicating portfolio returns over time
	"""
	# Collects start and end date from portfolio
	startDate = portfolio.index[0]
	endDate = portfolio.index[-1]
	# Titles and labels a plot of ticker data
	plt.title("Portfolio performance over time, from " + startDate + " to " + endDate)
	plt.xlabel("Time [Days]")
	plt.ylabel("Returns [Percent]")
	# Plots the closing price and rolling means
	portList = portfolio.close.values.tolist()
	baselineList = baseline.close.values.tolist()
	plt.plot(return_calculator.get_rolling_returns(portList), label="My Portfolio")
	plt.plot(return_calculator.get_rolling_returns(baselineList), label="S&P500 Index")
	plt.legend()
	# Deletes the x-axis ticks
	timeTicks = []
	plt.xticks(timeTicks)
	# If requested, save the file (default: do not save)
	if savePlot:
		figFilePath = folderPath + "/images/" + title + ".png"
		plt.savefig(figFilePath)
	# If requested, show the plot
	if showPlot:
		plt.show()