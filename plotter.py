## This code plots a portfolio's performance against a baseline. 
## Author: Miguel Opeña
## Version: 3.1.0

import pandas as pd
import return_calculator

import matplotlib.pyplot as plt

def plot(portfolio, baseline, folderPath, savePlot=True, showPlot=False, title="STRATEGY_01"):
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
