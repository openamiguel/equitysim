## This code models a very basic mean reversion strategy, using daily closing prices of one stock. 
## Author: Miguel Opeña
## Version: 1.4.0

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Gets the chosen filepath
DIRECTORY = "C:/Users/Miguel/Documents/stockData/"
FILE_PATH = DIRECTORY + "zzzzzzzz_DAILY.csv"
KEYWORD = "zzzzzzzz"

def meanReversionPlot(symbol, companyName, startDate, endDate, roll=[30,90], savePlot=True, showPlot=False):
	"""	Given a stock ticker, this function computes the rolling mean (with two metrics thereof) and saves it to a Pyplot figure.
		These calculations are all performed with the daily closing price. No other data is needed. 
		One has the option to show the window live, and to save it locally. 
		Inputs: symbol of company, the company's English name, start date of given window, end date of given window, 
			rolling lengths (default: 30-day and 90-day), order to save plot locally (default: yes), 
			order to show plot on command line (default: no) 
		Outputs: dataframe of daily closing price, rolling mean over X days, and rolling mean over Y days
	"""
	# Reads file from given filepath (entails assumptions about file name)
	filePath = FILE_PATH.replace(KEYWORD, symbol)
	ticker = pd.read_csv(filePath, index_col='timestamp')
	# Isolates the ticker data between the start date and end date
	thisTime = ticker[startDate:endDate]
	time = thisTime.index
	# Closing data only!
	price = thisTime.close
	# Computes the rolling mean (default: 30-day and 90-day)
	roll01 = price.rolling(roll[0]).mean()
	roll02 = price.rolling(roll[1]).mean()
	# Compiles all the data together for export
	priceRollingData = pd.concat([price, roll01, roll02], axis=1, join='inner')
	priceRollingData.dropna(inplace=True)
	priceRollingData.columns = ['close', 'roll', 'rollTrend']
	# Titles and labels a plot of ticker data
	plt.title(companyName + " Closing Price, from " + startDate + " to " + endDate)
	plt.xlabel("Time [Days]")
	plt.ylabel("Price [USD]")
	# Plots the closing price and rolling means
	plt.plot(time, price)
	plt.plot(time, roll01)
	plt.plot(time, roll02)
	# Deletes the x-axis ticks
	timeTicks = []# [int(round(i)) for i in range(0, len(time), round(len(time)/4.5))]
	plt.xticks(timeTicks)
	# If requested, save the file (default: do not save)
	if savePlot:
		figFilePath = DIRECTORY  + "images/" + symbol + "_MEAN_REVERSION_" + str(roll[0]) + "_" + str(roll[1]) + ".png"
		plt.savefig(figFilePath)
	# If requested, show the plot
	if showPlot:
		plt.show()
	# Return the combined data
	return priceRollingData

### WARNING: THIS STRATEGY IS BOGUS. IT MAY NOT EVEN MODEL WHAT I INTENDED IT TO. 
def meanReversionStrategy(priceRollingData, startingValue=1000, numBuys=1):
	price = priceRollingData.close.values.tolist()
	roll = priceRollingData.roll.values.tolist()
	rollTrend = priceRollingData.rollTrend.values.tolist()

	numPositions = 0
	portfolio = startingValue
	isGreater = roll[0] > rollTrend[0]

	for i in range(len(price)):
		thisPrice = price[i]
		thisRoll = roll[i]
		thisRollTrend = rollTrend[i]
		# print("Current portfolio value: %d" % portfolio)
		# print("Number of positions held: %d" % numPositions)
		# Go long
		if thisRoll < thisRollTrend and isGreater:
			isGreater = not isGreater
			# Dump previous short positions
			portfolio += numPositions * thisPrice
			print("Dumped %d positions. " % numPositions)
			numPositions = 0
			# Build up long positions
			portfolio -= numBuys * thisPrice
			numPositions += numBuys
			print("Acquired %d LONG positions.\n" % numBuys)
		# Go short
		elif thisRoll > thisRollTrend and not isGreater:
			isGreater = not isGreater
			# Dump previous long positions
			portfolio += numPositions * thisPrice
			print("Dumped %d positions. " % numPositions)
			numPositions = 0
			# Build up short positions
			portfolio += numBuys * thisPrice
			numPositions -= numBuys
			print("Acquired %d SHORT positions.\n" % numBuys)
		# Otherwise, simply hold one's position
	return portfolio

def meanReversionStrategyZScore(priceRollingData, startingValue=1000, numBuys=1):
	price = priceRollingData.close.values.tolist()
	roll = priceRollingData.roll.values.tolist()
	rollTrend = priceRollingData.rollTrend.values.tolist()
	stdev = np.std(roll)
	zscores = [(roll[i] - rollTrend[i]) / stdev for i in range(len(price))]

	numPositions = 0
	portfolio = startingValue

	for i in range(len(price)):
		thisPrice = price[i]
		thisZ = zscores[i]
		if numBuys * thisPrice >= portfolio:
			print("It seems you have run out of funds.")
			break
		# Sell short if z-score > 1
		if thisZ > 1:
			portfolio += thisPrice * numBuys
			numPositions -= numBuys
			print("Acquired %d SHORT positions.\n" % numBuys)
		# Buy long if z-score < -1
		elif thisZ < -1: 
			portfolio -= thisPrice * numBuys
			numPositions += numBuys
			print("Acquired %d LONG positions.\n" % numBuys)
		# Clear positions if z-score is too low
		elif abs(thisZ) < 0.5:
			portfolio += thisPrice * numPositions
			# Useless to display dumping 0 positions
			if numPositions > 0:
				print("Dumped %d positions. " % numPositions)
			numPositions = 0

	return portfolio

startDate = "2014-01-01"
endDate = "2018-06-01"
# To compare the stock itself with a moving average, set roll=[1, X]
priceRollingData = meanReversionPlot("TSLA", "Tesla", startDate, endDate, roll=[1,90])
startingValue = 1000000
numBuys = 300
endingValue = meanReversionStrategyZScore(priceRollingData, startingValue=startingValue, numBuys=numBuys)
print("Profit (percent): %f" % (100 * (endingValue - startingValue) / startingValue))