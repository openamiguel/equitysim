## This code contains several functionalities for plotting stocks: whether as individual assets (price), or as portfolios (returns).
## Author: Miguel Opeña
## Version: 4.2.3

import seaborn as sns
import sys
import numpy as np
import pandas as pd
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

import command_parser
import return_calculator
import single_download

YEARS = mdates.YearLocator()
MONTHS = mdates.MonthLocator()
DATES = mdates.DayLocator()
HOURS = mdates.HourLocator()

def feature_plot(symbol, folderpath="", savePlot=True, showPlot=False):
	"""	Given a dataframe of features (downloaded from a file), this code plots the correlations of said features as a heatmap.
		Inputs: symbol of company, folder path to write to and get plot from, order to save plot to folder path (default: yes), 
			order to show plot on command line (default: no)
		Outputs: heatmap of correlations
	"""
	# Initializes figure
	fig = plt.figure(figsize=(12.5, 9.5))
	plt.gcf().subplots_adjust(bottom=0.25)
	plt.gcf().subplots_adjust(left=0.2)
	# Get data from file
	filePath = folderpath + "/features/{}_Features.csv".format(symbol)
	features = pd.read_csv(filePath)
	featCorr = features.corr()
	# Gives plot a title
	plt.title(symbol + " features heatmap")
	# Plot the heatmap of correlations
	sns.heatmap(featCorr, xticklabels=featCorr.columns.values, yticklabels=featCorr.columns.values, center=0, linewidths=0.7, cmap="seismic")
	# If requested, save the file (default: do not save)
	if savePlot:
		figFilePath = folderpath + "/images/{}_Features.png".format(symbol)
		plt.savefig(figFilePath)
	# If requested, show the plot
	if showPlot:
		plt.show()
	plt.close(fig)

def price_plot(price_with_trends, symbol, subplot, returns, longdates=[], shortdates=[], folderpath="", savePlot=True, showPlot=False):
	"""	Given a dataframe of price, trend(s), and baseline(s) data, plots the price against trend(s) and baseline(s). 
		One has the option to show the window live, and to save it locally. 
		Inputs: price with trends, symbol of company, dates with long positions, dates with short positions, 
			folder path to write plot to, order to save plot to folder path (default: yes), order to show plot 
			on command line (default: no) 
		Outputs: plot with all the desired data
	"""
	# Every true element corresponds to command to plot list
	num_subplots = subplot.count(False) + 1
	# Converts dataframe to regular frequency for plotting purposes
	intraday = ":" in price_with_trends.index[0]
	price_with_trends.index = pd.to_datetime(price_with_trends.index)
	if intraday: price_with_trends = price_with_trends.resample('1T').asfreq()
	time = pd.to_datetime(price_with_trends.index)
	# Initializes plot as variable
	fig, axes = plt.subplots(num_subplots, 1, sharex=True)
	# Saves the first subplot as variable
	ax_main = axes[0] if num_subplots > 1 else axes
	# Loops through each column of the dataframe and plots it
	i = 0
	j = 1
	# Gets the plot title
	plotTitle = symbol + " " + "-".join(price_with_trends.columns.values.tolist())
	min_price = 0
	for column in price_with_trends:
		# Used to clean up the plots for buy and sell signals
		if i == 0: min_price = price_with_trends[column].min()
		lab = column
		# Checks if the column should be plotted as returns
		ypoints = return_calculator.get_rolling_returns(price_with_trends[column].values.tolist()) if returns[i] else price_with_trends[column]
		if subplot[i]:
			ax_main.set_title(plotTitle)
			ax_main.plot(time, ypoints, label=lab)
			ax_main.legend(loc="upper right")
		else:
			axes[j].set_title(lab)
			axes[j].plot(time, ypoints, label=lab)
			axes[j].legend(loc="upper right")
			j = j + 1
		i = i + 1
	# Parses the lists of longdates and shortdates for buy and sell signals
	for date in (longdates + shortdates):
		mark = "^" if date in longdates else "v"
		col = "green" if date in longdates else "red"
		ax_main.scatter(date, min_price, marker=mark, color=col)
	# Sets up plot title and x-axis labels
	xlab = "Time [Minutes]" if intraday else "Time [Days]"
	plt.xlabel(xlab)
	# Adds a legend
	plt.legend()
	# If requested, save the file (default: do not save)
	if savePlot:
		figFilePath = folderpath + "/images/" + symbol + "_" + "_".join(list(price_with_trends.columns.values)) + ".png"
		plt.savefig(figFilePath)
	# If requested, show the plot
	if showPlot:
		plt.show()
	plt.close(fig)

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
	symbol = command_parser.get_generic_from_prompts(prompts, "-symbol")
	## Handles where the user wants to download their files. 
	# Default folder path is relevant to the author only. 
	folder_path = command_parser.get_generic_from_prompts(prompts, query="-folderPath", default="C:/Users/Miguel/Documents/EQUITIES/stockDaily", req=False)
	## Handles collection of the start and end dates for trading
	start_date = command_parser.get_generic_from_prompts(prompts, query="-startDate")
	end_date = command_parser.get_generic_from_prompts(prompts, query="-endDate")
	## Handles the desired time series function. 
	function = command_parser.get_generic_from_prompts(prompts, query="-function")
	## Handles the special case: if INTRADAY selected. 
	interval = ""
	intraday = function == "INTRADAY"
	if intraday:
		interval = command_parser.get_generic_from_prompts(prompts, query="-interval")
		start_date = start_date.replace("_"," ")
		end_date = end_date.replace("_"," ")
	## Handles command line option for which column of dataframe to plot
	column_choice = command_parser.get_generic_from_prompts(prompts, query="-column", default="close", req=False)
	## Runs the plot code on the lone symbol
	tick_data = single_download.fetch_symbol_from_drive(symbol, function=function, folderPath=folder_path, interval=interval)
	tick_data = tick_data[start_date:end_date]
	tick_data.columns = [x if x != column_choice else "price" for x in tick_data.columns.values.tolist()]
	price_plot(pd.DataFrame(tick_data.price, columns=['price']), symbol, subplot=[True], returns=[False],folderpath=folder_path, savePlot=True, showPlot=True)
	return 0

if __name__ == "__main__":
	main()